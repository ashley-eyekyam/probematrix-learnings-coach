"""The register workbook (Phase 3, Task 6): tables, validation lists, print setup, LR links, share, run folder."""
import copy

import openpyxl

from test_pmlc import MINI_REG, run
from test_privacy import _cli, shws as shws, sign, write_doc  # noqa: F401,F811
from pmlc_lib.register.check import HOC_TIERS
import json
import os
import subprocess
import sys
from pathlib import Path
import pytest
from test_pmlc import PMLC, make_export  # noqa: F401
import pmlc  # noqa: E402
from pmlc_lib.register.check import check_register, norm_hoc  # noqa: E402
from pmlc_lib.register.markdown import register_markdown  # noqa: E402
from pmlc_lib.workspace import load_ws, pack_record, load_manifest  # noqa: E402

STATUS = "Learning purposes: not a statutory document"


def two_entry_reg():
    reg = copy.deepcopy(MINI_REG)
    second = copy.deepcopy(reg["entries"][0])
    second["lr_id"], second["title"], second["priority"], second["comparison"] = "LR-02", "Second", 2, "partial"
    reg["entries"].append(second)
    return reg


def build(tmp_path, reg=None, name="reg"):
    rp = write_doc(tmp_path, reg or two_entry_reg(), f"{name}.json")
    out = tmp_path / f"{name}.xlsx"
    run("register-xlsx", str(rp), "--out", str(out))
    return openpyxl.load_workbook(out)


def col_of(ws, header):
    return next(c.column_letter for c in ws[1] if c.value == header)


def test_xlsx_tables_and_filters(tmp_path):
    wb = build(tmp_path)
    for title, name in [("Learnings Register", "LearningsRegister"), ("Recommendations", "Recommendations"),
                        ("Learning Plan", "LearningPlan")]:
        ws = wb[title]
        assert list(ws.tables) == [name], title
        assert ws.tables[name].ref == ws.dimensions
        assert ws.tables[name].tableStyleInfo.name == "TableStyleMedium2"
    assert not wb["Summary"].tables and not wb["About"].tables


def dv_for(ws, col):
    rng = f"{col}2:{col}{ws.max_row}"
    return [d for d in ws.data_validations.dataValidation if d.type == "list" and rng in str(d.sqref).split()]


def test_xlsx_validation_lists(tmp_path):
    wb = build(tmp_path)
    reg, rec = wb["Learnings Register"], wb["Recommendations"]
    assert dv_for(reg, col_of(reg, "Priority"))[0].formula1 == '"1,2,3"'
    assert dv_for(reg, col_of(reg, "Counterpart in comparator report"))[0].formula1 == '"yes,partial,none,not compared"'
    assert dv_for(rec, col_of(rec, "Hierarchy-of-controls tier"))[0].formula1 == '"' + ",".join(HOC_TIERS) + '"'


def test_xlsx_print_setup(tmp_path):
    wb = build(tmp_path)
    for ws in wb.worksheets:
        assert ws.page_setup.orientation == "landscape", ws.title
        assert ws.sheet_properties.pageSetUpPr.fitToPage and ws.page_setup.fitToWidth == 1, ws.title
        assert ws.page_setup.fitToHeight == 0, ws.title
        assert ws.oddHeader.center.text.startswith(STATUS) and ws.oddFooter.center.text, ws.title
    for t in ("Learnings Register", "Recommendations", "Learning Plan"):
        assert wb[t].print_title_rows.replace("$", "") == "1:1"  # openpyxl reloads it as $1:$1


def test_xlsx_lr_hyperlinks(tmp_path):
    wb = build(tmp_path)
    rows = {c.value: c.row for c in wb["Learnings Register"]["A"][1:]}
    rec = wb["Recommendations"]
    cells = rec["A"][1:]
    assert len(cells) == 4
    for c in cells:
        assert c.hyperlink.location == f"'Learnings Register'!A{rows[c.value]}"


def test_xlsx_share_resets_docprops(tmp_path, shws):  # noqa: F811
    ws, orgs = shws
    rp = write_doc(tmp_path, copy.deepcopy(MINI_REG), "reg.json")
    sign(ws, rp, "--classification", "external", "--legal-review", "cleared")
    r = _cli("register-xlsx", str(rp), "--ws", str(ws), "--share", "external", "--orgs", str(orgs))
    assert r.returncode == 0, r.stderr
    p = openpyxl.load_workbook(tmp_path / "learnings-register.external.xlsx").properties
    assert not p.creator and not p.lastModifiedBy
    assert p.created.year == 2000 and p.modified.year == 2000
    # an internal copy keeps the ordinary properties
    internal = build(tmp_path).properties
    assert internal.created.year > 2000


def test_xlsx_run_folder_fallback(tmp_path):
    run_dir = tmp_path / "pmlc-runs" / "2024-03-20-plant-pump-fire"
    (run_dir / "workspace").mkdir(parents=True)
    (run_dir / "workspace" / "findings.json").write_text("[]", encoding="utf-8")
    side = run_dir / "elsewhere"
    side.mkdir()
    rp = write_doc(side, copy.deepcopy(MINI_REG), "reg.json")
    run("register-xlsx", str(rp))
    assert (side / "learnings-register.xlsx").exists()
    assert not (run_dir / "learnings-register.xlsx").exists()
    assert not (run_dir / "outputs").exists()
    wb = openpyxl.load_workbook(side / "learnings-register.xlsx")
    about = {r[0]: r[1] for r in wb["About"].iter_rows(values_only=True) if len(r) > 1 and r[1] is not None}
    assert "no workspace to check" in about["Review status"]


def test_xlsx_new_columns_only_when_present(tmp_path):
    wb = build(tmp_path, name="plain")
    heads = [c.value for c in wb["Learnings Register"][1]]
    assert "Urgency" not in heads and len(heads) == 28
    reg = two_entry_reg()
    reg["entries"][1].update(urgency="alert", recommendation_class="strategic", regulatory_touchpoint="Factories Act s.7")
    wb = build(tmp_path, reg, "rich")
    ws = wb["Learnings Register"]
    heads = [c.value for c in ws[1]]
    assert heads[28:] == ["Urgency", "Recommendation class", "Regulatory touchpoint"]
    assert [c.value for c in ws[3]][28:] == ["alert", "strategic", "Factories Act s.7"]
    assert list(ws.tables) == ["LearningsRegister"] and ws.tables["LearningsRegister"].ref == ws.dimensions
"""Register tests (Phase 3, Task 5): spine fields, check-register problems/warnings/--json, norm_hoc, register-md."""

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
    good = entry(urgency="alert", recommendation_class="action_taken", nine_m="M4",
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
    ("Personal protective equipment", "ppe"), ("eliminate or substitute", "elimination"), ("Engineering / administrative", "engineering"),
    ("Administrative / training", "administrative"),
    ("Engineering control: interlock", "engineering"), ("Administrative (procedure)", "administrative"),
    ("plant redesign, engineering", "engineering"), ("signal engineering", "engineering"),
    ("significant engineering change", "engineering"), ("engineering plan", "administrative"),
    ("engineering sign-off", "administrative"), ("Elimination and substitution", "elimination"),
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
    assert not [x for x in d["warnings"] if "priority-1 learning" in x], d["warnings"]     # X34: why_not_stronger
    assert len(d["warnings"]) == EXPECTED_HAZIRA_WARNINGS, d["warnings"]
    # Without the two why_not_stronger texts (Ruling X34), the priority-1 rule warns on exactly LR-08 and LR-12.
    reg = json.loads((HAZIRA / "outputs" / "learnings-register.json").read_text(encoding="utf-8"))
    for e in reg["entries"]:
        e.pop("why_not_stronger", None)
    bare = tmp_path / "register-without-why.json"
    bare.write_text(json.dumps(reg), encoding="utf-8")
    r = subprocess.run([sys.executable, str(PMLC), "check-register", str(ws), "--json", str(bare)],
                       capture_output=True, text=True)
    d = json.loads(r.stdout)
    p1 = [x for x in d["warnings"] if "priority-1 learning" in x]
    assert {x.split()[2] for x in p1} == {"LR-08", "LR-12"}, p1
    assert len(d["warnings"]) == EXPECTED_HAZIRA_WARNINGS + 2, d["warnings"]


EXPECTED_HAZIRA_WARNINGS = 17       # 19 before Ruling X34 gave LR-08 and LR-12 a why_not_stronger


def test_every_fixture_pack_still_passes_check_pack(wsdir):
    for f in sorted((FIX.parent / "packs").glob("*.json")):
        doc = json.loads(f.read_text(encoding="utf-8"))
        if f.name.startswith("bad-") or not (isinstance(doc, dict) and "pack" in doc and "sections" in doc):
            continue
        r = subprocess.run([sys.executable, str(PMLC), "check-pack", str(wsdir), str(f)], capture_output=True, text=True)
        assert r.returncode == 0, (f.name, r.stdout, r.stderr)
