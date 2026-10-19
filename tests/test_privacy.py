"""The privacy core (pmlc_privacy): names, variants, singleton roles, on the synthetic export."""
import json
import re

import openpyxl
import pytest

from test_pack import item, pack_with
from test_pmlc import make_export, run
import pmlc  # noqa: E402
import pmlc_lint as pl  # noqa: E402
import pmlc_privacy as pv  # noqa: E402

ROLES = "Security Guard - Gate 3, Shift Engineer (CR), Operator"


@pytest.fixture(scope="module")
def sws(tmp_path_factory):
    d = tmp_path_factory.mktemp("priv")
    x = make_export(d)
    wb = openpyxl.load_workbook(x)
    ws = wb["Identified Findings"]
    col = [c.value for c in ws[1]].index("Individuals Involved") + 1
    ws.cell(row=2, column=col).value = ROLES
    wb.save(x)
    run("ingest", str(x), "--legacy-out", str(d / "ws"))
    run("classify", str(d / "ws"))
    return d / "ws"


def test_singletons_written_by_classify(sws):
    p = sws / "singleton_roles.json"
    doc = json.loads(p.read_text())
    assert doc["version"] == 1
    by = {e["role"]: e for e in doc["roles"]}
    assert by["Security Guard - Gate 3"]["reason"] == "qualifier"
    assert by["Shift Engineer (CR)"]["reason"] == "qualifier"
    assert "Operator" not in by
    for e in doc["roles"]:
        assert set(e) == {"role", "reason", "findings", "generalised"}
        assert e["findings"] >= 1 and re.fullmatch(r".+ \(.+\)", e["generalised"])
    assert pv.load_singletons(pmlc.load_ws(sws))["Shift Engineer (CR)"] == by["Shift Engineer (CR)"]["generalised"]
    p.unlink()
    assert pmlc.load_ws(sws)["singletons"] == []
    run("classify", str(sws))
    assert p.exists()


def test_single_holder_role():
    tax = {"entities": [{"id": "F13", "name": "Plant & Asset Leadership"}]}
    rm = {"Plant Head": {"F": ["F13"], "T": "T4", "R": "owner"},
          "Plant Manager": {"F": ["F13"], "T": "T3", "R": "owner"},
          "Site Director": {"F": ["F13"], "T": "T3", "R": "owner"}}
    fs = [{"roles": ["Plant Head", "Plant Manager"]}, {"roles": ["Plant Head", "Site Director"]}]
    out = pv.build_singletons(rm, fs, tax, {"T3": "Function managers", "T4": "Site leadership"})
    assert out["roles"] == [{"role": "Plant Head", "reason": "single-holder", "findings": 2,
                             "generalised": "Plant & Asset Leadership (Site leadership)"}]


def test_jc7_uses_singletons(sws):
    w = pmlc.load_ws(sws)
    p = pack_with(item("para", text="The Security Guard - Gate 3 closed the valve.", cites=["FND-0001"]))
    internal = [h for h in pl.lint(p, w, kind="pack", share="internal") if h.rule == "JC7"]
    external = [h for h in pl.lint(p, w, kind="pack", share="external") if h.rule == "JC7"]
    assert [h.severity for h in internal] == ["warning"]
    assert [h.severity for h in external] == ["error"]
    clean = pack_with(item("para", text="The Operator closed the valve.", cites=["FND-0001"]))
    assert not [h for h in pl.lint(clean, w, kind="pack", share="external") if h.rule == "JC7"]


def test_name_variants():
    v = pv.name_variants("Shri R. K. Sharma")
    assert v[0] == "Shri R. K. Sharma"
    for x in ("Sharma", "R. Sharma", "R. K. Sharma", "Mr Sharma", "Smt. Sharma", "Dr Sharma"):
        assert x in v
    v = pv.name_variants("Mr J Smith")
    for x in ("Smith", "J. Smith", "J Smith", "Mrs. Smith", "Shri Smith"):
        assert x in v
    assert pv.name_variants("John Smith")[2] == "J. Smith"
    assert pv.name_variants("ID #4471") == ["ID #4471"]
    assert "Dr. Anand" in pv.name_variants("Anand")


def test_name_pattern_boundaries():
    assert pv.name_pattern([]) is None
    rx = pv.name_pattern(["Shri R. K. Sharma", "Mr J Smith"], variants=True)
    for text in ("Shri R. K. Sharma left", "report by R. Sharma.", "Mr  Smith said", "smt. sharma", "(J Smith)"):
        assert rx.search(text), text
    for text in ("Sharmaji left", "the Smithson seal", "unSharma", "Smith2"):
        assert not rx.search(text), text
    exact = pv.name_pattern(["R. K. Sharma"])
    assert exact.search("by R. K. Sharma") and not exact.search("by Sharma")


def test_names_file_comments_and_ids(tmp_path, monkeypatch):
    f = tmp_path / "names.txt"
    f.write_text("  # comment\n\nR. K. Sharma\nID #4471\n", encoding="utf-8")
    assert pv.load_names(str(f)) == ["R. K. Sharma", "ID #4471"]
    rx = pv.name_pattern(pv.load_names(str(f)))
    assert rx.search("Prepared by R. K. Sharma") and rx.search("badge ID #4471 scanned")
    monkeypatch.setenv("PMLC_NAMES", str(f))
    assert len(pv.load_names()) == 2
    monkeypatch.setenv("PMLC_ORGS", str(f))
    assert len(pv.load_orgs()) == 2
    monkeypatch.delenv("PMLC_NAMES")
    assert pv.load_names() == []


def test_patterns_and_suffix():
    assert re.search(pv.PATTERNS["email"], "a.b@x.org") and re.search(pv.PATTERNS["phone"], "+91 98765 43210")
    assert re.search(pv.PATTERNS["staff_no"], "Staff No. 4471") and pv.ORG_SUFFIX_RX.search("Acme Pumps Ltd")


def test_scan_names_uses_privacy_core(tmp_path):
    n = tmp_path / "names.txt"
    n.write_text("# list\n\nR. K. Sharma\n", encoding="utf-8")
    t = tmp_path / "t.md"
    t.write_text("by R. K. Sharma\n", encoding="utf-8")
    from test_pmlc import PMLC
    import subprocess
    import sys
    r = subprocess.run([sys.executable, str(PMLC), "scan-names", str(n), str(t)], capture_output=True, text=True)
    assert r.returncode == 1 and "1 hit" in r.stdout
