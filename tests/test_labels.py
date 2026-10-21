"""Phase 4, Task 2: UI labels as data, the pack's `lang` and `dir`, the Hindi labels and a right-to-left test locale
(Ruling P4-15, owner decision OD4-1, L4-14, L1-08). Synthetic fixtures only."""
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from test_pmlc import ws  # noqa: F401  (ws is a module-scoped fixture)
from test_pack import FIX, HTML_GOLDEN, fixture, pack_fixtures, render_fixture
import pmlc  # noqa: E402
import pmlc_pack as pp  # noqa: E402

from pmlc_lib.render import labels as RL  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "skills" / "learnings-coach" / "scripts"
LABELS = ROOT / "skills" / "learnings-coach" / "references" / "labels"
TEST_LABELS = Path(__file__).resolve().parent / "fixtures" / "labels"
PACK_JS = ENGINE / "dashboard_assets" / "pack.js"
NODE = shutil.which("node")
OLD_LITERALS = ("Bottom line", "Coverage", "What happened", "Hold point", "Leading indicator", "Evidence trail")
HI_REVIEW = "AI-drafted Hindi: check with a fluent speaker"


def _read(name):
    return json.loads((LABELS / name).read_text(encoding="utf-8"))


def _payload(page):
    m = re.search(r'<script type="application/json" id="pmlc-pack-data">(.*?)</script>', page, re.S)
    assert m, "no pmlc-pack-data block"
    return json.loads(m.group(1))


def _placeholders(s):
    return set(re.findall(r"\{[a-z_]*\}", s))


@pytest.fixture(scope="module")
def w(ws):  # noqa: F811
    return pmlc.load_ws(ws)


def test_english_output_unchanged():
    table = json.loads(HTML_GOLDEN.read_text(encoding="utf-8"))
    for name in pack_fixtures() + ["all-kinds"]:
        page = render_fixture(name, "html")[0].data
        assert hashlib.sha256(page.encode("utf-8")).hexdigest() == table[name], name
        assert "labels" not in _payload(page), name
        assert page.startswith('<!doctype html><html lang="en"><head>'), name
    for name in pack_fixtures():
        md = render_fixture(name, "md")[0].data
        assert md == (FIX / f"{name}.md").read_text(encoding="utf-8"), name


def test_hi_has_every_key():
    en, hi = _read("en.json"), _read("hi.json")
    assert set(hi) == set(en)
    for k, v in en.items():
        if isinstance(v, str):
            assert _placeholders(v) <= _placeholders(hi[k]), k
    assert hi["_review"] == HI_REVIEW
    assert hi["_dir"] == "ltr" and hi["_language"]
    assert en["_review"] is None
    assert any(k.startswith("ui.") for k in en) and all(isinstance(v, str) and v for k, v in hi.items()
                                                         if not k.startswith("_"))
    # glossary do_not_translate terms stay as written
    assert "ProbeMatrix" in hi["ui.js.ai_justification"]


def test_hindi_pack_renders_hindi_labels():
    hi = _read("hi.json")
    pack = dict(fixture("frontline-learning-cards"), lang="hi")
    page = render_fixture("frontline-learning-cards", "html", pack=pack)[0].data
    assert page.startswith('<!doctype html><html lang="hi" dir="ltr"><head>')
    for k in ("ui.bottom_line", "ui.evidence_trail", "ui.coverage", "f.what_happened", "f.warning_signs"):
        assert hi[k] in page, k
    for lit in ("<h2>Bottom line</h2>", "<h2>Evidence trail</h2>", ">What happened<"):
        assert lit not in page, lit
    assert pmlc.STATUS_PHRASE in page and pmlc.BRAND in page
    data = _payload(page)
    assert data["labels"]["ui.js.finding"] == hi["ui.js.finding"]
    md = render_fixture("frontline-learning-cards", "md", pack=pack)[0].data
    assert f"## {hi['ui.bottom_line']}" in md and "## Bottom line" not in md
    assert f"**{hi['f.what_happened']}:**" in md
    assert pmlc.BRAND in md


def test_rtl_fixture_locale(monkeypatch):
    ar = json.loads((TEST_LABELS / "ar.json").read_text(encoding="utf-8"))
    assert ar["_dir"] == "rtl" and len([k for k in ar if not k.startswith("_")]) == 3
    monkeypatch.setenv("PMLC_LABELS_DIR", str(TEST_LABELS))
    en = RL.load_labels("en")
    pack = dict(fixture("frontline-learning-cards"), lang="ar")
    page = render_fixture("frontline-learning-cards", "html", pack=pack)[0].data
    assert page.startswith('<!doctype html><html lang="ar" dir="rtl"><head>')
    assert f"<h2>{ar['ui.bottom_line']}</h2>" in page
    assert f"<h2>{en['ui.evidence_trail']}</h2>" in page            # not in ar.json: English
    assert _payload(page)["labels"]["ui.js.finding"] == en["ui.js.finding"]
    # an explicit dir on the pack wins over the locale's
    page = render_fixture("frontline-learning-cards", "html", pack=dict(pack, dir="ltr"))[0].data
    assert page.startswith('<html lang="ar" dir="ltr">', len("<!doctype html>"))


def test_lang_validated(w):
    base = fixture("frontline-learning-cards")
    assert pp.check_pack(dict(base, lang="hi", dir="ltr"), w).problems == []
    assert pp.check_pack(dict(base, lang="pt-BR"), w).problems == []
    probs = pp.check_pack(dict(base, lang="english"), w).problems
    assert any(p.startswith("lang:") for p in probs), probs
    probs = pp.check_pack(dict(base, dir="up"), w).problems
    assert any(p.startswith("dir:") for p in probs), probs
    probs = pp.check_pack(dict(base, lang=7), w).problems
    assert any(p.startswith("lang:") for p in probs), probs


def test_no_english_ui_literal_left():
    en_values = set(_read("en.json").values())
    for f in ("pack/html.py", "pack/markdown.py"):
        src = (ENGINE / "pmlc_lib" / f).read_text(encoding="utf-8")
        for lit in OLD_LITERALS:
            assert lit not in src, f"{f}: {lit!r} is a label now (references/labels/en.json)"
    for lit in OLD_LITERALS:
        assert lit in en_values, lit


def test_event_when_and_lint_notes_in_hindi():
    hi = RL.load_labels("hi")
    assert pp.event_when({"date": "2019-03"}, "2020-09-24", hi) == "2019-03 (" + hi["ui.months_before"].format(n=18) + ")"
    assert pp.event_when({"date": "2015"}, "2020-09-24", hi).startswith(hi["ui.circa"].format(year=2015))
    note = pp.lint_ok_notes({"lint_ok": {"rule": "JC3", "reason": "quoted"}}, hi)
    assert note == [hi["ui.lint_ok"].format(rule="JC3", reason="quoted")]


@pytest.mark.skipif(not NODE, reason="node not installed")
def test_pack_js_uses_payload_labels():
    script = f"""
const assert = require('assert');
const p = require({json.dumps(str(PACK_JS))});
const f = {{"FND-0001": {{label: "Seal", level: 1, rating: 4}}}};
assert.strictEqual(p.recordRows("FND-0001", {{findings: f}})[0][0], "Finding");
const L = {{"ui.js.finding": "निष्कर्ष", "ui.js.rating": "रेटिंग"}};
const rows = p.recordRows("FND-0001", {{findings: f, labels: L}});
assert.strictEqual(rows[0][0], "निष्कर्ष");
assert.ok(rows.some(function (r) {{ return r[0] === "रेटिंग"; }}));
assert.ok(rows.some(function (r) {{ return r[0] === "Level"; }}));        // a key the labels lack: English default
assert.strictEqual(p.learningLabel("LR-01"), "Learning LR-01");
assert.strictEqual(p.learningLabel("LR-01", {{"ui.learning_chip": "सीख {{id}}"}}), "सीख LR-01");
const ev = {{"EVD-001": {{description: "Log", type: "Doc", links: [{{code: "FND-0001", relevance: "high"}}]}}}};
assert.strictEqual(p.recordRows("EVD-001", {{evidence: ev, labels: {{"ui.js.linked_to": "{{code}} से जुड़ा"}}}})[2][0],
                   "FND-0001 से जुड़ा");
"""
    r = subprocess.run([NODE, "-e", script], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr + r.stdout
