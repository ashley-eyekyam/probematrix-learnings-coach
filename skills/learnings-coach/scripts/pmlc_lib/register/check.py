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
from ..workspace import downgraded_findings, EVD_RX, linked_evidence, load_ws, record_pack_check
from .. import lint


HOC_TIERS = ["elimination", "substitution", "engineering", "administrative", "training", "ppe"]


def norm_level(v):
    m = re.search(r"\bL\s?([1-4])\b|level\s?([1-4])", _flat(v), re.I)
    return f"L{m.group(1) or m.group(2)} {LEVEL_NAMES[int(m.group(1) or m.group(2))]}" if m else "unclassified"


# P3-4 / X11: administrative cues match at the START of a word, so "plant", "signal" and "significant" are no cue.
ADMIN_CUE_RX = re.compile(r"\b(?:review|procedur|checklist|audit|permit|plan(?!t)|instruction|sign(?!al|ific))")
STRONG_TIERS = ("elimination", "substitution", "engineering")     # the tiers above administrative
TIER_WORD_RX = {t: re.compile(r"\b" + stem) for t, stem in (
    ("elimination", "eliminat"), ("substitution", "substitut"), ("engineering", "engineer"),
    ("administrative", "administrat"), ("training", "train"), ("ppe", r"ppe\b"))}


def norm_hoc(v):
    """The control tier a hoc_tier text means (X22, replacing P3-4): an exact tier name (optional trailing
    'control(s)'); 'personal protective equipment' or PPE; an administrative cue at the start of a word; else the
    strongest tier mentioned, in HOC_TIERS order; else 'unclassified'."""
    s = re.sub(r"\s+", " ", _flat(v).lower()).strip()
    exact = re.sub(r"\s+controls?$", "", s)
    if exact in HOC_TIERS:
        return exact
    if "personal protective equipment" in s:
        return "ppe"
    if ADMIN_CUE_RX.search(s):
        return "administrative"
    for t in HOC_TIERS:
        if TIER_WORD_RX[t].search(s):
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

URGENCY = ("alert", "notice", "information")
REC_CLASSES = ("recommendation", "observation", "action_taken")
NINE_M = tuple(f"M{i}" for i in range(1, 10))
DUE_KEYS = ("due", "by_when", "due_date", "deadline")
DATE_RX = re.compile(r"\d{4}-\d{2}-\d{2}")
D7_WARNING = "owners and due dates are set by the organisation (D7)"
CheckResult = collections.namedtuple("CheckResult", "problems warnings stats")


def _role_words(w) -> set:
    """Words that make an owner text read as a role: the lint role nouns plus the words of the export's role strings."""
    words = {x.lower() for x in lint.load_terms().get("role_nouns", [])}
    for r in ((w or {}).get("clusters") or {}).get("role_map", {}):
        words |= lint._words(r)
    return words | {x[:-1] for x in words if x.endswith("s")}


def _is_role(text: str, words: set) -> bool:
    return any(x.lower() in words or x.lower().rstrip("s") in words for x in lint.WORD_RX.findall(text))


def _check_new_fields(e: dict, lid: str, problems: list) -> None:
    for field, allowed in (("urgency", URGENCY), ("recommendation_class", REC_CLASSES), ("nine_m", NINE_M)):
        for v in _vals(e.get(field)):
            if v.lower() not in [a.lower() for a in allowed]:
                problems.append(f"{lid}: {field} {v!r} is not one of {', '.join(allowed)}")
    if "verification" in e and not isinstance(e["verification"], dict):
        problems.append(f"{lid}: verification should be an object with the method and the indicator")
    for i, r in enumerate(e.get("recommendations") or [], 1):
        if isinstance(r, dict):
            for v in _vals(r.get("recommendation_class")):
                if v.lower() not in REC_CLASSES:
                    problems.append(f"{lid} rec {i}: recommendation_class {v!r} is not one of {', '.join(REC_CLASSES)}")


def _rec_warnings(e: dict, lid: str, w, words: set, out: list) -> None:
    dated = any(str(e.get(k) or "").strip() for k in DUE_KEYS)
    for i, r in enumerate(e.get("recommendations") or [], 1):
        if not isinstance(r, dict):
            continue
        owner = _s(r.get("owner"))
        if owner:
            if lint.personal_name(owner, w or {}):
                out.append(f"{lid} rec {i}: owner {owner!r} looks like a personal name; give a role")
            elif not _is_role(owner, words):
                out.append(f"{lid} rec {i}: owner {owner!r} does not look like a role")
        dated = dated or any(str(r.get(k) or "").strip() for k in DUE_KEYS)
        dated = dated or any(isinstance(v, str) and DATE_RX.fullmatch(v.strip()) for v in r.values())
    if dated:
        out.append(f"{lid}: {D7_WARNING}")


def check_register(reg, w=None, strict=False, lint_opts=None) -> CheckResult:
    """Check a Learnings Register against the workspace w (None: its structure only). Strict turns the priority-1
    rule (P3-3) from a warning into a problem. lint_opts are the check-language options (names, orgs, share)."""
    entries = reg["entries"] if isinstance(reg, dict) else reg
    has_ws = bool(w and w.get("findings") is not None)
    w = w or {}
    F = {f["id"]: f for f in w.get("findings", [])}
    E = w.get("evidence", {})
    cl = w.get("clusters", {}).get("findings", {})
    downs = downgraded_findings(w) if has_ws else set()
    words = _role_words(w)
    problems, warnings, covered = [], [], set()
    p1_weak = regulatory = 0
    for e in entries:
        lid = e.get("lr_id", "?")
        fids = e.get("finding_ids") or []
        if not fids:
            problems.append(f"{lid}: no finding_ids")
        for fid in fids:
            if has_ws and fid not in F:
                problems.append(f"{lid}: unknown finding {fid}")
            elif has_ws:
                covered.add(fid)
                if fid in downs:
                    problems.append(f"{lid}: cites {fid}, which has a reviewer downgrade vote")
        eids = e.get("evidence_ids") or []
        if not eids:
            problems.append(f"{lid}: no evidence_ids")
        linked = {x for fid in fids if fid in F for x in linked_evidence(F[fid])}
        for eid in eids:
            if has_ws and eid not in E:
                problems.append(f"{lid}: unknown evidence {eid}")
            elif linked and eid not in linked:
                problems.append(f"{lid}: {eid} is not linked to any of its findings")
        if norm_level(e.get("hfacs_level")) == "unclassified":
            problems.append(f"{lid}: hfacs_level should start with L1-L4")
        if _s(e.get("priority")) not in ("1", "2", "3"):
            problems.append(f"{lid}: priority should be 1, 2 or 3")
        if not e.get("tier_messages"):
            problems.append(f"{lid}: no tier_messages")
        recs = [r for r in (e.get("recommendations") or []) if isinstance(r, dict)]
        if not recs:
            problems.append(f"{lid}: no recommendations")
        for i, r in enumerate(recs, 1):
            raw = _s(r.get("hoc_tier"))
            tier = norm_hoc(raw)
            if not raw:
                problems.append(f"{lid} rec {i}: hoc_tier not one of {HOC_TIERS}")
            elif tier == "unclassified":
                warnings.append(f"{lid} rec {i}: hoc_tier '{raw}' is ambiguous")
            if not _s(r.get("leading_indicator")):
                problems.append(f"{lid} rec {i}: no leading_indicator")
        if _s(e.get("priority")) == "1" and not any(norm_hoc(r.get("hoc_tier")) in STRONG_TIERS for r in recs):
            p1_weak += 1
            if not _s(e.get("why_not_stronger")):
                msg = f"priority-1 learning {lid} has no fix above the administrative tier"
                (problems if strict else warnings).append(msg + ("" if strict else
                                                                 " (give why_not_stronger, or add a stronger fix)"))
        if _s(e.get("regulatory_touchpoint")):
            regulatory += 1
        _check_new_fields(e, lid, problems)
        _rec_warnings(e, lid, w, words, warnings)
        # owner suggestion: entity with the most findings in this learning (a warning: the author may know better)
        cnt = collections.Counter(x for fid in fids for x in cl.get(fid, {}).get("F", []) if x != "F99")
        if cnt and norm_entity(e.get("owner_entity")) not in [k for k, _ in cnt.most_common(3)]:
            warnings.append(f"{lid}: owner {norm_entity(e.get('owner_entity'))} is not among the top entities of its "
                            f"findings ({', '.join(k for k, _ in cnt.most_common(3))})")
    if has_ws:
        hits = lint.lint(reg, w, kind="register", **(lint_opts or {}))
        problems += [lint.as_problem(h) for h in hits if h.severity == "error"]
        warnings += [lint.as_problem(h) for h in hits if h.severity != "error"]
        warnings += [x[len("warning: "):] for x in register_warnings(entries, w)]
    hp, hw = check_handling(reg)
    problems += hp
    warnings += hw
    stats = {"learnings": len(entries), "findings_covered": len(covered), "findings_total": len(F),
             "regulatory_flagged": regulatory, "p1_without_strong_fix": p1_weak}
    return CheckResult(problems, warnings, stats)


def cmd_check_register(a):
    w = load_ws(a.ws)
    reg = json.loads(Path(a.register).read_text(encoding="utf-8"))
    res = check_register(reg, w, strict=getattr(a, "strict", False), lint_opts=lint.cli_options(a))
    res.warnings.extend(unsigned_warning(reg, w, a.register, a.ws))
    problems, warnings, st = res.problems, res.warnings, res.stats
    name = Path(a.register).name
    try:
        record_pack_check(a.ws, name[:-5] if name.endswith(".json") else name, a.register, not problems, len(problems),
                          strict=bool(getattr(a, "strict", False)))
    except OSError:
        pass
    if getattr(a, "json", False):
        print(json.dumps({"ok": not problems, "problems": problems, "warnings": warnings, "stats": st}, indent=2))
        sys.exit(1 if problems else 0)
    F = {f["id"]: f for f in w["findings"]}
    downs = downgraded_findings(w)
    covered = set(fid for e in (reg["entries"] if isinstance(reg, dict) else reg) for fid in e.get("finding_ids") or []
                  if fid in F)
    uncovered = [fid for fid in F if fid not in covered and fid not in downs]
    print(f"{_n(st['learnings'], 'learning')}; {st['findings_covered']} of {_n(st['findings_total'], 'finding')} covered "
          f"({100*st['findings_covered']/max(st['findings_total'], 1):.0f}%); {len(problems)} problem(s).")
    for p in problems[:80]:
        print(" -", p)
    if uncovered:
        print(f"Uncovered findings ({len(uncovered)}), highest rated first:")
        for fid in sorted(uncovered, key=lambda x: -(F[x]['rating'] or 0))[:20]:
            print(f"   {fid} {F[fid]['code']} r{F[fid]['rating']} {F[fid]['short'][:90]}")
    for x in warnings:
        print(f"warning: {x}")
    if st["regulatory_flagged"]:
        print(f"{st['regulatory_flagged']} learning(s) flagged for legal or compliance review")
    sys.exit(1 if problems else 0)
