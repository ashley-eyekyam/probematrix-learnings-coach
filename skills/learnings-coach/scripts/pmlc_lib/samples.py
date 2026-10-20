"""The check-samples command."""
from __future__ import annotations

import sys
from pathlib import Path

from .workspace import valid_run_slug


def sample_folder_problems(samples) -> list:
    """Contribution rule: samples/<YYYY-MM-DD>-<site>-<event>/ with README.md and <slug>_probematrix-findings.xlsx."""
    problems = []
    for d in sorted(p for p in Path(samples).iterdir() if p.is_dir()):
        if not valid_run_slug(d.name):
            problems.append(f"{d.name}: folder name must be YYYY-MM-DD-<site>-<event> "
                            "(lowercase words joined by hyphens)")
            continue
        if not (d / "README.md").is_file():
            problems.append(f"{d.name}: missing README.md")
        if not (d / f"{d.name}_probematrix-findings.xlsx").is_file():
            problems.append(f"{d.name}: missing {d.name}_probematrix-findings.xlsx")
    return problems


def cmd_check_samples(a):
    if not Path(a.dir).is_dir():
        sys.exit(f"No such folder: {a.dir}")
    probs = sample_folder_problems(a.dir)
    for p in probs:
        print(" -", p)
    print(f"{len(probs)} problem(s) in {a.dir}")
    sys.exit(1 if probs else 0)
