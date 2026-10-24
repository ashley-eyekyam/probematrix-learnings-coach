"""The check-samples command."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from .workspace import valid_run_slug


# Its Markdown is learnings-register.md and its HTML is the dashboard, organisation-learning-map.html (Task 27).
RENDER_EXEMPT = ("learnings-register.json",)
# Phase 5 staging (plan, New-skill checklist item 6): a new skill's Hazira golden pack lands as JSON only, and
# Task 24 renders its HTML and MD, then empties this set. Each entry must be a pack JSON with neither rendering.
RENDER_PENDING = frozenset({"compliance-crosswalk.json", "failure-to-learn-review.json", "latent-conditions-profile.json",
                            "open-questions-register.json", "people-workforce-learnings.json",
                            "risk-register-update.json"})


def _sample_render_problems(d) -> list:
    """OD4-4: every pack JSON (an object with a `pack` field) in outputs/ sits beside its .html and .md."""
    out = d / "outputs"
    problems = []
    for p in sorted(out.glob("*.json")) if out.is_dir() else []:
        if p.name in RENDER_EXEMPT or p.name in RENDER_PENDING:
            continue
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            problems.append(f"{d.name}: outputs/{p.name} is not readable JSON")
            continue
        if not (isinstance(doc, dict) and "pack" in doc):
            continue
        for ext in ("html", "md"):
            if not (out / f"{p.stem}.{ext}").is_file():
                problems.append(f"{d.name}: outputs/{p.name} has no {p.stem}.{ext}")
    return problems


def sample_folder_problems(samples) -> list:
    """Contribution rule: samples/<YYYY-MM-DD>-<site>-<event>/ with README.md and <slug>_probematrix-findings.xlsx,
    and every pack JSON in its outputs/ rendered beside it as .html and .md."""
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
        problems += _sample_render_problems(d)
    return problems


def cmd_check_samples(a):
    if not Path(a.dir).is_dir():
        sys.exit(f"No such folder: {a.dir}")
    probs = sample_folder_problems(a.dir)
    from .util import json_extra
    json_extra(problems=list(probs))
    for p in probs:
        print(" -", p)
    print(f"{len(probs)} problem(s) in {a.dir}")
    sys.exit(1 if probs else 0)
