"""Records and detail data embedded in HTML pages."""
from __future__ import annotations

import collections
import json
import re
import sys

from .. import brand_payload
from ..classify import TIER_LABELS
from ..handling import share_mode
from ..register.check import HOC_TIERS, norm_entity, norm_hoc, norm_level
from ..register.xlsx import REG_COLS
from ..util import _s, HERE
from ..workspace import downgraded_findings


# ----------------------------------------------------------------------------- dashboard

DASHBOARD_ASSETS = HERE / "dashboard_assets"


def citation_records(w: dict, finding_ids, evidence_ids=()) -> tuple:
    """Full workspace records for the given findings (each with its clusters and reviewer votes), and for the
    given evidence plus every evidence item those findings link. Unknown IDs are skipped; first-seen order kept.
    Shared by the Detailed register tab and learning packs so both embed identical records."""
    F = {f["id"]: f for f in w["findings"]}
    E = w.get("evidence", {})
    clf = w.get("clusters", {}).get("findings", {})
    votes = collections.defaultdict(list)
    for v in w.get("incident", {}).get("review_votes", []):
        votes[v.get("finding")].append(v)
    findings = {}
    for fid in finding_ids:
        if fid in F and fid not in findings:
            findings[fid] = dict(F[fid], clusters=clf.get(fid, {}), votes=votes.get(fid, []))
    eids = []
    for x in list(evidence_ids) + [x for f in findings.values() for x in (f.get("evidence") or [])]:
        if x not in eids:
            eids.append(x)
    return findings, {x: E[x] for x in eids if x in E}


# --embed (L4-17, L7-03): which workspace records an HTML page carries in its JSON payload.
EMBED_MODES = ("cited", "summary", "full")
EMBED_DEFAULT = "cited"
# --embed summary drops every key whose normalised name is one of these, at any depth, plus the evidence
# description, the Specific Reference quote of each evidence link (stored as links[].reference) and vote reasons.
SUMMARY_DROP_KEYS = {"specific_reference", "suggested_interviews", "key_questions"}
WITNESS_NOTE = "note: embedded evidence includes witness statements; consider --embed summary"
QUOTE_OMITTED = "[quote omitted]"
MIN_QUOTE = 12        # shorter evidence strings ("Index", "Work order") are labels, not quotes


def resolve_embed(a) -> str:
    """The embed mode a renderer uses: --embed when given; else summary for --share external|public (P2-9; the share
    gate refuses an explicit cited or full), else the default."""
    return getattr(a, "embed", None) or ("summary" if share_mode(a) != "internal" else EMBED_DEFAULT)


def label_only(f: dict) -> dict:
    """A finding as an uncovered or excluded entry travels under --embed cited: its label and rating only."""
    return {"id": f["id"], "label": f.get("label", ""), "rating": f.get("rating")}


def _norm_key(k) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(k).lower()).strip("_")


def _strip_summary(v):
    if isinstance(v, list):
        return [_strip_summary(x) for x in v]
    if isinstance(v, dict):
        return {k: _strip_summary(x) for k, x in v.items() if _norm_key(k) not in SUMMARY_DROP_KEYS}
    return v


def quote_rx(w: dict):
    """One pattern for every evidence description and Specific Reference in the workspace (longest first), or None.
    --embed summary replaces them where a finding's text repeats them word for word, as AI justifications often do."""
    qs = {_s(e.get("description")) for e in (w.get("evidence") or {}).values()}
    qs |= {_s(ln.get("reference")) for e in (w.get("evidence") or {}).values() for ln in (e.get("links") or [])}
    qs = sorted((q for q in qs if len(q) >= MIN_QUOTE), key=len, reverse=True)
    return re.compile("|".join(map(re.escape, qs))) if qs else None


def _omit_quotes(v, rx):
    if isinstance(v, str):
        return rx.sub(QUOTE_OMITTED, v)
    if isinstance(v, list):
        return [_omit_quotes(x, rx) for x in v]
    if isinstance(v, dict):
        return {k: _omit_quotes(x, rx) for k, x in v.items()}
    return v


def summary_record(rec: dict, evidence: bool = False, quotes=None) -> dict:
    """A copy of one finding or evidence record without its quotes: see SUMMARY_DROP_KEYS. quotes (quote_rx)
    also replaces any evidence description or Specific Reference the record repeats."""
    out = _strip_summary(rec)
    if isinstance(out.get("votes"), list):
        out["votes"] = [{k: x for k, x in v.items() if k != "reason"} if isinstance(v, dict) else v
                        for v in out["votes"]]
    if evidence:
        out.pop("description", None)
        if isinstance(out.get("links"), list):
            out["links"] = [{k: x for k, x in ln.items() if k != "reference"} if isinstance(ln, dict) else ln
                            for ln in out["links"]]
    return _omit_quotes(out, quotes) if quotes else out


def embedded_records(w: dict, cited, evidence_ids, others=(), embed: str = EMBED_DEFAULT,
                     linked: bool = True) -> tuple:
    """(findings, evidence) a page embeds. full: citation_records of the cited and the other findings, as before
    --embed existed. cited: full records of the cited findings and evidence only (plus, when linked, the evidence
    the cited findings link), and the other findings (uncovered, excluded) as label-only stubs. summary: cited,
    without quotes (summary_record), and with any evidence description or Specific Reference that a record repeats
    word for word replaced by QUOTE_OMITTED."""
    if embed not in EMBED_MODES:
        raise ValueError(f"embed must be one of {', '.join(EMBED_MODES)}, not {embed!r}")
    if embed == "full":
        return citation_records(w, list(cited) + list(others), evidence_ids)
    findings, evidence = citation_records(w, cited, evidence_ids)
    if not linked:
        evidence = {x: evidence[x] for x in dict.fromkeys(evidence_ids) if x in evidence}
    F = {f["id"]: f for f in w["findings"]}
    for x in others:
        if x in F and x not in findings:
            findings[x] = label_only(F[x])
    if embed == "summary":
        rx = quote_rx(w)
        findings = {k: summary_record(v, quotes=rx) for k, v in findings.items()}
        evidence = {k: summary_record(v, evidence=True, quotes=rx) for k, v in evidence.items()}
    return findings, evidence


def witness_note(evidence: dict) -> bool:
    """True when an embedded evidence item's type names a witness statement (case-insensitive)."""
    return any("witness" in _s(e.get("type")).lower() for e in evidence.values() if isinstance(e, dict))


def print_witness_note(evidence: dict, embed: str):
    """The stderr note for pages that carry witness statements' text (summary drops it, so no note)."""
    if embed != "summary" and witness_note(evidence):
        print(WITNESS_NOTE, file=sys.stderr)


def build_detail_data(w: dict, reg, embed: str = EMBED_DEFAULT) -> dict:
    """Everything the Detailed register tab shows: the register as given, plus the workspace records of every
    finding and evidence item it cites (each once, as --embed says) and the findings no learning covers."""
    entries = reg["entries"] if isinstance(reg, dict) else reg
    meta = {k: v for k, v in reg.items() if k != "entries"} if isinstance(reg, dict) else {}
    F = {f["id"]: f for f in w["findings"]}
    downs = downgraded_findings(w)

    derived, cited = {}, []
    for e in entries:
        hocs = [norm_hoc(r.get("hoc_tier")) for r in (e.get("recommendations") or [])]
        ranked = [t for t in HOC_TIERS if t in hocs]
        derived[_s(e.get("lr_id"))] = {"level": norm_level(e.get("hfacs_level")),
                                       "entity": norm_entity(e.get("owner_entity")),
                                       "hoc": hocs, "strongest": ranked[0] if ranked else "unclassified"}
        cited += [fid for fid in (e.get("finding_ids") or []) if fid in F and fid not in cited]
    uncovered = [{"id": fid, "label": f.get("label", ""), "rating": f.get("rating"), "level": f.get("level"),
                  "reason": "reviewer downgrade vote" if fid in downs else "not covered by any learning"}
                 for fid, f in F.items() if fid not in cited]

    findings, evidence = embedded_records(w, cited, [x for e in entries for x in (e.get("evidence_ids") or [])],
                                          [u["id"] for u in uncovered], embed)
    tax = w.get("clusters", {}).get("taxonomy", {})
    return {"register": meta, "entries": entries, "derived": derived, "findings": findings, "evidence": evidence,
            "taxonomy": {"entities": tax.get("entities", {}), "tiers": tax.get("tiers", {})},
            "brand": brand_payload(), "tier_labels": TIER_LABELS, "labels": dict(REG_COLS), "hoc_order": HOC_TIERS,
            "totals": {"findings": len(F), "evidence": len(w.get("evidence", {}))}, "uncovered": uncovered}


def embed_json(obj) -> str:
    """JSON safe to place inside <script type="application/json">: no '<', '>' or '&' characters."""
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return s.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
