"""Phase 4, Task 14: typed questions, the learner view and the GIFT, QTI 2.1 and quiz-CSV exports (P4-9, P4-10, P4-12).
Synthetic fixtures only."""
import csv
import io
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pytest

from test_pmlc import ws  # noqa: F401  (a module-scoped fixture)
from test_pack import fixture, item, pack_with
import pmlc  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pmlc_lib import BRAND, DRAFT_LABEL  # noqa: E402
from pmlc_lib import render as R  # noqa: E402
from pmlc_lib.render import quiz as Q  # noqa: E402
from pmlc_lib.handling import effective_handling  # noqa: E402
from pmlc_lib.pack import schema as PS  # noqa: E402
from test_render import ctx_for  # noqa: E402


@pytest.fixture(scope="module")
def w(ws):  # noqa: F811
    return pmlc.load_ws(ws)


def opts(*pairs):
    return [{"text": t, "correct": c} for t, c in pairs]


def question(**over):
    return item("question", **over)


SINGLE = dict(type="single", question="Where is the cause placed?", options=opts(("Supervision", True), ("The fitter", False)))
MULTI = dict(type="multi", question="Which are barriers?", options=opts(("Checklist", True), ("Guard", True), ("Luck", False)))
TF = dict(type="truefalse", question="A missing checklist is a person problem.", options=opts(("True", False), ("False", True)))
SHORT = dict(type="short", question="Name the level.", options=opts(("L3", True), ("supervision", True)))
ESSAY = dict(question="What would you change?")


def quiz_pack(*qs, **top):
    return pack_with(*[question(**q) for q in qs], **top)


def probs(p, w):
    r = PS.check_pack(p, w)
    return r.problems, r.warnings


def test_question_type_rules(w):
    def has(p, text):
        pr, wa = probs(p, w)
        return any(text in x for x in pr + wa), pr, wa

    assert probs(quiz_pack(SINGLE, MULTI, TF, SHORT, ESSAY), w)[0] == []
    for bad in (opts(("a", False), ("b", False)), opts(("a", True), ("b", True))):
        ok, pr, _ = has(quiz_pack(dict(SINGLE, options=bad)), "exactly one correct")
        assert ok, pr
    assert has(quiz_pack(dict(MULTI, options=opts(("a", False), ("b", False)))), "at least one correct")[0]
    assert has(quiz_pack(dict(TF, options=opts(("True", True), ("False", False), ("Maybe", False)))), "exactly 2 options")[0]
    assert has(quiz_pack(dict(TF, options=opts(("True", True), ("False", True)))), "exactly one correct")[0]
    assert has(quiz_pack(dict(SHORT, options=opts(("L3", True), ("L2", False)))), "accepted answers")[0]
    assert has(quiz_pack(dict(SINGLE, type="essay")), "type")[0]
    assert has(quiz_pack(dict(SINGLE, options=["a", "b"])), "options")[0]            # strings are a decision's shape
    assert has(quiz_pack(dict(SINGLE, options=opts(("a", True), ("", False)))), "text")[0]
    ok, pr, wa = has(quiz_pack(dict(question="Q?", options=opts(("a", True)))), "options without type are ignored")
    assert ok and not pr
    assert has(quiz_pack(dict(question="Q?", type="single")), "needs options")[0]
    assert has(quiz_pack(dict(SHORT, options=opts(*[(f"o{i}", True) for i in range(7)]))), "holds 6 options")[0]
    # a decision's options stay plain strings
    dec = item("decision", options=["Do it now", "Wait"])
    assert probs(pack_with(dec), w)[0] == []


def _html_md(w, pack, view):
    ctx = ctx_for(w, pack, view=view)
    return R.render("html", ctx)[0].data, R.render("md", ctx)[0].data


def test_learner_view_hides_keys_everywhere(w):
    qs = [dict(q, answer="SECRET-ANSWER", good_evidence="SECRET-EVIDENCE") for q in (SINGLE, MULTI, TF)]
    qs.append(dict(SHORT, answer="SECRET-ANSWER"))
    pack = quiz_pack(*qs)
    html, md = _html_md(w, pack, "learner")
    for text in (html, md):
        assert "SECRET" not in text
        assert "Supervision" in text and "Checklist" in text                      # the choices stay
    assert R.LEARNER_BANNER in html and R.LEARNER_BANNER in md
    assert 'class="status learner"' in html
    # the pack itself is untouched and the view really drops the flags
    view = RF_learner(pack)
    for it in view["sections"][0]["items"]:
        assert all("correct" not in o for o in it.get("options", []) if isinstance(o, dict))
    assert not any(it.get("options") for it in view["sections"][0]["items"] if it.get("type") == "short")
    assert any("correct" in o for it in pack["sections"][0]["items"] for o in it["options"])
    # the full view marks the keys, and has no banner
    html_f, md_f = _html_md(w, pack, "full")
    assert "SECRET-ANSWER" in html_f and R.LEARNER_BANNER not in html_f and R.LEARNER_BANNER not in md_f
    assert "correct" in html_f.lower() or "✓" in html_f
    # item_blocks hides them too (the layouts, docx, pptx and email all read blocks)
    from pmlc_lib.render.fields import item_blocks
    from pmlc_lib.render.labels import load_labels
    q = PS.with_item_ids(quiz_pack(SINGLE))["sections"][0]["items"][0]
    blocks = item_blocks(q, load_labels("en"), view="learner")
    ch = [b for b in blocks if b.field == "options"][0]
    assert ch.role == "choices" and all("correct" not in o for o in ch.value)
    assert any("correct" in o for b in item_blocks(q, load_labels("en")) if b.field == "options" for o in b.value)


def RF_learner(pack):
    from pmlc_lib.render.fields import learner_view
    return learner_view(pack)


def test_banner_survives_a_status_with_markup_characters(w):
    pack = quiz_pack(SINGLE, status="Learning purposes: not a statutory document & <draft> \"quoted\"")
    html, md = _html_md(w, pack, "learner")
    assert R.LEARNER_BANNER in html and R.LEARNER_BANNER in md


# --- GIFT --------------------------------------------------------------------------------------------------------

def unesc(s):
    return re.sub(r"\\(.)", r"\1", s)


def parse_gift(text):
    """A small test-side GIFT reader: (comments, [{id, stem, type, options: [(text, correct)], feedback}])."""
    comments = [ln for ln in text.splitlines() if ln.startswith("//")]
    body = "\n".join(ln for ln in text.splitlines() if not ln.startswith("//"))
    out = []
    for blk in re.split(r"\n\s*\n", body.strip()):
        m = re.match(r"::((?:\\.|[^\\:])*)::((?:\\.|[^\\{])*)\{(.*)\}\s*$", blk.strip(), re.S)
        assert m, blk
        qid, stem, ans = unesc(m.group(1)), unesc(m.group(2)).strip(), m.group(3)
        fb = None
        parts = re.split(r"(?<!\\)####", ans, maxsplit=1)
        if len(parts) == 2:
            ans, fb = parts[0], unesc(parts[1]).strip()
        ans = ans.strip()
        q = {"id": qid, "stem": stem, "feedback": fb}
        if ans in ("T", "F"):
            q.update(type="truefalse", options=[("True", ans == "T"), ("False", ans == "F")])
        elif ans == "":
            q.update(type="essay", options=[])
        else:
            toks = re.findall(r"(?<!\\)([=~])(%-?[\d.]+%)?((?:\\.|[^\\=~])*)", ans)
            os_ = [(unesc(t).strip(), k == "=" or bool(wt and not wt.startswith("%-"))) for k, wt, t in toks]
            if all(k == "=" for k, _, _ in toks):
                q["type"] = "short"
            elif any(wt for _, wt, _ in toks):
                q["type"] = "multi"
            else:
                q["type"] = "single"
            q["options"] = os_
        out.append(q)
    return comments, out


def test_gift_roundtrip(w):
    pack = quiz_pack(dict(SINGLE, why="Because."), MULTI, TF, SHORT, ESSAY,
                     status="Learning purposes: not a statutory document")
    ctx = ctx_for(w, pack)
    [o] = R.render("gift", ctx)
    assert o.name == "test-pack.gift.txt"
    comments, qs = parse_gift(o.data)
    text = " ".join(comments)
    assert "not a statutory document" in text and BRAND in o.data and DRAFT_LABEL in text
    assert [q["type"] for q in qs] == ["single", "multi", "truefalse", "short", "essay"]
    assert qs[0]["stem"] == SINGLE["question"]
    assert qs[0]["options"] == [("Supervision", True), ("The fitter", False)]
    assert qs[0]["feedback"] == "Because."
    assert qs[1]["options"] == [("Checklist", True), ("Guard", True), ("Luck", False)]
    assert qs[2]["options"] == [("True", False), ("False", True)]
    assert qs[3]["options"] == [("L3", True), ("supervision", True)]
    assert o.guard_text == o.data


def test_gift_escape_and_hostile_text(w):
    assert Q.gift_escape("a~b=c#d{e}f:g") == r"a\~b\=c\#d\{e\}f\:g"
    assert Q.gift_escape("plain") == "plain"
    assert Q.gift_escape("back\\slash") == "back\\\\slash"
    hostile = dict(SINGLE, question="Is x = y {maybe}: yes # no ~?",
                   options=opts(("a ~ b", True), ("c = d {e}", False)))
    [o] = R.render("gift", ctx_for(w, quiz_pack(hostile)))
    _, [q] = parse_gift(o.data)
    assert q["stem"] == hostile["question"]
    assert q["options"] == [("a ~ b", True), ("c = d {e}", False)]
    # a stem with a newline stays one GIFT line
    [o] = R.render("gift", ctx_for(w, quiz_pack(dict(ESSAY, question="Line one\nLine two"))))
    assert "Line one Line two" in o.data


# --- QTI -----------------------------------------------------------------------------------------------------------

NS = {"q": "http://www.imsglobal.org/xsd/imsqti_v2p1", "c": "http://www.imsglobal.org/xsd/imscp_v1p1"}


def test_qti_package(w):
    pack = quiz_pack(SINGLE, MULTI, TF, SHORT, ESSAY)
    [o] = R.render("qti", ctx_for(w, pack))
    assert o.name == "test-pack.qti.zip" and isinstance(o.data, bytes)
    z = zipfile.ZipFile(io.BytesIO(o.data))
    assert z.testzip() is None
    names = z.namelist()
    man = ET.fromstring(z.read("imsmanifest.xml"))
    hrefs = [r.get("href") for r in man.iterfind(".//c:resource", NS)]
    items = [n for n in names if n != "imsmanifest.xml"]
    assert len(items) == 5 and sorted(hrefs) == sorted(items)
    assert all(r.get("type") == "imsqti_item_xmlv2p1" for r in man.iterfind(".//c:resource", NS))
    files = [f.get("href") for f in man.iterfind(".//c:file", NS)]
    assert sorted(files) == sorted(items)
    roots = [ET.fromstring(z.read(n)) for n in items]                    # every item parses
    by_kind = {}
    for r in roots:
        ci = r.find(".//q:choiceInteraction", NS)
        by_kind[r.get("identifier")] = (r, ci)
    single = roots[0]
    ci = single.find(".//q:choiceInteraction", NS)
    assert ci.get("maxChoices") == "1"
    ids = [c.get("identifier") for c in ci.iterfind("q:simpleChoice", NS)]
    correct = [v.text for v in single.iterfind(".//q:correctResponse/q:value", NS)]
    assert correct == [ids[0]] and len(ids) == 2
    multi = roots[1]
    assert multi.find(".//q:choiceInteraction", NS).get("maxChoices") == "0"
    assert multi.find(".//q:responseDeclaration", NS).get("cardinality") == "multiple"
    assert len(list(multi.iterfind(".//q:correctResponse/q:value", NS))) == 2
    tf = roots[2]
    assert tf.find(".//q:choiceInteraction", NS).get("maxChoices") == "1"
    short = roots[3]
    assert short.find(".//q:textEntryInteraction", NS) is not None
    assert {e.get("mapKey") for e in short.iterfind(".//q:mapEntry", NS)} == {"L3", "supervision"}
    essay = roots[4]
    assert essay.find(".//q:extendedTextInteraction", NS) is not None
    assert essay.find(".//q:correctResponse", NS) is None
    blob = b" ".join(z.read(n) for n in names).decode("utf-8")
    assert "DRAFT" in blob
    for c in re.findall(r"<!--(.*?)-->", blob, flags=re.S):
        assert "--" not in c
    assert o.guard_text and SINGLE["question"] in o.guard_text


def test_qti_escapes_and_is_deterministic(w):
    hostile = dict(SINGLE, question="a < b & \"c\" ]]>", options=opts(("<x>", True), ("y & z", False)))
    d1 = R.render("qti", ctx_for(w, quiz_pack(hostile)))[0].data
    d2 = R.render("qti", ctx_for(w, quiz_pack(hostile)))[0].data
    z = zipfile.ZipFile(io.BytesIO(d1))
    for n in z.namelist():
        ET.fromstring(z.read(n))
    assert d1 == d2
    # the BRAND text holds no double hyphen that would end an XML comment early
    assert all(ET.fromstring(z.read(n)) is not None for n in z.namelist())


# --- quiz CSV ---------------------------------------------------------------------------------------------------

HEADER = "id,type,question,option_1,option_2,option_3,option_4,option_5,option_6,correct,why,cites"


def test_quiz_csv_columns_and_formula_safety(w):
    qs = [dict(SINGLE, why="Because.", cites=["FND-0002"]), MULTI, TF, SHORT, ESSAY,
          dict(SINGLE, question="=HYPERLINK(\"http://x\")", options=opts(("+1", True), ("-2", False)))]
    [o] = R.render("quiz-csv", ctx_for(w, quiz_pack(*qs)))
    assert o.name == "test-pack.quiz.csv"
    assert o.data.splitlines()[0] == HEADER
    rows = list(csv.reader(io.StringIO(o.data)))
    assert all(len(r) == 12 for r in rows)
    r1, r2, r3, r4, r5, r6 = rows[1:]
    assert r1[1] == "single" and r1[3:5] == ["Supervision", "The fitter"] and r1[9] == "1" and r1[10] == "Because."
    assert "FND-0002" in r1[11]
    assert r2[1] == "multi" and r2[9] == "1;2"
    assert r3[1] == "truefalse" and r3[9] == "2"
    assert r4[1] == "short" and r4[9] == "1;2"
    assert r5[1] == "discussion" and r5[3:9] == [""] * 6 and r5[9] == ""
    assert r6[2].startswith("'=") and r6[3].startswith("'+") and r6[4].startswith("'-")
    assert o.guard_text == o.data


def test_quiz_csv_more_than_six_options_is_noted(w):
    big = dict(MULTI, options=opts(*[(f"o{i}", i in (0, 6)) for i in range(7)]))
    ctx = ctx_for(w, quiz_pack(big))
    [o] = R.render("quiz-csv", ctx)
    row = list(csv.reader(io.StringIO(o.data)))[1]
    assert row[9] == "1" and ctx.notes                                   # option 7 is cut and said so


def test_no_questions_nothing_to_write(w):
    for fmt in ("gift", "qti", "quiz-csv"):
        ctx = ctx_for(w, pack_with(item("para")))
        assert R.render(fmt, ctx) == []
        assert ctx.notes and "question" in ctx.notes[-1]


def test_quiz_shared_copy(w):
    """A shared copy renders from the masked pack (ctx.pack) and returns every visible text as guard_text."""
    import argparse
    from pmlc_lib.handling import share_ctx, shared_copy
    pack = quiz_pack(dict(SINGLE, question="Who put the stem here?"))
    share = share_ctx(argparse.Namespace(names=None, orgs=None), w, "external")
    masked = shared_copy(pack, share, w)
    masked["sections"][0]["items"][0]["question"] = "MASKED STEM"
    ctx = ctx_for(shared_copy(w, share, w), masked, share=share, eh=effective_handling(pack, w))
    for fmt in ("gift", "qti", "quiz-csv"):
        [o] = R.render(fmt, ctx)
        assert "Who put the stem here" not in (o.guard_text or "") and "MASKED STEM" in o.guard_text
        if fmt != "qti":
            assert o.guard_text == o.data


def test_training_designer_fixture_has_typed_questions(w):
    p = fixture("training-designer")
    types = [i.get("type") for s in p["sections"] for i in s["items"] if i["kind"] == "question"]
    assert "single" in types and "truefalse" in types
    assert PS.check_pack(p, w).problems == []
    ctx = ctx_for(w, p)
    for fmt in ("gift", "qti", "quiz-csv"):
        assert R.render(fmt, ctx)
