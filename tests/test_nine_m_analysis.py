"""Phase 5 Task 22: the `nine-m-analysis` skill (spec §7.4-§7.7). Its manifest, profile, SKILL.md flow, workflow
step and register feed, and its Hazira golden (OD5-1): a scripted session (`nine-m-replay --accept-recommended`)
committed as nine-m-session.json, the pack written from it with the demo banner, and the nine-m-map.json side output."""
import csv
import io
import json
import re
import shutil
import subprocess
import sys

import pytest

from test_pmlc import PMLC, ROOT, run
from pmlc_lib.ninem import NINE_M_CODES, NINE_M_NONE
from pmlc_lib.pack.profiles import BANNERS

pytest.importorskip("openpyxl")
SKILL = "nine-m-analysis"
SKILLS_DIR = ROOT / "skills"
REFS = SKILLS_DIR / "learnings-coach" / "references"
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
OUTPUTS = SAMPLE / "outputs"
REGISTER = OUTPUTS / "learnings-register.json"
GOLDEN = OUTPUTS / f"{SKILL}.json"
SESSION = OUTPUTS / "nine-m-session.json"
MAP = OUTPUTS / "nine-m-map.json"
NEVER = re.compile(r"\b(?:disciplin\w*|accountab\w*|consequence management|punish\w*|sanction\w*|blame\w*)\b", re.I)


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def skill_md() -> str:
    return (SKILLS_DIR / SKILL / "SKILL.md").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def hz(tmp_path_factory):
    """A Hazira workspace with the seed and a fresh scripted replay, and the register and golden in its outputs."""
    root = tmp_path_factory.mktemp("hazira-9m")
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root),
        "--overlay", "india-process-site")
    ws = root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"
    run("nine-m-seed", str(ws))
    run("nine-m-replay", str(ws), "--accept-recommended")
    for p in (REGISTER, GOLDEN):
        shutil.copy(p, ws.parent / "outputs" / p.name)
    return ws


def _sections(pack) -> dict:
    return {s["id"]: s for s in pack["sections"]}


def _answers(session) -> dict:
    """{(m, step): (answer text, cites of the chosen suggestion)} from the session records."""
    out = {}
    for r in session["records"]:
        a = r["answer"]
        sug = r["suggestions"][a["choice"] - 1] if a.get("choice") else {"cites": []}
        out[(r["m"], r["step"])] = (a["text"], sug["cites"])
    return out


# ------------------------------------------------------------------------------------------- contract

def test_manifest_as_planned():
    m = load(SKILLS_DIR / SKILL / "skill.json")
    assert (m["kind"], m["interactive"], m["audiences"]) == ("interactive", True, [])
    assert m["requires"] == ["workspace", "nine-m-seed"] and m["optional_inputs"] == ["register"]
    assert m["produces"] == {"pack": SKILL, "files": ["outputs/nine-m-map.json"]}
    assert (m["formats"], m["share_default"], m["embed_default"], m["since"]) == \
        (["docx", "csv"], "internal", "cited", "2.0.0")
    assert len(m["questions"]) == 1 and m["questions"][0].startswith("Which Ms should we work through?")


def test_profile_as_planned():
    p = load(REFS / "pack-profiles.json")[SKILL]
    assert [(s["id"], s["kinds"], s["min"], s["max"]) for s in p["sections"]] == [
        ("nine-m-overview", ["table"], 1, 1),
        ("m*", ["learning", "barrier", "recommendation", "question"], 0, 12),
        ("not-relevant", ["table"], 0, 1),
        ("cross-m", ["graph"], 0, 1),
        ("organisation-context", ["para"], 0, 5)]
    assert p["rules"] == ["nine-m-overview", "nine-m-cites", "m1-balance", "no-owner-due", "banner:nine-m-demo"]
    assert p["bottom_line"] == {"min": 3, "max": 7} and p["coverage_floor"] == 0.25


def test_skill_md_sets_out_the_interview():
    t = skill_md()
    assert len(t.splitlines()) <= 150
    for need in ("PMLC nine-m-seed <ws>", "PMLC nine-m-suggest <ws>", "--record", "PMLC nine-m-answer <ws>",
                 "PMLC nine-m-actions-template <ws>", "one question per turn", "6 questions per M plus 4",
                 "3d", "organisation-context", "data_quality", "references/nine-m.md", NINE_M_NONE,
                 "nine-m-replay", BANNERS["nine-m-demo"], "say in `data_quality` they are yours",
                 "not with a seventh question"):
        assert need in t, need
    never = t.split("Never offered", 1)[1].split("\n\n", 1)[0].lower()
    for word in ("discipline", "accountability", "consequences"):
        assert word in never, word
    hand = t.split("## Check and hand over", 1)[1]
    assert hand.index("check-pack") < hand.index("PMLC pack") < hand.index("nine-m-actions-template")


def test_action_design_step_unplanned():
    wf = load(REFS / "workflows.json")["action-design"]["steps"]
    step = next(s for s in wf if s["skill"] == SKILL)
    assert "planned" not in step
    order = [s["skill"] for s in wf]
    assert order.index("learnings-register") < order.index(SKILL)


def test_register_feed_gather_line():
    t = (SKILLS_DIR / "learnings-register" / "SKILL.md").read_text(encoding="utf-8")
    gather = t.split("## Gather", 1)[1].split("\n## ", 1)[0]
    assert "outputs/nine-m-map.json" in gather and "nine_m_subcategory" in gather and "nine_m" in gather
    reg = load(ROOT / "tests" / "fixtures" / "registers" / "mini-register.json")
    assert any(e.get("nine_m") in NINE_M_CODES for e in reg["entries"])


# ------------------------------------------------------------------------------------------- golden

def test_golden_session_is_the_scripted_replay(hz):
    """OD5-1: the committed session is exactly what nine-m-replay --accept-recommended writes on Hazira today."""
    s = load(SESSION)
    assert s["mode"] == "replay"
    assert (hz / "nine_m_session.json").read_bytes() == SESSION.read_bytes()
    assert len(s["records"]) <= 9 * 6 + 4                                    # the question budget
    for r in s["records"]:
        assert 3 <= len(r["suggestions"]) <= 5 and r["suggestions"][-1]["text"] == NINE_M_NONE, r["q"]


def test_golden_passes_strict_and_language(hz):
    out = run("check-pack", str(hz), str(hz.parent / "outputs" / GOLDEN.name), "--strict", "--register", str(REGISTER))
    assert "OK:" in out and "problem" not in out, out
    lang = run("check-language", str(hz), str(hz.parent / "outputs" / GOLDEN.name))
    assert "check-language: 0 errors" in lang, lang


def test_golden_is_written_from_the_session():
    pack, ans = load(GOLDEN), _answers(load(SESSION))
    secs = _sections(pack)
    assert pack["pack"] == pack["skill"] == SKILL and "handling" not in pack
    assert 3 <= len(pack["bottom_line"]) <= 7
    paras = [it["text"] for s in pack["sections"] for it in s["items"] if it["kind"] == "para"]
    assert BANNERS["nine-m-demo"] in paras
    rows = secs["nine-m-overview"]["items"][0]["rows"]
    assert [r[0].split()[0] for r in rows] == list(NINE_M_CODES)
    for n, m in enumerate(NINE_M_CODES, 1):
        rel = ans[(m, "relevance")][0]
        assert rel.startswith("Relevant"), m                                   # every M is relevant on Hazira
        sec = secs[f"m{n}"]
        sub = re.match(r"(M\d\.\d\d)", ans[(m, "subcategory")][0]).group(1)
        assert sub in rows[n - 1][3], m                                        # the overview names the subcategory
        learning = next(it for it in sec["items"] if it["kind"] == "learning")
        cond = [x for x in ans[(m, "condition")][1] if x.startswith("FND-")]
        assert set(cond) <= set(learning["cites"]), m                          # the condition's findings are cited
        driver = re.search(r"System driver: ([A-Z]+ \d+\.\d+)", ans[(m, "driver")][0]).group(1)
        assert driver in learning["explanation"], m                            # 3d is in the learning (M1 first)
        recs = [it for it in sec["items"] if it["kind"] == "recommendation"]
        tier = ans[(m, "change")][0].split()[0].lower()
        assert recs and all(r["hoc_tier"] == tier for r in recs), m             # 3f, the direction chosen
        assert all(re.search(r"\b(?:corrective|preventive)\b", r["change"], re.I) for r in recs), m
        assert any(it["kind"] == "barrier" for it in sec["items"]), m
    assert "not-relevant" not in secs
    assert secs["cross-m"]["items"][0]["kind"] == "graph"
    lrs = [it["learning"] for s in pack["sections"] for it in s["items"] if it.get("learning")]
    assert len(lrs) == len(set(lrs))                                           # one M per register learning


def test_golden_says_which_choices_were_derived():
    """Fix round 1: with no 3g record and no 3f answer choosing corrective or preventive, the pack says the indicators
    and the labels are the analyst's own (SKILL.md: 'derive ... and say in data_quality they are yours')."""
    pack, session = load(GOLDEN), load(SESSION)
    recs = [it for s in pack["sections"] for it in s["items"] if it["kind"] == "recommendation"]
    steps = {r["step"] for r in session["records"]}
    dq = " ".join(x["text"] for x in pack["data_quality"]).lower()
    if any(r.get("indicator") for r in recs) and "indicator" not in steps:
        assert "indicators" in dq and "analyst's own" in dq, dq
    chosen = [r["answer"]["text"] for r in session["records"] if r["step"] == "change"]
    if any(r["change"].lower().startswith(("corrective", "preventive")) for r in recs) and all(
            "corrective or preventive" in a.lower() for a in chosen):                # no answer chose either
        assert "corrective or preventive label" in dq, dq


def test_golden_elimination_changes_are_not_gates():
    """Fix round 1: an elimination-tier change removes the hazard or the task; it is not a workflow gate, an approval
    rule or an automatic trip (engineering or administrative controls, which rec-review bands lower)."""
    gate = re.compile(r"\b(?:cannot (?:raise|close|extend)|until an approved|without the review and approval|"
                      r"isolated at once|escalation chain)\b", re.I)
    for s in load(GOLDEN)["sections"]:
        for it in s["items"]:
            if it["kind"] == "recommendation" and it["hoc_tier"] == "elimination":
                assert re.search(r"\b(?:remov\w*|retire)\b", it["change"], re.I), (s["id"], it["change"])
                assert not gate.search(it["change"]), (s["id"], it["change"])


def test_golden_d7_roles_and_never_offered():
    pack = load(GOLDEN)

    def dicts(x):
        if isinstance(x, dict):
            yield x
            for v in x.values():
                yield from dicts(v)
        elif isinstance(x, list):
            for v in x:
                yield from dicts(v)
    assert all("owner" not in d and "by_when" not in d for d in dicts(pack))   # D7, anywhere in the pack
    text = json.dumps(pack)
    assert not re.search(r"\[(?:CE|JEA|CCTV CR)\]|\bMr\.|\bShri\b", text)       # roles only
    assert not NEVER.search(text)


def test_golden_coverage_of_top_rated(hz):
    import pmlc
    from pmlc_lib.pack.profiles import top_rated_of
    w = pmlc.load_ws(hz)
    top = set(top_rated_of(w, [f["id"] for f in w["findings"]]))
    text = json.dumps(load(GOLDEN))
    got = {x for x in top if x in text}
    assert len(got) >= 0.25 * len(top), (len(got), len(top))


def test_golden_side_output_and_template(hz, tmp_path):
    """pack writes the committed nine-m-map.json; every condition has its M and subcategory; the actions template
    lists every recommendation with Owner, Due date and Status blank (D7)."""
    out = tmp_path / "out"
    out.mkdir()
    pk = out / GOLDEN.name
    shutil.copy(GOLDEN, pk)
    r = subprocess.run([sys.executable, str(PMLC), "pack", str(hz), str(pk), "--out", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (out / "nine-m-map.json").read_bytes() == MAP.read_bytes()
    mp = load(MAP)
    assert sorted({c["m"] for c in mp["conditions"].values()}) == list(NINE_M_CODES)
    for c in mp["conditions"].values():
        assert c["subcategory"] and c["subcategory"].startswith(c["m"] + "."), c
        assert c["recommendation_ids"], c
    sheet = out / f"{SKILL}.actions-template.csv"
    r = subprocess.run([sys.executable, str(PMLC), "nine-m-actions-template", str(hz), str(pk), "--format", "csv",
                        "--out", str(sheet)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    rows = list(csv.reader(io.StringIO(sheet.read_text(encoding="utf-8"))))
    n = sum(1 for s in load(GOLDEN)["sections"] for it in s["items"] if it["kind"] == "recommendation")
    assert len(rows) == n + 1 and all(x[6] == x[7] == x[8] == "" for x in rows[1:])


def test_owner_on_a_recommendation_fails_without_strict(hz, tmp_path):
    pack = load(GOLDEN)
    rec = next(it for s in pack["sections"] for it in s["items"] if it["kind"] == "recommendation")
    rec["by_when"] = "30 June"
    bad = tmp_path / GOLDEN.name
    bad.write_text(json.dumps(pack), encoding="utf-8")
    r = subprocess.run([sys.executable, str(PMLC), "check-pack", str(hz), str(bad)], capture_output=True, text=True)
    assert r.returncode != 0 and "owner and due dates are set by the organisation" in r.stdout + r.stderr


def test_golden_demo_banner_needed_on_a_replay(hz, tmp_path):
    """The banner is what makes the scripted golden pass: without it the replayed session fails --strict."""
    pack = load(GOLDEN)
    for s in pack["sections"]:
        s["items"] = [it for it in s["items"] if it.get("text") != BANNERS["nine-m-demo"]]
    pack["sections"] = [s for s in pack["sections"] if s["items"]]
    bad = tmp_path / GOLDEN.name
    bad.write_text(json.dumps(pack), encoding="utf-8")
    r = subprocess.run([sys.executable, str(PMLC), "check-pack", str(hz), str(bad), "--strict"],
                       capture_output=True, text=True)
    assert r.returncode != 0 and "banner nine-m-demo" in r.stdout + r.stderr
