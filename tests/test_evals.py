"""Eval set tests: evals/evals.json structure and per-skill counts, and the grader on a synthetic run."""
import json
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

from test_pmlc import ROOT, make_export, run

RUNNER = ROOT / "evals" / "run_evals.py"
EVALS = ROOT / "evals" / "evals.json"
FIX = Path(__file__).resolve().parent / "fixtures" / "packs"
SKILLS = sorted(p.name for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").exists())


def runner(*args):
    return subprocess.run([sys.executable, str(RUNNER), *args], capture_output=True, text=True)


def test_evals_structure():
    r = runner("check")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "23 skills" in r.stdout


def test_every_skill_has_three():
    data = json.loads(EVALS.read_text(encoding="utf-8"))
    assert data["skill_name"] == "probematrix-learnings-coach"
    assert (ROOT / data["sample"]).exists()
    evals = data["evals"]
    assert len(SKILLS) == 23 and len(evals) >= 69
    by = Counter(e["owner"] for e in evals)
    kinds = Counter((e["owner"], e["kind"]) for e in evals)
    for s in SKILLS:
        assert by[s] >= 3, s
        assert kinds[(s, "no-trigger")] >= 1, s
        assert kinds[(s, "collision")] >= 1, s
    for e in evals:
        assert e["kind"] in ("trigger", "no-trigger", "collision")
        if e["kind"] == "no-trigger":
            assert e["skill"] is None and e["not_skill"] == e["owner"]
        if e["kind"] == "collision":
            assert e["skill"] in SKILLS and e["sibling"] in SKILLS and e["skill"] != e["sibling"]
    in_collision = {e["skill"] for e in evals if e["kind"] == "collision"} | \
                   {e["owner"] for e in evals if e["kind"] == "collision"}
    assert set(SKILLS) <= in_collision


def test_check_names_each_problem(tmp_path):
    bad = {"skill_name": "probematrix-learnings-coach", "sample": "samples/nope.xlsx", "evals": [
        {"id": 1, "owner": "board-brief", "skill": "board-brief", "kind": "trigger", "prompt": "p",
         "files": ["samples/missing.xlsx"], "expectations": [{"type": "smells_nice"}]},
        {"id": 1, "owner": "no-such-skill", "skill": "board-brief", "kind": "maybe", "prompt": "p", "files": [],
         "expectations": []},
        {"id": 2, "owner": "board-brief", "skill": "board-brief", "kind": "collision", "prompt": "p", "files": [],
         "expectations": []},
    ]}
    f = tmp_path / "evals.json"
    f.write_text(json.dumps(bad))
    r = runner("check", "--file", str(f))
    assert r.returncode == 1
    out = r.stdout + r.stderr
    for msg in ["sample: samples/nope.xlsx does not exist", "eval 1: duplicate id",
                "eval 1: files: samples/missing.xlsx does not exist", "eval 1: unknown expectation type smells_nice",
                "owner: no-such-skill is not a skill folder", "kind: maybe is not one of",
                "eval 2: collision needs a sibling", "board-brief: needs at least 3 evals",
                "manager-coach: needs at least 1 no-trigger eval", "manager-coach: needs at least 1 collision eval"]:
        assert msg in out, msg


def _run_folder(tmp_path) -> Path:
    x = make_export(tmp_path)
    run("ingest", str(x), "--slug", "synthetic-pump-fire", "--root", str(tmp_path))
    rd = next((tmp_path / "pmlc-runs").iterdir())
    run("classify", str(rd / "workspace"))
    shutil.copy(FIX / "supervisor-coach.json", rd / "outputs" / "supervisor-coach.json")
    return rd


def _evals_file(tmp_path, scope) -> Path:
    exp = [{"type": "pack_exists", "pack": "supervisor-coach"},
           {"type": "check_pack_ok", "pack": "supervisor-coach"},
           {"type": "scope_equals", "pack": "supervisor-coach", "scope": scope},
           {"type": "coverage_min", "pack": "supervisor-coach", "ratio": 0.25},
           {"type": "routes_to", "skill": "supervisor-coach"}]
    data = {"skill_name": "probematrix-learnings-coach", "evals": [
        {"id": 7, "owner": "supervisor-coach", "skill": "supervisor-coach", "kind": "trigger", "prompt": "p",
         "files": [], "expectations": exp},
        {"id": 8, "owner": "board-brief", "skill": "board-brief", "kind": "trigger", "prompt": "p", "files": [],
         "expectations": [{"type": "pack_exists", "pack": "board-brief"}]},
    ]}
    f = tmp_path / "evals-grade.json"
    f.write_text(json.dumps(data))
    return f


def test_grade_on_fixture_run(tmp_path):
    rd = _run_folder(tmp_path)
    r = runner("grade", str(rd), "--file", str(_evals_file(tmp_path, {"tiers": ["T2"]})))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "| id | skill | expectation | pass/fail |" in r.stdout
    assert "| 7 | supervisor-coach | routes_to supervisor-coach | manual |" in r.stdout
    assert "| 8 |" not in r.stdout                        # board-brief.json is absent, so eval 8 is skipped
    assert "Pass rate: 4/4 machine checks (100%)" in r.stdout


def test_grade_fails_and_ids_force(tmp_path):
    rd = _run_folder(tmp_path)
    f = _evals_file(tmp_path, {"tiers": ["T1"]})
    r = runner("grade", str(rd), "--file", str(f))
    assert r.returncode == 1
    assert "| 7 | supervisor-coach | scope_equals supervisor-coach | fail" in r.stdout
    r = runner("grade", str(rd), "--file", str(f), "--ids", "8")
    assert r.returncode == 1
    assert "| 8 | board-brief | pack_exists board-brief | fail" in r.stdout and "| 7 |" not in r.stdout
    assert "Pass rate: 0/1" in r.stdout


def test_grade_needs_a_run_folder(tmp_path):
    r = runner("grade", str(tmp_path / "nope"))
    assert r.returncode != 0 and "workspace" in r.stderr


def _one_eval(tmp_path, exps):
    data = {"skill_name": "probematrix-learnings-coach", "evals": [
        {"id": 7, "owner": "supervisor-coach", "skill": "supervisor-coach", "kind": "trigger", "prompt": "p",
         "files": [], "expectations": exps}]}
    f = tmp_path / "evals-one.json"
    f.write_text(json.dumps(data))
    return f


def test_language_clean_expectation(tmp_path):
    rd = _run_folder(tmp_path)
    f = _one_eval(tmp_path, [{"type": "language_clean", "pack": "supervisor-coach"}])
    r = runner("grade", str(rd), "--file", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "language_clean supervisor-coach | pass" in r.stdout
    pack = json.loads((rd / "outputs" / "supervisor-coach.json").read_text(encoding="utf-8"))
    pack["bottom_line"] = "John Smith was careless and should be disciplined."
    (rd / "outputs" / "supervisor-coach.json").write_text(json.dumps(pack), encoding="utf-8")
    r = runner("grade", str(rd), "--file", str(f))
    assert r.returncode == 1 and "language_clean supervisor-coach | fail" in r.stdout


def test_pack_absent_expectation(tmp_path):
    rd = _run_folder(tmp_path)
    f = _one_eval(tmp_path, [{"type": "pack_absent", "pack": "board-brief"},
                             {"type": "pack_absent", "pack": "supervisor-coach"}])
    r = runner("grade", str(rd), "--file", str(f), "--ids", "7")
    assert "pack_absent board-brief | pass" in r.stdout
    assert "pack_absent supervisor-coach | fail" in r.stdout and r.returncode == 1


def test_card_fields_expectation(tmp_path):
    rd = _run_folder(tmp_path)
    out = rd / "outputs"
    card = {"kind": "card", "title": "t", "why_made_sense": "w", "organisation_changing": "o"}
    pack = {"sections": [{"id": "c", "heading": "Cards", "items": [card, dict(card)]}]}
    (out / "cards-ok.json").write_text(json.dumps(pack), encoding="utf-8")
    del pack["sections"][0]["items"][1]["organisation_changing"]
    (out / "cards-bad.json").write_text(json.dumps(pack), encoding="utf-8")
    (out / "cards-none.json").write_text(json.dumps({"sections": []}), encoding="utf-8")
    fields = ["why_made_sense", "organisation_changing"]
    f = _one_eval(tmp_path, [{"type": "card_fields", "pack": p, "fields": fields}
                             for p in ("cards-ok", "cards-bad", "cards-none")])
    r = runner("grade", str(rd), "--file", str(f), "--ids", "7")
    assert "card_fields cards-ok | pass" in r.stdout
    assert "card_fields cards-bad | fail: 1 of 2 cards lack organisation_changing" in r.stdout
    assert "card_fields cards-none | fail: no cards" in r.stdout


def test_grade_zero_outputs_fails(tmp_path):
    rd = _run_folder(tmp_path)
    (rd / "outputs" / "supervisor-coach.json").unlink()
    r = runner("grade", str(rd), "--file", str(_evals_file(tmp_path, {"tiers": ["T2"]})))
    assert r.returncode == 1 and "no outputs graded" in r.stdout


def test_grader_survives_bad_pack(tmp_path):
    rd = _run_folder(tmp_path)
    f = _evals_file(tmp_path, {"tiers": ["T2"]})
    p = rd / "outputs" / "supervisor-coach.json"
    for text in ("[1, 2]", json.dumps({"scope": "T2", "sections": "x"})):
        p.write_text(text, encoding="utf-8")
        r = runner("grade", str(rd), "--file", str(f))
        assert "Traceback" not in r.stderr, r.stderr
        assert r.returncode == 1
        assert "| 7 | supervisor-coach | scope_equals supervisor-coach | fail" in r.stdout
        assert "| 7 | supervisor-coach | coverage_min supervisor-coach >= 0.25 | fail" in r.stdout


def test_check_enforces_owner_and_files(tmp_path):
    sample = json.loads(EVALS.read_text(encoding="utf-8"))["sample"]

    def ev(i, **kw):
        base = {"id": i, "owner": "board-brief", "skill": "board-brief", "kind": "trigger", "prompt": "p",
                "files": [sample], "expectations": [{"type": "routes_to", "skill": "board-brief"}]}
        base.update(kw)
        return base
    bad = {"skill_name": "probematrix-learnings-coach", "sample": sample, "evals": [
        ev(1, skill="manager-coach"),
        ev(2, expectations=[{"type": "routes_to", "skill": "manager-coach"}]),
        ev(3, files=[]),
        ev(4, kind="no-trigger", skill=None, not_skill="board-brief", expectations=[]),
        ev(5, files=[str((ROOT / sample).resolve())]),
        ev(6, prompt="Use /home/someone/export.xlsx please"),
    ]}
    f = tmp_path / "evals.json"
    f.write_text(json.dumps(bad))
    r = runner("check", "--file", str(f))
    out = r.stdout + r.stderr
    for msg in ["eval 1: a trigger eval's skill must equal its owner",
                "eval 1: routes_to must name the eval's skill", "eval 2: routes_to must name the eval's skill",
                "eval 3: a trigger eval needs files", "eval 4: a no-trigger eval has no files",
                "eval 5: files: absolute path", "eval 6: prompt: absolute path"]:
        assert msg in out, msg


# ---- phase 3, task 18 (A29)
def _load_runner():
    import importlib.util
    spec = importlib.util.spec_from_file_location("run_evals_t18", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_abs_path_covers_srv_and_home_tilde():
    rx = _load_runner().ABS_PATH
    for s in ("/srv/data/x.xlsx", "open ~/Documents/x.xlsx", "see (/home/a/x)", "C:\\Users\\a", "~/x"):
        assert rx.search(s), s
    for s in ("samples/hazira/export.xlsx", "the srv folder", "a ~ b", "docs/home/x"):
        assert not rx.search(s), s


def test_coverage_cache_computes_once(monkeypatch):
    mod = _load_runner()
    import pmlc
    import pmlc_pack
    calls = []

    def fake(w, pack):
        calls.append(1)
        return {"relevant": 4, "cited": 1}

    monkeypatch.setattr(pmlc, "load_ws", lambda ws: {})
    monkeypatch.setattr(pmlc_pack, "coverage", fake)
    mod._COV.clear()
    key = ("ws", "pack.json")
    assert mod._coverage("ws", {}, key) == 0.25 and mod._coverage("ws", {}, key) == 0.25
    assert len(calls) == 1
    mod._coverage("ws", {}, ("ws", "other.json"))
    assert len(calls) == 2
    mod._coverage("ws", {})                        # no key: never cached
    mod._coverage("ws", {})
    assert len(calls) == 4
    mod._COV.clear()
