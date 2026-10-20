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
import re
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
    "language_clean": ("pack",),
    "pack_absent": ("pack",),
    "card_fields": ("pack", "fields"),
}
ABS_PATH = re.compile(r"(?:^|[\s\"'(])(?:/(?:home|Users|tmp|var|mnt|opt|etc|root|srv)/|~/|[A-Za-z]:[\\/])")
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
    if kind == "trigger" and "owner" in e and e.get("skill") != e["owner"]:
        bad(f"{tag}: a trigger eval's skill must equal its owner")
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
    if kind == "trigger" and not files:
        bad(f"{tag}: a trigger eval needs files")
    if kind == "no-trigger" and files:
        bad(f"{tag}: a no-trigger eval has no files")
    for f in files:
        if isinstance(f, str) and (Path(f).is_absolute() or ABS_PATH.search(f)):
            bad(f"{tag}: files: absolute path {f}")
        elif not isinstance(f, str) or not (ROOT / f).exists():
            bad(f"{tag}: files: {f} does not exist")
    if isinstance(e.get("prompt"), str) and ABS_PATH.search(e["prompt"]):
        bad(f"{tag}: prompt: absolute path")
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
        if t == "routes_to":
            if x.get("skill") is not None and x.get("skill") not in SKILLS:
                bad(f"{tag}: routes_to: {x.get('skill')} is not a skill folder")
            if "skill" in e and x.get("skill") != e.get("skill"):
                bad(f"{tag}: routes_to must name the eval's skill")
        if t == "card_fields" and not (isinstance(x.get("fields"), list) and x["fields"]
                                       and all(isinstance(f, str) for f in x["fields"])):
            bad(f"{tag}: card_fields needs a non-empty list of field names")
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


_COV = {}                                    # (workspace, pack file) -> ratio; cleared by grade()


def _coverage(ws, pack, key=None) -> float:
    if key is not None and key in _COV:
        return _COV[key]
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import pmlc
    import pmlc_pack
    cov = pmlc_pack.coverage(pmlc.load_ws(ws), pack)
    ratio = 1.0 if not cov["relevant"] else cov["cited"] / cov["relevant"]
    if key is not None:
        _COV[key] = ratio
    return ratio


def _cards(pack) -> list:
    secs = pack.get("sections") if isinstance(pack, dict) else None
    out = []
    for sec in secs if isinstance(secs, list) else []:
        items = sec.get("items") if isinstance(sec, dict) else None
        out += [i for i in items if isinstance(i, dict) and i.get("kind") == "card"] if isinstance(items, list) else []
    return out


def grade_one(x, ws, out) -> tuple:
    """(result, detail) for one expectation; result is pass, fail or manual."""
    t = x["type"]
    if t == "routes_to":
        return "manual", ""
    path = out / f"{x['pack']}.json"
    if t == "pack_absent":
        return ("fail", f"{path.name} exists") if path.exists() else ("pass", "")
    if not path.exists():
        return "fail", f"{path.name} not found"
    if t == "pack_exists":
        return "pass", ""
    if t in ("check_pack_ok", "check_register_ok", "language_clean"):
        cmd = {"check_pack_ok": "check-pack", "check_register_ok": "check-register",
               "language_clean": "check-language"}[t]
        ok, msg = _engine(cmd, ws, path)
        return ("pass", "") if ok else ("fail", msg)
    try:
        pack = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as e:
        return "fail", f"{path.name} is not JSON: {e}"
    if not isinstance(pack, dict):
        return "fail", f"{path.name} is not a JSON object"
    if t == "scope_equals":
        got = pack.get("scope")
        return ("pass", "") if got == x["scope"] else ("fail", f"scope is {json.dumps(got)}")
    if t == "card_fields":
        cards = _cards(pack)
        if not cards:
            return "fail", "no cards"
        for f in x["fields"]:
            n = sum(1 for c in cards if not c.get(f))
            if n:
                return "fail", f"{n} of {len(cards)} cards lack {f}"
        return "pass", ""
    if not isinstance(pack.get("scope"), (dict, type(None))):
        return "fail", "scope is not an object"
    try:
        ratio = _coverage(ws, pack, (str(ws), str(path)))
    except Exception as e:                   # a malformed pack must fail the check, not crash the grader
        return "fail", f"cannot compute coverage ({e.__class__.__name__})"
    return ("pass" if ratio >= x["ratio"] else "fail"), f"{ratio:.2f}"


def _label(x) -> str:
    t = x["type"]
    if t == "routes_to":
        return f"routes_to {x.get('skill') or '(no learnings-coach skill)'}"
    if t == "coverage_min":
        return f"coverage_min {x['pack']} >= {x['ratio']}"
    return f"{t} {x['pack']}"


def grade(run_dir, path, ids=None) -> int:
    _COV.clear()
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
    if not total:
        print("\nno outputs graded")
        return 1
    rate = f"{100 * passed / total:.0f}%"
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
