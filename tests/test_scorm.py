"""Phase 4, Task 21: the SCORM 1.2 package with a client-graded quiz (Ruling P4-11). Synthetic fixtures only."""
import io
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pytest

from test_pmlc import ws  # noqa: F401  (a module-scoped fixture)
from test_pack import fixture
from test_quiz import ESSAY, MULTI, SHORT, SINGLE, TF, opts, quiz_pack
from test_render import ctx_for
import pmlc  # noqa: E402

from pmlc_lib import BRAND, DRAFT_LABEL, STATUS_PHRASE  # noqa: E402
from pmlc_lib import render as R  # noqa: E402
from pmlc_lib.handling import effective_handling  # noqa: E402
from pmlc_lib.pack import schema as PS  # noqa: E402
from pmlc_lib.render import LEARNER_BANNER  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCORM_JS = ROOT / "skills" / "learnings-coach" / "scripts" / "dashboard_assets" / "scorm.js"
NODE = shutil.which("node")
CP = "{http://www.imsproject.org/xsd/imscp_rootv1p1p2}"
ADLCP = "{http://www.adlnet.org/xsd/adlcp_rootv1p2}"
SECRET = "Supervision owns the gap"          # an answer field: never visible to the learner
SINGLE2 = dict(type="single", question="Which fix is strongest?", options=opts(("Redesign the valve", True),
                                                                                 ("Retrain the crew", False)))
SHORT_KEY = "Quorvex level"                   # a short question's accepted answer: the key, never visible


@pytest.fixture(scope="module")
def w(ws):  # noqa: F811
    return pmlc.load_ws(ws)


def five_pack():
    """Five scored questions (single, multi, truefalse, short, single) and one reflect question."""
    p = quiz_pack(dict(SINGLE, answer=SECRET), MULTI, TF, dict(SHORT, options=opts((SHORT_KEY, True))), SINGLE2, ESSAY)
    return p


def package(w, pack, **kw):
    outs = R.render("scorm", ctx_for(w, pack, **kw))
    assert [o.name for o in outs] == [f"{pack['pack']}.scorm.zip"]
    return outs[0], zipfile.ZipFile(io.BytesIO(outs[0].data))


def visible(page: str) -> str:
    """The page without its script elements (the key travels there as data, P4-11)."""
    return re.sub(r"<script\b.*?</script>", "", page, flags=re.S | re.I)


def test_scorm_registered():
    assert R.FORMATS["scorm"].kind == "document"


def test_scorm_manifest(w):
    _, z = package(w, five_pack())
    names = set(z.namelist())
    assert {"imsmanifest.xml", "index.html", "scorm.js"} <= names
    root = ET.fromstring(z.read("imsmanifest.xml"))
    assert root.tag == f"{CP}manifest"
    md = root.find(f"{CP}metadata")
    assert md.find(f"{CP}schema").text == "ADL SCORM" and md.find(f"{CP}schemaversion").text == "1.2"
    orgs = root.find(f"{CP}organizations")
    org = orgs.findall(f"{CP}organization")
    assert len(org) == 1 and orgs.get("default") == org[0].get("identifier")
    items = org[0].findall(f"{CP}item")
    assert len(items) == 1
    assert items[0].find(f"{ADLCP}masteryscore").text == "80"
    res = root.find(f"{CP}resources").findall(f"{CP}resource")
    assert len(res) == 1 and items[0].get("identifierref") == res[0].get("identifier")
    assert res[0].get(f"{ADLCP}scormtype") == "sco" and res[0].get("href") == "index.html"
    listed = [f.get("href") for f in res[0].findall(f"{CP}file")]
    assert "index.html" in listed and "scorm.js" in listed
    for href in listed:
        assert href in names, href
    desc = " ".join(t for t in root.itertext())
    assert STATUS_PHRASE in desc and BRAND in desc and DRAFT_LABEL in desc        # P4-20: in the lom description
    assert z.read("scorm.js").decode("utf-8") == SCORM_JS.read_text(encoding="utf-8")


def test_scorm_is_reproducible(w, monkeypatch):
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1600905600")
    a, za = package(w, five_pack())
    b, _ = package(w, five_pack())
    assert a.data == b.data
    assert all(i.date_time == (2020, 9, 24, 0, 0, 0) for i in za.infolist())


def test_scorm_page_is_learner_view(w):
    o, z = package(w, five_pack())
    page = z.read("index.html").decode("utf-8")
    seen = visible(page)
    assert SECRET not in seen and SHORT_KEY not in seen
    assert "correct" not in seen.lower().replace("not correct", "")              # no correct-option marks
    assert STATUS_PHRASE in seen and BRAND in seen and DRAFT_LABEL in seen and LEARNER_BANNER in seen
    assert '<script src="scorm.js"></script>' in page
    # the quiz: one fieldset per scored choice question, a text box for the short one, a reflect box, unscored
    assert seen.count('type="radio"') == 2 + 2 + 2 and seen.count('type="checkbox"') == 3
    assert seen.count("<fieldset") == 5 and "<textarea" in seen
    assert "not scored" in seen.lower()
    # the key is data inside the page, as in any client-graded SCORM quiz
    key = json.loads(re.search(r'<script type="application/json" id="sm-key">(.*?)</script>', page, re.S).group(1))
    assert key["pass"] == 80 and len(key["questions"]) == 5
    assert key["questions"][0] == {"id": key["questions"][0]["id"], "type": "single", "correct": [0]}
    assert {"type": "short", "accept": [SHORT_KEY]}.items() <= key["questions"][3].items()
    # every visible text, and the key, goes through the name guard
    assert SHORT_KEY in o.guard_text and STATUS_PHRASE in o.guard_text


def test_scorm_ignores_view_flag(w):
    """SCORM always builds from the learner view and keeps its key, whatever --view says (P4-9)."""
    full, _ = package(w, five_pack())
    outs = R.render("scorm", ctx_for(w, five_pack(), view="learner"))
    assert [o.name for o in outs] == ["test-pack.scorm.zip"]
    assert outs[0].data == full.data


def test_scorm_approved_has_no_draft(w):
    p = five_pack()
    eh = dict(effective_handling(p, w), effective_status="approved")
    _, z = package(w, p, eh=eh)
    page = z.read("index.html").decode("utf-8")
    assert DRAFT_LABEL not in visible(page) and STATUS_PHRASE in page
    assert DRAFT_LABEL not in z.read("imsmanifest.xml").decode("utf-8")


def test_scorm_no_questions(w):
    _, z = package(w, fixture("frontline-learning-cards"))
    page = z.read("index.html").decode("utf-8")
    key = json.loads(re.search(r'id="sm-key">(.*?)</script>', page, re.S).group(1))
    assert key["questions"] == []
    assert 'id="sm-finish"' in page and "<fieldset" not in page
    man = z.read("imsmanifest.xml").decode("utf-8")
    assert "masteryscore" not in man                         # nothing to master: the LMS must not grade it


def test_scorm_table_renders_once(w):
    from test_pack import item, pack_with
    p = pack_with(item("table", columns=["Role", "Need"], rows=[["Fitters", "A test record"]]))
    _, z = package(w, p)
    page = z.read("index.html").decode("utf-8")
    assert page.count("<table>") == 1 and '<th scope="col">Role</th>' in page and "<td>Fitters</td>" in page


def test_scorm_escapes_and_key_cannot_close_script(w):
    p = quiz_pack(dict(SINGLE, question='Is </script><b>"x" & y</b> safe?',
                       options=opts(("</script>", True), ("<b>", False))))
    _, z = package(w, p)
    page = z.read("index.html").decode("utf-8")
    assert page.count("</script>") == 2                       # the key and scorm.js; none from the text
    assert "&lt;/script&gt;&lt;b&gt;&quot;x&quot; &amp; y" in page
    ET.fromstring(z.read("imsmanifest.xml"))


def test_scorm_all_fixtures_render(w):
    for name in ("all-kinds", "board-brief", "training-designer", "dossier-F02"):
        p = fixture(name)
        _, z = package(w, p)
        assert "index.html" in z.namelist()


def test_scorm_shared_copy(w, tmp_path):
    """A shared copy renders from the masked pack (ctx.pack); the CLI writes only <pack>.scorm.external.zip."""
    import argparse
    from pmlc_lib.handling import share_ctx, shared_copy
    pack = quiz_pack(dict(SINGLE, question="Who put the stem here?"))
    share = share_ctx(argparse.Namespace(names=None, orgs=None), w, "external")
    masked = shared_copy(pack, share, w)
    masked["sections"][0]["items"][0]["question"] = "MASKED STEM"
    ctx = ctx_for(shared_copy(w, share, w), masked, share=share, eh=effective_handling(pack, w))
    [o] = R.render("scorm", ctx)
    page = zipfile.ZipFile(io.BytesIO(o.data)).read("index.html").decode("utf-8")
    assert "Who put the stem here" not in page + o.guard_text and "MASKED STEM" in page and "MASKED STEM" in o.guard_text


def test_scorm_shared_copy_cli(tmp_path):
    from test_privacy import share_ws, sign, write_doc
    from test_layouts import _cli
    sws, orgs = share_ws(tmp_path)
    doc = quiz_pack(dict(SINGLE, question="Did the seal from the supplier pass its test?", cites=["FND-0001"]))
    p = sign(sws, write_doc(tmp_path, doc), "--classification", "external", "--legal-review", "cleared")
    out = tmp_path / "o"
    r = _cli("pack", str(sws), str(p), "--share", "external", "--orgs", str(orgs), "--out", str(out),
             "--embed", "summary", "--format", "scorm")
    assert r.returncode == 0, r.stderr
    assert sorted(x.name for x in out.iterdir()) == ["test-pack.scorm.external.zip"]
    z = zipfile.ZipFile(out / "test-pack.scorm.external.zip")
    for n in z.namelist():
        assert b"Bharat Seals" not in z.read(n), n
    page = z.read("index.html").decode("utf-8")
    assert STATUS_PHRASE in page and DRAFT_LABEL not in visible(page)
    assert "scorm written to" in r.stdout


def test_scorm_name_guard(w, ws, tmp_path):  # noqa: F811
    """The name guard reads the package's text: an invented name in a question stops the command."""
    import argparse
    from pmlc_lib.pack import command
    pack = quiz_pack(dict(SINGLE, options=opts(("Quillon Vantress", True), ("The fitter", False)),
                          lint_ok={"rule": "JC1", "reason": "an invented name, to test the name guard"}))
    assert PS.check_pack(pack, w).problems == []
    pj = tmp_path / "p.json"
    pj.write_text(json.dumps(pack), encoding="utf-8")
    names = tmp_path / "names.txt"
    names.write_text("Quillon Vantress\n", encoding="utf-8")
    ns = argparse.Namespace(ws=str(ws), pack=str(pj), cmd="pack", share=None, embed=None,
                            out=str(tmp_path / "o"), no_md=False, names=str(names), orgs=None, format=["scorm"],
                            view="full", layout=None, paper=None, base_url=None)
    with pytest.raises(SystemExit) as e:
        command.cmd_pack(ns)
    assert "refused: a listed name appears in the output" in str(e.value)
    assert not (tmp_path / "o").exists()


# ----------------------------------------------------------------------------- scorm.js against a mock API

def node(script: str) -> str:
    r = subprocess.run([NODE, "-e", script], capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr + r.stdout
    return r.stdout


MOCK = """
function mock() {
  const calls = [];
  const api = {calls,
    LMSInitialize(a) { calls.push(['LMSInitialize', a]); return 'true'; },
    LMSSetValue(k, v) { calls.push(['LMSSetValue', k, v]); return 'true'; },
    LMSGetValue(k) { calls.push(['LMSGetValue', k]); return ''; },
    LMSCommit(a) { calls.push(['LMSCommit', a]); return 'true'; },
    LMSFinish(a) { calls.push(['LMSFinish', a]); return 'true'; },
    LMSGetLastError() { return '0'; }};
  return api;
}
const count = (api, n) => api.calls.filter(c => c[0] === n).length;
const set = (api) => Object.fromEntries(api.calls.filter(c => c[0] === 'LMSSetValue').map(c => [c[1], c[2]]));
"""

KEY = ('[{"id":"a","type":"single","correct":[0]},{"id":"b","type":"multi","correct":[0,1]},'
       '{"id":"c","type":"truefalse","correct":[1]},{"id":"d","type":"short","accept":["L3","Supervision"]},'
       '{"id":"e","type":"single","correct":[1]}]')


@pytest.mark.skipif(not NODE, reason="node not installed")
def test_scorm_js_reports_score():
    node(f"""
const assert = require('assert');
const s = require({json.dumps(str(SCORM_JS))});
{MOCK}
const key = {KEY};
// 4 of 5 right: the multi misses one option
let r = s.score({{a: 0, b: [0], c: 1, d: '  supervision ', e: 1}}, key);
assert.deepStrictEqual(r, {{raw: 80, scored: 5}});
let api = mock();
assert.strictEqual(s.finish(api, r.raw, r.scored), 'passed');
assert.strictEqual(set(api)['cmi.core.score.raw'], '80');
assert.strictEqual(set(api)['cmi.core.score.min'], '0');
assert.strictEqual(set(api)['cmi.core.score.max'], '100');
assert.strictEqual(set(api)['cmi.core.lesson_status'], 'passed');
assert.strictEqual(count(api, 'LMSCommit'), 1);
assert.strictEqual(count(api, 'LMSFinish'), 1);
// 3 of 5: failed
r = s.score({{a: 0, b: [1, 0], c: 0, d: 'L2', e: 1}}, key);
assert.deepStrictEqual(r, {{raw: 60, scored: 5}});
api = mock();
assert.strictEqual(s.finish(api, r.raw, r.scored), 'failed');
assert.strictEqual(set(api)['cmi.core.score.raw'], '60');
assert.strictEqual(set(api)['cmi.core.lesson_status'], 'failed');
assert.strictEqual(count(api, 'LMSCommit'), 1);
assert.strictEqual(count(api, 'LMSFinish'), 1);
// no scored questions: completed, and no score
r = s.score({{}}, []);
assert.deepStrictEqual(r, {{raw: 0, scored: 0}});
api = mock();
assert.strictEqual(s.finish(api, r.raw, r.scored), 'completed');
assert.strictEqual(set(api)['cmi.core.lesson_status'], 'completed');
assert.ok(!('cmi.core.score.raw' in set(api)));
assert.strictEqual(count(api, 'LMSCommit'), 1);
assert.strictEqual(count(api, 'LMSFinish'), 1);
// unanswered and malformed answers count as wrong, never throw; 2 of 3 rounds down (66), so 79.x never passes
assert.deepStrictEqual(s.score({{a: 'x', b: 'nope'}}, key), {{raw: 0, scored: 5}});
assert.deepStrictEqual(s.score({{a: 0, b: [0, 1]}}, key.slice(0, 3)), {{raw: 66, scored: 3}});
assert.deepStrictEqual(s.score(null, key.slice(0, 1)), {{raw: 0, scored: 1}});
// with no LMS the status is still worked out
assert.strictEqual(s.finish(null, 90, 2), 'passed');
console.log('ok');
""")


@pytest.mark.skipif(not NODE, reason="node not installed")
def test_scorm_js_find_api():
    node(f"""
const assert = require('assert');
const s = require({json.dumps(str(SCORM_JS))});
const api = {{LMSInitialize() {{}}}};
const top = {{API: api}}; top.parent = top;
const mid = {{parent: top}};
const win = {{parent: mid}};
assert.strictEqual(s.findAPI(win), api);
const lone = {{}}; lone.parent = lone;
assert.strictEqual(s.findAPI(lone), null);
const opened = {{parent: null, opener: win}};
assert.strictEqual(s.findAPI(opened), api);
// a deep chain stops searching after 7 levels
let w = {{API: api}}; w.parent = w;
for (let i = 0; i < 9; i++) w = {{parent: w}};
w.opener = null;
assert.strictEqual(s.findAPI(w), null);
// a cross-origin parent that throws is skipped, never fatal
const hostile = {{}}; Object.defineProperty(hostile, 'API', {{get() {{ throw new Error('blocked'); }}}});
hostile.parent = hostile;
assert.strictEqual(s.findAPI({{parent: hostile}}), null);
assert.strictEqual(s.findAPI(null), null);
console.log('ok');
""")


@pytest.mark.skipif(not NODE, reason="node not installed")
def test_scorm_page_runs_against_a_mock_lms(w, tmp_path):
    """index.html in jsdom with a mock API on the parent: answering 4 of 5 and submitting reports passed, once."""
    from test_a11y_js import JS_DIR, need_node_modules
    need_node_modules()
    _, z = package(w, five_pack())
    z.extractall(tmp_path / "pkg")
    page = tmp_path / "pkg" / "index.html"
    out = node(f"""
const assert = require('assert');
const fs = require('fs');
const {{ JSDOM }} = require({json.dumps(str(JS_DIR / "node_modules" / "jsdom"))});
{MOCK}
const api = mock();
let html = fs.readFileSync({json.dumps(str(page))}, 'utf8');
html = html.replace('<script src="scorm.js"></script>',
  '<script>' + fs.readFileSync({json.dumps(str(tmp_path / "pkg" / "scorm.js"))}, 'utf8') + '</script>');
const dom = new JSDOM(html, {{runScripts: 'dangerously', beforeParse(win) {{ win.API = api; }}}});
dom.window.addEventListener('load', () => {{
const d = dom.window.document;
const key = JSON.parse(d.getElementById('sm-key').textContent).questions;
assert.strictEqual(count(api, 'LMSInitialize'), 1);
key.forEach((q, i) => {{
  const box = d.querySelector('[data-q="' + q.id + '"]');
  if (q.type === 'short') {{ box.querySelector('input').value = i === 3 ? 'wrong' : q.accept[0]; return; }}
  q.correct.forEach(n => {{ box.querySelectorAll('input')[n].checked = true; }});
}});
d.getElementById('sm-submit').click();
d.getElementById('sm-submit').click();             // a second click records nothing more
assert.strictEqual(set(api)['cmi.core.lesson_status'], 'passed');
assert.strictEqual(set(api)['cmi.core.score.raw'], '80');
assert.strictEqual(count(api, 'LMSFinish'), 1);
assert.ok(/80/.test(d.getElementById('sm-result').textContent));
console.log('ok');
}});
""")
    assert out.strip().splitlines()[-1] == "ok", out          # an assertion inside a jsdom listener does not exit 1


@pytest.mark.skipif(not NODE, reason="node not installed")
def test_scorm_quiz_page_axe(w, tmp_path):
    """The quiz form itself (every question type and a reflect box) has no serious or critical axe violation."""
    from test_a11y_js import axe, blocking
    _, z = package(w, five_pack())
    z.extractall(tmp_path / "pkg")
    bad = blocking(axe(tmp_path / "pkg" / "index.html"))
    assert bad == [], json.dumps(bad, indent=1)
