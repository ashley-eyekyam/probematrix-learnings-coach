"""The check-register command and the register vocabulary."""
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

from .. import LEVEL_NAMES
from ..classify import TIER_LABELS
from ..handling import check_handling, unsigned_warning
from ..util import _flat, _n, _s
from ..workspace import downgraded_findings, EVD_RX, linked_evidence, load_ws
from .. import lint


HOC_TIERS = ["elimination", "substitution", "engineering", "administrative", "training", "ppe"]


def norm_level(v):
    m = re.search(r"\bL\s?([1-4])\b|level\s?([1-4])", _flat(v), re.I)
    return f"L{m.group(1) or m.group(2)} {LEVEL_NAMES[int(m.group(1) or m.group(2))]}" if m else "unclassified"


def norm_hoc(v):
    s = _flat(v).lower()
    for t in HOC_TIERS:
        if t in s or (t == "ppe" and "protective equipment" in s) or (t == "administrative" and "procedur" in s):
            return t
    return "unclassified"


def norm_entity(v):
    s = _flat(v)
    m = re.match(r"\s*(F\d{2}[a-z]?)\b", s)
    return m.group(1) if m else (s or "unset")


# ----------------------------------------------------------------------------- check-register

REGISTER_VOCAB = {
    "evidence_strength": ("direct", "corroborated", "inferred"),
    "confidence": ("high", "medium", "low"),
    "causal_role": ("initiating", "contributory", "escalating", "failed mitigation"),
    "transferability": ("same site", "other sites", "industry-wide"),
    "comparison": ("yes", "partial", "none", "not compared"),
}
PERFORMANCE_MODES = ("skill-based", "rule-based", "knowledge-based", "n/a")


def _vals(v) -> list:
    """Non-empty string values of a field; a list is taken element by element."""
    items = v if isinstance(v, (list, tuple)) else [v]
    return [x for x in (_s(i) for i in items if i is not None) if x]


def _fold_spelling(s) -> str:
    s = _s(s)
    return re.sub(r"\s+", " ", s.lower().replace("isation", "ization")).strip()


def register_warnings(entries: list, w: dict) -> list:
    """Controlled-vocabulary drift as 'warning: ...' lines. Absent or empty fields are not checked."""
    E = w.get("evidence", {})
    subs = {_fold_spelling(f["subcategory"]) for f in w.get("findings", []) if _s(f.get("subcategory"))}
    out = []
    for e in entries:
        lid = e.get("lr_id", "?")
        for field, allowed in REGISTER_VOCAB.items():
            for v in _vals(e.get(field)):
                if v.lower() not in allowed:
                    out.append(f"warning: {lid}: {field} {v!r} is not one of {', '.join(allowed)}")
        for v in _vals(e.get("performance_mode")):
            if not v.lower().startswith(PERFORMANCE_MODES):
                out.append(f"warning: {lid}: performance_mode {v!r} does not start with one of "
                           f"{', '.join(PERFORMANCE_MODES)}")
        tm = e.get("tier_messages")
        for k in (tm if isinstance(tm, dict) else {}):
            if k not in TIER_LABELS:
                out.append(f"warning: {lid}: tier_messages key {k!r} is not one of {', '.join(TIER_LABELS)}")
        bases = [e.get("evidence_basis")] + [r.get("evidence_basis") for r in (e.get("recommendations") or [])
                                              if isinstance(r, dict)]
        for eid in sorted({x for b in bases for v in _vals(b) for x in EVD_RX.findall(v)}):
            if eid not in E:
                out.append(f"warning: {lid}: evidence_basis names {eid}, which is not in the workspace")
        for lv in (_vals(e.get("hfacs_level")) if subs else []):
            m = re.match(r"\s*L\s?[1-4]\b[\s:.\-]*(.*)$", lv, re.I | re.S)
            rest = _fold_spelling(m.group(1)) if m else ""
            if rest and not any(rest == x or re.match(re.escape(x) + r"[\s(:]", rest) for x in subs):
                out.append(f"warning: {lid}: hfacs_level sub-category {lv!r} matches no sub-category in the export")
    return out

def cmd_check_register(a):
    w = load_ws(a.ws)
    reg = json.loads(Path(a.register).read_text(encoding="utf-8"))
    entries = reg["entries"] if isinstance(reg, dict) else reg
    F = {f["id"]: f for f in w["findings"]}
    E = w.get("evidence", {})
    cl = w.get("clusters", {}).get("findings", {})
    downs = downgraded_findings(w)
    problems, covered = [], set()
    for e in entries:
        lid = e.get("lr_id", "?")
        fids = e.get("finding_ids") or []
        if not fids:
            problems.append(f"{lid}: no finding_ids")
        for fid in fids:
            if fid not in F:
                problems.append(f"{lid}: unknown finding {fid}")
            else:
                covered.add(fid)
                if fid in downs:
                    problems.append(f"{lid}: cites {fid}, which has a reviewer downgrade vote")
        eids = e.get("evidence_ids") or []
        if not eids:
            problems.append(f"{lid}: no evidence_ids")
        linked = {x for fid in fids if fid in F for x in linked_evidence(F[fid])}
        for eid in eids:
            if eid not in E:
                problems.append(f"{lid}: unknown evidence {eid}")
            elif linked and eid not in linked:
                problems.append(f"{lid}: {eid} is not linked to any of its findings")
        if norm_level(e.get("hfacs_level")) == "unclassified":
            problems.append(f"{lid}: hfacs_level should start with L1-L4")
        if _s(e.get("priority")) not in ("1", "2", "3"):
            problems.append(f"{lid}: priority should be 1, 2 or 3")
        if not e.get("tier_messages"):
            problems.append(f"{lid}: no tier_messages")
        recs = e.get("recommendations") or []
        if not recs:
            problems.append(f"{lid}: no recommendations")
        for i, r in enumerate(recs, 1):
            if norm_hoc(r.get("hoc_tier")) == "unclassified":
                problems.append(f"{lid} rec {i}: hoc_tier not one of {HOC_TIERS}")
            if not _s(r.get("leading_indicator")):
                problems.append(f"{lid} rec {i}: no leading_indicator")
        # owner suggestion: entity with most findings in this learning
        cnt = collections.Counter(x for fid in fids for x in cl.get(fid, {}).get("F", []) if x != "F99")
        if cnt and norm_entity(e.get("owner_entity")) not in [k for k, _ in cnt.most_common(3)]:
            problems.append(f"{lid}: owner {norm_entity(e.get('owner_entity'))} is not among the top entities of its "
                            f"findings ({', '.join(k for k, _ in cnt.most_common(3))})")
    lint_hits = lint.lint(reg, w, kind="register", **lint.cli_options(a))
    problems += [lint.as_problem(h) for h in lint_hits if h.severity == "error"]
    uncovered = [fid for fid in F if fid not in covered and fid not in downs]
    hp, hw = check_handling(reg)
    problems += hp
    hw += unsigned_warning(reg, w, a.register, a.ws)
    print(f"{_n(len(entries), 'learning')}; {len(covered)} of {_n(len(F), 'finding')} covered "
          f"({100*len(covered)/max(len(F),1):.0f}%); {len(problems)} problem(s).")
    for p in problems[:80]:
        print(" -", p)
    if uncovered:
        print(f"Uncovered findings ({len(uncovered)}), highest rated first:")
        for fid in sorted(uncovered, key=lambda x: -(F[x]['rating'] or 0))[:20]:
            print(f"   {fid} {F[fid]['code']} r{F[fid]['rating']} {F[fid]['short'][:90]}")
    for line in register_warnings(entries, w):
        print(line)
    for line in hw:
        print(f"warning: {line}")
    for h in lint_hits:
        if h.severity != "error":
            print("warning: " + lint.as_problem(h))
    sys.exit(1 if problems else 0)
