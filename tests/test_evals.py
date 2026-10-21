"""Eval set tests: evals/evals.json structure and per-skill counts, and the grader on a synthetic run."""
import json
import re
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
    evals = [e for e in data["evals"] if e["kind"] != "router"]      # router evals: test_router_evals_min_30
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


# ---- phase 3, task 24: router evals and the per-skill floor
PRESETS = sorted(json.loads((ROOT / "skills" / "learnings-coach" / "references" / "workflows.json")
                            .read_text(encoding="utf-8")))
SUB_SKILLS = [s for s in SKILLS if s != "learnings-coach"]


def _router(evals):
    return [e for e in evals if e.get("kind") == "router"]


def _target(e):
    return next(x.get("value") for x in e["expectations"] if x.get("type") == "routes_to")


def _router_file(tmp_path, n, value="board-brief", sibling=None, extra=None):
    sample = json.loads(EVALS.read_text(encoding="utf-8"))["sample"]
    evals = []
    for i in range(n):
        e = {"id": 1000 + i, "owner": "learnings-coach", "kind": "router", "prompt": f"route {i}",
             "files": [sample], "expectations": [{"type": "routes_to", "value": value}]}
        if sibling:
            e["sibling"] = sibling
        evals.append(e)
    evals += extra or []
    f = tmp_path / "router.json"
    f.write_text(json.dumps({"skill_name": "probematrix-learnings-coach", "sample": sample, "evals": evals}))
    return f


def test_router_evals_min_30(tmp_path):
    evals = json.loads(EVALS.read_text(encoding="utf-8"))["evals"]
    router = _router(evals)
    assert len(router) >= 30, len(router)
    for e in router:
        assert e["owner"] == "learnings-coach" and "skill" not in e, e["id"]
        assert [x["type"] for x in e["expectations"]] == ["routes_to"], e["id"]
    r = runner("check")
    assert r.returncode == 0, r.stdout
    assert f"{len(router)} router" in r.stdout
    r = runner("check", "--file", str(_router_file(tmp_path, 29)))
    assert r.returncode == 1
    assert "router: needs at least 30 router evals (has 29)" in r.stdout


def test_routes_to_targets_exist(tmp_path):
    router = _router(json.loads(EVALS.read_text(encoding="utf-8"))["evals"])
    targets = [_target(e) for e in router]
    assert all(t in PRESETS or t in SUB_SKILLS for t in targets), set(targets) - set(PRESETS) - set(SUB_SKILLS)
    assert set(PRESETS) <= set(targets), set(PRESETS) - set(targets)            # all 9 presets
    assert set(SUB_SKILLS) <= set(targets), set(SUB_SKILLS) - set(targets)      # all 22 sub-skills
    sibs = [e for e in router if e.get("sibling")]
    assert len(sibs) >= 8, len(sibs)
    for e in sibs:
        assert e["sibling"] in PRESETS or e["sibling"] in SUB_SKILLS, e["id"]
        assert e["sibling"] != _target(e), e["id"]
    bad = [{"id": 1, "owner": "learnings-coach", "kind": "router", "prompt": "p", "files": [],
            "expectations": [{"type": "routes_to", "value": "no-such-thing"}]},
           {"id": 2, "owner": "board-brief", "kind": "router", "prompt": "p", "files": [],
            "expectations": [{"type": "routes_to", "skill": "board-brief"}], "sibling": "nope"},
           {"id": 3, "owner": "learnings-coach", "kind": "router", "prompt": "p", "files": [],
            "expectations": [{"type": "routes_to", "value": "leadership"}], "sibling": "leadership"}]
    r = runner("check", "--file", str(_router_file(tmp_path, 30, extra=bad)))
    assert r.returncode == 1
    out = r.stdout
    for msg in ["eval 1: routes_to: no-such-thing is neither a skill folder nor a workflows.json preset",
                "eval 2: a router eval is owned by learnings-coach", "eval 2: routes_to needs value",
                "eval 2: sibling: nope is neither a skill folder nor a workflows.json preset",
                "eval 3: sibling must differ from the routes_to value",
                "router: no router eval routes to full-cascade", "router: no router eval routes to causal-map",
                "router: needs at least 8 sibling collisions (has 2)"]:
        assert msg in out, msg
    assert "router: no router eval routes to board-brief" not in out


def test_each_skill_three_evals_with_no_trigger_and_collision(tmp_path):
    evals = json.loads(EVALS.read_text(encoding="utf-8"))["evals"]
    for s in SKILLS:
        own = [e for e in evals if e["owner"] == s and e["kind"] != "router"]
        assert len(own) >= 3, s
        assert any(e["kind"] == "no-trigger" for e in own), s
        assert any(e["kind"] == "collision" for e in own), s
    # router evals are owned by the hub but never count towards a skill's floor
    r = runner("check", "--file", str(_router_file(tmp_path, 30)))
    out = r.stdout
    assert r.returncode == 1
    assert "learnings-coach: needs at least 3 evals (has 0)" in out
    for s in SKILLS:
        assert f"{s}: needs at least 1 no-trigger eval" in out, s
        assert f"{s}: needs at least 1 collision eval" in out, s


def test_routes_scores_against_the_floor(tmp_path):
    router = _router(json.loads(EVALS.read_text(encoding="utf-8"))["evals"])
    answers = {str(e["id"]): _target(e) for e in router}
    f = tmp_path / "answers.json"
    f.write_text(json.dumps(answers))
    r = runner("routes", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    n = len(router)
    assert f"Routing: {n}/{n} router evals (100%); floor 90%." in r.stdout
    wrong = [str(e["id"]) for e in router[:4]]
    for i in wrong[:3]:
        answers[i] = "board-brief" if answers[i] != "board-brief" else "leadership"
    del answers[wrong[3]]
    f.write_text(json.dumps(answers))
    r = runner("routes", str(f))
    assert r.returncode == (0 if (n - 4) / n >= 0.9 else 1)
    assert f"Routing: {n - 4}/{n} router evals" in r.stdout and "(no answer)" in r.stdout
    assert f"| {wrong[0]} | {_target(router[0])} |" in r.stdout
    f.write_text("[1]")
    r = runner("routes", str(f))
    assert r.returncode == 1 and "must be a JSON object" in r.stderr


def test_grade_section_exists(tmp_path):
    """X33: section_exists passes when the pack has a section with that id (profile globs allowed) and fails
    naming the missing id."""
    rd = _run_folder(tmp_path)
    data = {"skill_name": "probematrix-learnings-coach", "evals": [
        {"id": 9, "owner": "supervisor-coach", "skill": "supervisor-coach", "kind": "trigger", "prompt": "p",
         "files": [], "expectations": [{"type": "section_exists", "pack": "supervisor-coach", "section": "refuse"},
                                       {"type": "section_exists", "pack": "supervisor-coach", "section": "cascade"}]}]}
    f = tmp_path / "evals-section.json"
    f.write_text(json.dumps(data))
    r = runner("grade", str(rd), "--file", str(f))
    assert r.returncode == 1
    assert "| 9 | supervisor-coach | section_exists supervisor-coach refuse | pass |" in r.stdout, r.stdout
    assert "| 9 | supervisor-coach | section_exists supervisor-coach cascade | fail: no section cascade |" in r.stdout
    bad = dict(data, evals=[dict(data["evals"][0], expectations=[{"type": "section_exists", "pack": "x"}])])
    f.write_text(json.dumps(bad))
    assert "eval 9: section_exists needs section" in runner("check", "--file", str(f)).stdout


def test_router_prompts_do_not_echo_the_hub_table():
    """Task 24 m-1 / I-6: the analysis-route prompts 101-104 are in a user's own words. None shares a run of three
    words with any cell of the hub's Step 2 routing tables, so a routing run is not a string match."""
    hub = (ROOT / "skills" / "learnings-coach" / "SKILL.md").read_text(encoding="utf-8")
    step2 = hub.split("## Step 2", 1)[1].split("## Step 3", 1)[0]
    cells = [c.strip() for line in step2.splitlines() if line.startswith("| ") for c in line.strip("|").split("|")]

    def words(s):
        return re.findall(r"[a-z0-9]+", s.lower())

    grams = {tuple(words(c)[i:i + 3]) for c in cells for i in range(len(words(c)) - 2)}
    evals = {e["id"]: e for e in json.loads((ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))["evals"]}
    for n in (101, 102, 103, 104):
        w = words(evals[n]["prompt"])
        echo = [" ".join(w[i:i + 3]) for i in range(len(w) - 2) if tuple(w[i:i + 3]) in grams]
        assert not echo, (n, echo)


def test_p4h_routes_floor_exactly_90_percent(tmp_path):
    """Task 24 m-7: 27 of 30 is exactly the 90% floor and passes; 26 of 30 does not."""
    ef = _router_file(tmp_path, 30)
    answers = {str(1000 + i): "board-brief" for i in range(30)}
    for i in range(3):
        answers[str(1000 + i)] = "leadership"
    af = tmp_path / "answers.json"
    af.write_text(json.dumps(answers))
    r = runner("routes", str(af), "--file", str(ef))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "Routing: 27/30 router evals (90%); floor 90%." in r.stdout
    answers["1003"] = "leadership"
    af.write_text(json.dumps(answers))
    r = runner("routes", str(af), "--file", str(ef))
    assert r.returncode == 1 and "Routing: 26/30 router evals (87%); floor 90%." in r.stdout


def test_p4h_eval_98_does_not_echo_the_hub_table():
    """X39: no router prompt repeats a four-word run of the hub's routing-table rows (here: eval 98)."""
    import re
    hub = (ROOT / "skills" / "learnings-coach" / "SKILL.md").read_text(encoding="utf-8")
    e98 = next(e for e in json.loads(EVALS.read_text(encoding="utf-8"))["evals"] if e["id"] == 98)

    def grams(t):
        w = re.findall(r"[a-z]+", t.lower())
        return {tuple(w[i:i + 4]) for i in range(len(w) - 3)}
    rows = "\n".join(line for line in hub.splitlines() if line.startswith("| ") and "`" in line)
    assert not grams(e98["prompt"]) & grams(rows)


# ------------------------------------------------- Task 24: format evals and the command_contains expectation

def _cmd_eval(tmp_path, exps, eid=7):
    data = {"skill_name": "probematrix-learnings-coach", "evals": [
        {"id": eid, "owner": "supervisor-coach", "skill": "supervisor-coach", "kind": "trigger", "prompt": "p",
         "files": [], "expectations": exps}]}
    f = tmp_path / "evals-cmd.json"
    f.write_text(json.dumps(data))
    return f


def test_p4s_command_contains_check(tmp_path):
    f = _cmd_eval(tmp_path, [{"type": "command_contains"},
                             {"type": "command_contains", "command": "Pack now", "flags": ["docx"], "contains": "x"},
                             {"type": "command_contains", "command": "pack", "flags": {"format": 3}}])
    out = runner("check", "--file", str(f)).stdout
    for msg in ("eval 7: command_contains needs command", "eval 7: command_contains: command must be a pmlc subcommand",
                "eval 7: command_contains: flags must map flag names to values",
                "eval 7: command_contains: contains must be a list of strings"):
        assert msg in out, (msg, out)
    ok = _cmd_eval(tmp_path, [{"type": "command_contains", "command": "pack",
                               "flags": {"format": "docx", "layout": "paper"}, "contains": ["board-brief.json"]}])
    assert "command_contains" not in runner("check", "--file", str(ok)).stdout


def test_p4s_command_contains_grade(tmp_path):
    rd = _run_folder(tmp_path)
    exps = [{"type": "pack_exists", "pack": "supervisor-coach"},
            {"type": "command_contains", "command": "pack", "flags": {"format": "docx", "layout": "checklist"},
             "contains": ["supervisor-coach.json"]}]
    f = _cmd_eval(tmp_path, exps)
    r = runner("grade", str(rd), "--file", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "| 7 | supervisor-coach | command_contains pack --format docx --layout checklist supervisor-coach.json | manual |" in r.stdout
    tr = tmp_path / "transcript.txt"
    tr.write_text("python3 skills/learnings-coach/scripts/pmlc.py check-pack ws o/supervisor-coach.json --strict\n"
                  "python3 skills/learnings-coach/scripts/pmlc.py pack ws o/supervisor-coach.json "
                  "--format=email,docx --layout checklist\n", encoding="utf-8")
    r = runner("grade", str(rd), "--file", str(f), "--transcript", str(tr))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "command_contains pack --format docx --layout checklist supervisor-coach.json | pass |" in r.stdout
    assert "Pass rate: 2/2" in r.stdout
    tr.write_text("PMLC pack ws o/supervisor-coach.json --format email --layout checklist\n"
                  "PMLC check-pack ws o/supervisor-coach.json --format docx --layout checklist\n", encoding="utf-8")
    r = runner("grade", str(rd), "--file", str(f), "--transcript", str(tr))
    assert r.returncode == 1
    assert "command_contains pack --format docx --layout checklist supervisor-coach.json | fail: no pmlc pack command with" in r.stdout
    r = runner("grade", str(rd), "--file", str(f), "--transcript", str(tmp_path / "none.txt"))
    assert r.returncode != 0 and "none.txt" in r.stderr


def test_p4s_format_evals():
    """Task 24: at least six format evals, each a trigger eval that expects its skill and a pmlc command with the
    format or layout flag; every flag value is a registered format or layout."""
    sys.path.insert(0, str(ROOT / "skills" / "learnings-coach" / "scripts"))
    from pmlc_lib import render
    from pmlc_lib.render.layouts import LAYOUTS
    known = set(render.FORMATS) | set(LAYOUTS) | {"scorm"}          # scorm: Task 21, merged in the same wave
    evals = json.loads(EVALS.read_text(encoding="utf-8"))["evals"]
    fmt = [e for e in evals if any(x["type"] == "command_contains" for x in e["expectations"])]
    assert len(fmt) >= 6
    for e in fmt:
        assert e["kind"] == "trigger" and e["skill"] == e["owner"], e["id"]
        assert {"type": "routes_to", "skill": e["skill"]} in e["expectations"], e["id"]
        for x in e["expectations"]:
            if x["type"] == "command_contains" and x["command"] == "pack":
                vals = [v for k, v in x.get("flags", {}).items() if k in ("format", "layout")]
                assert vals and set(vals) <= known, (e["id"], vals)
