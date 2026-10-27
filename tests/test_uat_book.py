"""The consolidated UAT book (docs/uat/v2.0-consolidated-uat.md): the Phase 5 and Phase 6 sections are complete.

Every case named in the plans (Phase 5 Task 27, Phase 6 Task 21) is there, with the parts each case needs, every
engine command it names is a real subcommand, and every input file it attaches exists in docs/uat/inputs or the
Hazira sample."""
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
    """From the line that starts with `heading` to the next line that starts with `nxt`."""
    start = re.search(rf"^{re.escape(heading)}.*$", text, re.M).start()
    return text[start:re.search(rf"^{re.escape(nxt)}", text[start + 1:], re.M).start() + start + 1]


def _phase5() -> str:
    return _section(BOOK.read_text(encoding="utf-8"), "## Phase 5: deeper analysis", "## Phase 6")


def _phase6() -> str:
    return _section(BOOK.read_text(encoding="utf-8"), "## Phase 6", "## Phase 7")


def _cases(sec: str, phase: int = 5) -> dict:
    parts = re.split(rf"\n#### P{phase}-([A-I]\d)\. ", sec)
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


# ----------------------------------------------------------------------------- Phase 6 (plan Task 21)

CASES6 = ["A1", "A2", "A3", "A4", "B1", "B2", "B3", "C1", "C2", "D1", "E1", "F1", "F2",
          "G1", "G2", "G3", "G4", "G5", "H1", "H2", "H3", "H4", "H5"]
NEW_SKILLS = ["safety-alert", "could-it-happen-here", "safety-moment-deck", "learning-team-facilitator",
              "restorative-response-guide", "systemic-accimap", "learning-effectiveness-plan"]


def test_phase6_placeholder_replaced():
    text = BOOK.read_text(encoding="utf-8")
    assert "*To be added when Phase 6 is finished.*" not in text
    assert text.count("\n## Phase 6") == 1


def test_phase6_has_every_case_with_its_parts():
    cases = _cases(_phase6(), 6)
    assert list(cases) == CASES6
    for cid, body in cases.items():
        for part in PARTS:
            assert f"- **{part}" in body, f"P6-{cid} has no {part}"
        assert "- **Result:** [ ] Pass [ ] Fail" in body, f"P6-{cid}: no tick boxes"


def test_phase6_covers_every_new_skill_and_command():
    sec = _phase6()
    for skill in NEW_SKILLS:
        assert f"`{skill}`" in sec or f"{skill} skill" in sec, skill
    for cmd in ("alert-grade", "templates", "consolidate", "wai-wad", "accimap", "effect-plan", "library publish"):
        assert f"$E {cmd}" in sec, cmd


def test_phase6_fixed_copy_is_verbatim():
    """The banners a tester checks are quoted exactly as the engine holds them."""
    sys.path.insert(0, str(PMLC.parent))
    from pmlc_lib.pack.profiles import BANNERS
    sec = _phase6()
    for key in ("alert-review-copy", "cihh", "learning-team", "restorative", "accimap-inferred", "effectiveness"):
        assert BANNERS[key] in sec, key


def test_phase6_routing_and_regression():
    sec = _phase6()
    cases = _cases(sec, 6)
    targets = {"H1": "safety-alert", "H2": "could-it-happen-here", "H3": "safety-moment-deck",
               "H4": "learning-team-facilitator", "H5": "systemic-accimap"}
    for cid, skill in targets.items():
        prompt = cases[cid].split("- **Prompt:**", 1)[1].split("- **Engine:**", 1)[0]
        assert skill not in prompt, f"P6-{cid}: the prompt names its skill"
        assert f"`{skill} [todo]`" in cases[cid], cid
    reg = sec[sec.index("### P6-I."):]
    for case in ("P5-A1", "P5-C3", "P5-E2"):
        assert f"**{case}" in reg, case


def test_phase6_conversations():
    sec = _phase6()
    for conv in ("16", "17", "18", "19", "20"):
        assert re.search(rf"^\| {conv} \| P6-", sec, re.M), f"conversation {conv} missing"
    assert "20 conversations" in BOOK.read_text(encoding="utf-8")


def test_phase6_library_is_synthetic():
    """The library cases publish the made-up pump fire only, never Hazira (owner scope change)."""
    sec = _phase6()
    lib = sec[sec.index("### P6-G."):sec.index("### P6-H.")]
    assert "uat-approvable.xlsx" in lib and "uat-library-register.json" in lib
    assert "hazira-gas-release-fire" not in lib and "samples/" not in lib
    assert "mktemp -d" in lib


def test_phase6_engine_lines_use_real_subcommands():
    r = subprocess.run([sys.executable, str(PMLC), "-h"], capture_output=True, text=True, check=True)
    subs = set(re.search(r"\{([a-z,-]+)\}", r.stdout).group(1).split(","))
    used = set(re.findall(r"\$E ([a-z][a-z-]+)", _phase6()))
    assert used and used <= subs, sorted(used - subs)


def test_phase6_attachments_exist():
    names = set(re.findall(r"`((?:uat-[\w.-]+)\.(?:json|xlsx|csv|txt))`", _phase6()))
    assert {"uat-no-urgency-register.json", "uat-library-register.json", "uat-approvable.xlsx",
            "uat-names.txt"} <= names
    made = {"uat-sister-alert.json", "uat-industry-alert.json", "uat-grade-test.json", "uat-no-urgency-alert.json",
            "uat-needs-test.json", "uat-accimap-banner-test.json", "uat-lagging-test.json", "uat-library-edited.json",
            "uat-library-named.json"}                  # copies the agent makes in the outputs folder
    for n in names - made:
        assert (INPUTS / n).is_file(), n
    inputs = "\n".join(re.findall(r"^- \*\*Input:\*\*.*$", _phase6(), re.M))
    for n in set(re.findall(r"`([\w.-]+\.json)`", inputs)) - names:
        assert (SAMPLE / "outputs" / n).is_file(), n
