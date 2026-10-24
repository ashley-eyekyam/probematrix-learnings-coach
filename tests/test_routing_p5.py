"""Phase 5 Task 25: routing. The hub's Step 2 routes every skill folder, the union eval set meets the Phase 5 floor,
and every new skill's router eval names the sibling it is most easily confused with."""
from __future__ import annotations

import json
import re

from test_evals import ROOT, all_evals, runner

HUB = ROOT / "skills" / "learnings-coach" / "SKILL.md"
FOLDERS = sorted(p.parent.name for p in (ROOT / "skills").glob("*/skill.json"))
NEW = sorted(s for s in FOLDERS
             if json.loads((ROOT / "skills" / s / "skill.json").read_text(encoding="utf-8")).get("since") == "2.0.0")
BASE_EVALS = 134            # evals.json at the start of Phase 5 (117ad35)


def _step2() -> str:
    return HUB.read_text(encoding="utf-8").split("## Step 2", 1)[1].split("## Step 3", 1)[0]


def _skill_column() -> set:
    """The backticked names in the Skill column of the hub's one-audience table (three cells per row)."""
    out = set()
    for line in _step2().splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("| ") and len(cells) == 3:
            out |= set(re.findall(r"`([a-z0-9-]+)`", cells[1]))
    return out


def _router_target(e) -> str:
    return next(x["value"] for x in e["expectations"] if x.get("type") == "routes_to")


def test_new_skills_are_the_nine():
    assert len(NEW) == 9, NEW


def test_hub_step2_routes_every_skill_folder():
    """Step 1 of Task 25: the Step 2 table holds a row for each of the nine new skills (and every other sub-skill),
    and the hub stays within 150 lines."""
    assert set(FOLDERS) - {"learnings-coach"} <= _skill_column(), sorted(set(FOLDERS) - _skill_column())
    assert len(HUB.read_text(encoding="utf-8").splitlines()) <= 150


def test_union_eval_total_meets_the_phase5_floor():
    """At least 134 + 9 x 4 + the extension evals (fragment evals owned by a skill older than 2.0.0); the check passes."""
    frag = []
    for f in sorted((ROOT / "evals" / "skills").glob("*.json")):
        frag.extend(json.loads(f.read_text(encoding="utf-8"))["evals"])
    ext = [e for e in frag if e["owner"] not in NEW]
    assert len(all_evals()) >= BASE_EVALS + 4 * len(NEW) + len(ext), (len(all_evals()), len(ext))
    r = runner("check")
    assert r.returncode == 0 and r.stdout.strip().endswith("OK"), r.stdout + r.stderr


def test_every_new_skill_has_a_router_eval_with_a_sibling():
    """Each new skill is a router target at least once, and that router eval names the sibling it collides with,
    so the blind run measures the tie-break and not only the trigger words."""
    router = [e for e in all_evals() if e["kind"] == "router"]
    for s in NEW:
        mine = [e for e in router if _router_target(e) == s]
        assert mine, f"no router eval routes to {s}"
        assert any(e.get("sibling") for e in mine), (s, [e["id"] for e in mine])


def test_sibling_is_a_tie_break_in_the_target_description():
    """A router eval's sibling for a new skill is named in that skill's own "Not for ... (use X)" tie-break, or the
    sibling's description names the new skill, so a misroute can be fixed by tightening a description (Step 4)."""
    router = [e for e in all_evals() if e["kind"] == "router" and _router_target(e) in NEW and e.get("sibling")]

    def desc(s):
        t = (ROOT / "skills" / s / "SKILL.md").read_text(encoding="utf-8")
        return next(line for line in t.splitlines() if line.startswith("description:"))
    for e in router:
        s, sib = _router_target(e), e["sibling"]
        if sib in FOLDERS:
            assert f"`{sib}`" in desc(s) or f"`{s}`" in desc(sib), (e["id"], s, sib)
