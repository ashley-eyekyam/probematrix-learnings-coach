"""The crosswalk command (L7-01): which clauses of a standard the learnings give evidence for, and what the
organisation must still show. The engine never sets "not applicable": that is the organisation's call."""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

from .templates import load_adoption, load_distribution, load_register_entries, OrgFileError
from .util import _abs, REFS
from .workspace import load_ws, outputs_dir

STEPS = ["needs organisation evidence", "partly", "evidenced here"]
FRAMEWORKS = ["iso45001", "psm", "rmp", "seveso", "rbps", "icmm", "india"]
TABLE_COLUMNS = ["Requirement", "Status", "Evidence here", "Organisation must show"]
# rows the adoption and distribution records speak to (ISO 45001 7.3 and 7.4, PSM (m)(6))
ORG_FILE_ROWS = ("ISO45001-7.3", "ISO45001-7.4", "PSM-(m)(6)")
MUST_SHOW = "Records showing how the organisation meets this requirement; the learnings here are not that record."


def _cw_register_entries(register) -> list:
    """The learnings of a register dict, or exit with one plain sentence when this is not a Learnings Register."""
    ents = register.get("entries", register.get("learnings")) if isinstance(register, dict) else register
    if not isinstance(ents, list) or (isinstance(register, dict) and "pack" in register and "sections" in register):
        sys.exit("crosswalk needs a Learnings Register (learnings-register.json) with entries, not a pack or another file")
    return [e for e in ents if isinstance(e, dict)]


def _cw_text(e: dict) -> str:
    parts = [e.get("title"), e.get("lesson"), e.get("context"), e.get("org_system"), e.get("pattern")]
    parts += [r.get("what") for r in e.get("recommendations") or [] if isinstance(r, dict)]
    parts += list((e.get("tier_messages") or {}).values())
    return " ".join(str(p) for p in parts if p)


def _cw_requirements(framework, system_csv):
    if system_csv:
        p = Path(system_csv)
        try:
            with open(p, encoding="utf-8-sig", newline="") as fh:
                rd = csv.DictReader(fh)
                head = [h.strip().lower() for h in rd.fieldnames or []]
                if "id" not in head or "title" not in head:
                    sys.exit(f"{p} needs the columns id,title[,topics]")
                rows = [{k.strip().lower(): (v or "").strip() for k, v in r.items() if k} for r in rd]
        except OSError:
            sys.exit(f"Cannot read {p}")
        reqs = [{"id": r["id"], "title": r["title"], "verified": False, "topics": r.get("topics", "")}
                for r in rows if r.get("id")]
        return f"Organisation system: {p.name}", reqs
    d = json.loads((REFS / "standards-crosswalk.json").read_text(encoding="utf-8"))["frameworks"]
    if framework not in d:
        sys.exit(f"Unknown framework {framework}; choose one of {', '.join(d)}")
    return d[framework]["title"], d[framework]["requirements"]


def crosswalk(w, register, framework, system_csv=None, adoption=None, distribution=None) -> dict:
    ents = _cw_register_entries(register)
    title, reqs = _cw_requirements(framework, system_csv)
    known = {f["id"] for f in (w or {}).get("findings", [])}
    files = [n for n, rows in (("adoption.csv", adoption), ("distribution.csv", distribution)) if rows]
    out = []
    for r in reqs:
        by_clause = [e for e in ents if r["id"] in (e.get("clauses") or [])]
        rx = None
        if r.get("topics"):
            try:
                rx = re.compile(r["topics"], re.I)
            except re.error:
                rx = None
        by_topic = [] if by_clause or not rx else [e for e in ents if rx.search(_cw_text(e))]
        status = STEPS[2] if by_clause else STEPS[1] if by_topic else STEPS[0]
        must = r.get("must_show") or MUST_SHOW
        if files and r["id"] in ORG_FILE_ROWS:
            status = STEPS[min(STEPS.index(status) + 1, 2)]
            must += f" Moved up one step on the strength of {' and '.join(files)}; confirm the rows are complete."
        mine = by_clause or by_topic
        ids = sorted({str(e.get("lr_id")) for e in mine if e.get("lr_id")})
        cites = sorted({c for e in mine for c in e.get("finding_ids") or [] if not known or c in known})
        out.append({"id": r["id"], "title": r["title"], "verified": bool(r.get("verified")), "status": status,
                    "evidence_here": ids, "organisation_must_show": must, "cites": cites})
    return {"framework": "system" if system_csv else framework, "title": title, "rows": out}


def table_item(cw) -> dict:
    rows = [[f"{r['id']} {r['title']}", r["status"], ", ".join(r["evidence_here"]) or "none",
             r["organisation_must_show"]] for r in cw["rows"]]
    cites = [r["cites"] for r in cw["rows"]]
    return {"kind": "table", "id": f"crosswalk-{cw['framework']}", "columns": list(TABLE_COLUMNS), "rows": rows,
            "row_cites": cites, "cites": sorted({x for c in cites for x in c})}


def _cw_org_rows(ws):
    try:
        return load_adoption(ws), load_distribution(ws)
    except OrgFileError as e:
        sys.exit(str(e))


def cmd_crosswalk(a):
    ws = _abs(a.ws)
    if not a.framework and not a.system_csv:
        sys.exit("crosswalk needs --framework (" + ", ".join(FRAMEWORKS) + ") or --system-csv FILE")
    reg = Path(a.register) if a.register else outputs_dir(ws) / "learnings-register.json"
    if not reg.is_file():
        sys.exit(f"No Learnings Register at {reg}: write it first, or pass --register FILE")
    try:
        data = json.loads(reg.read_text(encoding="utf-8"))
    except ValueError:
        sys.exit(f"{reg} is not a Learnings Register (it is not JSON)")
    _cw_register_entries(data)
    adoption, distribution = _cw_org_rows(ws)
    cw = crosswalk(load_ws(ws), data if isinstance(data, dict) else {"entries": data}, a.framework, a.system_csv,
                   adoption, distribution)
    if a.table_item:
        print(json.dumps(table_item(cw), indent=1, ensure_ascii=False))
    elif a.json:
        print(json.dumps(cw, indent=1, ensure_ascii=False))
    else:
        print(f"{cw['title']}\n\n| Requirement | Status | Evidence here |\n|---|---|---|")
        for r in cw["rows"]:
            print(f"| {r['id']} {r['title']} | {r['status']} | {', '.join(r['evidence_here']) or 'none'} |")
