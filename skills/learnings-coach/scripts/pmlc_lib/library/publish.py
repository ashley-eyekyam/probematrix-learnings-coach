"""`library publish`: append a finished run's learnings to the library (spec §8.1, Ruling P6-11).

Every line is built first. The existing files are validated, then each file gets one append. Any refusal writes
nothing, not even library.json.

- A learning gets its LL- ID once per (incident_key, lr_id) and keeps it.
- A snapshot is appended only when its content_hash changed, with `supersedes` naming the previous snapshot.
- A learning that has left the register gets a `withdrawn` event; one that comes back gets a `status` event
  ("reinstated"). A change in the register's effective review status alone gets a `status` event.
- An incident line is appended when anything but its `published` month changed.
- Absent register fields are omitted from `learning`, never written as null.

The de-identification gate (deid.deidentify, Ruling P6-12) runs on every public line before it is hashed: a listed name
refuses the publish, the site becomes its S-code, and the text is masked as a --share external copy is."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

from .. import __version__
from .deid import deidentify
from .events import collect_events, event_key
from .ids import allocate, incident_key
from ..templates import OrgFileError
from .store import LibraryError, canonical, open_library

# The register fields a snapshot's `learning` carries, in the shared contract's order, and where each comes from.
PUBLISH_FIELDS = (("title", "title"), ("lesson", "lesson"), ("public_context", "context"),
                  ("hfacs_level", "hfacs_level"), ("org_system", "org_system"), ("barrier", "barrier"),
                  ("priority", "priority"), ("transferability", "transferability"),
                  ("evidence_strength", "evidence_strength"), ("urgency", "urgency"))
PUBLISH_REFS = (("finding_refs", "finding_ids"), ("evidence_refs", "evidence_ids"))
PUBLISH_STATE_EVENTS = ("withdrawn", "status")
PUBLISH_ORG_FILE = ("library publish refused: a file your organisation filled in has problems, so nothing was written. "
                    "Fix these lines, then publish again:\n{problems}")
PUBLISH_DAMAGED = ("library publish refused: the library at {path} is damaged, so nothing was written. Restore the "
                   "file from a backup, then publish again")


def _publish_absent(v) -> bool:
    return v is None or (isinstance(v, (str, list, dict)) and not (v.strip() if isinstance(v, str) else v))


def _publish_hash(obj) -> str:
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def _publish_refs(ikey: str, ids) -> list:
    if isinstance(ids, str):
        ids = [x for x in ids.replace(";", ",").split(",")]
    out = [f"{ikey}/{str(x).strip()}" for x in (ids if isinstance(ids, list) else []) if str(x).strip()]
    return list(dict.fromkeys(out))


def _publish_recs(ll_id: str, recs) -> list:
    out = []
    for n, r in enumerate(recs if isinstance(recs, list) else [], 1):
        r = {"what": r} if isinstance(r, str) else (r if isinstance(r, dict) else {})
        row = {"id": f"{ll_id}/R{n}"}
        for k, srcs in (("change", ("what", "change")), ("hoc_tier", ("hoc_tier",)),
                        ("indicator", ("leading_indicator", "indicator"))):
            v = next((r[s] for s in srcs if not _publish_absent(r.get(s))), None)
            if v is not None:
                row[k] = v
        out.append(row)
    return out


def snapshot(entry: dict, incident_key: str, ll_id: str, n: int, prev, review_status: str = "draft") -> dict:
    """The learnings.jsonl line for one register entry: snapshot n of ll_id, superseding prev (None for the first)."""
    learning = {}
    for k, src in PUBLISH_FIELDS:
        if not _publish_absent(entry.get(src)):
            learning[k] = entry[src]
    for k, src in PUBLISH_REFS:
        refs = _publish_refs(incident_key, entry.get(src))
        if refs:
            learning[k] = refs
    recs = _publish_recs(ll_id, entry.get("recommendations"))
    if recs:
        learning["recommendations"] = recs
    return {"ll_id": ll_id, "snapshot_id": f"{ll_id}#{n}", "supersedes": prev, "incident_key": incident_key,
            "lr_id": str(entry["lr_id"]), "content_hash": _publish_hash(learning), "review_status": review_status,
            "learning": learning}


def _publish_deidentify(lines: list, ctx: dict) -> list:
    """# P6-12 hook: deid.deidentify on [(file, obj)] public lines (raises LibraryError on a refusal)."""
    return deidentify(lines, ctx)


def _publish_event(etype, ll_id, ikey, month, data) -> dict:
    return {"type": etype, "ll_id": ll_id, "incident_key": ikey, "month": month, "source": "engine", "data": data}


def _publish_fail(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)


def _publish_register(path: Path):
    """(doc, entries) of a Learnings Register (a {"entries": [...]} object or a v0.3 bare list), or exit 2."""
    if not path.is_file():
        _publish_fail(f"library publish: no Learnings Register at {path}: write it first, or pass --register FILE")
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        _publish_fail(f"library publish reads a learnings register, and {path} is not one")
    entries = d.get("entries") if isinstance(d, dict) else d
    if (not isinstance(entries, list) or not entries or (isinstance(d, dict) and "sections" in d)
            or not all(isinstance(e, dict) and e.get("lr_id") for e in entries)):
        _publish_fail(f"library publish reads a learnings register, and {path} is not one")
    seen = set()
    for e in entries:
        lr = str(e["lr_id"])
        if lr in seen:
            _publish_fail(f"library publish: {lr} appears twice in the register {path}")
        seen.add(lr)
    return (d if isinstance(d, dict) else {"entries": entries}), entries


def _publish_status(doc, w, src, ws) -> str:
    from ..handling import effective_handling
    return effective_handling(doc, w, src=src, ws=ws)["effective_status"]


def _publish_workspace(ws: Path) -> dict:
    from ..workspace import is_standard_ws, load_ws
    if not (ws / "findings.json").is_file():
        _publish_fail(f"library publish: {ws} is not a workspace (no findings.json): run setup first")
    w = load_ws(ws)
    if not isinstance(w.get("clusters"), dict):
        _publish_fail(f"library publish: {ws} has no clusters.json: run classify (or setup) first")
    w["slug"] = ws.parent.name if is_standard_ws(ws) else ws.name
    return w


def _publish_month(w):
    from ..workspace import incident_date
    d = incident_date(w)
    return d[:7] if d else None


def _publish_export_sha(ws: Path):
    try:
        m = json.loads((ws / "manifest.json").read_text(encoding="utf-8"))
        return (m.get("export") or {}).get("sha256")
    except (OSError, ValueError, AttributeError):
        return None


def plan_publish(lib, ws: Path, reg_path: Path, ctx: dict) -> dict:
    """Everything one publish would append, as {"lines": {file: [obj]}, "counts": {...}, "report": [str]}."""
    from ..render import build_date
    w = _publish_workspace(ws)
    doc, entries = _publish_register(reg_path)
    status = _publish_status(doc, w, reg_path, ws)
    ikey = incident_key(w)
    published = build_date()[:7]
    ctx = dict(ctx, workspace=ws, w=w, incident_key=ikey, library=lib)

    latest, count = {}, {}
    for s in lib.learnings():
        latest[s["ll_id"]] = s
        count[s["ll_id"]] = count.get(s["ll_id"], 0) + 1
    withdrawn, ev_status, ev_hashes, last_state, org_latest = {}, {}, set(), {}, {}
    org_last = {}
    for e in lib.events():
        ev_hashes.add(e.get("event_hash"))
        data = e.get("data") if isinstance(e.get("data"), dict) else {}
        if e.get("source") == "organisation":
            org_latest[event_key(e)] = {k: v for k, v in data.items() if k != "after"}
            org_last[event_key(e)] = e.get("event_hash")
            continue
        if e.get("type") in PUBLISH_STATE_EVENTS:
            last_state[e.get("ll_id")] = e.get("event_hash")
        if e.get("type") == "withdrawn":
            withdrawn[e.get("ll_id")] = True
        elif e.get("type") == "status" and data.get("status") == "reinstated":
            withdrawn[e.get("ll_id")] = False
        if e.get("type") == "status" and "review_status" in data:
            ev_status[(e.get("ll_id"), data.get("snapshot_id"))] = data["review_status"]

    cands = []
    for e in entries:
        ll = allocate(lib, ikey, str(e["lr_id"]))
        prev = latest.get(ll)
        cands.append((e, snapshot(e, ikey, ll, count.get(ll, 0) + 1, prev["snapshot_id"] if prev else None, status)))
    lls = sorted(s["ll_id"] for _, s in cands)
    inc = {"incident_key": ikey, "site_code": None, "month": _publish_month(w),
           "taxonomy_version": w["clusters"].get("taxonomy_version"),
           "taxonomy_fingerprint": w["clusters"].get("taxonomy_fingerprint"),
           "export_fingerprint": _publish_export_sha(ws), "engine_version": __version__, "published": published,
           "learnings": lls}
    public = _publish_deidentify([("learnings.jsonl", s) for _, s in cands] + [("incidents.jsonl", inc)], ctx)
    snaps = [o for f, o in public if f == "learnings.jsonl"]
    inc = next(o for f, o in public if f == "incidents.jsonl")

    out = {"learnings.jsonl": [], "events.jsonl": [], "incidents.jsonl": [], "private/contexts.jsonl": []}
    counts = {"new": 0, "superseded": 0, "unchanged": 0, "withdrawn": 0, "reinstated": 0, "status": 0,
              "site_assessments": 0, "verifications": 0, "adoption": 0}
    report, events = [], []
    for (e, _), s in zip(cands, snaps):
        s["content_hash"] = _publish_hash(s["learning"])
        prev = latest.get(s["ll_id"])
        if prev and prev.get("content_hash") == s["content_hash"]:
            counts["unchanged"] += 1
            known = ev_status.get((s["ll_id"], prev["snapshot_id"]), prev.get("review_status"))
            if known != status:
                events.append(("status", None, _publish_event("status", s["ll_id"], ikey, published,
                               {"review_status": status, "snapshot_id": prev["snapshot_id"]})))
        else:
            counts["superseded" if prev else "new"] += 1
            out["learnings.jsonl"].append(s)
            report.append(f"  + {s['snapshot_id']} {s['lr_id']} ({'supersedes ' + prev['snapshot_id'] if prev else 'new'})")
            if not _publish_absent(e.get("context")):
                out["private/contexts.jsonl"].append({"ll_id": s["ll_id"], "snapshot_id": s["snapshot_id"],
                                                      "context": e["context"]})
        if withdrawn.get(s["ll_id"]):
            last = prev["snapshot_id"] if prev else s["snapshot_id"]
            events.append(("reinstated", f"  + reinstated {s['ll_id']} ({s['lr_id']})",
                           _publish_event("status", s["ll_id"], ikey, published,
                                          {"status": "reinstated", "snapshot_id": last})))
    here = set(lls)
    for ll, s in sorted(latest.items()):
        if s.get("incident_key") == ikey and ll not in here and not withdrawn.get(ll):
            events.append(("withdrawn", f"  + withdrawn {ll} ({s['lr_id']})",
                           _publish_event("withdrawn", ll, ikey, published,
                                          {"lr_id": s["lr_id"], "snapshot_id": s["snapshot_id"]})))
    notes = []
    try:
        org = collect_events(ws, lib, {s["lr_id"]: (s["ll_id"], ikey) for _, s in cands}, published, notes)
    except OrgFileError as e:
        raise LibraryError(PUBLISH_ORG_FILE.format(problems="\n".join(e.problems)), 1)
    kinds = {"site_assessment": "site_assessments", "verification": "verifications", "status": "adoption"}
    events += [(kinds[o["type"]], None, o) for o in org]
    public_ev = _publish_deidentify([("events.jsonl", ev) for _, _, ev in events], ctx)
    for (kind, line, _), (_, ev) in zip(events, public_ev):
        # A state event names the state event it follows (data.after), so each transition hashes uniquely: a
        # withdraw -> reinstate -> withdraw cycle in one month keeps its second withdrawal (review r0, C1).
        mine = ev.get("source") == "organisation"
        if mine:
            if org_latest.get(event_key(ev)) == ev["data"]:
                continue                  # the latest event for this reading says the same: nothing new
            after = org_last.get(event_key(ev))     # a changed reading names the one it follows, so A -> B -> A keeps
        else:                                       # each change (same idea as the state events below)
            after = last_state.get(ev["ll_id"])
        if after and isinstance(ev.get("data"), dict):
            ev["data"]["after"] = after
        ev.pop("event_hash", None)
        ev["event_hash"] = _publish_hash(ev)
        if ev["event_hash"] in ev_hashes:
            continue
        if mine:
            org_latest[event_key(ev)] = {k: v for k, v in ev["data"].items() if k != "after"}
            org_last[event_key(ev)] = ev["event_hash"]
        else:
            last_state[ev["ll_id"]] = ev["event_hash"]
        ev_hashes.add(ev["event_hash"])
        out["events.jsonl"].append(ev)
        counts[kind] += 1                 # count only what is appended
        if line:
            report.append(line)

    def _same(x):
        return {k: v for k, v in x.items() if k != "published"}
    last_inc = next((i for i in reversed(lib.incidents()) if i.get("incident_key") == ikey), None)
    if last_inc is None or canonical(_same(last_inc)) != canonical(_same(inc)):
        out["incidents.jsonl"].append(inc)
        report.append(f"  + incident {ikey} ({len(lls)} learnings)")
    missing = [src for _, src in PUBLISH_FIELDS if all(_publish_absent(e.get(src)) for e in entries)]
    return {"lines": out, "counts": counts, "report": report, "incident_key": ikey, "missing": missing, "notes": notes,
            "site_code": inc.get("site_code")}


def cmd_library(a):
    from ..util import _abs
    path = a.library or os.environ.get("PMLC_LIBRARY")
    try:
        lib = open_library(path)
    except LibraryError as e:
        _publish_fail(f"library publish: {e}", e.code)
    probs = lib.validate()
    if probs:
        for p in probs:
            print(f"library publish: {p}", file=sys.stderr)
        _publish_fail(PUBLISH_DAMAGED.format(path=lib.path), 1)
    ws = _abs(a.ws)
    if a.register:
        reg = Path(a.register)
    else:
        from ..workspace import outputs_dir
        reg = outputs_dir(ws) / "learnings-register.json"
    try:
        plan = plan_publish(lib, ws, reg, {"site": a.site, "names": a.names, "orgs": getattr(a, "orgs", None)})
    except LibraryError as e:
        _publish_fail(f"library publish: {e}", e.code)
    lines, c = plan["lines"], plan["counts"]
    total = sum(len(v) for v in lines.values())
    head = "library publish (dry run: nothing written)" if a.dry_run else "library publish"
    print(f"{head}: {lib.path}{' (new library)' if lib.new else ''}")
    print(f"incident {plan['incident_key']}: {c['new']} new, {c['superseded']} superseded, {c['unchanged']} unchanged, "
          f"{c['withdrawn']} withdrawn, {c['reinstated']} reinstated, {c['status']} status changes")
    if any(c[k] for k in ("site_assessments", "verifications", "adoption")):
        print(f"organisation events: {c['site_assessments']} site assessments, {c['verifications']} verification "
              f"readings, {c['adoption']} adoption responses")
    for n in plan["notes"]:
        print(f"note: {n}")
    if plan["missing"]:
        print("note: the register has no " + ", ".join(plan["missing"]) + " in any learning (an older register), "
              "so the snapshots leave them out")
    if not (a.names or os.environ.get("PMLC_NAMES")):
        print("note: no names list (--names or PMLC_NAMES), so the zero-hit name check did not run: a personal name "
              "written in the register could reach the library", file=sys.stderr)
    if plan["site_code"]:
        print(f"site coded {plan['site_code']} (the real name stays in private/sites.json, which is never shared)")
    if not total:
        print("nothing to append: the library already holds this run as it stands")
        return
    for line in plan["report"]:
        print(line)
    verb = "would append" if a.dry_run else "appended"
    print(f"{verb}: " + ", ".join(f"{name}: {len(v)}" for name, v in lines.items()))
    if a.dry_run:
        return
    if lib.new:
        lib.init()
    lib.write_sites()                 # the private site map first, so no public code is ever left without its name
    for name, v in lines.items():
        lib.append(name, v)
