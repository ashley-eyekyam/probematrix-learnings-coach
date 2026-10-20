"""export-actions: every recommendation, decision and indicator item of the packs, and each register
recommendation, as actions.csv / actions.json for import into an action-tracking system. Owner, due date, status,
CAPA reference and effectiveness check are always written blank (D7): the organisation assigns them."""
from __future__ import annotations

import csv
import io
import json
import sys
from pathlib import Path

from .pack.schema import with_item_ids
from .privacy import load_names, name_pattern
from .templates import REGISTER_FILE, _outputs, load_register_entries, pack_files
from .util import REFS
from .workspace import is_standard_ws, outputs_dir

ACTION_COLUMNS = ["id", "lr_id", "change", "hoc_tier", "barrier", "indicator", "owner", "due", "status", "capa_ref",
                  "effectiveness_check", "cites", "evidence_strength"]
PROFILES_FILE = REFS / "actions-profiles.json"
PROFILE_NAMES = ["generic", "enablon", "intelex", "cority", "sap-ehs"]
KINDS = ("recommendation", "decision", "indicator")


def load_profiles() -> dict:
    return json.loads(PROFILES_FILE.read_text(encoding="utf-8"))


def _blank(**kw) -> dict:
    row = {c: "" for c in ACTION_COLUMNS}
    row.update(kw)
    return row


def _item_row(slug: str, pack: str, it: dict) -> dict:
    k = it["kind"]
    if k == "recommendation":
        change, indicator = it.get("change", ""), it.get("indicator", "")
    elif k == "decision":
        change, indicator = it.get("decision", ""), ""
    else:
        change, indicator = it.get("name", ""), it.get("measure", "")
    return _blank(id=f"{slug}/{pack}/{it['id']}", lr_id=it.get("learning", ""), change=change,
                  hoc_tier=it.get("hoc_tier", ""), barrier=it.get("barrier") or it.get("barrier_id") or "",
                  indicator=indicator, cites=list(it.get("cites") or []),
                  evidence_strength=it.get("evidence_strength", ""))


def collect_actions(slug: str, packs: list, entries: list) -> list:
    """packs: [(pack document)]; entries: register entries. Rows carry cites as a list."""
    rows = []
    for d in packs:
        for s in with_item_ids(d)["sections"]:
            rows += [_item_row(slug, d["pack"], it) for it in s["items"] if it.get("kind") in KINDS]
    for e in entries:
        for n, r in enumerate(e.get("recommendations") or [], 1):
            rows.append(_blank(id=f"{slug}/register/{e.get('lr_id', '')}/R{n}", lr_id=e.get("lr_id", ""),
                               change=r.get("what", ""), hoc_tier=r.get("hoc_tier", ""),
                               barrier=r.get("level_barrier") or e.get("barrier") or "",
                               indicator=r.get("leading_indicator", ""),
                               cites=list(e.get("finding_ids") or []) + list(e.get("evidence_ids") or []),
                               evidence_strength=r.get("evidence_strength") or e.get("evidence_strength") or ""))
    return rows


FORMULA_LEAD = ("=", "+", "-", "@", "\t", "\r")


def _flat(v) -> str:
    return "; ".join(str(x) for x in v) if isinstance(v, list) else v


def _csv_cell(v) -> str:
    """X20: a CSV cell that starts with = + - @ tab or CR gets a leading single quote, so Excel never runs it."""
    s = _flat(v)
    return "'" + s if isinstance(s, str) and s.startswith(FORMULA_LEAD) else s


def _slug(ws: Path) -> str:
    return ws.parent.name if is_standard_ws(ws) else ws.name


def cmd_export_actions(a):
    ws = Path(a.ws).resolve()
    out_dir = outputs_dir(ws)
    profiles = load_profiles()
    prof = profiles[a.profile]
    if not prof.get("verified"):
        print(f"profile '{a.profile}' is an unverified mapping: check the column names against your system "
              f"before importing", file=sys.stderr)
    if a.packs:
        docs = []
        for p in a.packs:
            f = Path(p) if Path(p).is_file() else out_dir / (p if p.endswith(".json") else p + ".json")
            if not f.is_file():
                sys.exit(f"No pack file {p}")
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
            except ValueError:
                d = None
            if not (isinstance(d, dict) and d.get("pack") and isinstance(d.get("sections"), list)):
                sys.exit(f"{f} is not a learning pack (it needs 'pack' and 'sections')")
            docs.append(d)
    else:
        docs = [d for _, d in pack_files(_outputs(ws))]
    reg = Path(a.register) if a.register else out_dir / REGISTER_FILE
    if a.register and not reg.is_file():
        sys.exit(f"No Learnings Register at {reg}")
    entries = load_register_entries(reg) if reg.is_file() else []
    rows = collect_actions(_slug(ws), docs, entries)
    cmap = {c: prof["columns"].get(c, c) for c in ACTION_COLUMNS}
    jrows = [{cmap[c]: r[c] for c in ACTION_COLUMNS} for r in rows]
    buf = io.StringIO(newline="")
    w = csv.writer(buf, lineterminator="\r\n")
    w.writerow([cmap[c] for c in ACTION_COLUMNS])
    for r in rows:
        w.writerow([_csv_cell(r[c]) for c in ACTION_COLUMNS])
    csv_text = buf.getvalue()
    json_text = json.dumps(jrows, indent=2, ensure_ascii=False) + "\n"
    names = load_names(a.names)
    rx = name_pattern(names, variants=True, skip_role_words=True)
    if rx:
        hits = sorted({m.group(0) for m in rx.finditer(csv_text + json_text)})
        if hits:
            print(f"name scan: {len(hits)} hit(s) in the actions ({', '.join(hits)}); nothing written. "
                  f"Fix the pack or register text and run again.", file=sys.stderr)
            sys.exit(1)
    d = Path(a.out_dir) if a.out_dir else out_dir
    d.mkdir(parents=True, exist_ok=True)
    (d / "actions.csv").write_bytes(csv_text.encode("utf-8"))
    (d / "actions.json").write_text(json_text, encoding="utf-8")
    print(f"wrote {d / 'actions.csv'} and {d / 'actions.json'} ({len(rows)} actions, profile {a.profile}); "
          f"owner, due, status, capa_ref and effectiveness_check are blank for your organisation to fill in")
