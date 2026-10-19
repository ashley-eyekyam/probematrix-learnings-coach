"""The privacy core (pmlc_privacy): names, variants, singleton roles, on the synthetic export."""
import json
import re

import openpyxl
import pytest

from test_pack import item, pack_with
from test_pmlc import make_export, run
import pmlc  # noqa: E402
import pmlc_lint as pl  # noqa: E402
import pmlc_privacy as pv  # noqa: E402

ROLES = "Security Guard - Gate 3, Shift A Engineer (CR 2), Operator"


@pytest.fixture(scope="module")
def sws(tmp_path_factory):
    d = tmp_path_factory.mktemp("priv")
    x = make_export(d)
    wb = openpyxl.load_workbook(x)
    ws = wb["Identified Findings"]
    col = [c.value for c in ws[1]].index("Individuals Involved") + 1
    ws.cell(row=2, column=col).value = ROLES
    wb.save(x)
    run("ingest", str(x), "--legacy-out", str(d / "ws"))
    run("classify", str(d / "ws"))
    return d / "ws"


def test_singletons_written_by_classify(sws):
    p = sws / "singleton_roles.json"
    doc = json.loads(p.read_text())
    assert doc["version"] == 1
    by = {e["role"]: e for e in doc["roles"]}
    assert by["Security Guard - Gate 3"]["reason"] == "qualifier"
    assert by["Shift A Engineer (CR 2)"]["reason"] == "qualifier"
    assert "Operator" not in by
    for e in doc["roles"]:
        assert set(e) == {"role", "reason", "findings", "generalised"}
        assert e["findings"] >= 1 and re.fullmatch(r".+ \(.+\)", e["generalised"])
    assert pv.load_singletons(pmlc.load_ws(sws))["Shift A Engineer (CR 2)"] == by["Shift A Engineer (CR 2)"]["generalised"]
    p.unlink()
    assert pmlc.load_ws(sws)["singletons"] == []
    run("classify", str(sws))
    assert p.exists()


def _qual(role):
    tax = {"entities": [{"id": "F01", "name": "Ops"}]}
    out = pv.build_singletons({role: {"F": ["F01"], "T": "T1", "R": "actor"}}, [{"roles": [role]}], tax, {"T1": "Frontline"})
    return [e["role"] for e in out["roles"]]


@pytest.mark.parametrize("role", ["Control Room Operator", "Control Room Operators", "Shift Supervisor",
                                  "Maintenance Planner (owner)", "Field Operator - Operations",
                                  "Gas Terminal Control Room Operators (Gas Terminal CR 2)"])
def test_crew_and_bare_qualifiers_are_not_singletons(role):
    assert _qual(role) == []


@pytest.mark.parametrize("role", ["Security Guard - Gate 3", "Panel Operator CR-2", "Shift A Supervisor",
                                  "Clerk #4", "Welder (Bay 7)", "Desk B Clerk", "Control Room 2 Operator"])
def test_instance_ids_are_singletons(role):
    assert _qual(role) == [role]


def test_single_holder_role():
    tax = {"entities": [{"id": "F13", "name": "Plant & Asset Leadership"}]}
    rm = {"Plant Head": {"F": ["F13"], "T": "T4", "R": "owner"},
          "Plant Manager": {"F": ["F13"], "T": "T3", "R": "owner"},
          "Site Director": {"F": ["F13"], "T": "T3", "R": "owner"}}
    fs = [{"roles": ["Plant Head", "Plant Manager"]}, {"roles": ["Plant Head", "Site Director"]}]
    out = pv.build_singletons(rm, fs, tax, {"T3": "Function managers", "T4": "Site leadership"})
    assert out["roles"] == [{"role": "Plant Head", "reason": "single-holder", "findings": 2,
                             "generalised": "Plant & Asset Leadership (Site leadership)"}]


def test_jc7_uses_singletons(sws):
    w = pmlc.load_ws(sws)
    p = pack_with(item("para", text="The Security Guard - Gate 3 closed the valve.", cites=["FND-0001"]))
    internal = [h for h in pl.lint(p, w, kind="pack", share="internal") if h.rule == "JC7"]
    external = [h for h in pl.lint(p, w, kind="pack", share="external") if h.rule == "JC7"]
    assert [h.severity for h in internal] == ["warning"]
    assert [h.severity for h in external] == ["error"]
    ordinary = pack_with(item("para", text="The Control Room Operator closed the valve.", cites=["FND-0001"]))
    assert not [h for h in pl.lint(ordinary, w, kind="pack", share="external") if h.rule == "JC7"]
    clean = pack_with(item("para", text="The Operator closed the valve.", cites=["FND-0001"]))
    assert not [h for h in pl.lint(clean, w, kind="pack", share="external") if h.rule == "JC7"]


def test_name_variants():
    v = pv.name_variants("Shri R. K. Sharma")
    assert v[0] == "Shri R. K. Sharma"
    for x in ("Sharma", "R. Sharma", "R. K. Sharma", "Mr Sharma", "Smt. Sharma", "Dr Sharma"):
        assert x in v
    v = pv.name_variants("Mr J Smith")
    for x in ("Smith", "J. Smith", "J Smith", "Mrs. Smith", "Shri Smith"):
        assert x in v
    assert pv.name_variants("John Smith")[2] == "J. Smith"
    assert pv.name_variants("ID #4471") == ["ID #4471"]
    assert "Dr. Anand" in pv.name_variants("Anand")


def test_name_pattern_boundaries():
    assert pv.name_pattern([]) is None
    rx = pv.name_pattern(["Shri R. K. Sharma", "Mr J Smith"], variants=True)
    for text in ("Shri R. K. Sharma left", "report by R. Sharma.", "Mr  Smith said", "smt. sharma", "(J Smith)"):
        assert rx.search(text), text
    for text in ("Sharmaji left", "the Smithson seal", "unSharma", "Smith2"):
        assert not rx.search(text), text
    exact = pv.name_pattern(["R. K. Sharma"])
    assert exact.search("by R. K. Sharma") and not exact.search("by Sharma")


def test_names_file_comments_and_ids(tmp_path, monkeypatch):
    f = tmp_path / "names.txt"
    f.write_text("  # comment\n\nR. K. Sharma\nID #4471\n", encoding="utf-8")
    assert pv.load_names(str(f)) == ["R. K. Sharma", "ID #4471"]
    rx = pv.name_pattern(pv.load_names(str(f)))
    assert rx.search("Prepared by R. K. Sharma") and rx.search("badge ID #4471 scanned")
    monkeypatch.setenv("PMLC_NAMES", str(f))
    assert len(pv.load_names()) == 2
    monkeypatch.setenv("PMLC_ORGS", str(f))
    assert len(pv.load_orgs()) == 2
    monkeypatch.delenv("PMLC_NAMES")
    assert pv.load_names() == []


def test_patterns_and_suffix():
    assert re.search(pv.PATTERNS["email"], "a.b@x.org") and re.search(pv.PATTERNS["phone"], "+91 98765 43210")
    assert re.search(pv.PATTERNS["staff_no"], "Staff No. 4471") and pv.ORG_SUFFIX_RX.search("Acme Pumps Ltd")


def test_scan_names_uses_privacy_core(tmp_path):
    n = tmp_path / "names.txt"
    n.write_text("# list\n\nR. K. Sharma\n", encoding="utf-8")
    t = tmp_path / "t.md"
    t.write_text("by R. K. Sharma\n", encoding="utf-8")
    from test_pmlc import PMLC
    import subprocess
    import sys
    r = subprocess.run([sys.executable, str(PMLC), "scan-names", str(n), str(t)], capture_output=True, text=True)
    assert r.returncode == 1 and "1 hit" in r.stdout


# ---- Task 10: scan-names hardening and private-output ignore rules ----------------------------------------------
def _scan(tmp_path, names, *args, env=None):
    import subprocess
    import sys
    from test_pmlc import PMLC
    n = tmp_path / "names10.txt"
    n.write_text(names, encoding="utf-8")
    return subprocess.run([sys.executable, str(PMLC), "scan-names", str(n), *map(str, args)],
                          capture_output=True, text=True, env=env)


def _zip(path, members):
    import zipfile
    with zipfile.ZipFile(path, "w") as z:
        for k, v in members.items():
            z.writestr(k, v)
    return path


def test_scan_names_variants(tmp_path):
    t = tmp_path / "t.md"
    t.write_text("Mr Sharma signed. Checked by R. Sharma.\n", encoding="utf-8")
    assert _scan(tmp_path, "Ravi Sharma\n", t).returncode == 0
    r = _scan(tmp_path, "Ravi Sharma\n", t, "--variants")
    assert r.returncode == 1 and "2 hit" in r.stdout and "Mr Sharma" in r.stdout and "R. Sharma" in r.stdout


def test_scan_names_docprops_and_comments(tmp_path):
    d = _zip(tmp_path / "a.docx", {
        "word/document.xml": "<w:t>clean</w:t>",
        "docProps/core.xml": "<dc:creator>Ravi Sharma</dc:creator>",
        "word/comments.xml": "<w:t>ask Ravi Sharma</w:t>",
        "word/header1.xml": "<w:t>Ravi Sharma</w:t>"})
    r = _scan(tmp_path, "Ravi Sharma\n", d)
    assert r.returncode == 1 and "3 hit" in r.stdout and "docProps/core.xml" in r.stdout
    assert "word/comments.xml" in r.stdout and "word/header1.xml" in r.stdout
    x = tmp_path / "b.xlsx"
    wb = openpyxl.Workbook()
    wb.properties.creator = "Ravi Sharma"
    wb.save(x)
    r = _scan(tmp_path, "Ravi Sharma\n", x)
    assert r.returncode == 1 and "docProps/core.xml" in r.stdout
    p = _zip(tmp_path / "c.pptx", {"docProps/core.xml": "<dc:creator>Ravi Sharma</dc:creator>"})
    assert _scan(tmp_path, "Ravi Sharma\n", p).returncode == 1


def test_scan_names_patterns(tmp_path):
    t = tmp_path / "t.md"
    t.write_text("mail a.b@x.org or call +91 98765 43210; Staff No. 4471\n", encoding="utf-8")
    assert _scan(tmp_path, "Nobody Here\n", t).returncode == 0
    r = _scan(tmp_path, "Nobody Here\n", t, "--patterns")
    assert r.returncode == 1
    for lab in ("pattern:email", "pattern:phone", "pattern:staff_no"):
        assert lab in r.stdout


def test_scan_names_pdf_metadata(tmp_path):
    import shutil
    if not shutil.which("pdfinfo"):
        pytest.skip("pdfinfo not installed")
    pdf = tmp_path / "m.pdf"
    pdf.write_bytes(
        b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 10 10]>>endobj\n"
        b"4 0 obj<</Author(Ravi Sharma)/Creator(Writer)>>endobj\n"
        b"trailer<</Root 1 0 R/Info 4 0 R/Size 5>>\n%%EOF\n")
    r = _scan(tmp_path, "Ravi Sharma\n", pdf)
    assert "pdf:Author" in r.stdout and "1 hit" in r.stdout and r.returncode == 1


def test_scan_names_pdf_without_pdfinfo(tmp_path):
    import os
    pdf = tmp_path / "m.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    env = dict(os.environ, PATH=str(tmp_path / "empty"))
    r = _scan(tmp_path, "Ravi Sharma\n", pdf, env=env)
    assert "note: pdfinfo not found: PDF metadata not checked" in r.stdout


def test_gitignore_private_outputs():
    import shutil
    import subprocess
    if not shutil.which("git"):
        pytest.skip("git not installed")
    root = pmlc.HERE.parent.parent.parent

    def ignored(p):
        return subprocess.run(["git", "check-ignore", "-q", p], cwd=root).returncode == 0
    for p in ("pmlc-runs/x/outputs/a.pdf", "docs/x.docx", "x.pptx"):
        assert ignored(p), p
    for p in ("samples/x/a.pdf", "docs/briefs/a.pdf", "samples/x/outputs/a.docx"):
        assert not ignored(p), p


def test_scan_names_unreadable_office_files_are_unread(tmp_path):
    for nm in ("bad.docx", "bad.xlsx", "bad.pptx"):
        f = tmp_path / nm
        f.write_text("not a zip", encoding="utf-8")
        r = _scan(tmp_path, "Ravi Sharma\n", f)
        assert r.returncode == 2 and nm in r.stdout and "not scanned" in r.stdout, nm


def test_scan_names_split_runs_and_body(tmp_path):
    d = _zip(tmp_path / "s.docx", {
        "word/document.xml": "<w:p><w:r><w:t>Ra</w:t></w:r><w:r><w:rPr><w:b/></w:rPr><w:t>vi Sharma</w:t></w:r></w:p>"})
    r = _scan(tmp_path, "Ravi Sharma\n", d)
    assert r.returncode == 1 and "1 hit" in r.stdout and "word/document.xml" in r.stdout
    e = _zip(tmp_path / "e.pptx", {"ppt/slides/slide1.xml": "<a:p><a:r><a:t>R&amp;D: Ravi</a:t></a:r></a:p>"
                                   "<a:p><a:r><a:t>Sharma</a:t></a:r></a:p>"})
    assert _scan(tmp_path, "Ravi Sharma\n", e).returncode == 1  # a paragraph break counts as whitespace (conservative)
    assert _scan(tmp_path, "R&D\n", e).returncode == 1  # entity unescaped


def test_scan_names_names_only_in_attributes(tmp_path):
    cases = {
        "a.docx": ("word/comments.xml", '<w:comment w:id="0" w:author="Ravi Sharma" w:initials="RS"><w:p/></w:comment>'),
        "b.docx": ("word/people.xml", '<w15:person w15:author="Ravi Sharma"><w15:presenceInfo/></w15:person>'),
        "c.pptx": ("ppt/commentAuthors.xml", '<p:cmAuthor id="0" name="Ravi Sharma" initials="RS"/>'),
        "f.pptx": ("ppt/authors.xml", '<p188:author id="{1}" name="Ravi Sharma" userId="x"/>'),
        "g.xlsx": ("xl/persons/person.xml", '<person displayName="Ravi Sharma" id="{1}" userId="x"/>'),
        "d.pptx": ("ppt/comments/modernComment_1_2.xml", "<p188:cm author='Ravi Sharma'/>"),
    }
    for nm, (part, xml) in cases.items():
        r = _scan(tmp_path, "Ravi Sharma\n", _zip(tmp_path / nm, {part: xml}))
        assert r.returncode == 1 and part in r.stdout, nm
    n = _zip(tmp_path / "h.docx", {"word/comments.xml": '<w:comment username="Ravi Sharma" filename="Ravi Sharma"/>'})
    assert _scan(tmp_path, "Ravi Sharma\n", n).returncode == 0  # username= / filename= are not name attributes
    z = _zip(tmp_path / "e.docx", {"word/comments.xml": '<w:comment w:author="A &amp; Ravi Sharma"/>'})
    assert _scan(tmp_path, "A & Ravi Sharma\n", z).returncode == 1


def test_scan_names_oversize_member(tmp_path, monkeypatch):
    monkeypatch.setattr(pmlc, "_MAX_MEMBER", 10)
    d = _zip(tmp_path / "big.docx", {"docProps/core.xml": "<x>" + "a" * 50 + "</x>"})
    out = list(pmlc._iter_texts(d, bad := []))
    assert out == [] and bad == [str(d)]


def test_pdf_meta_failure_is_not_checked(tmp_path):
    import shutil
    if not shutil.which("pdfinfo"):
        pytest.skip("pdfinfo not installed")
    f = tmp_path / "junk.pdf"
    f.write_bytes(b"junk")
    assert pmlc._pdf_meta(f) is False


# ----------------------------------------------------------------------------- public-sample tooling (Task 9)

def _sample(tmp_path, *extra, hidden_name=False):
    import subprocess
    import sys
    from openpyxl.comments import Comment
    from test_pmlc import ROOT
    memo = "To: Qux Zorbin\nFrom: Qux Zorbin\nCc: boss\n" + "The pump seal failed and leaked. " * 8
    x = make_export(tmp_path, summary=[("Investigating Officer", "Qux Zorbin"), ("Supervisor at Time", "Qux Zorbin")],
                    narrative=memo)
    wb = openpyxl.load_workbook(x)
    wb.properties.creator = "Qux Zorbin"
    wb.properties.lastModifiedBy = "Qux Zorbin"
    ws = wb["Identified Findings"]
    ws["A2"].comment = Comment("note by Qux Zorbin", "Qux Zorbin")
    ws.oddHeader.center.text = "Qux Zorbin"
    ws.oddFooter.left.text = "Qux Zorbin"
    if hidden_name:
        ws.append(["FND-9999", "", "Hidden Qux Zorbin"])
        ws.row_dimensions[ws.max_row].hidden = True
    wb.create_sheet("Personnel").append(["Qux Zorbin"])
    wb["Personnel"].sheet_state = "hidden"
    wb.save(x)
    out = tmp_path / "out.xlsx"
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "make-public-sample.py"), str(x), str(out), *extra],
                       capture_output=True, text=True)
    return out, r


def test_make_public_sample_strips_metadata(tmp_path):
    import subprocess
    import sys
    import zipfile
    from test_pmlc import PMLC
    out, r = _sample(tmp_path)
    assert r.returncode == 0, r.stderr + r.stdout
    with zipfile.ZipFile(out) as z:
        assert not [n for n in z.namelist() if "comment" in n.lower()]
        blob = " ".join(z.read(n).decode("utf-8", "ignore") for n in z.namelist())
    assert "Qux" not in blob
    names = tmp_path / "n.txt"
    names.write_text("Qux Zorbin\n")
    r = subprocess.run([sys.executable, str(PMLC), "scan-names", str(names), str(out)], capture_output=True, text=True)
    assert r.returncode == 0 and "0 hit" in r.stdout
    # a hidden row in a kept sheet is unhidden, so the --names scan sees it and refuses to write
    h = tmp_path / "h"
    h.mkdir()
    out2, r2 = _sample(h, "--names", str(names), hidden_name=True)
    assert r2.returncode != 0 and "Hidden Qux" in r2.stdout and not out2.exists()


def test_make_public_sample_blanks_fields_and_memo_lines(tmp_path):
    out, r = _sample(tmp_path)
    assert r.returncode == 0, r.stderr
    s = openpyxl.load_workbook(out)["Incident Summary"]
    vals = {r[0].value: r[1].value for r in s.iter_rows() if r[0].value}
    assert vals["Investigating Officer"] is None and vals["Supervisor at Time"] is None
    text = " ".join(str(c.value) for r in s.iter_rows() for c in r if c.value)
    assert "To:" not in text and "From:" not in text and "Cc:" not in text and "pump seal failed" in text
    k = tmp_path / "k"
    k.mkdir()
    out2, r2 = _sample(k, "--keep-field", "Investigating Officer")
    assert r2.returncode == 0, r2.stderr
    s2 = openpyxl.load_workbook(out2)["Incident Summary"]
    vals2 = {r[0].value: r[1].value for r in s2.iter_rows() if r[0].value}
    assert vals2["Investigating Officer"] == "Qux Zorbin" and vals2["Supervisor at Time"] is None


def test_initials_without_space_match(tmp_path):
    rx = pv.name_pattern(["R. K. Sharma"], variants=True)
    for t in ("R.K. Sharma", "R. K. Sharma", "R K Sharma", "Shri Sharma", "r.k. sharma"):
        assert rx.fullmatch(t), t
    assert not rx.search("RKSharmaji")


def test_keep_field_unknown_warns_and_label_tolerant(tmp_path):
    import subprocess
    import sys
    from test_pmlc import ROOT
    x = make_export(tmp_path, summary=[(" investigating officer ", "Qux Zorbin")])
    out = tmp_path / "o.xlsx"
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "make-public-sample.py"), str(x), str(out),
                        "--keep-field", "Nonsense"], capture_output=True, text=True)
    assert r.returncode == 0 and "--keep-field 'nonsense' matches none" in r.stderr
    s = openpyxl.load_workbook(out)["Incident Summary"]
    assert "Qux" not in " ".join(str(c.value) for row in s.iter_rows() for c in row if c.value)
