"""Tests on the committed Hazira sample (public record). Later tasks reuse the module fixture `hz`."""
import json
import re
import subprocess
import sys
import types
from pathlib import Path

import pytest

from test_pmlc import PMLC, ROOT, pmlc, run

pytest.importorskip("openpyxl")
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
REGISTER = SAMPLE / "outputs" / "learnings-register.json"
GOLDEN = Path(__file__).resolve().parent / "fixtures" / "roles-golden.json"


@pytest.fixture(scope="module")
def hz(tmp_path_factory):
    root = tmp_path_factory.mktemp("hazira")
    run("ingest", str(EXPORT), "--slug", "hazira-gas-release-fire", "--root", str(root))
    ws = root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"
    run("classify", str(ws), "--overlay", "india-process-site")

    def select(*args):
        return json.loads(run("select", str(ws), *args, "--format", "json"))

    return types.SimpleNamespace(
        ws=ws, select=select,
        clusters=json.loads((ws / "clusters.json").read_text(encoding="utf-8")),
        incident=json.loads((ws / "incident.json").read_text(encoding="utf-8")))


def test_baseline(hz):
    findings = json.loads((hz.ws / "findings.json").read_text(encoding="utf-8"))
    assert len(findings) == 436
    assert len(json.loads((hz.ws / "evidence.json").read_text(encoding="utf-8"))) == 46
    assert max(f["rating"] or 0 for f in findings) == 4
    assert len(hz.clusters["role_map"]) == 630
    assert len(hz.select("--entity", "F02", "F06")) == 196


def test_golden_roles(hz):
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    assert len(golden) >= 50
    rm = hz.clusters["role_map"]
    wrong = {r: ({k: rm[r][k] for k in "FTR"} if r in rm else None, want) for r, want in golden.items()
             if r not in rm or {k: rm[r][k] for k in "FTR"} != want}
    assert wrong == {}


def test_no_design_role_is_approver(hz):
    assert not [r for r, m in hz.clusters["role_map"].items() if "design" in r.lower() and m["R"] == "approver"]


def test_plant_policy_roles_are_t4(hz):
    roles = {r: m["T"] for r, m in hz.clusters["role_map"].items() if re.search(r"(?i)plant manag.*polic", r)}
    assert roles and set(roles.values()) == {"T4"}, roles


def test_register_still_clean(hz):
    r = subprocess.run([sys.executable, str(PMLC), "check-register", str(hz.ws), str(REGISTER)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "; 0 problem(s)." in r.stdout


def test_select_by_tag_on_hazira(hz):
    emergency = {d["id"] for d in hz.select("--tag", "emergency")}
    assert emergency == {d["id"] for d in hz.select("--entity", "F09a", "F09b", "F10")}
    assert hz.clusters["taxonomy"]["overlays"] == ["india-process-site"]


def test_entity_mode_all_is_intersection(hz):
    assert len(hz.select("--entity", "F02", "F06")) == 196
    assert len(hz.select("--entity", "F02", "F06", "--entity-mode", "all")) == 27


def test_budget_truncates_by_rating(hz):
    r = subprocess.run([sys.executable, str(PMLC), "select", str(hz.ws), "--tier", "T2", "--budget-chars", "60000"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert len(r.stdout) <= 60000
    ratings = [int(x) for x in re.findall(r"· rating (\d+)", r.stdout)]
    assert ratings and ratings == sorted(ratings, reverse=True)
    m = re.search(r"Dropped for budget: (\d+) findings", r.stdout)
    assert m and int(m.group(1)) > 0
    assert len(ratings) + int(m.group(1)) == len(hz.select("--tier", "T2"))


def test_analysis_stats_cross_check(hz):
    st = hz.incident["analysis_stats"]
    assert st["total"] == 436
    assert {int(k): v for k, v in st["by_level"].items()} == {1: 36, 2: 92, 3: 167, 4: 141}


def test_export_schema_doc_matches_sample(hz):
    import openpyxl
    wb = openpyxl.load_workbook(EXPORT, read_only=True)
    for sheet, known in pmlc.KNOWN_COLUMNS.items():
        header = [c for c in next(wb[sheet].iter_rows(values_only=True)) if c]
        assert header == known, sheet
    doc = (ROOT / "skills" / "learnings-coach" / "references" / "export-schema.md").read_text(encoding="utf-8")
    for name in [c for cols in pmlc.KNOWN_COLUMNS.values() for c in cols] + pmlc.KNOWN_SUMMARY_FIELDS:
        assert name in doc, name
    assert set(hz.incident["fields"]) <= set(pmlc.KNOWN_SUMMARY_FIELDS)
