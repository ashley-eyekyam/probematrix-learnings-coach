#!/usr/bin/env python3
"""Check and grade the ProbeMatrix Learnings Coach eval set (evals/evals.json).

  run_evals.py check [--file F]                     structure, paths, kinds and per-skill counts (CI runs this)
  run_evals.py grade <run-dir> [--ids 3,7] [--file F]
                                                    machine checks against <run-dir>/outputs and <run-dir>/workspace

Standard library only (Python 3.9+). `grade` calls the engine for check-pack / check-register and reuses
pmlc_pack.coverage for coverage_min. `routes_to` needs a human (or a transcript) and is reported as `manual`.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "evals" / "evals.json"
SCRIPTS = ROOT / "skills" / "learnings-coach" / "scripts"
ENGINE = SCRIPTS / "pmlc.py"
SKILLS = sorted(p.name for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").exists())
KINDS = ("trigger", "no-trigger", "collision")
REQUIRED = ("id", "owner", "skill", "kind", "prompt", "files", "expectations")
EXPECT = {                                   # expectation type -> its required parameters
    "pack_exists": ("pack",),
    "check_pack_ok": ("pack",),
    "check_register_ok": ("pack",),
    "scope_equals": ("pack", "scope"),
    "coverage_min": ("pack", "ratio"),
    "routes_to": ("skill",),
}
MIN_EVALS, MIN_NO_TRIGGER, MIN_COLLISION = 3, 1, 1


def load(path) -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        sys.exit(f"Cannot read {path}: {e}")


# ----------------------------------------------------------------------------- check

def _check_eval(e, seen, bad):
    eid = e.get("id")
    tag = f"eval {eid}"
    for k in REQUIRED:
        if k not in e:
            bad(f"{tag}: missing {k}")
    if not isinstance(eid, int) or isinstance(eid, bool):
        bad(f"{tag}: id must be an integer")
    elif eid in seen:
        bad(f"{tag}: duplicate id")
    seen.add(eid)
    kind = e.get("kind")
    if kind not in KINDS:
        bad(f"{tag}: kind: {kind} is not one of {', '.join(KINDS)}")
    if "owner" in e and e["owner"] not in SKILLS:
        bad(f"{tag}: owner: {e['owner']} is not a skill folder")
    if not isinstance(e.get("prompt"), str) or not e.get("prompt", "").strip():
        bad(f"{tag}: prompt must be non-empty text")
    if kind == "no-trigger":
        if e.get("skill") is not None:
            bad(f"{tag}: a no-trigger eval has skill null")
        if e.get("not_skill") != e.get("owner"):
            bad(f"{tag}: not_skill must name the owner skill")
    elif "skill" in e and e["skill"] not in SKILLS:
        bad(f"{tag}: skill: {e['skill']} is not a skill folder")
    if kind == "collision":
        sib = e.get("sibling")
        if sib is None:
            bad(f"{tag}: collision needs a sibling")
        elif sib not in SKILLS:
            bad(f"{tag}: sibling: {sib} is not a skill folder")
        elif sib == e.get("skill"):
            bad(f"{tag}: sibling must differ from skill")
    elif "sibling" in e:
        bad(f"{tag}: only a collision eval has a sibling")
    files = e.get("files", [])
    if not isinstance(files, list):
        bad(f"{tag}: files must be a list")
        files = []
    for f in files:
        if not isinstance(f, str) or not (ROOT / f).exists():
            bad(f"{tag}: files: {f} does not exist")
    exps = e.get("expectations", [])
    if not isinstance(exps, list):
        bad(f"{tag}: expectations must be a list")
        exps = []
    for x in exps:
        t = x.get("type") if isinstance(x, dict) else None
        if t not in EXPECT:
            bad(f"{tag}: unknown expectation type {t}")
            continue
        for p in EXPECT[t]:
            if p not in x:
                bad(f"{tag}: {t} needs {p}")
        if t == "routes_to" and x.get("skill") is not None and x.get("skill") not in SKILLS:
            bad(f"{tag}: routes_to: {x.get('skill')} is not a skill folder")
        if t == "coverage_min" and not (isinstance(x.get("ratio"), (int, float)) and 0 <= x.get("ratio", -1) <= 1):
            bad(f"{tag}: coverage_min ratio must be between 0 and 1")


def check(path) -> int:
    data = load(path)
    problems = []
    bad = problems.append
    if data.get("skill_name") != "probematrix-learnings-coach":
        bad("skill_name: must be probematrix-learnings-coach")
    sample = data.get("sample")
    if not isinstance(sample, str) or not (ROOT / sample).exists():
        bad(f"sample: {sample} does not exist")
    evals = data.get("evals")
    if not isinstance(evals, list) or not evals:
        bad("evals: must be a non-empty list")
        evals = []
    seen = set()
    for e in evals:
        if isinstance(e, dict):
            _check_eval(e, seen, bad)
        else:
            bad("evals: every entry must be an object")
    evals = [e for e in evals if isinstance(e, dict)]
    owned = Counter(e.get("owner") for e in evals)
    kinds = Counter((e.get("owner"), e.get("kind")) for e in evals)
    for s in SKILLS:
        if owned[s] < MIN_EVALS:
            bad(f"{s}: needs at least {MIN_EVALS} evals (has {owned[s]})")
        if kinds[(s, "no-trigger")] < MIN_NO_TRIGGER:
            bad(f"{s}: needs at least {MIN_NO_TRIGGER} no-trigger eval")
        if kinds[(s, "collision")] < MIN_COLLISION:
            bad(f"{s}: needs at least {MIN_COLLISION} collision eval")
    by_kind = Counter(e.get("kind") for e in evals)
    print(f"{len(evals)} evals over {len(SKILLS)} skills: "
          + ", ".join(f"{by_kind[k]} {k}" for k in KINDS))
    if problems:
        print(f"{len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("OK")
    return 0


# ----------------------------------------------------------------------------- grade

def _engine(cmd, ws, path) -> tuple:
    r = subprocess.run([sys.executable, str(ENGINE), cmd, str(ws), str(path)], capture_output=True, text=True)
    last = (r.stdout + r.stderr).strip().splitlines()
    return r.returncode == 0, (last[-1] if last else f"exit {r.returncode}")


def _coverage(ws, pack) -> float:
    sys.path.insert(0, str(SCRIPTS))
    import pmlc
    import pmlc_pack
    cov = pmlc_pack.coverage(pmlc.load_ws(ws), pack)
    return 1.0 if not cov["relevant"] else cov["cited"] / cov["relevant"]


def grade_one(x, ws, out) -> tuple:
    """(result, detail) for one expectation; result is pass, fail or manual."""
    t = x["type"]
    if t == "routes_to":
        return "manual", ""
    path = out / f"{x['pack']}.json"
    if not path.exists():
        return "fail", f"{path.name} not found"
    if t == "pack_exists":
        return "pass", ""
    if t in ("check_pack_ok", "check_register_ok"):
        ok, msg = _engine("check-pack" if t == "check_pack_ok" else "check-register", ws, path)
        return ("pass", "") if ok else ("fail", msg)
    try:
        pack = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as e:
        return "fail", f"{path.name} is not JSON: {e}"
    if t == "scope_equals":
        got = pack.get("scope")
        return ("pass", "") if got == x["scope"] else ("fail", f"scope is {json.dumps(got)}")
    ratio = _coverage(ws, pack)
    return ("pass" if ratio >= x["ratio"] else "fail"), f"{ratio:.2f}"


def _label(x) -> str:
    t = x["type"]
    if t == "routes_to":
        return f"routes_to {x.get('skill') or '(no learnings-coach skill)'}"
    if t == "coverage_min":
        return f"coverage_min {x['pack']} >= {x['ratio']}"
    return f"{t} {x['pack']}"


def grade(run_dir, path, ids=None) -> int:
    run_dir = Path(run_dir)
    ws, out = run_dir / "workspace", run_dir / "outputs"
    if not (ws / "findings.json").exists():
        sys.exit(f"No workspace with findings.json under {run_dir}. Pass a run folder (<run>/workspace, <run>/outputs).")
    evals = load(path).get("evals", [])
    if ids:
        chosen = [e for e in evals if e.get("id") in ids]
        missing = sorted(set(ids) - {e.get("id") for e in chosen})
        if missing:
            sys.exit(f"No eval with id {', '.join(map(str, missing))} in {path}.")
    else:
        chosen = [e for e in evals
                  if any("pack" in x and (out / f"{x['pack']}.json").exists() for x in e.get("expectations", []))]
    print("| id | skill | expectation | pass/fail |")
    print("|---|---|---|---|")
    passed = total = 0
    for e in chosen:
        for x in e.get("expectations", []):
            res, detail = grade_one(x, ws, out)
            if res != "manual":
                total += 1
                passed += res == "pass"
            cell = f"{res}: {detail}" if detail else res
            print(f"| {e['id']} | {e.get('skill') or '(none)'} | {_label(x)} | {cell.replace('|', '/')} |")
    rate = f"{100 * passed / total:.0f}%" if total else "n/a"
    print(f"\nGraded {len(chosen)} eval(s). Pass rate: {passed}/{total} machine checks ({rate}); routes_to is manual.")
    return 0 if passed == total else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="run_evals", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="validate evals.json structure, paths and per-skill counts")
    c.add_argument("--file", default=str(DEFAULT))
    g = sub.add_parser("grade", help="grade machine expectations against a run folder")
    g.add_argument("run_dir")
    g.add_argument("--ids", help="comma-separated eval ids (default: evals whose packs exist in the run)")
    g.add_argument("--file", default=str(DEFAULT))
    a = ap.parse_args(argv)
    if a.cmd == "check":
        return check(a.file)
    ids = None
    if a.ids:
        try:
            ids = [int(i) for i in a.ids.split(",") if i.strip()]
        except ValueError:
            sys.exit("--ids takes comma-separated integers, for example --ids 3,7.")
    return grade(a.run_dir, a.file, ids)


if __name__ == "__main__":
    sys.exit(main())
