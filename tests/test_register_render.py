"""register-render (Task 22, L4-27 and L4-03): the Learnings Register as a Word document and an email digest."""
import copy
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from ooxml_check import check_package, soffice_roundtrip
from test_pmlc import MINI_REG, PMLC, run
from test_privacy import _cli, shws as shws, sign, write_doc  # noqa: F401,F811
import pmlc  # noqa: E402
from pmlc_lib import BRAND, DRAFT_LABEL, STATUS_PHRASE  # noqa: E402
from pmlc_lib.handling import effective_handling  # noqa: E402
from pmlc_lib.register import render as RR  # noqa: E402
from pmlc_lib.render.docx import docx_text  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HAZIRA = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
SECTIONS = ["Summary", "Priority 1 learnings", "All learnings"]
HOSTILE = "R&D <b>\"q\"</b> 'x' \x0bनमस्ते \U0001F600"


@pytest.fixture(scope="module")
def hws(tmp_path_factory):
    d = tmp_path_factory.mktemp("rrhaz")
    run("ingest", str(HAZIRA / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"),
        "--slug", "hazira-gas-release-fire", "--root", str(d))
    return d / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"


@pytest.fixture(scope="module")
def mws(tmp_path_factory):
    d = tmp_path_factory.mktemp("rrmini")
    from test_pmlc import make_export
    x = make_export(d)
    run("ingest", str(x), "--legacy-out", str(d / "ws"))
    run("classify", str(d / "ws"))
    return d / "ws"


def mini_reg():
    reg = copy.deepcopy(MINI_REG)
    e = copy.deepcopy(reg["entries"][0])
    e.update(lr_id="LR-02", title="Hostile " + HOSTILE, priority=2, lesson="Lesson " + HOSTILE)
    reg["entries"].append(e)
    return reg


def render_to(ws, reg_path, out, *extra):
    r = subprocess.run([sys.executable, str(PMLC), "register-render", str(ws), str(reg_path), "--out", str(out),
                        *extra], capture_output=True, text=True)
    return r


def parts(data):
    z = zipfile.ZipFile(__import__("io").BytesIO(data))
    return {n: z.read(n).decode("utf-8", "replace") for n in z.namelist() if n.endswith(".xml")}


def check_docx(path, draft=True):
    data = Path(path).read_bytes()
    assert check_package(data) == []
    text = docx_text(data)
    assert STATUS_PHRASE in text and BRAND in text
    p = parts(data)
    assert STATUS_PHRASE in p["word/footer1.xml"] and BRAND in p["word/footer1.xml"]
    assert (DRAFT_LABEL in text) is draft
    return text


@pytest.mark.parametrize("which", ["mini", "hazira"])
def test_register_docx_valid_and_conformant(which, mws, hws, tmp_path):
    ws, reg = (mws, mini_reg()) if which == "mini" else (hws, json.loads((HAZIRA / "outputs" / "learnings-register.json").read_text("utf-8")))
    rp = write_doc(tmp_path, reg, "reg.json")
    r = render_to(ws, rp, tmp_path / "o", "--format", "docx")
    assert r.returncode == 0, r.stderr
    out = tmp_path / "o"
    assert sorted(x.name for x in out.iterdir()) == ["learnings-register.docx"]
    text = check_docx(out / "learnings-register.docx")
    eh = effective_handling(reg, pmlc.load_ws(ws), src=str(rp), ws=str(ws))
    for line in pmlc.handling_lines(eh):
        assert line in text
    pos = [text.index(s) for s in SECTIONS]
    assert pos == sorted(pos) and reg.get("title", "Learnings Register") in text
    for e in reg["entries"]:
        assert e["lr_id"] in text
    assert soffice_roundtrip(out / "learnings-register.docx") in (True, False)


def test_register_docx_soffice(mws, tmp_path):
    from shutil import which
    if not which("soffice"):
        pytest.skip("soffice not installed")
    rp = write_doc(tmp_path, mini_reg(), "reg.json")
    assert render_to(mws, rp, tmp_path / "o", "--format", "docx").returncode == 0
    assert soffice_roundtrip(tmp_path / "o" / "learnings-register.docx") is True


def test_register_docx_hostile_text_survives(mws, tmp_path):
    rp = write_doc(tmp_path, mini_reg(), "reg.json")
    assert render_to(mws, rp, tmp_path / "o", "--format", "docx").returncode == 0
    text = check_docx(tmp_path / "o" / "learnings-register.docx")
    assert "R&D <b>" in text and "नमस्ते" in text and "\U0001F600" in text


def test_register_email(hws, tmp_path):
    reg = json.loads((HAZIRA / "outputs" / "learnings-register.json").read_text("utf-8"))
    rp = write_doc(tmp_path, reg, "reg.json")
    r = render_to(hws, rp, tmp_path / "o", "--format", "email")
    assert r.returncode == 0, r.stderr
    html = (tmp_path / "o" / "learnings-register.email.html").read_bytes()
    txt = (tmp_path / "o" / "learnings-register.email.txt").read_text("utf-8")
    assert not (tmp_path / "o" / "learnings-register.docx").exists()
    assert len(html) < 100_000
    for body in (html.decode("utf-8"), " ".join(txt.split())):
        assert STATUS_PHRASE in body and BRAND in body and DRAFT_LABEL in body
    assert "<script" not in html.decode("utf-8") and "<img" not in html.decode("utf-8")
    assert "LR-01" in txt and "Priority 1 learnings" in txt


def test_register_email_size(hws, tmp_path):
    reg = json.loads((HAZIRA / "outputs" / "learnings-register.json").read_text("utf-8"))
    rp = write_doc(tmp_path, reg, "reg.json")
    assert render_to(hws, rp, tmp_path / "o").returncode == 0
    assert (tmp_path / "o" / "learnings-register.email.html").stat().st_size < 100_000
    assert (tmp_path / "o" / "learnings-register.docx").is_file()          # the default is docx,email


def test_register_render_shared(tmp_path, shws):  # noqa: F811
    ws, orgs = shws
    reg = copy.deepcopy(MINI_REG)
    reg["entries"][0]["lesson"] += " Bharat Seals did it."
    reg["source"] = "secret-export.xlsx"
    rp = write_doc(tmp_path, reg, "reg.json")
    sign(ws, rp, "--classification", "external", "--legal-review", "cleared")
    out = tmp_path / "o"
    r = render_to(ws, rp, out, "--share", "external", "--orgs", str(orgs))
    assert r.returncode == 0, r.stderr
    names = sorted(x.name for x in out.iterdir())
    assert names == ["learnings-register.email.external.html", "learnings-register.email.external.txt",
                     "learnings-register.external.docx"]
    text = check_docx(out / "learnings-register.external.docx", draft=False)
    assert "Shared external: identifying details are masked" in text
    for n in names:
        raw = (out / n).read_bytes()
        body = "".join(parts(raw).values()) if n.endswith(".docx") else raw.decode("utf-8")
        assert "Bharat Seals" not in body and "secret-export" not in body, n
    assert "[organisation]" in text
    assert "Shared external" in (out / "learnings-register.email.external.txt").read_text("utf-8")


def test_register_render_shared_refused_while_draft(mws, tmp_path):
    rp = write_doc(tmp_path, copy.deepcopy(MINI_REG), "reg.json")
    r = render_to(mws, rp, tmp_path / "o", "--share", "external")
    assert r.returncode == 1 and "cannot share externally" in r.stderr
    assert not (tmp_path / "o").exists()


def test_register_render_name_guard(mws, tmp_path):
    names = tmp_path / "names.txt"
    names.write_text("Hostile\n", encoding="utf-8")
    rp = write_doc(tmp_path, mini_reg(), "reg.json")
    r = render_to(mws, rp, tmp_path / "o", "--names", str(names))
    assert r.returncode == 1 and "a listed name appears" in r.stderr
    assert not (tmp_path / "o").exists()


@pytest.mark.parametrize("fmt", ["md", "xlsx", "docx,md", "email,xlsx"])
def test_register_render_refuses_md(fmt, mws, tmp_path):
    rp = write_doc(tmp_path, mini_reg(), "reg.json")
    r = render_to(mws, rp, tmp_path / "o", "--format", fmt)
    assert r.returncode == 2
    assert "use register-md / register-xlsx" in r.stderr
    assert not (tmp_path / "o").exists()


def test_register_render_unknown_format_and_pack(mws, tmp_path):
    rp = write_doc(tmp_path, mini_reg(), "reg.json")
    r = render_to(mws, rp, tmp_path / "o", "--format", "pdf")
    assert r.returncode == 2 and "choose from: docx, email" in r.stderr
    pack = write_doc(tmp_path, {"pack": "x", "schema": 1, "sections": []}, "pack.json")
    assert render_to(mws, pack, tmp_path / "o2").returncode != 0


def test_register_render_default_out_is_run_outputs(shws, tmp_path):  # noqa: F811
    ws, _ = shws
    rp = write_doc(tmp_path, copy.deepcopy(MINI_REG), "reg.json")
    r = _cli("register-render", str(ws), str(rp))
    assert r.returncode == 0, r.stderr
    out = ws.parent / "outputs"
    assert (out / "learnings-register.docx").is_file() and (out / "learnings-register.email.html").is_file()


def test_register_blocks_order_and_cites():
    eh = {"effective_status": "draft", "classification": "internal", "version": 1, "draft_reasons": [],
          "reviewer_role": None, "reviewed_on": None, "legal_review": "not-required", "distribution": []}
    blocks = RR.register_blocks(MINI_REG["entries"], eh, "T", "")
    kinds = [b[0] for b in blocks]
    assert kinds[0] == "title" and blocks[0][1] == "T"
    heads = [b[1] for b in blocks if b[0] == "heading1"]
    assert heads == SECTIONS
    cited = [b[2] for b in blocks if b[2]]
    assert cited == [["FND-0001", "FND-0002", "EVD-0001"]]
    assert blocks[-1] == ("note", BRAND, None)
    assert not re.search(r"owner|due", " ".join(str(b[1]) for b in blocks if b[0] == "heading1"), re.I)


def test_register_email_counts_learnings_left_out(mws, tmp_path):
    reg = copy.deepcopy(MINI_REG)
    base = reg["entries"][0]
    reg["entries"] = [dict(copy.deepcopy(base), lr_id=f"LR-{n:03d}", priority=3,
                           title=f"Learning {n} " + "word " * 60) for n in range(1, 161)]
    rp = write_doc(tmp_path, reg, "reg.json")
    assert render_to(mws, rp, tmp_path / "o", "--format", "email").returncode == 0
    txt = (tmp_path / "o" / "learnings-register.email.txt").read_text("utf-8")
    html = (tmp_path / "o" / "learnings-register.email.html").read_text("utf-8")
    shown = len(re.findall(r"^  - LR-\d{3} \|", txt, re.M))
    said = re.findall(r"(\d+) more learnings are in the full register \(learnings-register\.docx / \.md\)",
                      " ".join(txt.split()))
    assert 0 < shown < 160 and said == [str(160 - shown)]
    assert said[0] in html and "more items are in the full pack" not in txt


def test_register_left_key_labels_in_both_languages():
    from pmlc_lib.render.labels import load_labels
    for lang in ("en", "hi"):
        assert "{n}" in load_labels(lang)["ui.email.learnings_left"]
