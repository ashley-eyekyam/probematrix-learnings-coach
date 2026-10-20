"""The user manual (docs/manual/): every command, flag, tool and environment variable is documented, nothing
stale is documented, and every link resolves the way the wiki mirror (tools/sync-wiki.py) needs."""
import argparse
import importlib.util
import os
import re
import subprocess
import sys
from collections import deque
from pathlib import Path, PurePosixPath

import pytest

ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "docs" / "manual"
PMLC = ROOT / "skills" / "learnings-coach" / "scripts" / "pmlc.py"
sys.path.insert(0, str(PMLC.parent))
import pmlc  # noqa: E402

_spec = importlib.util.spec_from_file_location("sync_wiki", ROOT / "tools" / "sync-wiki.py")
sw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sw)

HEADINGS = ["What it does", "When to use it", "Synopsis", "Arguments", "Flags", "Examples", "Common problems",
            "Related"]
FLAG_TABLE = "| Flag | Value | Default | What it does |"
ALWAYS_OK = {"--version", "--help"}
LINK_RX = re.compile(r"\]\(([^)\s]+)\)")
FLAG_RX = re.compile(r"(?<![\w-])(--[a-z][a-z-]*)")
CMD_LINE_RX = re.compile(r"\$E\s+([a-z][a-z-]*)\b([^\n]*)")
SCHEME_RX = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def _subparsers() -> dict:
    sub = next(a for a in pmlc.build_parser()._actions if isinstance(a, argparse._SubParsersAction))
    return dict(sub.choices)


SUBS = _subparsers()


def _options(name: str) -> set:
    return {o for a in SUBS[name]._actions for o in a.option_strings if o.startswith("--")}


def _pages() -> list:
    return sorted(MANUAL.rglob("*.md"))


def _page(name: str) -> str:
    return (MANUAL / "commands" / f"{name}.md").read_text(encoding="utf-8")


def _prose(text: str) -> str:
    """The text outside fenced code blocks."""
    out, fenced = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced:
            out.append(line)
    return "\n".join(out)


def _slug(heading: str) -> str:
    """GitHub's heading anchor: lower case, punctuation dropped (hyphens and underscores kept), spaces to '-'."""
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def _anchors(path: Path) -> set:
    seen: dict = {}
    for line in _prose(path.read_text(encoding="utf-8")).splitlines():
        m = re.match(r"^#{1,6}\s+(.*?)\s*#*\s*$", line)
        if m:
            s = _slug(m.group(1))
            n = seen.get(s, 0)
            seen[s] = n + 1
            yield s if n == 0 else f"{s}-{n}"


def _links(path: Path):
    """(target path or None, anchor or '') for each relative link in a page, code blocks excluded."""
    for href in LINK_RX.findall(_prose(path.read_text(encoding="utf-8"))):
        if SCHEME_RX.match(href):
            continue
        target, _, anchor = href.partition("#")
        yield ((path.parent / target).resolve() if target else path.resolve()), anchor


def test_manual_exists():
    assert (MANUAL / "Home.md").is_file() and (MANUAL / "Commands.md").is_file()
    assert (MANUAL / "Developer-tools.md").is_file()


def test_every_subcommand_has_a_page():
    missing = [n for n in SUBS if not (MANUAL / "commands" / f"{n}.md").is_file()]
    assert not missing, f"no docs/manual/commands/<name>.md for: {missing}"
    extra = sorted(p.stem for p in (MANUAL / "commands").glob("*.md") if p.stem not in SUBS)
    assert not extra, f"command pages for commands that do not exist: {extra}"
    index = (MANUAL / "Commands.md").read_text(encoding="utf-8")
    unlisted = [n for n in SUBS if f"(commands/{n}.md)" not in index]
    assert not unlisted, f"not linked from Commands.md: {unlisted}"
    for flag in ("`--version`", "`-h`"):
        assert flag in index, f"Commands.md does not document the global {flag}"


def test_every_flag_documented():
    problems = []
    for name, sp in SUBS.items():
        page = _page(name)
        for a in sp._actions:
            if isinstance(a, argparse._HelpAction):
                continue
            for o in a.option_strings:
                if o.startswith("--") and f"`{o}`" not in page:
                    problems.append(f"{name}: flag {o}")
            if not a.option_strings and f"`{a.dest}`" not in page:
                problems.append(f"{name}: argument {a.dest}")
            for c in a.choices or ():  # the value must be in the Flags section, not just anywhere on the page
                if not re.search(rf"(?<![\w-]){re.escape(str(c))}(?![\w-])", _section(page, "Flags")):
                    problems.append(f"{name}: {a.option_strings[0] if a.option_strings else a.dest} value {c}")
    assert not problems, "undocumented in docs/manual/commands/: " + "; ".join(problems)


def _section(page: str, heading: str) -> str:
    """The text of one `## heading` section, up to the next H2."""
    return re.split(r"^## ", page.split(f"\n## {heading}\n", 1)[-1], maxsplit=1, flags=re.M)[0]


def _synopsis_flags(name: str) -> list:
    """Flags in the Synopsis section's fenced block that the subcommand does not have."""
    block = _section(_page(name), "Synopsis")
    return [f"{name} synopsis {f}" for f in FLAG_RX.findall(block) if f not in _options(name) | ALWAYS_OK]


def _stale(text: str, default: str) -> list:
    """Flags in inline code spans and in `$E <cmd> ...` lines that the named subcommand does not have. An inline
    span that starts with a subcommand name (`select --tier`) is checked against that subcommand."""
    bad = []
    for cmd, rest in CMD_LINE_RX.findall(text):
        if cmd in SUBS:
            bad += [f"{cmd} {f}" for f in FLAG_RX.findall(rest) if f not in _options(cmd) | ALWAYS_OK]
        else:
            bad.append(f"unknown subcommand {cmd}")
    for span in re.findall(r"`([^`\n]+)`", _prose(text)):
        first = span.split()[0]
        if first not in SUBS and ("/" in first or first.endswith((".py", ".sh"))):
            continue  # a repository tool, such as `tools/make-public-sample.py --slug`
        cmd = first if first in SUBS else default
        if cmd is None:
            continue
        bad += [f"{cmd} {f}" for f in FLAG_RX.findall(span) if f not in _options(cmd) | ALWAYS_OK]
    return bad


def test_no_stale_flags():
    problems = []
    for name in SUBS:
        problems += [f"commands/{name}.md: {b}" for b in _stale(_page(name), name) + _synopsis_flags(name)]
    for p in _pages():
        if p.parent.name != "commands":
            problems += [f"{p.relative_to(MANUAL)}: {b}" for b in _stale(p.read_text(encoding="utf-8"), None)]
    assert not problems, "flags that are not options of that subcommand: " + "; ".join(problems)


def test_command_page_headings():
    problems = []
    for name in SUBS:
        page = _page(name)
        prose = _prose(page)
        h2 = re.findall(r"^## (.+?)\s*$", prose, flags=re.M)
        if h2 != HEADINGS:
            problems.append(f"{name}: H2 headings are {h2}")
        if not re.match(rf"^# `?{re.escape(name)}`?\s*$", prose.splitlines()[0]):
            problems.append(f"{name}: first line must be the H1 '# {name}'")
        flags = prose.split("## Flags", 1)[-1].split("## Examples", 1)[0]
        if FLAG_TABLE not in flags:
            problems.append(f"{name}: the Flags section has no '{FLAG_TABLE}' table")
        examples = page.split("## Examples", 1)[-1].split("## Common problems", 1)[0]
        if f"$E {name}" not in examples:
            problems.append(f"{name}: no '$E {name}' example")
    assert not problems, "; ".join(problems)


def test_tools_flags_documented():
    dev = (MANUAL / "Developer-tools.md").read_text(encoding="utf-8")
    problems = []
    for f in sorted((ROOT / "tools").glob("*.py")):
        if f"`tools/{f.name}`" not in dev:
            problems.append(f"tools/{f.name}")
        for flag in re.findall(r'add_argument\(\s*"(--[a-z][a-z-]*)"', f.read_text(encoding="utf-8")):
            if f"`{flag}`" not in dev:
                problems.append(f"tools/{f.name} {flag}")
    evals = (ROOT / "evals" / "run_evals.py").read_text(encoding="utf-8")
    subs = re.findall(r'add_parser\(\s*"([a-z-]+)"', evals)
    assert subs, "found no run_evals.py subcommands"
    for s in subs:
        if f"run_evals.py {s}" not in dev:
            problems.append(f"evals/run_evals.py {s}")
    for flag in re.findall(r'add_argument\(\s*"(--[a-z][a-z-]*)"', evals):
        if f"`{flag}`" not in dev:
            problems.append(f"evals/run_evals.py {flag}")
    assert not problems, "not documented in Developer-tools.md: " + "; ".join(problems)


def _env_keys() -> set:
    keys = set()
    for base in ("skills", "tools"):
        for f in (ROOT / base).rglob("*.py"):
            t = f.read_text(encoding="utf-8")
            keys |= set(re.findall(r"""os\.(?:environ(?:\.get)?|getenv)\s*[\[(]\s*["']([A-Z][A-Z0-9_]*)["']""", t))
            if re.search(r"os\.(environ|getenv)", t):  # keys passed through a variable, such as env="PMLC_NAMES"
                keys |= set(re.findall(r"""["'](PMLC_[A-Z0-9_]+)["']""", t))
    return keys


def test_env_vars_documented():
    keys = _env_keys()
    assert {"PMLC_NAMES", "PMLC_ORGS"} <= keys
    text = "\n".join(p.read_text(encoding="utf-8") for p in _pages())
    missing = sorted(k for k in keys if not re.search(rf"(?<![A-Z0-9_]){re.escape(k)}(?![A-Z0-9_])", text))
    assert not missing, f"environment variables not documented in docs/manual/: {missing}"


def test_manual_links_resolve():
    problems = []
    for p in _pages():
        rel = p.relative_to(MANUAL)
        for target, anchor in _links(p):
            if not target.exists():
                problems.append(f"{rel}: missing {os.path.relpath(target, MANUAL)}")
                continue
            if MANUAL.resolve() not in target.parents:
                problems.append(f"{rel}: {target} is outside docs/manual (use an absolute GitHub URL)")
                continue
            if anchor and target.suffix == ".md" and anchor not in set(_anchors(target)):
                problems.append(f"{rel}: no heading for #{anchor} in {target.relative_to(MANUAL)}")
    assert not problems, "; ".join(problems)


def test_every_page_reachable_from_home():
    home = (MANUAL / "Home.md").resolve()
    seen, todo = {home}, deque([home])
    while todo:
        for target, _ in _links(todo.popleft()):
            if target.suffix == ".md" and target.exists() and target not in seen:
                seen.add(target)
                todo.append(target)
    lost = sorted(str(p.relative_to(MANUAL)) for p in _pages() if p.resolve() not in seen)
    assert not lost, f"not reachable from Home.md: {lost}"


def test_manual_page_names_unique():
    names: dict = {}
    for p in _pages():
        rel = PurePosixPath(p.relative_to(MANUAL).as_posix())
        name = sw.wiki_name(str(rel))
        assert name not in names, f"{rel} and {names[name]} both map to the wiki page {name}"
        names[name] = rel


def test_allow_abbrev_disabled(tmp_path):
    r = subprocess.run([sys.executable, str(PMLC), "select", str(tmp_path), "--top-rat"], capture_output=True,
                       text=True)
    assert r.returncode == 2 and "unrecognized arguments: --top-rat" in r.stderr
    r = subprocess.run([sys.executable, str(PMLC), "--vers"], capture_output=True, text=True)
    assert r.returncode == 2


@pytest.mark.parametrize("text,bad", [("`--nope`", ["select --nope"]), ("`select --tier T2`", []),
                                      ("```\n$E profile $WS --top 5 --tier\n```", ["profile --tier"]),
                                      ("```\n$E frobnicate $WS\n```", ["unknown subcommand frobnicate"]),
                                      ("`tools/release.py --root x`", [])])
def test_stale_checker(text, bad):
    assert _stale(text, "select") == bad


def test_section_and_synopsis_checks(monkeypatch):
    page = "# x\n\n## Synopsis\n\n```text\npmlc select ws [--tier T] [--nope]\n```\n\n## Flags\n\n`any`\n"
    assert _section(page, "Flags").strip() == "`any`" and "--nope" in _section(page, "Synopsis")
    monkeypatch.setattr(sys.modules[__name__], "_page", lambda name: page)
    assert _synopsis_flags("select") == ["select synopsis --nope"]


def test_slug_rules():
    assert _slug("Common problems") == "common-problems"
    assert _slug("`--share`: who may read it?") == "--share-who-may-read-it"
