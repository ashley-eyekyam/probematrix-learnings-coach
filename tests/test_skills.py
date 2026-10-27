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
PENDING: set = set()                       # Tasks 21-23 done: every skill is on the skeleton
HUB_PENDING: set = set()                   # Task 24 rewrote the hub (empty from here on)

SKELETON = ("Before you start", "Gather", "Write", "If the evidence is thin", "Not covered here",
            "Check and hand over")                                        # P3-19, in this order
HUB_HEADINGS = ("Where things are", "Step 1: set up", "Step 2: work out the intent", "Step 3: plan and confirm",
                "Step 4: run the plan", "Step 5: finish", "Review and sharing")   # P3-18, in this order
COMMON_HEADINGS = ("1. Engine and paths", "2. Before you start: preconditions and direct invocation",
                   "3. Pack conventions", "4. The check and pack loop", "5. Hand-over checklist",
                   "6. If the evidence is thin", "7. Sharing outside the organisation", "8. Formats")

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
    ("frontline-learning-cards", "supply-chain-contractor-learnings"),
    ("supply-chain-contractor-learnings", "frontline-learning-cards"),
    ("safety-committee-guide", "frontline-learning-cards"),
    ("latent-conditions-profile", "causal-map"), ("latent-conditions-profile", "learning-clusters"),
    ("open-questions-register", "investigator-coach"),
    ("evidence-strength-scorecard", "investigator-coach"), ("evidence-strength-scorecard", "auditor-assurance-pack"),
    ("failure-to-learn-review", "precursor-timeline"), ("failure-to-learn-review", "site-leadership-coach"),
    ("risk-register-update", "barrier-learnings"), ("risk-register-update", "board-brief"),
    ("people-workforce-learnings", "training-designer"), ("people-workforce-learnings", "manager-coach"),
    ("compliance-crosswalk", "auditor-assurance-pack"), ("compliance-crosswalk", "learnings-register"),
    ("nine-m-analysis", "barrier-learnings"), ("nine-m-analysis", "recommendation-strength-review"),
    ("recommendation-strength-review", "nine-m-analysis"), ("recommendation-strength-review", "learnings-register"),
    ("systemic-accimap", "causal-map"), ("systemic-accimap", "latent-conditions-profile"),
    ("systemic-accimap", "organisation-learning-map"),
}
NO_PROFILE = {"learnings-register"}        # writes a register, not a pack: its Write table has no profile
# Variant packs (Task 20 review m-5): a variant has the main pack's sections (rule same-sections-as), so it shares the
# skill's one Write table; its profile must equal the main profile's sections and bottom line.
# A variant is a fixture whose `skill` names this skill and whose pack is <skill>-<variant> (Ruling P4-22).
def _variants() -> dict:
    out = {}
    for p in sorted((ROOT / "tests" / "fixtures" / "packs").glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        sk = d.get("skill") if isinstance(d, dict) else None
        if isinstance(sk, str) and p.stem.startswith(sk + "-"):
            out.setdefault(sk, []).append(p.stem)
    return {k: tuple(v) for k, v in out.items()}


VARIANTS = _variants()
# Task 21: what each register and analysis skill must say after its Phase 3 changes (brief, Task 21 block).
PHASE3_TEXT = {
    "learnings-register": ("urgency", "recommendation_class", "recipient_role", "regulatory_touchpoint",
                           "verification", "why_not_stronger", "PMLC register-md", "never hand-write",
                           "check-register <ws> <run>/outputs/learnings-register.json --strict"),
    "learning-clusters": ("--org-chart", "tags", "statutory"),
    "organisation-learning-map": ("cascade", "deliverer role", "window (relative weeks)", "completion measure",
                                  "PMLC templates <ws> distribution", "reach"),
    "causal-map": ("PMLC causal <ws> --top 60 --hubs", "PMLC table-item <ws> hubs", "end on a condition"),
    "precursor-timeline": ("PMLC timeline-item <ws> --before incident", "year-only", "undated"),
    "interface-learnings": ("joint-review agenda", "co_owner", "lower id first", "mitigation"),
    "barrier-learnings": ("barriers-and-controls.md", "barrier_id", "unmapped", "ICMM", "Seveso"),
    "report-comparison": ("comparator.json", "PMLC compare", "own-action-plan", "report-comparison-regulator-safe",
                          "additional learning", "--embed summary", "legal review", "statutory_status"),
}
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


def write_table(text: str, need_kinds: bool = True) -> list:
    """Rows of the Write section-spec table as dicts {id, kinds, min, max}. AssertionError when it is missing.
    need_kinds=False (NO_PROFILE skills, Task 20 review m-4): the Kind cell names register field types, not pack
    kinds, so it is not checked."""
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
        assert kinds or not need_kinds, f"no pack kind in the Kind cell: {line}"
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

def test_no_pending_skills():
    """Ruling X8: the staging sets cannot survive Phase 3. Every skill is on the skeleton and the hub on its headings,
    so no skeleton test may skip."""
    assert PENDING == set(), f"skills still PENDING: {sorted(PENDING)}"
    assert HUB_PENDING == set(), f"hub still HUB_PENDING: {sorted(HUB_PENDING)}"


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
    assert re.search(r"required top-level `status` field to contain\s+`Learning purposes: not a statutory document`",
                     s3), "section 3 must name the required status field with the exact phrase"
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
    rows = write_table(skill_md(skill), need_kinds=skill not in NO_PROFILE)
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


@pytest.mark.parametrize("skill", sorted(VARIANTS))
def test_variant_profiles_share_the_main_sections(skill):
    ready(skill)
    profs = json.loads(read(REFS / "pack-profiles.json"))
    main = profs[profile_key(skill)]
    t = skill_md(skill)
    for v in VARIANTS[skill]:
        assert v in profs, f"{skill}: no profile {v}"
        assert profs[v]["sections"] == main["sections"] and profs[v]["bottom_line"] == main["bottom_line"], v
        assert f"same-sections-as:{profile_key(skill)}" in profs[v].get("rules", []), v
        assert f"<run>/outputs/{v}.json" in t, f"{skill}: SKILL.md must name {v}.json"


@pytest.mark.parametrize("skill", sorted(PHASE3_TEXT))
def test_phase3_changes_present(skill):
    ready(skill)
    t = skill_md(skill)
    missing = [x for x in PHASE3_TEXT[skill] if x not in t]
    assert missing == [], f"{skill}: Phase 3 text missing {missing}"
    assert len(t.splitlines()) <= 150, f"{skill}: {len(t.splitlines())} lines"


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
    for h in HUB_HEADINGS:
        assert sum(1 for x in heads if re.match(rf"^{re.escape(h)}\b", x)) == 1, f"hub: '{h}' more than once"
    assert COMMON_LINK.split("learnings-coach/", 1)[1] in skill_md(HUB)


def test_hub_description_and_principles():
    """Task 20 review m-9: the hub meets the description and principles-link rules the other 22 meet."""
    t = skill_md(HUB)
    d = description(t)
    assert "ProbeMatrix" in d and "Use when" in d
    assert len(d) <= 1024, f"hub: description is {len(d)} characters"
    assert PRINCIPLES_LINK in t
    assert len(t.splitlines()) <= 150, len(t.splitlines())


def test_hub_plans_and_waits():
    """Spec section 2.4 and D11: set up, ask one question at a time, plan, wait for the OK, run, index."""
    t = skill_md(HUB)
    s1, s2 = section(t, "Step 1: set up"), section(t, "Step 2: work out the intent")
    s3, s4, s5 = section(t, "Step 3: plan and confirm"), section(t, "Step 4: run the plan"), section(t, "Step 5: finish")
    review = section(t, "Review and sharing")
    assert "PMLC setup" in s1 and "PMLC run-manifest" in s1 and "--jurisdiction" in s1 and "--intended-use" in s1
    assert "one question at a time" in s2 and "p1_by_tier" in s2 and "PMLC facts" in s2
    presets = json.loads(read(REFS / "workflows.json"))
    for p in presets:
        assert f"`{p}`" in s2, f"hub: preset {p} is not in the routing table"
    for s in NON_HUB:
        assert f"`{s}`" in s2, f"hub: skill {s} is not in the routing table"
    assert "PMLC plan" in s3 and "wait" in s3.lower() and "OK" in s3
    assert "plan --next" in s4 or "PMLC plan <ws> --next" in s4
    assert "PMLC index" in s5 and "HTML" in s5
    assert "templates <ws> distribution" in s5 and "templates <ws> verification" in s5
    assert "sign-off" in s5 and "never" in s5.lower()
    assert "never run sign-off unless" in review
    assert "skill-common.md` §7" in review                                    # X29: sharing rules moved there
    assert "learning-principles.md` (§7)" not in t
    for x in ("first-48-hours", "Direct invocation", "Thin export", "Portability"):
        assert x in t, x


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


def test_write_table_register_rows_need_no_pack_kind():
    reg = SAMPLE.replace("| `question` (with `to`) | up to 12 |", "| text field | up to 12 |")
    with pytest.raises(AssertionError):
        write_table(reg)
    assert write_table(reg, need_kinds=False)[-1] == {"id": "questions", "kinds": [], "min": 1, "max": 12}


# ------------------------------------------------- Task 22: management-review input (L7-16), exactly six rows

MR_ROWS = ["Incidents and corrective actions", "Monitoring results", "Audit results", "Risks and opportunities",
           "Adequacy of resources", "Consultation outcomes"]
MR_SKILLS = ["top-management-brief", "site-leadership-coach", "manager-coach"]
NOT_IN = "not in this investigation"


@pytest.mark.parametrize("skill", MR_SKILLS)
def test_management_review_input_six_rows(skill):
    t = skill_md(skill)
    assert all(r in t for r in MR_ROWS) and NOT_IN in t, f"{skill}: SKILL.md must name the six inputs"
    pack = json.loads(read(ROOT / "tests" / "fixtures" / "packs" / f"{skill}.json"))
    sec = next(s for s in pack["sections"] if s["id"] == "management-review")
    tab = next(it for it in sec["items"] if it["kind"] == "table")
    assert [r[0] for r in tab["rows"]] == MR_ROWS
    det, ind = tab["columns"].index("Deterioration trigger"), tab["columns"].index("Indicator")
    for row, cites in zip(tab["rows"], tab["row_cites"]):
        assert row[det].strip() and row[ind].strip() if cites else NOT_IN in row[1].lower(), (skill, row)



# --------------------------- Tasks 24-26: skills offer their Phase 4 formats (`formats` in skill.json; L2-08)
# A skill that lists `formats` in its skill.json offers each one in "Check and hand over" with a runnable `PMLC` line
# (`--format <names>` or `--layout <name>`; `register-render --format` for the register), and its Write section
# links the Hazira worked example. Tasks 24, 25 and 26 add `formats` group by group; these tests pick each skill up
# as soon as its skill.json has the key.

from pmlc_lib import render as _p4s_render  # noqa: E402
from pmlc_lib.render.layouts import LAYOUTS as _P4S_LAYOUTS  # noqa: E402

P4S_SAMPLE_OUT = "samples/2020-09-24-hazira-gas-release-fire/outputs/"
P4S_WORKED = re.compile(r"^Worked example: `?" + re.escape(P4S_SAMPLE_OUT)
                        + r"([A-Za-z0-9-]+\.json)`? \(repository only\)\.?$", re.M)
P4S_GROUP_A = ("board-brief", "top-management-brief", "site-leadership-coach", "manager-coach",
               "safety-committee-guide", "organisation-learning-map", "learnings-register")


def _p4s_manifest(skill: str) -> dict:
    return json.loads(read(SKILLS_DIR / skill / "skill.json"))


P4S_OFFERS = [s for s in ALL_SKILLS if "formats" in _p4s_manifest(s)]


def _p4s_offered(text: str) -> set:
    """Format and layout names offered by the `PMLC …` lines of a SKILL.md's "Check and hand over" section."""
    out = set()
    for line in section(text, "Check and hand over").splitlines():
        cmd = line.split("#", 1)[0]
        if not cmd.strip().startswith("PMLC "):
            continue
        for m in re.finditer(r"--format[ =]([A-Za-z0-9,-]+)", cmd):
            out |= set(m.group(1).split(","))
        out |= set(re.findall(r"--layout[ =]([a-z]+)", cmd))
    return out


def test_group_a_skills_declare_formats():
    """Task 24: every group A skill names the formats it offers by default."""
    assert [s for s in P4S_GROUP_A if s not in P4S_OFFERS] == []


@pytest.mark.parametrize("skill", P4S_OFFERS)
def test_skill_formats_registered(skill):
    fmts = _p4s_manifest(skill)["formats"]
    assert isinstance(fmts, list) and fmts and len(set(fmts)) == len(fmts), f"{skill}: formats {fmts}"
    known = set(_p4s_render.FORMATS) | set(_P4S_LAYOUTS)
    assert [f for f in fmts if f not in known] == [], f"{skill}: not a registered format or layout"
    assert not {"html", "md"} & set(fmts), f"{skill}: html and md are every pack's defaults; list only extras"


@pytest.mark.parametrize("skill", P4S_OFFERS)
def test_skill_mentions_its_formats(skill):
    t = skill_md(skill)
    hand = section(t, "Check and hand over")
    offered = _p4s_offered(t)
    fmts = _p4s_manifest(skill)["formats"]
    assert [f for f in fmts if f not in offered] == [], f"{skill}: formats without a PMLC line in Check and hand over"
    assert [f for f in offered if f not in fmts] == [], f"{skill}: a PMLC line offers a format skill.json lacks"
    assert "--strict" in hand and re.search(r"^PMLC (pack|register-md) ", hand, re.M), f"{skill}: X28 lines kept"
    assert len(t.splitlines()) <= 150, f"{skill}: {len(t.splitlines())} lines"


@pytest.mark.parametrize("skill", P4S_OFFERS)
def test_skill_links_worked_example(skill):
    write = section(skill_md(skill), "Write")
    found = P4S_WORKED.findall(write)
    assert len(found) == 1, f"{skill}: Write needs one 'Worked example: {P4S_SAMPLE_OUT}<pack>.json (repository only)'"
    pack = _p4s_manifest(skill)["produces"]["pack"] or ""
    stem = found[0][: -len(".json")]
    assert stem == pack or stem.startswith(pack.split("<", 1)[0]), f"{skill}: worked example {stem} is not its pack"
    assert (ROOT / P4S_SAMPLE_OUT / found[0]).is_file(), f"{skill}: {found[0]} is not in the Hazira samples"


def test_p4s_offered_parser():
    t = ("## Check and hand over\n\n```bash\nPMLC pack <ws> x.json --format docx,pptx --layout paper   # a\n"
         "PMLC pack <ws> x.json --format=email\n# PMLC pack <ws> x.json --format gift\n"
         "PMLC register-render <ws> r.json --format docx,email\n```\n")
    assert _p4s_offered(t) == {"docx", "pptx", "paper", "email"}


def test_skill_common_formats_section():
    """Task 24: skill-common.md §8 says which format suits which channel, that shared copies cover every format, and
    that translation goes through `strings`; output-style.md describes the engine's formats."""
    t = read(REFS / "skill-common.md")
    assert headings(t)[-1] == "8. Formats"
    s8 = section(t, "8. Formats")
    for x in ("--format", "--layout", "docx", "pptx", "email", "paper", "checklist", "toolbox", "cards", "ics",
              "--start", "gift", "svg", "register-render", "--share external", "strings extract", "strings apply",
              "fluent speaker", "back_translation", "--view learner", "nothing to write"):
        assert x in s8, x
    assert "strings" in section(t, "3. Pack conventions") and "§8" in section(t, "3. Pack conventions")
    style = read(REFS / "output-style.md")
    default, converted = section(style, "Default format"), section(style, "Converted files")
    assert "--format" in default and "register-render" in default and "skill-common.md" in default
    assert "only when the user asks, using whatever document tools" not in default
    assert "creator" in converted and "docx" in converted and "pptx" in converted


# ------------------------------------------------- Task 26: skills group C offer their Phase 4 formats
# The generic format tests are the Task 24 block above; these are the group C specifics.

from pmlc_lib.render import FORMATS as C_FORMATS  # noqa: E402
from pmlc_lib.render.layouts import LAYOUTS as C_LAYOUTS  # noqa: E402

C_SAMPLE_OUT = "samples/2020-09-24-hazira-gas-release-fire/outputs"
C_SKILL_FORMATS = {            # skill.json `formats`: what each group C skill offers beyond html and md
    "learning-clusters": ("docx",),
    "causal-map": ("svg", "png", "graphml", "pptx"),
    "precursor-timeline": ("poster",),
    "interface-learnings": ("docx",),
    "barrier-learnings": ("bowtie-csv",),
    "cluster-learning-dossier": ("docx",),
    "auditor-assurance-pack": ("checklist",),
    "investigator-coach": (),  # follow-up.csv is written by every pack run (not a format, Task 17)
    "report-comparison": ("docx",),
}
C_DOC_PACK = {"cluster-learning-dossier": "dossier-<F-id>"}       # the pack name the SKILL.md command lines use
C_PACK_LINE = re.compile(r"^PMLC pack <ws> <run>/outputs/(\S+)\.json(.*)$", re.M)


def c_pack_lines(skill: str) -> list:
    """(pack, flags) for each `PMLC pack` line in Check and hand over, comments dropped."""
    body = section(skill_md(skill), "Check and hand over")
    return [(m.group(1), m.group(2).split("#", 1)[0]) for m in C_PACK_LINE.finditer(body)]


def test_group_c_skills_declare_formats():
    """Task 26: each group C skill offers exactly these formats; registration, the PMLC lines and the worked example
    are checked for every skill with `formats` by the Task 24 tests above."""
    got = {s: tuple(json.loads(read(SKILLS_DIR / s / "skill.json")).get("formats", ())) for s in C_SKILL_FORMATS}
    assert got == C_SKILL_FORMATS
    assert [s for s in C_SKILL_FORMATS if C_SKILL_FORMATS[s] and s not in P4S_OFFERS] == []


@pytest.mark.parametrize("skill", sorted(C_SKILL_FORMATS))
def test_group_c_x28_lines_name_the_pack(skill):
    pack = C_DOC_PACK.get(skill, skill)
    body = section(skill_md(skill), "Check and hand over")
    assert f"PMLC check-pack <ws> <run>/outputs/{pack}.json --strict" in body, f"{skill}: X28 check-pack line"
    assert f"PMLC pack <ws> <run>/outputs/{pack}.json" in body, f"{skill}: X28 pack line"


def test_investigator_coach_links_worked_example():
    """investigator-coach offers no format, so the Task 24 worked-example test does not reach it."""
    rel = f"{C_SAMPLE_OUT}/investigator-coach.json"
    assert f"Worked example: {rel} (repository only)" in section(skill_md("investigator-coach"), "Write")
    assert (ROOT / rel).is_file(), rel


def test_group_c_skill_specific_formats():
    bar = skill_md("barrier-learnings")
    assert "bowtie-csv" in section(bar, "Check and hand over") and "For a bow-tie, map the" not in bar
    inv = skill_md("investigator-coach")
    assert "`RMP-68.81`" in section(inv, "Write") and "follow-up.csv" in section(inv, "Check and hand over")
    aud = section(skill_md("auditor-assurance-pack"), "Check and hand over")
    assert "PMLC pack-xlsx <ws> <run>/outputs/auditor-assurance-pack.json --kind test_point" in aud
    rc = c_pack_lines("report-comparison")
    for variant in ("report-comparison-client-safe", "report-comparison-regulator-safe"):
        assert any(p == variant and "docx" in flags for p, flags in rc), f"no docx line for {variant}"
    cm = c_pack_lines("causal-map")
    assert any("pptx" in flags for _, flags in cm) and "graph slide" in skill_md("causal-map")


def test_dossier_formats_row_names_real_layouts():
    row = next(line for line in section(skill_md("cluster-learning-dossier"), "Write").splitlines()
               if line.startswith("| S14 "))
    named = set(re.findall(r"--layout (\w+)", row)) | set(re.findall(r"--format (\w+)", row))
    assert {"cards", "toolbox"} <= named, row
    assert named <= set(C_LAYOUTS) | set(C_FORMATS), row
    assert "Brief paragraph" not in row


@pytest.mark.parametrize("skill, sec", [("auditor-assurance-pack", "evidence-requests"),
                                        ("investigator-coach", "interview-plan")])
def test_group_c_counts_are_bounded(skill, sec):
    """Task 22 (Phase 3) minor 3: open-ended "at least 1" counts become "up to N" (L2-17)."""
    rows = [r for r in write_table(skill_md(skill)) if r["id"] == sec]
    assert rows and all(r["max"] < NO_LIMIT for r in rows), rows


# ------------------------------------------------- Task 25: skills group B offer their Phase 4 formats
# The generic format tests are the Task 24 block above; these are the group B specifics.

B_SKILL_FORMATS = {            # skill.json `formats`: what each group B skill offers beyond html and md
    "frontline-learning-cards": ["cards", "field", "toolbox"],
    "supervisor-coach": ["checklist"],
    "emergency-response-learnings": ["cards", "pptx"],
    "training-designer": ["docx", "gift", "qti", "quiz-csv", "scorm", "srt", "narration"],
    "supply-chain-contractor-learnings": ["email"],
    "engineering-integrity-learnings": ["docx", "csv"],
}
# Review I-1: a person, never the AI, checks a translation and its back-translations before it is issued.
B_FLUENT_CHECK = ("must not be issued until a fluent speaker of the target language, not the AI, has checked the "
                  "whole translation and compared every safety-critical item's back-translation with its English "
                  "source")
# What each group B skill must say about its Phase 4 formats and fields (Task 25 brief).
B_SKILL_TEXT = {
    "frontline-learning-cards": ("--base-url", "did_you_know", "what_you_can_do", "opening_question",
                                 "crew_question", "PMLC strings extract", "PMLC strings apply", "back_translation",
                                 "fluent speaker", "frontline-learning-cards-hi.json", B_FLUENT_CHECK),
    "supervisor-coach": ("distribution.csv", "hold_point"),
    "emergency-response-learnings": ("injects", "offset", "drill brief"),
    "training-designer": ('"type"', '"options"', "--view learner", "`script`", "segments"),
    "supply-chain-contractor-learnings": ("PMLC strings extract", "PMLC strings apply", "fluent speaker",
                                          "--share external", B_FLUENT_CHECK),
    "engineering-integrity-learnings": ("actions.csv", "never overwrit"),
}
# Task 16 m4: the manual pages name the optional toolbox and script items.
B_MANUAL_TEXT = {"frontline-learning-cards": ("toolbox", B_FLUENT_CHECK), "training-designer": ("script", "srt", "scorm"),
                 "supply-chain-contractor-learnings": (B_FLUENT_CHECK,)}


def test_group_b_skills_declare_formats():
    got = {s: _p4s_manifest(s).get("formats") for s in B_SKILL_FORMATS}
    assert got == B_SKILL_FORMATS


@pytest.mark.parametrize("skill", sorted(B_SKILL_FORMATS))
def test_group_b_x28_lines_and_specifics(skill):
    t = skill_md(skill)
    hand = section(t, "Check and hand over")
    pack = _p4s_manifest(skill)["produces"]["pack"]
    for x in (f"PMLC check-pack <ws> <run>/outputs/{pack}.json --strict", f"PMLC pack <ws> <run>/outputs/{pack}.json\n"):
        assert x in hand, f"{skill}: the X28 line {x.strip()!r} must stay"
    flat = " ".join(t.split())                       # the rule may wrap across lines
    missing = [x for x in B_SKILL_TEXT[skill] if x not in flat]
    assert missing == [], f"{skill}: missing {missing}"


@pytest.mark.parametrize("skill", sorted(B_SKILL_FORMATS))
def test_group_b_manual_page_names_formats(skill):
    page = read(ROOT / "docs" / "manual" / "skills" / f"{skill}.md")
    for f in B_SKILL_FORMATS[skill]:
        flag = "--layout" if f in _P4S_LAYOUTS else "--format"
        assert re.search(rf"{flag} (\S+,)?{re.escape(f)}\b", page), f"{skill}: manual page lacks {flag} {f}"
    missing = [x for x in B_MANUAL_TEXT.get(skill, ()) if x not in page]
    assert missing == [], f"{skill}: manual page lacks {missing}"
