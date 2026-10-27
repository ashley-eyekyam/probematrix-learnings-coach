"""Phase 6 Task 9: the `safety-moment-deck` skill (session leaders: supervisors and trainers giving a short session,
in the style of the CCPS Process Safety Beacon). Its manifest, audience entry, profile and routing; the section deck
(profile "pptx_slides": "sections", 3-6 content slides); check tiles on the poster; the srt and narration files only
with a script; and its Hazira golden pack, which reuses the frontline cards' LR ids."""
import json
import re
import subprocess
import sys

import pytest

from test_pmlc import PMLC, ROOT, run, ws  # noqa: F401  (ws is a module-scoped fixture)
from test_pack import RUN, fixture, item, pack_with, render_fixture
import pmlc  # noqa: E402

from pmlc_lib import render as R  # noqa: E402
from pmlc_lib.handling import effective_handling  # noqa: E402
from pmlc_lib.pack import schema as PS  # noqa: E402
from pmlc_lib.render import layouts as LY  # noqa: E402
from pmlc_lib.render.pptx import pptx_notes_text, pptx_slides_text  # noqa: E402

SKILL = "safety-moment-deck"
SKILLS_DIR = ROOT / "skills"
REFS = SKILLS_DIR / "learnings-coach" / "references"
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
REGISTER = SAMPLE / "outputs" / "learnings-register.json"
CARDS = SAMPLE / "outputs" / "frontline-learning-cards.json"
GOLDEN = SAMPLE / "outputs" / f"{SKILL}.json"
SECTIONS = [("what-happened", ["para"], 1, 2), ("did-you-know", ["para"], 1, 3), ("what-you-can-do", ["check"], 2, 5),
            ("questions", ["question"], 2, 4), ("script", ["script"], 0, 1)]


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def skill_md() -> str:
    return (SKILLS_DIR / SKILL / "SKILL.md").read_text(encoding="utf-8")


def content_slides(data: bytes) -> list:
    """The slides between the title slide and the closing slide."""
    return pptx_slides_text(data)[1:-1]


# ----------------------------------------------------------------------------- manifest, profile, routing

def test_manifest_as_planned():
    m = load(SKILLS_DIR / SKILL / "skill.json")
    assert m["kind"] == "audience" and m["audiences"] == ["session-leaders"]
    assert m["requires"] == ["workspace", "register"] and m["optional_inputs"] == ["frontline-learning-cards"]
    assert m["formats"] == ["pptx", "poster", "srt", "narration"] and m["share_default"] == "internal"
    assert m["since"] == "2.0.0" and m["embed_default"] == "cited" and m["produces"]["pack"] == SKILL


def test_audience_entry():
    a = next(x for x in load(REFS / "audiences.json") if x["id"] == "session-leaders")
    assert a["skill"] == SKILL and a["tier"] == "T2" and a["reading_level"] == "plain"
    assert "supervisors" in a["typical_people"] and "trainers" in a["typical_people"]
    assert "| Session leaders |" in (REFS / "audiences.md").read_text(encoding="utf-8")


def test_profile_as_planned():
    p = load(REFS / "pack-profiles.json")[SKILL]
    assert [(s["id"], s["kinds"], s["min"], s["max"]) for s in p["sections"]] == SECTIONS
    assert p["rules"] == ["no-owner-due"] and p["bottom_line"] == {"min": 1, "max": 3}
    assert p["pptx_slides"] == "sections"


def test_training_workflow_runs_the_deck():
    steps = load(REFS / "workflows.json")["training"]["steps"]
    assert steps[-1] == {"skill": SKILL}
    plan = load(ROOT / "tests" / "fixtures" / "plans" / "training.json")
    step = next(s for s in plan["steps"] if s["skill"] == SKILL)
    assert step["status"] == "todo" and step["planned_for"] is None and step["produces"] == SKILL
    assert f"PMLC check-pack <ws> <run>/outputs/{SKILL}.json --strict" in step["commands"]


def test_hub_routes_to_the_deck():
    hub = (SKILLS_DIR / "learnings-coach" / "SKILL.md").read_text(encoding="utf-8")
    assert re.search(rf"^\|[^|]+\| `{SKILL}` \|", hub, re.M)


# ----------------------------------------------------------------------------- the section deck

def test_fixture_deck_has_three_to_six_content_slides():
    """Spec §6.2: 3-6 slides. The section deck gives one bottom-line slide and one slide per section; questions share
    their section's slide."""
    p = fixture(SKILL)
    o = render_fixture(SKILL, "pptx")[0]
    body = content_slides(o.data)
    assert 3 <= len(body) <= 6, len(body)
    assert len(body) == 1 + len(p["sections"])
    heads = [s["heading"] for s in p["sections"]]
    assert [s.split("\n", 1)[0] for s in body[1:]] == heads
    q = next(s for s in p["sections"] if s["id"] == "questions")
    qs = body[1 + p["sections"].index(q)]
    assert all(it["question"] in qs for it in q["items"])
    assert all(it["answer"] not in "\n".join(body) for it in q["items"] if "answer" in it)   # answers: notes only
    notes = "\n".join(pptx_notes_text(o.data))
    assert all(it["answer"] in notes for it in q["items"] if "answer" in it)


def test_section_deck_bottom_line_on_one_slide():
    p = fixture(SKILL)
    p["bottom_line"] = [{"text": f"Point {i}.", "cites": ["FND-0001"]} for i in range(1, 4)]
    o = render_fixture(SKILL, "pptx", pack=p)[0]
    first = content_slides(o.data)[0]
    assert all(f"Point {i}." in first for i in range(1, 4))
    assert len(content_slides(o.data)) == 1 + len(p["sections"])


def test_section_deck_shows_a_short_story_in_full():
    """A 2-3 sentence "What happened" is not clipped at the normal 180-character summary on the section deck."""
    p = fixture(SKILL)
    story = ("A pump was restarted after a seal change without a leak test, and the seal leaked within the week. "
             "The work order had no line for the test, so the quickest check became the normal one. "
             "Nobody had asked for the record before the restart.")
    assert 180 < len(story) <= 480
    p["sections"][0]["items"][0]["text"] = story + " [FND-0001]"
    o = render_fixture(SKILL, "pptx", pack=p)[0]
    assert story in content_slides(o.data)[1]


def test_other_profiles_keep_one_slide_per_question(w):
    """A pack without the section deck still gives each question its own slide."""
    p = pack_with(item("question", question="Who signs the test?", why="Because."),
                  item("question", question="Who holds the record?", why="Because."))
    slides = pptx_slides_text(R.render("pptx", ctx(w, p))[0].data)
    assert sum("Who signs the test?" in s for s in slides) == 1
    assert sum("Who holds the record?" in s for s in slides) == 1
    assert not any("Who signs the test?" in s and "Who holds the record?" in s for s in slides)


def ctx(w, pack, **kw):
    kw.setdefault("eh", effective_handling(pack, w))
    return R.RenderContext(w=w, pack=PS.with_item_ids(pack), run=RUN, generated="2020-09-24", embed="cited", **kw)


@pytest.fixture(scope="module")
def w(ws):  # noqa: F811
    return pmlc.load_ws(ws)


# ----------------------------------------------------------------------------- poster, srt and narration

def test_poster_shows_the_checks(w):
    p = fixture(SKILL)
    outs = LY.render_layout(ctx(w, p, layout="poster"))
    doc = outs[0].data
    checks = [it for s in p["sections"] for it in s["items"] if it["kind"] == "check"]
    assert checks and all(PS.ID_RX.sub("", it["text"]).split("[")[0].strip()[:30] in doc for it in checks)
    assert doc.count('<div class="tile">') == min(len(checks), LY.POSTER_MAX)


def test_poster_cards_and_learnings_come_first(w):
    many = [item("check", text=f"Check {i}") for i in range(3)] + [item("learning", lesson=f"Lesson {i}")
                                                                     for i in range(6)]
    doc = LY.render_layout(ctx(w, pack_with(*many), layout="poster"))[0].data
    assert doc.count('<div class="tile">') == LY.POSTER_MAX and "Check 0" not in doc and "Lesson 5" in doc


def test_srt_and_narration_only_with_a_script(w):
    p = fixture(SKILL)
    assert [o.name for o in R.render("srt", ctx(w, p))] and [o.name for o in R.render("narration", ctx(w, p))]
    p["sections"] = [s for s in p["sections"] if s["id"] != "script"]
    c = ctx(w, p)
    assert R.render("srt", c) == [] and R.render("narration", c) == []


# ----------------------------------------------------------------------------- the Hazira golden

@pytest.fixture(scope="module")
def hz(tmp_path_factory):
    pytest.importorskip("openpyxl")
    root = tmp_path_factory.mktemp("hazira-moment")
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root),
        "--overlay", "india-process-site")
    return root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"


def test_hazira_golden_passes_strict(hz):
    pack = load(GOLDEN)
    assert pack["pack"] == SKILL and pack["skill"] == SKILL and "handling" not in pack
    r = subprocess.run([sys.executable, str(PMLC), "check-pack", str(hz), str(GOLDEN), "--strict",
                        "--register", str(REGISTER)], capture_output=True, text=True)
    assert r.returncode == 0 and "OK:" in r.stdout and "problem" not in r.stdout + r.stderr, r.stdout + r.stderr
    r = subprocess.run([sys.executable, str(PMLC), "check-language", str(hz), str(GOLDEN)],
                       capture_output=True, text=True)
    assert r.returncode == 0 and "0 errors" in r.stdout + r.stderr, r.stdout + r.stderr


def test_hazira_golden_reuses_the_cards_lr_ids():
    pack, cards = load(GOLDEN), load(CARDS)
    card_lrs = {it["learning"] for s in cards["sections"] for it in s["items"] if it.get("learning")}
    used = {it["learning"] for s in pack["sections"] for it in s["items"] if it.get("learning")}
    used |= {b["learning"] for b in pack["bottom_line"] if b.get("learning")}
    assert used and used <= card_lrs, used - card_lrs
    checks = [it for s in pack["sections"] if s["id"] == "what-you-can-do" for it in s["items"]]
    assert all(it.get("learning") for it in checks)


def test_hazira_golden_content():
    pack = load(GOLDEN)
    items = {s["id"]: s["items"] for s in pack["sections"]}
    assert [s["id"] for s in pack["sections"]] == [s[0] for s in SECTIONS]
    assert len(items["script"]) == 1 and items["script"][0]["kind"] == "script"
    assert 1 <= len(pack["bottom_line"]) <= 3
    text = json.dumps(pack)
    assert not re.search(r"\[(?:CE|JEA|CCTV CR)\]|\bMr\.", text)                       # roles only
    assert not any(k in it for v in items.values() for it in v for k in ("owner", "by_when", "co_owner"))  # D7
    assert "be more careful" not in text.lower() and "stay vigilant" not in text.lower()


def test_skill_md_names_the_deck_and_poster():
    t = skill_md()
    assert "frontline-learning-cards.json" in t and "LR-" in t and "3 to 6" in t
    assert len(t.splitlines()) <= 150
