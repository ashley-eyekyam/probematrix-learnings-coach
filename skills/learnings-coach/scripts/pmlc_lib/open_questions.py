"""The open-questions command: what the export leaves open, as a list a person can chase (Phase 5, Task 4).

Four sources, all deterministic: follow-up columns the export leaves empty on every finding, Incident Summary fields
left blank, findings whose justification says something is absent (the `absence` lexicon), and findings whose
justification is hedged (the `hedge` lexicon). Gaps that earlier packs recorded in outputs/gaps.json are merged in."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from .util import _s, REFS
from .workspace import file_sha256, is_standard_ws, load_ws, outputs_dir, record_derived
from .util import _abs

MAX_QUESTIONS = 30
FOLLOW_UP_LABELS = (("evidence_to_collect", "Evidence to Collect"), ("key_questions", "Key Questions"),
                    ("suggested_interviews", "Suggested Interviews"), ("causal_hypothesis", "Causal Hypothesis"))
_DEFAULT_SOURCE = "document"


def load_lexicons() -> dict:
    return json.loads((REFS / "open-questions.json").read_text(encoding="utf-8"))


def oq_pattern(words) -> "re.Pattern":
    """One case-insensitive pattern for a list of words and phrases, matched at word boundaries ('mayor' is not
    'may'); a space in a phrase matches any run of whitespace."""
    alts = sorted({re.escape(x.strip()).replace(r"\ ", r"\s+") for x in words if x.strip()}, key=lambda x: (-len(x), x))
    return re.compile(r"(?<![\w])(?:" + "|".join(alts) + r")(?![\w])", re.IGNORECASE)


def oq_matches(text, rx) -> bool:
    return bool(rx.search(text or ""))


def _read_gaps(run) -> list:
    if run is None:
        return []
    p = Path(run) / "outputs" / "gaps.json"
    try:
        d = json.loads(p.read_text(encoding="utf-8")).get("gaps", [])
    except (OSError, UnicodeDecodeError, ValueError, AttributeError):
        return []
    return [{"pack": _s(g.get("pack")), "text": _s(g.get("text")), "cites": list(g.get("cites") or []),
             "evidence_needed": _s(g.get("evidence_needed"))} for g in d if isinstance(g, dict)] if isinstance(d, list) else []


def collect(w, run=None) -> dict:
    """The open_questions.json document for a loaded workspace. run is the run folder (its outputs/gaps.json is
    merged in) or None."""
    lex = load_lexicons()
    ab, hg = oq_pattern(lex["absence"]), oq_pattern(lex["hedge"])
    F = w["findings"]
    inc = w.get("incident", {})
    notes = []
    empty = [lab for col, lab in FOLLOW_UP_LABELS if F and not any(f.get(col) for f in F)]
    if "summary_fields" in inc:
        blank, total = list(inc.get("blank_summary_fields", [])), len(inc["summary_fields"])
    else:
        blank, total = [], 0
        notes.append("This workspace was ingested before blank summary fields were recorded: re-run ingest to count them")
    if not F:
        notes.append("No findings: nothing to check for absence or hedging")
    return {"version": 1, "empty_follow_up_columns": empty, "blank_summary_fields": blank, "summary_fields": total,
            "absence": [f["id"] for f in F if oq_matches(f.get("justification"), ab)],
            "hedged": [f["id"] for f in F if oq_matches(f.get("justification"), hg)],
            "gaps": _read_gaps(run), "notes": notes}


def _source_for(text, lex) -> str:
    low = _s(text).lower()
    for src, words in lex["sources"].items():
        if oq_pattern(words).search(low):
            return src
    return _DEFAULT_SOURCE


def _label(f) -> str:
    return (_s(f.get("label")) or _s(f.get("short")) or _s(f.get("name"))).strip().rstrip(".")


def question_items(oq, w=None) -> list:
    """At most MAX_QUESTIONS question items: empty follow-up columns, then top-rated absence findings, then the
    other absence findings, then hedged ones. w (the loaded workspace) supplies the finding text."""
    lex = load_lexicons()
    by_id = {f["id"]: f for f in (w or {}).get("findings", [])}
    col_src = lex["columns"]
    items = []
    for lab in oq["empty_follow_up_columns"]:
        key = next(k for k, v in FOLLOW_UP_LABELS if v == lab)
        items.append({"kind": "question", "question": f"What should be recorded under '{lab}' for the findings?",
                      "why": f"The export leaves '{lab}' empty on every finding.",
                      "good_evidence": col_src.get(key, _DEFAULT_SOURCE)})
    ratings = [f.get("rating") or 0 for f in by_id.values()]
    top = max(ratings) if ratings else 0

    def order(ids):
        return sorted(ids, key=lambda i: (-(by_id.get(i, {}).get("rating") or 0), i))
    ab = [i for i in oq["absence"] if i in by_id]
    ab_top = order([i for i in ab if (by_id[i].get("rating") or 0) >= top and top])
    ab_rest = order([i for i in ab if i not in ab_top])
    hg = order([i for i in oq["hedged"] if i in by_id and i not in ab])
    for ids, why in ((ab_top + ab_rest, "The justification says a record or fact is absent"),
                     (hg, "The justification is hedged")):
        for fid in ids:
            f = by_id[fid]
            what = _label(f) or f.get("name", "")
            q = (f"What record or evidence would settle this: {what}?" if why.endswith("absent")
                 else f"What evidence would firm up this finding: {what}?")
            items.append({"kind": "question", "question": q, "why": f"{why} ({fid}).",
                          "good_evidence": _source_for(" ".join((_s(f.get("justification")), _s(f.get("short")))), lex),
                          "cites": [fid]})
    return items[:MAX_QUESTIONS]


def cmd_open_questions(a):
    ws = _abs(a.ws)
    w = load_ws(ws)
    run = ws.parent if is_standard_ws(ws) else outputs_dir(ws).parent
    oq = collect(w, run)
    (ws / "open_questions.json").write_text(json.dumps(oq, indent=1, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    record_derived(ws, "open_questions.json",
                   {n: file_sha256(ws / n) for n in ("findings.json", "incident.json") if (ws / n).is_file()})
    if getattr(a, "items", False):
        print(json.dumps(question_items(oq, w), indent=1, ensure_ascii=False))
        return
    if getattr(a, "as_json", False):
        print(json.dumps(oq, indent=1, ensure_ascii=False, sort_keys=True))
        return
    n = len(w["findings"])
    print(f"open_questions.json written to {ws / 'open_questions.json'}")
    print(f"- empty follow-up columns: {len(oq['empty_follow_up_columns'])}"
          + (f" ({', '.join(oq['empty_follow_up_columns'])})" if oq["empty_follow_up_columns"] else ""))
    print(f"- blank Incident Summary fields: {len(oq['blank_summary_fields'])} of {oq['summary_fields']}")
    print(f"- findings whose justification says something is absent: {len(oq['absence'])} of {n}")
    print(f"- findings whose justification is hedged: {len(oq['hedged'])} of {n}")
    print(f"- gaps recorded by packs: {len(oq['gaps'])}")
    for x in oq["notes"]:
        print(f"note: {x}", file=sys.stderr)
