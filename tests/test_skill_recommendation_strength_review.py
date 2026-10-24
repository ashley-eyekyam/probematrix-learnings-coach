"""Phase 5 Task 23: the recommendation-strength-review skill. Its manifest, profile, workflow step, evals and hub row
follow the plan, and its Hazira golden reviews the register and the 9M analysis (Task 22's nine-m-map.json) as a set:
it pastes the engine's rec-review tables unchanged (24 stronger, 15 intermediate, 5 weaker; one recommendation per M),
says which set it reviewed, writes direction-of-change items with no owner or date (D7) and passes check-pack --strict
--register and check-language with no errors."""
import json
import shutil
import subprocess
import sys

import pytest

from test_pmlc import PMLC, ROOT, run

SKILL = "recommendation-strength-review"
REFS = ROOT / "skills" / "learnings-coach" / "references"
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
OUTPUTS = SAMPLE / "outputs"
GOLDEN = OUTPUTS / f"{SKILL}.json"
REGISTER = OUTPUTS / "learnings-register.json"
NINE_M_MAP = OUTPUTS / "nine-m-map.json"
NINE_M_PACK = OUTPUTS / "nine-m-analysis.json"
BOTH = "the learnings register and the 9M analysis"


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def skill_md() -> str:
    return (ROOT / "skills" / SKILL / "SKILL.md").read_text(encoding="utf-8")


def _items(pack, sec):
    return [it for s in pack["sections"] if s["id"] == sec for it in s["items"]]


def test_manifest():
    m = load(ROOT / "skills" / SKILL / "skill.json")
    assert (m["kind"], m["audiences"], m["interactive"]) == ("analysis", [], False)
    assert m["requires"] == ["workspace", "register"] and m["optional_inputs"] == ["nine-m-map"]
    assert m["produces"] == {"pack": SKILL, "files": []} and m["formats"] == ["docx"]
    assert (m["share_default"], m["embed_default"], m["since"]) == ("internal", "cited", "2.0.0")


def test_profile():
    p = load(REFS / "pack-profiles.json")[SKILL]
    assert [(s["id"], s["kinds"], s["min"], s["max"]) for s in p["sections"]] == [
        ("reviewed-set", ["para"], 1, 1), ("strength", ["table"], 1, 1), ("spread", ["table"], 0, 1),
        ("loops", ["para"], 1, 3), ("directions", ["recommendation"], 1, 10), ("smart", ["table"], 0, 1)]
    assert p["bottom_line"] == {"min": 1, "max": 5}
    assert p["rules"] == ["no-owner-due"]


def test_skill_md_gathers_with_rec_review_and_names_the_set():
    t = skill_md()
    gather = t.split("## Gather", 1)[1].split("## Write", 1)[0]
    for which in ("strength", "spread", "smart"):
        assert f"--table-item {which}" in gather, which
    assert "PMLC rec-review <ws> <run>/outputs/learnings-register.json" in gather
    assert "--nine-m" in gather
    write = t.split("## Write", 1)[1]
    assert '"the learnings register"' in write and f'"{BOTH}"' in write
    assert "CAPA Planner" in t                                        # never an input (spec D8)


def test_workflow_step_unplanned():
    steps = load(REFS / "workflows.json")["action-design"]["steps"]
    mine = [s for s in steps if s["skill"] == SKILL]
    assert len(mine) == 1 and "planned" not in mine[0]
    order = [s["skill"] for s in steps]
    assert order.index("learnings-register") < order.index("nine-m-analysis") < order.index(SKILL)


def test_evals_fragment():
    ev = load(ROOT / "evals" / "skills" / f"{SKILL}.json")["evals"]
    assert {"trigger", "no-trigger", "collision", "router"} <= {e["kind"] for e in ev} and len(ev) >= 4
    router = [e for e in ev if e["kind"] == "router"]
    assert any(x.get("value") == SKILL for e in router for x in e["expectations"])
    assert all(e["owner"] == SKILL for e in ev if e["kind"] != "router")
    siblings = {e.get("sibling") for e in ev if e["kind"] == "collision"}
    assert "nine-m-analysis" in siblings


def test_hub_routes_to_it():
    hub = (ROOT / "skills" / "learnings-coach" / "SKILL.md").read_text(encoding="utf-8")
    step2 = hub.split("## Step 2", 1)[1].split("## Step 3", 1)[0]
    assert f"| `{SKILL}` |" in step2
    assert len(hub.splitlines()) <= 150


def test_overlaps_name_both_siblings():
    from test_skills import OVERLAPS
    for pair in ((SKILL, "nine-m-analysis"), (SKILL, "learnings-register"), ("nine-m-analysis", SKILL)):
        assert pair in OVERLAPS, pair


# ----------------------------------------------------------------------------------------- the Hazira golden

@pytest.fixture(scope="module")
def hz(tmp_path_factory):
    pytest.importorskip("openpyxl")
    root = tmp_path_factory.mktemp("hazira-rsr")
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root),
        "--overlay", "india-process-site")
    ws = root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"
    for p in (REGISTER, NINE_M_MAP, GOLDEN):
        shutil.copy(p, ws.parent / "outputs" / p.name)
    return ws


def _engine_item(hz, which):
    return json.loads(run("rec-review", str(hz), str(hz.parent / "outputs" / REGISTER.name), "--nine-m",
                          "--table-item", which))


def test_golden_pastes_the_engine_tables(hz):
    pack = load(GOLDEN)
    for sec, which in (("strength", "strength"), ("spread", "spread")):
        want = _engine_item(hz, which)
        got = [it for it in _items(pack, sec) if it["kind"] == "table"]
        assert len(got) == 1, sec
        assert {k: got[0][k] for k in ("columns", "rows", "row_cites")} == \
            {k: want[k] for k in ("columns", "rows", "row_cites")}, sec
    if not _engine_item(hz, "smart")["rows"]:                          # no SMART gap on Hazira: the section is left out
        assert "smart" not in {s["id"] for s in pack["sections"]}


def test_golden_states_the_band_counts(hz):
    out = run("rec-review", str(hz), str(hz.parent / "outputs" / REGISTER.name), "--nine-m")
    assert out.splitlines()[0] == "rec-review (register+9M): stronger 24; intermediate 15; weaker 5; unrated 0"
    text = " ".join(b["text"] for b in load(GOLDEN)["bottom_line"])
    for want in ("24", "15", "5", "44"):
        assert want in text, want


def test_golden_says_which_set_it_reviewed():
    pack = load(GOLDEN)
    paras = _items(pack, "reviewed-set")
    assert len(paras) == 1 and paras[0]["kind"] == "para"
    assert BOTH in paras[0]["text"]
    assert "demonstration" in paras[0]["text"]                         # the 9M answers were scripted (OD5-1)


def test_golden_directions_carry_a_tier_and_no_owner_or_date():
    pack = load(GOLDEN)
    dirs = _items(pack, "directions")
    assert 1 <= len(dirs) <= 10 and all(d["kind"] == "recommendation" for d in dirs)
    lr = {e["lr_id"] for e in load(REGISTER)["entries"]}
    for d in dirs:
        assert d["hoc_tier"] and d["indicator"] and d["cites"], d
        assert d.get("learning") in lr, d
    items = [it for s in pack["sections"] for it in s["items"]]
    assert not [it for it in items if it.get("owner") or it.get("by_when")]          # D7
    assert pack["skill"] == SKILL and "handling" not in pack


def test_golden_passes_strict_and_language(hz):
    out = run("check-pack", str(hz), str(hz.parent / "outputs" / GOLDEN.name), "--strict", "--register",
              str(REGISTER))
    assert out.splitlines()[-1].startswith("OK:"), out
    lang = json.loads(run("check-language", str(hz), str(hz.parent / "outputs" / GOLDEN.name), "--json"))
    assert lang["ok"] and lang["output"][-1].startswith("check-language: 0 errors"), lang


def test_owner_on_a_direction_fails_without_strict(hz, tmp_path):
    pack = load(GOLDEN)
    _items(pack, "directions")[0]["owner"] = "Plant manager"
    bad = tmp_path / GOLDEN.name
    bad.write_text(json.dumps(pack), encoding="utf-8")
    r = subprocess.run([sys.executable, str(PMLC), "check-pack", str(hz), str(bad)], capture_output=True, text=True)
    assert r.returncode != 0 and "owner and due dates are set by the organisation" in r.stdout + r.stderr


def test_golden_is_rendered():
    """Task 24 rendered the golden beside its JSON (OD4-4), so it is no longer staged in RENDER_PENDING."""
    from pmlc_lib import samples
    assert f"{SKILL}.json" not in samples.RENDER_PENDING
    assert all(GOLDEN.with_suffix(f".{ext}").is_file() for ext in ("html", "md"))
