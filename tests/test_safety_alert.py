"""Phase 6 Task 7: the `safety-alert` skill (other sites; spec §6.2, Rulings P6-2, P6-3, P6-4, owner decision OD6-1).
Its manifest, audience entry, profile and routing; the urgency added to the Hazira sample register; the synthetic
fixture's one-slide deck; and its Hazira golden pack."""
import json
import re
import subprocess
import sys
from collections import Counter

import pytest

from test_pmlc import PMLC, ROOT, run
from test_pack import render_fixture
from pmlc_lib import alert  # noqa: E402
from pmlc_lib.pack import profiles  # noqa: E402
from pmlc_lib.render.fields import pack_words  # noqa: E402
from pmlc_lib.render.pptx import pptx_slides_text  # noqa: E402

SKILL = "safety-alert"
SKILLS_DIR = ROOT / "skills"
REFS = SKILLS_DIR / "learnings-coach" / "references"
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
REGISTER = SAMPLE / "outputs" / "learnings-register.json"
GOLDEN = SAMPLE / "outputs" / f"{SKILL}.json"
FIXTURE = ROOT / "tests" / "fixtures" / "packs" / f"{SKILL}.json"
SECTIONS = [("what-happened", ["para"], 1, 1), ("why-it-matters", ["para"], 1, 1), ("learnings", ["learning"], 1, 3),
            ("checks", ["check"], 1, 5), ("crew-questions", ["question"], 2, 2), ("contact", ["para"], 1, 1)]
# OD6-1: the P6-3 suggestion rule over the 25 Hazira learnings (calibration: test_calibration_p6)
URGENCY = {"alert": 11, "notice": 12, "information": 2}
REGISTER_WARNINGS_MAX = 17


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def _pmlc(*args):
    return subprocess.run([sys.executable, str(PMLC), *args], capture_output=True, text=True)


# ----------------------------------------------------------------------------- the contracts

def test_manifest_as_planned():
    m = load(SKILLS_DIR / SKILL / "skill.json")
    assert m["kind"] == "audience" and m["audiences"] == ["other-sites"]
    assert m["requires"] == ["workspace", "register"]
    assert m["produces"]["pack"] == SKILL and m["formats"] == ["docx", "pptx", "email", "poster"]
    assert m["share_default"] == "internal" and m["since"] == "2.0.0" and m["embed_default"] == "cited"
    q = " ".join(m["questions"])
    assert "Who is the alert for?" in q and all(w in q for w in ("internal", "sister-site", "industry"))


def test_audience_entry():
    a = next(x for x in load(REFS / "audiences.json") if x["id"] == "other-sites")
    assert a["skill"] == SKILL
    assert a["default_scope"] == load(SKILLS_DIR / SKILL / "skill.json")["scope"]


def test_profile_as_planned():
    p = load(REFS / "pack-profiles.json")[SKILL]
    assert [(s["id"], s["kinds"], s["min"], s["max"]) for s in p["sections"]] == SECTIONS
    assert p["rules"] == ["no-owner-due", "grade-source", "alert-priority-1"]
    assert p["max_words"] == 400 and p["pptx_slides"] == 1 and p["bottom_line"] == {"min": 1, "max": 3}


def test_unplanned_in_first_48_hours_and_sister_sites():
    wf = load(REFS / "workflows.json")
    for preset, mode in (("first-48-hours", "internal"), ("sister-sites", "sister-site")):
        step = next(s for s in wf[preset]["steps"] if s["skill"] == SKILL)
        assert step == {"skill": SKILL, "mode": mode}, preset
        plan = load(ROOT / "tests" / "fixtures" / "plans" / f"{preset}.json")
        st = next(s for s in plan["steps"] if s["skill"] == SKILL)
        assert st["status"] == "todo" and st["mode"] == mode and st["planned_for"] is None
        assert f"PMLC check-pack <ws> <run>/outputs/{SKILL}.json --strict" in st["commands"]


def test_skill_md_names_the_gather_and_formats():
    t = (SKILLS_DIR / SKILL / "SKILL.md").read_text(encoding="utf-8")
    for want in ("PMLC alert-grade <ws> --register <run>/outputs/learnings-register.json",
                 "PMLC register-items <ws> --lr", '"chosen by the user"', '"register urgency"',
                 "--format docx,pptx,email", "--layout poster", "--share external", "--share public"):
        assert want in t, want


# ----------------------------------------------------------------------------- the Hazira register (OD6-1)

def test_hazira_register_urgency_by_the_p6_3_rule():
    """Task 7 adds urgency to all 25 Hazira learnings by the P6-3 suggestion rule (11 alert, 12 notice, 2
    information); nothing else in the register changes."""
    entries = load(REGISTER)["entries"]
    assert len(entries) == 25
    assert all(e.get("urgency") == alert.suggest_grade(e) for e in entries)
    assert Counter(e["urgency"] for e in entries) == URGENCY


@pytest.fixture(scope="module")
def hz(tmp_path_factory):
    pytest.importorskip("openpyxl")
    root = tmp_path_factory.mktemp("hazira-alert")
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root),
        "--overlay", "india-process-site")
    return root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"


def test_hazira_register_still_checks(hz):
    r = _pmlc("check-register", str(hz), str(REGISTER), "--strict")
    out = r.stdout + r.stderr
    assert r.returncode == 0 and "0 problem(s)" in out, out
    assert out.count("warning:") <= REGISTER_WARNINGS_MAX, out


def test_hazira_alert_grade_reads_the_register(hz):
    g = json.loads(run("alert-grade", str(hz), "--register", str(REGISTER), "--json"))
    assert g["grade"] == "alert" and g["grade_source"] == "register urgency" and g["suggested"] is None
    assert g["learnings"] == ["LR-01", "LR-02", "LR-03"] and g["notes"] == []


# ----------------------------------------------------------------------------- the Hazira golden

def test_hazira_golden_passes_strict(hz):
    pack = load(GOLDEN)
    assert pack["pack"] == SKILL and pack["skill"] == SKILL and "handling" not in pack
    r = _pmlc("check-pack", str(hz), str(GOLDEN), "--strict", "--register", str(REGISTER))
    out = r.stdout + r.stderr
    assert r.returncode == 0 and "OK:" in r.stdout and "problem" not in out and "grade-source" not in out, out
    r = _pmlc("check-language", str(hz), str(GOLDEN))
    assert r.returncode == 0 and "0 errors" in r.stdout + r.stderr, r.stdout + r.stderr


def test_hazira_golden_content():
    """mode internal (P6-4: a draft cannot be shared), the grade read from the register (OD6-1), the default
    learnings LR-01..LR-03, a role as the contact, and no owner or date (D7)."""
    pack = load(GOLDEN)
    assert pack["mode"] == "internal" and pack["grade"] == "alert" and pack["grade_source"] == "register urgency"
    items = {s["id"]: s["items"] for s in pack["sections"]}
    assert [s["id"] for s in pack["sections"]] == [s[0] for s in SECTIONS]
    assert [it["learning"] for it in items["learnings"]] == ["LR-01", "LR-02", "LR-03"]
    reg = {e["lr_id"]: e for e in load(REGISTER)["entries"]}
    assert all(reg[it["learning"]]["priority"] == 1 and it["cites"] for it in items["learnings"])
    assert pack_words(pack) <= 400
    sentences = [x for x in re.split(r"(?<=[.!?])\s+", items["what-happened"][0]["text"]) if x.strip()]
    assert 2 <= len(sentences) <= 3
    assert len(items["crew-questions"]) == 2 and all(q.get("why") for q in items["crew-questions"])
    for v in items.values():
        assert not any("owner" in it or "by_when" in it for it in v)
    text = json.dumps(pack)
    assert not re.search(r"\[(?:CE|JEA|CCTV CR)\]|\bMr\.|@|\+?\d{3}[ -]?\d{3}[ -]?\d{4}", text)   # roles only


def test_hazira_golden_priority_2_learning_is_a_problem(hz, tmp_path):
    """alert-priority-1: an alert that carries LR-04 (priority 2) fails, even without --strict."""
    pack = load(GOLDEN)
    sec = next(s for s in pack["sections"] if s["id"] == "learnings")
    sec["items"][0]["learning"] = "LR-04"
    bad = tmp_path / f"{SKILL}.json"
    bad.write_text(json.dumps(pack), encoding="utf-8")
    r = _pmlc("check-pack", str(hz), str(bad), "--register", str(REGISTER))
    assert r.returncode != 0 and "alert-priority-1" in r.stdout + r.stderr and "LR-04" in r.stdout + r.stderr


def test_hazira_golden_owner_fails_even_without_strict(hz, tmp_path):
    pack = load(GOLDEN)
    pack["sections"][-1]["items"][0]["owner"] = "Site HSE manager"
    bad = tmp_path / f"{SKILL}.json"
    bad.write_text(json.dumps(pack), encoding="utf-8")
    r = _pmlc("check-pack", str(hz), str(bad), "--register", str(REGISTER))
    assert r.returncode != 0 and "owner and due dates are set by the organisation" in r.stdout + r.stderr


# ----------------------------------------------------------------------------- the synthetic fixture

def test_fixture_is_a_sister_site_alert():
    """The shared modes appear only in fixtures (P6-4); the fixture's grade was chosen by the user (OD6-1)."""
    pack = load(FIXTURE)
    assert pack["mode"] == "sister-site" and pack["grade"] in ("alert", "notice", "information")
    assert pack["grade_source"] == "chosen by the user"


def test_fixture_deck_is_one_content_slide():
    """pptx_slides 1: cover, one content slide holding every section in order, closing."""
    slides = pptx_slides_text(render_fixture(SKILL, "pptx")[0].data)
    assert len(slides) == 3
    one = slides[1]
    heads = [s["heading"] for s in load(FIXTURE)["sections"]]
    assert [one.index(h) for h in heads] == sorted(one.index(h) for h in heads)


def test_profile_rules_are_known():
    assert set(load(REFS / "pack-profiles.json")[SKILL]["rules"]) <= set(profiles.RULES)
