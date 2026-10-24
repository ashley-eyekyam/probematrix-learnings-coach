"""Phase 5 Task 13: the evidence-strength-scorecard skill. Its manifest, profile, workflow steps, evals and hub row
follow the plan, and its Hazira golden pack pastes the engine's evidence-audit tables unchanged (203 single-source,
195 document-only, 167 level-3 findings with 11 citing a witness, EVD-8645 behind 67) and passes check-pack
--strict --register and check-language with no errors."""
import json
import shutil

import pytest

from test_pmlc import ROOT, run

SKILL = "evidence-strength-scorecard"
REFS = ROOT / "skills" / "learnings-coach" / "references"
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
GOLDEN = SAMPLE / "outputs" / f"{SKILL}.json"
REGISTER = SAMPLE / "outputs" / "learnings-register.json"
BANNER = ("This scorecard shows where more evidence would strengthen confidence. It does not grade the "
          "investigation team.")


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def test_manifest():
    m = load(ROOT / "skills" / SKILL / "skill.json")
    assert (m["kind"], m["audiences"], m["scope"]["levels"]) == ("analysis", [], [1, 2, 3, 4])
    assert m["requires"] == ["workspace", "evidence-audit"] and m["optional_inputs"] == ["register"]
    # Ruling P5-21: the plan listed csv, but `--format csv` writes only recommendation, decision and indicator items, which this
    # pack has none of; the spreadsheet route is pack-xlsx --kind question|table (Task 13 report, Decisions).
    assert m["produces"]["pack"] == SKILL and m["formats"] == ["docx"]
    assert (m["share_default"], m["embed_default"], m["since"]) == ("internal", "cited", "2.0.0")


def test_profile():
    p = load(REFS / "pack-profiles.json")[SKILL]
    assert [(s["id"], s["kinds"], s["min"], s["max"]) for s in p["sections"]] == [
        ("banner", ["para"], 1, 1), ("scorecard", ["table"], 1, 1), ("levels", ["table"], 1, 1),
        ("concentration", ["table"], 0, 1), ("requests", ["question"], 1, 12), ("limits", ["para"], 1, 2)]
    assert p["bottom_line"] == {"min": 1, "max": 5}
    assert p["rules"] == ["banner:evidence"] and p["coverage_floor"] == 0.25


def test_workflow_steps_unplanned():
    wf = load(REFS / "workflows.json")
    for preset in ("assurance", "investigation-quality"):
        steps = [s for s in wf[preset]["steps"] if s["skill"] == SKILL]
        assert len(steps) == 1 and "planned" not in steps[0], preset


def test_investigator_coach_reads_the_audit():
    assert "evidence-audit" in load(ROOT / "skills" / "investigator-coach" / "skill.json")["optional_inputs"]


def test_evals_fragment():
    ev = load(ROOT / "evals" / "skills" / f"{SKILL}.json")["evals"]
    kinds = {e["kind"] for e in ev}
    assert {"trigger", "no-trigger", "collision", "router"} <= kinds and len(ev) >= 4
    router = [e for e in ev if e["kind"] == "router"]
    assert any(x.get("value") == SKILL for e in router for x in e["expectations"])
    assert all(e["owner"] == SKILL for e in ev if e["kind"] != "router")


def test_hub_routes_to_it():
    hub = (ROOT / "skills" / "learnings-coach" / "SKILL.md").read_text(encoding="utf-8")
    step2 = hub.split("## Step 2", 1)[1].split("## Step 3", 1)[0]
    assert f"| `{SKILL}` |" in step2
    assert len(hub.splitlines()) <= 150


# ----------------------------------------------------------------------------------------- the Hazira golden

@pytest.fixture(scope="module")
def hz(tmp_path_factory):
    pytest.importorskip("openpyxl")
    root = tmp_path_factory.mktemp("hazira-esc")
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root),
        "--overlay", "india-process-site")
    ws = root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"
    run("evidence-audit", str(ws))
    shutil.copy(REGISTER, ws.parent / "outputs" / REGISTER.name)
    shutil.copy(GOLDEN, ws.parent / "outputs" / GOLDEN.name)
    return ws


def _items(pack, sec):
    return [it for s in pack["sections"] if s["id"] == sec for it in s["items"]]


def test_golden_pastes_the_engine_tables(hz):
    pack = load(GOLDEN)
    for sec, which in (("scorecard", "scorecard"), ("levels", "levels"), ("concentration", "concentration")):
        want = json.loads(run("evidence-audit", str(hz), "--table-item", which))
        got = [it for it in _items(pack, sec) if it["kind"] == "table"]
        assert len(got) == 1, sec
        assert {k: got[0][k] for k in ("columns", "rows", "row_cites")} == \
            {k: want[k] for k in ("columns", "rows", "row_cites")}, sec


def test_golden_shows_the_calibration_numbers():
    pack = load(GOLDEN)
    score = {r[0]: r[1] for r in _items(pack, "scorecard")[0]["rows"]}
    assert score["single-source"] == 203 and score["document-only"] == 195
    l3 = next(r for r in _items(pack, "levels")[0]["rows"] if r[0] == "Level 3")
    assert (l3[1], l3[4]) == (167, 11)
    assert _items(pack, "concentration")[0]["rows"][0][:2] == ["EVD-8645", 67]


def test_golden_banner_roles_and_learnings():
    pack = load(GOLDEN)
    assert [it["text"] for it in _items(pack, "banner")] == [BANNER]
    assert pack["skill"] == SKILL and "handling" not in pack
    items = [it for s in pack["sections"] for it in s["items"]]
    assert not [it for it in items if it.get("owner") or it.get("by_when")]            # D7
    lr = {e["lr_id"] for e in load(REGISTER)["entries"]}
    used = {it["learning"] for it in items if it.get("learning")}
    assert used and used <= lr
    assert 1 <= len(_items(pack, "requests")) <= 12


def test_golden_passes_strict_and_language(hz):
    out = run("check-pack", str(hz), str(hz.parent / "outputs" / GOLDEN.name), "--strict", "--register",
              str(REGISTER))
    assert out.splitlines()[-1].startswith("OK:"), out                   # run() asserts exit 0: no problems
    lang = json.loads(run("check-language", str(hz), str(hz.parent / "outputs" / GOLDEN.name), "--json"))
    assert lang["ok"] and lang["output"][-1].startswith("check-language: 0 errors"), lang


def test_render_pending_exempts_only_its_packs(tmp_path, monkeypatch):
    """A golden JSON may land before its render (plan, New-skill checklist item 6): check-samples lets a pack listed
    in RENDER_PENDING sit without its .html and .md, and only that pack. Task 24 rendered this golden."""
    from pmlc_lib import samples
    assert f"{SKILL}.json" not in samples.RENDER_PENDING
    assert all(GOLDEN.with_suffix(f".{ext}").is_file() for ext in ("html", "md"))
    monkeypatch.setattr(samples, "RENDER_PENDING", frozenset({f"{SKILL}.json"}))
    d = tmp_path / "2020-09-24-hazira-gas-release-fire"
    out = d / "outputs"
    out.mkdir(parents=True)
    (d / "README.md").write_text("x")
    (d / f"{d.name}_probematrix-findings.xlsx").write_bytes(b"x")
    for name in (SKILL, "board-brief"):
        (out / f"{name}.json").write_text(json.dumps({"pack": name, "sections": []}))
    assert samples.sample_folder_problems(tmp_path) == [f"{d.name}: outputs/board-brief.json has no board-brief.html",
                                                        f"{d.name}: outputs/board-brief.json has no board-brief.md"]
