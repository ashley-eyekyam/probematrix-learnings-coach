"""Unit tests for the learning-pack page's pure JavaScript functions (run under Node if installed)."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "skills" / "learnings-coach" / "scripts" / "dashboard_assets"
PACK_JS = ASSETS / "pack.js"
PACK_CSS = ASSETS / "pack.css"
NODE = shutil.which("node")


def node(script: str) -> str:
    r = subprocess.run([NODE, "-e", script], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr + r.stdout
    return r.stdout


@pytest.mark.skipif(not NODE, reason="node not installed")
def test_pack_js_pure_functions():
    node(f"""
const assert = require('assert');
const p = require({json.dumps(str(PACK_JS))});
assert.deepStrictEqual(p.parseHash('#s/before-work'), {{kind:'s', id:'before-work'}});
assert.deepStrictEqual(p.parseHash('#i/before-work-2'), {{kind:'i', id:'before-work-2'}});
assert.strictEqual(p.parseHash('#x/a'), null);
assert.strictEqual(p.parseHash('#s/<img>'), null);
assert.strictEqual(p.parseHash('#s/%E0'), null);
assert.strictEqual(p.parseHash(''), null);
assert.strictEqual(p.parseHash(undefined), null);
assert.ok(p.matches('Leak-test record attached', 'LEAK record'));
assert.ok(!p.matches('Leak-test record attached', 'leak permit'));
assert.ok(p.matches('anything', '   '));
assert.ok(p.matches(null, ''));
assert.strictEqual(p.tickKey('supervisor-coach', '2024-03-20-pump-fire'), 'pmlc-pack:supervisor-coach:2024-03-20-pump-fire');
const mem = {{s:{{}}, getItem(k){{return k in this.s ? this.s[k] : null;}}, setItem(k,v){{this.s[k]=String(v);}}}};
assert.deepStrictEqual(p.readTicks(mem, 'k'), {{}});
assert.ok(p.writeTicks(mem, 'k', {{'leak-test':1}}));
assert.deepStrictEqual(p.readTicks(mem, 'k'), {{'leak-test':1}});
mem.s.k = 'not json';
assert.deepStrictEqual(p.readTicks(mem, 'k'), {{}});
mem.s.k = '[1]';
assert.deepStrictEqual(p.readTicks(mem, 'k'), {{}});
const boom = {{getItem(){{throw new Error('denied');}}, setItem(){{throw new Error('denied');}}}};
assert.deepStrictEqual(p.readTicks(boom, 'k'), {{}});
assert.strictEqual(p.writeTicks(boom, 'k', {{}}), false);
const D = {{findings: {{'FND-0001': {{id:'FND-0001', label:'Pump restarted', level:1, level_name:'Unsafe Acts', rating:3,
  roles:['Pump Technician'], clusters:{{F:['F02'], T:['T1'], R:['actor']}}, votes:[{{vote:'downgrade', reason:'dup'}}],
  evidence:['EVD-0001'], justification:'no test'}}}},
  evidence: {{'EVD-0001': {{id:'EVD-0001', type:'document', description:'Work order',
  links:[{{code:'AB 1.1', relevance:'Shows no test', reference:'no leak test recorded'}}]}}}}}};
const fr = p.recordRows('FND-0001', D);
assert.deepStrictEqual(fr[0], ['Finding', 'Pump restarted']);
assert.ok(fr.some(r => r[0] === 'Level' && r[1] === 'L1 Unsafe Acts'));
assert.ok(fr.some(r => r[0] === 'Learning clusters' && r[1] === 'F02 · T1 · actor'));
assert.ok(fr.some(r => r[0] === 'Reviewer votes' && r[1] === 'downgrade: dup'));
assert.ok(!fr.some(r => r[0] === 'Causal explanation'));
assert.deepStrictEqual(p.recordRows('EVD-0001', D),
  [['Evidence','Work order'],['Type','document'],['Linked to AB 1.1','Shows no test: no leak test recorded']]);
assert.strictEqual(p.recordRows('FND-9999', D), null);
assert.strictEqual(p.recordRows('FND-0001', null), null);
""")


def test_pack_assets_are_inline_safe():
    js, css = PACK_JS.read_text(encoding="utf-8"), PACK_CSS.read_text(encoding="utf-8")
    assert "</script" not in js.lower() and "</style" not in css.lower()
    for s in (js, css):
        assert "http://" not in s and "https://" not in s
    assert "function init()" in js and "localStorage" in js
    assert ".rail{" in css and "@media print" in css and ".tablewrap{" in css
    assert "appearance:none" in css                       # print shows empty tick boxes
    assert "scroll-margin-top" in css                     # deep links land below the sticky toolbar
    assert "repeat(auto-fit," in css and "repeat(auto-fill," not in css     # no empty card columns on wide screens
    assert ".tablewrap td.cites-cell{min-width:" in css                    # citations cannot squeeze text columns


@pytest.mark.skipif(not NODE, reason="node not installed")
def test_pack_js_loads_without_dom():
    out = node(f"const p = require({json.dumps(str(PACK_JS))}); console.log(Object.keys(p).sort().join(','));")
    assert out.strip() == "isTicked,matches,parseHash,readTicks,recordRows,recordView,tickKey,writeTicks"


@pytest.mark.skipif(not NODE, reason="node not installed")
def test_pack_js_review_fixes():
    node(f"""
const assert = require('assert');
const p = require({json.dumps(str(PACK_JS))});
assert.strictEqual(p.isTicked({{}}, 'constructor'), false);                 // review 9
assert.strictEqual(p.isTicked({{'leak-test':1}}, 'leak-test'), true);
assert.strictEqual(p.isTicked({{'leak-test':0}}, 'leak-test'), false);
""")
    js = PACK_JS.read_text(encoding="utf-8")
    assert 'querySelectorAll("main details:not(.rail)")' in js                   # review 3
    assert 'closest("[hidden]")' in js                                            # review 4


@pytest.mark.skipif(not NODE, reason="node not installed")
def test_pack_js_provenance_labels():
    node(f"""
const assert = require('assert');
const p = require({json.dumps(str(PACK_JS))});
const brand = {{ai_justification_label:'AI justification (ProbeMatrix)', ai_chip:'AI-drafted, not human-edited',
  export_banner:"This is the investigation's AI-drafted wording, shown as evidence; it is not the coach's learning."}};
const D = {{brand: brand, findings: {{
  'FND-0001': {{id:'FND-0001', label:'Pump restarted', justification:'no test', user_edited:''}},
  'FND-0002': {{id:'FND-0002', label:'Seal', justification:'local buy', user_edited:'No'}},
  'FND-0003': {{id:'FND-0003', label:'Edited', justification:'checked', user_edited:'Yes'}}}},
  evidence: {{'EVD-0001': {{id:'EVD-0001', type:'document', description:'Work order'}}}}}};
const v = p.recordView('FND-0001', D);
assert.strictEqual(v.banner, brand.export_banner);
assert.strictEqual(v.chip, brand.ai_chip);
assert.ok(v.rows.some(r => r[0] === brand.ai_justification_label && r[1] === 'no test'));
assert.ok(!v.rows.some(r => r[0] === 'Justification'));
assert.strictEqual(p.recordView('FND-0002', D).chip, brand.ai_chip);
assert.strictEqual(p.recordView('FND-0003', D).chip, null);
D.findings['FND-0003'].user_edited = 'false';                     // only yes, y, true or 1 count as edited (X26)
assert.strictEqual(p.recordView('FND-0003', D).chip, brand.ai_chip);
D.findings['FND-0003'].user_edited = 'Yes';
assert.strictEqual(p.recordView('FND-0003', D).banner, brand.export_banner);
const e = p.recordView('EVD-0001', D);
assert.strictEqual(e.banner, null);
assert.strictEqual(e.chip, null);
assert.strictEqual(p.recordView('FND-9999', D), null);
""")


@pytest.mark.skipif(not NODE, reason="node not installed")
def test_pack_js_label_only_records():
    """--embed cited: uncovered and excluded findings travel as {id, label, rating}; summary drops quotes."""
    node(f"""
const assert = require('assert');
const p = require({json.dumps(str(PACK_JS))});
const brand = {{ai_chip:'AI-drafted, not human-edited', export_banner:'banner'}};
const D = {{brand: brand, findings: {{
  'FND-0003': {{id:'FND-0003', label:'Seals bought locally', rating:4}},
  'FND-0004': {{id:'FND-0004', label:'Alarm display only', rating:null}}}},
  evidence: {{'EVD-0001': {{id:'EVD-0001', type:'document', links:[{{code:'AB 1.1', relevance:'Shows no test'}}]}}}}}};
assert.deepStrictEqual(p.recordRows('FND-0003', D),
  [['Finding','Seals bought locally'],['Rating','4'],['Detail','Only the label and rating are embedded in this page.']]);
assert.deepStrictEqual(p.recordRows('FND-0004', D),
  [['Finding','Alarm display only'],['Detail','Only the label and rating are embedded in this page.']]);
const v = p.recordView('FND-0003', D);
assert.strictEqual(v.chip, null);                 // user_edited is not embedded: claim nothing
assert.strictEqual(v.banner, 'banner');           // the label is still the investigation's wording
assert.deepStrictEqual(p.recordRows('EVD-0001', D), [['Type','document'],['Linked to AB 1.1','Shows no test']]);
""")
