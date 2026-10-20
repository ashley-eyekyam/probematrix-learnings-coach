"""Register tests (Phase 3, Task 5): spine fields, check-register problems/warnings/--json, norm_hoc, register-md."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from test_pmlc import MINI_REG, PMLC, make_export, run  # noqa: F401
import pmlc  # noqa: E402
from pmlc_lib.register.check import check_register, norm_hoc  # noqa: E402
from pmlc_lib.register.markdown import register_markdown  # noqa: E402
from pmlc_lib.workspace import load_ws, pack_record, load_manifest  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures" / "registers"
ROOT = Path(__file__).resolve().parents[1]
HAZIRA = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
HAZIRA_WARNINGS = None  # recorded by test_hazira_register_still_passes


@pytest.fixture(scope="module")
def w(tmp_path_factory):
    d = tmp_path_factory.mktemp("reg")
    x = make_export(d)
    run("ingest", str(x), "--legacy-out", str(d / "ws"))
    run("classify", str(d / "ws"))
    return load_ws(d / "ws")


@pytest.fixture(scope="module")
def wsdir(w, tmp_path_factory):
    d = tmp_path_factory.mktemp("reg2")
    x = make_export(d)
    run("ingest", str(x), "--legacy-out", str(d / "ws"))
    run("classify", str(d / "ws"))
    return d / "ws"


def entry(**kw):
    e = {"lr_id": "LR-09", "finding_ids": ["FND-0001"], "evidence_ids": ["EVD-0001"], "priority": 1,
         "hfacs_level": "L3 x", "owner_entity": "F02 Mechanical Maintenance", "tier_messages": {"T2": "m"},
         "recommendations": [{"what": "w", "hoc_tier": "administrative", "leading_indicator": "i"}]}
    e.update(kw)
    return e


def reg(*entries):
    return {"entries": list(entries)}


def test_p1_admin_only_warns_and_strict_fails(w):
    r = check_register(reg(entry()), w)
    assert not r.problems
    assert any("priority-1 learning LR-09 has no fix above the administrative tier" in x for x in r.warnings)
    assert r.stats["p1_without_strong_fix"] == 1
    r = check_register(reg(entry()), w, strict=True)
    assert any("priority-1 learning LR-09 has no fix above the administrative tier" in x for x in r.problems)
    for strict in (False, True):
        r = check_register(reg(entry(why_not_stronger="no engineering option exists")), w, strict=strict)
        assert not [x for x in r.problems + r.warnings if "priority-1" in x]
    strong = entry(recommendations=[{"what": "w", "hoc_tier": "engineering", "leading_indicator": "i"}])
    assert not [x for x in check_register(reg(strong), w, strict=True).problems if "priority-1" in x]


def test_owner_and_due_warnings(w):
    e = entry(recommendations=[{"what": "w", "hoc_tier": "engineering", "leading_indicator": "i",
                                "owner": "maintenance supervisor"}])
    assert not [x for x in check_register(reg(e), w).warnings if "owner" in x and "rec 1" in x]
    e["recommendations"][0]["owner"] = "Mr Fictional Person"
    assert any("personal name" in x for x in check_register(reg(e), w).warnings)
    e["recommendations"][0]["owner"] = "Zzz"
    assert any("does not look like a role" in x for x in check_register(reg(e), w).warnings)
    for k, v in (("due", "next month"), ("by_when", "Q3"), ("note", "2025-01-31")):
        e = entry(recommendations=[{"what": "w", "hoc_tier": "engineering", "leading_indicator": "i", k: v}])
        r = check_register(reg(e), w)
        assert any("owners and due dates are set by the organisation (D7)" in x for x in r.warnings), k
    e = entry(owner_entity="F13 Nowhere")
    r = check_register(reg(e), w)
    assert not [x for x in r.problems if "owner" in x]


def test_new_fields_validated(w):
    bad = entry(urgency="critical", recommendation_class="order", nine_m="M10", verification="check it")
    p = "\n".join(check_register(reg(bad), w).problems)
    for t in ("urgency 'critical'", "recommendation_class 'order'", "nine_m 'M10'", "verification should be"):
        assert t in p
    good = entry(urgency="alert", recommendation_class="action already taken", nine_m="M4",
                 verification={"method": "sample", "indicator": "share"})
    assert not [x for x in check_register(reg(good), w).problems if "urgency" in x or "nine_m" in x or "verif" in x]


def test_regulatory_count(w, wsdir, tmp_path):
    r = reg(entry(regulatory_touchpoint="PSM"), entry(lr_id="LR-10", regulatory_touchpoint=""), entry(lr_id="LR-11"))
    assert check_register(r, w).stats["regulatory_flagged"] == 1
    p = tmp_path / "r.json"
    p.write_text(json.dumps(r))
    out = subprocess.run([sys.executable, str(PMLC), "check-register", str(wsdir), str(p)],
                         capture_output=True, text=True).stdout
    assert "1 learning(s) flagged for legal or compliance review" in out


def test_check_register_json(wsdir, tmp_path):
    p = tmp_path / "learnings-register.json"
    p.write_text(json.dumps(MINI_REG))
    r = subprocess.run([sys.executable, str(PMLC), "check-register", str(wsdir), str(p), "--json"],
                       capture_output=True, text=True)
    d = json.loads(r.stdout)
    assert set(d) == {"ok", "problems", "warnings", "stats"} and d["ok"] is True
    assert set(d["stats"]) == {"learnings", "findings_covered", "findings_total", "regulatory_flagged",
                               "p1_without_strong_fix"}
    rec = pack_record(load_manifest(wsdir), p)
    assert rec and rec["ok"] is True


@pytest.mark.parametrize("text,tier", [
    ("Engineering review of the procedure", "administrative"), ("engineering", "engineering"),
    ("Engineering controls", "engineering"), ("Interlock", "unclassified"), ("PPE", "ppe"),
    ("Personal protective equipment", "ppe"), ("eliminate or substitute", "unclassified"),
    ("Engineering control: interlock", "engineering"), ("Administrative (procedure)", "administrative"),
    ("plant redesign, engineering", "engineering"), ("signal engineering", "engineering"),
    ("significant engineering change", "engineering"), ("engineering plan", "administrative"),
    ("engineering sign-off", "administrative"), ("Elimination and substitution", "unclassified"),
])
def test_norm_hoc_rules(text, tier):
    assert norm_hoc(text) == tier


def test_ambiguous_hoc_is_a_warning(w):
    e = entry(recommendations=[{"what": "w", "hoc_tier": "Interlock", "leading_indicator": "i"}])
    r = check_register(reg(e), w)
    assert "LR-09 rec 1: hoc_tier 'Interlock' is ambiguous" in r.warnings
    assert not [x for x in r.problems if "hoc_tier" in x]


def fixture_reg():
    return json.loads((FIX / "mini-register.json").read_text(encoding="utf-8"))


def test_mini_register_fixture_is_sound(w):
    r = check_register(fixture_reg(), w, strict=False)
    assert not r.problems, r.problems


def test_register_md_has_status_handling_and_draft(w):
    md = register_markdown(fixture_reg(), w, pmlc.effective_handling(fixture_reg(), w))
    assert md.startswith("# Synthetic register")
    assert "DRAFT" in md and pmlc.STATUS_PHRASE in md
    for line in pmlc.handling_lines(pmlc.effective_handling(fixture_reg(), w)):
        assert line in md
    for h in ("## Summary", "## Priority 1 learnings", "## All learnings"):
        assert h in md
    assert md.endswith(pmlc.BRAND + "\n")


def test_register_md_golden(w):
    md = register_markdown(fixture_reg(), w, pmlc.effective_handling(fixture_reg(), w))
    golden = FIX / "mini-register.md"
    if os.environ.get("PMLC_UPDATE_GOLDEN"):
        golden.write_text(md, encoding="utf-8")
    assert golden.exists(), "run with PMLC_UPDATE_GOLDEN=1, then review it"
    assert md == golden.read_text(encoding="utf-8")


def test_register_md_command(wsdir, tmp_path):
    p = tmp_path / "reg.json"
    p.write_text(json.dumps(fixture_reg()))
    out = tmp_path / "o.md"
    run("register-md", str(wsdir), str(p), "--out", str(out))
    assert out.read_text(encoding="utf-8").startswith("# Synthetic register")


def test_hazira_register_still_passes(tmp_path):
    export = HAZIRA / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
    run("ingest", str(export), "--slug", "hazira-gas-release-fire", "--root", str(tmp_path))
    ws = tmp_path / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"
    r = subprocess.run([sys.executable, str(PMLC), "check-register", str(ws), "--json",
                        str(HAZIRA / "outputs" / "learnings-register.json")], capture_output=True, text=True)
    d = json.loads(r.stdout)
    assert d["problems"] == [], d["problems"]
    p1 = [x for x in d["warnings"] if "priority-1 learning" in x]
    assert {x.split()[2] for x in p1} == {"LR-08", "LR-12"}, p1
    assert len(d["warnings"]) == EXPECTED_HAZIRA_WARNINGS, d["warnings"]


EXPECTED_HAZIRA_WARNINGS = 19
