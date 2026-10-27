"""pmlc plan: resolve a workflow preset, audiences or skills into an ordered, tracked plan (spec §2.2).

plan.json is deterministic (Ruling P3-16): no timestamps and no absolute paths. Commands use the literal
placeholders PMLC, <ws> and <run>; only the printed plan substitutes the real ones. A preset step whose skill has not
shipped carries "planned": "Phase N" and is listed as planned and skipped (P3-17); any other unknown skill, a
dependency cycle or a requirement nothing produces exits 1 with a sentence naming it.
"""
from __future__ import annotations

import json
import os
import shlex
import sys
from pathlib import Path

from . import contracts
from .util import HERE, write_json
from .workspace import (check_current, load_manifest, manifest_state_hash, outputs_dir, record_derived,
                        stale_files, taxonomy_hash)

PLAN = "plan.json"
PLAN_VERSION = 1
PMLC_PATH = HERE / "pmlc.py"
REGISTER_PACK = "learnings-register"


def _split(v) -> list:
    out = []
    for x in v if isinstance(v, (list, tuple)) else [v]:
        out += [t.strip() for t in str(x).split(",") if t.strip()]
    return list(dict.fromkeys(out))


TEMPLATE_MODES = {"learning-team-notes": "learning-team"}   # an artefact whose `templates` mode is not its name


def _engine_commands(cmd: str, produces: list) -> list:
    if cmd == "ingest":
        return ["PMLC ingest <export.xlsx> --slug <site>-<event>"]
    if cmd == "templates":
        return [f"PMLC templates <ws> {TEMPLATE_MODES.get(a, a)}" for a in produces]
    return [f"PMLC {cmd} <ws>"]


class _Resolver:
    def __init__(self, manifests, artefacts, presets):
        self.manifests, self.artefacts, self.presets = manifests, artefacts, presets
        self.nodes, self.order, self.done = {}, [], set()

    def _node(self, key, **kw):
        n = self.nodes.setdefault(key, {"produces": [], "mode": None, "when": None, "planned": None})
        for k, v in kw.items():
            if k == "produces":
                n["produces"] += [a for a in v if a not in n["produces"]]
            elif v is not None and n.get(k) is None:
                n[k] = v
        return n

    def request(self, step: dict) -> None:
        sk = step["skill"]
        if sk.startswith("engine:"):
            made = [a for a, d in self.artefacts.items() if d.get("producer") == sk]
            if step.get("mode") in made:
                made = [step["mode"]]
            self._node(sk, produces=made, mode=step.get("mode"), when=step.get("when"))
            self._visit(sk, [])
            return
        if sk not in self.manifests:
            if step.get("planned"):
                self._node(sk, planned=step["planned"], mode=step.get("mode"), when=step.get("when"))
                self._visit(sk, [])
                return
            sys.exit(f"unknown skill: {sk} (skills: {', '.join(sorted(self.manifests))})")
        self._node(sk, mode=step.get("mode"), when=step.get("when"))
        self._visit(sk, [])

    def _deps(self, key) -> list:
        m = self.manifests.get(key)
        if m is None:   # an engine step or a planned skill: no recorded requirements
            return []
        out = []
        for r in m["requires"]:   # optional_inputs never create an edge
            art = self.artefacts.get(r)
            if art is None:
                sys.exit(f"nothing produces '{r}', which {key} requires (it is not in artefacts.json)")
            kind, _, who = str(art.get("producer", "")).partition(":")
            if kind == "engine":
                self._node(f"engine:{who}", produces=[r])
                out.append(f"engine:{who}")
            elif kind == "skill" and who in self.manifests:
                self._node(who)
                out.append(who)
            elif kind == "skill" and art.get("planned"):
                self._node(who, planned=art["planned"])
                out.append(who)
            else:
                sys.exit(f"nothing produces '{r}', which {key} requires (its producer {art.get('producer')} "
                         "is not a shipped skill)")
        return out

    def _visit(self, key, stack) -> None:
        """Depth-first, dependencies first: the post-order is a topological order that keeps the request order
        wherever the dependencies allow (the same order Kahn's algorithm gives with a queue ranked by it)."""
        if key in self.done:
            return
        if key in stack:
            sys.exit("cycle: " + " -> ".join(stack[stack.index(key):] + [key]))
        stack.append(key)
        for d in self._deps(key):
            self._visit(d, stack)
        stack.pop()
        self.done.add(key)
        self.order.append(key)


def _file(ws: Path, rel: str) -> Path:
    """An artefact's run-relative file in this workspace's layout (legacy workspaces keep outputs/ inside)."""
    head, _, rest = rel.partition("/")
    if head == "workspace":
        return ws / rest
    if head == "outputs":
        return outputs_dir(ws) / rest
    return outputs_dir(ws).parent / rel


def _checked(manifest, path: Path, strict: bool = False) -> bool:
    if not path.is_file():
        return False
    return check_current(manifest, path, strict=strict)


def _step(key, node, ctx) -> dict:
    ws, manifest, stale, arts, manifests, presets = ctx
    st = {"n": 0, "skill": key, "status": "todo", "planned_for": None, "produces": None, "mode": node["mode"],
          "when": node["when"], "commands": [], "questions": [], "gate": []}
    if node["planned"]:
        st.update(status="planned", planned_for=node["planned"])
        return st
    if key.startswith("engine:"):
        made = node["produces"]
        st["produces"] = ",".join(made) or None
        st["commands"] = _engine_commands(key.split(":", 1)[1], made)
        files = [_file(ws, arts[a]["file"]) for a in made if not arts[a]["file"].startswith("$")]
        current = all(f.is_file() and (f.parent != ws or (f.name in manifest.get("files", {}) and
                                                          f.name not in stale)) for f in files)
        if files and current:
            st["status"] = "done"
        return st
    m = manifests[key]
    pack = m["produces"]["pack"]
    mine = [a for a, d in arts.items() if d.get("producer") == f"skill:{key}"]
    st["produces"] = mine[0] if mine else pack
    st["questions"] = list(m.get("questions", []))
    cmds = [f"PMLC select <ws> --preset {key}:{p['name']}" for p in presets.get(key, [])]
    if pack is None:
        st["commands"] = cmds
        return st
    target = f"<run>/outputs/{pack}.json"
    if pack == REGISTER_PACK:
        cmds += [f"PMLC check-register <ws> {target} --strict", f"PMLC register-xlsx {target}",
                 f"PMLC register-md <ws> {target}"]
        st["gate"] = ["check-register --strict"]
    else:
        if m["kind"] == "dissemination":
            cmds.append(f"PMLC dashboard <ws> --register <run>/outputs/{REGISTER_PACK}.json")
        cmds += [f"PMLC check-pack <ws> {target} --strict", f"PMLC pack <ws> {target}"]
        st["gate"] = ["check-pack --strict"]
    if m["share_default"] in ("external", "public"):
        st["gate"].append("approved review")
    st["commands"] = cmds
    strict = any("--strict" in g for g in st["gate"])     # the gate the plan prints is the one done-detection needs
    if "<" not in pack and _checked(manifest, outputs_dir(ws) / f"{pack}.json", strict=strict):
        st["status"] = "done"
    return st


def next_step(plan: dict) -> dict | None:
    """The first step still to do (planned and done steps are skipped), or None when the plan is complete."""
    return next((s for s in plan["steps"] if s["status"] == "todo"), None)


def build(w, run=None, *, workflow=None, audiences=(), skills=(), skills_root=None, refs=None) -> dict:
    """The plan.json dict for workspace folder w. Exactly one of workflow, audiences or skills names the request.
    skills_root and refs default to the installed skills/ folder and learnings-coach/references/."""
    ws = Path(w)
    manifests = contracts.load_manifests(skills_root)
    arts = contracts.load_artefacts(refs)
    presets = json.loads(((Path(refs) if refs else contracts.REFS) / "select-presets.json").read_text(
        encoding="utf-8"))
    r = _Resolver(manifests, arts, presets)
    audiences, skills = _split(audiences) if audiences else [], _split(skills) if skills else []
    if workflow:
        wfs = contracts.load_workflows(refs)
        if workflow not in wfs:
            sys.exit(f"unknown workflow: {workflow} (presets: {', '.join(wfs)})")
        req = [dict(s) for s in wfs[workflow]["steps"]]
    elif audiences:
        by_id = {a["id"]: a["skill"] for a in contracts.load_audiences(refs)}
        bad = [a for a in audiences if a not in by_id]
        if bad:
            sys.exit(f"unknown audience: {', '.join(bad)} (audiences: {', '.join(by_id)})")
        req = [{"skill": by_id[a]} for a in audiences]
    elif skills:
        req = [{"skill": s} for s in skills]
    else:
        sys.exit("plan needs --workflow, --audiences or --skills")
    for s in req:
        r.request(s)
    manifest = load_manifest(ws)
    stale = dict(stale_files(ws))
    ctx = (ws, manifest, stale, arts, manifests, presets)
    steps = []
    for i, key in enumerate(r.order, 1):
        st = _step(key, r.nodes[key], ctx)
        st["n"] = i
        steps.append(st)
    plan = {"plan_version": PLAN_VERSION,
            "request": {"workflow": workflow or None, "audiences": audiences, "skills": skills},
            "steps": steps, "next": None}
    nxt = next_step(plan)
    plan["next"] = nxt["n"] if nxt else None
    return plan


def write_plan(ws, plan: dict, skills_root=None) -> Path:
    """Write <ws>/plan.json and record it in the manifest, built from the manifest state and the contracts."""
    ws = Path(ws)
    paths = [p for p in contracts.contract_paths(skills_root) if p.is_file()]
    inputs = {"manifest.json": manifest_state_hash(ws), "contracts": taxonomy_hash(paths)}
    write_json(ws / PLAN, plan)
    record_derived(ws, PLAN, inputs, sources={"contracts": [str(p) for p in paths]})
    return ws / PLAN


def _real(text: str, ws: Path, run: Path, relative: bool = False) -> str:
    """A command with the real engine, workspace and run paths (relative to the current folder when the workspace
    was given as a relative path)."""
    def q(p):
        return shlex.quote(os.path.relpath(p) if relative else str(p))
    return text.replace("PMLC ", f"python3 {q(PMLC_PATH)} ", 1).replace("<ws>", q(ws)).replace("<run>", q(run))


def step_lines(st: dict, ws: Path, run: Path, relative: bool = False) -> list:
    if st["status"] == "planned":
        return [f"{st['n']:2}. {st['skill']} [planned for v2.0, {st['planned_for']}]"]
    extra = "".join(f" ({k} {st[k]})" for k in ("mode",) if st[k])
    out = [f"{st['n']:2}. {st['skill']} [{st['status']}]{extra}"]
    if st["status"] == "done":
        return out
    if st["when"]:
        out.append(f"      when: {st['when']}")
    out += [f"      ask: {q}" for q in st["questions"]]
    out += [f"      {_real(c, ws, run, relative)}" for c in st["commands"]]
    if st["gate"]:
        out.append(f"      gate: {', '.join(st['gate'])}")
    return out


def _title(req: dict, refs=None) -> str:
    if req["workflow"]:
        return f"Plan: {req['workflow']} ({contracts.load_workflows(refs)[req['workflow']]['title']})"
    if req["audiences"]:
        return f"Plan: audiences {', '.join(req['audiences'])}"
    return f"Plan: skills {', '.join(req['skills'])}"


def cmd_plan(a):
    ws = Path(a.ws).resolve()
    if not (ws / "findings.json").is_file():
        sys.exit(f"No findings.json in {ws}. Run: pmlc.py ingest <export.xlsx> --slug <site>-<event>")
    run = outputs_dir(ws).parent
    if a.next:
        try:
            req = json.loads((ws / PLAN).read_text(encoding="utf-8"))["request"]
        except (OSError, ValueError, KeyError, TypeError):
            sys.exit(f"no plan in {ws}: run pmlc plan {ws} --workflow NAME (or --audiences, --skills) first")
    else:
        req = {"workflow": a.workflow, "audiences": _split(a.audiences or []), "skills": _split(a.skills or [])}
    plan = build(ws, run, workflow=req.get("workflow"), audiences=req.get("audiences") or (),
                 skills=req.get("skills") or ())
    write_plan(ws, plan)
    nxt = next_step(plan)
    rel = not Path(a.ws).is_absolute()
    if a.json:
        print(json.dumps(plan, indent=1, ensure_ascii=False))
    elif a.next:
        if nxt:
            print("Next step:")
            print("\n".join(step_lines(nxt, ws, run, rel)))
        else:
            print("The plan is complete: every step is done or planned for a later phase.")
    else:
        print(_title(plan["request"]))
        for st in plan["steps"]:
            print("\n".join(step_lines(st, ws, run, rel)))
        print(f"Next: step {nxt['n']}" if nxt else "Next: none, the plan is complete")
    if a.next and not nxt:
        sys.exit(2)
