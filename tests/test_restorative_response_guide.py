"""Phase 6 Task 11: the `restorative-response-guide` skill (leaders and peer support). Its manifest, audience entry,
profile and routing (no workflow step: `plan --skills` and the hub row), the Hazira select counts it is written
against, its fixed banner and rules (needs are questions, JC3 and JC4 are errors) and its Hazira golden pack."""
import json
import re
import subprocess
import sys

import pytest

from test_pmlc import PMLC, ROOT, run, ws  # noqa: F401  (ws is a module-scoped fixture)

SKILL = "restorative-response-guide"
SKILLS_DIR = ROOT / "skills"
REFS = SKILLS_DIR / "learnings-coach" / "references"
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
REGISTER = SAMPLE / "outputs" / "learnings-register.json"
GOLDEN = SAMPLE / "outputs" / f"{SKILL}.json"
FIXTURE = ROOT / "tests" / "fixtures" / "packs" / f"{SKILL}.json"
BANNER = ("The export holds no information about the people affected. Every need here is a question to ask, or the "
          "organisation's own answer.")
HARM = "on foot|head.?count|shanty|civilian|injur|casualt|evacuat|muster"
SCOPE = {"tiers": [], "levels": [2, 3, 4], "tags": []}
SIBLINGS = ("people-workforce-learnings", "learning-team-facilitator")


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def skill_md() -> str:
    return (SKILLS_DIR / SKILL / "SKILL.md").read_text(encoding="utf-8")


def items_of(pack) -> dict:
    return {s["id"]: s["items"] for s in pack["sections"]}


def test_manifest_as_planned():
    m = load(SKILLS_DIR / SKILL / "skill.json")
    assert m["kind"] == "audience" and m["audiences"] == ["leaders-and-peer-support"]
    assert m["scope"] == SCOPE
    assert m["requires"] == ["workspace"] and m["optional_inputs"] == ["register"]
    assert m["formats"] == ["docx"] and m["share_default"] == "internal"
    assert m["since"] == "2.0.0" and m["embed_default"] == "cited" and m["produces"]["pack"] == SKILL
    assert m["interactive"] is False


def test_audience_entry():
    a = next(x for x in load(REFS / "audiences.json") if x["id"] == "leaders-and-peer-support")
    assert a["skill"] == SKILL and a["default_scope"] == SCOPE and a["reading_level"] == "plain"
    for who in ("site and line leaders", "peer supporters"):
        assert who in a["typical_people"], who
    assert "leaders-and-peer-support" in (REFS / "audiences.md").read_text(encoding="utf-8") or \
        a["label"] in (REFS / "audiences.md").read_text(encoding="utf-8")


def test_profile_as_planned():
    p = load(REFS / "pack-profiles.json")[SKILL]
    assert [(s["id"], s["kinds"], s["min"], s["max"]) for s in p["sections"]] == [
        ("banner", ["para"], 1, 1), ("who-is-hurt", ["question"], 1, 4), ("needs", ["question"], 2, 6),
        ("obligations", ["para"], 1, 3), ("system-conditions", ["learning"], 1, 5), ("support", ["check"], 2, 6)]
    assert p["rules"] == ["no-owner-due", "banner:restorative", "needs-are-questions"]
    assert p["lint_errors"] == ["JC3", "JC4"] and p["bottom_line"] == {"min": 1, "max": 3}


def test_description_tie_breaks():
    """The description names both siblings in its 'Not for … (use X)' tie-break. test_skills.OVERLAPS checks the
    people-workforce-learnings pair; this test also covers learning-team-facilitator (Task 10, a parallel branch)."""
    d = re.search(r"^description: (.+)$", skill_md(), re.M).group(1)
    assert "Not for" in d
    for s in SIBLINGS:
        assert f"use `{s}`" in d, s


def test_no_workflow_step_reached_through_skills(tmp_path):
    """P6 Task 11: no preset runs it; it is reached through `plan --skills`, the hub row and a router eval."""
    wf = load(REFS / "workflows.json")
    assert SKILL not in json.dumps(wf)
    hub = (SKILLS_DIR / "learnings-coach" / "SKILL.md").read_text(encoding="utf-8")
    assert f"| `{SKILL}` |" in hub and len(hub.splitlines()) <= 150
    evals = load(ROOT / "evals" / "skills" / f"{SKILL}.json")["evals"]
    assert {e["kind"] for e in evals} >= {"trigger", "no-trigger", "collision", "router"}
    assert any(e["kind"] == "router" and e["expectations"][0]["value"] == SKILL for e in evals)


def test_learning_principles_name_dekker_and_second_victim():
    t = (REFS / "learning-principles.md").read_text(encoding="utf-8")
    assert re.search(r"Dekker.*who is hurt.*what do they need.*whose obligation", t, re.I | re.S)
    assert "second victim" in t.lower()


def test_select_lines_match_the_presets():
    pre = {p["name"]: p["args"] for p in load(REFS / "select-presets.json")[SKILL]}
    assert pre == {"in-harms-way": ["--text", HARM, "--fields", "label,level,short"],
                   "conditions": ["--level", "2", "3", "4", "--text", HARM, "--brief"]}


@pytest.fixture(scope="module")
def hz(tmp_path_factory):
    pytest.importorskip("openpyxl")
    root = tmp_path_factory.mktemp("hazira-restorative")
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root),
        "--overlay", "india-process-site")
    return root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"


def _ids(w, *args) -> set:
    out = run("select", str(w), *args, "--format", "json")
    return {f["id"] for f in json.loads(out[out.index("["):])}


def test_hazira_select_counts(hz):
    """The harm regex gives 13 Hazira findings (2 at level 1, the actions of a person); 11 at levels 2-4. The register
    entries that cite any of them are LR-07, LR-08, LR-12, LR-13 and LR-25."""
    allx, cond = _ids(hz, "--text", HARM), _ids(hz, "--level", "2", "3", "4", "--text", HARM)
    assert (len(allx), len(cond)) == (13, 11) and cond < allx
    reg = load(REGISTER)["entries"]
    assert sorted(e["lr_id"] for e in reg if allx & set(e["finding_ids"])) == ["LR-07", "LR-08", "LR-12", "LR-13",
                                                                                "LR-25"]


def test_hazira_golden_passes_strict(hz):
    pack = load(GOLDEN)
    assert pack["pack"] == SKILL and "handling" not in pack and pack["scope"] == SCOPE
    r = subprocess.run([sys.executable, str(PMLC), "check-pack", str(hz), str(GOLDEN), "--strict",
                        "--register", str(REGISTER)], capture_output=True, text=True)
    assert r.returncode == 0 and "OK:" in r.stdout and "problem" not in r.stdout + r.stderr, r.stdout + r.stderr
    r = subprocess.run([sys.executable, str(PMLC), "check-language", str(hz), str(GOLDEN)],
                       capture_output=True, text=True)
    assert r.returncode == 0 and "0 errors" in r.stdout + r.stderr, r.stdout + r.stderr


def test_hazira_golden_conditions_cite_levels_2_to_4(hz):
    """system-conditions cite findings that show conditions, never the actions of a person: levels 2-4 only."""
    level = {f["id"]: f["level"] for f in load(hz / "findings.json")}
    conds = items_of(load(GOLDEN))["system-conditions"]
    cited = [c for it in conds for c in it["cites"] if c.startswith("FND-")]
    assert cited and all(level[c] in (2, 3, 4) for c in cited), [c for c in cited if level[c] == 1]
    assert all(re.fullmatch(r"LR-\d\d", it.get("learning", "")) for it in conds)


def test_hazira_golden_content():
    pack = load(GOLDEN)
    items = items_of(pack)
    assert items["banner"] == [{"kind": "para", "text": BANNER}]
    assert all(it["kind"] == "question" for it in items["who-is-hurt"] + items["needs"])
    assert "second victim" in json.dumps(items["support"]).lower()
    assert 1 <= len(pack["bottom_line"]) <= 3
    text = json.dumps(pack)
    assert not re.search(r"\[(?:CE|JEA|CCTV CR)\]|\bMr\.?\s", text)                       # roles only
    assert not any(k in it for v in items.values() for it in v for k in ("owner", "by_when", "co_owner"))  # D7


@pytest.fixture
def syn(ws):  # noqa: F811  (the synthetic pump-fire workspace of test_pmlc)
    return ws


def _variant(tmp_path, change) -> str:
    pack = load(FIXTURE)
    change(pack)
    p = tmp_path / f"{SKILL}.json"
    p.write_text(json.dumps(pack), encoding="utf-8")
    return str(p)


def test_a_need_that_is_not_a_question_is_refused(syn, tmp_path):
    """needs-are-questions: a need written as a statement is inferred about people the export says nothing about."""
    def stmt(pack):
        next(s for s in pack["sections"] if s["id"] == "needs")["items"].append(
            {"kind": "para", "text": "The crew need time off.", "cites": ["FND-0001"]})
    r = subprocess.run([sys.executable, str(PMLC), "check-pack", str(syn), _variant(tmp_path, stmt), "--strict"],
                       capture_output=True, text=True)
    assert r.returncode != 0 and "needs are asked, never inferred" in r.stdout + r.stderr, r.stdout + r.stderr


def test_a_missing_banner_is_refused(syn, tmp_path):
    def nob(pack):
        next(s for s in pack["sections"] if s["id"] == "banner")["items"][0]["text"] = "About the people affected."
    r = subprocess.run([sys.executable, str(PMLC), "check-pack", str(syn), _variant(tmp_path, nob), "--strict"],
                       capture_output=True, text=True)
    assert r.returncode != 0 and "banner" in r.stdout + r.stderr, r.stdout + r.stderr


@pytest.mark.parametrize("words,rule", [("The supervisor should have stopped the job.", "JC3"),
                                        ("The gap was obvious in hindsight.", "JC4")])
def test_counterfactual_and_hindsight_wording_are_errors(syn, tmp_path, words, rule):
    """JC3 (counterfactual) and JC4 (hindsight) are errors in this pack (lint_errors), not warnings."""
    def bad(pack):
        next(s for s in pack["sections"] if s["id"] == "system-conditions")["items"][0]["explanation"] += " " + words
    p = _variant(tmp_path, bad)
    r = subprocess.run([sys.executable, str(PMLC), "check-language", str(syn), p], capture_output=True, text=True)
    assert r.returncode != 0 and f"ERROR {rule}" in r.stdout, r.stdout + r.stderr
    r = subprocess.run([sys.executable, str(PMLC), "check-pack", str(syn), p], capture_output=True, text=True)
    assert r.returncode != 0 and rule in r.stdout + r.stderr, r.stdout + r.stderr


def test_plan_skills_runs_it(syn):
    out = run("plan", str(syn), "--skills", SKILL)
    assert SKILL in out
