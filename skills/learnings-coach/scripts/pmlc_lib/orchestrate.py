"""Orchestration commands: setup, check-all, render-all, index and dossier-index (Ruling P3-23, P3-27)."""
from __future__ import annotations

import contextlib
import datetime as dt
import io
import json
import re
import string
import sys
from html import escape
from pathlib import Path

from . import BRAND, DRAFT_LABEL, STATUS_PHRASE
from .handling import effective_handling
from .util import HERE, write_json
from .workspace import file_sha256, load_manifest, load_ws, outputs_dir, pack_record

REGISTER_NAME = "learnings-register.json"
TEMPLATES = Path(__file__).resolve().parent / "dashboard" / "templates"


def _run(argv, capture=True):
    """Parse argv with the real parser and run its command in-process: (exit code, stdout, stderr)."""
    from .cli import build_parser   # cli imports this module
    out, err = io.StringIO(), io.StringIO()
    code = 0
    ctx = (contextlib.redirect_stdout(out), contextlib.redirect_stderr(err)) if capture else ()
    with contextlib.ExitStack() as st:
        for c in ctx:
            st.enter_context(c)
        try:
            a = build_parser().parse_args(argv)
            a._argv = list(argv)
            a.fn(a)
        except SystemExit as e:
            c = e.code
            if c is None or c == 0:
                code = 0
            else:
                code = c if isinstance(c, int) else 1
                if not isinstance(c, int):
                    print(c, file=sys.stderr)
    return code, out.getvalue(), err.getvalue()


def _pack_files(out: Path) -> list:
    """Pack files in outputs/ (Ruling P3-23): JSON objects with a sections list, the register excluded."""
    found = []
    for p in sorted(out.glob("*.json")) if out.is_dir() else []:
        if p.name == REGISTER_NAME:
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(d, dict) and isinstance(d.get("sections"), list):
            found.append((p, d))
    return found


# ----------------------------------------------------------------------------- setup

def cmd_setup(a):
    ws = None
    ing = ["ingest", a.xlsx, "--slug", a.slug]
    for flag, v in (("--date", a.date), ("--root", a.root), ("--redact", a.redact)):
        if v:
            ing += [flag, v]
    ing += (["--force"] if a.force else []) + (["--strict"] if a.strict else [])
    steps = [("ingest", ing)]
    for name in ("profile", "classify", "causal", "timeline", "interfaces"):
        steps.append((name, None))
    for name, argv in steps:
        if argv is None:
            argv = [name, str(ws)]
            if name == "profile":
                argv += ["--out", str(ws / "profile.md")]
            if name == "classify" and a.overlay:
                argv += ["--overlay", a.overlay]
        code, out, err = _run(argv)
        if code:
            sys.stderr.write(out + err)
            sys.exit(f"setup stopped at {name}")
        if name == "ingest":
            m = re.search(r"-> (.+)$", out, re.M)
            if not m:
                sys.exit("setup stopped at ingest")
            ws = Path(m.group(1).strip())
    w = load_ws(ws)
    cl = w.get("clusters", {})
    unresolved = cl.get("unresolved_roles", [])
    print(f"Ingested {len(w['findings'])} findings and {len(w.get('evidence', {}))} evidence items")
    print(f"Unresolved roles ({len(unresolved)}): " + ("; ".join(unresolved) if unresolved else "none"))
    prof = (ws / "profile.md").read_text(encoding="utf-8")
    flags = prof.split("## Data-quality flags", 1)[-1].split("\n---", 1)[0].strip().splitlines()
    print("Profile flags:")
    for line in [x for x in flags if x.strip()]:
        print(f"  {line}")
    print(f"Workspace: {ws}")
    try:
        names = ", ".join(json.loads((HERE.parent / "references" / "workflows.json").read_text(encoding="utf-8")))
    except (OSError, ValueError):
        names = ""
    print(f"Next: PMLC plan {ws} --workflow <name>" + (f"  (workflows: {names})" if names else ""))


# ----------------------------------------------------------------------------- check-all

def _check_pack_argv(ws, path, strict):
    argv = ["check-pack", str(ws), str(path)]
    if strict:
        from .cli import build_parser
        if "--strict" in _flags(build_parser(), "check-pack"):
            argv.append("--strict")
    return argv


def _flags(parser, name):
    for act in parser._actions:
        if hasattr(act, "choices") and isinstance(act.choices, dict) and name in act.choices:
            return {o for x in act.choices[name]._actions for o in x.option_strings}
    return set()


def _problem_count(code, out, err):
    m = re.findall(r"(\d+) problem\(s\)", out + err)
    return int(m[-1]) if m else (1 if code else 0)


def _check_all_results(a):
    ws = Path(a.ws)
    out = outputs_dir(ws)
    results = []
    for p, _ in _pack_files(out):
        code, so, se = _run(_check_pack_argv(ws, p, a.strict))
        results.append({"file": p.name, "kind": "pack", "ok": code == 0, "problems": _problem_count(code, so, se),
                        "detail": [x for x in se.splitlines() if x.strip()]})
    reg = out / REGISTER_NAME
    if reg.is_file():
        code, so, se = _run(["check-register", str(ws), str(reg)])
        results.append({"file": reg.name, "kind": "register", "ok": code == 0, "problems": _problem_count(code, so, se),
                        "detail": [x for x in so.splitlines() if x.startswith(" - ")]})
    return results


def cmd_check_all(a):
    ws = Path(a.ws)
    if not ws.is_dir():
        sys.exit(f"{ws} is not a folder.")
    load_ws(ws)
    results = _check_all_results(a)
    say = sys.stderr if a.json else sys.stdout
    if not results:
        print("No packs or register found in outputs/.", file=say)
    for r in results:
        print(f"{r['file']}: " + ("ok" if r["ok"] else f"{r['problems']} problem(s)"), file=say)
        for line in ([] if r["ok"] else r["detail"]):
            print(f"  {line}", file=sys.stderr)
    bad = [r for r in results if not r["ok"]]
    if a.json:
        print(json.dumps({"ok": not bad, "files": [{k: r[k] for k in ("file", "kind", "ok", "problems")}
                                                   for r in results]}))
    if bad:
        sys.exit(1)


# ----------------------------------------------------------------------------- render-all

def cmd_render_all(a):
    ws = Path(a.ws)
    load_ws(ws)
    out = outputs_dir(ws)
    m = load_manifest(ws)
    share_flags = [x for flag, v in (("--share", a.share), ("--names", a.names), ("--orgs", a.orgs)) if v
                   for x in (flag, v)]
    extra = (["--embed", a.embed] if a.embed else []) + share_flags   # pack and dashboard take both
    failed = 0

    def go(label, argv):
        nonlocal failed
        code, so, se = _run(argv)
        sys.stdout.write(so)
        sys.stderr.write(se)
        if code:
            failed += 1
            print(f"failed {label}", file=sys.stderr)

    for p, _ in _pack_files(out):
        rec = pack_record(m, p)
        if not (rec and rec.get("ok") and rec.get("sha256") == file_sha256(p)):
            print(f"skipped {p.name}: run check-all first")
            continue
        go(p.name, ["pack", str(ws), str(p)] + extra)
    reg = out / REGISTER_NAME
    if reg.is_file():
        code, _, _ = _run(["check-register", str(ws), str(reg)])
        if code:
            print(f"skipped {reg.name}: run check-all first")
        else:
            # register-xlsx has no --embed
            go("register-xlsx", ["register-xlsx", str(reg), "--ws", str(ws)] + share_flags)
            from .cli import build_parser
            if "register-md" in {c for act in build_parser()._actions
                                 for c in (getattr(act, "choices", None) or {}) if isinstance(c, str)}:
                go("register-md", ["register-md", str(ws), str(reg)])
            else:
                print("note: register-md is not available in this engine; register Markdown skipped")
            go("dashboard", ["dashboard", str(ws), "--register", str(reg)] + extra)
    if failed:
        sys.exit(1)


# ----------------------------------------------------------------------------- index

def _skill_audiences() -> dict:
    """pack name -> audiences, from skills/<skill>/skill.json."""
    res = {}
    for f in sorted((HERE.parent.parent).glob("*/skill.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(d, dict):
            continue
        aud = d.get("audiences") or []
        names = {d.get("name")}
        prod = d.get("produces")
        if isinstance(prod, dict):
            names.add(prod.get("pack"))
        for n in names:
            if isinstance(n, str):
                res.setdefault(n, aud)
    return res


def _coverage(rec) -> str:
    c = (rec or {}).get("coverage")
    if isinstance(c, dict) and "cited" in c and "relevant" in c:
        return f"{c['cited']} of {c['relevant']}"
    return str(c) if c not in (None, "") else "not recorded"


def _row(ws, w, out, dest, p, d, rec, aud, kind):
    stem = p.stem
    fmts = [f for f, ext in (("html", ".html"), ("md", ".md"), ("xlsx", ".xlsx")) if (out / f"{stem}{ext}").is_file()]
    eh = effective_handling(d, w, src=str(p), ws=str(ws))
    status = DRAFT_LABEL if eh["effective_status"] == "draft" else eh["effective_status"].capitalize()
    target = next((out / f"{stem}{e}" for e in (".html", ".xlsx", ".md") if (out / f"{stem}{e}").is_file()), p)
    link = Path(_relpath(target, dest.parent)).as_posix()
    title = d.get("title") if isinstance(d, dict) and isinstance(d.get("title"), str) else stem
    date = dt.date.fromtimestamp(p.stat().st_mtime).isoformat()
    cls = ' class="draft"' if status == DRAFT_LABEL else ""
    cells = [escape(title), escape(", ".join(aud) or "n/a"), escape(_coverage(rec)),
             escape(", ".join(fmts) or "json"), date, f'<span{cls}>{escape(status)}</span>',
             f'<a href="{escape(link, quote=True)}">{escape(target.name)}</a>']
    return "<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>"


def _relpath(target: Path, base: Path) -> str:
    import os
    return os.path.relpath(str(target.resolve()), str(base.resolve()))


def cmd_index(a):
    ws = Path(a.ws)
    w = load_ws(ws)
    out = outputs_dir(ws)
    dest = Path(a.out) if a.out else out / "index.html"
    m = load_manifest(ws)
    auds = _skill_audiences()
    rows = []
    for p, d in _pack_files(out):
        rows.append(_row(ws, w, out, dest, p, d, pack_record(m, p), auds.get(d.get("pack"), []), "pack"))
    reg = out / REGISTER_NAME
    if reg.is_file():
        try:
            rd = json.loads(reg.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            rd = {}
        rd = rd if isinstance(rd, dict) else {}
        rd.setdefault("title", "Learnings register")
        rows.append(_row(ws, w, out, dest, reg, rd, None, ["all"], "register"))
    inc = w.get("incident", {}).get("fields", {}).get("Incident Title", "")
    title = f"Learning outputs: {inc}" if inc else "Learning outputs"
    text = (TEMPLATES / "index.html").read_text(encoding="utf-8")
    page = string.Template(text).substitute(
        title=escape(title), status_phrase=escape(STATUS_PHRASE), brand=escape(BRAND),
        rows="\n".join(rows) if rows else '<tr><td colspan="7">No packs in outputs/ yet.</td></tr>')
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page, encoding="utf-8")
    print(f"Index written to {dest} ({len(rows)} row(s))")


# ----------------------------------------------------------------------------- dossier-index

def cmd_dossier_index(a):
    from .pack.schema import cited_ids
    ws = Path(a.ws)
    w = load_ws(ws)
    out = outputs_dir(ws)
    dossiers = [(p, d) for p, d in _pack_files(out) if re.fullmatch(r"dossier-F\d+[a-z]?", p.stem)]
    if not dossiers:
        sys.exit(f"no dossier-F*.json packs found in {out}")
    rows, cites, ents = [], [], []
    for p, d in dossiers:
        ent = (d.get("scope") or {}).get("entities") if isinstance(d.get("scope"), dict) else None
        ent = ent or [p.stem.split("-", 1)[1]]
        n_items = sum(len(s.get("items", [])) for s in d["sections"] if isinstance(s, dict)
                      and isinstance(s.get("items"), list))
        fids = cited_ids(d)[0]
        rows.append([", ".join(ent), d.get("title", p.stem), n_items])
        cites.append(fids)
        ents += [e for e in ent if e not in ents]
    flat = list(dict.fromkeys(x for c in cites for x in c))[:3]
    inc = w.get("incident", {}).get("fields", {}).get("Incident Title", "")
    pack = {
        "pack": "dossier-index", "schema": 1,
        "title": "Cluster learning dossiers" + (f": {inc}" if inc else ""),
        "audience": "Investigation team and site leadership", "status": STATUS_PHRASE,
        "bottom_line": [{"text": f"This run has {len(rows)} cluster learning dossier(s), one per part of the organisation.",
                         "cites": flat}],
        "scope": {"entities": ents},
        "sections": [{"id": "dossiers", "heading": "Dossiers in this run", "items": [
            {"kind": "table", "columns": ["Entity", "Dossier", "Items"], "rows": rows, "row_cites": cites}]}]}
    dest = Path(a.out) if a.out else out / "dossier-index.json"
    write_json(dest, pack)
    print(f"Dossier index written to {dest} ({len(rows)} dossier(s))")
