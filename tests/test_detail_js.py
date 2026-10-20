"""Unit tests for the detailed-register tab's pure JavaScript functions (run under Node if installed)."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "skills" / "learnings-coach" / "scripts" / "dashboard_assets"
DETAIL_JS = ASSETS / "detail.js"
DETAIL_CSS = ASSETS / "detail.css"
NODE = shutil.which("node")


def node(script: str) -> str:
    r = subprocess.run([NODE, "-e", script], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr + r.stdout
    return r.stdout


@pytest.mark.skipif(not NODE, reason="node not installed")
def test_detail_js_pure_functions():
    node(f"""
const assert = require('assert');
const d = require({json.dumps(str(DETAIL_JS))});
assert.deepStrictEqual(d.tokenize('see EVD-0001 and FND-7C3A90E1; LR-03.'),
  [{{text:'see '}},{{id:'EVD-0001'}},{{text:' and '}},{{id:'FND-7C3A90E1'}},{{text:'; '}},{{id:'LR-03'}},{{text:'.'}}]);
assert.deepStrictEqual(d.tokenize('LR-1000'), [{{id:'LR-1000'}}]);
assert.deepStrictEqual(d.tokenize(''), []);
assert.deepStrictEqual(d.tokenize(null), []);
assert.deepStrictEqual(d.parseHash('#detail/LR-03'), {{tab:'detail', id:'LR-03'}});
assert.deepStrictEqual(d.parseHash('#detail'), {{tab:'detail', id:null}});
assert.deepStrictEqual(d.parseHash(''), {{tab:'overview', id:null}});
assert.deepStrictEqual(d.parseHash('#overview'), {{tab:'overview', id:null}});
assert.deepStrictEqual(d.parseHash('#detail/<img>'), {{tab:'detail', id:null}});
assert.deepStrictEqual(d.parseHash('#detail/%E0'), {{tab:'detail', id:null}});
const data = {{
  entries: [
    {{lr_id:'LR-02', priority:2, title:'B', tier_messages:{{T5:'board msg'}}, finding_ids:['FND-B'], lesson:'gauge drift'}},
    {{lr_id:'LR-01', priority:1, title:'A', tier_messages:{{T1:'do x', T2:'check y'}}, finding_ids:['FND-A','FND-B','FND-X'],
      evidence_ids:['EVD-1'], lesson:'isolate early'}}],
  derived: {{'LR-01':{{level:'L4 Organisational Influences', entity:'F09b', hoc:['engineering','administrative'], strongest:'engineering'}},
             'LR-02':{{level:'L2 Preconditions', entity:'F04', hoc:['training'], strongest:'training'}}}},
  findings: {{'FND-A':{{id:'FND-A', rating:3, level:2, evidence:['EVD-1'], justification:'valve was manual'}},
              'FND-B':{{id:'FND-B', rating:5, level:4, evidence:[]}}}},
  evidence: {{'EVD-1':{{id:'EVD-1', description:'DCS log quote'}}}},
  tier_labels: {{T1:'Frontline', T2:'Supervisors', T5:'Corporate / board'}}
}};
const e2 = data.entries[0], e1 = data.entries[1];
assert.deepStrictEqual(d.sortEntries(data.entries).map(e => e.lr_id), ['LR-01','LR-02']);
assert.deepStrictEqual(d.sortFindings(['FND-X','FND-A','FND-B'], data.findings), ['FND-B','FND-A','FND-X']);
assert.deepStrictEqual(d.lensesFor(data).map(l => l.value), ['all','T1','T2','T5','investigator','auditor']);
assert.strictEqual(d.lensesFor(data)[1].label, 'T1 Frontline');
assert.deepStrictEqual(d.evidenceIdsFor(e1, data), ['EVD-1']);
assert.ok(d.matches(e1, data, {{}}));
assert.ok(d.matches(e1, data, {{tier:'T2'}}) && !d.matches(e2, data, {{tier:'T2'}}));
assert.ok(d.matches(e1, data, {{priority:'1'}}) && !d.matches(e2, data, {{priority:'1'}}));
assert.ok(d.matches(e1, data, {{owner:'F09b', level:'L4 Organisational Influences', hoc:'engineering'}}));
assert.ok(!d.matches(e1, data, {{hoc:'training'}}));
assert.ok(d.matches(e1, data, {{q:'VALVE WAS'}}));
assert.ok(d.matches(e1, data, {{q:'dcs log'}}));
assert.ok(!d.matches(e2, data, {{q:'dcs log'}}));
assert.ok(d.matches(e2, data, {{q:'  '}}));
assert.ok(!d.matches(e1, data, {{q:'justification'}}));   // field names are not searchable text
const t2 = d.lensSpec('T2');
assert.strictEqual(t2.tier, 'T2');
assert.deepStrictEqual(t2.order.slice(0, 4), ['lesson','context','warn','recs']);
assert.ok(d.lensSpec('T5').order.includes('risk'));
const inv = d.lensSpec('investigator');
assert.deepStrictEqual(inv.open.slice().sort(), inv.order.slice().sort());
assert.strictEqual(d.lensSpec('auditor').order[1], 'recs');
assert.strictEqual(d.lensSpec('all').tier, null);
assert.strictEqual(d.lensSpec('').tier, null);
assert.deepStrictEqual(d.summarise([e1, e2], data), {{learnings:2, p1:1, recs:3, strongPct:33, findings:2, evidence:1}});
assert.deepStrictEqual(d.summarise([], data), {{learnings:0, p1:0, recs:0, strongPct:0, findings:0, evidence:0}});
""")


def test_assets_are_inline_safe():
    js, css = DETAIL_JS.read_text(encoding="utf-8"), DETAIL_CSS.read_text(encoding="utf-8")
    assert "</script" not in js.lower() and "</style" not in css.lower()
    for s in (js, css):
        assert "http://" not in s and "https://" not in s
    assert "function init()" in js


@pytest.mark.skipif(not NODE, reason="node not installed")
def test_detail_js_loads_without_dom():
    out = node(f"const d = require({json.dumps(str(DETAIL_JS))}); console.log(Object.keys(d).sort().join(','));")
    assert out.strip() == "evidenceIdsFor,lensSpec,lensesFor,matches,parseHash,provenance,sortEntries,sortFindings,statusLead,summarise,tokenize"


@pytest.mark.skipif(not NODE, reason="node not installed")
def test_detail_js_provenance_labels():
    node(f"""
const assert = require('assert');
const d = require({json.dumps(str(DETAIL_JS))});
const brand = {{ai_justification_label:'AI justification (ProbeMatrix)', ai_chip:'AI-drafted, not human-edited',
  export_banner:"This is the investigation's AI-drafted wording, shown as evidence; it is not the coach's learning."}};
const p = d.provenance({{id:'FND-A', justification:'valve was manual', user_edited:''}}, brand);
assert.deepStrictEqual(p, {{banner: brand.export_banner, chip: brand.ai_chip, label: brand.ai_justification_label}});
assert.strictEqual(d.provenance({{user_edited:'no'}}, brand).chip, brand.ai_chip);
assert.strictEqual(d.provenance({{}}, brand).chip, brand.ai_chip);
assert.strictEqual(d.provenance({{user_edited:'Yes'}}, brand).chip, null);
for (const ue of ['N', 'false', 'maybe']) assert.strictEqual(d.provenance({{user_edited: ue}}, brand).chip, brand.ai_chip);
for (const ue of ['y', 'TRUE', '1']) assert.strictEqual(d.provenance({{user_edited: ue}}, brand).chip, null);
assert.strictEqual(d.provenance({{user_edited:''}}, undefined).label, 'Justification');
""")


@pytest.mark.skipif(not NODE, reason="node not installed")
def test_detail_js_label_only_records():
    node(f"""
const assert = require('assert');
const d = require({json.dumps(str(DETAIL_JS))});
const brand = {{ai_chip:'AI-drafted, not human-edited', export_banner:'banner'}};
assert.strictEqual(d.provenance({{id:'FND-0003', label:'Seals', rating:4}}, brand).chip, null);
assert.strictEqual(d.provenance({{id:'FND-0003', label:'Seals', rating:4, short:'x'}}, brand).chip, brand.ai_chip);
assert.deepStrictEqual(d.sortFindings(['FND-A', 'FND-B'], {{'FND-A': {{id:'FND-A', label:'a', rating:2}},
  'FND-B': {{id:'FND-B', label:'b', rating:4}}}}), ['FND-B', 'FND-A']);
""")
    assert "Only the label and rating are embedded in this page." in DETAIL_JS.read_text(encoding="utf-8")


@pytest.mark.skipif(not NODE, reason="node not installed")
def test_detail_banner_lead_only_with_status_phrase():
    node(f"""
const assert = require('assert');
const d = require({json.dumps(str(DETAIL_JS))});
assert.strictEqual(d.statusLead({{status_phrase: 'Learning purposes: not a statutory document'}}),
  'Learning purposes: not a statutory document. ');
for (const b of [{{}}, {{status_phrase: ''}}, null, undefined]) assert.strictEqual(d.statusLead(b), '');
""")
