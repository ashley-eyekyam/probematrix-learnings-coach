"""The pptx renderer (L4-04, Rulings P4-25, P4-9, P4-20): a 16:9 deck with one slide master, one blank layout and
one theme; a footer on every slide; citations and full text in the notes; graphs as native DrawingML shapes."""
import io
import json
import re
import shutil
import struct
import zipfile
import zlib
from pathlib import Path

import pytest

from test_pmlc import ws  # noqa: F401  (ws is a module-scoped fixture)
from test_pack import FIX, fixture, item, pack_fixtures, pack_with, render_fixture
from test_render import ctx_for, std_ws, _cli  # noqa: F401  (std_ws is a fixture)
import pmlc  # noqa: E402

import ooxml_check  # noqa: E402

from pmlc_lib import BRAND, DRAFT_LABEL, privacy, STATUS_PHRASE, VERSION_STAMP  # noqa: E402
from pmlc_lib import render as R  # noqa: E402
from pmlc_lib.handling import effective_handling, shared_copy, status_line  # noqa: E402
from pmlc_lib.pack.schema import ID_RX, TOP_PRINT_LINE, with_item_ids  # noqa: E402
from pmlc_lib.render.pptx import pptx_notes_text, pptx_slides_text  # noqa: E402

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
LABELS_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "labels"


@pytest.fixture(scope="module")
def w(ws):  # noqa: F811
    return pmlc.load_ws(ws)


def one(outs):
    assert len(outs) == 1, [o.name for o in outs]
    return outs[0]


def parts(data: bytes) -> dict:
    z = zipfile.ZipFile(io.BytesIO(data))
    return {n: z.read(n) for n in z.namelist()}


def slide_xml(data: bytes) -> list:
    ps = parts(data)
    names = sorted((n for n in ps if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
                   key=lambda n: int(re.search(r"(\d+)\.xml$", n).group(1)))
    return [ps[n].decode("utf-8") for n in names]


def png_1x1() -> bytes:
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(b"\x00\x00\x77\xb6")) + chunk(b"IEND", b""))


def no_cites(s: str) -> str:
    return re.sub(r"\s*\[[^\]]*\]", "", s)


def test_pptx_is_registered():
    assert R.FORMATS["pptx"].kind == "document"


@pytest.mark.parametrize("name", pack_fixtures() + ["all-kinds"])
def test_pptx_every_fixture_valid(name):
    o = one(render_fixture(name, "pptx"))
    assert o.name == f"{fixture(name)['pack']}.pptx" and isinstance(o.data, bytes)
    assert ooxml_check.check_package(o.data) == []
    slides, notes = pptx_slides_text(o.data), pptx_notes_text(o.data)
    assert len(slides) == len(notes) >= 3
    pres = parts(o.data)["ppt/presentation.xml"].decode("utf-8")
    assert '<p:sldSz cx="12192000" cy="6858000"' in pres
    ps = parts(o.data)
    assert len([n for n in ps if n.startswith("ppt/slideMasters/slideMaster")]) == 1
    assert len([n for n in ps if re.fullmatch(r"ppt/slideLayouts/slideLayout\d+\.xml", n)]) == 1
    assert all(t in o.guard_text for t in slides + notes)
    core = ps["docProps/core.xml"].decode("utf-8")
    assert "creator" not in core and "lastModifiedBy" not in core


def test_pptx_slide_order():
    pack = fixture("board-brief")
    o = one(render_fixture("board-brief", "pptx"))
    slides = pptx_slides_text(o.data)
    assert pack["title"] in slides[0] and status_line(pack["status"]) in slides[0]
    assert pack["audience"] in slides[0]
    bl = pack["bottom_line"]
    for i, b in enumerate(bl, 1):
        assert no_cites(b["text"]) in slides[i]
    qs = [it for s in pack["sections"] for it in s["items"] if it["kind"] == "question"]
    assert len(qs) == 2
    for k, q in enumerate(qs, 1 + len(bl)):
        assert no_cites(q["question"]) in slides[k]
    others = [s for s in pack["sections"] if any(it["kind"] != "question" for it in s["items"])]
    assert len(slides) == 1 + len(bl) + len(qs) + len(others) + 1
    for k, s in enumerate(others, 1 + len(bl) + len(qs)):
        assert s["heading"] in slides[k]
    assert "This pack cites" in slides[-1] and TOP_PRINT_LINE.split("{")[0] in slides[-1]
    assert STATUS_PHRASE in slides[-1] and BRAND in slides[-1]


def test_pptx_footer_every_slide(w):
    for name in ("board-brief", "causal-map", "all-kinds"):
        slides = pptx_slides_text(one(render_fixture(name, "pptx")).data)
        for s in slides:
            assert STATUS_PHRASE in s and VERSION_STAMP in s and BRAND in s and DRAFT_LABEL in s, name
    pack = fixture("board-brief")
    eh = dict(effective_handling(pack, w), effective_status="approved", draft_reasons=[])
    data = one(render_fixture("board-brief", "pptx", w=w, eh=eh)).data
    for s in pptx_slides_text(data):
        assert STATUS_PHRASE in s and VERSION_STAMP in s and DRAFT_LABEL not in s
    assert not [x for x in slide_xml(data) if 'name="Draft' in x]


def test_pptx_citations_in_notes():
    for name in ("board-brief", "all-kinds", "dossier-F02"):
        pack = with_item_ids(fixture(name))
        o = one(render_fixture(name, "pptx"))
        slides, notes = pptx_slides_text(o.data), pptx_notes_text(o.data)
        assert not [s for s in slides if ID_RX.search(s)], name
        allnotes = "\n".join(notes)
        for i, b in enumerate(pack["bottom_line"], 1):
            for x in ID_RX.findall(json.dumps(b)):
                assert x in notes[i], (name, x)
        for s in pack["sections"]:
            for it in s["items"]:
                for x in ID_RX.findall(json.dumps(it)):
                    assert x in allnotes, (name, x)
    # each question's cites sit in that question's own notes (board-brief: slides 4 and 5)
    pack = fixture("board-brief")
    notes = pptx_notes_text(one(render_fixture("board-brief", "pptx")).data)
    qs = [it for s in pack["sections"] for it in s["items"] if it["kind"] == "question"]
    for k, q in enumerate(qs, 3):
        assert no_cites(q["question"]) in notes[k]
        for x in ID_RX.findall(json.dumps(q)):
            assert x in notes[k]


def test_pptx_cited_findings_listed_with_labels(w):
    o = one(R.render("pptx", ctx_for(w, "board-brief")))
    notes = "\n".join(pptx_notes_text(o.data))
    F = {f["id"]: f for f in w["findings"]}
    assert f"FND-0001: {F['FND-0001']['label']}" in notes


def test_pptx_continued_slides(w):
    items = [item("para", text=f"Point number {i} about the seal change.", cites=["FND-0001"]) for i in range(1, 15)]
    o = one(R.render("pptx", ctx_for(w, pack_with(*items))))
    slides = pptx_slides_text(o.data)
    sec = [s for s in slides if "Section one" in s]
    assert len(sec) == 3
    assert "(continued)" not in sec[0] and all("Section one (continued)" in s for s in sec[1:])
    assert [sum(f"Point number {i} " in s for i in range(1, 15)) for s in sec] == [6, 6, 2]


def test_pptx_graph_native_shapes():
    pack = fixture("causal-map")
    g = pack["sections"][0]["items"][0]
    o = one(render_fixture("causal-map", "pptx"))
    xs = [x for x in slide_xml(o.data) if 'prst="roundRect"' in x]
    assert len(xs) == 1
    x = xs[0]
    nodes = re.findall(r'<p:sp>(?:(?!</p:sp>).)*?prst="roundRect"(?:(?!</p:sp>).)*?</p:sp>', x, re.S)
    assert len(nodes) == len(g["nodes"])
    texts = sorted("".join(re.findall(r"<a:t>([^<]*)</a:t>", n)) for n in nodes)
    assert texts == sorted(n["label"] for n in g["nodes"])
    assert max(len(t) for t in texts) > 28                                  # longer than the SVG's clip
    assert x.count("<p:cxnSp>") == len(g["edges"])
    assert x.count('prst="straightConnector1"') == len(g["edges"])
    # every shape lies inside the slide
    boxes = re.findall(r'<a:off x="(-?\d+)" y="(-?\d+)"/><a:ext cx="(\d+)" cy="(\d+)"/>', x)
    assert len(boxes) >= len(g["nodes"]) + len(g["edges"])
    for a, b, c, d in ((int(v) for v in t) for t in boxes):
        assert 0 <= a and a + c <= 12192000 and 0 <= b and b + d <= 6858000
    notes = pptx_notes_text(o.data)
    gn = [n for n in notes if "2 mentions" in n]
    assert gn and "L4 OR 2.2 Spares Programme Failure → L1 AB 1.1 Step Omitted" in gn[0]


def test_pptx_graph_back_edge_and_omitted(w):
    nodes = [{"id": f"N{i}", "label": f"Node {i}"} for i in range(1, 5)]
    edges = [{"from": "N1", "to": "N2"}, {"from": "N2", "to": "N3"}, {"from": "N3", "to": "N1"},
             {"from": "N1", "to": "N3"}, {"from": "N3", "to": "N4", "label": "leads to"}]
    g = item("graph", nodes=nodes, edges=edges, cites=["FND-0001"])
    o = one(R.render("pptx", ctx_for(w, pack_with(g))))
    assert ooxml_check.check_package(o.data) == []
    x = [s for s in slide_xml(o.data) if 'prst="roundRect"' in s][0]
    assert x.count("<p:cxnSp>") == 5 and x.count('<a:prstDash val="dash"/>') == 1        # N3 -> N1 goes back
    assert x.count("<a:stCxn ") == 5 and x.count("<a:endCxn ") == 5                       # glued to the nodes
    from pmlc_lib.render import pptx as PX
    many = [{"id": f"M{i}", "label": f"Many {i}"} for i in range(70)]
    g2 = item("graph", nodes=many, edges=[{"from": "M0", "to": f"M{i}"} for i in range(1, 70)], cites=["FND-0001"])
    o2 = one(R.render("pptx", ctx_for(w, pack_with(g2))))
    x2 = [s for s in slide_xml(o2.data) if 'prst="roundRect"' in s][0]
    assert x2.count('prst="roundRect"') == 60
    assert "10 nodes with the fewest links are not drawn" in "\n".join(pptx_notes_text(o2.data))
    assert PX.PX_SLIDE_W == 12192000


def test_pptx_learner_view(w):
    pack = fixture("training-designer")
    answers = [it[f] for s in pack["sections"] for it in s["items"] for f in ("answer", "good_evidence") if f in it]
    assert answers
    full = one(R.render("pptx", ctx_for(w, pack)))
    assert full.name == "training-designer.pptx"
    fulltext = "\n".join(pptx_slides_text(full.data) + pptx_notes_text(full.data))
    assert all(no_cites(a) in fulltext for a in answers) and R.LEARNER_BANNER not in fulltext
    o = one(R.render("pptx", ctx_for(w, pack, view="learner")))
    assert o.name == "training-designer.learner.pptx"
    blob = b"".join(parts(o.data).values()).decode("utf-8", "replace")
    assert not [a for a in answers if no_cites(a) in blob]
    assert R.LEARNER_BANNER in pptx_slides_text(o.data)[0]
    assert ooxml_check.check_package(o.data) == []


HOSTILE = "Ampersand & <tag> \"quoted\" 'single' \x0bvertical तेल रिसाव 🔥 fire"


def test_pptx_escaping_and_scripts(w, tmp_path):
    p = pack_with(item("para", text=HOSTILE, cites=["FND-0001"]),
                  item("question", question=HOSTILE, why=HOSTILE, cites=["FND-0001"]),
                  title="Title & <b>bold</b> \x0b तेल 🔥", audience="Crew \"A\" & 'B'")
    o = one(R.render("pptx", ctx_for(w, p)))
    assert ooxml_check.check_package(o.data) == []
    clean = HOSTILE.replace("\x0b", "")
    slides = pptx_slides_text(o.data)
    assert "Title & <b>bold</b>  तेल 🔥" in slides[0] and "Crew \"A\" & 'B'" in slides[0]
    assert any(clean in s for s in slides[1:])
    assert "\x0b" not in o.guard_text
    if shutil.which("soffice"):
        f = tmp_path / "hostile.pptx"
        f.write_bytes(o.data)
        assert ooxml_check.soffice_roundtrip(f) is True


def test_pptx_rtl(w, monkeypatch):
    monkeypatch.setenv("PMLC_LABELS_DIR", str(LABELS_FIXTURES))
    p = dict(fixture("board-brief"), lang="ar")
    o = one(R.render("pptx", ctx_for(w, p)))
    assert ooxml_check.check_package(o.data) == []
    for x in slide_xml(o.data):
        assert 'rtl="1"' in x
        assert not re.search(r"<a:pPr(?![^>]*rtl=\"1\")[^>]*>", x)       # every paragraph is right to left
    text = "\n".join(pptx_slides_text(o.data))
    assert "الخلاصة 1/2" in text and "التغطية" in text
    assert 'lang="ar"' in slide_xml(o.data)[0]
    en = one(R.render("pptx", ctx_for(w, "board-brief")))
    assert not [x for x in slide_xml(en.data) if 'rtl="1"' in x]
    lt = one(R.render("pptx", ctx_for(w, dict(fixture("board-brief"), lang="ar", dir="ltr"))))
    assert not [x for x in slide_xml(lt.data) if 'rtl="1"' in x]


def test_pptx_shared_copy(w, tmp_path):
    share = privacy.ShareCtx("external", ["Quillon Vantress"], ["Ostrava Pumpworks"], {})
    pack = pack_with(item("para", text="Quillon Vantress of Ostrava Pumpworks restarted the pump.", cites=["FND-0001"]))
    rw, rpack = shared_copy(w, share, w), shared_copy(pack, share, w)
    ctx = ctx_for(rw, rpack, share=share, eh=effective_handling(pack, w))
    o = one(R.render("pptx", ctx))
    blob = b"".join(parts(o.data).values()).decode("utf-8", "replace")
    for x in ("Quillon", "Vantress", "Ostrava"):
        assert x not in blob and x not in o.guard_text
    slides = pptx_slides_text(o.data)
    assert "[name]" in "\n".join(slides) and "Shared external: identifying details are masked" in slides[0]
    # from the command: only the .external.pptx is written, from the masked pack
    from test_privacy import ORGS, share_ws, sign, SPACK, write_doc
    sws, orgs = share_ws(tmp_path)
    p = sign(sws, write_doc(tmp_path, SPACK), "--classification", "external", "--legal-review", "cleared")
    names = tmp_path / "names.txt"
    names.write_text("Quillon Vantress\n", encoding="utf-8")
    out = tmp_path / "out"
    r = _cli("pack", str(sws), str(p), "--share", "external", "--orgs", str(orgs), "--names", str(names),
             "--format", "pptx", "--out", str(out))
    assert r.returncode == 0, r.stderr
    assert sorted(x.name for x in out.iterdir()) == ["test-pack.external.pptx"]
    data = (out / "test-pack.external.pptx").read_bytes()
    assert ooxml_check.check_package(data) == []
    blob = b"".join(parts(data).values()).decode("utf-8", "replace")
    assert not [x for x in ORGS if x in blob] and "Quillon" not in blob
    assert "pptx written to" in r.stdout


def test_pptx_brand(w):
    brand = R.Brand("Ostrava Learning Trust", "#1A5276", png_1x1(), "image/png")
    o = one(R.render("pptx", ctx_for(w, "board-brief", brand=brand)))
    assert ooxml_check.check_package(o.data) == []
    ps = parts(o.data)
    assert ps["ppt/media/image1.png"] == png_1x1()
    rels = ps["ppt/slides/_rels/slide1.xml.rels"].decode("utf-8")
    assert "/relationships/image" in rels and "../media/image1.png" in rels
    x = slide_xml(o.data)[0]
    assert "<p:pic>" in x and 'r:embed="' in x and 'val="1A5276"' in x
    assert "Ostrava Learning Trust" in pptx_slides_text(o.data)[0]
    jpg = R.Brand(None, None, b"\xff\xd8\xff\xe0fakejpeg", "image/jpeg")
    o2 = one(R.render("pptx", ctx_for(w, "board-brief", brand=jpg)))
    assert ooxml_check.check_package(o2.data) == [] and "ppt/media/image1.jpeg" in parts(o2.data)
    plain = one(R.render("pptx", ctx_for(w, "board-brief")))
    assert not [n for n in parts(plain.data) if n.startswith("ppt/media/")]
    assert 'val="0077B6"' in slide_xml(plain.data)[0]


def test_pptx_old_and_odd_packs(w):
    from test_pack import alpha4_copy
    empty = pack_with()
    odd = pack_with(item("para", text="Known."), {"kind": "mystery", "text": "An unknown kind.", "extra": ["a", "b"]})
    for p in (alpha4_copy(fixture("board-brief")), empty, odd, pack_with(item("para", text="One."))):
        o = one(R.render("pptx", ctx_for(w, p)))
        assert ooxml_check.check_package(o.data) == []
    slides = pptx_slides_text(one(R.render("pptx", ctx_for(w, odd))).data)
    assert any("An unknown kind." in s for s in slides)


def test_pptx_deterministic(w, monkeypatch):
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1600905600")
    a = one(R.render("pptx", ctx_for(w, "causal-map"))).data
    b = one(R.render("pptx", ctx_for(w, "causal-map"))).data
    assert a == b


def test_pptx_from_the_command(std_ws, tmp_path):  # noqa: F811
    r = _cli("pack", str(std_ws), str(FIX / "board-brief.json"), "--format", "pptx", "--out", str(tmp_path / "o"))
    assert r.returncode == 0, r.stderr
    assert [x.name for x in (tmp_path / "o").iterdir()] == ["board-brief.pptx"]
    assert "pptx written to" in r.stdout


@pytest.mark.skipif(not shutil.which("soffice"), reason="soffice not installed")
def test_pptx_soffice_roundtrip(tmp_path):
    for name in ("board-brief", "causal-map"):
        f = tmp_path / f"{name}.pptx"
        f.write_bytes(one(render_fixture(name, "pptx")).data)
        assert ooxml_check.soffice_roundtrip(f) is True, name
