"""The user manual's guide and skill pages (docs/manual/, D18): every skill has a page with the agreed headings,
the guide pages are written, and their links, flags and quoted engine messages are real."""
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "docs" / "manual"
SCRIPTS = ROOT / "skills" / "learnings-coach" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import pmlc  # noqa: E402

REPO_BLOB = "https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/"
GUIDES = ["Getting-started.md", "Workflows-and-recipes.md", "Skills.md", "Files-and-folders.md",
          "Review-and-sharing.md", "Language-checks.md", "Troubleshooting.md", "Glossary.md"]
SKILLS = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))
SKILL_COUNT = len(list((ROOT / "skills").glob("*/skill.json")))      # P5-1: derived from the folders
SKILL_HEADINGS = ["What it is for", "How to start it", "What it needs", "Engine commands and flags", "What you get",
                  "Worked example (Hazira)", "Related skills"]
# Pages Task 13 writes (they exist once both tasks are merged).
SUBCOMMANDS = ["ingest", "profile", "classify", "select", "causal", "timeline", "interfaces", "dashboard",
               "check-register", "check-language", "register-xlsx", "status", "run-path", "check-samples",
               "check-pack", "pack", "causal-item", "sign-off", "scan-names", "run-manifest", "purge", "setup",
               "check-all", "render-all", "index", "dossier-index", "templates", "export-actions", "plan", "compare",
               "register-md", "table-item", "register-items", "timeline-item", "facts", "pack-xlsx", "register-render"]
SUBCOMMANDS += ["strings", "crosswalk", "hfacs-profile", "open-questions", "rec-review", "nine-m-seed",
                "missed-opportunities", "evidence-audit"]
SUBCOMMANDS += ["wai-wad"]
SUBCOMMANDS += ["nine-m-suggest", "nine-m-answer", "nine-m-replay", "nine-m-actions-template"]
T13_PAGES = {"Home.md", "Commands.md", "Developer-tools.md"} | {f"commands/{c}.md" for c in SUBCOMMANDS}
# Flags of other programs the pages quote (pip).
OTHER_FLAGS = {"--user"}
STUB = "This page is being written."
REQUIRED_TERMS = ["HFACS", "Unsafe Acts", "Preconditions", "Supervision", "Organisational Influences", "Tier",
                  "Entity", "Relation", "Finding", "Evidence", "Pack", "Register", "LR-ID", "Handling", "Embed",
                  "Share", "Hierarchy of controls", "Just culture"]
LINK_RX = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)\s]+)\)")


def owned_pages() -> list:
    return [MANUAL / g for g in GUIDES] + [MANUAL / "skills" / f"{s}.md" for s in SKILLS]


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def headings(text: str, level: int) -> list:
    """Headings of one level, outside fenced code blocks."""
    out, fence = [], False
    for line in text.splitlines():
        if line.startswith("```"):
            fence = not fence
            continue
        m = re.match(r"^(#{1,6}) (.+?)\s*$", line)
        if not fence and m and len(m.group(1)) == level:
            out.append(m.group(2))
    return out


def sections(text: str, level: int = 2) -> dict:
    """{heading: body} for the headings of one level."""
    out, cur, fence = {}, None, False
    for line in text.splitlines():
        if line.startswith("```"):
            fence = not fence
        m = None if fence else re.match(r"^(#{1,6}) (.+?)\s*$", line)
        if m and len(m.group(1)) == level:
            cur = m.group(2)
            out[cur] = []
        elif m and len(m.group(1)) < level:
            cur = None
        elif cur is not None:
            out[cur].append(line)
    return {k: "\n".join(v) for k, v in out.items()}


def slug(heading: str) -> str:
    """GitHub heading anchor: lower case, punctuation dropped, spaces to hyphens."""
    s = re.sub(r"[`*_]", "", heading).strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def parser_flags() -> dict:
    """{subcommand: {long option strings}} from the engine's parser."""
    p = pmlc.build_parser()
    sub = next(a for a in p._actions if a.__class__.__name__ == "_SubParsersAction")
    return {name: {o for a in sp._actions for o in a.option_strings if o.startswith("--")}
            for name, sp in sub.choices.items()}


@pytest.mark.parametrize("page", GUIDES)
def test_guide_page_exists(page):
    assert (MANUAL / page).is_file(), page


def test_every_skill_has_a_page():
    assert len(SKILLS) == SKILL_COUNT
    missing = [s for s in SKILLS if not (MANUAL / "skills" / f"{s}.md").is_file()]
    assert not missing, missing
    extra = sorted(p.stem for p in (MANUAL / "skills").glob("*.md") if p.stem not in SKILLS)
    assert not extra, extra


@pytest.mark.parametrize("skill", SKILLS)
def test_skill_page_headings(skill):
    text = read(MANUAL / "skills" / f"{skill}.md")
    assert headings(text, 1) and headings(text, 1)[0].startswith(skill), skill
    assert headings(text, 2) == SKILL_HEADINGS, skill
    starts = sections(text)["How to start it"]
    prompts = [x for x in starts.splitlines() if x.startswith(("- \"", "- *\"", "> "))]
    assert 2 <= len(prompts) <= 3, (skill, prompts)


@pytest.mark.parametrize("skill", SKILLS)
def test_skill_page_names_its_select_filters_and_preset(skill):
    """The engine section names every select flag the skill's SKILL.md uses, and its preset when it has one."""
    body = sections(read(MANUAL / "skills" / f"{skill}.md"))["Engine commands and flags"]
    src = read(ROOT / "skills" / skill / "SKILL.md")
    used = set()
    for line in src.splitlines():
        if re.search(r"\bPMLC select\b", line):
            used |= set(re.findall(r"(?<![\w-])--[a-z][a-z-]*", line.split("#")[0]))
    missing = sorted(f for f in used if f"`{f}" not in body and f" {f}" not in body)
    assert not missing, (skill, missing)
    presets = json.loads(read(ROOT / "skills" / "learnings-coach" / "references" / "select-presets.json"))
    if skill in presets:
        assert f"--preset {skill}" in body, skill
    if used or skill in presets:
        assert "commands/select.md" in body, skill


def test_no_stub_pages_left():
    stubs = [p.relative_to(MANUAL).as_posix() for p in sorted(MANUAL.rglob("*.md")) if STUB in read(p)]
    assert not stubs, stubs


def test_recipes_count():
    text = read(MANUAL / "Workflows-and-recipes.md")
    recipes = headings(text, 2)
    assert len(recipes) >= 12, len(recipes)
    for h, body in sections(text).items():
        for part in ("Goal", "Prompt", "Engine commands", "What to check"):
            assert f"**{part}" in body, (h, part)


def test_glossary_terms():
    terms = headings(read(MANUAL / "Glossary.md"), 3)
    assert len(terms) >= 40, len(terms)
    assert len(terms) == len(set(terms)), "duplicate glossary terms"
    joined = " | ".join(terms).lower()
    missing = [t for t in REQUIRED_TERMS if t.lower() not in joined]
    assert not missing, missing


def _sources() -> str:
    """The engine's source, with adjacent string literals split over lines joined back together."""
    src = "\n".join(read(p) for p in [*SCRIPTS.glob("pmlc*.py"), *SCRIPTS.glob("pmlc_lib/**/*.py"), ROOT / "skills" / "learnings-coach" / "references" /
                                       "lint-terms.json",
                                       ROOT / "tests" / "test_a11y_js.py"])   # Task 28: the contributors' npm ci hint
    return re.sub(r"[\"']\s*\n\s*[rf]?[\"']", "", src)


def test_troubleshooting_count():
    """At least 12 problems, each quoting an engine message. The longest fixed part of the quote (between placeholders,
    numbers, quoted values and the joins the engine adds) must be in the engine's source or its lint terms."""
    text = read(MANUAL / "Troubleshooting.md")
    probs = sections(text)
    assert len(probs) >= 12, len(probs)
    src, bad = _sources(), []
    for h, body in probs.items():
        blocks = re.findall(r"```(?:text)?\n(.*?)\n```", body, re.S)
        if not blocks:
            bad.append(f"{h}: quote the engine's message in a text block")
            continue
        line = re.sub(r"^(?:warning|WARNING|ERROR)\b:? ?", "", blocks[0].splitlines()[0])
        parts = re.split(r"<[^>]+>|…|\d+|[\"']|; |: ", line)   # placeholders, numbers, quoted values, joins
        chunk = sorted((x.strip(" .,;:") for x in parts), key=len, reverse=True)[0]
        if len(chunk) < 6 or chunk not in src:
            bad.append(f"{h}: {chunk!r} is not in the engine's source")
    assert not bad, bad


def _links(p: Path):
    fence = False
    for line in read(p).splitlines():
        if line.startswith("```"):
            fence = not fence
        if not fence:
            yield from LINK_RX.findall(line)


def test_owned_page_links_resolve():
    """Relative links stay inside the manual and reach a page (or a Task 13 page); anchors into these pages match a
    heading; GitHub links point at files in this repository."""
    owned = {p.relative_to(MANUAL).as_posix() for p in owned_pages()}
    bad = []
    for p in owned_pages():
        rel = p.relative_to(MANUAL).as_posix()
        for _, href in _links(p):
            if href.startswith(REPO_BLOB):
                path = href[len(REPO_BLOB):].split("#")[0]
                if not (ROOT / path).exists():
                    bad.append(f"{rel}: {href}")
                continue
            if re.match(r"^[a-z]+:", href):
                continue
            path, _, anchor = href.partition("#")
            if not path:
                target = rel
            else:
                if not path.endswith(".md"):
                    bad.append(f"{rel}: {href} (link a manual page, or use a GitHub URL)")
                    continue
                parts = []
                for seg in (Path(rel).parent / path).as_posix().split("/"):
                    if seg == "..":
                        if not parts:
                            bad.append(f"{rel}: {href} leaves the manual")
                            break
                        parts.pop()
                    elif seg not in (".", ""):
                        parts.append(seg)
                target = "/".join(parts)
            if target in T13_PAGES:
                if anchor and anchor != "flags":
                    bad.append(f"{rel}: {href} (anchor into a Task 13 page)")
                continue
            if target not in owned:
                bad.append(f"{rel}: {href} (no such page)")
            elif anchor and anchor not in {slug(h) for lv in (1, 2, 3) for h in headings(read(MANUAL / target), lv)}:
                bad.append(f"{rel}: {href} (no such heading)")
    assert not bad, bad


FLAG_RX = re.compile(r"(?<![\w-])--[a-z][a-z-]*[a-z]")
# Ways a line names the subcommand its flags belong to: a command line, a link to its page, or a code span that
# starts with its name (`select --tier T2`).
CMD_RXS = [re.compile(r"(?:\$E|\bpmlc(?:\.py)?)\s+([a-z][a-z-]*)"), re.compile(r"\(\.?\.?/?commands/([a-z-]+)\.md"),
           re.compile(r"`([a-z][a-z-]*)[ `]")]


def line_flag_problems(line: str, flags: dict) -> list:
    """Flags on one line that are not engine flags; when the line names subcommands, flags that none of them has."""
    every = set().union(*flags.values()) | OTHER_FLAGS | {"--help", "--version"}
    named = {c for rx in CMD_RXS for c in rx.findall(line) if c in flags}
    allowed = set().union(*(flags[c] for c in named)) | OTHER_FLAGS | {"--help", "--version"} if named else every
    out = []
    for f in sorted(set(FLAG_RX.findall(line))):
        if f not in every:
            out.append(f)
        elif f not in allowed:
            out.append(f"{f} (not a flag of {', '.join(sorted(named))})")
    return out


def test_owned_pages_name_only_real_flags():
    """Every `--flag` written on these pages is an engine flag. On a line that names its subcommand (a command
    line, a link to the command's page, or a code span starting with its name), the flag belongs to that
    subcommand, or to one of them when the line names several."""
    flags, bad = parser_flags(), []
    for p in owned_pages():
        for n, line in enumerate(read(p).splitlines(), 1):
            bad += [f"{p.relative_to(MANUAL).as_posix()}:{n}: {x}" for x in line_flag_problems(line, flags)]
    assert not bad, bad


@pytest.mark.parametrize("line,bad", [
    ("`select --tier T2`", []),
    ("`select --share external`", ["--share (not a flag of select)"]),
    ("[pack](commands/pack.md) takes `--embed summary`", []),
    ("[register-xlsx](commands/register-xlsx.md) takes `--embed summary`", ["--embed (not a flag of register-xlsx)"]),
    ("Use `--nope`.", ["--nope"]),
    ("Both take `--share`: [pack](commands/pack.md) and [select](commands/select.md).", []),
])
def test_line_flag_problems(line, bad):
    assert line_flag_problems(line, parser_flags()) == bad


def test_owned_pages_use_no_blame_words():
    """The manual itself follows the language check it describes, outside quoted examples of flagged wording."""
    rx = re.compile(r"\b(careless|reckless|negligent|punish\w*|disciplinary)\b", re.I)
    bad = []
    for p in owned_pages():
        if p.name in ("Language-checks.md", "Glossary.md", "Troubleshooting.md"):
            continue
        fence = False
        for n, line in enumerate(read(p).splitlines(), 1):
            if line.startswith("```"):
                fence = not fence
            if fence or line.startswith(">") or "`" in line:
                continue
            if rx.search(line):
                bad.append(f"{p.name}:{n}: {line.strip()[:80]}")
    assert not bad, bad


def test_commands_usage_example_lists_every_subcommand():
    """The usage block in Commands.md is the parser's own list, once, in the parser's order."""
    import argparse
    text = (MANUAL / "Commands.md").read_text(encoding="utf-8")
    groups = re.findall(r"\{([a-z0-9,-]+)\}", text.split("## Typing flags", 1)[1].split("## Exit codes", 1)[0])
    sub = next(a for a in pmlc.build_parser()._actions if isinstance(a, argparse._SubParsersAction))
    assert groups == [",".join(sub.choices)]
