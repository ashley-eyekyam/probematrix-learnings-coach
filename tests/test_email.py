"""Phase 4, Task 12: the email-safe digest and its plain-text twin (Ruling P4-24). Synthetic fixtures only."""
import argparse
import html as std_html
import json
import re
import sys
from pathlib import Path

import pytest

from test_pmlc import ws  # noqa: F401  (ws is a module-scoped fixture)
from test_pack import fixture, item, pack_fixtures, pack_with
from test_render import ctx_for
import pmlc  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pmlc_lib import render as R  # noqa: E402
from pmlc_lib.handling import SHARED_LINE, effective_handling, share_ctx, shared_copy  # noqa: E402
from pmlc_lib.render import labels as RL  # noqa: E402

NAMES = pack_fixtures() + ["all-kinds"]


@pytest.fixture(scope="module")
def w(ws):  # noqa: F811
    return pmlc.load_ws(ws)


def both(w, pack, **kw):
    outs = R.render("email", ctx_for(w, pack, **kw))
    assert [o.name.rsplit(".email.", 1)[1] for o in outs] == ["html", "txt"]
    return outs[0].data, outs[1].data


def plain(page: str) -> str:
    return " ".join(std_html.unescape(re.sub(r"<[^>]+>", " ", page)).split())


def big_pack(n=300):
    items = [item("para", text=("A long synthetic paragraph about pump seals and isolation. " * 8) + f"No. {i}",
                  cites=["FND-0002"]) for i in range(n)]
    p = pack_with(*items[:150])
    p["sections"].append({"id": "s2", "heading": "Section two", "items": [dict(x) for x in items[150:]]})
    return p


def stress_pack(sections=120, intro_words=400):
    intro = "A long introduction about isolation, seals and handover practice. " * (intro_words // 9)
    secs = [{"id": f"s{i}", "heading": f"Section number {i}", "intro": intro,
             "items": [item("para", text="Short synthetic point. " * 6, cites=["FND-0002"]) for _ in range(5)]}
            for i in range(sections)]
    return pack_with(item("para", text="x"), sections=secs)


def test_email_is_registered_as_a_document_format():
    assert R.FORMATS["email"].kind == "document"


@pytest.mark.parametrize("name", NAMES)
def test_email_no_script_style_link_img(w, name):
    page, _ = both(w, name)
    assert not re.search(r"<\s*(script|style|link|img)\b", page, re.I)
    assert not re.search(r"\sclass\s*=", page, re.I)
    assert "style=" in page
    assert "http" not in page                                 # no URL without --base-url
    for tag in re.findall(r"<(?:p|td|table|h[1-4]|a|ul|li|div|span|body)\b[^>]*>", page):
        assert "style=" in tag, tag


@pytest.mark.parametrize("name", NAMES + ["synthetic-300"])
def test_email_size_under_100k(w, name):
    pack = big_pack() if name == "synthetic-300" else name
    page, txt = both(w, pack)
    assert len(page.encode("utf-8")) < 100_000 and len(txt.encode("utf-8")) < 100_000
    if name == "synthetic-300":
        more = R.MORE_IN_PACK
        counts = [int(m) for m in re.findall(r"(\d+) more items are in the full pack", txt)]
        assert len(counts) == 2 and all(c > 0 for c in counts)          # one line per section
        assert more.format(n=counts[0]) in page
        assert sum(counts) < 300


@pytest.mark.parametrize("name", NAMES)
def test_email_txt_twin(w, name):
    page, txt = both(w, name)
    assert all(len(line) <= 78 for line in txt.splitlines()), max(txt.splitlines(), key=len)
    pack = ctx_for(w, name).pack
    flat, ptxt = " ".join(txt.split()), plain(page)
    for b in pack["bottom_line"]:
        t = " ".join(b["text"].split())
        assert t in flat and t in ptxt
    from pmlc_lib.handling import status_line
    for s in (status_line(pack["status"]), pmlc.BRAND, pack["title"]):
        assert " ".join(s.split()) in flat and " ".join(s.split()) in ptxt
    assert pmlc.DRAFT_LABEL in txt and pmlc.DRAFT_LABEL in page      # fixtures are drafts


def test_email_draft_and_status(w):
    pack = fixture("board-brief")
    eh = effective_handling(pack, w)
    page, txt = both(w, pack, eh=dict(eh, effective_status="approved"))
    assert pmlc.DRAFT_LABEL not in page and pmlc.DRAFT_LABEL not in txt
    assert pmlc.STATUS_PHRASE in page and pmlc.STATUS_PHRASE in txt
    page, txt = both(w, pack, eh=dict(eh, effective_status="draft"))
    assert pmlc.DRAFT_LABEL in page and pmlc.DRAFT_LABEL in txt


def test_email_base_url_link(w):
    url = "https://learn.example.org/pack/board-brief.html"
    page, txt = both(w, "board-brief", base_url=url)
    assert page.count("http") == 1 and page.count(f'href="{url}"') == 1
    assert txt.count(url) == 1 and txt.count("http") == 1
    assert RL.label(RL.load_labels("en"), "ui.email.full_pack") in page
    page, txt = both(w, "board-brief", base_url="javascript:alert(1)")        # not a web address: no link
    assert "javascript" not in page and "href" not in page and "javascript" not in txt


def test_email_base_url_is_escaped_or_refused(w):
    page, _ = both(w, "board-brief", base_url="https://learn.example.org/a?x=1&y=2")
    assert 'href="https://learn.example.org/a?x=1&amp;y=2"' in page
    ctx = ctx_for(w, "board-brief", base_url='https://learn.example.org/a?x="1"&y=<2>')
    page = R.render("email", ctx)[0].data
    assert "href" not in page and "<2>" not in page and "learn.example.org" not in page
    assert any("--base-url" in n for n in ctx.notes)


def test_email_shared_copy(w):
    pack = fixture("board-brief")
    share = share_ctx(argparse.Namespace(names=None, orgs=None), w, "external")
    ctx = ctx_for(shared_copy(w, share, w), shared_copy(pack, share, w), share=share, eh=effective_handling(pack, w))
    outs = R.render("email", ctx)
    for o in outs:
        assert SHARED_LINE.format(mode="external") in o.data
        assert ctx.run not in o.data and o.guard_text
    assert outs[0].guard_text == outs[1].data


def test_email_shows_the_brand_name_without_a_logo(w):
    """I2 (P4-16): with --brand the digest names the organisation right under the title, in the html and the txt,
    and never carries the logo; a shared copy shows the masked name."""
    from pmlc_lib.render.brand import shared_brand
    brand = R.Brand("Quorvel Process Ltd", "#1A7070", b"\x89PNG\r\n\x1a\nlogo", "image/png")
    page, txt = both(w, "board-brief", brand=brand)
    assert "Quorvel Process Ltd" in plain(page) and "Quorvel Process Ltd" in txt
    assert "<img" not in page and "base64" not in page
    title = fixture("board-brief")["title"]
    lines = [x for x in txt.splitlines() if x.strip()]
    assert lines[lines.index(next(x for x in lines if title in x)) + 1].strip() == "Quorvel Process Ltd"
    page, txt = both(w, "board-brief")                                       # no brand: no name line
    assert "Quorvel" not in page and "Quorvel" not in txt
    pack = fixture("board-brief")
    share = share_ctx(argparse.Namespace(names=None, orgs=None), w, "external")   # "... Ltd": a company-suffix name
    ctx = ctx_for(shared_copy(w, share, w), shared_copy(pack, share, w), share=share, eh=effective_handling(pack, w),
                  brand=shared_brand(brand, share))
    for o in R.render("email", ctx):
        assert "Quorvel" not in o.data and "[organisation]" in o.data and "<img" not in o.data


def test_email_learner_view_hides_answers(w):
    q = item("question", answer="SECRET-ANSWER", good_evidence="SECRET-EVIDENCE")
    page, txt = both(w, pack_with(q), view="learner")
    assert R.LEARNER_BANNER in page and R.LEARNER_BANNER in txt
    assert "SECRET" not in page and "SECRET" not in txt
    page, txt = both(w, pack_with(q))
    assert "SECRET-ANSWER" in page and "SECRET-ANSWER" in txt


def test_email_reading_time(w, tmp_path, monkeypatch):
    (tmp_path / "en.json").write_text(json.dumps({"ui.reading_time": "Reading: {n} minutes"}), encoding="utf-8")
    monkeypatch.setenv("PMLC_LABELS_DIR", str(tmp_path))
    n = R.fields.reading_minutes(fixture("board-brief"))
    page, txt = both(w, "board-brief", labels=RL.load_labels("en"))
    assert page.count(f"Reading: {n} minutes") == 1 and txt.count(f"Reading: {n} minutes") == 1
    monkeypatch.delenv("PMLC_LABELS_DIR")
    page, txt = both(w, "board-brief", labels=dict(RL.load_labels("en"), **{"ui.reading_time": "{n} min"}))
    assert f"{n} min" in page
    page, txt = both(w, "board-brief")                                       # the fixed copy until a label exists
    assert R.READING_TIME.format(n=n) in page and R.READING_TIME.format(n=n) in txt


def test_email_hostile_text_is_escaped_and_clean(w):
    p = pack_with(item("para", text='A & B <b>bold</b> "q" \x0b tab\there देवनागरी \U0001F600 [FND-0002]'))
    page, txt = both(w, p)
    assert "<b>" not in page and "&lt;b&gt;" in page and "\x0b" not in page and "\x0b" not in txt
    assert "देवनागरी" in page and "देवनागरी" in txt


def test_email_cited_ids_coverage_and_brand_close_the_digest(w):
    page, txt = both(w, "board-brief")
    pack = ctx_for(w, "board-brief").pack
    from pmlc_lib.pack.schema import cited_ids
    fids, eids = cited_ids(pack)
    for x in fids + eids:
        assert x in txt and x in page
    assert " ".join(txt.split()).endswith(pmlc.BRAND) and plain(page).endswith(pmlc.BRAND)
    assert "relevant findings" in txt and "top-rated" in txt


def test_email_every_item_kind_has_text(w):
    page, txt = both(w, "all-kinds")
    assert "<table" in page and "[FND-" in txt


def test_email_hindi_labels_exist():
    en, hi = RL.load_labels("en"), RL.load_labels("hi")
    for k in ("ui.email.cited", "ui.email.full_pack"):
        assert en[k] and hi[k] and hi[k] != en[k]


def test_email_stress_120_sections_long_intros_stays_under_100k(w):
    page, txt = both(w, stress_pack())
    assert len(page.encode("utf-8")) < 100_000
    assert page.count("Section number") == 120                                    # every heading still fits
    assert txt.count(R.MORE_IN_PACK.format(n=5)) >= 100                           # later sections: heading + line only


def test_email_headings_that_cannot_fit_end_in_one_line(w):
    page, txt = both(w, stress_pack(1500, 20))
    assert len(page.encode("utf-8")) < 100_000
    m = re.search(r"(\d+) more sections are in the full pack", txt)
    assert m and plain(page).count(m.group(0)) == 1
    assert page.count("Section number") + int(m.group(1)) == 1500
    assert "Section number 0" in page and R.MORE_IN_PACK.format(n=5) in page      # first sections keep a heading and a line


@pytest.mark.parametrize("sections,words", [(1, 20000), (3, 8000), (40, 900), (300, 30)])
def test_email_every_part_is_charged_to_the_budget(w, sections, words):
    page, _ = both(w, stress_pack(sections, words))
    assert len(page.encode("utf-8")) < 100_000


def test_email_txt_url_line_is_the_only_one_over_78(w):
    url = "https://learn.example.org/" + "a" * 100 + "/board-brief.html"
    _, txt = both(w, "board-brief", base_url=url)
    # a wrapped URL would be a broken link, so the URL line alone is exempt from the 78-column rule
    assert [x for x in txt.splitlines() if len(x) > 78] == [url]
