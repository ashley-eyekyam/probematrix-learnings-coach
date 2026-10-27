"""The consolidated UAT book (docs/uat/v2.0-consolidated-uat.md): the Phase 5 section is complete.

Every Phase 5 case named in the plan (Task 27) is there, with the parts each case needs, every engine command it
names is a real subcommand, and every input file it attaches exists in docs/uat/inputs or the Hazira sample."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "docs" / "uat" / "v2.0-consolidated-uat.md"
PMLC = ROOT / "skills" / "learnings-coach" / "scripts" / "pmlc.py"
INPUTS = ROOT / "docs" / "uat" / "inputs"
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"

CASES = ["A1", "A2", "A3", "B1", "B2", "C1", "C2", "C3", "D1", "D2", "E1", "E2", "E3",
         "F1", "F2", "F3", "F4", "F5", "G1", "G2", "G3", "G4", "G5"]
PARTS = ["Purpose", "Input", "Prompt", "Engine", "Expected", "Result", "Notes"]


def _section(text: str, heading: str, nxt: str) -> str:
    start = text.index(f"\n{heading}\n")
    return text[start:text.index(f"\n{nxt}\n", start)]


def _phase5() -> str:
    return _section(BOOK.read_text(encoding="utf-8"), "## Phase 5: deeper analysis", "## Phase 6")


def _cases(sec: str) -> dict:
    parts = re.split(r"\n#### P5-([A-H]\d)\. ", sec)
    return {parts[i]: parts[i + 1].split("\n### ")[0] for i in range(1, len(parts), 2)}


def test_phase5_placeholder_replaced():
    text = BOOK.read_text(encoding="utf-8")
    assert "## Phase 5\n\n*To be added when Phase 5 is finished.*" not in text
    assert text.count("\n## Phase 5") == 1


def test_phase5_has_every_case_with_its_parts():
    cases = _cases(_phase5())
    assert list(cases) == CASES
    for cid, body in cases.items():
        for part in PARTS:
            assert f"- **{part}" in body, f"P5-{cid} has no {part}"
        assert "- **Result:** [ ] Pass [ ] Fail" in body, f"P5-{cid}: no tick boxes"


def test_phase5_regression_names_the_phase4_cases():
    sec = _phase5()
    reg = sec[sec.index("### P5-H."):]
    for case in ("P4-A1", "P4-B1", "P4-D1", "P4-E1"):
        assert f"**{case}" in reg, case


def test_phase5_owner_interview_and_conversations():
    sec = _phase5()
    c1 = _cases(sec)["C1"]
    assert "OD5-1" in c1 and "None / unknown (record as a gap)" in c1 and "promote" in c1
    for conv in ("11", "12", "13", "14"):
        assert re.search(rf"^\| {conv} \| P5-", sec, re.M), f"conversation {conv} missing"


def test_phase5_engine_lines_use_real_subcommands():
    r = subprocess.run([sys.executable, str(PMLC), "-h"], capture_output=True, text=True, check=True)
    subs = set(re.search(r"\{([a-z,-]+)\}", r.stdout).group(1).split(","))
    used = set(re.findall(r"\$E ([a-z][a-z-]+)", _phase5()))
    assert used and used <= subs, sorted(used - subs)


def test_phase5_attachments_exist():
    names = set(re.findall(r"`((?:uat-[\w.-]+)\.(?:json|xlsx|csv))`", _phase5()))
    assert {"uat-weak-fix-register.json", "uat-capa-planner-9m.xlsx", "uat-process-export.xlsx"} <= names
    for n in names:
        assert (INPUTS / n).is_file(), n
    inputs = "\n".join(re.findall(r"^- \*\*Input:\*\*.*$", _phase5(), re.M))
    for n in set(re.findall(r"`([\w.-]+\.json)`", inputs)) - names:
        assert (SAMPLE / "outputs" / n).is_file(), n
