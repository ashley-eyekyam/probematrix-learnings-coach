"""Phase 4, Task 13: the print layouts (cards, field, toolbox, checklist, poster, paper), QR links and the printable
delivery record (Rulings P4-7, P4-8, P3-15). Synthetic fixtures, plus the public Hazira 2-card pack for the page
count. Toolbox items and scenario injects belong to Task 16: they are hand-built here."""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from test_pmlc import PMLC, ws  # noqa: F401  (ws is a module-scoped fixture)
from test_pack import FIX, GOLDEN_EPOCH, HTML_GOLDEN, RUN, fixture, item, pack_with
import pmlc  # noqa: E402

from pmlc_lib import DRAFT_LABEL, STATUS_PHRASE, VERSION_STAMP  # noqa: E402
from pmlc_lib import render as R  # noqa: E402
from pmlc_lib.handling import effective_handling  # noqa: E402
from pmlc_lib.pack import schema as PS  # noqa: E402
from pmlc_lib.render import layouts as LY  # noqa: E402
from pmlc_lib.render.labels import load_labels  # noqa: E402
from pmlc_lib.templates import DISTRIBUTION_COLUMNS  # noqa: E402

FOOTER = f"{VERSION_STAMP} · ProbeMatrix by Eyekyam"
PAGE_RX = re.compile(r'<section class="page[^"]*">(.*?)</section>', re.S)
BASE = "https://learning.example.org/packs/frontline-learning-cards.html"
TOOLBOX = {"kind": "toolbox", "id": "tb-1", "opening_question": "Who signs the test record before a restart?",
           "story": "A pump went back into service after a seal change without a leak test [FND-0001].",
           "warning_signs": ["No test record on the work order", "A seal from an unlisted supplier"],
           "one_change": "No restart until the leak-test record is signed.",
           "crew_question": "What would make you stop a restart on this shift?", "duration": "5 min",
           "cites": ["FND-0001", "EVD-0001"]}
INJECTS = [{"offset": "+00:05", "text": "The panel shows a gas alarm in the pump bay.",
            "decision": "Do you stop the restart?"},
           {"offset": "+00:20", "text": "The crew lead asks for the test record."}]


@pytest.fixture(scope="module")
def w(ws):  # noqa: F811
    return pmlc.load_ws(ws)


def lay(w, name_or_pack, layout, **kw):
    """The one Output of `layout` for a fixture (by name) or a hand-built pack."""
    pack = fixture(name_or_pack) if isinstance(name_or_pack, str) else name_or_pack
    kw.setdefault("eh", effective_handling(pack, w))
    ctx = R.RenderContext(w=w, pack=PS.with_item_ids(pack), run=RUN, generated="2020-09-24", embed="cited",
                          layout=layout, **kw)
    outs = LY.render_layout(ctx)
    return outs, ctx


def page_of(w, name_or_pack, layout, **kw):
    outs, ctx = lay(w, name_or_pack, layout, **kw)
    assert len(outs) == 1, ctx.notes
    return outs[0].data


def pages(doc):
    return PAGE_RX.findall(doc)


def assert_every_page_marked(doc, draft=True):
    ps = pages(doc)
    assert ps
    for p in ps:
        assert STATUS_PHRASE in p and FOOTER in p
        assert (DRAFT_LABEL in p) == draft


def cards_pack():
    p = fixture("frontline-learning-cards")
    return p, [it for s in p["sections"] for it in s["items"] if it["kind"] == "card"]


# ----------------------------------------------------------------------------- cards

def test_cards_one_page_per_card(w):
    p, cards = cards_pack()
    outs, ctx = lay(w, p, "cards")
    assert [o.name for o in outs] == ["frontline-learning-cards.cards.html"]
    doc = outs[0].data
    ps = pages(doc)
    assert len(ps) == len(cards) + 1                                  # one per card, then the closing count
    for c, pg in zip(cards, ps):
        assert c["title"] in pg
    others = sum(len(s["items"]) for s in p["sections"]) - len(cards)
    assert R.MORE_IN_PACK.format(n=others) in ps[-1]
    assert_every_page_marked(doc, draft=True)
    assert "@page{size:A4}" in doc and outs[0].guard_text == doc
    assert doc.startswith("<!doctype html>") and '<html lang="en">' in doc


def test_cards_approved_pack_has_no_draft_label(w):
    p, _ = cards_pack()
    doc = page_of(w, p, "cards", eh=dict(effective_handling(p, w), effective_status="approved"))
    assert_every_page_marked(doc, draft=False)


def test_cards_a5(w):
    doc = page_of(w, "frontline-learning-cards", "cards", paper="A5")
    assert "@page{size:A5}" in doc and "@page{size:A4}" not in doc


def test_cards_print_test_points_and_injects(w):
    sc = item("scenario", injects=INJECTS)
    p = pack_with(item("test_point", requirement="Leak-test record on file"), sc, TOOLBOX, item("para"))
    doc = page_of(w, p, "cards")
    ps = pages(doc)
    assert len(ps) == 1 + 2 + 1 + 1                     # test point, two injects, toolbox, closing count
    assert "Leak-test record on file" in ps[0]
    assert "+00:05" in ps[1] and "The panel shows a gas alarm" in ps[1] and "Do you stop the restart?" in ps[1]
    assert "+00:20" in ps[2] and "Do you stop" not in ps[2]
    assert TOOLBOX["opening_question"] in ps[3]
    assert R.MORE_IN_PACK.format(n=1) in ps[4]


def test_cards_with_nothing_else_have_no_closing_page(w):
    p = pack_with(item("card", title="Only card"))
    ps = pages(page_of(w, p, "cards"))
    assert len(ps) == 1 and "more items" not in ps[0]


def test_cards_learner_view(w):
    p = pack_with(item("test_point", requirement="R1"), item("question", answer="SECRET-ANSWER"))
    outs, _ = lay(w, p, "cards", view="learner")
    assert outs[0].name == "test-pack.cards.learner.html"
    assert R.LEARNER_BANNER in outs[0].data and "SECRET-ANSWER" not in outs[0].data


def test_layout_translation_and_rtl(w):
    p = pack_with(item("card", title="Karte"), translation_of="test-pack", lang="hi")
    doc = page_of(w, p, "cards")
    assert R.TRANSLATION_NOTE in doc and '<html lang="hi"' in doc
    assert load_labels("hi")["ui.layout.delivery_record"] in page_of(w, p, "field")


# ----------------------------------------------------------------------------- field and the delivery record

def test_field_endnotes_and_delivery_record(w):
    p, cards = cards_pack()
    doc = page_of(w, p, "field")
    ps = pages(doc)
    assert "@page{size:A4}" in doc
    for c, pg in zip(cards, ps):
        assert c["title"] in pg
        assert 'class="cite"' not in pg and not PS.ID_RX.search(pg)      # no inline chips, no bracketed IDs
        assert re.search(r'<sup class="en">\d+', pg)
    notes, record = ps[-2], ps[-1]
    fids, eids = PS.cited_ids(PS.with_item_ids(p))
    cited_in_cards = {x for c in cards for x in c.get("cites", [])}
    listed = re.findall(r'<li id="en-(\d+)">(FND-[0-9A-Za-z]+|EVD-\d+)', notes)
    assert [int(n) for n, _ in listed] == list(range(1, len(listed) + 1))
    assert cited_in_cards <= {x for _, x in listed}
    f = next(x for x in w["findings"] if x["id"] in cited_in_cards)
    assert f"{f['id']}: {f.get('label')}" in notes
    head = re.findall(r'<th scope="col">([^<]*)</th>', record)
    assert head == DISTRIBUTION_COLUMNS[2:] == ["channel", "date", "delivered_by_role", "attendees",
                                                "contractors_included", "questions_raised", "concerns_escalated"]
    rows = re.findall(r"<tr>(.*?)</tr>", record.split("</thead>", 1)[1], re.S)
    assert len(rows) >= 8 and all(re.fullmatch(r"(<td></td>){7}", r) for r in rows)
    assert not re.search(r"\bname\b|signature", record, re.I)
    assert "frontline-learning-cards" in record and p["audience"] in record
    assert_every_page_marked(doc, draft=True)


def test_field_inline_brackets_become_endnote_numbers(w):
    c = item("card", what_happened="Seal fitted [FND-0001; EVD-0001] then restarted [FND-0002].",
             cites=["FND-0001"])
    doc = page_of(w, pack_with(c), "field")
    first = pages(doc)[0]
    assert "Seal fitted<sup" in first and "[" not in first.split("Seal fitted", 1)[1].split("</p>", 1)[0]
    assert not PS.ID_RX.search(first)


# ----------------------------------------------------------------------------- toolbox

def test_toolbox_needs_toolbox_items(w):
    outs, ctx = lay(w, "frontline-learning-cards", "toolbox")
    assert outs == [] and ctx.notes == [R.NOTHING_TO_WRITE.format(fmt="toolbox", why="no toolbox items")]
    tb2 = dict(TOOLBOX, id="tb-2", opening_question="Second talk opener?")
    doc = page_of(w, pack_with(item("para"), TOOLBOX, tb2), "toolbox")
    ps = pages(doc)
    assert len(ps) == 3 and "@page{size:A4}" in doc
    for tb, pg in zip((TOOLBOX, tb2), ps):
        at = [pg.index(tb[f] if isinstance(tb[f], str) else tb[f][0]) for f in
              ("opening_question", "story", "warning_signs", "one_change", "crew_question")]
        assert at == sorted(at), at
    assert "delivered_by_role" in ps[2]
    assert_every_page_marked(doc)


# ----------------------------------------------------------------------------- checklist

def test_checklist_lines(w):
    p = fixture("supervisor-coach")
    doc = page_of(w, p, "checklist")
    checks = [it for s in p["sections"] for it in s["items"] if it["kind"] in ("check", "test_point")]
    assert doc.count("☐") == len(checks)
    holds = [it for it in checks if it.get("hold_point")]
    assert holds and doc.count("Hold point") == len(holds)
    groups = [s for s in p["sections"] if any(it["kind"] in ("check", "test_point") for it in s["items"])]
    assert doc.count(R.CHECK_LINE) == len(groups)
    body = doc
    for s in groups:                                           # each section's checks, then its check line
        i = body.index(s["heading"])
        j = body.index(R.CHECK_LINE, i)
        last = [it for it in s["items"] if it["kind"] == "check"][-1]["text"]
        assert i < body.index(last, i) < j
        body = body[j + 1:]
    assert "recommendation" not in doc and "Known problems" not in doc
    assert_every_page_marked(doc)


def test_checklist_needs_checks(w):
    outs, ctx = lay(w, "precursor-timeline", "checklist")
    assert outs == [] and ctx.notes == [R.NOTHING_TO_WRITE.format(fmt="checklist", why="no check or test_point items")]


# ----------------------------------------------------------------------------- poster

def test_poster_a3(w):
    doc = page_of(w, "precursor-timeline", "poster")
    assert "@page{size:A3 landscape}" in doc and len(pages(doc)) == 1
    assert 'class="htl"' in doc and doc.count('<li class="ev">') >= 2
    many = [item("card", title=f"Card {i}", good_looks_like=f"Good {i}") for i in range(5)]
    many += [item("learning", lesson=f"Lesson {i}") for i in range(4)]
    doc = page_of(w, pack_with(*many), "poster")
    tiles = re.findall(r'<div class="tile">', doc)
    assert len(tiles) == 6 and "Good 4" in doc and "Lesson 0" in doc and "Lesson 1" not in doc
    assert 'class="htl"' not in doc and "<svg" not in doc
    p = fixture("precursor-timeline")
    doc = page_of(w, p, "poster", base_url=BASE)
    assert f'aria-label="QR code: {BASE}"' in doc and p["bottom_line"][0]["text"][:20] in doc
    assert_every_page_marked(doc)


# ----------------------------------------------------------------------------- paper

def test_paper_order(w):
    p = fixture("board-brief")
    doc = page_of(w, p, "paper")
    at = [doc.index(x) for x in ('class="page cover"', "Decisions requested", "Bottom line", '<span class="num">1.</span>',
                                 '<span class="num">1.1</span>', "Annex A", "Annex B")]
    assert at == sorted(at), at
    cover = pages(doc)[0]
    assert p["title"] in cover and "About" in cover and "min read" in cover and DRAFT_LABEL in cover
    annex_a = doc[doc.index("Annex A"):doc.index("Annex B")]
    qs = [it for s in p["sections"] for it in s["items"] if it["kind"] == "question"]
    assert all(q["question"] in annex_a for q in qs)
    annex_b = doc[doc.index("Annex B"):]
    assert "<table" in annex_b and p["sections"][6]["items"][0]["name"] in annex_b
    numbered = doc[doc.index('<span class="num">1.</span>'):doc.index("Annex A")]
    assert "<table" not in numbered and all(q["question"] not in numbered for q in qs)
    assert_every_page_marked(doc)


def test_paper_decisions_first(w):
    p = fixture("top-management-brief")
    doc = page_of(w, p, "paper")
    d = next(it for s in p["sections"] for it in s["items"] if it["kind"] == "decision")
    assert doc.index("Decisions requested") < doc.index(d["decision"]) < doc.index("Bottom line")


def test_paper_renders_every_kind(w):
    doc = page_of(w, fixture("all-kinds"), "paper")
    assert "Annex A" in doc and "Annex B" in doc and "Traceback" not in doc


@pytest.mark.parametrize("layout", LY.LAYOUTS)
def test_every_layout_renders_every_fixture(w, layout):
    from test_pack import pack_fixtures
    for name in pack_fixtures() + ["all-kinds"]:
        outs, ctx = lay(w, name, layout)
        if not outs:
            assert len(ctx.notes) == 1 and ctx.notes[0].startswith(f"{layout}: nothing to write"), (name, ctx.notes)
            continue
        assert outs[0].name == f"{fixture(name)['pack']}.{layout}.html"
        assert_every_page_marked(outs[0].data)


# ----------------------------------------------------------------------------- QR links

def test_qr_on_cards_with_base_url(w):
    p, cards = cards_pack()
    doc = page_of(w, p, "cards", base_url=BASE)
    ids = [it["id"] for it in PS.with_item_ids(p)["sections"][1]["items"]]
    ps = pages(doc)
    for cid, pg in zip(ids, ps):
        assert pg.count(f'aria-label="QR code: {BASE}#i/{cid}"') == 1
    assert "<svg" not in page_of(w, p, "cards")
    assert "<svg" in page_of(w, p, "field", base_url=BASE)


def test_qr_too_long_is_left_out_with_a_note(w):
    p, _ = cards_pack()
    long_url = "https://example.org/" + "x" * 3000
    outs, ctx = lay(w, p, "cards", base_url=long_url)
    assert "<svg" not in outs[0].data
    assert len(ctx.notes) == 1 and ctx.notes[0].startswith("cards: QR codes left out")


# ----------------------------------------------------------------------------- brand

def test_brand_logo_and_organisation(w):
    logo = b"\x89PNG\r\n\x1a\n" + b"0" * 16
    doc = page_of(w, "frontline-learning-cards", "cards",
                  brand=R.Brand("Example Works", "#005a8c", logo, "image/png"))
    assert doc.count('src="data:image/png;base64,') == len(pages(doc)) and "Example Works" in doc


# ----------------------------------------------------------------------------- the command

def _cli(*args):
    env = dict(os.environ, SOURCE_DATE_EPOCH=GOLDEN_EPOCH)
    return subprocess.run([sys.executable, str(PMLC), *args], capture_output=True, text=True, env=env)


@pytest.fixture()
def std_ws(ws, tmp_path):  # noqa: F811
    d = tmp_path / "pmlc-runs" / RUN / "workspace"
    shutil.copytree(ws, d)
    return d


def test_layout_does_not_change_main_page(std_ws, tmp_path):
    out = tmp_path / "o"
    r = _cli("pack", str(std_ws), str(FIX / "board-brief.json"), "--out", str(out), "--layout", "paper",
             "--base-url", BASE)
    assert r.returncode == 0, r.stderr
    assert sorted(p.name for p in out.iterdir()) == ["board-brief.html", "board-brief.md", "board-brief.paper.html"]
    golden = json.loads(HTML_GOLDEN.read_text(encoding="utf-8"))["board-brief"]
    assert hashlib.sha256((out / "board-brief.html").read_bytes()).hexdigest() == golden
    assert "paper layout written to" in r.stdout


def test_layout_flags(std_ws, tmp_path):
    p = str(FIX / "frontline-learning-cards.json")
    for bad in (["--layout", "slides"], ["--paper", "A3"], ["--base-url", "ftp://x.example"]):
        r = _cli("pack", str(std_ws), p, "--out", str(tmp_path / "x"), *bad)
        assert r.returncode == 2, (bad, r.stderr)
    r = _cli("pack", str(std_ws), p, "--out", str(tmp_path / "o"), "--layout", "toolbox")
    assert r.returncode == 0 and "toolbox: nothing to write (no toolbox items)" in r.stderr
    assert sorted(x.name for x in (tmp_path / "o").iterdir()) == ["frontline-learning-cards.html",
                                                                   "frontline-learning-cards.md"]
    r = _cli("pack", str(std_ws), p, "--out", str(tmp_path / "a5"), "--layout", "cards", "--paper", "A5",
             "--view", "learner")
    assert r.returncode == 0, r.stderr
    t = (tmp_path / "a5" / "frontline-learning-cards.cards.learner.html").read_text(encoding="utf-8")
    assert "@page{size:A5}" in t and R.LEARNER_BANNER in t


def test_layout_shared_copy(tmp_path):
    """A shared copy of a layout is built from the masked pack and workspace, under its own name (Review Focus 1)."""
    from test_privacy import share_ws, sign, write_doc
    sws, orgs = share_ws(tmp_path)
    doc = {"pack": "test-pack", "schema": 1, "title": "Test pack: synthetic pump fire", "audience": "Crews",
           "status": STATUS_PHRASE, "bottom_line": [{"text": "Test before service.", "cites": ["FND-0002"]}],
           "sections": [{"id": "s1", "heading": "Cards", "items": [
               {"kind": "card", "title": "Test the seal", "what_happened": "A seal from the supplier failed.",
                "warning_signs": ["No test record"], "good_looks_like": "A signed test record.",
                "cites": ["FND-0001"]}]}]}
    p = sign(sws, write_doc(tmp_path, doc), "--classification", "external", "--legal-review", "cleared")
    raw = json.dumps(json.loads((sws / "incident.json").read_text(encoding="utf-8")))
    assert "Bharat Seals" in raw                                  # the unmasked workspace names the organisation
    for layout in ("paper", "field"):
        out = tmp_path / layout
        r = _cli("pack", str(sws), str(p), "--share", "external", "--orgs", str(orgs), "--out", str(out),
                 "--layout", layout, "--base-url", BASE)
        assert r.returncode == 0, r.stderr
        got = sorted(x.name for x in out.iterdir())
        assert f"test-pack.{layout}.external.html" in got and f"test-pack.{layout}.html" not in got
        t = (out / f"test-pack.{layout}.external.html").read_text(encoding="utf-8")
        assert "Bharat Seals" not in t and DRAFT_LABEL not in t and STATUS_PHRASE in t
    t = (tmp_path / "paper" / "test-pack.paper.external.html").read_text(encoding="utf-8")
    assert "Shared external: identifying details are masked" in t
    assert "Synthetic pump fire · March 2024" in t                # the masked workspace: dates generalised


def test_layout_name_guard(std_ws, tmp_path, monkeypatch):
    """The name guard reads the layout's guard_text too: a leaking layout stops every output."""
    import argparse
    from pmlc_lib.pack import command
    monkeypatch.setattr(LY, "render_layout",
                        lambda ctx: [R.Output("x.cards.html", "<p>ok</p>", "printed for Quillon Vantress")])
    names = tmp_path / "names.txt"
    names.write_text("Quillon Vantress\n", encoding="utf-8")
    ns = argparse.Namespace(ws=str(std_ws), pack=str(FIX / "board-brief.json"), cmd="pack", share=None, embed=None,
                            out=str(tmp_path / "o"), no_md=False, names=str(names), orgs=None, format=["html"],
                            view="full", layout="cards", paper="A4", base_url=None)
    with pytest.raises(SystemExit) as e:
        command.cmd_pack(ns)
    assert "refused: a listed name appears in the output (1 times)" in str(e.value)
    assert not (tmp_path / "o").exists()


def test_base_url_reaches_the_context(std_ws, tmp_path, monkeypatch):
    """--base-url is wired into RenderContext.base_url before any format renders (Task 12's email reads it)."""
    seen = []
    R.register("test-seen", lambda ctx: seen.append((ctx.base_url, ctx.layout, ctx.paper)) or [], kind="data")
    try:
        import argparse
        from pmlc_lib.pack import command
        ns = argparse.Namespace(ws=str(std_ws), pack=str(FIX / "frontline-learning-cards.json"), cmd="pack",
                                share=None, embed=None, out=str(tmp_path / "o"), no_md=False, names=None, orgs=None,
                                format=["test-seen"], view="full", layout="cards", paper="A5", base_url=BASE)
        command.cmd_pack(ns)
    finally:
        R.FORMATS.pop("test-seen")
    assert seen == [(BASE, "cards", "A5")]
    r = _cli("pack", str(std_ws), str(FIX / "frontline-learning-cards.json"), "--out", str(tmp_path / "c"),
             "--layout", "cards", "--base-url", BASE)
    assert r.returncode == 0, r.stderr
    t = (tmp_path / "c" / "frontline-learning-cards.cards.html").read_text(encoding="utf-8")
    assert f'aria-label="QR code: {BASE}#i/' in t


@pytest.mark.skipif("docx" not in R.FORMATS, reason="the docx format (Task 10) is not registered in this base")
def test_paper_layout_with_docx_writes_the_board_paper(std_ws, tmp_path):
    """ctx.layout reaches the formats: --layout paper with docx also writes <pack>.paper.docx (P4-7, Task 10)."""
    out = tmp_path / "o"
    r = _cli("pack", str(std_ws), str(FIX / "board-brief.json"), "--out", str(out), "--layout", "paper",
             "--format", "docx")
    assert r.returncode == 0, r.stderr
    assert (out / "board-brief.paper.docx").is_file() and (out / "board-brief.paper.html").is_file()


# ----------------------------------------------------------------------------- printing

@pytest.fixture(scope="module")
def hz(tmp_path_factory):
    pytest.importorskip("openpyxl")
    from test_sample import EXPORT
    from test_pmlc import run
    root = tmp_path_factory.mktemp("hazira-layouts")
    run("ingest", str(EXPORT), "--slug", "hazira-gas-release-fire", "--root", str(root))
    ws_ = root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"
    run("classify", str(ws_), "--overlay", "india-process-site")
    return ws_


@pytest.mark.skipif(not R.find_browser(), reason="no Chromium-family browser")
def test_print_page_count_with_browser(hz, tmp_path):
    two = Path(__file__).resolve().parent / "fixtures" / "hazira" / "print-2-card.json"
    out = tmp_path / "o"
    r = _cli("pack", str(hz), str(two), "--out", str(out), "--layout", "cards", "--no-md")
    assert r.returncode == 0, r.stderr
    page = out / "frontline-learning-cards.cards.html"
    pdf = tmp_path / "cards.pdf"
    r = subprocess.run([R.find_browser(), "--headless", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf}", page.as_uri()], capture_output=True, text=True, timeout=120)
    assert pdf.exists(), r.stderr
    n = len(re.findall(rb"/Type\s*/Page(?![s\w])", pdf.read_bytes()))
    assert 1 <= n <= 3, n


def test_layouts_module_registered():
    from pmlc_lib import _compat
    assert "pmlc_lib.render.layouts" in _compat.MODULES
    assert LY.LAYOUTS == ("cards", "toolbox", "poster", "checklist", "paper", "field")
