"""Taxonomy 2.0: version and fingerprint, the A1-A4 regex fixes, OD-1, org-chart import and statutory roles."""
import json
import re
import subprocess
import sys

import pytest

import test_pmlc
from test_pmlc import PMLC, ROOT, make_export, pmlc, run

pytest.importorskip("openpyxl")
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
OVERLAY = "india-process-site"


def _map(role, overlays=()):
    return pmlc.map_role(role, pmlc._load_taxonomy(None, list(overlays)))


def test_leadership_needs_qualifier():                                                        # A1
    assert "F13" not in _map("Function leadership")["F"] and _map("Function leadership")["T"] != "T4"
    plant = _map("Plant leadership team")
    assert "F13" in plant["F"] and plant["T"] == "T4"
    assert _map("Senior leadership")["T"] == "T4"


@pytest.mark.parametrize("role", ["signing authority", "Signatories", "countersigned by the manager"])
def test_sign_variants_are_approver(role):                                                    # A2
    assert _map(role)["R"] == "approver"


def test_design_is_still_not_approver():
    assert _map("Design engineers")["R"] != "approver"


T3_FORMS = ["DGM", "DGM (Production)", "Dy. GM (Operations)", "Dy.GM", "Dy GM", "Deputy GM", "Deputy General Manager",
            "Dy. General Manager", "Asst. GM", "Asst GM", "Assistant GM", "Assistant General Manager"]
T4_FORMS = ["Addl. GM", "Addl GM", "Additional GM", "Additional General Manager", "GM (Production)"]


@pytest.mark.parametrize("role,tier", [(r, "T3") for r in T3_FORMS] + [(r, "T4") for r in T4_FORMS])
def test_dgm_tier_per_od1(role, tier):                                                        # A3, OD-1
    assert _map(role, [OVERLAY])["T"] == tier, role


def test_bare_agm_stays_unresolved():                                                         # ruling X21
    assert _map("AGM (Operations)", [OVERLAY])["T"] == "T9"


@pytest.mark.parametrize("role", ["Leadership team", "The leadership team", "Senior leadership team",
                                  "Plant leadership team"])
def test_leadership_team_is_site_leadership(role):
    m = _map(role)
    assert m["T"] == "T4" and "F13" in m["F"], role


def test_dgm_not_in_base_taxonomy():
    base = json.loads((ROOT / "skills/learnings-coach/references/taxonomy.json").read_text(encoding="utf-8"))
    assert all("dgm" not in t["match"].lower() for t in base["tiers"])
    assert _map("DGM (Production)")["T"] != "T2"


def test_document_custodian_f07():                                                            # A4
    assert "F07" in _map("Controlled document custodian")["F"]
    assert "F07" in _map("Document owner (procedures)")["F"]
    assert "F07" not in _map("DMP/ERDMP document owners", [OVERLAY])["F"]                       # ruling 10


def _classified(tmp_path, overlay=None, rows=None, name="w"):
    d = tmp_path
    if rows is not None:
        old = test_pmlc.ROWS
        test_pmlc.ROWS = rows
    try:
        x = make_export(d)
    finally:
        if rows is not None:
            test_pmlc.ROWS = old
    ws = d / name
    run("ingest", str(x), "--legacy-out", str(ws))
    return ws


def _clusters(ws):
    return json.loads((ws / "clusters.json").read_text(encoding="utf-8"))


def test_taxonomy_version_and_fingerprint(tmp_path):                                          # A5
    ws = _classified(tmp_path)
    run("classify", str(ws))
    a = _clusters(ws)
    assert a["taxonomy_version"] == "2.0"
    assert re.fullmatch(r"[0-9a-f]{64}", a["taxonomy_fingerprint"])
    run("classify", str(ws))
    assert _clusters(ws)["taxonomy_fingerprint"] == a["taxonomy_fingerprint"]
    ov = tmp_path / "ov.json"
    ov.write_text(json.dumps({"name": "x", "extend": {"entities": {"F01": "zzz"}}}), encoding="utf-8")
    run("classify", str(ws), "--overlay", str(ov))
    b = _clusters(ws)["taxonomy_fingerprint"]
    assert b != a["taxonomy_fingerprint"]
    ov.write_text(json.dumps({"name": "x", "extend": {"entities": {"F01": "yyy"}}}), encoding="utf-8")
    run("classify", str(ws), "--overlay", str(ov))
    assert _clusters(ws)["taxonomy_fingerprint"] != b


CHART = ("department,entity,match,tier\n"
         "Reliability Cell,,reliab;seal,T3\n"
         "Stores Desk,F06,stores desk,\n"
         "Budget Office,,budget|finance,\n")


def test_org_chart_import_stable_ids(tmp_path):
    ws = _classified(tmp_path)
    chart = tmp_path / "org.csv"
    chart.write_text(CHART, encoding="utf-8")
    out = run("classify", str(ws), "--org-chart", str(chart))
    assert re.search(r"\d+ of 4 findings mapped to your departments", out)
    c = _clusters(ws)
    assert c["taxonomy"]["entities"]["F20"] == "Reliability Cell" and c["taxonomy"]["entities"]["F21"] == "Budget Office"
    assert "F20" in c["findings"]["FND-0003"]["F"] and "F21" in c["findings"]["FND-0003"]["F"]
    ids = json.loads((ws / "org-chart-ids.json").read_text(encoding="utf-8"))
    # a reordered chart keeps the ids; a new department takes the next one
    chart.write_text("department,entity,match,tier\nNew Cell,,newcell,\nBudget Office,,budget|finance,\n"
                     "Reliability Cell,,reliab;seal,T3\n", encoding="utf-8")
    run("classify", str(ws), "--org-chart", str(chart))
    names = _clusters(ws)["taxonomy"]["entities"]
    assert names["F20"] == "Reliability Cell" and names["F21"] == "Budget Office" and names["F22"] == "New Cell"
    assert ids["Reliability Cell"] == "F20"
    # remembered on a plain re-run, cleared by --no-org-chart
    run("classify", str(ws))
    assert "F22" in _clusters(ws)["taxonomy"]["entities"]
    run("classify", str(ws), "--no-org-chart")
    assert "F20" not in _clusters(ws)["taxonomy"]["entities"]


def test_org_chart_tier_and_entity_extension(tmp_path):
    ws = _classified(tmp_path)
    role = "Emergency Response planners"
    run("classify", str(ws))
    before = _clusters(ws)["role_map"][role]
    assert "F06" not in before["F"] and before["T"] != "T3"
    chart = tmp_path / "org.csv"
    chart.write_text("department,entity,match,tier\nSpares,F06,emergency response,T3\n", encoding="utf-8")
    out = run("classify", str(ws), "--org-chart", str(chart))
    c = _clusters(ws)
    assert "2 of 4 findings mapped to your departments" in out  # FND-0003 has F06 natively
    assert "F20" not in c["taxonomy"]["entities"]                       # an entity row adds no new entity
    assert "F06" in c["role_map"][role]["F"] and c["role_map"][role]["T"] == "T3"
    assert c["findings"]["FND-0004"]["F"].count("F06") == 1


def test_org_chart_bad_row_named(tmp_path):
    ws = _classified(tmp_path)
    chart = tmp_path / "org.csv"
    chart.write_text("department,entity,match,tier\nA,,aaa,\nB,,bbb,\nC,,,\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(PMLC), "classify", str(ws), "--org-chart", str(chart)],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "org chart row 4: match is required" in r.stderr
    chart.write_text("department,entity,match,tier\nA,,aaa,\nB,,,\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(PMLC), "classify", str(ws), "--org-chart", str(chart)],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "org chart row 3: match is required" in r.stderr


def test_org_chart_row_is_the_csv_line(tmp_path):
    ws = _classified(tmp_path)
    chart = tmp_path / "org.csv"
    chart.write_text("department,entity,match,tier\nA,,aaa,\n\nB,,,\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(PMLC), "classify", str(ws), "--org-chart", str(chart)],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "org chart row 4: match is required" in r.stderr


def test_org_chart_other_errors(tmp_path):
    ws = _classified(tmp_path)
    chart = tmp_path / "org.csv"
    for body, msg in [("department,match\n,x\n", "org chart row 2: department is required"),
                      ("department,match,tier\nA,x,T7\n", "org chart row 2: tier T7"),
                      ("department,match,entity\nA,x,F77\n", "org chart row 2: entity F77"),
                      ("department,match\nA,(\n", "org chart row 2: match is not a valid regex"),
                      ("name,match\nA,x\n", "org chart: missing column")]:
        chart.write_text(body, encoding="utf-8")
        r = subprocess.run([sys.executable, str(PMLC), "classify", str(ws), "--org-chart", str(chart)],
                           capture_output=True, text=True)
        assert r.returncode == 1 and msg in r.stderr, (body, r.stderr)


def test_statutory_roles_listed(tmp_path):
    rows = [list(r) for r in test_pmlc.ROWS]
    ind = test_pmlc.FIND_COLS.index("Individuals Involved")
    rows[0][ind] = "Occupier, Factory Manager (statutory duty)"
    rows[1][ind] = "Mine Manager, Pump Technician"
    rows[2][ind] = "PSM contract employee, COMAH operator"
    ws = _classified(tmp_path, rows=rows)
    run("classify", str(ws))
    sr = _clusters(ws)["statutory_roles"]
    by = {(x["role"], x["regime"]): x for x in sr}
    assert by[("Occupier", "in")]["findings"] == ["FND-0001"] and by[("Occupier", "in")]["label"]
    assert ("Factory Manager (statutory duty)", "in") in by and ("Mine Manager", "in") in by
    assert ("PSM contract employee", "us") in by and ("COMAH operator", "uk") in by
    assert "Pump Technician" not in {x["role"] for x in sr}
    tax = json.loads((ROOT / "skills/learnings-coach/references/taxonomy.json").read_text(encoding="utf-8"))
    assert tax["version"] == "2.0" and {x["regime"] for x in tax["statutory_roles"]} == {"in", "uk", "us"}


def test_hazira_calibration_after_taxonomy(tmp_path):
    root = tmp_path / "r"
    run("ingest", str(EXPORT), "--slug", "hazira-gas-release-fire", "--root", str(root))
    ws = root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"
    run("classify", str(ws), "--overlay", OVERLAY)
    assert len(json.loads((ws / "findings.json").read_text(encoding="utf-8"))) == 436
    assert len(json.loads((ws / "evidence.json").read_text(encoding="utf-8"))) == 46
    sel = json.loads(run("select", str(ws), "--entity", "F02", "F06", "--entity-mode", "all", "--format", "json"))
    assert len(sel) == 27


@pytest.mark.parametrize("role,ent", [("Maintenance leadership", "F02"), ("HSE Leadership", "F11"),
                                      ("Operations leadership (acceptance of alarm-only configuration)", "F01")])
def test_function_leadership_is_t3(role, ent):                                               # ruling X19
    m = _map(role, [OVERLAY])
    assert m["T"] == "T3" and ent in m["F"] and "F13" not in m["F"]


def test_team_leader_still_t2():
    assert _map("Team leader")["T"] == "T2"
