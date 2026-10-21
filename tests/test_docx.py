"""Phase 4, Task 10: the docx renderer and the board-paper docx (L4-03, L4-20; Rulings P4-26, P4-7, P4-9, P4-20).
Synthetic fixtures only; invented names only."""
import argparse
import copy
import io
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pytest

from test_pmlc import PMLC, ws  # noqa: F401  (ws is a module-scoped fixture)
from test_pack import fixture, FIX, item, pack_fixtures, pack_with, render_fixture, RUN
import pmlc  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ooxml_check  # noqa: E402

from pmlc_lib import render as R  # noqa: E402
from pmlc_lib.render import docx as DX, labels as RL  # noqa: E402
from pmlc_lib.handling import effective_handling, share_ctx, shared_copy  # noqa: E402
from pmlc_lib.pack import schema as PS  # noqa: E402

W = ooxml_check.W
WT = f"{{{W}}}"
LABELS_FIX = Path(__file__).resolve().parent / "fixtures" / "labels"
EN = RL.load_labels("en")
# A 1x1 transparent PNG.
PNG_1X1 = bytes.fromhex("89504e470d0a1a0a0000000d4948445200000001000000010806000000"
                        "1f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082")


@pytest.fixture(scope="module")
def w(ws):  # noqa: F811
    return pmlc.load_ws(ws)


def one(outs, suffix=".docx"):
    hits = [o for o in outs if o.name.endswith(suffix)]
    assert len(hits) == 1, [o.name for o in outs]
    return hits[0]


def parts(data) -> dict:
    z = zipfile.ZipFile(io.BytesIO(data))
    return {n: z.read(n) for n in z.namelist()}


def xml(data, name="word/document.xml"):
    return parts(data)[name].decode("utf-8")


def paragraphs(data, name="word/document.xml"):
    """(style, text) of each body paragraph, in order."""
    root = ET.fromstring(parts(data)[name])
    out = []
    for p in root.iter(f"{WT}p"):
        st = p.find(f"{WT}pPr/{WT}pStyle")
        out.append((st.get(f"{WT}val") if st is not None else "", "".join(t.text or "" for t in p.iter(f"{WT}t"))))
    return out


def ctx_of(w, pack, **kw):
    kw.setdefault("eh", effective_handling(pack, w))
    return R.RenderContext(w=w, pack=PS.with_item_ids(pack), run=RUN, generated="2020-09-24", embed="cited", **kw)


def test_docx_registered():
    assert R.FORMATS["docx"].kind == "document"
    assert "docx" not in R.DEFAULT_FORMATS


@pytest.mark.parametrize("name", pack_fixtures() + ["all-kinds"])
def test_docx_every_fixture_valid(name):
    o = one(render_fixture(name, "docx"))
    assert o.name == f"{fixture(name)['pack']}.docx"
    assert ooxml_check.check_package(o.data) == []
    assert o.guard_text == DX.docx_text(o.data)
    text = o.guard_text
    assert pmlc.STATUS_PHRASE in text and pmlc.BRAND in text and pmlc.DRAFT_LABEL in text


def test_docx_status_under_title(w):
    data = one(R.render("docx", ctx_of(w, fixture("board-brief")))).data
    ps = paragraphs(data)
    i = next(n for n, (st, _) in enumerate(ps) if st == "Title")
    assert ps[i][1] == fixture("board-brief")["title"]
    assert pmlc.STATUS_PHRASE in ps[i + 1][1] and pmlc.AI_STATUS in ps[i + 1][1]
    assert ps[i + 2][1] == pmlc.DRAFT_LABEL
    assert ps[i + 3][1].startswith("Review: draft")
    styles = xml(data, "word/styles.xml")
    for st in ("Title", "Heading1", "Heading2", "Normal", "TableGrid", "Caption"):
        assert f'w:styleId="{st}"' in styles, st
    doc = xml(data)
    assert '<w:pgSz w:w="11906" w:h="16838"/>' in doc and 'w:top="1134"' in doc and 'w:left="1134"' in doc
    assert EN["ui.bottom_line"] in [t for st, t in ps if st == "Heading1"]


def test_docx_footer_every_page(w):
    data = one(R.render("docx", ctx_of(w, fixture("board-brief")))).data
    root = ET.fromstring(parts(data)["word/document.xml"])
    refs = [r for s in root.iter(f"{WT}sectPr") for r in s.findall(f"{WT}footerReference")]
    assert refs and all(r.get(f"{WT}type") == "default" for r in refs)
    footer = xml(data, "word/footer1.xml")
    assert pmlc.STATUS_PHRASE in footer and pmlc.BRAND in footer
    assert re.search(r'w:instr=" ?PAGE ?"', footer) or "PAGE" in re.sub(r"<[^>]+>", " ", footer)


def test_docx_draft_header(tmp_path, w):
    data = one(R.render("docx", ctx_of(w, fixture("board-brief")))).data
    assert pmlc.DRAFT_LABEL in xml(data, "word/header1.xml")
    root = ET.fromstring(parts(data)["word/document.xml"])
    assert [r.get(f"{WT}type") for r in root.iter(f"{WT}headerReference")] == ["default"]
    # An approved pack, made through the sign-off fixture path: no DRAFT anywhere.
    from test_handling import build, eh_of, PACK, signed
    okws = build(tmp_path, edited={"FND-0001": "Yes"})
    doc = signed(tmp_path, okws, PACK)
    eh = eh_of(tmp_path, okws, doc)
    assert eh["effective_status"] == "approved"
    out = one(R.render("docx", ctx_of(pmlc.load_ws(okws), doc, eh=eh)))
    assert ooxml_check.check_package(out.data) == []
    for n, b in parts(out.data).items():
        assert b"DRAFT" not in b, n
    assert pmlc.STATUS_PHRASE in out.guard_text and "Review: approved by HSE manager" in out.guard_text


def test_docx_tables_separated(w):
    data = one(R.render("docx", ctx_of(w, fixture("investigator-coach")))).data
    doc = xml(data)
    n = doc.count("</w:tbl>")
    assert n >= 2 and doc.count("</w:tbl><w:p/>") == n
    assert "<w:tblHeader/>" in doc
    t1 = item("table", columns=["Finding", "Note"], rows=[["FND-0002", "first"]], row_cites=[["FND-0002"]])
    t2 = item("table", columns=["Check", "Result"], rows=[["Seal", "ok"], ["Test", "missing"]])
    tp = item("test_point", requirement="Restarts are tested", clause="7.1", red_flags=["No record"])
    data = one(R.render("docx", ctx_of(w, pack_with(t1, t2, tp, t2)))).data
    doc = xml(data)
    assert doc.count("</w:tbl>") == 4 and doc.count("</w:tbl><w:p/>") == 4
    assert ooxml_check.check_package(data) == []
    root = ET.fromstring(parts(data)["word/document.xml"])
    grids = [t for t in root.iter(f"{WT}tbl") if len(t.findall(f"{WT}tblGrid/{WT}gridCol")) == 2]
    assert any("Restarts are tested" in "".join(x.text or "" for x in g.iter(f"{WT}t")) for g in grids)


def test_docx_endnotes_list_cited_labels(w):
    pack = fixture("board-brief")
    data = one(R.render("docx", ctx_of(w, pack))).data
    notes = xml(data, "word/endnotes.xml")
    fids, eids = PS.cited_ids(pack)
    F = {f["id"]: f for f in w["findings"]}
    for x in fids:
        f = F[x]
        assert f"{x}: {f['label']} · L{f['level']} · rating {f['rating']}" in DX.docx_text(data), x
    for x in eids:
        assert f"{x}: {w['evidence'][x]['type']}" in DX.docx_text(data), x
    doc = xml(data)
    refs = re.findall(r'<w:endnoteReference w:id="(\d+)"/>', doc)
    ids = set(re.findall(r'<w:endnote w:id="(\d+)"', notes))
    assert refs and set(refs) <= ids and len(refs) == len(set(refs))
    assert '<w:endnote w:type="separator" w:id="-1">' in notes
    assert "<w:endnotePr>" in xml(data, "word/settings.xml")


def test_docx_no_creator(w):
    data = one(R.render("docx", ctx_of(w, fixture("board-brief")))).data
    core = xml(data, "docProps/core.xml")
    assert "creator" not in core and "lastModifiedBy" not in core
    assert fixture("board-brief")["title"] in core


def test_docx_paper_layout(w):
    outs = render_fixture("board-brief", "docx", layout="paper")
    assert sorted(o.name for o in outs) == ["board-brief.docx", "board-brief.paper.docx"]
    paper = one(outs, ".paper.docx")
    assert ooxml_check.check_package(paper.data) == []
    ps = paragraphs(paper.data)
    heads = [(st, t) for st, t in ps if st.startswith("Heading")]
    assert heads[0] == ("Heading1", EN["ui.docx.decisions_requested"])
    names = [t for _, t in heads]
    assert EN["ui.docx.annex_a"] in names and EN["ui.docx.annex_b"] in names
    assert names.index(EN["ui.docx.annex_a"]) < names.index(EN["ui.docx.annex_b"])
    doc = xml(paper.data)
    cover_end = doc.index('<w:br w:type="page"/>')
    assert doc.index(fixture("board-brief")["title"]) < cover_end < doc.index(EN["ui.docx.decisions_requested"])
    texts = [t for _, t in ps]
    assert any(re.match(r"1\. ", t) for t in texts) and any(re.match(r"1\.1 ", t) for t in texts)
    q = next(it["question"] for s in fixture("board-brief")["sections"] for it in s["items"] if it["kind"] == "question")
    qi = next(i for i, t in enumerate(texts) if q in t)
    assert qi > texts.index(EN["ui.docx.annex_a"])
    # A decision item opens the paper, before the bottom line.
    p = pack_with(item("para", cites=["FND-0001"]), item("decision", decision="Fund a spares review",
                                                          cites=["FND-0003"]))
    paper = one(R.render("docx", ctx_of(w, p, layout="paper")), ".paper.docx")
    texts = [t for _, t in paragraphs(paper.data)]
    d = texts.index(EN["ui.docx.decisions_requested"])
    assert "Fund a spares review" in texts[d + 1] and texts.index("Test before service.") > d + 1
    # Other layouts leave the docx alone.
    assert [o.name for o in R.render("docx", ctx_of(w, p, layout="cards"))] == ["test-pack.docx"]


def test_docx_learner_view_hides_answers(w):
    pack = fixture("training-designer")
    answers = [it[f] for s in pack["sections"] for it in s["items"] for f in ("answer", "good_evidence") if f in it]
    assert answers
    full = one(R.render("docx", ctx_of(w, pack)))
    assert all(a in full.guard_text for a in answers)
    o = one(R.render("docx", ctx_of(w, pack, view="learner")))
    assert o.name == "training-designer.learner.docx"
    assert not [a for a in answers if a in o.guard_text]
    texts = [t for _, t in paragraphs(o.data)]
    i = next(n for n, t in enumerate(texts) if pmlc.STATUS_PHRASE in t)
    assert texts[i + 1] == R.LEARNER_BANNER
    paper = R.render("docx", ctx_of(w, pack, view="learner", layout="paper"))
    assert sorted(x.name for x in paper) == ["training-designer.learner.docx", "training-designer.paper.learner.docx"]


def test_docx_escaping_and_scripts(w, tmp_path):
    hostile = "Fitter & crew <said> \"stop\" 'now'\x0b हिंदी पाठ 🔥 done"
    p = pack_with(item("para", text=hostile, cites=["FND-0001"]),
                  item("table", columns=["A & B", "<C>"], rows=[[hostile, "x\x0by"]]),
                  title="Test & <pack> \"one\"")
    o = one(R.render("docx", ctx_of(w, p)))
    assert ooxml_check.check_package(o.data) == []
    clean = hostile.replace("\x0b", "")
    assert clean in o.guard_text and "A & B" in o.guard_text and "Test & <pack> \"one\"" in o.guard_text
    for n, b in parts(o.data).items():
        if n.endswith((".xml", ".rels")):
            ET.fromstring(b)
    path = tmp_path / "hostile.docx"
    path.write_bytes(o.data)
    if shutil.which("soffice"):
        assert ooxml_check.soffice_roundtrip(path) is True


def test_docx_rtl(w, monkeypatch):
    monkeypatch.setenv("PMLC_LABELS_DIR", str(LABELS_FIX))
    p = pack_with(item("para", cites=["FND-0001"]), lang="ar")
    o = one(R.render("docx", ctx_of(w, p)))
    assert ooxml_check.check_package(o.data) == []
    root = ET.fromstring(parts(o.data)["word/document.xml"])
    ps = [x for x in root.iter(f"{WT}p") if x.find(f"{WT}pPr") is not None]
    assert ps and all(x.find(f"{WT}pPr/{WT}bidi") is not None for x in ps)
    assert "الخلاصة" in o.guard_text                                  # the fixture's ui.bottom_line
    ltr = one(R.render("docx", ctx_of(w, pack_with(item("para", cites=["FND-0001"])))))
    assert "<w:bidi/>" not in xml(ltr.data)


def test_docx_shared_copy(tmp_path):
    from test_privacy import _cli, share_ws, sign, SPACK, write_doc
    ws_, orgs = share_ws(tmp_path)
    names = tmp_path / "names.txt"
    names.write_text("# staff\nFictional Person\n", encoding="utf-8")
    doc = copy.deepcopy(SPACK)
    doc["sections"][0]["items"][0].update(text="Fictional Person tested the seal.",
                                          lint_ok={"rule": "JC1", "reason": "test of the shared docx"})
    p = sign(ws_, write_doc(tmp_path, doc), "--classification", "external", "--legal-review", "cleared")
    out = tmp_path / "out"
    r = _cli("pack", str(ws_), str(p), "--share", "external", "--format", "docx", "--orgs", str(orgs),
             "--names", str(names), "--out", str(out))
    assert r.returncode == 0, r.stderr
    assert sorted(x.name for x in out.iterdir()) == ["test-pack.external.docx"]
    data = (out / "test-pack.external.docx").read_bytes()
    assert ooxml_check.check_package(data) == []
    text = DX.docx_text(data)
    assert "Fictional Person" not in text and "[name] tested the seal." in text
    for n, b in parts(data).items():
        assert b"Fictional Person" not in b and b"Bharat Seals" not in b, n
    assert "Shared external: identifying details are masked" in text
    # The same through a hand-built context: the masked pack and workspace.
    w_ = pmlc.load_ws(ws_)
    share = share_ctx(argparse.Namespace(names=str(names), orgs=str(orgs)), w_, "external")
    ctx = ctx_of(shared_copy(w_, share, w_), shared_copy(doc, share, w_), share=share,
                 eh=effective_handling(doc, w_))
    o = one(R.render("docx", ctx))
    assert "Fictional Person" not in o.guard_text and o.name == "test-pack.docx"


def test_docx_brand(w):
    brand = R.Brand("Fictional Works", "#1a5276", PNG_1X1, "image/png")
    o = one(R.render("docx", ctx_of(w, fixture("board-brief"), brand=brand)))
    assert ooxml_check.check_package(o.data) == []
    ps = parts(o.data)
    media = [n for n in ps if n.startswith("word/media/")]
    assert media and ps[media[0]] == PNG_1X1
    rels = ps["word/_rels/document.xml.rels"].decode()
    assert "relationships/image" in rels and media[0].split("word/", 1)[1] in rels
    assert "<a:blip" in xml(o.data) or "a:blip" in xml(o.data)
    styles = ps["word/styles.xml"].decode()
    h1 = styles.split('w:styleId="Heading1"', 1)[1].split("</w:style>", 1)[0]
    assert '<w:color w:val="1A5276"/>' in h1
    assert "Fictional Works" in o.guard_text
    plain = parts(one(R.render("docx", ctx_of(w, fixture("board-brief")))).data)
    assert not [n for n in plain if n.startswith("word/media/")]
    assert '<w:color w:val="1A5276"/>' not in plain["word/styles.xml"].decode()


def test_docx_text_order_and_parts(w):
    o = one(R.render("docx", ctx_of(w, fixture("all-kinds"))))
    t = o.guard_text
    assert t.index(pmlc.DRAFT_LABEL) < t.index(fixture("all-kinds")["title"]) < t.index(pmlc.BRAND)
    assert "Seal bought locally → Pump restarted untested (enabled)" in t      # graph: links as text
    assert "Local seal purchases begin" in t and "24 months before" in t      # timeline: a table
    assert DX.docx_text(b"not a zip") == ""


def test_docx_deterministic(w, monkeypatch):
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1600905600")
    a = one(R.render("docx", ctx_of(w, fixture("board-brief")))).data
    b = one(R.render("docx", ctx_of(w, fixture("board-brief")))).data
    assert a == b


def test_write_docx_blocks(w):
    ctx = ctx_of(w, fixture("board-brief"))
    blocks = [("title", "Register", []), ("status", "A status", []), ("heading1", "Entries", []),
              ("heading2", "Group", []), ("para", "Lesson one", ["FND-0001", "EVD-0001", "LR-01"]),
              ("list", ["a", "b"], ["FND-0002"]), ("list", {"items": ["x", "y"], "ordered": True}, []),
              ("table", {"columns": ["ID", "Lesson"], "rows": [["LR-01", "One"]]}, ["FND-0003"]),
              ("table", {"columns": ["ID"], "rows": [["LR-02"]]}, [])]
    data = DX.write_docx(blocks, ctx)
    assert ooxml_check.check_package(data) == []
    t = DX.docx_text(data)
    assert "LR-01" in t and "FND-0001:" in t
    doc = xml(data)
    assert doc.count("</w:tbl><w:p/>") == 2
    with pytest.raises(ValueError):
        DX.write_docx([("nope", "x", [])], ctx)


def test_docx_from_the_command(tmp_path, ws):  # noqa: F811
    out = tmp_path / "o"
    r = subprocess.run([sys.executable, str(PMLC), "pack", str(ws), str(FIX / "board-brief.json"), "--out", str(out),
                        "--format", "html,docx"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert sorted(x.name for x in out.iterdir()) == ["board-brief.docx", "board-brief.html"]
    assert "docx written to" in r.stdout


@pytest.mark.skipif(not shutil.which("soffice"), reason="soffice not installed")
def test_docx_soffice_roundtrip(tmp_path):
    for name, kw in (("board-brief", {}), ("all-kinds", {}), ("board-brief", {"layout": "paper"})):
        for o in render_fixture(name, "docx", **kw):
            p = tmp_path / o.name
            p.write_bytes(o.data)
            assert ooxml_check.soffice_roundtrip(p) is True, o.name


def test_docx_labels_in_both_locales():
    hi = json.loads((RL.LABELS_DIR / "hi.json").read_text(encoding="utf-8"))
    for k in [k for k in EN if k.startswith("ui.docx.")]:
        assert k in hi and hi[k] and hi[k] != EN[k], k


def test_docx_lang_from_pack(w, monkeypatch):
    """styles.xml names the pack's lang (en-GB without one); an rtl pack's lang is also the complex-script lang."""
    def lang_of(p):
        styles = parts(one(R.render("docx", ctx_of(w, p))).data)["word/styles.xml"].decode()
        return re.search(r"<w:lang [^>]*/>", styles).group(0)
    assert lang_of(pack_with(item("para"))) == '<w:lang w:val="en-GB"/>'
    assert lang_of(pack_with(item("para"), lang="hi")) == '<w:lang w:val="hi"/>'
    monkeypatch.setenv("PMLC_LABELS_DIR", str(LABELS_FIX))
    assert lang_of(pack_with(item("para"), lang="ar")) == '<w:lang w:val="ar" w:bidi="ar"/>'


def test_docx_logo_alt_from_label(w):
    brand = R.Brand("Fictional Works", "#1a5276", PNG_1X1, "image/png")
    hi = json.loads((RL.LABELS_DIR / "hi.json").read_text(encoding="utf-8"))
    for lang, alt in (("en", EN["ui.docx.logo_alt"]), ("hi", hi["ui.docx.logo_alt"])):
        p = dict(fixture("board-brief"), lang=lang)
        doc = xml(one(R.render("docx", ctx_of(w, p, brand=brand))).data)
        assert f'name="Logo" descr="{alt}"' in doc, lang
