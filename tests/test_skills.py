"""Skill structure tests (Rulings P3-18, P3-19; L2-01, L2-04, L2-05, L2-06, L3-08).

Every non-hub skill follows the standard skeleton (CONTRIBUTING.md "Skill skeleton"). Skills still in PENDING skip
the skeleton tests until their group task (Tasks 21 to 23) restructures them and removes their names; the hub skips
test_hub_headings until Task 24 removes it from HUB_PENDING. test_cited_references_exist never skips.

The Write table (one row per section entry, `| § | id | Heading | Content rule | Kind | Count |`) must give the same
ids, kinds and counts as the skill's entry in references/pack-profiles.json. Count grammar (parse_count):
  "N"                  min N, max N
  "up to N"            min 1, max N
  "N–M" (or "N-M")     min N, max M
  "at least N", "N or more"   min N, no limit (max 99)
  "optional"           min 0, no limit; "optional, up to N" gives min 0, max N
Text in parentheses is ignored, so "up to 12 (mix: this site, all sites)" is "up to 12".
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
REFS = SKILLS_DIR / "learnings-coach" / "references"
sys.path.insert(0, str(SKILLS_DIR / "learnings-coach" / "scripts"))
from pmlc_lib.pack.schema import KINDS  # noqa: E402

HUB = "learnings-coach"
ALL_SKILLS = sorted(p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md"))
NON_HUB = [s for s in ALL_SKILLS if s != HUB]

# Tasks 21-23 remove their skills' names as each skill reaches the skeleton (staged, Ruling X8).
PENDING = {
    # Task 21: register and analysis
    "learnings-register", "learning-clusters", "organisation-learning-map", "causal-map", "precursor-timeline",
    "interface-learnings", "barrier-learnings", "report-comparison",
    # Task 22: leadership, assurance and investigation
    "board-brief", "top-management-brief", "site-leadership-coach", "manager-coach", "cluster-learning-dossier",
    "auditor-assurance-pack", "investigator-coach",
    # Task 23: frontline and specialists
    "frontline-learning-cards", "supervisor-coach", "safety-committee-guide", "training-designer",
    "emergency-response-learnings", "engineering-integrity-learnings", "supply-chain-contractor-learnings",
}
HUB_PENDING = {"learnings-coach"}          # Task 24 removes it when the hub is rewritten

SKELETON = ("Before you start", "Gather", "Write", "If the evidence is thin", "Not covered here",
            "Check and hand over")                                        # P3-19, in this order
HUB_HEADINGS = ("Where things are", "Step 1: set up", "Step 2: work out the intent", "Step 3: plan and confirm",
                "Step 4: run the plan", "Step 5: finish", "Review and sharing")   # P3-18, in this order
COMMON_HEADINGS = ("1. Engine and paths", "2. Before you start: preconditions and direct invocation",
                   "3. Pack conventions", "4. The check and pack loop", "5. Hand-over checklist",
                   "6. If the evidence is thin", "7. Sharing outside the organisation")

# L2-04 tie-breaks: (skill, sibling) means the skill's description says "Not for ..." and names the sibling.
OVERLAPS = {
    ("manager-coach", "site-leadership-coach"), ("manager-coach", "cluster-learning-dossier"),
    ("site-leadership-coach", "manager-coach"), ("cluster-learning-dossier", "manager-coach"),
    ("learning-clusters", "organisation-learning-map"), ("organisation-learning-map", "learning-clusters"),
    ("organisation-learning-map", "learnings-register"),
    ("top-management-brief", "board-brief"), ("board-brief", "top-management-brief"),
    ("top-management-brief", "auditor-assurance-pack"),
    ("auditor-assurance-pack", "top-management-brief"), ("auditor-assurance-pack", "board-brief"),
    ("frontline-learning-cards", "emergency-response-learnings"), ("emergency-response-learnings", "frontline-learning-cards"),
    ("frontline-learning-cards", "supervisor-coach"), ("supervisor-coach", "frontline-learning-cards"),
    ("frontline-learning-cards", "training-designer"), ("training-designer", "frontline-learning-cards"),
    ("barrier-learnings", "engineering-integrity-learnings"), ("engineering-integrity-learnings", "barrier-learnings"),
}
NO_PROFILE = {"learnings-register"}        # writes a register, not a pack: its Write table has no profile
WRITE_HEADER = ["§", "id", "heading", "content rule", "kind", "count"]
NO_LIMIT = 99
COMMON_LINK = "learnings-coach/references/skill-common.md"
PRINCIPLES_LINK = "learnings-coach/references/learning-principles.md"


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def skill_md(name: str) -> str:
    return read(SKILLS_DIR / name / "SKILL.md")


def headings(text: str, level: str = "##") -> list:
    return [m.group(1).strip() for m in re.finditer(rf"^{level} (.+)$", text, re.M)]


def section(text: str, heading: str) -> str:
    """The body under the first `## <heading…>` up to the next `## ` heading ('' when absent)."""
    m = re.search(rf"^## {re.escape(heading)}\b.*$", text, re.M)
    if not m:
        return ""
    rest = text[m.end():]
    n = re.search(r"^## ", rest, re.M)
    return rest[:n.start()] if n else rest


def heading_order(heads: list, wanted) -> list:
    """For each wanted heading, the index of the first `##` heading that starts with it (None when missing)."""
    out = []
    for w in wanted:
        rx = re.compile(rf"^{re.escape(w)}\b")
        out.append(next((i for i, h in enumerate(heads) if rx.match(h)), None))
    return out


def description(text: str) -> str:
    """The front-matter description, joining folded or indented continuation lines."""
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert fm, "no front matter"
    lines = fm.group(1).splitlines()
    for i, line in enumerate(lines):
        if line.startswith("description:"):
            first = line.split(":", 1)[1].strip()
            more = []
            for x in lines[i + 1:]:
                if x[:1] in (" ", "\t"):
                    more.append(x.strip())
                else:
                    break
            if first in (">", "|", ">-", "|-"):
                first = ""
            return " ".join([first] + more).strip().strip("\"'")
    raise AssertionError("no description")


def parse_count(cell: str) -> tuple:
    """(min, max) from a Count cell (module docstring); ValueError when it does not parse."""
    t = re.sub(r"\([^)]*\)", "", cell).replace("`", "").strip().lower()
    t = re.sub(r"\s+", " ", t).rstrip(".")
    lo = 1
    if t.startswith("optional"):
        lo, t = 0, t[len("optional"):].lstrip(" ,;").strip()
        if not t:
            return 0, NO_LIMIT
    m = re.fullmatch(r"up to (\d+)", t)
    if m:
        return lo, int(m.group(1))
    m = re.fullmatch(r"(\d+) ?[–-] ?(\d+)", t)
    if m and lo:
        return int(m.group(1)), int(m.group(2))
    m = re.fullmatch(r"(?:at least (\d+)|(\d+) or more)", t)
    if m and lo:
        return int(m.group(1) or m.group(2)), NO_LIMIT
    m = re.fullmatch(r"(\d+)", t)
    if m and lo:
        return int(m.group(1)), int(m.group(1))
    raise ValueError(f"unreadable Count {cell!r}")


def parse_kinds(cell: str) -> list:
    """The pack kinds named in a Kind cell (text in parentheses is a note, not a kind)."""
    t = re.sub(r"\([^)]*\)", "", cell)
    kinds = [k for k in re.findall(r"[a-z_]+", t) if k in KINDS or k == "bottom_line"]
    return list(dict.fromkeys(kinds))


def write_table(text: str) -> list:
    """Rows of the Write section-spec table as dicts {id, kinds, min, max}. AssertionError when it is missing."""
    body = section(text, "Write")
    lines = body.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip().startswith("|"):
            cells = [c.strip().replace("`", "").lower() for c in line.strip().strip("|").split("|")]
            if cells == WRITE_HEADER:
                start = i
                break
    assert start is not None, "no Write table with the header | § | id | Heading | Content rule | Kind | Count |"
    rows = []
    for line in lines[start + 2:]:
        if not line.strip().startswith("|"):
            break
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        assert len(cells) == 6, f"Write row has {len(cells)} cells, expected 6: {line}"
        kinds = parse_kinds(cells[4])
        assert kinds, f"no pack kind in the Kind cell: {line}"
        lo, hi = parse_count(cells[5])
        rows.append({"id": cells[1].replace("`", "").strip(), "kinds": sorted(kinds), "min": lo, "max": hi})
    assert rows, "the Write table has no rows"
    return rows


def profile_key(skill: str) -> str:
    pack = json.loads(read(SKILLS_DIR / skill / "skill.json"))["produces"]["pack"]
    if pack and "<" in pack:                                   # dossier-<F-id>: the profile is keyed dossier-F02
        profs = json.loads(read(REFS / "pack-profiles.json"))
        rx = re.compile("^" + re.escape(pack.split("<", 1)[0]) + r"F\d+[a-z]?$")
        pack = next((k for k in profs if rx.match(k)), pack)
    return pack


def ready(skill):
    if skill in PENDING:
        pytest.skip(f"{skill}: not on the skeleton yet (PENDING)")


# ------------------------------------------------------------------------------------------------ never skipped

def test_pending_names_real_skills():
    assert PENDING <= set(NON_HUB), PENDING - set(NON_HUB)
    assert HUB_PENDING <= {HUB}
    assert {a for a, _ in OVERLAPS} | {b for _, b in OVERLAPS} <= set(NON_HUB)


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_cited_references_exist(skill):
    """Every references/<file> a SKILL.md names exists: <skill>/references/<file> by that skill's folder, a bare
    references/<file> in the skill's own folder or the hub's."""
    text = skill_md(skill)
    missing = []
    for m in re.finditer(r"(?:\b([a-z0-9-]+)/)?references/([A-Za-z0-9_.\-/]*[A-Za-z0-9_/])", text):
        owner, rel = m.group(1), m.group(2)
        if owner and owner in ("skills",):
            owner = None
        cands = [SKILLS_DIR / owner / "references" / rel] if owner else \
            [SKILLS_DIR / skill / "references" / rel, REFS / rel]
        if not any(c.exists() for c in cands):
            missing.append(m.group(0))
    assert missing == [], f"{skill}/SKILL.md names missing references: {missing}"


def test_skill_common_sections():
    t = read(REFS / "skill-common.md")
    assert headings(t) == list(COMMON_HEADINGS)
    s2 = section(t, "2. Before you start")
    assert "PMLC setup" in s2 and "learnings-register.json" in s2
    s3 = section(t, "3. Pack conventions")
    for x in ('learning: "LR-', "clauses", "gaps", "limits", "data_quality", "exclusions", "supporting_cites",
              "translat"):
        assert x in s3, x
    s4 = section(t, "4. The check and pack loop")
    assert "check-pack" in s4 and "--strict" in s4 and "PMLC pack" in s4
    s5 = section(t, "5. Hand-over checklist")
    assert "HTML path first" in s5
    s6 = section(t, "6. If the evidence is thin")
    for x in ("up to N", "at least one per supported theme", "inferred", "padding"):
        assert x in s6, x
    s7 = section(t, "7. Sharing outside the organisation")
    for x in ("legal review", "--share external", "--embed summary", "client-safe", "privilege"):
        assert x in s7, x
    assert "PMLC = python3" in section(t, "1. Engine and paths")          # defined once, here


def test_principles_fixes():
    t = read(REFS / "learning-principles.md")
    assert "7. Review status and draft learnings" in headings(t)
    assert "Sharing outside the organisation" not in headings(t)
    s2 = section(t, "2. Ground every sentence")
    assert "AI Justification" in s2 and "the analysis states" in s2
    assert "independent" in s2 and "same source" in s2
    s6 = section(t, "6. Recommendations, not action plans")
    assert "by_when" in s6 and "relative horizon" in s6 and "a role" in s6
    s7 = section(t, "7. Review status and draft learnings")
    assert "User Edited" in s7 and "draft learnings" in s7 and "data_quality" in s7


# ------------------------------------------------------------------------------------- skeleton (skip PENDING)

@pytest.mark.parametrize("skill", NON_HUB)
def test_skeleton_headings(skill):
    ready(skill)
    heads = headings(skill_md(skill))
    idx = heading_order(heads, SKELETON)
    missing = [h for h, i in zip(SKELETON, idx) if i is None]
    assert missing == [], f"{skill}: missing headings {missing}"
    assert idx == sorted(idx), f"{skill}: headings out of order {heads}"
    for h in SKELETON:
        assert sum(1 for x in heads if re.match(rf"^{re.escape(h)}\b", x)) == 1, f"{skill}: '{h}' more than once"


@pytest.mark.parametrize("skill", NON_HUB)
def test_description_rules(skill):
    ready(skill)
    d = description(skill_md(skill))
    assert "ProbeMatrix" in d and "Use when" in d
    assert len(d) <= 1024, f"{skill}: description is {len(d)} characters"
    first = re.match(r"[A-Za-z]+", d)
    assert first and first.group(0).endswith("s"), f"{skill}: description should open in the third person"
    for a, b in sorted(OVERLAPS):
        if a == skill:
            assert "Not for" in d and b in d, f"{skill}: description needs 'Not for ... (use {b})'"


@pytest.mark.parametrize("skill", NON_HUB)
def test_links_skill_common(skill):
    ready(skill)
    t = skill_md(skill)
    assert COMMON_LINK in t
    before, hand = section(t, "Before you start"), section(t, "Check and hand over")
    assert "skill-common.md" in before and "§1" in before, f"{skill}: Before you start must link skill-common §1"
    assert "§4" in hand and "§5" in hand, f"{skill}: Check and hand over must run skill-common §4 and tick §5"


@pytest.mark.parametrize("skill", NON_HUB)
def test_cites_principles_full_path(skill):
    ready(skill)
    assert PRINCIPLES_LINK in skill_md(skill)


@pytest.mark.parametrize("skill", NON_HUB)
def test_write_table_matches_profile(skill):
    ready(skill)
    rows = write_table(skill_md(skill))
    if skill in NO_PROFILE:
        return
    profs = json.loads(read(REFS / "pack-profiles.json"))
    key = profile_key(skill)
    assert key in profs, f"{skill}: no profile {key} in pack-profiles.json"
    prof = profs[key]
    bl = [r for r in rows if r["kinds"] == ["bottom_line"] or r["id"] == "bottom_line"]
    body = [r for r in rows if r not in bl]
    want = [{"id": e["id"], "kinds": sorted(e["kinds"]), "min": e["min"], "max": e["max"]} for e in prof["sections"]]
    assert body == want, f"{skill}: Write table and pack-profiles.json {key} differ"
    for r in bl:
        lim = prof.get("bottom_line") or {}
        assert (r["min"], r["max"]) == (lim.get("min"), lim.get("max")), f"{skill}: bottom_line count differs"


@pytest.mark.parametrize("skill", NON_HUB)
def test_no_repeated_boilerplate(skill):
    ready(skill)
    t = skill_md(skill)
    assert "PMLC = python3" not in t, f"{skill}: the PMLC definition lives in skill-common.md §1"
    assert not re.search(r"data_quality[^.\n]*exclusions|exclusions[^.\n]*data_quality", t), \
        f"{skill}: the data_quality / exclusions sentence lives in skill-common.md §3"


# ------------------------------------------------------------------------------------------------------- hub

def test_hub_headings():
    if HUB in HUB_PENDING:
        pytest.skip("learnings-coach: hub rewrite pending (Task 24)")
    heads = headings(skill_md(HUB))
    idx = heading_order(heads, HUB_HEADINGS)
    assert None not in idx, f"hub: missing {[h for h, i in zip(HUB_HEADINGS, idx) if i is None]}"
    assert idx == sorted(idx), f"hub: headings out of order {heads}"
    assert COMMON_LINK.split("learnings-coach/", 1)[1] in skill_md(HUB)


# ------------------------------------------------------------------------------------- the parsers themselves

@pytest.mark.parametrize("cell,want", [
    ("3", (3, 3)), ("up to 12", (1, 12)), ("up to 12 (mix: this site, all sites)", (1, 12)), ("3–5", (3, 5)),
    ("1-7", (1, 7)), ("at least 1", (1, NO_LIMIT)), ("2 or more", (2, NO_LIMIT)), ("optional", (0, NO_LIMIT)),
    ("optional, up to 4", (0, 4)), ("`up to 8`", (1, 8)),
])
def test_parse_count(cell, want):
    assert parse_count(cell) == want


@pytest.mark.parametrize("cell", ["", "several", "optional 3-5", "up to", "eight"])
def test_parse_count_refuses(cell):
    with pytest.raises(ValueError):
        parse_count(cell)


SAMPLE = """---
name: sample-skill
description: Produces a sample from a ProbeMatrix investigation export. Use when testing. Not for real work
  (use `board-brief`).
---

# Sample

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 and §2.

## Gather

## Write

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | Three points | `bottom_line` | 1–7 |
| 1 | `what-happened` | What happened | One paragraph | `para` | at least 1 |
| 2 | `questions` | Questions | Board format | `question` (with `to`) | up to 12 |

## If the evidence is thin

## Not covered here

## Check and hand over

Run `skill-common.md` §4, then tick §5.
"""


def test_write_table_parser():
    rows = write_table(SAMPLE)
    assert rows == [{"id": "bottom_line", "kinds": ["bottom_line"], "min": 1, "max": 7},
                    {"id": "what-happened", "kinds": ["para"], "min": 1, "max": NO_LIMIT},
                    {"id": "questions", "kinds": ["question"], "min": 1, "max": 12}]
    assert description(SAMPLE).endswith("(use `board-brief`).")
    assert heading_order(headings(SAMPLE), SKELETON) == [0, 1, 2, 3, 4, 5]
    with pytest.raises(AssertionError):
        write_table(SAMPLE.replace("| Count |", "| How many |"))
