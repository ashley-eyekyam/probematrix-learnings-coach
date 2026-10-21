"""Structural checks for the docx and pptx files the engine writes (Ruling P4-28): the problems that make Word or
PowerPoint refuse to open a file, found without either program. check_package returns a list of problems ([] when
the package is sound); soffice_roundtrip converts the file to PDF with LibreOffice when it is installed."""
import io
import posixpath
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"
SLIDE_RX = re.compile(r"ppt/slides/(slide\d+\.xml)")


def _open(path_or_bytes):
    data = path_or_bytes if isinstance(path_or_bytes, (bytes, bytearray)) else Path(path_or_bytes).read_bytes()
    return zipfile.ZipFile(io.BytesIO(data))


def _rels_base(name: str) -> str:
    """The folder a .rels part's relative targets resolve from: word/_rels/document.xml.rels -> word/."""
    head = name.rsplit("_rels/", 1)[0]
    return head


def _adjacent_tables(name, root, problems):
    tbl = f"{{{W}}}tbl"
    for parent in root.iter():
        kids = list(parent)
        for a, b in zip(kids, kids[1:]):
            if a.tag == tbl and b.tag == tbl:
                problems.append(f"{name}: a w:tbl directly followed by another w:tbl (separate them with a paragraph)")
                return


def check_package(path_or_bytes) -> list:
    """Every problem found: unparsable XML, a part with no content type, a relationship whose target is missing, a
    docx section without a footer, missing separator endnotes (-1 and 0), two adjacent tables, a pptx slide without
    a notes slide."""
    try:
        z = _open(path_or_bytes)
    except zipfile.BadZipFile:
        return ["(package): not a zip file"]
    names = [n for n in z.namelist() if not n.endswith("/")]
    have = set(names)
    problems, trees = [], {}
    for n in names:
        if n.endswith((".xml", ".rels")):
            try:
                trees[n] = ET.fromstring(z.read(n))
            except ET.ParseError as e:
                problems.append(f"{n}: does not parse ({e})")
    ct = trees.get("[Content_Types].xml")
    if ct is None:
        problems.append("[Content_Types].xml: missing or unparsable")
        defaults, overrides = {}, set()
    else:
        defaults = {e.get("Extension", "").lower() for e in ct.iter(f"{{{CT}}}Default")}
        overrides = {e.get("PartName", "").lower() for e in ct.iter(f"{{{CT}}}Override")}
    for n in names:
        if n == "[Content_Types].xml":
            continue
        ext = n.rsplit(".", 1)[-1].lower() if "." in n.rsplit("/", 1)[-1] else ""
        if f"/{n}".lower() not in overrides and ext not in defaults:
            problems.append(f"{n}: no content type (Default or Override) in [Content_Types].xml")
    for n, root in trees.items():
        if not n.endswith(".rels"):
            continue
        base = _rels_base(n)
        for rel in root.iter(f"{{{PR}}}Relationship"):
            if rel.get("TargetMode") == "External":
                continue
            t = rel.get("Target", "")
            target = t.lstrip("/") if t.startswith("/") else posixpath.normpath(posixpath.join(base, t))
            if target not in have:
                problems.append(f"{n}: relationship {rel.get('Id')} targets {target}, which is missing")
    doc = trees.get("word/document.xml")
    if doc is not None:
        sects = list(doc.iter(f"{{{W}}}sectPr"))
        if not any(s.find(f"{{{W}}}footerReference") is not None for s in sects):
            problems.append("word/document.xml: no sectPr has a footer reference")
    notes = trees.get("word/endnotes.xml")
    if notes is not None:
        ids = {e.get(f"{{{W}}}id") for e in notes.iter(f"{{{W}}}endnote")}
        if not {"-1", "0"} <= ids:
            problems.append("word/endnotes.xml: the separator endnotes (ids -1 and 0) are missing")
    for n, root in trees.items():
        if n.startswith("word/") and n.endswith(".xml"):
            _adjacent_tables(n, root, problems)
    for n in names:
        m = SLIDE_RX.fullmatch(n)
        if not m:
            continue
        rels = trees.get(f"ppt/slides/_rels/{m.group(1)}.rels")
        if rels is None or not any(r.get("Type", "").endswith("/notesSlide")
                                   for r in rels.iter(f"{{{PR}}}Relationship")):
            problems.append(f"{n}: no notes slide relationship")
    return problems


def soffice_roundtrip(path) -> bool:
    """True when LibreOffice (soffice on PATH) converts the file to a PDF; False when it fails or is absent."""
    exe = shutil.which("soffice")
    if not exe:
        return False
    with tempfile.TemporaryDirectory() as d:
        profile = Path(d) / "profile"
        try:
            subprocess.run([exe, f"-env:UserInstallation=file://{profile}", "--headless", "--convert-to", "pdf",
                            "--outdir", d, str(path)], capture_output=True, timeout=180, check=False)
        except (OSError, subprocess.TimeoutExpired):
            return False
        return (Path(d) / (Path(path).stem + ".pdf")).is_file()
