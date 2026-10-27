"""Phase 6 Task 19: routing. The hub's Step 2 table routes each of the seven Phase 6 skills, the union eval set meets
the Phase 6 floor (185 + 7 x 4), every new skill's router eval names the sibling it is most easily confused with, and
no Phase 6 router or format prompt repeats a four-word run of the hub (so a blind routing run is not a string match)."""
from __future__ import annotations

import json
import re

from test_evals import ROOT, all_evals, runner

HUB = ROOT / "skills" / "learnings-coach" / "SKILL.md"
FOLDERS = sorted(p.parent.name for p in (ROOT / "skills").glob("*/skill.json"))
PHASE6_SKILLS = ("could-it-happen-here", "learning-effectiveness-plan", "learning-team-facilitator",
                 "restorative-response-guide", "safety-alert", "safety-moment-deck", "systemic-accimap")
BASE_EVALS = 185            # the union eval set at the start of Phase 6 (2b69ad4)
# the two presets whose planned steps Phase 6 un-planned (Task 7: safety-alert; Task 8: could-it-happen-here)
UNPLANNED_PRESETS = ("first-48-hours", "sister-sites")


def _step2() -> str:
    return HUB.read_text(encoding="utf-8").split("## Step 2", 1)[1].split("## Step 3", 1)[0]


def _skill_rows() -> dict:
    """{skill: (the user wants…, not this when…)} from the hub's one-audience table (three cells per row)."""
    out = {}
    for line in _step2().splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("| ") and len(cells) == 3:
            for s in re.findall(r"`([a-z0-9-]+)`", cells[1]):
                out.setdefault(s, (cells[0], cells[2]))
    return out


def _router_target(e) -> str:
    return next(x["value"] for x in e["expectations"] if x.get("type") == "routes_to")


def _desc(skill: str) -> str:
    t = (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
    return next(line for line in t.splitlines() if line.startswith("description:"))


def test_phase6_skills_are_the_seven_new_folders():
    """The seven are skill folders marked since 2.0.0, and with them the count is 39 (P6-1)."""
    for s in PHASE6_SKILLS:
        assert s in FOLDERS, s
        assert json.loads((ROOT / "skills" / s / "skill.json").read_text(encoding="utf-8"))["since"] == "2.0.0", s
    assert len(FOLDERS) == 39, len(FOLDERS)


def test_hub_step2_has_a_row_for_each_phase6_skill():
    """Step 1: a row per new skill, with a "Not this when…" cell that names a sibling, and the hub at <= 150 lines."""
    rows = _skill_rows()
    for s in PHASE6_SKILLS:
        assert s in rows, s
        sibs = set(re.findall(r"`([a-z0-9-]+)`", rows[s][1])) - {s}
        assert sibs and sibs <= set(FOLDERS) | set(UNPLANNED_PRESETS) | {"action-design"}, (s, sibs)
    assert set(FOLDERS) - {"learnings-coach"} <= set(rows), sorted(set(FOLDERS) - set(rows))
    assert len(HUB.read_text(encoding="utf-8").splitlines()) <= 150


def test_union_eval_total_meets_the_phase6_floor():
    """Step 1: at least 185 + 7 x 4 evals in the union set, each new skill owns at least four (trigger, no-trigger,
    collision) plus a hub router eval, and `run_evals.py check` passes."""
    evals = all_evals()
    assert len(evals) >= BASE_EVALS + 4 * len(PHASE6_SKILLS), len(evals)
    for s in PHASE6_SKILLS:
        own = [e for e in evals if e["owner"] == s]
        kinds = {e["kind"] for e in own}
        assert len(own) >= 3 and {"trigger", "no-trigger", "collision"} <= kinds, (s, sorted(kinds))
        assert any(e["kind"] == "router" and _router_target(e) == s for e in evals), s
    r = runner("check")
    assert r.returncode == 0 and r.stdout.strip().endswith("OK"), r.stdout + r.stderr


def test_every_phase6_skill_has_a_router_eval_with_a_sibling():
    router = [e for e in all_evals() if e["kind"] == "router"]
    for s in PHASE6_SKILLS:
        mine = [e for e in router if _router_target(e) == s]
        assert mine, f"no router eval routes to {s}"
        assert any(e.get("sibling") for e in mine), (s, [e["id"] for e in mine])
    targets = {_router_target(e) for e in router}
    assert set(UNPLANNED_PRESETS) <= targets, sorted(set(UNPLANNED_PRESETS) - targets)


def test_phase6_sibling_is_a_tie_break_in_a_description():
    """Step 4 relies on it: a Phase 6 router eval's sibling is named in the target's own "Not for … (use X)"
    tie-break, or the sibling's description names the target, so a misroute is fixed by tightening a description."""
    router = [e for e in all_evals() if e["kind"] == "router" and _router_target(e) in PHASE6_SKILLS
              and e.get("sibling")]
    assert len(router) >= len(PHASE6_SKILLS)
    for e in router:
        s, sib = _router_target(e), e["sibling"]
        assert sib in FOLDERS, (e["id"], sib)
        assert f"`{sib}`" in _desc(s) or f"`{s}`" in _desc(sib), (e["id"], s, sib)


def test_phase6_prompts_share_no_four_word_run_with_the_hub():
    """Step 2: no router or format prompt about a Phase 6 skill repeats a four-word run of the hub's SKILL.md (its
    routing tables, Formats bullets or any other line). The eval's own file paths are left out."""
    def grams(t):
        w = re.findall(r"[a-z]+", t.lower())
        return {tuple(w[i:i + 4]) for i in range(len(w) - 3)}
    hub = grams(HUB.read_text(encoding="utf-8"))
    scanned = [e for e in all_evals()
               if (e["kind"] == "router" and _router_target(e) in PHASE6_SKILLS + UNPLANNED_PRESETS)
               or (e["owner"] in PHASE6_SKILLS
                   and any(x["type"] == "command_contains" for x in e["expectations"]))]
    assert len(scanned) >= len(PHASE6_SKILLS)
    echoes = {}
    for e in scanned:
        prompt = e["prompt"]
        for f in e.get("files", []):
            prompt = prompt.replace(f, " ")
        shared = grams(prompt) & hub
        if shared:
            echoes[e["id"]] = sorted(" ".join(g) for g in shared)
    assert echoes == {}, echoes
