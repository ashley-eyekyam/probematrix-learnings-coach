"""Item generators (table-item, register-items, timeline-item), causal --hubs, facts and pack-xlsx (Task 12)."""
import copy
import json
import re
import subprocess
import sys

import pytest

from test_pmlc import MINI_REG, PMLC, make_export, run
from test_sample import REGISTER as HZ_REGISTER, hz  # noqa: F401  (hz is a module-scoped fixture)
import pmlc  # noqa: E402  (test_pmlc put the engine folder on sys.path)
import pmlc_pack as pp  # noqa: E402
from pmlc_lib.templates import ADOPTION_COLUMNS

STATUS = "Learning purposes: not a statutory document"
KINDS = ["clusters", "tiers", "relations", "hubs", "interfaces", "evidence-types", "entity-tier", "hoc", "adoption"]


def cli(*args):
    return subprocess.run([sys.executable, str(PMLC), *args], capture_output=True, text=True)


def wrap(*items):
    return {"pack": "test-pack", "schema": 1, "title": "Test pack: synthetic pump fire", "audience": "Testers",
            "status": STATUS, "incident": {"date": "2024-03-20"},
            "bottom_line": [{"text": "Test before service.", "cites": ["FND-0002"]}],
            "sections": [{"id": "s1", "heading": "Section one", "items": copy.deepcopy(list(items))}]}


def register(extra=True):
    reg = copy.deepcopy(MINI_REG)
    if extra:
        base = reg["entries"][0]
        reg["entries"] += [dict(base, lr_id="LR-02", title="Second", priority=2, tiers=["T1"], finding_ids=["FND-0003"]),
                           dict(base, lr_id="LR-03", title="Third", priority=1, tiers=["T1", "T3"],
                                finding_ids=["FND-0004"], tier_messages={"T3": "Own the spares specification."}),
                           dict(base, lr_id="LR-04", title="Fourth", priority=3, tiers=["T2"])]
    return reg


@pytest.fixture(scope="module")
def rund(tmp_path_factory):
    d = tmp_path_factory.mktemp("items")
    x = make_export(d, causal_rows=True)
    run("ingest", str(x), "--slug", "test-pump", "--date", "2024-03-20")
    ws = d / "pmlc-runs" / "2024-03-20-test-pump" / "workspace"
    run("classify", str(ws))
    run("causal", str(ws))
    run("interfaces", str(ws))
    run("timeline", str(ws), "--before", "incident")
    out = ws.parent / "outputs"
    out.mkdir(exist_ok=True)
    (out / "learnings-register.json").write_text(json.dumps(register()), encoding="utf-8")
    return ws


def table(ws, kind, *extra):
    r = cli("table-item", str(ws), kind, *extra)
    assert r.returncode == 0, r.stderr + r.stdout
    return json.loads(r.stdout)


def checked(ws, item, tmp_path):
    p = tmp_path / "pack.json"
    p.write_text(json.dumps(wrap(item)), encoding="utf-8")
    r = cli("check-pack", str(ws), str(p))
    assert r.returncode == 0, r.stderr + r.stdout
    return r


@pytest.mark.parametrize("kind", KINDS)
def test_each_table_item_passes_check_pack(rund, tmp_path, kind):
    extra = {"entity-tier": ["--entity", "F02"], "hoc": ["--register", str(rund.parent / "outputs" / "learnings-register.json")]}
    it = table(rund, kind, *extra.get(kind, []))
    assert it["kind"] == "table" and it["rows"] and len(it["row_cites"]) == len(it["rows"])
    assert all(len(r) == len(it["columns"]) for r in it["rows"])
    assert it["cites"] == sorted({x for c in it["row_cites"] for x in c})
    checked(rund, it, tmp_path)


def test_table_item_hoc_from_a_pack(rund, tmp_path):
    p = tmp_path / "recs.json"
    p.write_text(json.dumps(wrap({"kind": "recommendation", "change": "Add a test", "indicator": "Share tested",
                                  "hoc_tier": "engineering", "cites": ["FND-0001"]})), encoding="utf-8")
    it = table(rund, "hoc", "--pack", str(p))
    assert it["rows"][0][0].lower() == "engineering" and it["row_cites"][0] == ["FND-0001"]
    assert cli("table-item", str(rund), "hoc").returncode != 0


def test_table_item_rows_sorted_and_capped(rund):
    it = table(rund, "clusters", "--top", "2")
    assert len(it["rows"]) == 2
    counts = [r[2] for r in it["rows"]]
    assert counts == sorted(counts, reverse=True)
    lv4 = table(rund, "tiers", "--level", "4")
    assert sum(r[2] for r in lv4["rows"]) <= len(json.loads((rund / "findings.json").read_text()))


def test_table_item_adoption_without_file(rund, tmp_path):
    it = table(rund, "adoption")
    assert it["rows"] == [["No adoption record yet: run PMLC templates <ws> adoption and fill it in"]]
    checked(rund, it, tmp_path)


def test_table_item_adoption_with_file(rund, tmp_path):
    out = rund.parent / "outputs"
    (out / "adoption.csv").write_text(",".join(ADOPTION_COLUMNS) + "\r\nLR-01,Return to service,accepted,,Plant manager,30 days\r\n",
                                      encoding="utf-8")
    try:
        it = table(rund, "adoption")
        assert it["rows"] == [["LR-01", "Return to service", "accepted", "", "Plant manager", "30 days"]]
        assert it["row_cites"] == [["FND-0001", "FND-0002"]]
        checked(rund, it, tmp_path)
    finally:
        (out / "adoption.csv").unlink()


def test_register_items_p1_first(rund, tmp_path):
    r = cli("register-items", str(rund), "--tier", "T1")
    assert r.returncode == 0, r.stderr
    items = json.loads(r.stdout)
    assert [i["learning"] for i in items] == ["LR-01", "LR-03", "LR-02"]
    assert all(i["kind"] == "learning" and i["cites"] for i in items)
    assert items[0]["lesson"] == "Do not pressurise without the test record."
    t3 = json.loads(cli("register-items", str(rund), "--tier", "T3").stdout)
    assert [i["learning"] for i in t3] == ["LR-03"] and t3[0]["lesson"] == "Own the spares specification."
    p = tmp_path / "pack.json"
    p.write_text(json.dumps(wrap(*items)), encoding="utf-8")
    r = cli("check-pack", str(rund), str(p), "--strict")       # learning is a known field, checked against the register
    assert r.returncode == 0, r.stderr + r.stdout
    assert "unknown field" not in r.stdout + r.stderr and "unknown learning" not in r.stdout + r.stderr
    assert "learning ids not verified" not in r.stdout + r.stderr
    assert cli("register-items", str(rund), "--tier", "T5").stdout.strip() == "[]"


def test_timeline_item_months_before(rund, tmp_path):
    r = cli("timeline-item", str(rund), "--before", "incident", "--top", "5")
    assert r.returncode == 0, r.stderr
    it = json.loads(r.stdout)
    assert it["kind"] == "timeline" and 1 <= len(it["events"]) <= 5
    dates = [e["date"] for e in it["events"]]
    assert dates == sorted(dates) and max(dates) <= "2024-03-20"
    assert all(e["cites"] for e in it["events"])
    march = next(e for e in it["events"] if e["date"] == "2022-03")
    assert re.search(r"\(F\d+[a-z]?, T\d\)$", march["received_by"])
    checked(rund, it, tmp_path)
    md = pp.render_pack_md(wrap(it), pmlc.load_ws(rund))
    assert "2022-03 (24 months before)" in md
    assert cli("timeline-item", str(rund), "--before", "2022-12-31").returncode == 0
    assert cli("timeline-item", str(rund), "--before", "nonsense").returncode != 0


def test_causal_hubs_table(rund):
    out = run("causal", str(rund), "--hubs")
    assert "| Factor | Level | Links out | Mentions |" in out
    row = next(line for line in out.split("Hubs")[1].splitlines() if line.startswith("| OR 2.2"))
    cells = [c.strip() for c in row.strip("|").split("|")]
    assert cells[1] == "L4" and cells[2] == "4"
    assert "Hubs" not in run("causal", str(rund))
    hubs = table(rund, "hubs")
    assert hubs["rows"][0][0] == "OR 2.2"


def test_ties_are_ordered_by_id(rund):
    g = json.loads((rund / "causal_graph.json").read_text())
    key = [(-e["mentions"], e["from"], e["to"]) for e in g["edges"]]
    assert key == sorted(key)
    pairs = json.loads((rund / "interfaces.json").read_text())["pairs"]
    key = [(-(p["shared_findings"] * 3 + p["cross_causal_mentions"]), p["a"], p["b"]) for p in pairs]
    assert key == sorted(key)


def test_facts_keys_and_hazira_values(hz, tmp_path):  # noqa: F811
    d = json.loads(cli("facts", str(hz.ws), "--json").stdout)
    assert d["findings"] == 436 and d["evidence_items"] == 46
    assert d["levels"] == {"1": 36, "2": 92, "3": 167, "4": 141} and d["l34_share"] == 0.706
    assert set(d) == {"findings", "evidence_items", "levels", "l34_share", "entities", "tiers", "top_rating",
                      "top_rated", "incident_date", "p1_by_tier"}
    assert d["incident_date"] == "2020-09-24" and d["top_rating"] == 4 and d["p1_by_tier"] is None
    assert d["entities"]["F02"] > 0 and d["tiers"]["T1"] > 0
    reg = json.loads(HZ_REGISTER.read_text(encoding="utf-8"))["entries"]
    d = json.loads(cli("facts", str(hz.ws), "--json", "--register", str(HZ_REGISTER)).stdout)
    for t in ("T1", "T2", "T3", "T4", "T5"):
        want = [e["lr_id"] for e in reg if e["priority"] == 1 and t in e["tiers"]]
        assert d["p1_by_tier"][t] == want
    assert "LR-04" not in sum(d["p1_by_tier"].values(), [])
    md = cli("facts", str(hz.ws), "--register", str(HZ_REGISTER)).stdout
    assert md.startswith("| Fact | Value |") and "| findings | 436 |" in md


def test_facts_without_clusters(tmp_path):
    x = make_export(tmp_path)
    run("ingest", str(x), "--legacy-out", str(tmp_path / "ws"))
    d = json.loads(cli("facts", str(tmp_path / "ws"), "--json").stdout)
    assert d["findings"] == 4 and d["entities"] == {} and d["tiers"] == {}


def pack_with_tests():
    return wrap({"kind": "test_point", "requirement": "Hold point is signed", "sample": "Ten work orders",
                 "conformity_evidence": "Signed test record", "red_flags": ["Blank signature"], "cites": ["EVD-0001"],
                 "clause": "free text"},
                {"kind": "question", "question": "Who checks the part number?", "why": "No check exists",
                 "to": "Stores", "cites": ["FND-0003"]},
                {"kind": "para", "text": "Ignored by the sheet.", "cites": ["FND-0001"]})


def test_pack_xlsx_cites_column_and_status(rund, tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    p = tmp_path / "pack.json"
    p.write_text(json.dumps(pack_with_tests()), encoding="utf-8")
    out = tmp_path / "tp.xlsx"
    r = cli("pack-xlsx", str(rund), str(p), "--kind", "test_point", "--out", str(out))
    assert r.returncode == 0, r.stderr + r.stdout
    wb = openpyxl.load_workbook(out)
    assert len(wb.worksheets) == 1
    sh = wb.active
    header = [c.value for c in sh[1]]
    assert header[-1] == "cites" and "requirement" in header and "conformity_evidence" in header
    row = [c.value for c in sh[2]]
    assert row[header.index("cites")] == "EVD-0001" and row[header.index("red_flags")] == "Blank signature"
    assert sh.max_row == 2
    assert STATUS in sh.oddHeader.center.text and "DRAFT" in sh.oddHeader.center.text
    assert "ProbeMatrix Learnings Coach" in sh.oddFooter.center.text
    q = tmp_path / "q.xlsx"
    assert cli("pack-xlsx", str(rund), str(p), "--kind", "question", "--out", str(q)).returncode == 0
    assert openpyxl.load_workbook(q).active["A2"].value
    default = cli("pack-xlsx", str(rund), str(p), "--kind", "question")
    assert default.returncode == 0 and (rund.parent / "outputs" / "test-pack-questions.xlsx").is_file()


def test_pack_xlsx_refuses_pack_without_that_kind(rund, tmp_path):
    p = tmp_path / "pack.json"
    p.write_text(json.dumps(wrap({"kind": "para", "text": "x", "cites": ["FND-0001"]})), encoding="utf-8")
    r = cli("pack-xlsx", str(rund), str(p), "--kind", "question", "--out", str(tmp_path / "x.xlsx"))
    assert r.returncode == 1 and "no question items" in (r.stderr + r.stdout)
