"""Phase 5, Task 8: the `risk_change` kind and the `risk-csv` format (D7: the risk owner's decision column stays
blank). Synthetic fixtures only."""
import copy
import csv
import io

import pytest

from test_pmlc import ws  # noqa: F401  (ws is a module-scoped fixture)
from test_pack import fixture, item, pack_with, render_fixture
from test_privacy import SPACK, _cli, share_ws, sign, write_doc
import pmlc  # noqa: E402
import pmlc_pack as pp  # noqa: E402

from pmlc_lib import render as R  # noqa: E402
from pmlc_lib.pack import schema as PS  # noqa: E402

COLUMNS = "id,risk,change_type,current_assumption,evidence_says,proposed_change,cites,risk_owner_decision"
RISK = {"kind": "risk_change", "id": "rc-seal", "risk": "Seal failure on the transfer pump",
        "change_type": "control-rating",
        "current_assumption": "The leak test before restart is rated as a reliable control.",
        "evidence_says": "The test record was not asked for after a seal change [FND-0001].",
        "proposed_change": "Re-rate the control as degraded until the record is part of the work order.",
        "cites": ["FND-0001", "EVD-0001"]}


@pytest.fixture(scope="module")
def w(ws):  # noqa: F811
    return pmlc.load_ws(ws)


def test_risk_change_valid(w):
    assert PS.KINDS["risk_change"]["cite"]
    r = pp.check_pack(pack_with(RISK), w)
    assert r.problems == [] and not [x for x in r.warnings if "unknown field" in x], r
    assert R.FORMATS["risk-csv"].kind == "data"
    bad = {k: v for k, v in RISK.items() if k != "proposed_change"}
    assert "sections[0].items[0].proposed_change: required for risk_change" in pp.check_pack(pack_with(bad), w).problems


@pytest.mark.parametrize("ct", ["missing-threat", "control-rating", "accepted-without-authority", "kri", "other"])
def test_risk_change_types(w, ct):
    assert pp.check_pack(pack_with(dict(RISK, change_type=ct)), w).problems == []


def test_risk_change_bad_type(w):
    r = pp.check_pack(pack_with(dict(RISK, change_type="rating")), w)
    assert any("change_type" in p and "missing-threat" in p for p in r.problems), r.problems


def test_risk_csv_columns(w):
    outs = render_fixture("x", "risk-csv", w=w, pack=pack_with(RISK, dict(RISK, id="rc-2", risk="=SUM(A1)")))
    assert [o.name for o in outs] == ["test-pack.risk-changes.csv"]
    rows = list(csv.reader(io.StringIO(outs[0].data)))
    assert ",".join(rows[0]) == COLUMNS
    assert len(rows) == 3
    assert rows[1][0] == "rc-seal" and rows[1][2] == "control-rating" and rows[1][6] == "FND-0001;EVD-0001"
    assert all(r[-1] == "" for r in rows[1:])                      # D7: the risk owner decides
    assert rows[2][1] == "'=SUM(A1)"                               # never a live formula
    assert render_fixture("x", "risk-csv", w=w, pack=pack_with(item("para"))) == []


def test_risk_csv_nothing_to_write_note(w):
    notes = []
    render_fixture("x", "risk-csv", w=w, pack=pack_with(item("para")), notes=notes)
    assert notes and "nothing to write" in notes[0]


def test_risk_csv_shared_copy(tmp_path):
    ws_, orgs = share_ws(tmp_path)
    doc = copy.deepcopy(SPACK)
    doc["sections"][0]["items"].append(dict(RISK, evidence_says="Raised by the Plant Manager at 09:15 [FND-0001].",
                                            current_assumption="The Plant Manager rated the control as reliable."))
    p = sign(ws_, write_doc(tmp_path, doc), "--classification", "external", "--legal-review", "cleared")
    r = _cli("pack", str(ws_), str(p), "--share", "external", "--orgs", str(orgs), "--embed", "summary",
             "--format", "risk-csv", "--out", str(tmp_path / "o"))
    assert r.returncode == 0, r.stderr
    names = sorted(x.name for x in (tmp_path / "o").iterdir())
    assert names == ["test-pack.risk-changes.external.csv"]
    text = (tmp_path / "o" / names[0]).read_text(encoding="utf-8")
    assert "09:15" not in text and text.endswith(",\n")            # times masked; decision column blank


def test_risk_csv_refuses_overwrite(tmp_path):
    """D7: the risk owner records decisions in <pack>.risk-changes.csv, so a second `pack --format risk-csv` refuses
    to replace it (exit 1, nothing else written), as `--format csv` does for <pack>.actions.csv."""
    ws_, _ = share_ws(tmp_path)
    doc = copy.deepcopy(SPACK)
    doc["sections"][0]["items"].append(dict(RISK))
    p = write_doc(tmp_path, doc)
    out = tmp_path / "o"
    r = _cli("pack", str(ws_), str(p), "--format", "risk-csv", "--out", str(out))
    assert r.returncode == 0, r.stderr
    f = out / "test-pack.risk-changes.csv"
    assert f.read_bytes().endswith(b",\r\n")                      # rows kept as \r\n, decision column blank
    decided = COLUMNS + "\r\nrc-seal,x,control-rating,a,b,c,FND-0001,Accepted by the risk owner\r\n"
    f.write_bytes(decided.encode("utf-8"))
    r = _cli("pack", str(ws_), str(p), "--format", "html,risk-csv", "--out", str(out))
    assert r.returncode == 1
    assert f"{f} already exists and may hold your organisation's entries; move it or pass a new --out" in r.stderr
    assert f.read_bytes() == decided.encode("utf-8")
    assert not (out / "test-pack.html").exists()                    # nothing else was written either
    assert _cli("pack", str(ws_), str(p), "--format", "risk-csv", "--out", str(tmp_path / "o2")).returncode == 0


def test_risk_change_all_formats(w):
    """The conformance loop over all-kinds: every registered format renders a pack with a risk_change item."""
    pack = fixture("all-kinds")
    assert any(i["kind"] == "risk_change" for s in pack["sections"] for i in s["items"])
    for name, fmt in R.FORMATS.items():
        if name in ("png", "ics"):
            continue
        try:
            render_fixture("all-kinds", name, w=w)
        except Exception as e:                                      # noqa: BLE001
            pytest.fail(f"{name}: {e!r}")
