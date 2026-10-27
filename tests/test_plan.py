"""pmlc plan: resolve a workflow preset, audiences or skills into an ordered, tracked plan (spec §2.2)."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from test_pmlc import PMLC, make_export, run, run_fail, ws  # noqa: F401  (ws is a module-scoped fixture)
from test_sample import hz  # noqa: F401  (the Hazira module fixture)
from pmlc_lib import contracts, plan  # noqa: E402  (test_pmlc put the engine folder on sys.path)

GOLDEN = Path(__file__).resolve().parent / "fixtures" / "plans"
PRESETS = list(contracts.load_workflows())
STATUS = "Learning purposes: not a statutory document"


@pytest.fixture
def fresh(ws, tmp_path):  # noqa: F811
    """A private copy of the synthetic workspace (ingested and classified)."""
    d = tmp_path / "ws"
    shutil.copytree(ws, d)
    return d


def plan_json(*args):
    return json.loads(run("plan", *args, "--json"))


def steps(p):
    return [(s["skill"], s["status"]) for s in p["steps"]]


def mini_pack(name):
    return {"pack": name, "schema": 1, "title": f"{name}: synthetic pump fire", "audience": "Testers",
            "status": STATUS, "bottom_line": [{"text": "Test before service.", "cites": ["FND-0002"]}],
            "sections": [{"id": "s1", "heading": "Section one", "items": [
                {"kind": "learning", "lesson": "Test a disturbed joint before service.", "cites": ["FND-0002"]}]}]}


def test_plan_orders_by_dependency(fresh):
    p = plan_json(str(fresh), "--skills", "board-brief")
    assert steps(p) == [("engine:ingest", "done"), ("engine:classify", "done"), ("board-brief", "todo")]
    assert [s["n"] for s in p["steps"]] == [1, 2, 3]
    assert p["next"] == 3
    assert p["request"] == {"workflow": None, "audiences": [], "skills": ["board-brief"]}
    bb = p["steps"][2]
    assert bb["commands"] == ["PMLC select <ws> --preset board-brief:top-l4",
                              "PMLC select <ws> --preset board-brief:assurance-l34",
                              "PMLC select <ws> --preset board-brief:earlier-warnings",
                              "PMLC check-pack <ws> <run>/outputs/board-brief.json --strict",
                              "PMLC pack <ws> <run>/outputs/board-brief.json"]
    assert p["steps"][1]["commands"] == ["PMLC classify <ws>"] and p["steps"][1]["produces"] == "clusters"


def test_plan_marks_done_from_manifest(tmp_path):
    x = make_export(tmp_path)
    w = tmp_path / "ws"
    run("ingest", str(x), "--legacy-out", str(w))
    assert steps(plan_json(str(w), "--skills", "board-brief"))[1] == ("engine:classify", "todo")
    run("classify", str(w))
    assert steps(plan_json(str(w), "--skills", "board-brief"))[1] == ("engine:classify", "done")


def test_plan_stale_output_not_done(fresh, tmp_path):
    x = make_export(tmp_path, edited={"FND-0001": "Yes"}, name="changed.xlsx")
    run("ingest", str(x), "--legacy-out", str(fresh), "--force")
    p = plan_json(str(fresh), "--skills", "board-brief")
    assert steps(p)[:2] == [("engine:ingest", "done"), ("engine:classify", "todo")]
    assert p["next"] == 2


def test_plan_planned_skill_skipped(fresh):
    p = plan_json(str(fresh), "--workflow", "first-48-hours")
    by = {s["skill"]: s for s in p["steps"]}
    sa = by["safety-alert"]
    assert sa["status"] == "planned" and sa["planned_for"] == "Phase 6" and sa["commands"] == []
    assert sa["mode"] == "internal"
    assert by["learnings-register"]["mode"] == "draft"
    assert [s["skill"] for s in p["steps"]][-3:] == ["learnings-register", "safety-alert", "supervisor-coach"]
    reg = by["learnings-register"]
    reg["status"] = "done"
    assert plan.next_step(p)["skill"] == "supervisor-coach"
    out = run("plan", str(fresh), "--workflow", "first-48-hours")
    assert "planned for v2.0, Phase 6" in out


def _skill(root, name, requires, optional=(), pack=None):
    d = root / name
    d.mkdir(parents=True)
    m = {"name": name, "kind": "analysis", "audiences": [], "scope": {"tiers": [], "levels": [], "tags": []},
         "requires": list(requires), "optional_inputs": list(optional), "produces": {"pack": pack, "files": []},
         "share_default": "internal", "embed_default": "cited", "interactive": False, "since": "2.0.0"}
    (d / "skill.json").write_text(json.dumps(m), encoding="utf-8")


def _refs(root, artefacts):
    refs = root / "refs"
    refs.mkdir(parents=True)
    (refs / "artefacts.json").write_text(json.dumps(artefacts), encoding="utf-8")
    (refs / "workflows.json").write_text("{}", encoding="utf-8")
    (refs / "audiences.json").write_text("[]", encoding="utf-8")
    (refs / "select-presets.json").write_text("{}", encoding="utf-8")
    return refs


ART = {"workspace": {"file": "workspace/findings.json", "producer": "engine:ingest", "org_filled": False},
       "a-out": {"file": "outputs/a.json", "producer": "skill:a", "org_filled": False},
       "b-out": {"file": "outputs/b.json", "producer": "skill:b", "org_filled": False}}


def test_plan_cycle_refused(fresh, tmp_path):
    root = tmp_path / "skills"
    _skill(root, "a", ["workspace", "b-out"])
    _skill(root, "b", ["workspace", "a-out"])
    with pytest.raises(SystemExit) as e:
        plan.build(fresh, fresh, skills=["a"], skills_root=root, refs=_refs(tmp_path, ART))
    assert str(e.value.code) == "cycle: a -> b -> a"


def test_optional_input_makes_no_edge(fresh, tmp_path):
    root = tmp_path / "skills"
    _skill(root, "a", ["workspace"], optional=["a-out", "b-out"])
    _skill(root, "b", ["workspace", "a-out"])
    p = plan.build(fresh, fresh, skills=["a", "b"], skills_root=root, refs=_refs(tmp_path, ART))
    assert [s["skill"] for s in p["steps"]] == ["engine:ingest", "a", "b"]
    # report-comparison lists comparator, which it produces itself, only as an optional input: not a cycle
    p = plan_json(str(fresh), "--skills", "report-comparison")
    assert [s["skill"] for s in p["steps"]] == ["engine:ingest", "report-comparison"]
    rc = p["steps"][-1]
    assert rc["produces"] == "comparator" and rc["questions"] == ["Which official or other report is being compared?"]


def test_plan_missing_producer_refused(fresh, tmp_path):
    root = tmp_path / "skills"
    _skill(root, "a", ["workspace", "ghost"])
    with pytest.raises(SystemExit) as e:
        plan.build(fresh, fresh, skills=["a"], skills_root=root, refs=_refs(tmp_path, ART))
    assert "ghost" in str(e.value.code) and "a" in str(e.value.code)
    root2 = tmp_path / "skills2"
    _skill(root2, "a", ["workspace", "b-out"])   # b-out's producer, skill b, has no folder and is not planned
    with pytest.raises(SystemExit) as e:
        plan.build(fresh, fresh, skills=["a"], skills_root=root2, refs=_refs(tmp_path / "x", ART))
    assert "b-out" in str(e.value.code)


def test_planned_artefact_producer_is_a_planned_step(fresh, tmp_path):
    root = tmp_path / "skills"
    _skill(root, "a", ["workspace", "b-out"])
    art = dict(ART, **{"b-out": dict(ART["b-out"], planned="Phase 5")})
    p = plan.build(fresh, fresh, skills=["a"], skills_root=root, refs=_refs(tmp_path, art))
    assert [(s["skill"], s["status"], s["planned_for"]) for s in p["steps"]] == [
        ("engine:ingest", "done", None), ("b", "planned", "Phase 5"), ("a", "todo", None)]


def test_invalid_manifest_exits(tmp_path):
    root = tmp_path / "skills"
    _skill(root, "a", ["workspace"])
    m = json.loads((root / "a" / "skill.json").read_text(encoding="utf-8"))
    m["kind"] = "nope"
    (root / "a" / "skill.json").write_text(json.dumps(m), encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        contracts.load_manifests(root)
    assert str(e.value.code).startswith("skill.json for a: ") and "kind" in str(e.value.code)
    (root / "a" / "skill.json").write_text(json.dumps(dict(m, kind="analysis", name="x")), encoding="utf-8")
    with pytest.raises(SystemExit, match="differs from the folder name"):
        contracts.load_manifests(root)
    (root / "a" / "skill.json").write_text("{", encoding="utf-8")
    with pytest.raises(SystemExit, match="skill.json for a: not valid JSON"):
        contracts.load_manifests(root)
    (root / "a" / "skill.json").unlink()
    (root / "a" / "SKILL.md").write_text("x", encoding="utf-8")
    with pytest.raises(SystemExit, match="skill.json for a: missing"):
        contracts.load_manifests(root)


def test_plan_unknown_skill_refused(fresh):
    r = run_fail("plan", str(fresh), "--skills", "nope")
    assert r.returncode == 1 and "nope" in r.stderr
    r = run_fail("plan", str(fresh), "--workflow", "nope")
    assert r.returncode == 1 and "first-48-hours" in r.stderr
    r = run_fail("plan", str(fresh), "--audiences", "nope")
    assert r.returncode == 1 and "nope" in r.stderr
    r = run_fail("plan", str(fresh), "--next")
    assert r.returncode == 1 and "no plan" in r.stderr
    r = run_fail("plan", str(fresh), "--skills", "board-brief", "--workflow", "leadership")
    assert r.returncode == 2


def fixture_pack(name):
    """A committed fixture pack: these pass check-pack --strict on the synthetic workspace (Ruling P3-5)."""
    return json.loads((Path(__file__).resolve().parent / "fixtures" / "packs" / f"{name}.json").read_text(
        encoding="utf-8"))


def test_plan_next_advances_after_check_pack(fresh):
    p = plan_json(str(fresh), "--skills", "board-brief,supervisor-coach")
    assert p["next"] == 3 and p["steps"][2]["skill"] == "board-brief"
    out = fresh / "outputs"
    out.mkdir(exist_ok=True)
    (out / "board-brief.json").write_text(json.dumps(fixture_pack("board-brief")), encoding="utf-8")
    run("check-pack", str(fresh), str(out / "board-brief.json"))
    assert "3. board-brief" in run("plan", str(fresh), "--next")      # the gate says --strict: non-strict is not done
    run("check-pack", str(fresh), str(out / "board-brief.json"), "--strict")
    nxt = run("plan", str(fresh), "--next")
    assert "4. supervisor-coach" in nxt and "board-brief" not in nxt
    assert str(fresh / "outputs" / "supervisor-coach.json") in nxt      # printed with the real paths
    assert json.loads((fresh / "plan.json").read_text(encoding="utf-8"))["next"] == 4
    (out / "supervisor-coach.json").write_text(json.dumps(fixture_pack("supervisor-coach")), encoding="utf-8")
    run("check-pack", str(fresh), str(out / "supervisor-coach.json"), "--strict")
    run("check-all", str(fresh))       # a later non-strict pass on unchanged content keeps the strict pass
    r = subprocess.run([sys.executable, str(PMLC), "plan", str(fresh), "--next"], capture_output=True, text=True)
    assert r.returncode == 2 and "complete" in r.stdout
    # an edit after the check makes the step todo again
    edited = fixture_pack("board-brief")
    edited["title"] = "Edited after the check"
    (out / "board-brief.json").write_text(json.dumps(edited, indent=2), encoding="utf-8")
    assert "3. board-brief" in run("plan", str(fresh), "--next")


def test_plan_json_deterministic(fresh, tmp_path):
    run("plan", str(fresh), "--workflow", "full-cascade")
    a = (fresh / "plan.json").read_bytes()
    run("plan", str(fresh), "--workflow", "full-cascade")
    assert (fresh / "plan.json").read_bytes() == a
    text = a.decode("utf-8")
    assert str(tmp_path) not in text and "/<ws>" not in text and "<ws>" in text
    assert "written" not in text


def test_plan_recorded_in_manifest(fresh):
    from pmlc_lib.workspace import KNOWN_DERIVED, REBUILD
    assert "plan.json" in KNOWN_DERIVED and REBUILD["plan.json"] == "plan"
    run("plan", str(fresh), "--skills", "board-brief")
    m = json.loads((fresh / "manifest.json").read_text(encoding="utf-8"))
    assert set(m["files"]["plan.json"]["inputs"]) == {"manifest.json", "contracts"}
    assert "| plan.json | current |" in run("status", str(fresh))
    run("classify", str(fresh))
    assert "| plan.json | stale | manifest.json changed" in run("status", str(fresh))


def test_plan_gate_approved_review_for_external(fresh):
    p = plan_json(str(fresh), "--skills", "board-brief,supervisor-coach")
    by = {s["skill"]: s for s in p["steps"]}
    assert by["board-brief"]["gate"] == ["check-pack --strict", "approved review"]
    assert by["supervisor-coach"]["gate"] == ["check-pack --strict"]


def test_register_and_engine_steps(fresh):
    p = plan_json(str(fresh), "--workflow", "full-cascade")
    by = {s["skill"]: s for s in p["steps"]}
    reg = by["learnings-register"]
    assert reg["produces"] == "register" and reg["gate"] == ["check-register --strict"]
    assert reg["commands"] == ["PMLC select <ws> --preset learnings-register:top",
                               "PMLC check-register <ws> <run>/outputs/learnings-register.json --strict",
                               "PMLC register-xlsx <run>/outputs/learnings-register.json",
                               "PMLC register-md <ws> <run>/outputs/learnings-register.json"]
    assert reg["status"] == "todo"
    tpl = by["engine:templates"]
    assert tpl["status"] == "todo" and tpl["commands"] == [
        "PMLC templates <ws> adoption", "PMLC templates <ws> distribution", "PMLC templates <ws> verification",
        "PMLC templates <ws> learning-team"]
    olm = by["organisation-learning-map"]
    assert olm["commands"][0] == "PMLC dashboard <ws> --register <run>/outputs/learnings-register.json"
    order = [s["skill"] for s in p["steps"]]
    assert order.index("learnings-register") < order.index("organisation-learning-map")
    p = plan_json(str(fresh), "--workflow", "follow-up")
    assert p["steps"][-1]["commands"] == ["PMLC templates <ws> verification"]
    assert p["steps"][-1]["produces"] == "verification"
    (fresh / "outputs").mkdir(exist_ok=True)
    (fresh / "outputs" / "verification.jsonl").write_text("", encoding="utf-8")
    assert plan_json(str(fresh), "--workflow", "follow-up")["steps"][-1]["status"] == "done"


def test_plan_printed(fresh):
    out = run("plan", str(fresh), "--workflow", "leadership")
    assert out.startswith("Plan: leadership")
    assert "1. engine:ingest [done]" in out and "gate: check-pack --strict, approved review" in out
    assert "<ws>" not in out and str(fresh) in out and "Next: step 3" in out


def test_plan_audiences_flag(fresh):
    p = plan_json(str(fresh), "--audiences", "board,supervisors")
    assert [s["skill"] for s in p["steps"] if not s["skill"].startswith("engine:")] == ["board-brief",
                                                                                         "supervisor-coach"]
    assert p["request"]["audiences"] == ["board", "supervisors"]


@pytest.fixture(scope="module")
def hzp(hz):  # noqa: F811
    for cmd in ("causal", "timeline", "interfaces"):
        run(cmd, str(hz.ws))
    return hz.ws


@pytest.mark.parametrize("preset", PRESETS)
def test_every_preset_matches_golden(hzp, preset):
    assert len(PRESETS) == 9
    run("plan", str(hzp), "--workflow", preset)
    got = json.loads((hzp / "plan.json").read_text(encoding="utf-8"))
    golden = GOLDEN / f"{preset}.json"
    if os.environ.get("PMLC_UPDATE_GOLDEN"):
        golden.parent.mkdir(parents=True, exist_ok=True)
        golden.write_text(json.dumps(got, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    assert golden.exists(), f"no golden {golden.name}: run with PMLC_UPDATE_GOLDEN=1, then review it"
    assert got == json.loads(golden.read_text(encoding="utf-8"))


def test_plan_strict_pass_needed_for_pack_with_unknown_learning(fresh):
    """I-2 repro 1: an unknown LR-nn passes check-pack but not --strict (with a register), so the step stays todo."""
    from test_pmlc import MINI_REG
    out = fresh / "outputs"
    out.mkdir(exist_ok=True)
    (out / "learnings-register.json").write_text(json.dumps(MINI_REG), encoding="utf-8")
    pk = mini_pack("board-brief")
    pk["sections"][0]["items"][0]["learning"] = "LR-99"
    (out / "board-brief.json").write_text(json.dumps(pk), encoding="utf-8")
    run("check-pack", str(fresh), str(out / "board-brief.json"))
    assert run_fail("check-pack", str(fresh), str(out / "board-brief.json"), "--strict").returncode == 1
    p = plan_json(str(fresh), "--skills", "board-brief")
    assert dict(steps(p))["board-brief"] == "todo"
    run("check-all", str(fresh))            # a non-strict check-all never makes it done
    assert dict(steps(plan_json(str(fresh), "--skills", "board-brief")))["board-brief"] == "todo"


def test_plan_register_done_needs_strict_pass(hz, tmp_path):  # noqa: F811
    """I-2 repro 2: the sample register without why_not_stronger passes check-register, gives 2 problems under
    --strict; check-all --strict must fail on it and the plan's register step must stay todo."""
    run_dir = tmp_path / "pmlc-runs" / hz.ws.parent.name
    shutil.copytree(hz.ws.parent, run_dir)
    w, out = run_dir / "workspace", run_dir / "outputs"
    out.mkdir(exist_ok=True)
    sample = Path(__file__).resolve().parents[1] / "samples" / "2020-09-24-hazira-gas-release-fire" / "outputs"
    reg = json.loads((sample / "learnings-register.json").read_text(encoding="utf-8"))
    for e in reg["entries"]:
        e.pop("why_not_stronger", None)
    (out / "learnings-register.json").write_text(json.dumps(reg, indent=2), encoding="utf-8")
    run("check-register", str(w), str(out / "learnings-register.json"))
    strict = run_fail("check-register", str(w), str(out / "learnings-register.json"), "--strict")
    assert strict.returncode == 1 and "2 problem(s)" in strict.stdout
    assert dict(steps(plan_json(str(w), "--skills", "learnings-register")))["learnings-register"] == "todo"
    r = run_fail("check-all", str(w), "--strict")
    assert r.returncode == 1 and "learnings-register.json: 2 problem(s)" in r.stdout
    assert "LR-08" in r.stderr
    assert dict(steps(plan_json(str(w), "--skills", "learnings-register")))["learnings-register"] == "todo"
    shutil.copy(sample / "learnings-register.json", out / "learnings-register.json")
    run("check-all", str(w), "--strict")
    assert dict(steps(plan_json(str(w), "--skills", "learnings-register")))["learnings-register"] == "done"


def test_full_cascade_classifies_before_learning_clusters(fresh):
    """I-5 (FR-2): learning-clusters and interface-learnings need clusters.json, so classify is planned first."""
    names = [s["skill"] for s in plan_json(str(fresh), "--workflow", "full-cascade")["steps"]]
    assert names.index("engine:classify") < names.index("learning-clusters")
    names = [s["skill"] for s in plan_json(str(fresh), "--skills", "interface-learnings")["steps"]]
    assert names.index("engine:classify") < names.index("interface-learnings")
