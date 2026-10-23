"""The 9M lens (spec §7.3, §7.6; D9): references/nine-m.json (the nine Ms and their subcategories, names only from
the ProbeMatrix 9M framework, definitions and probes newly written), references/nine-m-map.json (the Nanocode -> M
map, new work) and the nine-m-seed command, which scores every finding per M and prints the M profile."""
from __future__ import annotations

import html
import json
import re
import sys
import zipfile
from pathlib import Path

from .ingest.schema import CAPA_PLANNER_SHEETS
from .util import REFS, _abs, write_json
from .workspace import file_sha256, load_ws, record_derived, top_rating

NINE_M_NONE = "None / unknown (record as a gap)"
NINE_M_CODES = tuple(f"M{i}" for i in range(1, 10))
# Scoring weights (spec §7.3): the Nanocode's primary M 3, each secondary M 1, a keyword hit 1, an entity hit 1.
NINE_M_W_PRIMARY, NINE_M_W_SECONDARY, NINE_M_W_KEYWORD, NINE_M_W_ENTITY = 3, 1, 1, 1
NINE_M_SEED_FILE = "nine_m_seed.json"
CAPA_PLANNER_MSG = ("This is a ProbeMatrix CAPA Planner workbook. nine-m-analysis reads the findings export only "
               "(Identified Findings); export that instead.")
NINE_M_TOP_CODES = 5
NINE_M_TOP_FINDINGS = 5


def load_nine_m(path=None) -> dict:
    """references/nine-m.json: {_about, version, chapters: [{code, title, definition, subcategories: [{id, name,
    definition, probes}]}]}."""
    return json.loads(Path(path or REFS / "nine-m.json").read_text(encoding="utf-8"))


def _ninem_bad_map(path, why):
    sys.exit(f"{path}: not a 9M map ({why}). Start from references/nine-m-map.json.")


def load_map(path=None) -> dict:
    """references/nine-m-map.json (or a file given with --map), checked: every primary and secondary M is M1..M9,
    every keyword compiles and every entity list is a list. A bad map stops with one plain sentence."""
    p = Path(path) if path else REFS / "nine-m-map.json"
    try:
        mp = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        sys.exit(f"Cannot read the 9M map {p}: {e}")
    if not isinstance(mp, dict):
        _ninem_bad_map(p, "the top level is not an object")
    for key in ("prefixes", "codes", "keywords", "entities"):
        if not isinstance(mp.get(key, {}), dict):
            _ninem_bad_map(p, f"'{key}' is not an object")
    for where in ("prefixes", "codes"):
        for k, v in mp.get(where, {}).items():
            if not isinstance(v, dict) or v.get("primary") not in NINE_M_CODES:
                _ninem_bad_map(p, f"{where} {k}: primary {v.get('primary') if isinstance(v, dict) else v!r} "
                                  f"is not one of M1-M9")
            bad = [m for m in v.get("secondary", []) if m not in NINE_M_CODES]
            if bad:
                _ninem_bad_map(p, f"{where} {k}: secondary {', '.join(map(str, bad))} is not one of M1-M9")
    for where in ("keywords", "entities"):
        for m, v in mp.get(where, {}).items():
            if m not in NINE_M_CODES or not isinstance(v, list):
                _ninem_bad_map(p, f"{where} {m}: the key must be M1-M9 and the value a list")
    for m, rxs in mp.get("keywords", {}).items():
        for rx in rxs:
            try:
                re.compile(rx)
            except re.error as e:
                _ninem_bad_map(p, f"keywords {m}: {rx!r} does not compile ({e})")
    return mp


def resolve_code(code, mp) -> dict | None:
    """{primary, secondary} for a Nanocode: its own entry under 'codes', else its prefix default; None if neither."""
    code = (code or "").strip()
    if code in mp.get("codes", {}):
        return mp["codes"][code]
    return mp.get("prefixes", {}).get(code.split(" ")[0] if code else "")


_NINEM_RX_CACHE: dict = {}


def _ninem_rx(mp) -> dict:
    key = json.dumps(mp.get("keywords", {}), sort_keys=True)
    if key not in _NINEM_RX_CACHE:
        _NINEM_RX_CACHE[key] = {m: [re.compile(r, re.I) for r in mp.get("keywords", {}).get(m, [])] for m in NINE_M_CODES}
    return _NINEM_RX_CACHE[key]


def keyword_ms(f, mp) -> list:
    """The Ms whose keywords match the finding's Instance Label or Short Description (one hit per M, in M order).
    The justification and causal text are left out: they mention most Ms and would drown the signal (R6 §4.3)."""
    text = f"{f.get('label') or ''}\n{f.get('short') or ''}"
    rx = _ninem_rx(mp)
    return [m for m in NINE_M_CODES if any(r.search(text) for r in rx[m])]


def entity_ms(fid, w, mp) -> list:
    """The Ms whose entity list shares an entity with the finding's Learning Clusters (clusters.json)."""
    ents = set(((w.get("clusters") or {}).get("findings", {}).get(fid) or {}).get("F", []))
    return [m for m in NINE_M_CODES if ents & set(mp.get("entities", {}).get(m, []))]


def score_finding(f, w, mp) -> dict:
    """{m_primary, m_secondary, scores} for one finding.

    The Nanocode's primary M is m_primary: with the spec weights no other M can outscore it (secondary, keyword
    and entity reach 3 at most, and a tie keeps the Nanocode's choice). m_secondary is the Nanocode's secondary Ms
    plus any other M that two signals agree on (score 2 or more), in M order. An unmapped code has no primary."""
    r = resolve_code(f.get("code"), mp)
    scores = dict.fromkeys(NINE_M_CODES, 0)
    primary, secondary = None, []
    if r:
        primary = r["primary"]
        secondary = [m for m in r.get("secondary", []) if m != primary]
        scores[primary] += NINE_M_W_PRIMARY
        for m in secondary:
            scores[m] += NINE_M_W_SECONDARY
    for m in keyword_ms(f, mp):
        scores[m] += NINE_M_W_KEYWORD
    for m in entity_ms(f["id"], w, mp):
        scores[m] += NINE_M_W_ENTITY
    sec = [m for m in NINE_M_CODES if m != primary and (m in secondary or scores[m] >= 2)]
    return {"m_primary": primary, "m_secondary": sec, "scores": {m: n for m, n in scores.items() if n}}


def seed(w, mp=None) -> dict:
    """The nine_m_seed.json shape: every finding scored per M, the M profile (primary findings by level, top-rated,
    top codes and top findings) and the unmapped findings. Deterministic: findings in file order, ties by id."""
    mp = mp if mp is not None else load_map()
    F = w["findings"]
    notes = []
    if not w.get("clusters"):
        notes.append("No clusters.json: the entity signal was not used. Run: pmlc.py classify <ws>")
    out_f, unmapped, unknown = {}, [], {}
    for f in F:
        s = score_finding(f, w, mp)
        out_f[f["id"]] = s
        if s["m_primary"] is None:
            unmapped.append(f["id"])
            unknown.setdefault((f.get("code") or "").split(" ")[0] or "(blank)", []).append(f.get("code") or "")
    for pre, codes in sorted(unknown.items()):
        notes.append(f"Prefix {pre} is not in the 9M map ({', '.join(sorted(set(codes)))}): "
                     f"{len(codes)} finding(s) unmapped; add it to nine-m-map.json or pass --map")
    top = top_rating(w)
    profile = {}
    for m in NINE_M_CODES:
        mine = [f for f in F if out_f[f["id"]]["m_primary"] == m]
        by_level = {str(lv): sum(1 for f in mine if f.get("level") == lv) for lv in (1, 2, 3, 4)}
        codes = {}
        for f in mine:
            c = codes.setdefault(f["code"], {"code": f["code"], "n": 0, "name": f.get("name") or ""})
            c["n"] += 1
        ranked = sorted(enumerate(mine), key=lambda t: (-(t[1].get("rating") or 0), -(t[1].get("level") or 0), t[0]))
        profile[m] = {"findings": len(mine), "by_level": by_level,
                      "top_rated": sum(1 for f in mine if top and (f.get("rating") or 0) == top),
                      "top_codes": sorted(codes.values(), key=lambda c: (-c["n"], c["code"]))[:NINE_M_TOP_CODES],
                      "top_findings": [f["id"] for _, f in ranked[:NINE_M_TOP_FINDINGS]]}
    return {"version": 1, "map_version": mp.get("version"), "findings": out_f, "profile": profile,
            "unmapped": unmapped, "notes": notes}


def is_capa_planner(path) -> bool:
    """True when the file is a ProbeMatrix CAPA Planner workbook: at least two of its sheets Corrective Actions,
    Preventive Actions, Chapter Headers and Residual Risks (the rule ingest uses), and no Identified Findings sheet.
    Reads only the workbook's sheet list, so a large or broken file costs nothing and never raises."""
    p = Path(path)
    if not p.is_file():
        return False
    try:
        with zipfile.ZipFile(p) as z:
            wbxml = z.read("xl/workbook.xml").decode("utf-8", "replace")
    except (OSError, KeyError, zipfile.BadZipFile):   # not a zip, or a zip that is not a workbook: not a planner
        return False
    names = {html.unescape(n).strip().lower() for n in re.findall(r"<(?:\w+:)?sheet\b[^>]*\bname=\"([^\"]*)\"", wbxml)}
    return "identified findings" not in names and sum(s.lower() in names for s in CAPA_PLANNER_SHEETS) >= 2


def _ninem_table(s, w) -> list:
    nm = {c["code"]: c["title"] for c in load_nine_m()["chapters"]}
    F = {f["id"]: f for f in w["findings"]}
    top = top_rating(w)
    secondary = {m: 0 for m in NINE_M_CODES}
    signal = {m: 0 for m in NINE_M_CODES}
    for fid, v in s["findings"].items():
        for m in v["m_secondary"]:
            secondary[m] += 1
        for m in v["scores"]:
            if m != v["m_primary"] and m not in v["m_secondary"]:
                signal[m] += 1
    lines = [f"9M seed: {len(F)} findings" + (f", top rating {top}" if top else ""), "",
             "| M | Name | Primary | L1 | L2 | L3 | L4 | By rating | Top-rated | Secondary | Signal only | Top codes |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in NINE_M_CODES:
        p = s["profile"][m]
        rat = {}
        for fid, v in s["findings"].items():
            if v["m_primary"] == m:
                r = F[fid].get("rating") or 0
                rat[r] = rat.get(r, 0) + 1
        by_r = ", ".join(f"{r}: {n}" for r, n in sorted(rat.items(), reverse=True)) or "-"
        codes = ", ".join(f"{c['code']} ({c['n']})" for c in p["top_codes"]) or "-"
        lv = p["by_level"]
        lines.append(f"| {m} | {nm.get(m, m)} | {p['findings']} | {lv['1']} | {lv['2']} | {lv['3']} | {lv['4']} | "
                     f"{by_r} | {p['top_rated']} | {secondary[m]} | {signal[m]} | {codes} |")
    lines.append("")
    for m in NINE_M_CODES:
        tf = s["profile"][m]["top_findings"]
        if tf:
            lines.append(f"{m} top findings: " + "; ".join(
                f"{fid} ({F[fid]['code']}, rating {F[fid].get('rating')}): {F[fid].get('label') or ''}" for fid in tf))
    lines.append("")
    lines.append("Unmapped: " + (f"{len(s['unmapped'])} ({', '.join(s['unmapped'])})" if s["unmapped"] else "none"))
    for n in s["notes"]:
        lines.append(f"Note: {n}")
    return lines


def cmd_nine_m_seed(a):
    target = _abs(a.ws)
    if target.is_file():
        if is_capa_planner(target):
            print(CAPA_PLANNER_MSG, file=sys.stderr)
            sys.exit(2)
        print(f"nine-m-seed reads a workspace folder, not {target.name}. Run: pmlc.py setup <export.xlsx> --slug "
              f"<site>-<event>, then pass the workspace it prints.", file=sys.stderr)
        sys.exit(2)
    if not target.is_dir():
        sys.exit(f"{target} is not a workspace folder. Run: pmlc.py setup <export.xlsx> --slug <site>-<event>")
    w = load_ws(target)
    mp = load_map(a.map)
    s = seed(w, mp)
    out = Path(a.out) if a.out else target / NINE_M_SEED_FILE
    write_json(out, json.loads(json.dumps(s, sort_keys=True)))
    if out.resolve() == (target / NINE_M_SEED_FILE).resolve():
        record_derived(target, NINE_M_SEED_FILE, {n: file_sha256(target / n) for n in ("findings.json", "clusters.json")
                                           if (target / n).is_file()})
    print("\n".join(_ninem_table(s, w)))
    print(f"\nWrote {out}")
