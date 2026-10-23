"""Phase 5 Task 17: the `people-workforce-learnings` skill (HR and workforce planning). Its manifest, audience entry,
profile and routing, the Hazira select counts it is written against, and its Hazira golden pack."""
import json
import re
import subprocess
import sys

import pytest

from test_pmlc import PMLC, ROOT, run

SKILL = "people-workforce-learnings"
SKILLS_DIR = ROOT / "skills"
REFS = SKILLS_DIR / "learnings-coach" / "references"
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
REGISTER = SAMPLE / "outputs" / "learnings-register.json"
GOLDEN = SAMPLE / "outputs" / f"{SKILL}.json"
# The code names the skill's --code line is built from (plan, Task 17), matched case-insensitively.
NAME_RX = re.compile(r"selection|staffing|crew|manning|qualif|authori|roster|fatigue|workload", re.I)
HAZIRA_CODES = ["OIS 4.1", "OIS 4.2", "PTF 1.1", "PTF 1.6", "SVIO 2.2", "SVIO 2.5", "SVIO 2.6", "SVV 4.4"]
BANNER = "Learnings about systems, not individuals' records."


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def skill_md() -> str:
    return (SKILLS_DIR / SKILL / "SKILL.md").read_text(encoding="utf-8")


def code_line_codes() -> list:
    """The codes on the SKILL.md `PMLC select <ws> --code …` line."""
    line = next(x for x in skill_md().splitlines() if x.startswith("PMLC select <ws> --code "))
    return re.findall(r'"([A-Z]+ \d+\.\d+)"', line.split("#", 1)[0])


def test_manifest_as_planned():
    m = load(SKILLS_DIR / SKILL / "skill.json")
    assert m["kind"] == "audience" and m["audiences"] == ["hr-workforce"]
    assert m["scope"] == {"tiers": ["T3", "T4"], "levels": [2, 3, 4], "tags": ["people"], "entities": ["F12"]}
    assert m["requires"] == ["workspace", "clusters"] and m["optional_inputs"] == ["register"]
    assert m["formats"] == ["docx", "email"] and m["share_default"] == "internal"
    assert m["since"] == "2.0.0" and m["embed_default"] == "cited" and m["produces"]["pack"] == SKILL


def test_audience_entry():
    a = next(x for x in load(REFS / "audiences.json") if x["id"] == "hr-workforce")
    assert a["label"] == "HR and workforce planning" and a["tier"] == "T3" and a["reading_level"] == "plain"
    assert a["skill"] == SKILL
    for who in ("HR business partners", "workforce planners", "rostering and fatigue owners",
                "competence-framework owners"):
        assert who in a["typical_people"], who


def test_profile_as_planned():
    p = load(REFS / "pack-profiles.json")[SKILL]
    assert [(s["id"], s["kinds"], s["min"], s["max"]) for s in p["sections"]] == [
        ("banner", ["para"], 1, 1), ("system", ["learning"], 1, 8), ("competence-framework", ["table"], 1, 1),
        ("rostering", ["learning"], 0, 4), ("handoff", ["para"], 1, 1)]
    assert p["rules"] == ["banner:people"] and p["lint_errors"] == ["JC2"] and p["required_scope"] == ["tiers"]
    assert p["bottom_line"] == {"min": 1, "max": 5}


def test_routed_in_full_cascade_after_manager_coach():
    steps = [s["skill"] for s in load(REFS / "workflows.json")["full-cascade"]["steps"]]
    assert steps[steps.index("manager-coach") + 1] == SKILL
    plan = load(ROOT / "tests" / "fixtures" / "plans" / "full-cascade.json")
    assert SKILL in json.dumps(plan)


def test_select_lines_match_the_presets():
    pre = {p["name"]: p["args"] for p in load(REFS / "select-presets.json")[SKILL]}
    assert pre["people-codes"] == ["--code", *HAZIRA_CODES, "--brief"]
    assert pre["hr-entity"] == ["--entity", "F12", "--brief"]
    assert code_line_codes() == HAZIRA_CODES


@pytest.fixture(scope="module")
def hz(tmp_path_factory):
    pytest.importorskip("openpyxl")
    root = tmp_path_factory.mktemp("hazira-people")
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root),
        "--overlay", "india-process-site")
    return root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"


def _ids(ws, *args) -> set:
    out = run("select", str(ws), *args, "--format", "json")
    data = json.loads(out[out.index("["):])
    return {f["id"] for f in data}


def test_hazira_code_list_and_counts(hz):
    """The --code list is every Hazira code whose name matches NAME_RX: 8 codes, 18 findings. --entity F12 gives 22;
    the two lines together give 38 distinct findings (2 in both)."""
    F = json.loads((hz / "findings.json").read_text(encoding="utf-8"))
    assert sorted({f["code"] for f in F if NAME_RX.search(f["name"])}) == HAZIRA_CODES
    codes, hr = _ids(hz, "--code", *HAZIRA_CODES), _ids(hz, "--entity", "F12")
    assert (len(codes), len(hr), len(codes | hr), len(codes & hr)) == (18, 22, 38, 2)


def test_hazira_golden_passes_strict(hz):
    pack = load(GOLDEN)
    assert pack["pack"] == SKILL and pack["skill"] == SKILL and "handling" not in pack
    assert pack["scope"] == load(SKILLS_DIR / SKILL / "skill.json")["scope"]
    r = subprocess.run([sys.executable, str(PMLC), "check-pack", str(hz), str(GOLDEN), "--strict",
                        "--register", str(REGISTER)], capture_output=True, text=True)
    assert r.returncode == 0 and "OK:" in r.stdout and "problem" not in r.stdout + r.stderr, r.stdout + r.stderr
    r = subprocess.run([sys.executable, str(PMLC), "check-language", str(hz), str(GOLDEN)],
                       capture_output=True, text=True)
    assert r.returncode == 0 and "0 errors" in r.stdout + r.stderr, r.stdout + r.stderr


def test_sanction_wording_is_an_error(hz, tmp_path):
    """JC2 (sanction wording, such as a performance review) is an error in this pack through check-language and
    check-pack (lint_errors, P5-5): an HR pack must not drift towards individuals' records."""
    pack = load(GOLDEN)
    sec = next(s for s in pack["sections"] if s["id"] == "system")
    sec["items"][0]["explanation"] += " Add the finding to the operator's performance review."
    bad = tmp_path / f"{SKILL}.json"
    bad.write_text(json.dumps(pack), encoding="utf-8")
    r = subprocess.run([sys.executable, str(PMLC), "check-language", str(hz), str(bad)], capture_output=True, text=True)
    assert r.returncode != 0 and "ERROR JC2" in r.stdout, r.stdout + r.stderr
    r = subprocess.run([sys.executable, str(PMLC), "check-pack", str(hz), str(bad), "--register", str(REGISTER)],
                       capture_output=True, text=True)
    assert r.returncode != 0 and "JC2" in r.stdout + r.stderr, r.stdout + r.stderr


def test_hazira_golden_content():
    pack = load(GOLDEN)
    items = {s["id"]: s["items"] for s in pack["sections"]}
    assert items["banner"] == [{"kind": "para", "text": BANNER}]
    assert any(it.get("learning") == "LR-12" for it in items["system"])
    tab = items["competence-framework"][0]
    assert tab["kind"] == "table" and len(tab["row_cites"]) == len(tab["rows"]) and all(tab["row_cites"])
    assert "training-designer" in items["handoff"][0]["text"]
    text = json.dumps(pack)
    assert not re.search(r"\[(?:CE|JEA|CCTV CR)\]|\bMr\.", text)                       # roles only
    assert not any("by_when" in it for v in items.values() for it in v)                # no due dates (D7)
    assert all(not re.search(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", it.get("owner", "")) for v in items.values() for it in v)
    rostering = [it for it in items["rostering"] if it["kind"] == "learning"]
    assert {"FND-0AEE9898", "FND-615DB819"} <= {c for it in rostering for c in it["cites"]}
    assert "fatigue" in " ".join(pack["limits"])                                      # no inferred fatigue
