"""The profile command."""
from __future__ import annotations

import collections
import datetime as dt
import json
from pathlib import Path

from . import BRAND, LEVEL_NAMES
from .analysis.timeline import _parse_dates
from .handling import _norm_status, is_edited
from .ingest.xlsx import personal_fields_present, REGULATOR_RX
from .util import _s, REFS
from .workspace import load_ws


# ----------------------------------------------------------------------------- profile

TIER_IDS = ("T1", "T2", "T3", "T4", "T5")


def _hfacs_levels() -> dict:
    return json.loads((REFS / "hfacs-codes.json").read_text(encoding="utf-8"))["levels"]


def _has_dated_text(w) -> bool:
    texts = [w.get("incident", {}).get("narrative", "")]
    texts += [_s(v) for f in w["findings"] for v in f.values() if isinstance(v, str)]
    texts += [_s(e.get("description")) for e in w.get("evidence", {}).values()]
    return any(h[1] < 3 for t in texts if t for h in _parse_dates(t))     # a bare year (pattern 3) orders nothing


def _thin_export_flags(w, ws) -> list:
    """Thin-export flags (P3-8). F99 and T9 shares and tier counts need clusters.json."""
    F, E = w["findings"], w.get("evidence", {})
    out = []
    sheets = {_s(n).strip().lower() for n in w.get("incident", {}).get("sheets") or []}
    if not E and sheets & {"evidence links", "evidence"}:
        out.append('Evidence Links sheet is empty: learnings rest on findings only; use evidence_strength "inferred"')
    elif not E:
        out.append('No Evidence Links sheet: learnings rest on findings only; use evidence_strength "inferred"')
    if not w.get("incident", {}).get("narrative", "").strip():
        out.append("No narrative text")
    if F and not _has_dated_text(w):
        out.append("No dated text: timelines will show order only")
    cp = Path(ws) / "clusters.json"
    if not F:
        return out
    if not cp.exists():
        out.append("Run classify to check the F99 and T9 shares")
        return out
    per = json.loads(cp.read_text(encoding="utf-8")).get("findings", {})
    n = len(F)
    f99 = sum(1 for f in F if "F99" in per.get(f["id"], {}).get("F", []))
    t9 = sum(1 for f in F if "T9" in per.get(f["id"], {}).get("T", []))
    if f99 * 10 > n:
        out.append(f"High F99 share: {f99} of {n} findings unmapped (over 10%)")
    if t9 * 4 > n:
        out.append(f"High T9 share: {t9} of {n} findings touch unresolved roles (over 25%)")
    tc = {t: sum(1 for f in F if t in per.get(f["id"], {}).get("T", [])) for t in TIER_IDS}
    empty = [t for t in TIER_IDS if tc[t] == 0]
    thin = [f"{t} ({tc[t]})" for t in TIER_IDS if 1 <= tc[t] <= 4]
    if empty:
        out.append("Empty tiers: " + ", ".join(empty))
    if thin:
        out.append("Thin tiers: " + ", ".join(thin))
    return out


def cmd_profile(a):
    w = load_ws(a.ws)
    F, E, inc = w["findings"], w.get("evidence", {}), w.get("incident", {})
    C = collections.Counter
    lvl = C(f["level"] for f in F)
    rat = C(f["rating"] for f in F)
    sub = C((f["level"], f["subcategory"]) for f in F)
    codes = C(f"{f['code']} {f['name']}" for f in F)
    roles = C(r for f in F for r in f["roles"])
    etypes = C(e["type"] for e in E.values())
    fields = inc.get("fields", {})
    L = []
    L.append(f"# Investigation profile: {fields.get('Incident Title', inc.get('source_file', ''))}\n")
    L.append("| Field | Value |\n|---|---|")
    for k in ("Incident Number", "Incident Title", "Incident Type", "Date", "Location", "Severity",
              "Investigation Status"):
        if k in fields:
            L.append(f"| {k} | {fields[k]} |")
    n = len(F)
    up = lvl.get(3, 0) + lvl.get(4, 0)
    L.append(f"\n**Findings:** {n} across {len(codes)} distinct factor codes. "
             f"**Evidence items:** {len(E)}. **Distinct role strings:** {len(roles)}.")
    if n:
        L.append(f"**Share at Supervision + Organisational levels:** {up} of {n} ({100*up/n:.0f}%).\n")
    L.append("## By level\n\n| Level | Name | Findings |\n|---|---|---:|")
    for k in sorted(x for x in lvl if x is not None):
        L.append(f"| {k} | {LEVEL_NAMES.get(k, '')} | {lvl[k]} |")
    L.append("\n## HFACS levels\n\n| Level | Name | Definition | Findings |\n|---|---|---|---:|")
    for k, d in sorted(_hfacs_levels().items(), key=lambda kv: int(kv[0])):
        L.append(f"| {k} | {d['name']} | {d['definition']} | {lvl.get(int(k), 0)} |")
    L.append("\n## By rating (higher = stronger causal contribution)\n\n| Rating | Findings |\n|---|---:|")
    for k in sorted(x for x in rat if x is not None):
        L.append(f"| {k} | {rat[k]} |")
    L.append("\n## Sub-categories\n\n| Level | Sub-category | Findings |\n|---|---|---:|")
    for (lv, sc), c in sub.most_common():
        L.append(f"| {lv} | {sc} | {c} |")
    L.append(f"\n## Most frequent factors (top {a.top})\n\n| Factor | Instances |\n|---|---:|")
    for k, c in codes.most_common(a.top):
        L.append(f"| {k} | {c} |")
    L.append(f"\n## Most-named roles (top {a.top}, raw strings)\n\n| Role | Findings |\n|---|---:|")
    for k, c in roles.most_common(a.top):
        L.append(f"| {k} | {c} |")
    L.append("\n## Evidence types\n\n| Type | Items |\n|---|---:|")
    for k, c in etypes.most_common():
        L.append(f"| {k or '(blank)'} | {c} |")
    flags = _thin_export_flags(w, a.ws)
    for col, lab in (("evidence_to_collect", "Evidence to Collect"), ("key_questions", "Key Questions"),
                     ("suggested_interviews", "Suggested Interviews"), ("causal_hypothesis", "Causal Hypothesis")):
        if n and not any(f[col] for f in F):
            flags.append(f"Column '{lab}' is empty on every finding (the investigator-coach skill can draft it).")
    if not inc.get("causal_chain_sheet"):
        flags.append("Causal Chain sheet is empty; use `pmlc.py causal` to extract links from the causal explanations.")
    if n and not any(is_edited(f["user_edited"]) for f in F):
        flags.append("No finding is marked 'User Edited'. Confirm the human review status before publishing learnings.")
    narr = inc.get("narrative", "")[:4000]
    sdate = fields.get("Date", "")
    if sdate and narr:
        try:
            d = dt.date.fromisoformat(sdate[:10])
            nd = [x[0] for x in _parse_dates(narr) if x[1] in (0, 1)]
            if nd and d not in nd:
                flags.append(f"Summary-sheet Date {sdate} does not appear in the narrative, which mentions "
                             f"{', '.join(sorted({x.isoformat() for x in nd})[:3])}. Confirm the date and pass "
                             f"`--date` to `dashboard`.")
        except ValueError:
            pass
    itype = fields.get("Incident Type", "")
    if itype and narr and itype.lower() not in narr.lower():
        flags.append(f"Incident Type '{itype}' is not mentioned in the narrative; check it before quoting it.")
    downs = [v for v in inc.get("review_votes", []) if _s(v.get("vote")).lower() in ("downgrade", "reject", "remove")]
    if downs:
        flags.append("Reviewer downgrade votes on: " + "; ".join(f"{v.get('finding')} ({v.get('reason', '')})" for v in downs)
                     + ". Exclude or flag these findings in learnings.")
    if _norm_status(fields.get("Investigation Status")) != "completed":
        flags.append(f"Investigation Status is '{_s(fields.get('Investigation Status')) or 'blank'}'; "
                     "label outputs as draft learnings.")
    rep = _s(fields.get("Reportable to Regulator"))
    if rep.lower() in ("", "no"):
        blob = " ".join([inc.get("narrative", "")] + [e.get("description", "") + " " + " ".join(
            lk.get("reference", "") for lk in e.get("links", [])) for e in E.values()])
        if REGULATOR_RX.search(blob):
            flags.append(f'Regulator involvement is mentioned but "Reportable to Regulator" is "{rep}": '
                         "confirm reporting status")
    pf = personal_fields_present(fields)
    if pf:
        flags.append(f"Personal fields present: do not quote {', '.join(pf)}")
    from .util import json_extra
    json_extra(incident=dict(fields), findings=n, evidence_items=len(E), distinct_factor_codes=len(codes),
               distinct_roles=len(roles), supervision_and_organisational=up,
               levels={str(k): lvl[k] for k in sorted(x for x in lvl if x is not None)},
               ratings={str(k): rat[k] for k in sorted(x for x in rat if x is not None)},
               sub_categories=[{"level": lv, "sub_category": sc, "findings": c} for (lv, sc), c in sub.most_common()],
               top_factors=[{"factor": k, "instances": c} for k, c in codes.most_common(a.top)],
               top_roles=[{"role": k, "findings": c} for k, c in roles.most_common(a.top)],
               evidence_types={(k or "(blank)"): c for k, c in etypes.most_common()},
               empty_columns=[lab for col, lab in (("evidence_to_collect", "Evidence to Collect"),
                                                   ("key_questions", "Key Questions"),
                                                   ("suggested_interviews", "Suggested Interviews"),
                                                   ("causal_hypothesis", "Causal Hypothesis"))
                              if n and not any(f[col] for f in F)],
               investigation_status=_s(fields.get("Investigation Status")),
               any_user_edited=any(is_edited(f["user_edited"]) for f in F),
               flags=list(flags))
    L.append("\n## Data-quality flags\n")
    L += [f"- {x}" for x in flags] or ["- None."]
    L.append(f"\n---\n*{BRAND}*")
    text = "\n".join(L)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"Profile written to {a.out}")
    else:
        print(text)
