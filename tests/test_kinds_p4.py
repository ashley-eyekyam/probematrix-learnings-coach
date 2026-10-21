"""Phase 4, Task 16: the `toolbox` and `script` kinds, the SRT and narration exports, scenario injects and the card
fields "Did you know?" and "What can you do?" (L2-18, L4-19, L4-30, R3; Ruling P4-5). Synthetic fixtures only."""
import copy
import re
from pathlib import Path

import pytest

from test_pmlc import ws  # noqa: F401  (ws is a module-scoped fixture)
from test_pack import alpha4_copy, fixture, item, pack_with, render_fixture
import pmlc  # noqa: E402
import pmlc_pack as pp  # noqa: E402

from pmlc_lib import render as R  # noqa: E402
from pmlc_lib.pack import schema as PS  # noqa: E402
from pmlc_lib.render import script as RS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / "skills" / "learnings-coach" / "references"
SRT_TIME = r"\d{2}:\d{2}:\d{2},\d{3}"
SRT_CUE = re.compile(rf"^(\d+)\n({SRT_TIME}) --> ({SRT_TIME})\n((?:.+\n){{1,2}})$")

TOOLBOX = {"kind": "toolbox", "id": "tb-leak", "duration": "5 min",
           "opening_question": "When did you last restart a pump after a seal change?",
           "story": "A pump went back into service after a seal change without a leak test [FND-0001].",
           "warning_signs": ["No test record on the work order", "A seal that looks different"],
           "one_change": "Ask for the signed leak-test record before any restart.",
           "crew_question": "Where is the test record kept on this unit?", "cites": ["FND-0001"]}
LONG = ("The seal was changed on the night shift and the pump was needed by the morning. Nobody asked for the "
        "leak-test record, because the work order had no line for it and the test rig was in the other unit.")
SCRIPT = {"kind": "script", "id": "pa-restart", "title": "Before you restart", "channel": "video",
          "purpose": "A short film for the start of shift.", "cites": ["FND-0001"],
          "segments": [{"visual": "A pump on its skid.", "narration": "This pump was restarted untested [FND-0001].",
                        "seconds": 30, "on_screen": "Test, record, restart"},
                       {"visual": "The work order.", "narration": LONG, "seconds": 45, "cites": ["FND-0002"]}]}
INJECTS = [{"offset": "+00:05", "text": "The gas alarm shows on the display only."},
           {"offset": "+00:15", "text": "The control room cannot reach the field operator.",
            "decision": "Isolate now, or wait for the shift supervisor?"}]


@pytest.fixture(scope="module")
def w(ws):  # noqa: F811
    return pmlc.load_ws(ws)


def _ctx(w, pack, **kw):
    from pmlc_lib.handling import effective_handling
    return R.RenderContext(w=w, pack=PS.with_item_ids(pack), run="r", generated="2020-09-24", embed="cited",
                           eh=effective_handling(pack, w), **kw)


def _item_html(page, item_id):
    m = re.search(rf'<div class="item k-\w+" id="i-{item_id}">(.*?)</div>(?=<div class="item|</div></details>)',
                  page, re.S)
    assert m, item_id
    return m.group(1)


def _in_order(text, needles):
    pos = [text.find(x) for x in needles]
    assert -1 not in pos, [x for x, p in zip(needles, pos) if p < 0]
    assert pos == sorted(pos), list(zip(needles, pos))


def test_kind_registry():
    assert {"toolbox", "script"} <= set(PS.KINDS)
    assert PS.KINDS["toolbox"]["cite"] and PS.KINDS["script"]["cite"]
    assert ["injects", "injects"] in PS.KINDS["scenario"]["fields"]
    assert ["segments", "segments"] in PS.KINDS["script"]["fields"]
    assert {"did_you_know", "what_you_can_do"} <= set(PS.KINDS["card"]["opt"])
    assert R.FORMATS["srt"].kind == "data" and R.FORMATS["narration"].kind == "data"


def test_toolbox_kind(w):
    r = pp.check_pack(pack_with(TOOLBOX), w)
    assert r.problems == [] and not [x for x in r.warnings if "toolbox" in x or "unknown field" in x], r
    bad = copy.deepcopy(TOOLBOX)
    del bad["crew_question"]
    assert "sections[0].items[0].crew_question: required for toolbox" in pp.check_pack(pack_with(bad), w).problems
    three = dict(TOOLBOX, warning_signs=["a", "b", "c"])
    r = pp.check_pack(pack_with(three), w)
    assert r.problems == [] and "toolbox tb-leak: a toolbox talk has two warning signs" in r.warnings
    one = dict(TOOLBOX, id=None)
    one.pop("id")
    one["warning_signs"] = ["a"]
    assert "toolbox s1-1: a toolbox talk has two warning signs" in pp.check_pack(pack_with(one), w).warnings
    parts = [TOOLBOX["opening_question"], "A pump went back", TOOLBOX["warning_signs"][0], TOOLBOX["one_change"],
             TOOLBOX["crew_question"]]
    page = pp.render_pack_html(w, pack_with(TOOLBOX), "r", "2020-09-24")
    body = _item_html(page, "tb-leak")
    labels = ["Opening question", "The story", "Warning signs", "One thing to do differently tomorrow",
              "Question to the crew"]
    _in_order(body, [x for pair in zip(labels, parts) for x in pair])
    assert 'data-id="FND-0001"' in body and "5 min" in body and "Toolbox talk" in body
    md = pp.render_pack_md(pack_with(TOOLBOX), w)
    _in_order(md, [x for pair in zip(labels, parts) for x in pair])
    assert "1. **Opening question:**" in md and "5. **Question to the crew:**" in md
    style = (REFS / "output-style.md").read_text(encoding="utf-8")
    assert "**Toolbox talk** (five minutes)" in style and "`toolbox` item" in style


def test_script_kind_and_exports(w):
    for mutate, needle in [(lambda s: s["segments"][0].update(seconds=0), "segments[0].seconds"),
                           (lambda s: s["segments"][0].update(seconds=True), "segments[0].seconds"),
                           (lambda s: s["segments"][1].update(seconds=601), "segments[1].seconds"),
                           (lambda s: s["segments"][0].pop("narration"), "segments[0].narration: required"),
                           (lambda s: s["segments"][0].update(cites="FND-0001"), "segments[0].cites"),
                           (lambda s: s["segments"].append("x"), "segments[2]: must be an object"),
                           (lambda s: s.update(channel="tv"), "channel: must be one of video, radio, pa, screen")]:
        s = copy.deepcopy(SCRIPT)
        mutate(s)
        probs = pp.check_pack(pack_with(s), w).problems
        assert any(needle in x for x in probs), (needle, probs)
    r = pp.check_pack(pack_with(SCRIPT), w)
    assert r.problems == [] and not [x for x in r.warnings if "unknown field" in x or "plain text" in x], r
    assert "FND-0002" in PS.cited_ids(pack_with(SCRIPT))[0]                 # segment cites count

    page = pp.render_pack_html(w, pack_with(SCRIPT), "r", "2020-09-24")
    body = _item_html(page, "pa-restart")
    assert '<th scope="col">Visual</th>' in body and '<th scope="col">Narration</th>' in body
    assert body.count("<th ") == 2 and "Total duration: 1:15 (min:sec)" in body and "0:30–1:15" in body
    assert "Test, record, restart" in body and 'data-id="FND-0002"' in body
    md = pp.render_pack_md(pack_with(SCRIPT), w)
    assert "| Visual | Narration |\n|---|---|\n| 0:00–0:30 · A pump on its skid. (On screen: Test, record, restart) |" in md
    assert "Total duration: 1:15 (min:sec)" in md and "**Script:** Before you restart [FND-0001]" in md

    ctx = _ctx(w, pack_with(SCRIPT))
    srt = R.render("srt", ctx)
    assert [o.name for o in srt] == ["test-pack.pa-restart.srt"]
    cues = srt[0].data.split("\n\n")
    assert cues[-1] == "" and srt[0].data.endswith("\n\n")
    parsed = []
    for n, cue in enumerate(cues[:-1], 1):
        m = SRT_CUE.match(cue + "\n")
        assert m, cue
        assert int(m.group(1)) == n
        lines = m.group(4).rstrip("\n").split("\n")
        assert all(len(x) <= 42 for x in lines) and len(lines) <= 2, lines
        parsed.append((m.group(2), m.group(3), " ".join(lines)))
    assert parsed[0][:2] == ("00:00:00,000", "00:00:30,000")
    assert parsed[0][2] == "This pump was restarted untested."            # citations are not spoken
    assert all(a[1] == b[0] for a, b in zip(parsed, parsed[1:]))             # cumulative, no gaps
    assert parsed[-1][1] == "00:01:15,000" and len(parsed) > 2              # the long narration split
    rest = parsed[1:]
    ms = [RS.srt_ms(b) - RS.srt_ms(a) for a, b, _ in rest]
    assert max(ms) - min(ms) <= 1 and sum(ms) == 45000                      # an even share of 45 s
    assert " ".join(t for _, _, t in rest) == LONG
    assert RS.srt_time(3723004) == "01:02:03,004"

    nar = R.render("narration", ctx)
    assert [o.name for o in nar] == ["test-pack.pa-restart.narration.txt"]
    assert nar[0].data == "This pump was restarted untested.\n\n" + LONG + "\n"
    for x in (pmlc.STATUS_PHRASE, "A pump on its skid", "Test, record, restart", "FND-", SCRIPT["title"]):
        assert x not in nar[0].data and x not in srt[0].data, x
    assert nar[0].guard_text == nar[0].data and srt[0].guard_text == srt[0].data

    ctx2 = _ctx(w, pack_with(item("para", cites=["FND-0001"])))
    assert R.render("srt", ctx2) == [] and R.render("narration", ctx2) == []
    assert ctx2.notes == ["srt: nothing to write (no script items)", "narration: nothing to write (no script items)"]


def test_srt_wrap_rules():
    assert RS.srt_cues("one two", 10_000) == [(0, 10_000, ["one two"])]
    words = " ".join(["abcdefghij"] * 18)                         # 3 words a line (4 would be 43): 6 lines, 3 cues
    cues = RS.srt_cues(words, 10_000, start=5_000)
    assert [c[:2] for c in cues] == [(5_000, 8_333), (8_333, 11_666), (11_666, 15_000)]
    assert all(len(c[2]) <= 2 and all(len(x) <= 42 for x in c[2]) for c in cues)
    assert RS.srt_cues("x" * 50, 1000)[0][2] == ["x" * 42, "x" * 8]       # a word longer than a line is broken
    assert RS.spoken("Restarted [FND-0001; EVD-0001] untested, see FND-0002.") == "Restarted untested, see."


def test_injects(w):
    sc = item("scenario", cites=["FND-0001"], injects=copy.deepcopy(INJECTS))
    r = pp.check_pack(pack_with(sc), w)
    assert r.problems == [] and not [x for x in r.warnings if "unknown field" in x], r
    for mutate, needle in [(lambda i: i[0].update(offset="10 min"), "injects[0].offset: must be"),
                           (lambda i: i[0].update(offset="+1:60"), "injects[0].offset: must be"),
                           (lambda i: i[1].pop("text"), "injects[1].text: required"),
                           (lambda i: i[1].update(decision=""), "injects[1].decision: must be non-empty text"),
                           (lambda i: i.append("x"), "injects[2]: must be an object")]:
        bad = copy.deepcopy(sc)
        mutate(bad["injects"])
        probs = pp.check_pack(pack_with(bad), w).problems
        assert any(needle in x for x in probs), (needle, probs)
    assert any("injects: must be a non-empty list" in x
               for x in pp.check_pack(pack_with(dict(sc, injects=[])), w).problems)
    page = pp.render_pack_html(w, pack_with(sc), "r", "2020-09-24")
    m = re.search(r'<ol class="timeline injects">(.*?)</ol>', page, re.S)
    assert m
    _in_order(m.group(1), ["<time>+00:05</time>", INJECTS[0]["text"], "<time>+00:15</time>", INJECTS[1]["text"],
                           "Decision point", INJECTS[1]["decision"]])
    assert m.group(1).count("<li>") == 2 and m.group(1).count("Decision point") == 1
    md = pp.render_pack_md(pack_with(sc), w)
    assert "1. **+00:05** The gas alarm shows" in md
    assert "2. **+00:15** The control room" in md and "**Decision point:** Isolate now" in md


def test_card_r3_fields(w):
    card = item("card", did_you_know=["Most seal leaks start within an hour of a restart."],
                what_you_can_do=["Ask for the test record.", "Stop the restart if it is missing."])
    r = pp.check_pack(pack_with(card), w)
    assert r.problems == [] and not [x for x in r.warnings if "unknown field" in x], r
    page = pp.render_pack_html(w, pack_with(card), "r", "2020-09-24")
    md = pp.render_pack_md(pack_with(card), w)
    for out in (page, md):
        _in_order(out, ["Did you know?", "Most seal leaks", "What can you do?", "Ask for the test record.",
                        "Stop the restart"])
    assert "**Did you know?**\n- Most seal leaks" in md and "Did you know?:" not in md
    assert any("must be a non-empty list of text" in x
               for x in pp.check_pack(pack_with(dict(card, did_you_know="x")), w).problems)
    plain = pp.render_pack_html(w, pack_with(item("card")), "r", "2020-09-24")
    assert "Did you know?" not in plain and "What can you do?" not in plain


def test_new_kinds_render_in_every_format():
    pack = fixture("all-kinds")
    kinds = {it["kind"] for s in pack["sections"] for it in s["items"]}
    assert {"toolbox", "script"} <= kinds and set(PS.KINDS) <= kinds
    assert any(it.get("injects") for s in pack["sections"] for it in s["items"])
    assert any(it.get("did_you_know") for s in pack["sections"] for it in s["items"])
    for name, f in R.FORMATS.items():
        if f.kind == "document":
            outs = render_fixture("all-kinds", name)
            assert outs and all(o.data for o in outs), name
    for view in ("full", "learner"):
        assert render_fixture("all-kinds", "html", view=view)[0].data
    assert [o.name for o in render_fixture("all-kinds", "srt")] == ["all-kinds.video-1.srt"]
    assert [o.name for o in render_fixture("all-kinds", "narration")] == ["all-kinds.video-1.narration.txt"]
    for name in ("frontline-learning-cards", "emergency-response-learnings", "training-designer"):
        page = render_fixture(name, "html")[0].data
        assert "Traceback" not in page


NEW = {"toolbox", "script"}


def _alpha5_copy(p):
    """The pack as alpha.5 wrote it: no toolbox or script items, no injects and no card R3 fields."""
    p = copy.deepcopy(p)
    for s in p["sections"]:
        s["items"] = [it for it in s["items"] if it.get("kind") not in NEW]
        for it in s["items"]:
            for f in ("injects", "did_you_know", "what_you_can_do"):
                it.pop(f, None)
    p["sections"] = [s for s in p["sections"] if s["items"]]
    return p


@pytest.mark.parametrize("name", ["frontline-learning-cards", "emergency-response-learnings", "training-designer",
                                  "all-kinds"])
def test_old_packs_unaffected(w, name):
    old = _alpha5_copy(fixture(name))
    assert old != fixture(name)                                    # the fixture does carry a new thing
    for p in (old, alpha4_copy(old)):
        r = pp.check_pack(p, w)
        assert r.problems == [], r.problems
        page = pp.render_pack_html(w, p, "r", "2020-09-24")
        md = pp.render_pack_md(p, w)
        for label in ("Did you know?", "What can you do?", "Decision point", "Total duration", "Opening question"):
            assert label not in page and label not in md, label
    assert pp.render_pack_md(old, w) != pp.render_pack_md(fixture(name), w)


def test_pack_schema_reference_names_the_new_roles():
    t = (REFS / "pack-schema.md").read_text(encoding="utf-8")
    assert "`graph`, `segments` or `injects`)" in t and "did_you_know[]" in t and "what_you_can_do[]" in t
    for x in ("`toolbox`", "`script`", "opening_question", "crew_question", "on_screen", "+HH:MM"):
        assert x in t, x


def test_srt_and_narration_shared_copy(w, tmp_path):
    """A shared copy's SRT and narration come from the masked pack: an invented listed name never reaches them."""
    import argparse
    from pmlc_lib.handling import effective_handling, share_ctx, shared_copy, shared_name
    names = tmp_path / "names.txt"
    names.write_text("Quillon Vantress\n", encoding="utf-8")
    s = copy.deepcopy(SCRIPT)
    s["segments"][0]["narration"] = "Quillon Vantress restarted the pump untested [FND-0001]."
    pack = pack_with(s)
    share = share_ctx(argparse.Namespace(names=str(names), orgs=None), w, "external")
    ctx = R.RenderContext(w=shared_copy(w, share, w), pack=PS.with_item_ids(shared_copy(pack, share, w)), run="r",
                          generated="2020-09-24", embed="cited", eh=effective_handling(pack, w), share=share)
    for fmt in ("srt", "narration"):
        out = R.render(fmt, ctx)
        assert out and "Vantress" not in out[0].data and "[name]" in out[0].data, fmt
        assert shared_name(tmp_path / out[0].name, "external").name.endswith(".external." + out[0].name.rsplit(".", 1)[1])
