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
LINK_RX = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)\s]+)\)")


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


def rewrite_links(text: str, rel: str, known: set) -> str:
    def sub(m: re.Match) -> str:
        label, href = m.group(1), m.group(2)
        path, hash_, anchor = href.partition("#")
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", href) or not path.endswith(".md"):
            return m.group(0)
        target = _resolve(rel, path)
        if target not in known:
            raise ValueError(f"{rel}: link to missing manual page {href}")
        return f"[{label}]({wiki_name(target)}{hash_}{anchor})"
    return LINK_RX.sub(sub, text)


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


def sync(manual_dir, wiki_dir, version, *, check=False, adopt=()) -> list:
    wiki_dir = Path(wiki_dir)
    pages = build_pages(Path(manual_dir), version)
    mpath = wiki_dir / MANIFEST
    owned = set(json.loads(mpath.read_text(encoding="utf-8"))["pages"]) if mpath.exists() else set()
    collisions = sorted(n for n in pages if (wiki_dir / f"{n}.md").exists() and n not in owned and n not in adopt)
    if collisions:
        print("Refusing to overwrite wiki pages this tool does not own: " + ", ".join(collisions)
              + "\nRe-run with --adopt NAME to take them over.", file=sys.stderr)
        raise SystemExit(1)
    changes = []
    for name, content in sorted(pages.items()):
        f = wiki_dir / f"{name}.md"
        if f.exists() and f.read_text(encoding="utf-8") == content:
            changes.append(f"unchanged {name}")
        else:
            changes.append(f"write {name}")
            if not check:
                wiki_dir.mkdir(parents=True, exist_ok=True)
                f.write_text(content, encoding="utf-8")
    for name in sorted(owned - set(pages)):
        f = wiki_dir / f"{name}.md"
        if f.exists():
            changes.append(f"delete {name}")
            if not check:
                f.unlink()
    manifest = json.dumps({"version": version, "pages": sorted(pages)}, indent=2) + "\n"
    if not check and (not mpath.exists() or mpath.read_text(encoding="utf-8") != manifest):
        wiki_dir.mkdir(parents=True, exist_ok=True)
        mpath.write_text(manifest, encoding="utf-8")
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
