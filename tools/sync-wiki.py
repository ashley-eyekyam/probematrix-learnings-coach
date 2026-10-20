#!/usr/bin/env python3
"""Mirror the user manual (docs/manual/) into a local clone of the GitHub Wiki.

Run from the repository root:
  python3 tools/sync-wiki.py --wiki-dir DIR [--manual-dir docs/manual] [--version V] [--check] [--adopt NAME ...]

Page names: Home.md -> Home, X.md -> X, commands/<n>.md -> Command-<n>, skills/<n>.md -> Skill-<n>.
Relative .md links are rewritten to wiki links, every page gets a version header, and _Sidebar and _Footer
are generated. Pages this tool wrote are recorded in <wiki-dir>/.pmlc-sync.json; only those are ever
updated or deleted. A page that exists but is not owned is never overwritten unless named with --adopt
(exit 1 otherwise). --check writes nothing and exits 1 if anything would change. The tool never runs git:
commit and push the wiki clone yourself.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "learnings-coach" / "scripts"))
import pmlc  # noqa: E402

REPO_URL = "https://github.com/ashley-eyekyam/probematrix-learnings-coach"
MANIFEST = ".pmlc-sync.json"
LINK_RX = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)\s]+)((?:\s+(?:\"[^\"]*\"|'[^']*'))?)\s*\)")
REF_RX = re.compile(r"^(\s{0,3}\[[^\]]+\]:\s*)(\S+)(.*)$")
CODE_SPAN_RX = re.compile(r"(`+)(?:(?!\1).)+?\1")
FENCE_RX = re.compile(r"^\s{0,3}(`{3,}|~{3,})")


def wiki_name(rel_path: str) -> str:
    """Map a manual-relative path (posix) to its wiki page name."""
    p = PurePosixPath(rel_path)
    stem = p.stem
    if len(p.parts) == 1:
        return stem
    if p.parts[0] == "commands" and len(p.parts) == 2:
        return f"Command-{stem}"
    if p.parts[0] == "skills" and len(p.parts) == 2:
        return f"Skill-{stem}"
    raise ValueError(f"unsupported manual path: {rel_path}")


def _resolve(rel: str, target: str) -> str:
    parts: list = []
    for seg in (PurePosixPath(rel).parent / target).parts:
        if seg == "..":
            if not parts:
                raise ValueError(f"{rel}: link {target} leaves the manual")
            parts.pop()
        elif seg != ".":
            parts.append(seg)
    return "/".join(parts)


def _target(href: str, rel: str, known: set):
    """Return the wiki link for a relative .md href, or None to leave it alone."""
    path, hash_, anchor = href.partition("#")
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", href) or not path.endswith(".md"):
        return None
    target = _resolve(rel, path)
    if target not in known:
        raise ValueError(f"{rel}: link to missing manual page {href}")
    return f"{wiki_name(target)}{hash_}{anchor}"


def _rewrite_line(line: str, rel: str, known: set) -> str:
    def inline(m: re.Match) -> str:
        new = _target(m.group(2), rel, known)
        return m.group(0) if new is None else f"[{m.group(1)}]({new}{m.group(3)})"

    m = REF_RX.match(line)
    if m:
        new = _target(m.group(2), rel, known)
        return line if new is None else f"{m.group(1)}{new}{m.group(3)}"
    out, pos = [], 0
    for span in CODE_SPAN_RX.finditer(line):
        out.append(LINK_RX.sub(inline, line[pos:span.start()]))
        out.append(span.group(0))
        pos = span.end()
    out.append(LINK_RX.sub(inline, line[pos:]))
    return "".join(out)


def rewrite_links(text: str, rel: str, known: set) -> str:
    """Rewrite relative .md links to wiki links, leaving fenced and inline code untouched."""
    out, fence = [], None
    for line in text.split("\n"):
        m = FENCE_RX.match(line)
        if fence is None and m:
            fence = m.group(1)[0] * len(m.group(1))
            out.append(line)
        elif fence is not None:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) and not line.strip().strip(fence[0]):
                fence = None
            out.append(line)
        else:
            out.append(_rewrite_line(line, rel, known))
    return "\n".join(out)


def build_pages(manual_dir: Path, version: str) -> dict:
    manual_dir = Path(manual_dir)
    rels = sorted(p.relative_to(manual_dir).as_posix() for p in manual_dir.rglob("*.md"))
    known = set(rels)
    pages: dict = {}
    for rel in rels:
        name = wiki_name(rel)
        if name in pages:
            raise ValueError(f"two manual files map to the wiki page {name}")
        header = (f"> Documents ProbeMatrix Learnings Coach v{version}. Source: "
                  f"[docs/manual/{rel}]({REPO_URL}/blob/main/docs/manual/{rel}). "
                  "Edit there, not here: this page is replaced on every release.")
        body = rewrite_links((manual_dir / rel).read_text(encoding="utf-8"), rel, known)
        pages[name] = f"{header}\n\n{body}"
    side = ["**[Home](Home)**", ""]
    guides = sorted(n for n in pages if n != "Home" and not n.startswith(("Command-", "Skill-")))
    side += [f"- [{n.replace('-', ' ')}]({n})" for n in guides]
    for title, prefix in (("Commands", "Command-"), ("Skills", "Skill-")):
        names = sorted(n for n in pages if n.startswith(prefix))
        if names:
            side += ["", f"**{title}**", ""] + [f"- [{n[len(prefix):]}]({n})" for n in names]
    pages["_Sidebar"] = "\n".join(side) + "\n"
    pages["_Footer"] = pmlc.BRAND + "\n"
    return pages


def _safe_name(name) -> bool:
    return isinstance(name, str) and bool(name) and not any(c in name for c in "/\\") and ".." not in name


def _write_manifest(mpath: Path, version: str, names) -> None:
    mpath.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps({"version": version, "pages": sorted(names)}, indent=2) + "\n"
    if not mpath.exists() or mpath.read_text(encoding="utf-8") != text:
        mpath.write_text(text, encoding="utf-8")


def sync(manual_dir, wiki_dir, version, *, check=False, adopt=()) -> list:
    wiki_dir = Path(wiki_dir)
    pages = build_pages(Path(manual_dir), version)
    unknown = sorted(n for n in adopt if n not in pages)
    if unknown:
        print("--adopt names no page this tool generates: " + ", ".join(unknown), file=sys.stderr)
        raise SystemExit(1)
    mpath = wiki_dir / MANIFEST
    owned = set()
    if mpath.exists():
        data = json.loads(mpath.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("pages"), list):
            raise ValueError("wiki manifest is malformed: pages must be a list")
        owned = {n for n in data["pages"] if isinstance(n, str)}
    collisions = sorted(n for n in pages if (wiki_dir / f"{n}.md").exists() and n not in owned and n not in adopt)
    if collisions:
        print("Refusing to overwrite wiki pages this tool does not own: " + ", ".join(collisions)
              + "\nRe-run with --adopt NAME to take them over.", file=sys.stderr)
        raise SystemExit(1)
    changes = []
    # Record ownership (old union new) before any page is written, so a crash leaves pages owned.
    if not check:
        _write_manifest(mpath, version, owned | set(pages))
    for name, content in sorted(pages.items()):
        f = wiki_dir / f"{name}.md"
        if f.exists() and f.read_text(encoding="utf-8") == content:
            changes.append(f"unchanged {name}")
        else:
            changes.append(f"write {name}")
            if not check:
                wiki_dir.mkdir(parents=True, exist_ok=True)
                f.write_text(content, encoding="utf-8")
    root = wiki_dir.resolve()
    for name in sorted(owned - set(pages)):
        f = wiki_dir / f"{name}.md"
        if not _safe_name(name) or root not in f.resolve().parents:
            changes.append(f"skip unsafe name {name!r}")
            continue
        if f.exists():
            changes.append(f"delete {name}")
            if not check:
                f.unlink()
    if not check:
        _write_manifest(mpath, version, pages)
    return changes


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Mirror docs/manual/ into a GitHub Wiki clone.", allow_abbrev=False)
    ap.add_argument("--wiki-dir", required=True, type=Path)
    ap.add_argument("--manual-dir", type=Path, default=ROOT / "docs" / "manual")
    ap.add_argument("--version", default=pmlc.__version__)
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 if anything would change")
    ap.add_argument("--adopt", nargs="+", default=[], metavar="NAME", help="take over existing unowned pages")
    a = ap.parse_args(argv)
    try:
        changes = sync(a.manual_dir, a.wiki_dir, a.version, check=a.check, adopt=a.adopt)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    for c in changes:
        print(c)
    return 1 if a.check and any(not c.startswith("unchanged") for c in changes) else 0


if __name__ == "__main__":
    sys.exit(main())
