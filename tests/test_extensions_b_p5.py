"""Phase 5, Task 21: extensions B to existing skills. manager-coach (work management for planners and schedulers,
select --prefix SVIO), auditor-assurance-pack (the assurance lens, P5-17), investigator-coach (evidence-audit
scorecard), learning-clusters (industry reference pack, P5-16), organisation-learning-map (the nine-m table, P5-18)
and the dossier reading budget (P5-19). Synthetic export from test_pmlc.py only (fictional event, no real data);
the Hazira numbers are in test_calibration_p5.py."""
import json
import re

from test_pmlc import ROOT

SKILLS = ROOT / "skills"
REFS = SKILLS / "learnings-coach" / "references"
SAMPLE_OUT = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire" / "outputs"


def read(p) -> str:
    return p.read_text(encoding="utf-8")


def load(p):
    return json.loads(read(p))


def section(text, heading) -> str:
    m = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    assert m, heading
    return m.group(1)


# ----------------------------------------------------------------------------- manager-coach

def test_manager_coach_gathers_planned_operations():
    """The work-management section gains select --prefix SVIO, with its preset."""
    gather = section(read(SKILLS / "manager-coach" / "SKILL.md"), "Gather")
    assert re.search(r"^PMLC select <ws> --prefix SVIO --brief\s+#.*", gather, re.M), gather
    presets = load(REFS / "select-presets.json")["manager-coach"]
    assert {"name": "work-management-svio", "args": ["--prefix", "SVIO", "--brief"]} in presets


def test_hub_routes_planners_to_manager_coach():
    s2 = section(read(SKILLS / "learnings-coach" / "SKILL.md"), "Step 2: work out the intent")
    rows = [x for x in s2.splitlines() if x.startswith("| planners and schedulers")]
    assert len(rows) == 1 and "`manager-coach` (work-management section)" in rows[0], rows


def test_router_eval_for_planners():
    frag = load(ROOT / "evals" / "skills" / "manager-coach.json")
    routers = [e for e in frag["evals"] if e["kind"] == "router"]
    assert any(e["expectations"] == [{"type": "routes_to", "value": "manager-coach"}]
               and "planner" in e["prompt"].lower() for e in routers), routers
