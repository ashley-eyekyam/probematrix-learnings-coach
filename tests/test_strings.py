"""Phase 4, Task 18: `strings extract/apply` (XLIFF 1.2 or CSV), translated variant packs, the back-translation check
and the Hindi glossary (Rulings P4-13, P4-14, P4-15; owner decision OD4-1; L4-14, L1-08). Synthetic fixtures only."""
import copy
import csv
import io
import json
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from test_pmlc import run, run_fail, ws  # noqa: F401  (ws is a module-scoped fixture)
from test_pack import fixture, render_fixture
import pmlc  # noqa: E402
import pmlc_pack as pp  # noqa: E402

from pmlc_lib import BRAND, STATUS_PHRASE, strings as S  # noqa: E402
from pmlc_lib.render import TRANSLATION_NOTE  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = ROOT / "skills" / "learnings-coach" / "references" / "glossary.json"
XLF = "{urn:oasis:names:tc:xliff:document:1.2}"
SRC = "frontline-learning-cards"
DOCTYPE_MSG = "strings file must not contain a DOCTYPE or entity declarations"


@pytest.fixture(scope="module")
def w(ws):  # noqa: F811
    return pmlc.load_ws(ws)


def fill_csv(text, edit=None):
    """Every target set to its source (edit(row) may change a row)."""
    rows = list(csv.DictReader(io.StringIO(text.lstrip("﻿"))))
    for r in rows:
        r["target"] = r["source"]
        if edit:
            edit(r)
    buf = io.StringIO(newline="")
    wr = csv.DictWriter(buf, fieldnames=list(rows[0]), lineterminator="\r\n")
    wr.writeheader()
    wr.writerows(rows)
    return buf.getvalue()


def fill_xliff(text):
    root = ET.fromstring(text)
    for tu in root.iter(f"{XLF}trans-unit"):
        src, tgt = tu.find(f"{XLF}source"), tu.find(f"{XLF}target")
        tgt.text = src.text
        for child in list(tgt):
            tgt.remove(child)
        for child in src:
            tgt.append(copy.deepcopy(child))
        tgt.set("state", "translated")
    return ET.tostring(root, encoding="unicode")


def fill(text, fmt):
    return fill_csv(text) if fmt == "csv" else fill_xliff(text)


def strip_translation(out):
    """The translated pack less what apply adds, so it can be compared with the source."""
    out = copy.deepcopy(out)
    for k in ("lang", "skill", "translation_of"):
        out.pop(k)
    out["pack"] = out["pack"][: -len("-hi")]
    for s in out["sections"]:
        for it in s["items"]:
            it.pop("source_text", None)
            it.pop("back_translation", None)
    return out


def test_extract_units_and_locked_fields():
    pack = fixture(SRC)
    us = S.units(pack)
    paths = [p for p, _ in us]
    assert len(paths) == len(set(paths))
    locked = ("kind", "id", "cites", "row_cites", "learning", "status", "schema", "pack", "scope", "hold_point")
    for p in paths:
        last = re.split(r"[.\[]", p.split("#")[0])[-1]
        assert last not in locked, p
        assert not p.startswith(("scope", "status", "pack", "schema")), p
    src = dict(us)
    assert src["sections[0].items[0].text"].endswith("at the shift briefing {c1}.")
    assert src["sections[1].items[0].why_made_sense"] == ("There was no return-to-service checklist, so the test was "
                                                          "easy to miss {c1}.")
    assert "FND-" not in "".join(src.values())
    assert src["title"] and src["sections[1].items[0].warning_signs[1]"]
    # the two "Stop and ask" checks are safety-critical: each gets a back-translation unit
    assert [p for p in paths if p.endswith("#back_translation")] == ["sections[3].items[0]#back_translation",
                                                                    "sections[3].items[1]#back_translation"]
    x = S.extract(pack, "hi", "xliff")
    assert 'target-language="hi"' in x and 'source-language="en"' in x
    assert '<x id="c1" ctype="x-pmlc-cite"/>' in x and "[FND-0002]" not in x
    c = S.extract(pack, "hi", "csv")
    assert c.startswith("﻿id,source,target,note\r\n") and "{c1}" in c and "target-language: hi" in c


def test_extract_glossary_notes():
    pack = fixture(SRC)
    pack["sections"][0]["items"].append({"kind": "para", "text": "Each HFACS barrier is a learning [FND-0001]."})
    rows = {r["id"]: r for r in csv.DictReader(io.StringIO(S.extract(pack, "hi", "csv").lstrip("﻿")))}
    note = rows["sections[0].items[2].text"]["note"]
    assert "HFACS (keep as written)" in note and "Barrier = सुरक्षा बचाव" in note and "Learning = सीख" in note
    x = S.extract(pack, "hi", "xliff")
    assert "HFACS (keep as written)" in x


def test_safety_critical():
    assert S.safety_critical({"kind": "check", "text": "Check the gauge.", "hold_point": True})
    assert not S.safety_critical({"kind": "check", "text": "Check the gauge.", "hold_point": False})
    for t in ("Do not restart the pump.", "HALT the job.", "do not enter the bund", "Do Not Proceed"):
        assert S.safety_critical({"kind": "para", "text": t}), t
    assert not S.safety_critical({"kind": "para", "text": "Nonstop production; the pump restarted."})
    assert S.safety_critical({"kind": "card", "title": "x", "warning_signs": ["Stop when unsure"]})


@pytest.mark.parametrize("fmt", ["xliff", "csv"])
def test_roundtrip_identity(w, fmt):
    pack = fixture(SRC)
    out = S.apply(pack, fill(S.extract(pack, "hi", fmt), fmt), "hi", fmt)
    assert out["pack"] == f"{SRC}-hi" and out["skill"] == SRC and out["translation_of"] == SRC and out["lang"] == "hi"
    assert strip_translation(out) == pack
    checks = out["sections"][3]["items"]
    assert checks[0]["source_text"] == {"text": "Stop and ask if there is no leak-test record before a restart.",
                                        "when": "before restart"}
    assert checks[0]["back_translation"].startswith("Stop and ask if there is no leak-test record")
    assert all("source_text" not in it for s in out["sections"][:3] for it in s["items"])
    assert pp.check_pack(out, w).problems == []
    assert pp.check_pack(out, w, strict=True).problems == []


def test_translated_text_lands_in_place():
    pack = fixture(SRC)

    def hindi(r):
        if r["id"] == "sections[0].items[0].text":
            r["target"] = "ये कार्ड पढ़ें {c1}।"
        if r["id"] == "title":
            r["target"] = "फ्रंटलाइन सीख कार्ड"
    out = S.apply(pack, fill_csv(S.extract(pack, "hi", "csv"), hindi), "hi", "csv")
    assert out["title"] == "फ्रंटलाइन सीख कार्ड"
    assert out["sections"][0]["items"][0]["text"] == "ये कार्ड पढ़ें [FND-0001; FND-0004]।"
    assert out["status"] == STATUS_PHRASE or STATUS_PHRASE in out["status"]


def test_apply_refuses_missing_placeholder():
    pack = fixture(SRC)

    def drop(r):
        if r["id"] == "sections[0].items[0].text":
            r["target"] = r["target"].replace("{c1}", "")
    with pytest.raises(S.StringsError, match=r"sections\[0\]\.items\[0\]\.text.*placeholder"):
        S.apply(pack, fill_csv(S.extract(pack, "hi", "csv"), drop), "hi", "csv")

    def add(r):
        if r["id"] == "title":
            r["target"] += " {c1}"
    with pytest.raises(S.StringsError, match="placeholder"):
        S.apply(pack, fill_csv(S.extract(pack, "hi", "csv"), add), "hi", "csv")


def test_apply_refuses_untranslated_without_allow_partial():
    pack = fixture(SRC)

    def blank(r):
        if r["id"] in ("title", "sections[3].items[0]#back_translation"):
            r["target"] = ""
    text = fill_csv(S.extract(pack, "hi", "csv"), blank)
    with pytest.raises(S.StringsError, match="2 units are untranslated.*--allow-partial"):
        S.apply(pack, text, "hi", "csv")
    out = S.apply(pack, text, "hi", "csv", allow_partial=True)
    assert out["title"] == pack["title"]                                  # the English is kept
    assert "back_translation" not in out["sections"][3]["items"][0]
    assert "back_translation" in out["sections"][3]["items"][1]


def test_apply_refuses_changed_source_and_unknown_unit():
    pack = fixture(SRC)
    text = fill_csv(S.extract(pack, "hi", "csv"))
    changed = copy.deepcopy(pack)
    changed["title"] = "Another title"
    with pytest.raises(S.StringsError, match="title: the English has changed since extract"):
        S.apply(changed, text, "hi", "csv")
    del changed["sections"][2]
    with pytest.raises(S.StringsError, match="not a unit of this pack"):
        S.apply(changed, text, "hi", "csv")
    with pytest.raises(S.StringsError, match="for de, not hi"):
        S.apply(pack, fill_xliff(S.extract(pack, "de", "xliff")), "hi", "xliff")


def _ws_copy(ws, tmp_path):  # noqa: F811
    d = tmp_path / "ws"
    shutil.copytree(ws, d)
    out = d / "outputs"
    out.mkdir(exist_ok=True)
    src = out / f"{SRC}.json"
    src.write_text(json.dumps(fixture(SRC), ensure_ascii=False), encoding="utf-8")
    return d, out, src


def test_translated_ids_must_match_source(ws, tmp_path):  # noqa: F811
    d, out, src = _ws_copy(ws, tmp_path)
    assert "strings written to" in run("strings", "extract", str(d), str(src), "--to", "csv")
    sf = out / f"{SRC}.strings.csv"
    sf.write_bytes(fill_csv(sf.read_text(encoding="utf-8-sig")).encode("utf-8"))
    assert "translation written to" in run("strings", "apply", str(d), str(src), str(sf), "--lang", "hi")
    tr = out / f"{SRC}-hi.json"
    assert run("check-pack", str(d), str(tr)).strip().endswith("cited IDs")
    t = json.loads(tr.read_text(encoding="utf-8"))
    t["sections"][1]["items"][1]["cites"] = ["FND-0003"]
    tr.write_text(json.dumps(t, ensure_ascii=False), encoding="utf-8")
    r = run_fail("check-pack", str(d), str(tr))
    assert f"differs from the source pack {SRC}" in r.stderr and "sections[1].items[1]" in r.stderr
    t["sections"][1]["items"][1]["cites"] = ["FND-0004"]
    t["sections"][1]["items"][1]["kind"] = "learning"
    t["sections"][1]["items"][1]["lesson"] = "x"
    t["sections"][0]["id"] = "using"
    tr.write_text(json.dumps(t, ensure_ascii=False), encoding="utf-8")
    r = run_fail("check-pack", str(d), str(tr))
    assert "sections: differs from the source pack" in r.stderr
    src.unlink()                                       # with no source beside it, only the pack itself is checked
    t["sections"][0]["id"] = "delivery"
    t["sections"][1]["items"][1]["kind"] = "card"
    tr.write_text(json.dumps(t, ensure_ascii=False), encoding="utf-8")
    run("check-pack", str(d), str(tr))


def test_translation_name_and_skill_checks(w):
    pack = fixture("dossier-F02")
    out = S.apply(pack, fill_csv(S.extract(pack, "hi", "csv")), "hi", "csv")
    assert out["pack"] == "dossier-F02-hi" and out["skill"] == "cluster-learning-dossier"
    assert pp.check_pack(out, w).problems == []
    bad = dict(out, pack="dossier-F02-xx")
    assert any(p.startswith("pack:") for p in pp.check_pack(bad, w).problems)
    nolang = {k: v for k, v in out.items() if k != "lang"}
    assert "lang: required in a translation (translation_of)" in pp.check_pack(nolang, w).problems
    self_ = dict(out, translation_of="Not A Name")
    assert any(p.startswith("translation_of:") for p in pp.check_pack(self_, w).problems)


def test_back_translation_warning_then_strict(w):
    pack = fixture(SRC)

    def blank(r):
        if r["id"].endswith("#back_translation"):
            r["target"] = ""
    out = S.apply(pack, fill_csv(S.extract(pack, "hi", "csv"), blank), "hi", "csv", allow_partial=True)
    msg = "item stop-and-ask-1 is safety-critical: add back_translation"
    r = pp.check_pack(out, w)
    assert r.problems == [] and any(msg in x for x in r.warnings)
    assert any(msg in x for x in pp.check_pack(out, w, strict=True).problems)
    # an English pack never gets the warning
    assert not any("back_translation" in x for x in pp.check_pack(pack, w).warnings)


def test_strings_extract_refuses_overwrite(ws, tmp_path):  # noqa: F811
    d, out, src = _ws_copy(ws, tmp_path)
    run("strings", "extract", str(d), str(src))
    xf = out / f"{SRC}.strings.xlf"
    before = xf.read_bytes()
    r = run_fail("strings", "extract", str(d), str(src))
    assert r.returncode == 1 and f"{xf} already exists and may hold your translator's work" in r.stderr
    assert xf.read_bytes() == before
    o = tmp_path / "mine.csv"
    run("strings", "extract", str(d), str(src), "--to", "csv", "--out", str(o), "--lang", "hi")
    assert o.read_text(encoding="utf-8-sig").startswith("id,source,target,note")
    r = run_fail("strings", "extract", str(d), str(src), "--to", "csv", "--out", str(o))
    assert r.returncode == 1 and "already exists" in r.stderr


def test_strings_apply_refuses_overwrite(ws, tmp_path):  # noqa: F811
    d, out, src = _ws_copy(ws, tmp_path)
    run("strings", "extract", str(d), str(src))
    xf = out / f"{SRC}.strings.xlf"
    xf.write_text(fill_xliff(xf.read_text(encoding="utf-8")), encoding="utf-8")
    run("strings", "apply", str(d), str(src), str(xf), "--lang", "hi")
    tr = out / f"{SRC}-hi.json"
    tr.write_text(tr.read_text(encoding="utf-8").replace("Stop and ask", "Stop and ask (reviewed)"), encoding="utf-8")
    before = tr.read_bytes()
    r = run_fail("strings", "apply", str(d), str(src), str(xf), "--lang", "hi")
    assert r.returncode == 1 and f"{tr} already exists and may hold a reviewed translation" in r.stderr
    assert tr.read_bytes() == before
    o = tmp_path / "t.json"
    run("strings", "apply", str(d), str(src), str(xf), "--lang", "hi", "--out", str(o))
    assert json.loads(o.read_text(encoding="utf-8"))["lang"] == "hi"


def test_strings_cli_usage_errors(ws, tmp_path):  # noqa: F811
    d, out, src = _ws_copy(ws, tmp_path)
    r = run_fail("strings", "apply", str(d), str(src), "--lang", "hi")
    assert "strings apply needs the strings file" in r.stderr
    r = run_fail("strings", "apply", str(d), str(src), str(tmp_path / "x.csv"))
    assert "strings apply needs --lang" in r.stderr
    r = run_fail("strings", "extract", str(d), str(src), str(tmp_path / "x.csv"))
    assert "strings extract takes no strings file" in r.stderr
    r = run_fail("strings", "extract", str(d), str(src), "--lang", "Hindi")
    assert "--lang must be a language tag" in r.stderr
    r = run_fail("strings", "apply", str(d), str(src), str(tmp_path / "missing.csv"), "--lang", "hi")
    assert "not found" in r.stderr
    nopack = tmp_path / "n.json"
    nopack.write_text("[]", encoding="utf-8")
    r = run_fail("strings", "extract", str(d), str(nopack))
    assert "is not a learning pack" in r.stderr
    bad = tmp_path / "bad.csv"
    bad.write_text("id,source,target,note\r\nnot-a-unit,a,b,\r\n", encoding="utf-8")
    r = run_fail("strings", "apply", str(d), str(src), str(bad), "--lang", "hi")
    assert r.returncode == 1 and "not a unit of this pack" in r.stderr and "nothing written" in r.stderr


def test_xliff_with_doctype_refused(ws, tmp_path):  # noqa: F811
    pack = fixture(SRC)
    good = fill_xliff(S.extract(pack, "hi", "xliff"))
    for evil in ('<!DOCTYPE xliff [<!ENTITY a "boom">]>\n', '<!doctype xliff>\n', '<!ENTITY a "b">\n'):
        text = evil + good                                   # good has no XML declaration (ET.tostring)
        with pytest.raises(S.StringsError, match=DOCTYPE_MSG):
            S.apply(pack, text, "hi", "xliff")
    d, out, src = _ws_copy(ws, tmp_path)
    xf = tmp_path / "evil.xlf"
    xf.write_text('<?xml version="1.0"?>\n<!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]>\n'
                  + good, encoding="utf-8")
    r = run_fail("strings", "apply", str(d), str(src), str(xf), "--lang", "hi")
    assert r.returncode == 1 and DOCTYPE_MSG in r.stderr
    assert not (out / f"{SRC}-hi.json").exists()
    with pytest.raises(S.StringsError, match="not a valid XLIFF"):
        S.apply(pack, "<xliff><file>", "hi", "xliff")


def test_csv_excel_habits():
    pack = fixture(SRC)
    text = fill_csv(S.extract(pack, "hi", "csv"))
    rows = list(csv.DictReader(io.StringIO(text)))
    buf = io.StringIO(newline="")
    cols = ["Comments", "note", "target", "id", "source"]                   # reordered, with an extra column
    wr = csv.DictWriter(buf, fieldnames=cols, lineterminator="\r\n")
    wr.writeheader()
    for r in rows:
        wr.writerow({"Comments": "checked", **r})
    excel = "﻿" + buf.getvalue().replace("\n", "\r\n").replace("\r\r\n", "\r\n")
    out = S.apply(pack, excel, "hi", "csv")
    assert strip_translation(out) == pack
    # a formula-led cell is neutralised on the way out and restored on the way in
    p2 = copy.deepcopy(pack)
    p2["sections"][0]["items"][1]["rows"][0][3] = "=no formula here"
    c = S.extract(p2, "hi", "csv")
    assert "'=no formula here" in c
    assert S.apply(p2, fill_csv(c), "hi", "csv")["sections"][0]["items"][1]["rows"][0][3] == "=no formula here"
    with pytest.raises(S.StringsError, match="needs the columns id and target"):
        S.apply(pack, "﻿key,value\r\na,b\r\n", "hi", "csv")


def test_translation_note_rendered(w):
    pack = fixture(SRC)
    out = S.apply(pack, fill_csv(S.extract(pack, "hi", "csv")), "hi", "csv")
    page = render_fixture(SRC, "html", pack=out)[0].data
    md = render_fixture(SRC, "md", pack=out)[0].data
    for text in (page, md):
        assert TRANSLATION_NOTE in text and STATUS_PHRASE in text and BRAND in text
    assert page.index('<p class="status">') < page.index(TRANSLATION_NOTE)
    assert md.index(STATUS_PHRASE) < md.index(TRANSLATION_NOTE)
    learner = render_fixture(SRC, "html", pack=out, view="learner")[0].data
    assert TRANSLATION_NOTE in learner
    # an English pack never shows it
    assert TRANSLATION_NOTE not in render_fixture(SRC, "html")[0].data
    assert TRANSLATION_NOTE not in render_fixture(SRC, "md")[0].data


def test_glossary_hi_complete():
    g = json.loads(GLOSSARY.read_text(encoding="utf-8"))
    assert "AI-drafted Hindi: check with a fluent speaker" in g["_about"]
    assert g["_review"] == {"hi": "AI-drafted Hindi: check with a fluent speaker"}
    for t in g["terms"]:
        if t["do_not_translate"]:
            assert t["translations"] == {}, t["term"]
        else:
            hi = t["translations"].get("hi")
            assert isinstance(hi, str) and hi.strip(), t["term"]
            assert re.search(r"[ऀ-ॿ]", hi), t["term"]       # Devanagari, not English left in place
