"""Phase 6 documentation (plan Task 20): the manual (with the new Library page), README, AGENTS.md and CHANGELOG
describe the Phase 6 commands, skills, files and messages, and every document states the skill count the folders
give (P6-1; the count statements themselves are pinned in test_docs_p5.py)."""
import importlib.util
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "docs" / "manual"
SAMPLE_OUT = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire" / "outputs"
PHASE6_SKILLS = ("safety-alert", "could-it-happen-here", "safety-moment-deck", "learning-team-facilitator",
                 "restorative-response-guide", "systemic-accimap", "learning-effectiveness-plan")
# The Phase 6 skills whose folders are on this branch (the listings follow the folders, P5-1 / P6-1).
PRESENT = tuple(s for s in PHASE6_SKILLS if (ROOT / "skills" / s / "skill.json").is_file())
P6_COMMANDS = ["alert-grade", "consolidate", "wai-wad", "accimap", "effect-plan", "library publish"]
P6_TEMPLATES = ["cihh", "learning-team"]
P6_RECIPES = {   # recipe -> the engine command text its section must show
    "sister-sites": ("--workflow sister-sites", "alert-grade", "templates <ws> cihh", "consolidate"),
    "follow-up": ("--workflow follow-up", "effect-plan", "templates <ws> verification"),
    "learning-team": ("wai-wad", "templates <ws> learning-team")}
P6_WORKSPACE_FILES = ["wai_wad.json", "accimap.json", "effect_plan.json"]
P6_OUTPUT_FILES = ["learning-team-notes.csv", "<pack>.cihh-template.xlsx", "cihh-consolidated.json",
                   "cihh-events.jsonl"]
LIBRARY_FILES = ["library.json", "learnings.jsonl", "events.jsonl", "incidents.jsonl", "private/sites.json",
                 "private/contexts.jsonl"]
P6_REFERENCES = ["learning-team.json", "effectiveness.json"]
P6_TROUBLES = {   # heading -> a message the section must quote
    "consolidate refuses a return": "nothing written (fix them, or pass --keep-going to use the good rows)",
    "library publish found a listed name": "listed name",
    "my sister-site alert says Review copy": "Review copy: not for distribution outside the organisation"}
P6_TERMS = ["accimap", "work as imagined and work as done", "learning team", "restorative just culture",
            "second victim", "kirkpatrick levels", "jacobsson's levels of learning", "ll-id"]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def sections(rel: str, level: str = "## ") -> dict:
    parts = re.split(rf"^{level}", read(rel), flags=re.M)[1:]
    return {p.split("\n", 1)[0].strip(): p for p in parts}


def slug(heading: str) -> str:
    return re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")


def test_phase_6_skills_on_this_branch():
    """Six of the seven are merged; learning-effectiveness-plan lands with its own task (the count follows)."""
    assert len(PRESENT) >= 6, PRESENT


@pytest.mark.parametrize("doc,row", [("README.md", "| `{s}` |"), ("docs/manual/Skills.md", "[{s}](skills/{s}.md)")])
def test_listings_name_every_phase_6_skill(doc, row):
    text = read(doc)
    missing = [s for s in PRESENT if row.format(s=s) not in text]
    assert not missing, (doc, missing)


def test_readme_whats_new_starts_with_phase_6():
    news = read("README.md").split("## What's new in v2.0 so far", 1)[1].split("\n## ", 1)[0]
    phases = re.findall(r"^\*\*Phase (\d+) \(([^)]*)\):\*\*", news, re.M)
    assert phases[:2] == [("6", "2.0.0-alpha.8"), ("5", "2.0.0-alpha.7")], phases
    assert "current build: 2.0.0-alpha.8, Phase 6" in news
    phase6 = news.split("**Phase 6 (2.0.0-alpha.8):**", 1)[1].split("**Phase 5", 1)[0]
    assert "v2.1" in phase6 and "multi-incident" in phase6
    assert "learnings library" in phase6.lower()


def test_agents_typical_run_has_the_phase_6_commands():
    run = read("AGENTS.md").split("## Typical run", 1)[1].split("```", 2)[1]
    for cmd in ("alert-grade", "consolidate", "wai-wad", "accimap", "effect-plan", "library publish"):
        assert re.search(rf"^python3 \$E {cmd} \$WS", run, re.M), cmd
    for t in P6_TEMPLATES:
        assert re.search(rf"^python3 \$E templates \$WS {t}\b", run, re.M), t


def test_changelog_2_0_0a8():
    log = read("CHANGELOG.md")
    assert log.index("### 2.0.0a8") < log.index("### 2.0.0a7")
    entry = log.split("### 2.0.0a8", 1)[1].split("### 2.0.0a7", 1)[0]
    missing = [f"`{c}`" for c in P6_COMMANDS if f"`{c}`" not in entry]
    missing += [f"`templates {t}`" for t in P6_TEMPLATES if f"`templates {t}`" not in entry]
    missing += [f"`{s}`" for s in PHASE6_SKILLS if f"`{s}`" not in entry]
    assert not missing, missing
    notes = entry.split("**Migration notes.**", 1)[1]
    for needle in ("`mode`", "`grade`", "`grade_source`", "`self_check`", "`learnings.jsonl`", "`urgency`",
                   "39 skills", "v2.1"):
        assert needle in notes, needle


@pytest.mark.parametrize("name", sorted(P6_RECIPES))
def test_recipes_cover_the_phase_6_jobs(name):
    """A Hazira recipe for each Phase 6 job, linked from Home."""
    hits = [h for h, b in sections("docs/manual/Workflows-and-recipes.md").items()
            if "Hazira" in b and all(c in b for c in P6_RECIPES[name])]
    assert hits, f"no Hazira recipe shows {P6_RECIPES[name]}"
    assert f"Workflows-and-recipes.md#{slug(hits[0])}" in read("docs/manual/Home.md"), hits[0]


def test_preset_table_has_no_stale_phase_6_planned_step():
    text = read("docs/manual/Workflows-and-recipes.md")
    row = next(line for line in text.splitlines() if line.startswith("| `sister-sites` |"))
    assert "could-it-happen-here" in row and "(Phase 6)" not in row, row


def test_library_page():
    """Library.md: what the library holds, the de-identification gate, what comes in v2.1; synthetic data only."""
    text = read("docs/manual/Library.md")
    heads = set(sections("docs/manual/Library.md"))
    for h in ("What the library holds", "The de-identification gate", "Coming in v2.1"):
        assert h in heads, (h, sorted(heads))
    for f in LIBRARY_FILES:
        assert f"`{f}`" in text, f
    assert "hazira" not in text.lower()        # owner scope change: no Hazira data in a library, even in a doc
    assert "invented" in text.lower() or "synthetic" in text.lower()
    assert "Library.md" in read("docs/manual/Home.md")


def test_files_and_folders_lists_the_phase_6_files():
    text = read("docs/manual/Files-and-folders.md")
    missing = [f for f in P6_WORKSPACE_FILES + P6_OUTPUT_FILES + LIBRARY_FILES + P6_REFERENCES
               if f"`{f}`" not in text]
    assert not missing, missing
    assert "PMLC_LIBRARY" in text and "Library.md" in text


@pytest.mark.parametrize("heading", sorted(P6_TROUBLES))
def test_troubleshooting_has_the_phase_6_problems(heading):
    found = sections("docs/manual/Troubleshooting.md")
    hit = [b for h, b in found.items() if h.lower() == heading.lower()]
    assert hit, heading
    assert P6_TROUBLES[heading] in hit[0], heading


def test_glossary_has_the_phase_6_terms():
    terms = [h.lower() for h in re.findall(r"^### (.+?)\s*$", read("docs/manual/Glossary.md"), re.M)]
    missing = [t for t in P6_TERMS if not any(h == t or h.startswith(t + " ") for h in terms)]
    assert not missing, missing


def test_smoke_covers_the_phase_6_goldens():
    """tools/smoke_sample.py checks every Phase 6 golden under check-pack --strict: each present skill's pack is a
    Hazira golden, and a missing one fails the smoke run."""
    spec = importlib.util.spec_from_file_location("smoke_sample", ROOT / "tools" / "smoke_sample.py")
    smoke = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(smoke)
    names = sorted(p.stem for p in SAMPLE_OUT.glob("*.json"))
    assert smoke.missing_goldens(names) == []
    assert set(PRESENT) <= set(smoke.missing_goldens([]))
    for s in PRESENT:
        pack = json.loads(read(f"skills/{s}/skill.json"))["produces"]["pack"]
        assert (SAMPLE_OUT / f"{pack}.json").is_file(), s
