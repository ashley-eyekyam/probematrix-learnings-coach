"""Task 13 (Phase 6): the learning-effectiveness-plan skill. Its Hazira golden pack pastes the effect-plan engine's
schedule and levels tables and its audit questions unchanged, fills the Lagging column the engine leaves blank (rule
leading-lagging), opens with the effectiveness banner, points to the organisation's verification log, writes no owner,
date or status, and passes check-pack --strict with the register and check-language with no errors."""
import json
import shutil

import pytest

from test_pmlc import ROOT, run, run_fail
from pmlc_lib import privacy
from pmlc_lib.pack.profiles import BANNERS

pytest.importorskip("openpyxl")
SKILL = "learning-effectiveness-plan"
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
GOLDEN = SAMPLE / "outputs" / f"{SKILL}.json"
REGISTER = SAMPLE / "outputs" / "learnings-register.json"
FIXTURE = ROOT / "tests" / "fixtures" / "packs" / f"{SKILL}.json"
REFS = ROOT / "skills" / "learnings-coach" / "references"


@pytest.fixture(scope="module")
def hz(tmp_path_factory):
    root = tmp_path_factory.mktemp("hazira-effectiveness")
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root),
        "--overlay", "india-process-site")
    ws = root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"
    shutil.copy(REGISTER, ws.parent / "outputs" / REGISTER.name)
    shutil.copy(GOLDEN, ws.parent / "outputs" / GOLDEN.name)
    run("effect-plan", str(ws), "--register", str(REGISTER))
    return ws


def _pack(p=GOLDEN):
    return json.loads(p.read_text(encoding="utf-8"))


def _section(pack, sid):
    return next(s for s in pack["sections"] if s["id"] == sid)


def _engine(hz, *flags):
    return json.loads(run("effect-plan", str(hz), "--register", str(REGISTER), *flags))


def test_manifest():
    m = json.loads((ROOT / "skills" / SKILL / "skill.json").read_text(encoding="utf-8"))
    assert (m["kind"], m["requires"]) == ("analysis", ["workspace", "register", "effect-plan"])
    assert (m["formats"], m["share_default"], m["embed_default"], m["since"]) == \
        (["docx", "csv"], "internal", "cited", "2.0.0")
    assert m["produces"]["pack"] == SKILL and m["interactive"] is False


def test_profile_entry():
    prof = json.loads((REFS / "pack-profiles.json").read_text(encoding="utf-8"))[SKILL]
    got = [(s["id"], s["kinds"], s["min"], s["max"]) for s in prof["sections"]]
    assert got == [("banner", ["para"], 1, 1), ("schedule", ["table"], 1, 1), ("levels", ["table"], 1, 1),
                   ("indicators", ["table"], 1, 1), ("audit", ["question"], 3, 25),
                   ("verification-log", ["para"], 1, 1)]
    assert prof["rules"] == ["no-owner-due", "banner:effectiveness", "leading-lagging"]
    assert prof["bottom_line"] == {"min": 1, "max": 3}


def test_follow_up_is_unplanned():
    wf = json.loads((REFS / "workflows.json").read_text(encoding="utf-8"))["follow-up"]["steps"]
    assert wf[0] == {"skill": SKILL}
    plan = _pack(ROOT / "tests" / "fixtures" / "plans" / "follow-up.json")
    order = [s["skill"] for s in plan["steps"]]
    assert "engine:effect-plan" in order and order.index("engine:effect-plan") < order.index(SKILL)
    assert all(s["status"] != "planned" for s in plan["steps"])
    eng = next(s for s in plan["steps"] if s["skill"] == "engine:effect-plan")
    # effect-plan refuses to run without --register, so the plan prints the line that runs as written
    assert eng["commands"] == ["PMLC effect-plan <ws> --register <run>/outputs/learnings-register.json"]


def test_golden_pastes_engine_items(hz):
    pack = _pack()
    for sid, which in (("schedule", "schedule"), ("levels", "levels")):
        assert _section(pack, sid)["items"] == [_engine(hz, "--table-item", which)], sid   # pasted whole
    eng = _engine(hz, "--items", "audit")
    got = _section(pack, "audit")["items"]
    assert 3 <= len(got) <= 25
    by_q = {it["question"]: it for it in eng}
    for it in got:                                   # each engine question unchanged; good_evidence may be added
        base = {k: v for k, v in it.items() if k != "good_evidence"}
        assert base == by_q[it["question"]], it["question"]
    assert len(_engine(hz, "--json")["rows"]) == 97                       # 11x5 + 14x3 (calibration, P6-8)


def test_golden_indicators_fill_lagging(hz):
    eng = _engine(hz, "--table-item", "indicators")
    tab = _section(_pack(), "indicators")["items"][0]
    assert tab["columns"] == eng["columns"] == ["LR", "Leading", "Lagging"]
    assert [r[:2] for r in tab["rows"]] == [r[:2] for r in eng["rows"]]   # LR and Leading pasted from the engine
    assert all(r[2].strip() for r in tab["rows"])                         # the model fills every Lagging cell
    assert tab["row_cites"] == eng["row_cites"]


def test_golden_banner_log_and_no_dates():
    pack = _pack()
    banner = _section(pack, "banner")["items"]
    assert [it["text"] for it in banner] == [BANNERS["effectiveness"]] and "cites" not in banner[0]
    log = _section(pack, "verification-log")["items"][0]["text"]
    assert "PMLC templates <ws> verification" in log and "organisation" in log
    assert all(not it.get("owner") and not it.get("by_when") for s in pack["sections"] for it in s["items"])
    text = json.dumps(pack, ensure_ascii=False)
    for rx in (privacy.ISO_DATE_RX, privacy.DMY_TEXT_RX, privacy.MDY_TEXT_RX):
        assert not rx.search(text), rx.pattern[:40]         # offsets from adoption only (D7)
    assert "status" not in {k for s in pack["sections"] for it in s["items"] for k in it}


def test_golden_passes_strict_and_language(hz):
    out = run("check-pack", str(hz), str(hz.parent / "outputs" / GOLDEN.name), "--strict", "--register", str(REGISTER))
    assert "OK:" in out and "problem" not in out, out                 # run() also asserts exit 0
    lang = run("check-language", str(hz), str(hz.parent / "outputs" / GOLDEN.name))
    assert "check-language: 0 errors" in lang, lang


def test_fixture_needs_lagging():
    """The synthetic fixture passes; a blank Lagging cell is a problem even without --strict."""
    from pmlc_lib.pack import profiles
    pack = _pack(FIXTURE)
    prof = profiles.load()[SKILL]
    assert profiles.hard(pack, prof) == []
    tab = _section(pack, "indicators")["items"][0]
    tab["rows"][0][2] = ""
    assert any(m.startswith("leading-lagging:") for m in profiles.hard(pack, prof))


def test_csv_lists_every_check_with_org_columns_blank(hz):
    """--format csv (skill.json) writes one actions.csv row per scheduled check, counted from adoption, with the
    owner, due, status, CAPA and effectiveness columns blank for the organisation (D7)."""
    import csv
    out = hz.parent / "outputs"
    target = out / f"{SKILL}.actions.csv"
    target.unlink(missing_ok=True)
    run("pack", str(hz), str(out / GOLDEN.name), "--format", "csv")
    rows = list(csv.DictReader(target.read_text(encoding="utf-8").splitlines()))
    assert len(rows) == 97
    first = rows[0]
    assert first["lr_id"] == "LR-01"
    assert first["change"] == "Check that LR-01 is communicated (Kirkpatrick L1), 30 days after adoption"
    assert first["indicator"].startswith("Share of critical pressure-boundary spares")
    for r in rows:
        assert not any(r[c] for c in ("owner", "due", "status", "capa_ref", "effectiveness_check")), r
        assert "after adoption" in r["change"] and r["cites"]
    run_fail("pack", str(hz), str(out / GOLDEN.name), "--format", "csv")   # never replaced: the organisation fills it
