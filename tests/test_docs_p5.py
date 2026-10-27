"""Phase 5 documentation (plan Task 26): every document states the skill count the folders give (ruling P5-1), and the
manual, README, AGENTS.md and CHANGELOG describe the Phase 5 commands, skills, files and messages."""
import importlib.util
import inspect
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "docs" / "manual"
SKILL_COUNT = len(list((ROOT / "skills").glob("*/skill.json")))      # P5-1: the folders, never a constant
SUB_COUNT = SKILL_COUNT - 1                                           # every skill but the hub

# (document, pattern whose one group is a count, the count it must state)
COUNT_STATEMENTS = [
    ("README.md", r"plugin of (\d+) agent skills", SKILL_COUNT),
    ("docs/manual/Home.md", r"The (\d+) skills", SKILL_COUNT),
    ("docs/manual/Skills.md", r"The Learnings Coach is (\d+) agent skills", SKILL_COUNT),
    ("AGENTS.md", r"routes to the other (\d+) skills", SUB_COUNT),
    ("skills/learnings-coach/SKILL.md", r"The other (\d+) skills", SUB_COUNT),
    ("docs/manual/skills/learnings-coach.md", r"one or more of the (\d+) skills", SUB_COUNT),
    ("docs/manual/Developer-tools.md", r"evals over (\d+) skills", SKILL_COUNT),
    ("docs/manual/Developer-tools.md", r"and (\d+) sub-skills covered", SUB_COUNT),
    ("evals/README.md", r"trigger evals for the (\d+) skills", SKILL_COUNT),
    ("evals/README.md", r"one of the (\d+) sub-skills", SUB_COUNT),
    ("evals/README.md", r"presets or (\d+) sub-skills", SUB_COUNT),
]
COUNT_RX = re.compile(r"\b(\d+) (?:agent |sub-)?skills\b")
# Phase 6 skills also carry since 2.0.0; the Phase 5 checks below are about the nine Phase 5 skills only.
P6_SKILLS = {"safety-alert", "could-it-happen-here", "safety-moment-deck", "learning-team-facilitator",
             "restorative-response-guide", "systemic-accimap", "learning-effectiveness-plan"}
NEW_SKILLS = sorted(p.parent.name for p in (ROOT / "skills").glob("*/skill.json")
                    if json.loads(p.read_text(encoding="utf-8")).get("since") == "2.0.0"
                    and p.parent.name not in P6_SKILLS)
NEW_COMMANDS = ["evidence-audit", "hfacs-profile", "open-questions", "nine-m-seed", "nine-m-suggest", "nine-m-answer",
                "nine-m-replay", "nine-m-actions-template", "rec-review", "missed-opportunities", "crosswalk"]
NEW_FLAGS = ["--event-day", "--m", "--m-secondary", "--industry", "--kind table"]
P5_FILES = ["evidence_audit.json", "hfacs_profile.json", "open_questions.json", "nine_m_seed.json",
            "nine_m_session.json", "missed_opportunities.json", "nine-m-map.json", "<pack>.actions-template.xlsx",
            "<pack>.actions-template.csv", "<pack>-tables.xlsx", "open-questions-follow-up.csv",
            "<pack>.risk-changes.csv"]
P5_RECIPES = {   # preset -> the engine command text its recipe must show
    "action-design": ("nine-m-seed", "rec-review", "nine-m-actions-template"),
    "investigation-quality": ("evidence-audit", "open-questions"),
    "assurance": ("crosswalk", "evidence-audit")}
P5_TROUBLES = ["This is a ProbeMatrix CAPA Planner workbook. nine-m-analysis reads the findings export only",
               "owner and due dates are set by the organisation, not in this pack",
               "evidence_strength is computed by the engine"]
P5_TERMS = ["nine ms (9m)", "rbps", "rca²", "single-loop and double-loop learning", "drupsteen's learning cycle", "kri"]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def recipes() -> dict:
    """{recipe heading: body} of Workflows-and-recipes.md."""
    parts = re.split(r"^## ", read("docs/manual/Workflows-and-recipes.md"), flags=re.M)[1:]
    return {p.split("\n", 1)[0].strip(): p for p in parts}


@pytest.mark.parametrize("doc,pattern,want", COUNT_STATEMENTS)
def test_docs_state_the_skill_count(doc, pattern, want):
    """P5-1: each document states the count the skill folders give (32 skills, 31 beside the hub)."""
    got = [int(n) for n in re.findall(pattern, read(doc), re.M)]
    assert got and set(got) == {want}, (doc, pattern, got, want)


@pytest.mark.parametrize("doc", sorted({d for d, _, _ in COUNT_STATEMENTS}))
def test_docs_state_no_other_skill_count(doc):
    """No stale count is left elsewhere in these documents. The README's release history is left as written."""
    text = read(doc)
    if doc == "README.md":
        text = text.split("## What's new in v2.0 so far", 1)[0] + "\n## " + text.split("\n## The skills", 1)[1]
    stale = sorted({int(n) for n in COUNT_RX.findall(text)} - {SKILL_COUNT, SUB_COUNT})
    assert not stale, (doc, stale)


def test_nine_new_skills():
    assert len(NEW_SKILLS) == 9, NEW_SKILLS


def test_phase_5_skills_are_since_2_0_0():
    since = {p.parent.name for p in (ROOT / "skills").glob("*/skill.json")
             if json.loads(p.read_text(encoding="utf-8")).get("since") == "2.0.0"}
    assert set(NEW_SKILLS) <= since, sorted(set(NEW_SKILLS) - since)


@pytest.mark.parametrize("doc,row", [("README.md", "| `{s}` |"), ("docs/manual/Skills.md", "[{s}](skills/{s}.md)")])
def test_listings_name_every_new_skill(doc, row):
    text = read(doc)
    missing = [s for s in NEW_SKILLS if row.format(s=s) not in text]
    assert not missing, (doc, missing)


def test_readme_whats_new_starts_with_phase_5():
    readme = read("README.md")
    news = readme.split("## What's new in v2.0 so far", 1)[1].split("\n## ", 1)[0]
    phases = re.findall(r"^\*\*Phase (\d+) \(([^)]*)\):\*\*", news, re.M)
    assert phases[0] == ("5", "2.0.0-alpha.7"), phases
    assert "current build: 2.0.0-alpha.7, Phase 5" in news


def test_agents_typical_run_has_evidence_audit_and_nine_m_seed():
    run = read("AGENTS.md").split("## Typical run", 1)[1].split("```", 2)[1]
    assert re.search(r"^python3 \$E evidence-audit \$WS", run, re.M)
    assert re.search(r"^python3 \$E nine-m-seed \$WS", run, re.M)


def test_changelog_2_0_0a7():
    log = read("CHANGELOG.md")
    assert log.index("### 2.0.0a7") < log.index("### 2.0.0a6")
    entry = log.split("### 2.0.0a7", 1)[1].split("### 2.0.0a6", 1)[0]
    missing = [f"`{c}`" for c in NEW_COMMANDS if f"`{c}`" not in entry]
    missing += [f"`{s}`" for s in NEW_SKILLS if f"`{s}`" not in entry]
    missing += [f for f in NEW_FLAGS if f"`{f}" not in entry]
    assert not missing, missing
    notes = entry.split("**Migration notes.**", 1)[1]
    for needle in ("evidence_audit.json", "whole words", "artefacts.json", "workspace/evidence_audit.json",
                   "workspace/hfacs_profile.json", "nine_m", "evals/skills/"):
        assert needle in notes, needle


@pytest.mark.parametrize("preset", sorted(P5_RECIPES))
def test_recipes_cover_the_phase_5_workflows(preset):
    """Each Phase 5 preset has a recipe that plans it and shows its engine commands on Hazira (Task 26)."""
    hits = [h for h, b in recipes().items() if f"--workflow {preset}" in b and "Hazira" in b
            and all(c in b for c in P5_RECIPES[preset])]
    assert hits, f"no Hazira recipe plans --workflow {preset} with {P5_RECIPES[preset]}"
    home = read("docs/manual/Home.md")
    slug = re.sub(r"[^\w\- ]", "", hits[0].lower()).replace(" ", "-")
    assert f"Workflows-and-recipes.md#{slug}" in home, slug


def test_files_and_folders_lists_the_phase_5_files():
    text = read("docs/manual/Files-and-folders.md")
    missing = [f for f in P5_FILES if f"`{f}`" not in text]
    assert not missing, missing


def test_troubleshooting_has_the_phase_5_problems():
    text = read("docs/manual/Troubleshooting.md")
    missing = [m for m in P5_TROUBLES if m not in text]
    assert not missing, missing


def test_glossary_has_the_phase_5_terms():
    terms = [h.lower() for h in re.findall(r"^### (.+?)\s*$", read("docs/manual/Glossary.md"), re.M)]
    missing = [t for t in P5_TERMS if not any(h == t or h.startswith(t + " ") for h in terms)]
    assert not missing, missing


def _smoke():
    spec = importlib.util.spec_from_file_location("smoke_sample", ROOT / "tools" / "smoke_sample.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_smoke_requires_a_golden_for_every_pack_skill():
    """tools/smoke_sample.py fails when a pack skill (the nine Phase 5 skills among them) has no Hazira golden in
    the --strict loop, so a new skill's pack cannot drop out of the smoke run unnoticed."""
    smoke = _smoke()
    outputs = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire" / "outputs"
    names = sorted(p.stem for p in outputs.glob("*.json"))
    assert smoke.missing_goldens(names) == []
    left = [n for n in names if n not in ("nine-m-analysis", "dossier-F02")]
    assert smoke.missing_goldens(left) == ["cluster-learning-dossier", "nine-m-analysis"]
    assert set(NEW_SKILLS) <= set(smoke.missing_goldens([]))
    src = inspect.getsource(smoke.format_loop)                 # the gate's loop really calls it, and fails on a gap
    assert "missing = missing_goldens(names)" in src and "if missing:" in src and "fail(" in src


WORDS = {16: "Sixteen", 17: "Seventeen", 18: "Eighteen", 19: "Nineteen", 20: "Twenty", 21: "Twenty-one",
         22: "Twenty-two", 23: "Twenty-three", 24: "Twenty-four", 25: "Twenty-five"}


def test_skills_page_states_the_preset_count():
    presets = json.loads(read("skills/learnings-coach/references/select-presets.json"))
    n = len([k for k in presets if not k.startswith("_")])
    assert f"{WORDS[n]} skills also have a recorded **preset**" in read("docs/manual/Skills.md"), n
