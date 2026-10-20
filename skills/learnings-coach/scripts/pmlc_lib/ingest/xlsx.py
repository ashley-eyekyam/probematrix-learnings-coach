"""Sheet readers and the ingest command."""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

from .. import LEVEL_NAMES
from ..ingest.schema import (
    _fmt_cols, analysis_stats, CAPA_PLANNER_SHEETS, find_sheet, REQUIRED_COLUMNS, rows_as_dicts, schema_report
)
from ..util import _abs, _int, _need_openpyxl, _s, iso_date, split_outside_parens, write_json
from ..workspace import (
    _save_manifest, file_sha256, is_standard_ws, load_manifest, outputs_dir, record_derived, record_export, run_slug,
    RUNS_DIR
)
from .. import privacy


# ----------------------------------------------------------------------------- ingest

def ingest_target(a, fields: dict) -> Path:
    """Resolve where ingest writes the workspace; exits with a clear message if the folder rule is broken."""
    if a.legacy_out:
        if not is_standard_ws(a.legacy_out):
            print(f"Warning: {a.legacy_out} is outside the standard layout "
                  f"<export-dir>/{RUNS_DIR}/<YYYY-MM-DD>-<site>-<event>/workspace.", file=sys.stderr)
        return _abs(a.legacy_out)
    if a.out:
        if not is_standard_ws(a.out):
            sys.exit(f"--out must be <dir>/{RUNS_DIR}/<YYYY-MM-DD>-<site>-<event>/workspace (got {a.out}). "
                     "Use --slug instead, or --legacy-out for a non-standard folder.")
        return _abs(a.out)
    if not a.slug:
        sys.exit("Give --slug <site>-<event>, e.g. --slug hazira-gas-release-fire "
                 "(the date comes from --date or the summary sheet's Date).")
    date = a.date or fields.get("Date", "")
    if not iso_date(date):
        src = "--date" if a.date else "the summary sheet's Date"
        sys.exit(f"No valid incident date from {src}: {date!r}. Pass --date YYYY-MM-DD.")
    try:
        slug = run_slug(date, a.slug)
    except ValueError as err:
        sys.exit(str(err))
    root = _abs(a.root) if a.root else _abs(a.xlsx).parent
    return root / RUNS_DIR / slug / "workspace"


PERSONAL_FIELDS = ("Investigating Officer", "Supervisor at Time", "Investigation Team")
REGULATOR_RX = re.compile(r"\b(?:regulator|enquiry|inquiry|statutory|ERDMP|OISD|PNGRB|HSE|OSHA)\b", re.I)


def personal_fields_present(fields: dict) -> list:
    return [k for k in PERSONAL_FIELDS if _s(fields.get(k))]


def load_redact_map(path) -> dict:
    """The --redact map: a flat JSON object of {name: replacement role}; anything else exits 1."""
    try:
        m = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        m = None
    if not isinstance(m, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in m.items()):
        sys.exit('--redact: expected a JSON object of "name": "role"')
    return {k: v for k, v in m.items() if k.strip()}


def _canon(x: str) -> str:
    return re.sub(r"[\s.]+", "", x.lower())


def build_redact_map(redact: dict) -> tuple:
    """(repl, multi) for a --redact map: repl maps the canonical form of each name and variant to its role, multi
    lists the multi-token forms. A form two names share with different roles (a surname, say) is ambiguous, so it
    maps to '[redacted]' and not to whichever name came last."""
    repl, multi = {}, []
    for name, role in redact.items():
        for v in privacy.name_variants(name) + [name]:
            key = _canon(v)
            repl[key] = "[redacted]" if repl.get(key, role) != role else role
            if len(v.split()) > 1:
                multi.append(v)
    return repl, multi


def redact_data(obj, rx, repl: dict, role_rx=None, single=None):
    """(redacted copy, count): every string value (not dict keys) passed through rx; repl maps the canonical match
    (lower case, no spaces or dots) to the role. Under a 'roles' key only role_rx (the multi-token forms) is used, so
    'Field Operator' survives a map that names 'John Field'. single, when given, counts one-word matches by text."""
    n = [0]

    def sub(m):
        n[0] += 1
        if single is not None and len(re.findall(r"\w+", m.group(0))) == 1:
            single[m.group(0)] = single.get(m.group(0), 0) + 1
        return repl.get(_canon(m.group(0)), "[redacted]")

    def walk(x, key=None):
        if isinstance(x, str):
            r = role_rx if key == "roles" else rx
            return r.sub(sub, x) if r else x
        if isinstance(x, list):
            return [walk(i, key) for i in x]
        if isinstance(x, dict):
            return {k: walk(v, k) for k, v in x.items()}
        return x
    return walk(obj), n[0]


def cmd_ingest(a):
    redact = load_redact_map(a.redact) if a.redact else None
    openpyxl = _need_openpyxl()
    wb = openpyxl.load_workbook(a.xlsx, read_only=True, data_only=True)
    names = {n.strip().lower() for n in wb.sheetnames}
    if sum(1 for c in CAPA_PLANNER_SHEETS if c.lower() in names) >= 2:
        sys.exit('This is a CAPA Planner export, not a findings export. '
                 'Export "Identified Findings" from the investigation instead.')

    fs = find_sheet(wb, "Identified Findings", "Findings")
    if fs is None:
        sys.exit("Could not find an 'Identified Findings' sheet in the workbook.")
    schema = schema_report(wb)
    req_missing = [c for c in REQUIRED_COLUMNS if c in schema["missing"].get("Identified Findings", [])]
    if a.strict and req_missing:
        sys.exit("--strict: Identified Findings is missing required column(s): " + ", ".join(req_missing))
    findings = []
    for r in rows_as_dicts(fs):
        fid = _s(r.get("Finding ID"))
        if not fid:
            continue
        lvl = _int(r.get("Level"))
        findings.append({
            "id": fid,
            "code": _s(r.get("Nanocode")),
            "name": _s(r.get("Name")),
            "level": lvl,
            "level_name": _s(r.get("Level Name")) or LEVEL_NAMES.get(lvl, ""),
            "category": _s(r.get("Category")),
            "subcategory": _s(r.get("Subcategory")),
            "classification": _s(r.get("Classification")),
            "rating": _int(r.get("Rating")),
            "instance": _s(r.get("Instance ID")),
            "label": _s(r.get("Instance Label")),
            "short": _s(r.get("Short Description")),
            "justification": _s(r.get("AI Justification")),
            "causal": _s(r.get("Causal Explanation")),
            "roles": split_outside_parens(_s(r.get("Individuals Involved"))),
            "evidence": [e.strip() for e in _s(r.get("Linked Evidence")).split(",") if e.strip()],
            "evidence_to_collect": _s(r.get("Evidence to Collect")),
            "key_questions": _s(r.get("Key Questions")),
            "suggested_interviews": _s(r.get("Suggested Interviews")),
            "causal_hypothesis": _s(r.get("Causal Hypothesis")),
            "user_edited": _s(r.get("User Edited")),
        })

    evidence = {}
    es = find_sheet(wb, "Evidence Links", "Evidence")
    if es is not None:
        for r in rows_as_dicts(es):
            eid = _s(r.get("Evidence ID"))
            if not eid:
                continue
            e = evidence.setdefault(eid, {"id": eid, "type": _s(r.get("Evidence Type")),
                                          "description": _s(r.get("Evidence Description")), "links": []})
            e["links"].append({"code": _s(r.get("Finding Code")), "relevance": _s(r.get("Relevance")),
                               "reference": _s(r.get("Specific Reference"))})

    incident = {"fields": {}, "narrative": ""}
    isht = find_sheet(wb, "Incident Summary")
    if isht is not None:
        grab_next = False
        for row in isht.iter_rows(values_only=True):
            cells = [c for c in row if c is not None]
            if not cells:
                continue
            if grab_next and len(cells) == 1 and len(_s(cells[0])) > 200:
                incident["narrative"] = _s(cells[0])
                grab_next = False
                continue
            k = _s(row[0]) if row else ""
            v = _s(row[1]) if len(row) > 1 else ""
            if k.upper() == "INCIDENT NARRATIVE":
                grab_next = True
                if len(v) > 200:
                    incident["narrative"] = v
                    grab_next = False
                continue
            if k and v and k not in ("Field",):
                incident["fields"][k] = v

    causal_sheet = []
    cs = find_sheet(wb, "Causal Chain")
    if cs is not None:
        for r in rows_as_dicts(cs):
            if _s(r.get("From Code")) and _s(r.get("To Code")):
                causal_sheet.append({k: _s(v) for k, v in r.items()})
    incident["causal_chain_sheet"] = causal_sheet
    votes = []
    vs = find_sheet(wb, "Collaboration Data")
    if vs is not None:
        mode = None
        for row in vs.iter_rows(values_only=True):
            first = _s(row[0]) if row else ""
            if first.upper() in ("VOTES", "COMMENTS"):
                mode = first.upper()
                continue
            if mode == "VOTES" and first and first != "Finding ID" and len(row) > 2:
                votes.append({"finding": first, "vote": _s(row[1]), "reason": _s(row[2])})
    incident["review_votes"] = votes
    incident["date"] = iso_date(a.date) or iso_date(incident["fields"].get("Date"))
    incident["source_file"] = os.path.basename(a.xlsx)
    incident["sheets"] = wb.sheetnames
    incident["schema"] = schema
    stats = analysis_stats(find_sheet(wb, "Analysis Statistics"))
    incident["analysis_stats"] = stats

    out = ingest_target(a, incident["fields"])
    if is_standard_ws(out) and (out / "findings.json").exists() and not a.force:
        sys.exit(f"{out} already holds a workspace. Pass --force to overwrite it.")
    redactions = None
    if redact is not None:
        repl, multi = build_redact_map(redact)
        rx = privacy.name_pattern(list(redact), variants=True)
        role_rx = privacy.name_pattern(multi)
        redactions, single = 0, {}
        if rx:
            findings, c1 = redact_data(findings, rx, repl, role_rx, single)
            evidence, c2 = redact_data(evidence, rx, repl, role_rx, single)
            incident, c3 = redact_data(incident, rx, repl, role_rx, single)
            redactions = c1 + c2 + c3
    write_json(out / "findings.json", findings)
    write_json(out / "evidence.json", evidence)
    write_json(out / "incident.json", incident)
    record_export(out, a.xlsx)
    for n in ("findings.json", "evidence.json", "incident.json"):
        record_derived(out, n, {"export": file_sha256(a.xlsx)})
    if redactions is not None:
        m = load_manifest(out)
        m["redactions"] = redactions
        _save_manifest(out, m)
    print(f"Ingested {len(findings)} findings, {len(evidence)} evidence items, "
          f"{len(causal_sheet)} causal-chain rows -> {out}")
    print(f"schema: fingerprint {schema['fingerprint']}; missing: {_fmt_cols(schema['missing'])}; "
          f"unknown: {_fmt_cols(schema['unknown'])}")
    if stats is None:
        print("note: no Analysis Statistics block recognised; cross-check skipped")
    elif stats["total"] == len(findings):
        print(f"cross-check: Analysis Statistics agrees ({stats['total']})")
    else:
        print(f"warning: Analysis Statistics says {stats['total']} findings, ingested {len(findings)}")
    if redactions is not None:
        for w_, c_ in sorted(single.items()):
            print(f'warning: surname-only match "{w_}" replaced {c_} times: check the text reads correctly')
        print(f"redacted {redactions} name occurrence(s) from the workspace")
    pf = personal_fields_present(incident["fields"])
    if pf:
        print(f"note: personal fields present ({', '.join(pf)}): they are not quoted in outputs")
    if is_standard_ws(out):
        outputs_dir(out).mkdir(parents=True, exist_ok=True)
        print(f"Run folder: {out.parent}\n  workspace: {out}\n  outputs:   {outputs_dir(out)}")
