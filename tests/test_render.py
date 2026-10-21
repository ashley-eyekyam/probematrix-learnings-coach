"""Phase 4, Task 1: the render core: the format registry, --format, field roles, the normalised pack, the OOXML
helpers and the learner view (Rulings P4-1 to P4-6, P4-9, P4-22, P4-23, P4-28). Synthetic fixtures only."""
import argparse
import copy
import datetime as dt
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from test_pmlc import PMLC, ws  # noqa: F401  (ws is a module-scoped fixture)
from test_pack import FIX, GOLDEN_EPOCH, HTML_GOLDEN, RUN, fixture, item, pack_with
import pmlc  # noqa: E402
import pmlc_pack  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ooxml_check  # noqa: E402

from pmlc_lib import render as R  # noqa: E402
from pmlc_lib.render import fields as RF, labels as RL, ooxml as RO  # noqa: E402
from pmlc_lib.handling import effective_handling, share_ctx, shared_copy  # noqa: E402
from pmlc_lib.pack import schema as PS  # noqa: E402
from pmlc_lib.pack.markdown import coverage  # noqa: E402

NORMALISED_KEYS = {"normalised_version", "schema", "generator", "generated", "pack", "skill", "lang", "dir", "status",
                   "brand", "effective_status", "words", "reading_minutes", "coverage", "citations", "bottom_line",
                   "sections"}


@pytest.fixture(scope="module")
def w(ws):  # noqa: F811
    return pmlc.load_ws(ws)


@pytest.fixture()
def std_ws(ws, tmp_path):  # noqa: F811
    """A copy of the synthetic workspace in the standard layout, so the run slug is the golden's."""
    d = tmp_path / "pmlc-runs" / RUN / "workspace"
    shutil.copytree(ws, d)
    return d


def _cli(*args, epoch=True):
    env = dict(os.environ)
    if epoch:
        env["SOURCE_DATE_EPOCH"] = GOLDEN_EPOCH
    return subprocess.run([sys.executable, str(PMLC), *args], capture_output=True, text=True, env=env)


def ctx_for(w, name_or_pack, **kw):
    pack = fixture(name_or_pack) if isinstance(name_or_pack, str) else name_or_pack
    kw.setdefault("eh", effective_handling(pack, w))
    return R.RenderContext(w=w, pack=PS.with_item_ids(pack), run=RUN, generated="2020-09-24", embed="cited", **kw)


def test_default_formats_unchanged(std_ws, tmp_path):
    out = tmp_path / "o"
    r = _cli("pack", str(std_ws), str(FIX / "board-brief.json"), "--out", str(out))
    assert r.returncode == 0, r.stderr
    assert sorted(p.name for p in out.iterdir()) == ["board-brief.html", "board-brief.md"]
    golden = json.loads(HTML_GOLDEN.read_text(encoding="utf-8"))["board-brief"]
    assert hashlib.sha256((out / "board-brief.html").read_bytes()).hexdigest() == golden
    assert (out / "board-brief.md").read_text(encoding="utf-8") == (FIX / "board-brief.md").read_text(encoding="utf-8")
    assert "HTML written to" in r.stdout and "Markdown written to" in r.stdout


def test_format_list_and_unknown(std_ws, tmp_path):
    p = str(FIX / "board-brief.json")
    r = _cli("pack", str(std_ws), p, "--out", str(tmp_path / "a"), "--format", "html")
    assert r.returncode == 0, r.stderr
    assert sorted(x.name for x in (tmp_path / "a").iterdir()) == ["board-brief.html"]
    r = _cli("pack", str(std_ws), p, "--out", str(tmp_path / "b"), "--format", "nope")
    assert r.returncode == 2 and "nope" in r.stderr and "html" in r.stderr and "md" in r.stderr
    assert not (tmp_path / "b").exists()
    r = _cli("pack", str(std_ws), p, "--out", str(tmp_path / "c"), "--format", "html,md", "--no-md")
    assert r.returncode == 0, r.stderr
    assert sorted(x.name for x in (tmp_path / "c").iterdir()) == ["board-brief.html"]
    r = _cli("pack", str(std_ws), p, "--out", str(tmp_path / "d"), "--format", "normalised")
    assert r.returncode == 0, r.stderr
    assert sorted(x.name for x in (tmp_path / "d").iterdir()) == ["board-brief.normalised.json"]


def test_parse_formats():
    assert R.parse_formats("html, md,html") == ["html", "md"]
    for bad in ("", "nope", "html,,nope"):
        with pytest.raises(argparse.ArgumentTypeError) as e:
            R.parse_formats(bad)
        assert "html" in str(e.value) and "normalised" in str(e.value)
    assert list(R.FORMATS)[:3] == ["html", "md", "normalised"]
    assert R.FORMATS["normalised"].kind == "data" and R.FORMATS["html"].kind == "document"
    assert R.DEFAULT_FORMATS == ("html", "md")


def test_output_name():
    assert R.output_name("board-brief", "html") == "board-brief.html"
    assert R.output_name("board-brief", "email.html", view="learner") == "board-brief.learner.email.html"
    assert R.output_name("p", "html", layout="cards", view="learner", item_id="g1") == "p.g1.cards.learner.html"


def test_build_date(monkeypatch):
    monkeypatch.setenv("SOURCE_DATE_EPOCH", GOLDEN_EPOCH)
    assert R.build_date() == "2020-09-24"
    monkeypatch.delenv("SOURCE_DATE_EPOCH")
    assert R.build_date() == dt.date.today().isoformat()
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "not-a-number")
    assert R.build_date() == dt.date.today().isoformat()


def test_normalised_shape(w):
    pack = fixture("board-brief")
    outs = R.render("normalised", ctx_for(w, pack))
    assert [o.name for o in outs] == ["board-brief.normalised.json"]
    d = json.loads(outs[0].data)
    assert set(d) == NORMALISED_KEYS | {"run"} and d["run"] == RUN
    cov = coverage(w, pack)
    assert d["coverage"] == {k: cov[k] for k in ("cited", "relevant", "top_cited", "top_relevant")}
    assert pmlc.STATUS_PHRASE in d["status"] and d["brand"] == pmlc.BRAND and d["generator"] == pmlc.VERSION_STAMP
    assert d["normalised_version"] == 1 and d["schema"] == 1 and d["lang"] == "en" and d["dir"] == "ltr"
    assert all(it.get("id") for s in d["sections"] for it in s["items"])
    fids, eids = PS.cited_ids(pack)
    assert set(d["citations"]) == set(fids) | set(eids)
    f = next(x for x in w["findings"] if x["id"] == fids[0])
    assert d["citations"][fids[0]] == {"label": f.get("label"), "level": f.get("level"), "rating": f.get("rating")}
    assert d["words"] == RF.pack_words(pack) and d["reading_minutes"] == RF.reading_minutes(pack)
    assert d["effective_status"] == "draft" and outs[0].guard_text == outs[0].data
    share = share_ctx(argparse.Namespace(names=None, orgs=None), w, "external")
    ctx = ctx_for(shared_copy(w, share, w), shared_copy(pack, share, w), share=share, eh=effective_handling(pack, w))
    d2 = json.loads(R.render("normalised", ctx)[0].data)
    assert "run" not in d2 and set(d2) == NORMALISED_KEYS


def test_unknown_kind_degrades_to_field_list(w, monkeypatch, tmp_path):
    monkeypatch.setitem(PS.KINDS, "poll", {"req": ["prompt"], "opt": ["choices_text"],
                                           "fields": [["prompt", "body"], ["choices_text", "list"]]})
    (tmp_path / "en.json").write_text(json.dumps({"f.prompt": "Prompt", "f.choices_text": "Choices"}), encoding="utf-8")
    monkeypatch.setenv("PMLC_LABELS_DIR", str(tmp_path))
    poll = {"kind": "poll", "prompt": "Which check comes first? [FND-0001]", "choices_text": "Leak test; Restart"}
    p = pack_with(item("para", cites=["FND-0002"]), poll)
    assert pmlc_pack.check_pack(p, w).problems == []
    assert "FND-0001" in PS.cited_ids(p)[0]                       # body fields render citation buttons
    page = pmlc_pack.render_pack_html(w, p, RUN, "2020-09-24")
    assert '<dl class="fields">' in page and "<dt>Prompt</dt>" in page and "<dt>Choices</dt>" in page
    assert 'class="item k-poll"' in page and 'data-id="FND-0001"' in page
    md = pmlc_pack.render_pack_md(p, w)
    assert "**Prompt:** Which check comes first? [FND-0001]" in md and "**Choices:** Leak test; Restart" in md


def test_every_kind_has_fields_and_labels():
    en = json.loads((RL.LABELS_DIR / "en.json").read_text(encoding="utf-8"))
    assert en["_language"] == "English" and en["_dir"] == "ltr" and en["_review"] is None
    assert all(k.startswith(("_", "f.", "k.", "ui.")) for k in en)
    for kind, spec in PS.KINDS.items():
        named = [f for f, _ in spec["fields"]]
        assert set(named) >= set(spec["req"] + spec["opt"]) - set(PS.CITE_FIELDS), kind
        assert len(named) == len(set(named)), kind
        assert all(role in RF.ROLES for _, role in spec["fields"]), kind
        assert f"k.{kind}" in en, kind
        for f in named:
            assert f"f.{f}" in en, f
    assert RL.load_labels()["f.why"] == "Why it matters"
    assert RL.text_dir(RL.load_labels()) == "ltr"


def test_labels_loader(monkeypatch, tmp_path):
    (tmp_path / "xx.json").write_text(json.dumps({"_language": "Test", "_dir": "rtl", "f.why": "W"}), encoding="utf-8")
    monkeypatch.setenv("PMLC_LABELS_DIR", str(tmp_path))
    lb = RL.load_labels("xx")
    assert lb["f.why"] == "W" and lb["f.answer"] == "Answer" and RL.text_dir(lb) == "rtl"
    assert RL.load_labels("zz")["f.why"] == "Why it matters"            # no file: English
    with pytest.raises(KeyError):
        RL.label(lb, "f.nothing")
    assert RL.label({"x": "{n} items"}, "x", n=3) == "3 items"
    with pytest.raises(ValueError):
        RL.load_labels("../etc")


def test_item_blocks_and_text():
    lb = RL.load_labels()
    q = item("question", answer="A key", good_evidence="Records", to="Planner")
    blocks = RF.item_blocks(q, lb)
    assert [b.field for b in blocks] == ["question", "to", "why", "answer", "good_evidence"]
    assert blocks[0] == RF.Block("question", "title", "Question", "q")
    assert [b.field for b in RF.item_blocks(q, lb, view="learner")] == ["question", "to", "why"]
    assert RF.item_text(q) == "q" and RF.item_text({"kind": "table", "columns": ["a"], "rows": []}) == ""
    unknown = RF.item_blocks({"kind": "mystery", "id": "x", "cites": [], "note": "n", "steps": ["a"]}, lb)
    assert [(b.field, b.role, b.label) for b in unknown] == [("note", "body", "note"), ("steps", "list", "steps")]


def test_pack_words_and_reading_minutes():
    p = pack_with(item("para", text="one two three [FND-0001]", cites=["FND-0001"]),
                  item("recommendation", change="fit an interlock", indicator="restarts", hoc_tier="engineering"))
    # bottom line "Test before service." 3 + para 3 + change 3 + indicator 1; the ID, kind, cites and hoc_tier skipped
    assert RF.pack_words(p) == 10
    assert RF.reading_minutes(p) == 1
    big = pack_with(item("para", text=" ".join(["word"] * 401)))
    assert RF.reading_minutes(big) == 3


def test_skill_field_and_variants(w):
    def probs(**top):
        return pmlc_pack.check_pack(dict(fixture("report-comparison-client-safe"), **top), w).problems

    assert probs(skill="report-comparison") == []
    assert "skill: pack board-brief is not a pack or variant of skill report-comparison" in probs(
        skill="report-comparison", pack="board-brief")
    assert any("unknown skill nope" in x for x in probs(skill="nope"))
    d = fixture("dossier-F02")
    assert pmlc_pack.check_pack(dict(d, skill="cluster-learning-dossier", pack="dossier-index"), w).problems == []
    assert pmlc_pack.check_pack(dict(d, skill="cluster-learning-dossier"), w).problems == []
    assert PS.pack_fits_skill("dossier-F09b", "cluster-learning-dossier")
    assert not PS.pack_fits_skill("dossier-F09b", "board-brief")
    assert PS.pack_fits_skill("board-brief", "board-brief") and PS.pack_fits_skill("board-brief-short", "board-brief")
    assert not PS.pack_fits_skill("board-briefs", "board-brief")


def test_build_date_and_zip_determinism(monkeypatch):
    parts = {"word/document.xml": "<a/>", "[Content_Types].xml": "<Types/>", "_rels/.rels": b"<r/>"}
    monkeypatch.setenv("SOURCE_DATE_EPOCH", GOLDEN_EPOCH)
    one, two = RO.zip_bytes(parts), RO.zip_bytes(dict(reversed(list(parts.items()))))
    assert one == two
    z = zipfile.ZipFile(io.BytesIO(one))
    assert [i.filename for i in z.infolist()] == ["[Content_Types].xml", "_rels/.rels", "word/document.xml"]
    assert {i.date_time for i in z.infolist()} == {(2020, 9, 24, 0, 0, 0)}
    assert {i.compress_type for i in z.infolist()} == {zipfile.ZIP_DEFLATED}
    monkeypatch.delenv("SOURCE_DATE_EPOCH")
    z = zipfile.ZipFile(io.BytesIO(RO.zip_bytes(parts)))
    assert {i.date_time for i in z.infolist()} == {(1980, 1, 1, 0, 0, 0)}


def test_xml_text_strips_invalid():
    assert RO.xml_text("a\x0bb & <c>") == "ab &amp; &lt;c&gt;"
    s = "सुरक्षा पहले 🔥 ok"
    assert RO.xml_text(s) == s
    assert RO.xml_text(None) == "" and RO.xml_text('say "hi"\x00￾') == "say &quot;hi&quot;"


def test_ooxml_part_helpers():
    import xml.etree.ElementTree as ET
    core = RO.core_props("A & B", "2020-09-24")
    root = ET.fromstring(core)
    assert "creator" not in core and "lastModifiedBy" not in core and "A &amp; B" in core
    assert any(e.text == "2020-09-24T00:00:00Z" for e in root.iter())
    ET.fromstring(RO.app_props())
    ct = RO.content_types({"xml": "application/xml"}, {"word/document.xml": "x/y"})
    assert 'PartName="/word/document.xml"' in ct and 'Extension="xml"' in ct
    rl = RO.rels([("rId1", "officeDocument", "word/document.xml"), ("rId2", "http://x/t", "a.xml")])
    assert RO.REL_TYPES["officeDocument"] in rl and 'Type="http://x/t"' in rl and 'Id="rId1"' in rl


def _minimal_docx(**over):
    parts = {
        "[Content_Types].xml": RO.content_types(
            {"rels": "application/vnd.openxmlformats-package.relationships+xml", "xml": "application/xml"},
            {"word/document.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml",
             "word/footer1.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"}),
        "_rels/.rels": RO.rels([("rId1", "officeDocument", "word/document.xml")]),
        "word/_rels/document.xml.rels": RO.rels([("rId1", "footer", "footer1.xml")]),
        "word/footer1.xml": f'<w:ftr xmlns:w="{ooxml_check.W}"><w:p/></w:ftr>',
        "word/document.xml": (f'<w:document xmlns:w="{ooxml_check.W}" xmlns:r="{ooxml_check.R}"><w:body>'
                              '<w:tbl/><w:p/><w:tbl/><w:p/><w:sectPr><w:footerReference r:id="rId1"/></w:sectPr>'
                              '</w:body></w:document>'),
    }
    parts.update(over)
    return RO.zip_bytes(parts)


def test_ooxml_check_catches_problems(tmp_path):
    assert ooxml_check.check_package(_minimal_docx()) == []
    p = tmp_path / "ok.docx"
    p.write_bytes(_minimal_docx())
    assert ooxml_check.check_package(p) == []
    bad = _minimal_docx(**{
        "word/document.xml": (f'<w:document xmlns:w="{ooxml_check.W}" xmlns:r="{ooxml_check.R}"><w:body>'
                              '<w:tbl/><w:tbl/><w:sectPr><w:footerReference r:id="rId1"/></w:sectPr>'
                              '</w:body></w:document>'),
        "word/media/logo.png": b"\x89PNG"})
    probs = ooxml_check.check_package(bad)
    assert any("word/media/logo.png" in x and "content type" in x for x in probs), probs
    assert any("w:tbl" in x for x in probs), probs
    more = ooxml_check.check_package(_minimal_docx(**{
        "word/_rels/document.xml.rels": RO.rels([("rId1", "footer", "footer9.xml")]),
        "word/endnotes.xml": f'<w:endnotes xmlns:w="{ooxml_check.W}"><w:endnote w:id="1"/></w:endnotes>',
        "word/footer1.xml": "<not-closed>"}))
    assert any("footer9.xml" in x for x in more) and any("endnote" in x for x in more)
    assert any("word/footer1.xml" in x and "parse" in x for x in more), more
    nofoot = ooxml_check.check_package(_minimal_docx(**{
        "word/document.xml": f'<w:document xmlns:w="{ooxml_check.W}"><w:body><w:sectPr/></w:body></w:document>'}))
    assert any("footer" in x for x in nofoot)
    pptx = RO.zip_bytes({
        "[Content_Types].xml": RO.content_types({"xml": "application/xml",
                                                 "rels": "application/vnd.openxmlformats-package.relationships+xml"}, {}),
        "ppt/slides/slide1.xml": "<sld/>", "ppt/slides/_rels/slide1.xml.rels": RO.rels([])})
    assert any("slide1.xml" in x and "notes" in x for x in ooxml_check.check_package(pptx))
    assert ooxml_check.check_package(b"not a zip") == ["(package): not a zip file"]


@pytest.mark.skipif(not shutil.which("soffice"), reason="soffice not installed")
def test_soffice_roundtrip(tmp_path):
    p = tmp_path / "ok.docx"
    p.write_bytes(_minimal_docx())
    assert ooxml_check.soffice_roundtrip(p) is True


def test_cmd_pack_names_still_exported():
    from pmlc_lib.pack import command
    assert pmlc.cmd_pack is command.cmd_pack and pmlc_pack.cmd_pack is command.cmd_pack
    import test_split
    for module in ("pmlc", "pmlc_pack"):
        test_split.test_every_old_name_still_exported(module)


def test_learner_view_applied_centrally(w):
    pack = fixture("training-designer")
    answers = [it[f] for s in pack["sections"] for it in s["items"] for f in ("answer", "good_evidence") if f in it]
    assert answers
    outs = R.render("html", ctx_for(w, pack, view="learner"))
    assert [o.name for o in outs] == ["training-designer.learner.html"]
    assert not [a for a in answers if a in outs[0].data] and R.LEARNER_BANNER in outs[0].data
    md = R.render("md", ctx_for(w, pack, view="learner"))
    assert md[0].name == "training-designer.learner.md" and not [a for a in answers if a in md[0].data]
    assert R.LEARNER_BANNER in md[0].data
    d = R.render("normalised", ctx_for(w, pack, view="learner"))
    assert d[0].name == "training-designer.normalised.json" and all(a in d[0].data for a in answers)
    lv = RF.learner_view({"sections": [{"items": [{"kind": "question", "answer": "x", "good_evidence": "y",
                                                   "options": [{"text": "a", "correct": True}, "b"]}]}]})
    assert lv["sections"][0]["items"][0] == {"kind": "question", "options": [{"text": "a"}, "b"]}
    full = R.render("html", ctx_for(w, pack))
    assert full[0].name == "training-designer.html" and R.LEARNER_BANNER not in full[0].data


def test_learner_view_from_the_command(std_ws, tmp_path):
    r = _cli("pack", str(std_ws), str(FIX / "training-designer.json"), "--out", str(tmp_path / "o"), "--view", "learner")
    assert r.returncode == 0, r.stderr
    assert sorted(x.name for x in (tmp_path / "o").iterdir()) == ["training-designer.learner.html",
                                                                  "training-designer.learner.md"]


def test_render_nothing_to_write(w):
    calls = []

    def empty(ctx):
        ctx.notes.append(R.NOTHING_TO_WRITE.format(fmt="test-empty", why="no items"))
        calls.append(ctx.view)
        return []

    R.register("test-empty", empty, kind="data")
    try:
        ctx = ctx_for(w, "board-brief")
        assert R.render("test-empty", ctx) == [] and ctx.notes == ["test-empty: nothing to write (no items)"]
    finally:
        R.FORMATS.pop("test-empty")


def test_nothing_to_write_from_the_command(std_ws, tmp_path, monkeypatch, capsys):
    from pmlc_lib.pack import command
    R.register("test-empty", lambda ctx: ctx.notes.append(R.NOTHING_TO_WRITE.format(fmt="test-empty", why="x")) or [],
               kind="data")
    try:
        ns = argparse.Namespace(ws=str(std_ws), pack=str(FIX / "board-brief.json"), cmd="pack", share=None,
                                embed=None, out=str(tmp_path / "o"), no_md=False, names=None, orgs=None,
                                format=["test-empty"], view="full")
        command.cmd_pack(ns)
    finally:
        R.FORMATS.pop("test-empty")
    cap = capsys.readouterr()
    assert "test-empty: nothing to write (x)" in cap.err
    assert not (tmp_path / "o").exists() or not list((tmp_path / "o").iterdir())


def test_name_guard_covers_every_output(std_ws, tmp_path):
    """The guard reads every format's guard_text, not only the HTML and Markdown: one leaking output stops them all."""
    from pmlc_lib.pack import command
    names = tmp_path / "names.txt"
    names.write_text("Quillon Vantress\n", encoding="utf-8")
    R.register("test-leak", lambda ctx: [R.Output("x.leak.txt", b"bytes", "seen by Quillon Vantress")], kind="data")
    try:
        ns = argparse.Namespace(ws=str(std_ws), pack=str(FIX / "board-brief.json"), cmd="pack", share=None,
                                embed=None, out=str(tmp_path / "o"), no_md=False, names=str(names), orgs=None,
                                format=["html", "test-leak"], view="full")
        with pytest.raises(SystemExit) as e:
            command.cmd_pack(ns)
    finally:
        R.FORMATS.pop("test-leak")
    assert "refused: a listed name appears in the output (1 times)" in str(e.value)
    assert not (tmp_path / "o").exists()


def test_translation_lines():
    assert R.translation_lines({"translation_of": "board-brief"}) == [R.TRANSLATION_NOTE]
    assert R.translation_lines({"pack": "board-brief"}) == []


def test_find_browser_order(monkeypatch, tmp_path):
    stub = tmp_path / "my-browser"
    stub.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    stub.chmod(0o755)
    monkeypatch.setenv("PMLC_BROWSER", str(stub))
    assert R.find_browser() == str(stub)
    monkeypatch.delenv("PMLC_BROWSER")
    monkeypatch.setenv("PATH", "")
    assert R.find_browser() is None
    bindir = tmp_path / "bin"
    bindir.mkdir()
    for n in ("google-chrome", "chromium-browser"):
        shutil.copy(stub, bindir / n)
    monkeypatch.setenv("PATH", str(bindir))
    assert R.find_browser() == str(bindir / "chromium-browser")


def test_fixed_copy_constants():
    assert R.READING_TIME == "About {n} min read"
    assert R.TRANSLATION_NOTE == "Translated with AI assistance: have a fluent speaker check it before use"
    assert R.CHECK_LINE == "Checked by (role): ________   Date: ________   Shift: ________"
    assert R.NOTHING_TO_WRITE == "{fmt}: nothing to write ({why})"
    assert R.PNG_NO_BROWSER == ("png: no Chromium-family browser found; open the .svg in a browser and export it, "
                                "or set PMLC_BROWSER")
    assert R.ICS_NEEDS_START == ("ics: needs --start YYYY-MM-DD; nothing written (the coach never sets dates by "
                                 "itself)")
    assert R.MORE_IN_PACK == "{n} more items are in the full pack"
    assert R.LEARNER_BANNER == "Learner view: answers are hidden"


def test_skill_fixtures_carry_their_skill():
    for name, skill in (("dossier-F02", "cluster-learning-dossier"), ("organisation-learning-plan",
                                                                      "organisation-learning-map"),
                        ("report-comparison-client-safe", "report-comparison"),
                        ("report-comparison-regulator-safe", "report-comparison")):
        assert fixture(name)["skill"] == skill
    d = fixture("dossier-F02")
    assert "S3 Conditions (L2)" in [s["heading"] for s in d["sections"]]
    assert copy.deepcopy(d)["limits"]


def test_bytes_output_is_written(std_ws, tmp_path, capsys):
    from pmlc_lib.pack import command
    R.register("test-bytes", lambda ctx: [R.Output(R.output_name(ctx.pack["pack"], "bin"), b"\x00\x01", "")],
               kind="data")
    try:
        ns = argparse.Namespace(ws=str(std_ws), pack=str(FIX / "board-brief.json"), cmd="pack", share=None,
                                embed=None, out=str(tmp_path / "o"), no_md=True, names=None, orgs=None,
                                format=["test-bytes", "md"], view="full")
        command.cmd_pack(ns)
    finally:
        R.FORMATS.pop("test-bytes")
    assert (tmp_path / "o" / "board-brief.bin").read_bytes() == b"\x00\x01"
    assert sorted(p.name for p in (tmp_path / "o").iterdir()) == ["board-brief.bin"]
    assert "test-bytes written to" in capsys.readouterr().out


def test_normalised_file_is_not_a_pack_for_check_all(w, tmp_path):
    from pmlc_lib.orchestrate import _pack_files
    (tmp_path / "board-brief.json").write_text(json.dumps(fixture("board-brief")), encoding="utf-8")
    o = R.render("normalised", ctx_for(w, "board-brief"))[0]
    (tmp_path / o.name).write_text(o.data, encoding="utf-8")
    assert [p.name for p, _ in _pack_files(tmp_path)] == ["board-brief.json"]


def test_shared_names_put_the_mode_before_the_last_extension():
    """I1 (review): shared_name (the Phase 2 contract) inserts the mode before the last suffix, after output_name."""
    from pmlc_lib.handling import shared_name
    p = Path("out")
    assert shared_name(p / R.output_name("bb", "normalised.json"), "external").name == "bb.normalised.external.json"
    assert shared_name(p / R.output_name("bb", "html", view="learner"), "public").name == "bb.learner.public.html"
    text = (Path(__file__).resolve().parents[1] / "docs" / "manual" / "commands" / "pack.md").read_text(encoding="utf-8")
    assert "`<pack>.normalised.external.json`" in text and "`<pack>.learner.external.html`" in text
    assert "<pack>.external.normalised.json" not in text
