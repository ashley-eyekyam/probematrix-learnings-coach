"""The comparator inventory (comparator.json, comparison-map.json) and the compare command."""
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

from .register.check import HOC_TIERS, norm_entity, norm_hoc
from .util import _s

ITEM_ID_RX = re.compile(r"^(OBS|RC|REC|ACT)-\d{2,}$")
COMPARATOR_ITEM_RX = ITEM_ID_RX
LR_ID_RX = re.compile(r"^LR-\d{2,}$")
TYPE_PREFIX = {"observation": "OBS", "root_cause": "RC", "recommendation": "REC", "action": "ACT"}
SOURCE_KINDS = ("official-report", "own-action-plan", "company-report")
MATCHES = ("yes", "partial", "none")
COMPARATOR_FILE = "comparator.json"
MAPPING_FILE = "comparison-map.json"


def _read_json(path, what):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, f"{what}: {path} not found"
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as e:
        return None, f"{what}: cannot read {path} as JSON ({e.__class__.__name__})"


def validate_comparator(c) -> list:
    """Problems with a comparator.json value (empty when it is sound)."""
    if not isinstance(c, dict):
        return ["comparator: must be a JSON object"]
    P = []
    src = c.get("source")
    if not isinstance(src, dict):
        P.append("comparator.source: required object")
    else:
        for k in ("title", "issuer_role", "statutory_status"):
            if not _s(src.get(k)):
                P.append(f"comparator.source.{k}: required text")
        if src.get("kind") not in SOURCE_KINDS:
            P.append(f"comparator.source.kind: must be one of {', '.join(SOURCE_KINDS)}")
    items = c.get("items")
    if not isinstance(items, list):
        return P + ["comparator.items: required list"]
    seen = set()
    for n, it in enumerate(items):
        if not isinstance(it, dict):
            P.append(f"comparator.items[{n}]: must be an object")
            continue
        iid = it.get("id")
        if not isinstance(iid, str) or not ITEM_ID_RX.fullmatch(iid):
            P.append(f"comparator.items[{n}].id: {iid!r} must look like OBS-01, RC-01, REC-01 or ACT-01")
        elif iid in seen:
            P.append(f"comparator.items[{n}].id: duplicate id {iid}")
        else:
            seen.add(iid)
        typ = it.get("type")
        if typ not in TYPE_PREFIX:
            P.append(f"comparator.items[{n}].type: must be one of {', '.join(TYPE_PREFIX)}")
        elif isinstance(iid, str) and ITEM_ID_RX.fullmatch(iid) and not iid.startswith(TYPE_PREFIX[typ] + "-"):
            P.append(f"comparator.items[{n}].id: {iid} does not fit type {typ} (use {TYPE_PREFIX[typ]}-nn)")
        if not _s(it.get("text")):
            P.append(f"comparator.items[{n}].text: required text")
    return P


def validate_mapping(m, ids, lr_ids=None) -> list:
    if not isinstance(m, list):
        return ["mapping: must be a JSON list"]
    P = []
    for n, r in enumerate(m):
        if not isinstance(r, dict):
            P.append(f"mapping[{n}]: must be an object")
            continue
        if not isinstance(r.get("lr_id"), str) or not LR_ID_RX.fullmatch(r["lr_id"]):
            P.append(f"mapping[{n}].lr_id: {r.get('lr_id')!r} must look like LR-01")
        elif lr_ids is not None and r["lr_id"] not in lr_ids:
            P.append(f"mapping[{n}].lr_id: {r['lr_id']} is not in the register")
        if r.get("ref") not in ids:
            P.append(f"mapping[{n}].ref: {r.get('ref')!r} is not a comparator item id")
        if r.get("match") not in MATCHES:
            P.append(f"mapping[{n}].match: {r.get('match')!r} must be one of {', '.join(MATCHES)}")
    return P


def _best(values):
    for v in MATCHES:
        if v in values:
            return v
    return "none"


def _counts(values):
    c = collections.Counter(values)
    return [c[m] for m in MATCHES]


def _table(columns, rows):
    return {"kind": "table", "columns": columns, "rows": rows}


def build_items(c, mapping, entries) -> list:
    """The ready pack items: a framing para and the tables."""
    src = c["source"]
    its = c["items"]
    ids = [i["id"] for i in its]
    if src["kind"] == "own-action-plan":
        label = "Comparison against the organisation's action plan"
    else:
        label = "Comparison against the other report"
    out = [{"kind": "para", "text": f"{label}: {src['title']} ({src['issuer_role']}; {src['statutory_status']}). "
                                    "The comparison covers analysis coverage, not the quality of either investigation."}]
    out.append(_table(["Item type", "Items"], [[t, sum(1 for i in its if i["type"] == t)] for t in TYPE_PREFIX]))
    by_lr, by_ref = collections.defaultdict(list), collections.defaultdict(list)
    for r in mapping:
        by_lr[r["lr_id"]].append(r["match"])
        by_ref[r["ref"]].append(r["match"])
    lr_ids = [e["lr_id"] for e in entries] if entries is not None else sorted(by_lr)
    out.append(_table(["Direction", "Yes", "Partial", "None"], [
        ["Learnings against comparator items"] + _counts([_best(by_lr.get(x, [])) for x in lr_ids]),
        ["Comparator items against learnings"] + _counts([_best(by_ref.get(x, [])) for x in ids])]))
    tiers = collections.Counter(norm_hoc(i.get("hoc_tier")) for i in its if i["type"] in ("recommendation", "action"))
    out.append(_table(["Control tier", "Recommendations"],
                      [[t, tiers[t]] for t in HOC_TIERS + ["unclassified"] if tiers[t] or t != "unclassified"]))
    if entries is not None:
        owner = {e["lr_id"]: norm_entity(e.get("owner_entity")) for e in entries}
        grp = {i["id"]: _s(i.get("group")) or "(none)" for i in its}
        cross = collections.Counter((grp[r["ref"]], owner[r["lr_id"]]) for r in mapping
                                    if r["match"] != "none" and r["lr_id"] in owner)
        out.append(_table(["Comparator group", "Learning owner entity", "Matches"],
                          [[g, o, n] for (g, o), n in sorted(cross.items())]))
    return out


def _md(its) -> str:
    L = []
    for i in its:
        if i["kind"] == "para":
            L += [i["text"], ""]
        else:
            L += ["| " + " | ".join(i["columns"]) + " |", "|" + "---|" * len(i["columns"])]
            L += ["| " + " | ".join(str(c) for c in r) + " |" for r in i["rows"]] + [""]
    return "\n".join(L)


def _section_ids(path, what):
    p, err = _read_json(path, what)
    if err:
        return None, err
    if not isinstance(p, dict) or not isinstance(p.get("sections"), list):
        return None, f"{what}: {path} is not a pack with sections"
    return [s.get("id") for s in p["sections"] if isinstance(s, dict)], None


def check_client_safe(client, main) -> list:
    a, ea = _section_ids(client, "client-safe pack")
    b, eb = _section_ids(main, "main pack")
    if ea or eb:
        return [x for x in (ea, eb) if x]
    if a == b:
        return []
    P = []
    for x in b:
        if x not in a:
            P.append(f"client-safe pack lacks section {x}, which the main pack has")
    for x in a:
        if x not in b:
            P.append(f"client-safe pack has section {x}, which the main pack lacks")
    if not P:
        P.append(f"client-safe pack section order {a} differs from the main pack's {b}")
    return P


def cmd_compare(a):
    from .workspace import load_ws
    load_ws(a.ws)
    ws = Path(a.ws)
    problems = []
    if bool(a.client_safe) != bool(a.main):
        sys.exit("--client-safe and --main go together: give both packs")
    c, err = _read_json(a.comparator or ws / COMPARATOR_FILE, "comparator")
    if err:
        sys.exit(err)
    problems += validate_comparator(c)
    entries = None
    if a.register:
        reg, err = _read_json(a.register, "register")
        if err:
            sys.exit(err)
        entries = reg.get("entries") if isinstance(reg, dict) else reg
        if not isinstance(entries, list):
            sys.exit("register: no entries list")
    mp = Path(a.mapping) if a.mapping else ws / MAPPING_FILE
    if mp.is_file():
        m, err = _read_json(mp, "mapping")
        if err:
            sys.exit(err)
    else:
        m = []
        print(f"note: {mp} not found; every item counts as unmapped", file=sys.stderr)
    if not problems:
        problems += validate_mapping(m, {i["id"] for i in c["items"]},
                                     None if entries is None else {e.get("lr_id") for e in entries})
    if a.client_safe:
        problems += check_client_safe(a.client_safe, a.main)
    if problems:
        for p in problems:
            print(p, file=sys.stderr)
        sys.exit(f"{len(problems)} problem(s) in the comparator inputs.")
    its = build_items(c, m, entries)
    sys.stdout.write(json.dumps(its, indent=1, ensure_ascii=False) + "\n" if a.json else _md(its))
