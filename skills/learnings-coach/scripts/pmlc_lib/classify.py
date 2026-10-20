"""Role taxonomy, overlays, overrides and the classify command."""
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

from .util import _abs, _overlay_path, REFS, write_json
from .workspace import file_sha256, load_manifest, load_ws, record_derived, taxonomy_hash, taxonomy_sources
from . import privacy


def _load_taxonomy(path=None, overlays=()) -> dict:
    """The taxonomy rules with compiled regexes. Each overlay (name or path) ORs its extra regexes onto the base
    rules with the same IDs: match = (?:base)|(?:extra)."""
    p = Path(path) if path else REFS / "taxonomy.json"
    if path and not p.is_file():
        sys.exit(f"--taxonomy {path}: file not found")
    t = json.loads(p.read_text(encoding="utf-8"))
    t["_file"] = str(path) if path else "taxonomy.json"
    t["_overlays"] = []
    for x in overlays:
        op = _overlay_path(x)
        if not op.exists():
            sys.exit(f"Overlay {x} not found at {op}. Pass a name from references/overlays/ or a path to a .json file.")
        try:
            ov = json.loads(op.read_text(encoding="utf-8"))
        except ValueError:
            sys.exit(f"overlay {op.stem}: not valid JSON ({op}). Fix the file or pass another overlay.")
        if not isinstance(ov, dict):
            sys.exit(f"overlay {op.stem}: must be a JSON object with an `extend` block ({op}).")
        name = ov.get("name") or op.stem
        ext = ov.get("extend") or {}
        if not isinstance(ext, dict):
            sys.exit(f"overlay {name}: `extend` must be an object keyed by entities, tiers or relations.")
        for group in ("entities", "tiers", "relations"):
            rules = {r["id"]: r for r in t[group]}
            if ext.get(group) is not None and not isinstance(ext.get(group), dict):
                sys.exit(f"overlay {name}: extend.{group} must be an object")
            for rid, extra in (ext.get(group) or {}).items():
                if rid not in rules:
                    sys.exit(f"Overlay {name} extends {rid}, which is not in the {group} of taxonomy {t['_file']}.")
                rules[rid]["match"] = f"(?:{rules[rid]['match']})|(?:{extra})"
        t["_overlays"].append(name)
    for group in ("entities", "tiers", "relations"):
        for rule in t[group]:
            rule["_rx"] = re.compile(rule["match"], re.I)
            rule["_ex"] = re.compile(rule["exclude"], re.I) if rule.get("exclude") else None
            rule["_wk"] = re.compile(rule["weak"], re.I) if rule.get("weak") else None
    return t


def map_role(role: str, tax: dict) -> dict:
    ents = [e["id"] for e in tax["entities"]
            if e["_rx"].search(role) and not (e["_ex"] and e["_ex"].search(role))]
    tier = next((t["id"] for t in tax["tiers"] if t["_rx"].search(role)), None) \
        or next((t["id"] for t in tax["tiers"] if t["_wk"] and t["_wk"].search(role)), "T9")
    rel = next((r["id"] for r in tax["relations"] if r["_rx"].search(role)), tax["default_relation"]["id"])
    return {"F": ents, "T": tier, "R": rel, "source": "rule"}


def entities_for_tags(clusters: dict, tags: list) -> list:
    """Entity IDs (taxonomy order) carrying any of the tags. Exits when a tag is unknown or clusters.json has no tags."""
    tx = clusters.get("taxonomy", {})
    tagmap = tx.get("tags") or {}
    in_use = sorted({t for ts in tagmap.values() for t in ts})
    if not in_use:
        sys.exit(f"Taxonomy {tx.get('file', 'unknown')} defines no tags: add `tags` to its entities (see "
                 "references/taxonomy.json), or re-run classify if clusters.json predates v2.0.")
    missing = [t for t in tags if t not in in_use]
    if missing:
        sys.exit(f"No entity has tag(s) {missing} in taxonomy {tx.get('file', 'unknown')}. Tags in use: "
                 f"{', '.join(in_use)}.")
    return [e for e, ts in tagmap.items() if set(ts) & set(tags)]


def _taxonomy_label(file, overlays) -> str:
    return " + ".join([file, *overlays])


OVERRIDE_SHAPE = '{"<role>": {"F": ["F05"], "T": "T3", "R": "owner"}}'


def load_overrides(path: Path, tax: dict | None = None) -> dict:
    """{role: {F: [ids], T: id, R: id}} from an overrides file, with F normalised to a list. Exits with a sentence
    naming the file (and the role) when the file is missing, is not JSON or has the wrong shape, or, given the
    taxonomy, when an ID is not one of its entities (or F99), tiers (or T9) or relations (or the default)."""
    p = Path(path)
    if not p.is_file():
        sys.exit(f"Overrides file {path} not found. Pass an existing file or --no-overrides.")
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        sys.exit(f"{path} is not valid JSON ({err}). Fix it or pass --no-overrides.")
    if not isinstance(raw, dict):
        sys.exit(f"{path} must be a JSON object of roles, shaped {OVERRIDE_SHAPE}.")
    allowed = None
    if tax is not None:
        allowed = {"F": {e["id"] for e in tax["entities"]} | {"F99"}, "T": {t["id"] for t in tax["tiers"]} | {"T9"},
                   "R": {r["id"] for r in tax["relations"]} | {tax["default_relation"]["id"]}}
    out = {}
    for role, o in raw.items():
        where = f"{path}: the override for role {role!r}"
        if not isinstance(o, dict):
            sys.exit(f"{where} must be an object shaped {OVERRIDE_SHAPE}, not {json.dumps(o)}.")
        extra = sorted(set(o) - {"F", "T", "R"})
        if extra:
            sys.exit(f"{where} has unknown key(s) {', '.join(extra)}; only F, T and R are read.")
        o = dict(o)
        if isinstance(o.get("F"), str):
            o["F"] = [o["F"]]
        if "F" in o and not (isinstance(o["F"], list) and all(isinstance(x, str) for x in o["F"])):
            sys.exit(f"{where} has F {json.dumps(o['F'])}; F must be a list of entity IDs such as [\"F05\"].")
        for k in ("T", "R"):
            if k in o and not isinstance(o[k], str):
                sys.exit(f"{where} has {k} {json.dumps(o[k])}; {k} must be one ID as a string.")
        if allowed:
            for k in ("F", "T", "R"):
                bad = [x for x in ([] if k not in o else o[k] if k == "F" else [o[k]]) if x not in allowed[k]]
                if bad:
                    sys.exit(f"{where} has unknown {k} ID(s) {', '.join(bad)}; taxonomy {tax['_file']} has "
                             f"{', '.join(sorted(allowed[k]))}.")
        out[role] = o
    return out


def _same_taxonomy_file(ws, prev, taxonomy) -> bool:
    """True when this classify's taxonomy file is the one the previous classify recorded (compared by real path)."""
    src = load_manifest(ws).get("files", {}).get("clusters.json", {}).get("sources", {}).get("taxonomy") or []
    now = Path(taxonomy) if taxonomy else REFS / "taxonomy.json"
    return bool(src) and Path(src[0]).resolve() == now.resolve()


def _previous_taxonomy(ws: Path, prev: dict):
    """(taxonomy path or None for the base one, [overlay names or paths]) that the last classify used. Prefers the
    manifest's absolute sources; a built-in overlay comes back as its bare name."""
    src = load_manifest(ws).get("files", {}).get("clusters.json", {}).get("sources", {}).get("taxonomy") or []
    names = list(prev.get("overlays", []))
    file = prev.get("file")
    tax = None
    custom = bool(file) and file != "taxonomy.json"
    if src and file == "taxonomy.json" and Path(src[0]).resolve() != (REFS / "taxonomy.json").resolve():
        custom = True  # a custom file that happens to be called taxonomy.json, recorded by its absolute path
    if custom:
        tax = src[0] if src and Path(src[0]).is_file() else file
    paths = src[1:] if len(src) == len(names) + 1 else [None] * len(names)
    builtin = (REFS / "overlays").resolve()
    overlays = []
    for name, op in zip(names, paths):
        if op and Path(op).is_file():
            overlays.append(Path(op).stem if Path(op).resolve().parent == builtin else op)
        else:
            overlays.append(name)
    return tax, overlays


def cmd_classify(a):
    ws = Path(a.ws)
    w = load_ws(ws)
    if a.no_overlay and a.overlay:
        sys.exit("--no-overlay and --overlay cannot be combined; pass one or the other.")
    prev = w.get("clusters", {}).get("taxonomy", {})
    taxonomy, overlays = a.taxonomy, list(a.overlay or ())
    reused, reused_tax = False, False
    if (not a.taxonomy or not a.overlay) and "file" in prev:
        rec_tax, rec_overlays = _previous_taxonomy(ws, prev)
        if not a.taxonomy:  # a flag for only one half keeps the other half from the previous classify
            taxonomy, reused_tax = rec_tax, bool(rec_tax)
        if not a.overlay and not a.no_overlay:
            overlays = rec_overlays
        if taxonomy and not Path(taxonomy).is_file():
            sys.exit(f"The previous classify used taxonomy {taxonomy}, which is no longer there. Pass --taxonomy "
                     f"<file> to choose one (the base taxonomy is {REFS / 'taxonomy.json'}).")
        reused = reused_tax or bool(overlays and not a.overlay)
        if reused:
            print(f"Reusing taxonomy {taxonomy or 'taxonomy.json'} and overlays {', '.join(overlays) or 'none'} "
                  "from the previous classify (pass --taxonomy/--overlay to change, --no-overlay for none).")
    if a.taxonomy and overlays and not a.overlay and not a.no_overlay:
        print(f"hint: overlay(s) {', '.join(overlays)} were remembered from the previous classify; "
              "pass --no-overlay to drop the remembered overlay")
    tax = _load_taxonomy(taxonomy, overlays)
    if reused_tax:
        tax["_file"] = prev["file"]  # the same file under the name it was recorded with
    if "file" in prev:
        was, now = _taxonomy_label(prev["file"], prev.get("overlays", [])), _taxonomy_label(tax["_file"], tax["_overlays"])
        if was != now and _same_taxonomy_file(ws, prev, taxonomy) and prev.get("overlays", []) == tax["_overlays"]:
            was = now  # the same file reached by a relative path one time and an absolute one the next
        if was != now:
            print(f"warning: previous classify used {was}; this run uses {now}")
    ov_path, remembered = None, False
    if a.no_overrides and a.overrides:
        print("warning: --no-overrides wins: ignoring --overrides", file=sys.stderr)
    if not a.no_overrides:
        if a.overrides:
            ov_path = a.overrides
        elif (ws / "role_overrides.json").exists():
            ov_path = str(ws / "role_overrides.json")
        else:  # an explicit --overrides file from the previous classify is remembered like the taxonomy is
            rec = load_manifest(ws).get("files", {}).get("clusters.json", {}).get("sources", {})
            if rec.get("overrides") and not rec.get("overrides_auto") and Path(rec["overrides"]).is_file():
                ov_path = rec["overrides"]
                remembered = True
    overrides = load_overrides(Path(ov_path), tax) if ov_path else {}
    role_map = {}
    for f in w["findings"]:
        for r in f["roles"]:
            if r in role_map:
                continue
            m = map_role(r, tax)
            if r in overrides:
                o = overrides[r]
                m = {"F": o.get("F", m["F"]), "T": o.get("T", m["T"]), "R": o.get("R", m["R"]), "source": "override"}
            role_map[r] = m
    applied = sum(1 for m in role_map.values() if m["source"] == "override")
    stale = sorted(k for k in overrides if k not in role_map)
    names = {e["id"]: e["name"] for e in tax["entities"]}
    names["F99"] = "Unmapped"
    tier_names = {t["id"]: t["name"] for t in tax["tiers"]}
    tier_names["T9"] = "Unresolved"
    per_f, ent_idx = {}, collections.defaultdict(list)
    for f in w["findings"]:
        Fs, Ts, Rs = set(), set(), set()
        for r in f["roles"]:
            m = role_map[r]
            Fs.update(m["F"] or ["F99"])
            Ts.add(m["T"])
            Rs.add(m["R"])
        if not f["roles"]:
            Fs.add("F99")
        per_f[f["id"]] = {"F": sorted(Fs), "T": sorted(Ts), "R": sorted(Rs)}
        for e in Fs:
            ent_idx[e].append(f["id"])
    byid = {f["id"]: f for f in w["findings"]}
    top_rating = max((f["rating"] or 0) for f in w["findings"]) if w["findings"] else 0
    entities = {}
    for e, ids in sorted(ent_idx.items()):
        lv = collections.Counter(byid[i]["level"] for i in ids)
        entities[e] = {"name": names.get(e, e), "findings": ids, "n": len(ids),
                       "by_level": {str(k): lv.get(k, 0) for k in (1, 2, 3, 4)},
                       "top_rated": sum(1 for i in ids if byid[i]["rating"] == top_rating)}
    unresolved = sorted(r for r, m in role_map.items() if not m["F"] or m["T"] == "T9")
    out = {"taxonomy": {"entities": names, "tiers": tier_names,
                        "relations": {r["id"]: r["name"] for r in tax["relations"]} | {
                            tax["default_relation"]["id"]: tax["default_relation"]["name"]},
                        "tags": {e["id"]: list(e.get("tags", [])) for e in tax["entities"]},
                        "file": tax["_file"], "overlays": tax["_overlays"]},
           "entities": entities, "findings": per_f, "role_map": role_map, "unresolved_roles": unresolved,
           "overrides": {"file": ov_path, "applied": applied, "stale": stale}}
    write_json(ws / "clusters.json", out)
    write_json(ws / "singleton_roles.json", privacy.build_singletons(role_map, w["findings"], tax, TIER_LABELS))
    tpaths = taxonomy_sources(taxonomy, overlays)
    for derived in ("clusters.json", "singleton_roles.json"):
        record_derived(ws, derived,
                       {"findings.json": file_sha256(ws / "findings.json"), "taxonomy": taxonomy_hash(tpaths),
                        "overrides": file_sha256(ov_path) if ov_path else "none"},
                       {"taxonomy": [str(_abs(p)) for p in tpaths],
                        "overrides": str(_abs(ov_path)) if ov_path else None,
                        "overrides_auto": not a.no_overrides and not a.overrides and not remembered})
    if ov_path:
        print(f"Applied {applied} override(s) from {ov_path}")
    if stale:
        print(f"warning: {len(stale)} override(s) match no role: {', '.join(stale)}")
    tc = collections.Counter(t for v in per_f.values() for t in v["T"])
    print(f"Classified {len(role_map)} distinct roles; {len(unresolved)} need resolution "
          f"(no entity or no tier). Wrote {ws/'clusters.json'}\n")
    print("| Cluster | Name | Findings | L1/L2/L3/L4 |\n|---|---|---:|---|")
    for e, d in entities.items():
        bl = d["by_level"]
        print(f"| {e} | {d['name']} | {d['n']} | {bl['1']}/{bl['2']}/{bl['3']}/{bl['4']} |")
    print("\n| Tier | Findings touching |\n|---|---:|")
    for t in sorted(tc):
        print(f"| {t} {tier_names.get(t, '')} | {tc[t]} |")
    if unresolved:
        p = ws / "unresolved_roles.json"
        write_json(p, unresolved)
        print(f"\nUnresolved roles listed in {p}. Resolve them into an overrides JSON "
              f"({{role: {{F: [...], T: ..., R: ...}}}}) in {ws/'role_overrides.json'} and re-run classify; "
              f"that file is picked up automatically.")
    else:
        (ws / "unresolved_roles.json").unlink(missing_ok=True)


TIER_LABELS = {"T1": "Frontline", "T2": "Supervisors", "T3": "Function managers", "T4": "Site leadership",
               "T5": "Corporate / board"}
