"""Output conformance across every skill and every format (Phase 4, Task 23; L4-27, spec 9.1, Ruling P4-20).

Document formats carry STATUS_PHRASE and BRAND, and DRAFT_LABEL exactly when the pack is not approved, read where a
person reads them: each docx footer (DRAFT in the header), every pptx slide, every xlsx sheet's header or footer and
every printed page of a layout. Data formats carry the status and the brand in their native comment or metadata slot;
the exempt ones are P4-20's, each with its reason. Every fixture (and its alpha.4 copy) renders in every registered
format, so a format added later (SCORM, Task 21) is covered once it registers itself."""
import contextlib
import copy
import dataclasses
import datetime as dt
import html
import io
import json
import re
import shutil
import struct
import subprocess
import sys
import zipfile
import zlib

import pytest

from test_pmlc import MINI_REG, PMLC, make_export, run
from test_pack import alpha4_copy, fixture, pack_fixtures, RUN
import ooxml_check
import pmlc  # noqa: E402  (test_pmlc put the engine folder on sys.path)
from pmlc_lib import BRAND, DRAFT_LABEL, STATUS_PHRASE  # noqa: E402
from pmlc_lib import render as R  # noqa: E402
from pmlc_lib import strings as ST  # noqa: E402
from pmlc_lib.handling import effective_handling  # noqa: E402
from pmlc_lib.pack.schema import with_item_ids  # noqa: E402
from pmlc_lib.render.layouts import LAYOUTS, render_layout  # noqa: E402

openpyxl = pytest.importorskip("openpyxl")

FIXTURES = pack_fixtures() + ["all-kinds"]
STATES = ("draft", "approved")
START = dt.date(2026, 11, 2)                      # an explicit --start, so ics has something to write (P4-20 slot)
DRAFT_RX = re.compile(rf"\b{DRAFT_LABEL}\b")
DOC_FORMATS = [n for n, f in R.FORMATS.items() if f.kind == "document"]
DATA_FORMATS = [n for n, f in R.FORMATS.items() if f.kind == "data"]
DOC_TARGETS = ([f"format:{n}" for n in DOC_FORMATS] + [f"layout:{x}" for x in LAYOUTS]
               + (["paper:docx"] if "docx" in DOC_FORMATS else []))        # docx with --layout paper: the board paper
DOC_TARGETS += [f"{t}:learner" for t in DOC_TARGETS]                         # the learner views (P4-9)
REGISTER_TARGETS = ("register-render:docx", "register-render:email", "register-xlsx", "pack-xlsx:test_point",
                    "pack-xlsx:question")

# P4-20: data formats with no status slot, and why. follow-up.csv is no format: investigator-coach writes it beside
# follow-up.json.
IMPORT_CLEAN = "import files must stay clean: a status row would be imported as data"
ON_AIR = ("the status would be shown on screen or spoken aloud; the shooting script in html, md and docx carries the "
          "status for them")
EXEMPT = {"csv": IMPORT_CLEAN, "quiz-csv": IMPORT_CLEAN, "bowtie-csv": IMPORT_CLEAN, "follow-up.csv": IMPORT_CLEAN,
          "srt": ON_AIR, "narration": ON_AIR}
NAMES = ("Fictional Person", "Tarvo Quillane")    # invented names for the shared-copy test


# ----------------------------------------------------------------------------- reading the outputs

def _norm(s) -> str:
    return " ".join(html.unescape(str(s)).split())


def _visible(page: str) -> str:
    """The text a person sees on an HTML page: no script, style or tags."""
    page = re.sub(r"<(script|style)\b.*?</\1>", " ", page, flags=re.S | re.I)
    return _norm(re.sub(r"<[^>]+>", " ", page))


def _runs(xml: bytes, tag: str, sep: str) -> str:
    return _norm(sep.join(re.findall(rf"<{tag}(?: [^>]*)?>([^<]*)</{tag}>", xml.decode("utf-8"))))


def _slots(name: str, data) -> dict:
    """{"status": [...], "brand": [...], "draft": [...]}: each status and brand slot must hold STATUS_PHRASE and BRAND;
    each draft slot holds DRAFT exactly when the pack is a draft. P4-20 says where each format keeps them."""
    if name.endswith((".docx", ".pptx", ".zip")):
        z = zipfile.ZipFile(io.BytesIO(data))
        parts = {n: z.read(n) for n in z.namelist()}
        if name.endswith(".docx"):                                     # the footer part; DRAFT in the header
            foot = [_runs(b, "w:t", "") for n, b in sorted(parts.items()) if re.fullmatch(r"word/footer\d*\.xml", n)]
            head = " ".join(_runs(b, "w:t", "") for n, b in sorted(parts.items())
                            if re.fullmatch(r"word/header\d*\.xml", n))
            return {"status": foot, "brand": foot, "draft": [head]}
        if name.endswith(".pptx"):                                     # on every slide
            slides = [_runs(b, "a:t", " ") for n, b in sorted(parts.items()) if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]
            return {"status": slides, "brand": slides, "draft": slides}
        out = {"status": [], "brand": [], "draft": []}                 # any other zip: each HTML page in it (SCORM)
        for n, b in sorted(parts.items()):
            if n.endswith(".html"):
                for k, v in _slots(n, b.decode("utf-8")).items():
                    out[k] += v
        assert out["status"], f"{name}: no HTML page in the package"
        return out
    if name.endswith(".xlsx"):                                         # every sheet's header or footer
        wb = openpyxl.load_workbook(io.BytesIO(data))
        hf = [_norm(" ".join(p.text or "" for hf in (s.oddHeader, s.oddFooter) for p in (hf.left, hf.center, hf.right)))
              for s in wb.worksheets]
        return {"status": hf, "brand": hf, "draft": hf}
    text = data.decode("utf-8") if isinstance(data, bytes) else data
    if name.endswith(".html"):
        pages = re.split(r'(?=<section class="page[ "])', text)[1:]
        if pages:                                                      # a print layout: every printed page
            seen = [_visible(p) for p in pages]
            return {"status": seen, "brand": [_visible(text)], "draft": seen}
        seen = [_visible(text)]
        return {"status": seen, "brand": seen, "draft": seen}
    if name.endswith((".md", ".txt")):
        seen = [_norm(text)]
        return {"status": seen, "brand": seen, "draft": seen}
    raise AssertionError(f"{name}: no conformance reader for this document file; add one to _slots")


def _assert_conforms(name, data, draft):
    s = _slots(name, data)
    assert s["status"] and s["draft"], name
    for i, t in enumerate(s["status"]):
        assert STATUS_PHRASE in t, f"{name} slot {i}: no status phrase"
    for i, t in enumerate(s["brand"]):
        assert BRAND in t, f"{name} slot {i}: no brand"
    for i, t in enumerate(s["draft"]):
        assert bool(DRAFT_RX.search(t)) == draft, f"{name} slot {i}: DRAFT shown is {not draft}, pack draft is {draft}"


# ----------------------------------------------------------------------------- the workspace and the signed packs

def _quiet_main(*argv):
    """pmlc's CLI in-process (faster than a subprocess per sign-off); its exit code."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        try:
            code = pmlc.cli.main(list(argv)) or 0
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
    assert code == 0, f"pmlc {' '.join(map(str, argv))} exited {code}: {out.getvalue()}"


@pytest.fixture(scope="module")
def env(tmp_path_factory):
    """A completed synthetic run with one finding edited by a person, so sign-off is allowed. Every fixture (and the
    mini register) sits in it twice: as is (a draft) and signed off as approved, the way the sign-off tests do it
    (tests/test_handling.py). The Hazira samples are never signed."""
    d = tmp_path_factory.mktemp("conformance")
    ws = d / "ws"
    run("ingest", str(make_export(d, edited={"FND-0001": "Yes"})), "--legacy-out", str(ws))
    run("classify", str(ws))
    files = {}
    for state in STATES:
        (d / state).mkdir()
        docs = {n: fixture(n) for n in FIXTURES}
        docs["learnings-register"] = copy.deepcopy(MINI_REG)
        for n, doc in docs.items():
            p = d / state / f"{n}.json"
            p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
            if state == "approved":
                _quiet_main("sign-off", str(ws), str(p), "--status", "approved", "--role", "HSE manager",
                            "--date", "2026-10-19")
            files[state, n] = p
    return {"dir": d, "ws": ws, "w": pmlc.load_ws(ws), "files": files}


def _ctx(env, name, state, **kw):
    p = env["files"][state, name]
    doc = json.loads(p.read_text(encoding="utf-8"))
    eh = effective_handling(doc, env["w"], src=p, ws=env["ws"])
    assert (eh["effective_status"] == "approved") == (state == "approved"), (name, state, eh["draft_reasons"])
    return R.RenderContext(w=env["w"], pack=with_item_ids(doc), run=RUN, generated=R.build_date(), embed="cited",
                           eh=eh, **kw)


def _render_target(ctx, target):
    """The Outputs of one document target: format:<name>, layout:<name> or paper:docx (docx under --layout paper,
    which adds <pack>.paper.docx), each with an optional :learner."""
    bits = target.split(":")
    if len(bits) == 3:
        ctx.view = "learner"
    if bits[0] == "layout":
        ctx.layout = bits[1]
        return render_layout(ctx)
    if bits[0] == "paper":
        ctx.layout = "paper"
        outs = R.render(bits[1], ctx)
        assert any(o.name.endswith(".paper.docx") or o.name.endswith(".paper.learner.docx") for o in outs), outs
        return outs
    return R.render(bits[1], ctx)


def _cli(*args):
    return subprocess.run([sys.executable, str(PMLC), *map(str, args)], capture_output=True, text=True)


def _register_outputs(env, source, target, state, out):
    """Write one register or xlsx target of source with the CLI into out; [(file name, bytes)]."""
    ws, f = env["ws"], env["files"]
    src, kinds = f[state, source], target.split(":")
    if kinds[0] == "register-render":
        r = _cli("register-render", ws, src, "--format", kinds[1], "--out", out)
    elif kinds[0] == "register-xlsx":
        r = _cli("register-xlsx", src, "--out", out / "learnings-register.xlsx", "--ws", ws)
    else:
        r = _cli("pack-xlsx", ws, src, "--kind", kinds[1], "--out", out / "all-kinds.xlsx")
    assert r.returncode == 0, r.stdout + r.stderr
    return [(p.name, p.read_bytes()) for p in sorted(out.iterdir())]


# ----------------------------------------------------------------------------- document formats

DOC_CASES = [(n, t, s) for n in FIXTURES for t in DOC_TARGETS for s in STATES]
DOC_CASES += [("all-kinds" if t.startswith("pack-xlsx") else "learnings-register", t, s)
              for t in REGISTER_TARGETS for s in STATES]


@pytest.mark.parametrize("source,target,state", DOC_CASES)
def test_document_formats_conform(env, tmp_path, source, target, state):
    """P4-20: every document output carries the status phrase and the brand, and DRAFT exactly while it is a draft:
    html, md, docx, pptx, email (html and txt), the 6 layouts, the learner views, register-render docx and email, and
    the register-xlsx and pack-xlsx sheets (SCORM's index.html, through the zip reader, once Task 21 registers it)."""
    if target in REGISTER_TARGETS:
        outs = _register_outputs(env, source, target, state, tmp_path)
    else:
        ctx = _ctx(env, source, state, start=START)
        outs = [(o.name, o.data) for o in _render_target(ctx, target)]
        if not outs:                                       # nothing applies (e.g. no cards): it says so (P4-1)
            assert any("nothing to write" in n for n in ctx.notes), ctx.notes
            return
    assert outs
    for name, data in outs:
        _assert_conforms(name, data, draft=(state == "draft"))


def test_document_targets_cover_every_document_format():
    """The conformance parametrisation follows the registry: a document format added later is read too."""
    assert {t.split(":")[1] for t in DOC_TARGETS if t.startswith("format:")} == set(DOC_FORMATS)
    assert {"html", "md", "docx", "pptx", "email"} <= set(DOC_FORMATS)
    assert len(DOC_TARGETS) == 2 * (len(DOC_FORMATS) + len(LAYOUTS) + 1)


def test_every_layout_writes_for_some_fixture(env):
    """No layout is checked only by its 'nothing to write' note: each prints at least one fixture."""
    for lay in LAYOUTS:
        assert any(render_layout(_ctx(env, n, "draft", layout=lay)) for n in FIXTURES), lay


# ----------------------------------------------------------------------------- data formats

def _ics_props(text: str) -> dict:
    lines = text.replace("\r\n ", "").split("\r\n")                  # unfold (RFC 5545 3.1)
    out = {}
    for ln in lines:
        k, _, v = ln.partition(":")
        out.setdefault(k.split(";")[0], []).append(v.replace("\\,", ",").replace("\\;", ";").replace("\\n", " "))
    return out


def _png_text(data: bytes) -> str:
    """The tEXt and iTXt chunks of a PNG."""
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    i, out = 8, []
    while i < len(data):
        n, kind = struct.unpack(">I4s", data[i:i + 8])
        body = data[i + 8:i + 8 + n]
        assert struct.unpack(">I", data[i + 8 + n:i + 12 + n])[0] == zlib.crc32(kind + body) & 0xFFFFFFFF, kind
        if kind == b"tEXt":
            out.append(body.split(b"\0", 1)[1].decode("latin-1"))
        elif kind == b"iTXt":
            out.append(body.split(b"\0", 1)[1][2:].split(b"\0", 2)[2].decode("utf-8"))
        i += 12 + n
    return " ".join(out)


def _xml_el(text: str, tag: str) -> str:
    return " ".join(_norm(m) for m in re.findall(rf"<{tag}(?: [^>]*)?>(.*?)</{tag}>", text, re.S))


def _qti_slot(data):
    man = zipfile.ZipFile(io.BytesIO(data)).read("imsmanifest.xml").decode("utf-8")
    return _xml_el(man, "lom:string") + " " + _xml_el(man, "description")


DATA_SLOTS = {   # P4-20: where each data format keeps the status and the brand
    "normalised": lambda d: (lambda j: f"{j['status']} {j['brand']}")(json.loads(d)),
    "gift": lambda d: _norm(" ".join(x[2:] for x in d.splitlines() if x.startswith("//"))),
    "svg": lambda d: _xml_el(d, "desc"),
    "graphml": lambda d: _xml_el(d, "desc"),
    "png": _png_text,
    "ics": lambda d: (lambda p: " ".join(p.get("X-PMLC-STATUS", []) + p.get("X-PMLC-BRAND", [])
                                        + p.get("DESCRIPTION", [])[:1]))(_ics_props(d.decode("utf-8"))),
    "qti": _qti_slot,
}


def _first_output(env, fmt):
    """The outputs of fmt for the first fixture that gives it something to write (all-kinds first)."""
    if fmt == "png" and not R.find_browser():
        pytest.skip("no Chromium-family browser: png writes nothing (OD4-2)")
    for n in ["all-kinds"] + FIXTURES:
        outs = R.render(fmt, _ctx(env, n, "draft", start=START))
        if outs:
            return outs
    raise AssertionError(f"no fixture gives {fmt} anything to write")


@pytest.mark.parametrize("fmt", DATA_FORMATS)
def test_data_formats_conform(env, fmt):
    """P4-20: each data format's native slot carries STATUS_PHRASE and BRAND; an exempt one carries neither."""
    outs = _first_output(env, fmt)
    for o in outs:
        if fmt in EXEMPT:
            text = o.data.decode("utf-8") if isinstance(o.data, bytes) else o.data
            assert STATUS_PHRASE not in text and BRAND not in text, f"{o.name}: exempt ({EXEMPT[fmt]})"
            continue
        slot = DATA_SLOTS[fmt](o.data)
        assert STATUS_PHRASE in slot and BRAND in slot, f"{o.name}: slot {slot[:200]!r}"


def test_xliff_file_note_carries_status_and_brand(env):
    """P4-20: an XLIFF strings file holds the status and the brand in a file-level <note>, which apply ignores."""
    pack = with_item_ids(fixture("frontline-learning-cards"))
    text = ST.extract(pack, "hi", "xliff")
    head = re.search(r"<file [^>]*>\s*<header>(.*?)</header>\s*<body>", text, re.S)
    assert head, text[:600]
    notes = _xml_el(head.group(1), "note")
    assert STATUS_PHRASE in notes and BRAND in notes
    assert ST._st_read_xliff(text, "hi") and all(STATUS_PHRASE not in (s or "") for s, _ in
                                                 ST._st_read_xliff(text, "hi").values())


def test_data_format_exempt_list_is_p4_20():
    """The exempt list is exactly P4-20's, each with its reason; every other data format has a slot reader."""
    assert EXEMPT == {"csv": IMPORT_CLEAN, "quiz-csv": IMPORT_CLEAN, "bowtie-csv": IMPORT_CLEAN,
                      "follow-up.csv": IMPORT_CLEAN, "srt": ON_AIR, "narration": ON_AIR}
    assert "follow-up.csv" not in R.FORMATS                         # written by investigator-coach, not a format
    assert set(DATA_FORMATS) == (set(EXEMPT) - {"follow-up.csv"}) | set(DATA_SLOTS)
    assert not set(DATA_SLOTS) & set(EXEMPT)


def test_follow_up_csv_is_clean(env, tmp_path):
    """The exempt follow-up.csv (P4-20) has no status row: it is imported as it is."""
    r = _cli("pack", env["ws"], env["files"]["draft", "investigator-coach"], "--out", tmp_path, "--no-md")
    assert r.returncode == 0, r.stderr
    text = (tmp_path / "follow-up.csv").read_text(encoding="utf-8")
    assert STATUS_PHRASE not in text and BRAND not in text


# ----------------------------------------------------------------------------- every fixture, every format

def _edge_packs():
    """Review Focus 4: an unknown kind, an empty section and a 1-item pack, besides the fixtures."""
    base = fixture("board-brief")
    unknown = copy.deepcopy(base)
    unknown["pack"] = "unknown-kind"
    unknown["sections"][0]["items"].append({"kind": "mystery", "text": "A kind this engine does not know.",
                                            "cites": ["FND-0001"]})
    empty = copy.deepcopy(base)
    empty["pack"] = "empty-section"
    empty["sections"].append({"id": "nothing", "heading": "Nothing here yet", "items": []})
    one = {k: base[k] for k in ("schema", "title", "audience", "status") if k in base}
    one.update(pack="one-item", bottom_line=[], sections=[{"id": "only", "heading": "Only", "items": [
        {"kind": "para", "text": "Test before service.", "cites": ["FND-0001"]}]}])
    return {"unknown-kind": unknown, "empty-section": empty, "one-item": one}


ALL_SOURCES = FIXTURES + [f"alpha4:{n}" for n in FIXTURES] + sorted(_edge_packs())


@pytest.mark.parametrize("source", ALL_SOURCES)
def test_all_fixtures_all_formats(env, source):
    """Review Focus 4 and 3: every fixture, its alpha.4 copy and the edge packs render in every registered format and
    every layout without a traceback; a format with nothing to write says so; every docx and pptx is a sound package."""
    if source.startswith("alpha4:"):
        doc = alpha4_copy(fixture(source.split(":", 1)[1]))
    else:
        doc = _edge_packs().get(source) or fixture(source)
    w = env["w"]
    eh = effective_handling(doc, w)
    targets = [(f, None) for f in R.FORMATS] + [("layout", x) for x in LAYOUTS]
    written = []
    for fmt, lay in targets:
        if fmt == "png" and source.startswith("alpha4:"):
            continue                    # alpha4 copies change no graph; the browser runs once per fixture
        ctx = R.RenderContext(w=w, pack=with_item_ids(doc), run=RUN, generated=R.build_date(), embed="cited", eh=eh,
                              start=START, layout=lay)
        outs = render_layout(ctx) if lay else R.render(fmt, ctx)
        if not outs:
            assert ctx.notes, f"{source} {fmt} {lay}: wrote nothing and said nothing"
        for o in outs:
            assert isinstance(o.data, (str, bytes)) and o.data, o.name
            assert isinstance(o.guard_text, str), o.name
            if o.name.endswith((".docx", ".pptx")):
                assert ooxml_check.check_package(o.data) == [], o.name
            written.append(o.name)
    assert written


def test_soffice_opens_the_all_kinds_docx_and_pptx(env, tmp_path):
    """Review Focus 3, optional: LibreOffice converts the all-kinds docx and pptx when it is installed."""
    if not shutil.which("soffice"):
        pytest.skip("soffice not installed")
    for fmt in ("docx", "pptx"):
        o = R.render(fmt, _ctx(env, "all-kinds", "approved"))[0]
        p = tmp_path / o.name
        p.write_bytes(o.data)
        assert ooxml_check.soffice_roundtrip(p), o.name


# ----------------------------------------------------------------------------- shared copies

@pytest.fixture(scope="module")
def shared(tmp_path_factory):
    """all-kinds with invented names in its text, signed off for external sharing in the privacy tests' run."""
    from test_privacy import share_ws
    d = tmp_path_factory.mktemp("shared")
    ws, orgs = share_ws(d)
    names = d / "names.txt"
    names.write_text("# staff\n" + "\n".join(NAMES) + "\n", encoding="utf-8")
    doc = fixture("all-kinds")
    a, b = NAMES
    for s in doc["sections"]:
        for it in s["items"]:
            for k in ("text", "title", "question", "change", "story", "what_happened", "lesson", "barrier",
                      "failure_mode"):
                if isinstance(it.get(k), str):
                    it[k] = f"{it[k]} {a} and {b} were there."
            for n in it.get("nodes") or []:
                n["label"] = f"{n['label']} ({a})"
            for seg in it.get("segments") or []:
                seg["narration"] = f"{seg['narration']} {b} said so."
            for opt in it.get("options") or []:
                if isinstance(opt, dict):
                    opt["text"] = f"{opt['text']} {a}"
            if it.get("kind") == "check":
                it["when"] = "30 days"                               # ics has an event to write
            it["lint_ok"] = {"rule": "JC1", "reason": "test of the shared copies"}
    doc["bottom_line"][0]["text"] += f" {b} agreed."
    doc["bottom_line"][0]["lint_ok"] = {"rule": "JC1", "reason": "test of the shared copies"}
    p = d / "all-kinds.json"
    p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    r = _cli("sign-off", ws, p, "--status", "approved", "--role", "HSE manager", "--date", "2026-10-19",
             "--classification", "external", "--legal-review", "cleared")
    assert r.returncode == 0, r.stdout + r.stderr
    return {"ws": ws, "orgs": orgs, "names": names, "pack": p, "doc": doc}


def _zip_or_bytes(data: bytes) -> dict:
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        return {"": data}
    return {n: z.read(n) for n in z.namelist()}


SHARE_TARGETS = list(R.FORMATS) + [f"layout:{x}" for x in LAYOUTS]


@pytest.mark.parametrize("target", SHARE_TARGETS)
def test_every_format_shared_copy_masked(shared, tmp_path, target):
    """Review Focus 1: `pack --share external --names` writes only .external. files, from the masked pack: no
    invented name in any Output's guard_text, nor in any byte of any file or zip part."""
    from pmlc_lib.handling import share_ctx, shared_copy
    import argparse
    assert all(n in json.dumps(shared["doc"], ensure_ascii=False) for n in NAMES)
    lay = target.split(":", 1)[1] if target.startswith("layout:") else None
    fmt = "html" if lay else target
    if fmt == "png" and not R.find_browser():
        pytest.skip("no Chromium-family browser: png writes nothing (OD4-2)")
    flags = ["--format", fmt, "--start", START.isoformat()] + (["--layout", lay] if lay else [])
    out = tmp_path / "out"
    r = _cli("pack", shared["ws"], shared["pack"], "--share", "external", "--names", shared["names"],
             "--orgs", shared["orgs"], "--out", out, *flags)
    assert r.returncode == 0, r.stdout + r.stderr
    got = sorted(x.name for x in out.iterdir()) if out.exists() else []
    if fmt not in ("png",) and not lay:
        assert got, f"{target}: nothing written"
    for f in got:
        assert ".external." in f, f
        for part, data in _zip_or_bytes((out / f).read_bytes()).items():
            for n in NAMES:
                assert n.encode("utf-8") not in data, (f, part, n)
    # The Outputs themselves: rendered from the masked pack and workspace, as cmd_pack builds them.
    w = pmlc.load_ws(shared["ws"])
    share = share_ctx(argparse.Namespace(names=str(shared["names"]), orgs=str(shared["orgs"])), w, "external")
    doc = json.loads(shared["pack"].read_text(encoding="utf-8"))
    ctx = R.RenderContext(w=shared_copy(w, share, w), pack=with_item_ids(shared_copy(doc, share, w)), run="shared",
                          generated=R.build_date(), embed="cited", share=share, start=START, layout=lay,
                          eh=effective_handling(doc, w, src=shared["pack"], ws=shared["ws"]))
    outs = render_layout(ctx) if lay else R.render(fmt, ctx)
    plain = dataclasses.replace(ctx, w=w, pack=with_item_ids(doc), share=None, notes=[])
    assert any(n in o.guard_text for o in (render_layout(plain) if lay else R.render(fmt, plain)) for n in NAMES), \
        f"{target}: the unmasked output holds no name, so the masking is not tested"
    for o in outs:
        for n in NAMES:
            assert n not in o.guard_text and n not in html.unescape(o.guard_text), (o.name, n)


# ----------------------------------------------------------------------------- the exit gate's formats

GATE_FORMATS = "html,md,docx,pptx,email,csv"


@pytest.mark.parametrize("name", pack_fixtures())
def test_exit_gate_formats_every_skill(env, tmp_path, name):
    """The Phase 4 exit gate: for every skill with a pack, `pack --format html,md,docx,pptx,email,csv` exits 0."""
    r = _cli("pack", env["ws"], env["files"]["draft", name], "--format", GATE_FORMATS, "--out", tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    got = {p.name for p in tmp_path.iterdir()}
    for ext in ("html", "md", "docx", "pptx", "email.html", "email.txt"):
        assert f"{name}.{ext}" in got, (ext, sorted(got))

