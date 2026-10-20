#!/usr/bin/env python3
"""Regenerate skills/learnings-coach/references/audiences.md from audiences.json.

  --write   rewrite audiences.md
  --check   exit 0 when audiences.md equals the regenerated text, 1 otherwise (prints a hint)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REFS = Path(__file__).resolve().parent.parent / "skills" / "learnings-coach" / "references"

HEAD = """# Audience catalogue

Who learns from an investigation, what they control, and which skill serves them. Use this to route requests and to write in the right register.

| Audience | Typical people | What they control | Learning they need | Skill |
|---|---|---|---|---|
"""
FOOT = """
Registers by audience: frontline short and concrete; supervisors checklists; managers systems and indicators; leadership decisions and trade-offs; board questions and assurance; auditors test criteria.
"""


def render(refs: Path = REFS) -> str:
    rows = json.loads((refs / "audiences.json").read_text(encoding="utf-8"))
    body = "".join(f"| {a['label']} | {a['typical_people']} | {a['controls']} | {a['needs']} | `{a['skill']}` |\n"
                   for a in rows)
    return HEAD + body + FOOT


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--write", action="store_true")
    ap.add_argument("--refs", default=str(REFS), help="references folder (default: the repository's)")
    a = ap.parse_args(argv)
    refs = Path(a.refs)
    text = render(refs)
    md = refs / "audiences.md"
    if a.write:
        md.write_bytes(text.encode("utf-8"))  # bytes: no newline= (Path.write_text needs 3.10+)
        print(f"wrote {md}")
        return 0
    if md.read_text(encoding="utf-8") == text:
        return 0
    print("audiences.md differs from audiences.json: run tools/make-audiences-md.py --write", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
