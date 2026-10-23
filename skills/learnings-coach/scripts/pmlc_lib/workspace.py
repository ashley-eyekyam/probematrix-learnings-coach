"""Run layout, workspace loading, the manifest, staleness, status and run-path."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path

from . import __version__
from .util import _abs, _overlay_path, _s, iso_date, REFS, write_json


def scan_comparator(path) -> tuple:
    """(sorted valid item ids, how many items have no valid id, None), or (None, 0, the reason it is unusable). An id
    is valid when it looks like OBS-01, RC-01, REC-01 or ACT-01. Never raises."""
    from .compare import ITEM_ID_RX
    try:
        c = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError, RecursionError) as e:
        return None, 0, f"cannot be read as JSON ({e.__class__.__name__})"
    if not isinstance(c, dict):
        return None, 0, "must be a JSON object"
    if not isinstance(c.get("items"), list):
        return None, 0, "has no items list"
    ids = {i["id"] for i in c["items"] if isinstance(i, dict) and isinstance(i.get("id"), str)
           and ITEM_ID_RX.fullmatch(i["id"])}
    bad = sum(1 for i in c["items"] if not (isinstance(i, dict) and isinstance(i.get("id"), str)
                                            and ITEM_ID_RX.fullmatch(i["id"])))
    return sorted(ids), bad, None


def read_comparator_ids(path) -> tuple:
    """(sorted item ids, None) of a comparator.json, or (None, the reason it is unusable). Never raises."""
    ids, _bad, why = scan_comparator(path)
    return ids, why


def load_ws(ws_dir: Path) -> dict:
    ws_dir = Path(ws_dir)
    out = {}
    for name in ("findings", "evidence", "incident", "clusters"):
        p = ws_dir / f"{name}.json"
        if p.exists():
            out[name] = json.loads(p.read_text(encoding="utf-8"))
    sp = ws_dir / "singleton_roles.json"
    out["singletons"] = json.loads(sp.read_text(encoding="utf-8")).get("roles", []) if sp.exists() else []
    cp = ws_dir / "comparator.json"   # the item ids check-pack validates comparator_refs against
    if cp.is_file():
        ids, bad, why = scan_comparator(cp)
        if why:
            out["comparator_error"] = why
        else:
            out["comparator_ids"] = ids
            if bad:
                out["comparator_bad_items"] = bad
    if "findings" not in out:
        sys.exit(f"No findings.json in {ws_dir}. Run: pmlc.py ingest <export.xlsx> --slug <site>-<event>")
    return out


# ----------------------------------------------------------------------------- manifest

MANIFEST = "manifest.json"
KNOWN_DERIVED = ("findings.json", "evidence.json", "incident.json", "clusters.json", "singleton_roles.json",
                 "causal_graph.json",
                 "causal_graph.mmd", "timeline_candidates.json", "timeline_event_day.json", "interfaces.json",
                 "hfacs_profile.json", "open_questions.json", "plan.json")
REBUILD = {"findings.json": "ingest", "evidence.json": "ingest", "incident.json": "ingest",
           "clusters.json": "classify", "singleton_roles.json": "classify", "causal_graph.json": "causal", "causal_graph.mmd": "causal",
           "timeline_candidates.json": "timeline", "timeline_event_day.json": "timeline",
           "interfaces.json": "interfaces", "hfacs_profile.json": "hfacs-profile", "open_questions.json": "open-questions",
           "plan.json": "plan"}


def file_sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _now() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def load_manifest(ws) -> dict:
    try:
        m = json.loads((Path(ws) / MANIFEST).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(m, dict):
        return {}
    files = m.get("files")
    m["files"] = {k: {**v, **{x: {} for x in ("inputs", "sources") if x in v and not isinstance(v[x], dict)}}
                  for k, v in (files if isinstance(files, dict) else {}).items() if isinstance(v, dict)}
    for v in m["files"].values():
        src = v.get("sources")
        if isinstance(src, dict) and isinstance(src.get("taxonomy"), str):
            v["sources"] = {**src, "taxonomy": [src["taxonomy"]]}
    packs = m.get("packs")
    m["packs"] = {k: v for k, v in (packs if isinstance(packs, dict) else {}).items() if isinstance(v, dict)}
    return m


def _path_key(path) -> str:
    return str(Path(path).resolve())


def pack_record(manifest: dict, pack_path) -> dict | None:
    """The packs-table record (last check-pack) for the pack file at pack_path, or None. The table is keyed by the
    pack file's resolved path; a record an older engine wrote under the pack's bare name (the file name without
    .json) is the fallback. Every lookup goes through here, so the keying lives in one place."""
    table = manifest.get("packs") or {}
    rec = table.get(_path_key(pack_path))
    if not isinstance(rec, dict):
        name = Path(pack_path).name
        rec = table.get(name[:-5] if name.endswith(".json") else name)
    return rec if isinstance(rec, dict) else None


def sign_off_entry(manifest: dict, path) -> dict | None:
    """The sign-offs-table entry for the file at path, or None. The table is keyed by the file's resolved path; an
    entry an older engine wrote under the bare file name is the fallback. The entry carries the resolved path,
    which sign_off_record checks. Every lookup goes through here (see pack_record)."""
    table = manifest.get("sign_offs") or {}
    rec = table.get(_path_key(path))
    if not isinstance(rec, dict):
        rec = table.get(Path(path).name)
    return rec if isinstance(rec, dict) else None


def drop_name_key(table: dict, path, legacy_key: str) -> None:
    """Remove the old bare-name record for path from table, but only when it was recorded for this very file."""
    old = table.get(legacy_key)
    if isinstance(old, dict) and old.get("path") in (None, "", _path_key(path)):
        del table[legacy_key]


def _save_manifest(ws, m: dict) -> None:
    m["engine_version"] = __version__
    m.setdefault("files", {})
    m.setdefault("packs", {})
    write_json(Path(ws) / MANIFEST, m)


def record_derived(ws, name: str, inputs: dict, sources: dict | None = None) -> None:
    """Record the sha256 of ws/name and of every input it was built from (read-modify-write)."""
    ws = Path(ws)
    m = load_manifest(ws)
    entry = {"sha256": file_sha256(ws / name), "inputs": inputs, "written": _now()}
    if sources:
        entry["sources"] = sources
    m.setdefault("files", {})[name] = entry
    _save_manifest(ws, m)


def record_export(ws, xlsx) -> None:
    ws = Path(ws)
    m = load_manifest(ws)
    m["export"] = {"file": os.path.basename(xlsx), "sha256": file_sha256(xlsx)}
    _save_manifest(ws, m)


def _doc_hash(path) -> str:
    """The handling-excluded content hash of the JSON document at path (what sign-off hashes), or ''."""
    from .handling import content_hash   # handling imports this module
    try:
        d = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    return content_hash(d) if isinstance(d, dict) else ""


def check_current(manifest: dict, path, strict: bool = False) -> bool:
    """True when the last recorded check of the file at path passed and the file's content is unchanged since. The
    comparison is on the handling-excluded content hash, so a sign-off (which rewrites only the handling block) does
    not make a check stale; a record without one (an older engine) falls back to the file sha256 (ruling X30).
    strict=True also needs the passing check to have been a --strict one; a record without the key (an older engine)
    is not strict, so the file is checked again."""
    path = Path(path)
    rec = pack_record(manifest, path)
    if not (path.is_file() and rec and rec.get("ok")):
        return False
    if strict and rec.get("strict") is not True:
        return False
    if rec.get("content_hash"):
        return rec["content_hash"] == _doc_hash(path)
    return rec.get("sha256") == file_sha256(path)


def record_pack_check(ws, pack_name, pack_path, ok, n_problems, coverage=None, strict=False) -> None:
    """Record a check-pack or check-register run. "strict" says whether a passing check was a --strict one; a later
    non-strict pass on unchanged content keeps an earlier strict pass (the content it vouched for is the same)."""
    ws = Path(ws)
    m = load_manifest(ws)
    p = Path(pack_path)
    table = m.setdefault("packs", {})
    prev = pack_record(m, p) or {}
    h = _doc_hash(p)
    strict = bool(ok) and (bool(strict) or (prev.get("ok") is True and prev.get("strict") is True
                                            and prev.get("content_hash") == h))
    drop_name_key(table, p, pack_name)
    table[_path_key(p)] = {
        "pack": pack_name, "sha256": file_sha256(p) if p.is_file() else "", "content_hash": h,
        "path": _path_key(p),
        "ok": bool(ok), "strict": strict, "problems": n_problems, "checked": _now()}
    if isinstance(coverage, dict):
        table[_path_key(p)]["coverage"] = {k: coverage[k] for k in ("cited", "relevant", "top_cited", "top_relevant")
                                           if k in coverage}
    _save_manifest(ws, m)


def taxonomy_sources(path, overlays) -> list:
    return [Path(path) if path else REFS / "taxonomy.json", *[_overlay_path(x) for x in overlays]]


def taxonomy_hash(paths) -> str:
    return hashlib.sha256("\n".join(file_sha256(p) for p in paths).encode()).hexdigest()


def manifest_state_hash(ws) -> str:
    """A hash of the manifest without plan.json's own entry and the engine version: what a plan is built from
    (every derived file and pack check recorded), so recording the plan does not make it stale."""
    m = load_manifest(ws)
    m.pop("engine_version", None)
    m["files"] = {k: v for k, v in m.get("files", {}).items() if k != "plan.json"}
    return hashlib.sha256(json.dumps(m, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def _current_input(ws: Path, name: str, entry: dict):
    """The input's hash now, 'none', or None when it cannot be checked (export) or is missing."""
    src = entry.get("sources", {})
    if name == "manifest.json":
        return manifest_state_hash(ws)
    if name == "contracts":
        paths = [Path(p) for p in src.get("contracts", [])]
        return taxonomy_hash(paths) if paths and all(p.is_file() for p in paths) else None
    if name == "taxonomy":
        paths = [Path(p) for p in src.get("taxonomy", [])]
        return taxonomy_hash(paths) if paths and all(p.is_file() for p in paths) else None
    if name == "overrides":
        p = src.get("overrides")
        if not p and src.get("overrides_auto") and (ws / "role_overrides.json").is_file():
            return file_sha256(ws / "role_overrides.json")
        return "none" if not p else (file_sha256(p) if Path(p).is_file() else None)
    if name == "org_chart":
        p = src.get("org_chart")
        return "none" if not p else (file_sha256(p) if Path(p).is_file() else None)
    if name == "export":
        return "skip"
    p = ws / name
    return file_sha256(p) if p.is_file() else None


def stale_files(ws) -> list:
    """[(file, reason)] for recorded derived files whose recorded input hash differs from the current one."""
    ws = Path(ws)
    files = load_manifest(ws).get("files", {})
    out = {}
    for name, entry in files.items():
        for inp, rec in entry.get("inputs", {}).items():
            cur = _current_input(ws, inp, entry)
            if cur == "skip":
                continue
            if cur is None:
                out[name] = f"input {inp} is missing"
                break
            if cur != rec:
                out[name] = f"{inp} changed since this was built"
                break
    changed = True
    while changed:  # a file built from a stale derived file is stale too
        changed = False
        for name, entry in files.items():
            if name in out:
                continue
            for inp in entry.get("inputs", {}):
                if inp in out and inp in files:
                    out[name] = f"input {inp} is stale"
                    changed = True
                    break
    return sorted(out.items())


def warn_stale(ws) -> None:
    for name, reason in stale_files(ws):
        if name == "plan.json":   # a plan feeds no command; status shows it, `plan` rebuilds it
            continue
        cmd = REBUILD.get(name, "ingest")
        print(f"warning: stale input {name} ({reason}); re-run pmlc {cmd} {ws}", file=sys.stderr)


def cmd_status(a):
    from .handling import _hash_mismatch   # handling imports this module
    ws = Path(a.ws)
    if not ws.is_dir():
        sys.exit(f"{ws} is not a folder.")
    m = load_manifest(ws)
    recorded = m.get("files", {})
    stale = dict(stale_files(ws))
    print("| File | State | Reason |\n|---|---|---|")
    names = [n for n in KNOWN_DERIVED if (ws / n).exists() or n in recorded]
    jfiles, jpacks, jsigned = [], [], []
    for n in names:
        if not (ws / n).exists():
            state, reason = "stale", "file is missing"
        elif n not in recorded:
            state, reason = "unknown (built before manifest)", ""
        elif n in stale:
            state, reason = "stale", stale[n]
        else:
            state, reason = "current", ""
        print(f"| {n} | {state} | {reason} |")
        jfiles.append({"file": n, "state": state, "reason": reason})
    shown = {}   # display name -> record or None; a listing of the whole table, read through the accessors
    seen = set()
    out = outputs_dir(ws)
    if out.is_dir():
        for p in sorted(out.glob("*.json")):
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if isinstance(d, dict) and isinstance(d.get("pack"), str):
                rec = pack_record(m, p)
                shown[d["pack"]] = rec
                if rec is not None:
                    seen.add(id(rec))
    for key, rec in m.get("packs", {}).items():
        if id(rec) not in seen:
            shown.setdefault(rec.get("pack") or (Path(rec["path"]).stem if rec.get("path") else Path(key).stem), rec)
    print("\n| Pack | Last check | Changed since |\n|---|---|---|")
    for name in sorted(shown):
        rec = shown[name]
        if not rec:
            print(f"| {name} | never | n/a |")
            jpacks.append({"pack": name, "last_check": "never", "changed_since": "n/a"})
            continue
        last = ("ok" if rec.get("ok") else f"{rec.get('problems', 0)} problem(s)") + f" ({rec.get('checked', '')})"
        p = Path(rec.get("path", ""))
        changed = "missing" if not p.is_file() else ("yes" if file_sha256(p) != rec.get("sha256") else "no")
        print(f"| {name} | {last} | {changed} |")
        jpacks.append({"pack": name, "last_check": last, "ok": bool(rec.get("ok")), "problems": rec.get("problems", 0),
                       "checked": rec.get("checked", ""), "changed_since": changed})
    from .retention import load_run_manifest   # retention imports this module
    rm = load_run_manifest(ws)
    if rm:
        print("\n| Run manifest | Value |\n|---|---|")
        for k in ("classification", "intended_use", "jurisdiction", "retention_review", "purged_on"):
            v = rm.get(k)
            print(f"| {k} | {', '.join(v) if isinstance(v, list) else (v if v is not None else '')} |")
    signed = m.get("sign_offs", {})
    if signed:
        print("\n| Signed off | Status | Role | Date | Changed since |\n|---|---|---|---|---|")
        rows = sorted((Path(k).name, r) for k, r in signed.items() if isinstance(r, dict))
        for name, r in rows:
            f = Path(r.get("path") or out / name)
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
                changed = "yes" if _hash_mismatch(d) else "no"
            except (OSError, ValueError):
                changed = "missing"
            print(f"| {name} | {r.get('status')} | {r.get('reviewer_role')} | {r.get('reviewed_on')} | {changed} |")
            jsigned.append({"file": name, "status": r.get("status"), "reviewer_role": r.get("reviewer_role"),
                            "reviewed_on": r.get("reviewed_on"), "changed_since": changed})
    from .util import json_extra
    json_extra(files=jfiles, packs=jpacks, sign_offs=jsigned, run_manifest=rm or None)


# ----------------------------------------------------------------------------- run folders

RUNS_DIR = "pmlc-runs"
SLUG_PART_RX = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RUN_SLUG_RX = re.compile(r"^\d{4}-\d{2}-\d{2}(?:-[a-z0-9]+)+$")


def run_slug(date, slug) -> str:
    """Incident date + '<site>-<event>' -> run folder name, e.g. 2020-09-24-hazira-gas-release-fire."""
    d = iso_date(date)
    if not d:
        raise ValueError(f"not an ISO date (YYYY-MM-DD): {date!r}")
    if not SLUG_PART_RX.match(slug or ""):
        raise ValueError("slug must be lowercase words joined by hyphens, "
                         f"e.g. hazira-gas-release-fire (got {slug!r})")
    return f"{d}-{slug}"


def valid_run_slug(s) -> bool:
    return bool(RUN_SLUG_RX.match(s or "")) and iso_date(s[:10]) is not None


def is_standard_ws(ws) -> bool:
    """True for <anything>/pmlc-runs/<valid slug>/workspace."""
    p = _abs(ws)
    return p.name == "workspace" and p.parent.parent.name == RUNS_DIR and valid_run_slug(p.parent.name)


def outputs_dir(ws) -> Path:
    """Where a workspace's outputs go: the sibling outputs/ in the standard layout, ws/outputs otherwise."""
    p = _abs(ws)
    return p.parent / "outputs" if is_standard_ws(p) else p / "outputs"


def cmd_run_path(a):
    ws = _abs(a.ws)
    std = is_standard_ws(ws)
    print(f"run:       {ws.parent if std else ws}")
    print(f"workspace: {ws}")
    print(f"outputs:   {outputs_dir(ws)}")
    print(f"slug:      {ws.parent.name if std else '(legacy layout: not under pmlc-runs/<slug>/workspace)'}")
    if (ws / "findings.json").is_file():
        w = load_ws(ws)
        print(f"top_rating: {top_rating(w)}")
        print(f"incident_date: {incident_date(w) or 'unknown'}")


def top_rating(w) -> int:
    """The highest rating in the workspace (0 when there are no findings)."""
    return max(((f["rating"] or 0) for f in w["findings"]), default=0)


def incident_date(w) -> str | None:
    """The incident date (YYYY-MM-DD): recorded at ingest, else the summary sheet's Date field, else None."""
    inc = w.get("incident", {})
    return inc.get("date") or iso_date(inc.get("fields", {}).get("Date"))


EVD_RX = re.compile(r"\bEVD-\d{3,}\b")


def linked_evidence(f: dict) -> set:
    """Evidence a finding is linked to: its Linked Evidence column plus the EVD IDs its AI Justification names."""
    return set(f["evidence"]) | set(EVD_RX.findall(f["justification"]))


def downgraded_findings(w: dict) -> set:
    """Finding IDs with a reviewer vote to downgrade, reject or remove them (incident.json review_votes)."""
    return {v.get("finding") for v in w.get("incident", {}).get("review_votes", [])
            if _s(v.get("vote")).lower() in ("downgrade", "reject", "remove")}
