"""The missed-opportunities command (P5-8, P5-9): the findings that cite an earlier recommendation, the
Failure-to-Correct (SVF) findings, the dated precursor candidates before the incident that cite them, and the findings
whose justification uses drift wording. One engine for two skills: precursor-timeline places the dated ones on its
timeline (knowable then), failure-to-learn-review analyses which learning-cycle step broke."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from .pack.items import trim_words
from .util import REFS, _abs, write_json
from .workspace import file_sha256, incident_date, load_ws, record_derived

ARTEFACT = "missed_opportunities.json"
LEXICON = REFS / "open-questions.json"          # Task 4 writes it; its `drift` list is read here (P5-9)
PRIOR_REC_RX = re.compile(r"\brecommend", re.I)
FAILURE_TO_CORRECT = "SVF"


def drift_terms() -> list:
    """The `drift` list of references/open-questions.json, or [] when the file (or the list) is not there."""
    try:
        data = json.loads(Path(LEXICON).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    terms = data.get("drift") if isinstance(data, dict) else None
    return [t for t in terms if isinstance(t, str) and t.strip()] if isinstance(terms, list) else []


def _missed_rx(terms):
    """Case-insensitive, whole words or phrases only: 'routine' does not match 'routinely'."""
    terms = sorted({t.strip() for t in terms if t and t.strip()}, key=lambda t: (-len(t), t.lower()))
    if not terms:
        return None
    return re.compile(r"(?<![\w-])(?:" + "|".join(re.escape(t) for t in terms) + r")(?![\w-])", re.I)


def _missed_date(c) -> str:
    d, prec = c["date"], c.get("precision", "day")
    return d if prec == "day" else d[:7] if prec == "month" else d[:4]


def missed(w, candidates=None, drift=None) -> dict:
    """The missed_opportunities.json document. `candidates` is the timeline_candidates.json list (None: not built
    yet); `drift` is the drift lexicon (None: read it from references/open-questions.json)."""
    findings = w.get("findings", [])
    notes = []
    prior = sorted(f["id"] for f in findings if PRIOR_REC_RX.search(str(f.get("justification") or "")))
    svf = sorted(f["id"] for f in findings if str(f.get("code") or "").split()[:1] == [FAILURE_TO_CORRECT])
    if not prior:
        notes.append("No finding's justification cites an earlier recommendation.")
    if not svf:
        notes.append("No Failure-to-Correct (SVF) findings in this export.")
    if drift is None:
        drift = drift_terms()
    rx = _missed_rx(drift)
    if rx is None:
        notes.append("No drift lexicon (references/open-questions.json `drift`): the drift list is empty.")
    drifted = sorted(f["id"] for f in findings if rx and rx.search(str(f.get("justification") or "")))
    watch = set(prior) | set(svf)
    dated = []
    inc = incident_date(w)
    if candidates is None:
        notes.append("No timeline_candidates.json: run `timeline <ws> --before incident` first; the dated list is "
                     "empty.")
    else:
        if not inc:
            notes.append("No incident date in this workspace: every dated candidate is kept.")
        for c in candidates:
            hits = sorted(watch & set(c.get("sources", [])))
            if hits and (not inc or c["date"] < inc):
                dated.append({"date": _missed_date(c), "snippet": c["snippet"], "findings": hits})
        dated.sort(key=lambda d: (d["date"], d["snippet"], d["findings"]))
        if not dated:
            notes.append("No dated candidate before the incident cites these findings.")
    return {"version": 1, "prior_recommendation": prior, "failure_to_correct": svf, "dated": dated,
            "drift": drifted, "notes": notes}


def missed_timeline_item(m) -> dict:
    """The dated missed opportunities as a ready timeline item: every event knowable then (P5-8)."""
    events = [{"date": d["date"], "text": trim_words(d["snippet"]), "cites": list(d["findings"]), "knowable_then": True}
              for d in m["dated"]]
    return {"kind": "timeline", "id": "missed-opportunities", "events": events,
            "cites": sorted({x for e in events for x in e["cites"]})}


def cmd_missed_opportunities(a):
    ws = _abs(a.ws)
    w = load_ws(ws)
    src = ws / "timeline_candidates.json"
    cands = json.loads(src.read_text(encoding="utf-8")) if src.is_file() else None
    m = missed(w, cands)
    write_json(ws / ARTEFACT, json.loads(json.dumps(m, sort_keys=True)))
    record_derived(ws, ARTEFACT, {n: file_sha256(ws / n) for n in ("findings.json", "incident.json",
                                                                     "timeline_candidates.json") if (ws / n).exists()})
    if a.timeline_item:
        it = missed_timeline_item(m)
        if not it["events"]:
            print("No dated missed opportunities before the incident: the timeline item is empty.", file=sys.stderr)
        print(json.dumps(it, indent=1, ensure_ascii=False))
        return
    if a.json:
        print(json.dumps(m, indent=1, ensure_ascii=False, sort_keys=True))
        return
    print(f"Missed opportunities written to {ws / ARTEFACT}.\n")
    print("| Set | Count |\n|---|---:|")
    print(f"| Cite an earlier recommendation | {len(m['prior_recommendation'])} |")
    print(f"| Failure to Correct (SVF) | {len(m['failure_to_correct'])} |")
    print(f"| Dated before the incident | {len(m['dated'])} |")
    print(f"| Drift wording | {len(m['drift'])} |")
    for n in m["notes"]:
        print(f"\nNote: {n}")
