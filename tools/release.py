#!/usr/bin/env python3
"""Bump the engine version in every place it lives, then print the git tag command.

    python3 tools/release.py 2.0.0a1 [--root DIR]

Rewrites __version__ in skills/learnings-coach/scripts/pmlc.py and "version" in
.claude-plugin/plugin.json and .claude-plugin/marketplace.json. Changes version
strings only; prints the tag command but does not run git. Standard library only.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

VERSION_RX = re.compile(r"(\d+)\.(\d+)\.(\d+)(?:(a|rc)(\d+))?")
TARGETS = [
    ("skills/learnings-coach/scripts/pmlc.py", re.compile(r'(__version__ = ")[^"]*(")')),
    (".claude-plugin/plugin.json", re.compile(r'("version": ")[^"]*(")')),
    (".claude-plugin/marketplace.json", re.compile(r'("version": ")[^"]*(")')),
]


def semver(v):
    """2.0.0a1 -> 2.0.0-alpha.1; 2.0.0rc1 -> 2.0.0-rc.1; 2.0.0 -> 2.0.0."""
    m = VERSION_RX.fullmatch(v)
    if not m:
        sys.exit(f"Version must look like 2.0.0, 2.0.0a1 or 2.0.0rc1, not {v!r}.")
    major, minor, patch, pre, n = m.groups()
    core = f"{major}.{minor}.{patch}"
    if not pre:
        return core
    return f"{core}-{'alpha' if pre == 'a' else 'rc'}.{n}"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("version")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[1]), help="repository root")
    a = ap.parse_args(argv)
    tag = semver(a.version)
    root = Path(a.root)
    texts = {}
    for rel, rx in TARGETS:
        path = root / rel
        if not path.is_file():
            sys.exit(f"Cannot find {path}.")
        text = path.read_text(encoding="utf-8")
        new, n = rx.subn(lambda m: m.group(1) + a.version + m.group(2), text, count=1)
        if n != 1:
            sys.exit(f"No version string found in {path}.")
        texts[path] = new
    for path, text in texts.items():
        path.write_text(text, encoding="utf-8")
        print(f"updated {path}")
    print(f'\ngit tag -a v{tag} -m "ProbeMatrix Learnings Coach {tag}"')


if __name__ == "__main__":
    main()
