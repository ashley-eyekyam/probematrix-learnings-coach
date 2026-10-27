"""Learning packs: the schema check and the check-pack command. Reference: references/pack-schema.md."""
from __future__ import annotations

import collections
import copy
import datetime as dt
import json
import re
import sys
from pathlib import Path

from ..classify import TIER_LABELS
from ..handling import check_handling, unsigned_warning
from ..register.check import HOC_TIERS, norm_hoc
from ..select import _filter, select_args
from ..util import REFS
from ..workspace import downgraded_findings, linked_evidence, load_ws, outputs_dir, record_pack_check
from .. import lint
from . import profiles
from .profiles import top_rated_of


SCHEMA_VERSION = 1
PACK_NAME_RX = re.compile(r"^(?:[a-z0-9]+(?:-[a-z0-9]+)*|dossier-F\d+[a-z]?)$")
SLUG_RX = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ID_RX = re.compile(r"\b(FND-[0-9A-Za-z]{4,}|EVD-\d{3,})\b")
DATE_RX = re.compile(r"^\d{4}(?:-\d{2}(?:-\d{2})?)?$")
MAX_BOTTOM_LINE = 7
UNCOVERED_PRINT_LINE = "{x} of {y} relevant findings cited"
TOP_PRINT_LINE = "{x} of {y} top-rated relevant findings cited"
COVERAGE_WARNING = "under a quarter of the top-rated relevant findings are cited ({x} of {y})"

# Item kinds: required fields, optional fields, and whether at least one citation is required.
KINDS = {
    "para": {"req": ["text"], "opt": []},
    "check": {"req": ["text"], "opt": ["hold_point", "when"]},
    "question": {"req": ["question", "why"], "opt": ["answer", "good_evidence", "to", "type", "options"]},
    "recommendation": {"req": ["change", "indicator", "hoc_tier"],
                       "opt": ["barrier", "owner", "by_when", "co_owner", "why_not_stronger", "barrier_id"], "cite": True},
    "decision": {"req": ["decision"], "opt": ["options", "trade_offs", "owner", "by_when"]},
    "indicator": {"req": ["name", "measure"], "opt": ["deterioration", "owner"]},
    "card": {"req": ["title", "what_happened", "warning_signs", "good_looks_like"],
             "opt": ["why_made_sense", "organisation_changing", "discussion"], "cite": True},
    "scenario": {"req": ["situation", "prompts"], "opt": []},
    "table": {"req": ["columns", "rows"], "opt": ["row_cites", "row_supporting_cites", "finding_notes"]},
    "test_point": {"req": ["requirement", "sample", "conformity_evidence"], "opt": ["red_flags", "clause"], "cite": True},
    "module": {"req": ["title", "objective", "content"], "opt": ["audience", "duration", "assessment"]},
    "barrier": {"req": ["barrier", "failure_mode", "hoc_tier"], "opt": ["type", "fix", "owner", "state", "indicator",
                                                                      "barrier_id"],
                "cite": True},
    "timeline": {"req": ["events"], "opt": []},
    "graph": {"req": ["nodes", "edges"], "opt": []},
    "learning": {"req": ["lesson"], "opt": ["explanation", "owner"], "cite": True},
}
# Field roles (Ruling P4-5): each kind's fields in the HTML page's order, with the role a renderer gives them
# (title|body|list|badge|indicator|table|events|graph|segments|choices|injects). Labels are the f.<field> keys of
# references/labels/<locale>.json. Cite fields are not listed: every renderer shows them its own way.
FIELD_ROLES = {
    "para": [["text", "body"]],
    "check": [["hold_point", "badge"], ["text", "body"], ["when", "badge"]],
    "question": [["question", "title"], ["to", "badge"], ["type", "badge"], ["options", "choices"], ["why", "body"],
                 ["answer", "body"], ["good_evidence", "body"]],
    "recommendation": [["change", "title"], ["hoc_tier", "badge"], ["barrier", "badge"], ["barrier_id", "badge"],
                       ["owner", "badge"], ["co_owner", "badge"], ["by_when", "badge"], ["indicator", "indicator"],
                       ["why_not_stronger", "body"]],
    "decision": [["decision", "title"], ["options", "list"], ["trade_offs", "body"], ["owner", "badge"],
                 ["by_when", "badge"]],
    "indicator": [["name", "title"], ["measure", "body"], ["deterioration", "body"], ["owner", "body"]],
    "card": [["title", "title"], ["what_happened", "body"], ["why_made_sense", "body"], ["organisation_changing", "body"],
             ["warning_signs", "list"], ["good_looks_like", "body"], ["discussion", "list"]],
    "scenario": [["situation", "body"], ["prompts", "list"]],
    "table": [["columns", "table"], ["rows", "table"], ["finding_notes", "list"]],
    "test_point": [["requirement", "title"], ["clause", "badge"], ["sample", "body"], ["conformity_evidence", "body"],
                   ["red_flags", "list"]],
    "module": [["title", "title"], ["audience", "badge"], ["duration", "badge"], ["objective", "body"],
               ["content", "list"], ["assessment", "list"]],
    "barrier": [["barrier", "title"], ["hoc_tier", "badge"], ["barrier_id", "badge"], ["type", "badge"],
                ["state", "badge"], ["owner", "badge"], ["failure_mode", "body"], ["fix", "body"],
                ["indicator", "indicator"]],
    "timeline": [["events", "events"]],
    "graph": [["nodes", "graph"], ["edges", "graph"]],
    "learning": [["lesson", "title"], ["owner", "badge"], ["explanation", "body"]],
}


def _ps_attach_fields() -> None:
    """KINDS[kind]["fields"] = FIELD_ROLES[kind] (a kind added later brings its own "fields")."""
    for kind, roles in FIELD_ROLES.items():
        KINDS[kind].setdefault("fields", roles)


_ps_attach_fields()
STR_LIST_FIELDS = {"options", "warning_signs", "discussion", "prompts", "columns", "content", "assessment", "red_flags"}
OBJ_LIST_FIELDS = {"rows", "row_cites", "row_supporting_cites", "events", "nodes", "edges"}
MAP_FIELDS = {"finding_notes"}
BOOL_FIELDS = {"hold_point"}
FOLLOW_UP_COLUMNS = ["Finding", "Evidence to collect", "Key questions", "Suggested interviews", "Causal hypothesis"]
FOLLOW_UP_KEYS = ["evidence_to_collect", "key_questions", "suggested_interviews", "causal_hypothesis"]

Result = collections.namedtuple("Result", "problems warnings stats")


def _text(v) -> bool:
    return isinstance(v, str) and v.strip() != ""


def _id_list(v) -> bool:
    return isinstance(v, list) and all(isinstance(x, str) and ID_RX.fullmatch(x) for x in v)


def _iso_partial(v) -> bool:
    """YYYY-MM-DD, YYYY-MM or YYYY, and a real calendar date."""
    if not isinstance(v, str) or not DATE_RX.match(v):
        return False
    full = v + "-01-01"[len(v) - 4:] if len(v) < 10 else v      # 2022 -> 2022-01-01, 2022-03 -> 2022-03-01
    try:
        dt.date.fromisoformat(full)
    except ValueError:
        return False
    return True


def _walk_ids(v, path):
    """Yield (json-path, ID) for every Finding or Evidence ID in any string under v."""
    if isinstance(v, str):
        for m in ID_RX.finditer(v):
            yield path, m.group(1)
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from _walk_ids(x, f"{path}[{i}]")
    elif isinstance(v, dict):
        for k, x in v.items():
            yield from _walk_ids(x, f"{path}.{k}" if path else str(k))


# Fields rendered with citation buttons. An ID anywhere else (headings, titles, badges, column headers, graph
# labels) is shown as plain text, so it is not a citation and does not count towards coverage.
INLINE_FIELDS = {
    "para": ["text"], "check": ["text"], "question": ["question", "why", "answer", "good_evidence"],
    "recommendation": ["change", "indicator"], "decision": ["decision", "options", "trade_offs"],
    "indicator": ["name", "measure", "deterioration", "owner"],
    "card": ["what_happened", "why_made_sense", "organisation_changing", "warning_signs", "good_looks_like", "discussion"],
    "scenario": ["situation", "prompts"], "table": ["rows"],
    "test_point": ["requirement", "sample", "conformity_evidence", "red_flags"],
    "module": ["objective", "content", "assessment"], "barrier": ["barrier", "failure_mode", "fix", "indicator"],
    "timeline": [], "graph": [], "learning": ["lesson", "explanation"],
}
CITE_FIELDS = ["cites", "row_cites", "row_supporting_cites", "supporting_cites"]
STRENGTHS = ("direct", "corroborated", "inferred")
BARRIER_STATES = ("absent", "degraded", "defeated", "worked partly", "worked")
TIME_RX = re.compile(r"(?:[01]\d|2[0-3]):[0-5]\d")          # used with fullmatch: "14:05", never "14:05\n"
GENERIC_FIELDS = ("kind", "id", "cites", "supporting_cites", "evidence_strength", "group", "lint_ok", "learning", "clauses",
                  "comparator_refs", "source_text", "back_translation")


# Phase 4, Task 16 (L2-18, L4-19, L4-30, R3): the toolbox and script kinds, scenario injects and the card fields.
# Appended, so the KINDS literal above stays as it was.
SCRIPT_CHANNELS = ("video", "radio", "pa", "screen")
OFFSET_RX = re.compile(r"\+\d{1,3}:[0-5]\d")                # used with fullmatch: "+00:15" after the start
TOOLBOX_SIGNS = 2                                           # output-style.md: two warning signs


def _ps_p4_media_kinds() -> None:
    KINDS["toolbox"] = {"req": ["opening_question", "story", "warning_signs", "one_change", "crew_question"],
                        "opt": ["duration"], "cite": True,
                        "fields": [["duration", "badge"], ["opening_question", "title"], ["story", "body"],
                                   ["warning_signs", "list"], ["one_change", "body"], ["crew_question", "body"]]}
    KINDS["script"] = {"req": ["title", "segments"], "opt": ["purpose", "channel"], "cite": True,
                       "fields": [["title", "title"], ["channel", "badge"], ["purpose", "body"],
                                  ["segments", "segments"]]}
    KINDS["scenario"]["opt"].append("injects")
    KINDS["scenario"]["fields"].append(["injects", "injects"])
    KINDS["card"]["opt"] += ["did_you_know", "what_you_can_do"]
    roles = KINDS["card"]["fields"]
    at = next((i for i, (f, _) in enumerate(roles) if f == "discussion"), len(roles))
    roles[at:at] = [["did_you_know", "list"], ["what_you_can_do", "list"]]
    STR_LIST_FIELDS.update(("did_you_know", "what_you_can_do"))
    OBJ_LIST_FIELDS.update(("segments", "injects"))
    INLINE_FIELDS["toolbox"] = ["opening_question", "story", "warning_signs", "one_change", "crew_question"]
    INLINE_FIELDS["script"] = ["purpose", "segments"]
    INLINE_FIELDS["scenario"] = INLINE_FIELDS["scenario"] + ["injects"]
    INLINE_FIELDS["card"] = INLINE_FIELDS["card"] + ["did_you_know", "what_you_can_do"]


_ps_p4_media_kinds()


# Phase 5, Task 8: the risk_change kind. The risk owner decides, so the kind has no owner, date or rating field.
RISK_CHANGE_TYPES = ("missing-threat", "control-rating", "accepted-without-authority", "kri", "other")


def _ps_p5_risk_change() -> None:
    KINDS["risk_change"] = {"req": ["risk", "change_type", "current_assumption", "evidence_says", "proposed_change"],
                            "opt": [], "cite": True,
                            "fields": [["risk", "title"], ["change_type", "badge"], ["current_assumption", "body"],
                                       ["evidence_says", "body"], ["proposed_change", "body"]]}
    INLINE_FIELDS["risk_change"] = ["current_assumption", "evidence_says", "proposed_change"]


_ps_p5_risk_change()


# Phase 6, Task 3 (P6-5): the self_check kind of could-it-happen-here. `templates <ws> cihh` writes one return-template
# row per self_check item; the site's answer, response and assessor are never in the pack (D7).
def _ps_p6_self_check() -> None:
    KINDS["self_check"] = {"req": ["condition", "evidence_to_check"], "opt": ["lr_id", "look_in"], "cite": True,
                           "fields": [["condition", "title"], ["lr_id", "badge"], ["evidence_to_check", "body"],
                                      ["look_in", "body"]]}
    INLINE_FIELDS["self_check"] = ["evidence_to_check", "look_in"]


_ps_p6_self_check()


def _check_self_check(it, ip, bad):
    """self_check: lr_id, when given, is a register id (LR- and two or more digits)."""
    if "lr_id" in it and not (isinstance(it["lr_id"], str) and LR_RX.fullmatch(it["lr_id"])):
        bad(f"{ip}.lr_id", "must be LR- followed by two or more digits, e.g. LR-01")


def _check_risk_change(it, ip, bad):
    """risk_change: change_type is one of RISK_CHANGE_TYPES."""
    if "change_type" in it and it["change_type"] not in RISK_CHANGE_TYPES:
        bad(f"{ip}.change_type", f"must be one of {', '.join(RISK_CHANGE_TYPES)}")


def _check_script(it, ip, bad):
    """script (L4-19): channel is one of SCRIPT_CHANNELS; each segment {visual*, narration*, seconds* (1-600),
    on_screen, cites}."""
    if "channel" in it and it["channel"] not in SCRIPT_CHANNELS:
        bad(f"{ip}.channel", f"must be one of {', '.join(SCRIPT_CHANNELS)}")
    segs = it.get("segments")
    for k, sg in enumerate(segs if isinstance(segs, list) else []):
        sp = f"{ip}.segments[{k}]"
        if not isinstance(sg, dict):
            bad(sp, "must be an object with visual, narration and seconds")
            continue
        for f in ("visual", "narration"):
            if not _text(sg.get(f)):
                bad(f"{sp}.{f}", "required")
        s = sg.get("seconds")
        if isinstance(s, bool) or not isinstance(s, int) or not 1 <= s <= 600:
            bad(f"{sp}.seconds", "must be a whole number from 1 to 600")
        if "on_screen" in sg and not _text(sg["on_screen"]):
            bad(f"{sp}.on_screen", "must be non-empty text")
        if "cites" in sg and not _id_list(sg["cites"]):
            bad(f"{sp}.cites", "must be a list of Finding or Evidence IDs")


def _check_injects(it, ip, bad):
    """scenario injects (L4-30): each {offset* (+HH:MM after the exercise starts), text*, decision}."""
    injects = it.get("injects")
    for k, x in enumerate(injects if isinstance(injects, list) else []):
        xp = f"{ip}.injects[{k}]"
        if not isinstance(x, dict):
            bad(xp, "must be an object with offset and text")
            continue
        if not (isinstance(x.get("offset"), str) and OFFSET_RX.fullmatch(x["offset"])):
            bad(f"{xp}.offset", "must be +HH:MM after the start of the exercise, e.g. +00:15")
        if not _text(x.get("text")):
            bad(f"{xp}.text", "required")
        if "decision" in x and not _text(x["decision"]):
            bad(f"{xp}.decision", "must be non-empty text")


def inline_fields(kind) -> list:
    """The fields of a kind that render citation buttons: INLINE_FIELDS, else (a kind it does not list) the kind's
    fields with role body or list (Ruling P4-5)."""
    if not isinstance(kind, str):
        return []
    if kind in INLINE_FIELDS:
        return INLINE_FIELDS[kind]
    return [f for f, role in (KINDS.get(kind) or {}).get("fields", []) if role in ("body", "list")]


def _pick(d, keys) -> dict:
    return {k: d[k] for k in keys if k in d} if isinstance(d, dict) else {}


def _citable_item(it) -> dict:
    """The parts of one item that render as citation buttons (same keys, so JSON paths are unchanged)."""
    if not isinstance(it, dict):
        return {}
    kind = it.get("kind")
    out = _pick(it, inline_fields(kind) + CITE_FIELDS)
    if kind == "timeline" and isinstance(it.get("events"), list):
        out["events"] = [_pick(e, ["text", "cites"]) for e in it["events"]]
    return out


def _citable(pack) -> dict:
    bl, secs, dq = pack.get("bottom_line"), pack.get("sections"), pack.get("data_quality")
    return {"data_quality": [_pick(n, ["text", "cites"]) for n in dq] if isinstance(dq, list) else [],
            "bottom_line": [_pick(e, ["text", "cites", "supporting_cites"]) for e in bl] if isinstance(bl, list) else [],
            "sections": [dict(_pick(s, ["intro"]),
                              items=[_citable_item(it) for it in s["items"]] if isinstance(s.get("items"), list) else [])
                         if isinstance(s, dict) else {} for s in secs] if isinstance(secs, list) else []}


def cited_ids(pack) -> tuple:
    """Ordered unique (finding IDs, evidence IDs) cited in the bottom line or sections: in cites lists, or inline in
    text that renders citation buttons."""
    fids, eids = [], []
    for _, x in _walk_ids(_citable(pack), ""):
        bucket = fids if x.startswith("FND-") else eids
        if x not in bucket:
            bucket.append(x)
    return fids, eids


def gap_ids(pack) -> tuple:
    """(finding IDs, evidence IDs) cited by the top-level gaps. They are not citations for coverage, but the page
    embeds their records so their buttons open."""
    fids, eids = [], []
    gaps = pack.get("gaps") if isinstance(pack.get("gaps"), list) else []
    for g in gaps:
        cites = g.get("cites") if isinstance(g, dict) else None
        for x in cites if isinstance(cites, list) else []:
            if not isinstance(x, str):
                continue
            bucket = fids if x.startswith("FND-") else eids
            if x not in bucket:
                bucket.append(x)
    return fids, eids


def embedded_ids(pack) -> tuple:
    """cited_ids plus gap_ids: every ID the page renders as a citation button."""
    (f1, e1), (f2, e2) = cited_ids(pack), gap_ids(pack)
    return list(dict.fromkeys(f1 + f2)), list(dict.fromkeys(e1 + e2))


def with_item_ids(pack) -> dict:
    """Deep copy in which every item has an id: its own, or <section-id>-<position>."""
    p = copy.deepcopy(pack)
    for s in p["sections"]:
        for n, it in enumerate(s["items"], 1):
            it.setdefault("id", f"{s['id']}-{n}")
    return p


def relevant_findings(w, scope=None) -> list:
    """Finding IDs a pack is expected to draw on: those matching its scope (the same filter as select), or,
    without a scope, the top-rated findings (rating equal to the workspace maximum, as classify counts them)."""
    if scope:
        a = select_args(entity=scope.get("entities") or None, tag=scope.get("tags") or None,
                             tier=scope.get("tiers") or None, relation=scope.get("relations") or None,
                             level=scope.get("levels") or None, entity_mode=scope.get("entity_mode") or "any",
                             top_rated=scope.get("min_rating") == "top",
                             min_rating=None if scope.get("min_rating") == "top" else scope.get("min_rating"))
        rel = {f["id"] for f, _ in _filter(w, a)}
        return [f["id"] for f in w["findings"] if f["id"] in rel]
    top = max(((f.get("rating") or 0) for f in w["findings"]), default=0)
    return [f["id"] for f in w["findings"] if top and (f.get("rating") or 0) == top]


def _check_field(v, f, path, bad):
    if f in BOOL_FIELDS:
        if not isinstance(v, bool):
            bad(path, "must be true or false")
    elif f in STR_LIST_FIELDS:
        if not isinstance(v, list) or not v or not all(_text(x) for x in v):
            bad(path, "must be a non-empty list of text")
    elif f in OBJ_LIST_FIELDS:
        if not isinstance(v, list) or not v:
            bad(path, "must be a non-empty list")
    elif f in MAP_FIELDS:
        return                                   # shape checked by the kind's own check (_check_table)
    elif not _text(v):
        bad(path, "must be non-empty text")


QUESTION_TYPES = ("single", "multi", "truefalse", "short")
QUIZ_CSV_OPTIONS = 6


def _check_question(it, ip, bad, warn):
    """P4-10: a question's type (single|multi|truefalse|short) and its options, a list of {text, correct}."""
    typ, ops = it.get("type"), it.get("options")
    if "type" in it and typ not in QUESTION_TYPES:
        bad(f"{ip}.type", f"must be one of {', '.join(QUESTION_TYPES)}")
        typ = None
    if "options" in it:
        if not isinstance(ops, list) or not ops or any(
                not isinstance(o, dict) or not _text(o.get("text")) or not isinstance(o.get("correct"), bool)
                for o in ops):
            bad(f"{ip}.options", "must be a non-empty list of {text, correct} objects (text non-empty, correct true or false)")
            return
        if "type" not in it:
            warn(f"{ip}.options", "options without type are ignored")
            return
    if typ is None:
        return
    if "options" not in it:
        bad(f"{ip}.options", f"a {typ} question needs options")
        return
    n = sum(1 for o in ops if o["correct"])
    if typ in ("single", "truefalse") and n != 1:
        bad(f"{ip}.options", f"a {typ} question needs exactly one correct option (found {n})")
    elif typ == "multi" and n < 1:
        bad(f"{ip}.options", "a multi question needs at least one correct option")
    elif typ == "short" and n != len(ops):
        bad(f"{ip}.options", "a short question lists accepted answers: mark every option correct")
    if typ == "truefalse" and len(ops) != 2:
        bad(f"{ip}.options", f"a truefalse question needs exactly 2 options (found {len(ops)})")
    if len(ops) > QUIZ_CSV_OPTIONS:
        warn(f"{ip}.options", f"the quiz CSV holds {QUIZ_CSV_OPTIONS} options; the rest are left out of it")


def _check_table(it, ip, bad):
    cols, rows = it.get("columns"), it.get("rows")
    if not isinstance(cols, list) or not isinstance(rows, list):
        return
    for r, row in enumerate(rows):
        if not isinstance(row, list) or len(row) != len(cols):
            bad(f"{ip}.rows[{r}]", f"must have {len(cols)} cells like columns")
            continue
        for c, cell in enumerate(row):
            if isinstance(cell, bool) or not isinstance(cell, (str, int, float)):
                bad(f"{ip}.rows[{r}][{c}]", "must be text or a number")
    for f in ("row_cites", "row_supporting_cites"):
        rc = it.get(f)
        if rc is None:
            continue
        if not isinstance(rc, list) or len(rc) != len(rows):
            bad(f"{ip}.{f}", "must hold one list of IDs per row")
            continue
        for r, c in enumerate(rc):
            if not _id_list(c):
                bad(f"{ip}.{f}[{r}]", "must be a list of Finding or Evidence IDs")
    _check_finding_notes(it, rows, ip, bad)


def _check_finding_notes(it, rows, ip, bad):
    """investigator-coach: an optional note per finding on the follow-up table, for findings that share a row."""
    notes = it.get("finding_notes")
    if notes is None:
        return
    if it.get("id") != "follow-up":
        bad(f"{ip}.finding_notes", "only on the investigator-coach follow-up table")
        return
    if not isinstance(notes, dict) or not notes:
        bad(f"{ip}.finding_notes", "must be an object of Finding ID to note")
        return
    firsts = {x for row in rows if isinstance(row, list) and row and isinstance(row[0], str)
              for x in re.split(r"[\s,;]+", row[0]) if x}
    for x, v in notes.items():
        if x not in firsts:
            bad(f"{ip}.finding_notes.{x}", "not a Finding ID in this table's first column")
        elif not _text(v):
            bad(f"{ip}.finding_notes.{x}", "must be non-empty text")


def _check_timeline(it, ip, bad):
    events = it.get("events")
    if not isinstance(events, list):
        return
    for k, ev in enumerate(events):
        ep = f"{ip}.events[{k}]"
        if not isinstance(ev, dict):
            bad(ep, "must be an object")
            continue
        if not _iso_partial(ev.get("date")):
            bad(f"{ep}.date", "must be YYYY-MM-DD, YYYY-MM or YYYY")
        if not _text(ev.get("text")):
            bad(f"{ep}.text", "required")
        if "signal" in ev and not isinstance(ev["signal"], bool):
            bad(f"{ep}.signal", "must be true or false")
        if "time" in ev and not (isinstance(ev["time"], str) and TIME_RX.fullmatch(ev["time"])):
            bad(f"{ep}.time", "must be HH:MM (24-hour)")
        if "knowable_then" in ev and not (isinstance(ev["knowable_then"], bool) or _text(ev["knowable_then"])):
            bad(f"{ep}.knowable_then", "must be true, false or text")
        for f in ("received_by", "response"):
            if f in ev and not _text(ev[f]):
                bad(f"{ep}.{f}", "must be non-empty text")
        if "cites" in ev and not _id_list(ev["cites"]):
            bad(f"{ep}.cites", "must be a list of Finding or Evidence IDs")


def _check_barrier(it, ip, bad):
    if "state" in it and it["state"] not in BARRIER_STATES:
        bad(f"{ip}.state", f"must be one of {', '.join(BARRIER_STATES)}")


def _check_graph(it, ip, bad):
    nodes, edges = it.get("nodes"), it.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        return
    ids = set()
    for k, n in enumerate(nodes):
        np_ = f"{ip}.nodes[{k}]"
        if not isinstance(n, dict) or not _text(n.get("id")) or not _text(n.get("label")):
            bad(np_, "needs id and label")
            continue
        if n["id"] in ids:
            bad(f"{np_}.id", f"duplicate node id {n['id']!r}")
        ids.add(n["id"])
    for k, e in enumerate(edges):
        ep = f"{ip}.edges[{k}]"
        if not isinstance(e, dict):
            bad(ep, "must be an object")
            continue
        for end in ("from", "to"):
            if not isinstance(e.get(end), str) or e.get(end) not in ids:
                bad(f"{ep}.{end}", f"{e.get(end)!r} is not a node id")
        if "label" in e and not _text(e["label"]):
            bad(f"{ep}.label", "must be text")


def _check_extras(d, p, bad):
    """Optional on every item and bottom-line entry: supporting_cites, evidence_strength and (items) group."""
    if "supporting_cites" in d and not _id_list(d["supporting_cites"]):
        bad(f"{p}.supporting_cites", "must be a list of Finding or Evidence IDs")
    if "evidence_strength" in d and d["evidence_strength"] not in STRENGTHS:
        bad(f"{p}.evidence_strength", f"must be one of {', '.join(STRENGTHS)}")
    if "group" in d and not _text(d["group"]):
        bad(f"{p}.group", "must be non-empty text")


def _check_item(it, ip, bad, warn):
    if not isinstance(it, dict):
        bad(ip, "must be an object")
        return
    kind = it.get("kind")
    spec = KINDS.get(kind) if isinstance(kind, str) else None
    if spec is None:
        bad(f"{ip}.kind", f"unknown kind {kind!r}; one of: {', '.join(KINDS)}")
        return
    known = spec["req"] + spec["opt"]
    for f in spec["req"]:
        if f not in it:
            bad(f"{ip}.{f}", f"required for {kind}")
    for f in known:
        if f in it and not (kind == "question" and f == "options"):        # a question's options are objects (P4-10)
            _check_field(it[f], f, f"{ip}.{f}", bad)
    if "cites" in it and not _id_list(it["cites"]):
        bad(f"{ip}.cites", "must be a list of Finding or Evidence IDs")
    if spec.get("cite") and not (_id_list(it.get("cites")) and it.get("cites")):
        bad(f"{ip}.cites", f"a {kind} needs at least one Finding or Evidence ID")
    _check_extras(it, ip, bad)
    for f in it:
        if f not in known and f not in GENERIC_FIELDS:
            warn(f"{ip}.{f}", f"unknown field for {kind} (ignored)")
    if _text(it.get("hoc_tier")) and norm_hoc(it["hoc_tier"]) == "unclassified":
        bad(f"{ip}.hoc_tier", f"must name a hierarchy-of-controls tier: {', '.join(HOC_TIERS)}")
    {"table": _check_table, "timeline": _check_timeline, "graph": _check_graph,
     "barrier": _check_barrier}.get(kind, lambda *x: None)(it, ip, bad)
    if kind == "question":
        _check_question(it, ip, bad, warn)
    {"script": _check_script, "scenario": _check_injects,
     "risk_change": _check_risk_change, "self_check": _check_self_check}.get(kind, lambda *x: None)(it, ip, bad)
    if not spec.get("cite") and not any(True for _ in _walk_ids(_citable_item(it), "")):
        warn(ip, "no Finding or Evidence ID cited")


def _check_scope(scope, w, bad):
    if scope is None:
        return
    if not isinstance(scope, dict):
        bad("scope", "must be an object")
        return
    for k in scope:
        if k not in ("tiers", "levels", "entities", "tags", "min_rating", "relations", "entity_mode"):
            bad(f"scope.{k}", "unknown key; use tiers, levels, entities, tags, min_rating, relations, entity_mode")
    t, lv, en, mr = scope.get("tiers") or [], scope.get("levels") or [], scope.get("entities") or [], scope.get("min_rating")
    tg = scope.get("tags") or []
    if not isinstance(t, list) or any(not isinstance(x, str) or x not in TIER_LABELS for x in t):
        bad("scope.tiers", "a list of T1 to T5")
    if not isinstance(lv, list) or any(isinstance(x, bool) or x not in (1, 2, 3, 4) for x in lv):
        bad("scope.levels", "a list of 1 to 4")
    if not isinstance(en, list) or any(not isinstance(x, str) for x in en):
        bad("scope.entities", "a list of entity IDs like F02")
    if not isinstance(tg, list) or any(not isinstance(x, str) for x in tg):
        bad("scope.tags", "a list of tags like emergency")
        tg = []
    if mr is not None and mr != "top" and (isinstance(mr, bool) or not isinstance(mr, int)):
        bad("scope.min_rating", 'a whole number, "top" or null')
    rl = scope.get("relations") or []
    if not isinstance(rl, list) or any(not isinstance(x, str) for x in rl):
        bad("scope.relations", "a list of relation IDs like owner")
        rl = []
    elif "clusters" in w:
        known_rel = w["clusters"].get("taxonomy", {}).get("relations", {})
        for x in rl:
            if x not in known_rel:
                bad("scope.relations", f"{x} is not a relation in clusters.json ({', '.join(sorted(known_rel))})")
    if scope.get("entity_mode") not in (None, "any", "all"):
        bad("scope.entity_mode", 'must be "any" or "all"')
    if "clusters" in w and isinstance(en, list):
        known = w["clusters"].get("taxonomy", {}).get("entities", {})
        for x in en:
            if isinstance(x, str) and x not in known:
                bad("scope.entities", f"{x} is not an entity in clusters.json")
    if "clusters" in w and tg:
        tagmap = w["clusters"].get("taxonomy", {}).get("tags")
        if tagmap is None:
            bad("scope.tags", "clusters.json has no tags (it predates v2.0). Re-run classify")
        else:
            known = {x for ts in tagmap.values() for x in ts}
            for x in tg:
                if x not in known:
                    bad("scope.tags", f"{x} is not a tag in clusters.json")
    if (t or en or tg or rl) and "clusters" not in w:
        bad("scope", "tiers, entities and tags need clusters.json. Run: pmlc.py classify <ws>")


def _check_notes(pack, w, bad):
    dq = pack.get("data_quality")
    if dq is not None:
        if not isinstance(dq, list) or not dq:
            bad("data_quality", "must be a non-empty list of {text, cites}")
        else:
            for i, n in enumerate(dq):
                if not isinstance(n, dict) or not _text(n.get("text")):
                    bad(f"data_quality[{i}].text", "required")
                elif "cites" in n and not _id_list(n["cites"]):
                    bad(f"data_quality[{i}].cites", "must be a list of Finding or Evidence IDs")
    ex = pack.get("exclusions")
    if ex is None:
        return
    if not isinstance(ex, list) or not ex:
        bad("exclusions", "must be a non-empty list of {id, reason}")
        return
    F = {f["id"] for f in w["findings"]}
    seen = set()
    for i, e in enumerate(ex):
        if not isinstance(e, dict):
            bad(f"exclusions[{i}]", "must be an object with id and reason")
            continue
        x = e.get("id")
        if not (isinstance(x, str) and ID_RX.fullmatch(x) and x.startswith("FND-")):
            bad(f"exclusions[{i}].id", "must be a Finding ID")
        elif x not in F:
            bad(f"exclusions[{i}].id", f"{x} is not in this workspace")
        elif x in seen:
            bad(f"exclusions[{i}].id", f"{x} is listed twice")
        else:
            seen.add(x)
        if not _text(e.get("reason")):
            bad(f"exclusions[{i}].reason", "required")


def excluded_ids(pack) -> list:
    ex = pack.get("exclusions")
    return [e["id"] for e in ex if isinstance(e, dict) and isinstance(e.get("id"), str)] if isinstance(ex, list) else []


def _check_follow_up(secs, bad):
    tables = [it for s in secs if isinstance(s, dict) and isinstance(s.get("items"), list)
              for it in s["items"] if isinstance(it, dict) and it.get("id") == "follow-up"]
    if not tables or tables[0].get("kind") != "table" or tables[0].get("columns") != FOLLOW_UP_COLUMNS:
        bad("investigator-coach", f"needs a table item with id follow-up and columns {FOLLOW_UP_COLUMNS}")
        return
    seen = set()
    for r, row in enumerate(tables[0].get("rows") if isinstance(tables[0].get("rows"), list) else []):
        if not isinstance(row, list) or not row:
            continue
        cell = [x for x in re.split(r"[\s,;]+", row[0]) if x] if isinstance(row[0], str) else []
        if not cell or not all(ID_RX.fullmatch(x) and x.startswith("FND-") for x in cell):
            bad(f"follow-up.rows[{r}][0]", "must be one or more Finding IDs")
            continue
        for x in cell:
            if x in seen:
                bad(f"follow-up.rows[{r}][0]", f"{x} already has a row")
            seen.add(x)


def tiers_in_scope(pack) -> list:
    sc = pack.get("scope") if isinstance(pack, dict) else None
    t = sc.get("tiers") if isinstance(sc, dict) else None
    return t if isinstance(t, list) else []


def _check_comparator_refs(pack, w, bad, warn):
    """comparator_refs ids must exist in <ws>/comparator.json (a problem), or only warn when there is no such file."""
    from ..compare import COMPARATOR_ITEM_RX
    known = set(w["comparator_ids"]) if "comparator_ids" in w else None
    for si, sec in enumerate(pack.get("sections") if isinstance(pack.get("sections"), list) else []):
        for ii, it in enumerate(sec.get("items", []) if isinstance(sec, dict) and isinstance(sec.get("items"), list) else []):
            refs = it.get("comparator_refs") if isinstance(it, dict) else None
            if refs is None:
                continue
            ip = f"sections[{si}].items[{ii}].comparator_refs"
            if not isinstance(refs, list) or not all(isinstance(x, str) and COMPARATOR_ITEM_RX.fullmatch(x) for x in refs):
                bad(ip, "must be a list of comparator item ids such as OBS-01, RC-01, REC-01 or ACT-01")
            elif "comparator_error" in w:
                warn(ip, f"comparator.json is not valid: {w['comparator_error']}; comparator_refs not verified")
            elif known is None:
                warn(ip, f"{', '.join(refs)} cannot be checked: no comparator.json in the workspace")
            else:
                for x in refs:
                    if x not in known:
                        bad(ip, f"{x} is not in comparator.json")
                if w.get("comparator_bad_items"):
                    warn(ip, f"comparator.json is not valid: {w['comparator_bad_items']} item(s) have no valid id "
                             "and are ignored")


LR_RX = re.compile(r"LR-\d{2,}")
WEAK_HOC = ("administrative", "training")
NO_REGISTER = "learning ids not verified: no register"
CROSSWALK = REFS / "standards-crosswalk.json"
_CLAUSE_IDS = []


def clause_ids() -> set:
    """Every requirement id in references/standards-crosswalk.json (frameworks.<fw>.requirements[].id), read once."""
    if not _CLAUSE_IDS:
        d = json.loads(CROSSWALK.read_text(encoding="utf-8"))
        _CLAUSE_IDS.append({r["id"] for f in d.get("frameworks", {}).values() for r in f.get("requirements", [])
                            if isinstance(r, dict) and isinstance(r.get("id"), str)})
    return _CLAUSE_IDS[0]


def register_ids(register) -> set:
    """The lr_id of every entry in a loaded register: {"entries": [...]} or a bare list."""
    entries = register.get("entries") if isinstance(register, dict) else register
    return {e["lr_id"] for e in (entries if isinstance(entries, list) else [])
            if isinstance(e, dict) and isinstance(e.get("lr_id"), str)}


def _check_links(d, p, bad, soft, known_lr, seen_lr):
    """Optional on every item and bottom-line entry: learning (a register LR id) and clauses (crosswalk ids). An id
    of the right shape that the register or crosswalk does not know is soft: a warning, or a problem when strict."""
    if "learning" in d:
        v = d["learning"]
        if not (isinstance(v, str) and LR_RX.fullmatch(v)):
            bad(f"{p}.learning", "must be LR- followed by two or more digits, e.g. LR-01")
        else:
            seen_lr.append(v)
            if known_lr is not None and v not in known_lr:
                soft(f"{p}.learning", f"unknown learning {v}")
    if "clauses" in d:
        v = d["clauses"]
        if not isinstance(v, list) or not v or not all(_text(x) for x in v):
            bad(f"{p}.clauses", "must be a non-empty list of standards-crosswalk ids, e.g. ISO45001-10.2")
        else:
            for k, x in enumerate(v):
                if x not in clause_ids():
                    soft(f"{p}.clauses[{k}]", f"unknown clause {x}")


def _check_gaps_limits(pack, w, bad):
    """Top level, optional: gaps [{text, cites, evidence_needed}] and limits [text] (L3-14)."""
    gaps = pack.get("gaps")
    if gaps is not None:
        if not isinstance(gaps, list) or not gaps:
            bad("gaps", "must be a non-empty list of {text, cites, evidence_needed}")
        else:
            F, E = {f["id"] for f in w["findings"]}, set(w.get("evidence", {}))
            for i, g in enumerate(gaps):
                gp = f"gaps[{i}]"
                if not isinstance(g, dict):
                    bad(gp, "must be an object with text, cites and evidence_needed")
                    continue
                for f in ("text", "evidence_needed"):
                    if not _text(g.get(f)):
                        bad(f"{gp}.{f}", "required")
                if "cites" in g:
                    if not _id_list(g["cites"]):
                        bad(f"{gp}.cites", "must be a list of Finding or Evidence IDs")
                    else:
                        for k, x in enumerate(g["cites"]):
                            if x not in (F if x.startswith("FND-") else E):
                                bad(f"{gp}.cites[{k}]", f"{x} is not in this workspace")
                for k in g:
                    if k not in ("text", "cites", "evidence_needed"):
                        bad(f"{gp}.{k}", "unknown key; use text, cites, evidence_needed")
    lim = pack.get("limits")
    if lim is not None and (not isinstance(lim, list) or not lim or not all(_text(x) for x in lim)):
        bad("limits", "must be a non-empty list of text")


SKILLS_DIR = REFS.parent.parent                                  # skills/<name>/skill.json
DOSSIER_PACK_RX = re.compile(r"dossier-(?:F\d+[a-z]?|index)")
VARIANT_RX = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def skill_pack(skill):
    """skills/<skill>/skill.json produces.pack, or None; KeyError when there is no such skill."""
    if not (isinstance(skill, str) and SLUG_RX.fullmatch(skill)):
        raise KeyError(skill)
    try:
        man = json.loads((SKILLS_DIR / skill / "skill.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise KeyError(skill) from e
    pk = (man.get("produces") or {}).get("pack") if isinstance(man, dict) else None
    return pk if isinstance(pk, str) else None


def pack_fits_skill(name, skill) -> bool:
    """Ruling P4-22: pack name `name` is the skill's produces.pack, or <produces.pack>-<variant>, or (for
    cluster-learning-dossier only) dossier-F<nn>[a-z] or dossier-index. False for an unknown skill."""
    try:
        main = skill_pack(skill)
    except KeyError:
        return False
    if not isinstance(name, str) or not main:
        return False
    if skill == "cluster-learning-dossier":
        return bool(DOSSIER_PACK_RX.fullmatch(name))
    return name == main or (name.startswith(main + "-") and bool(VARIANT_RX.fullmatch(name[len(main) + 1:])))


def _check_skill(pack, bad):
    """Optional top-level `skill` (L4-29): a folder in skills/ with a skill.json, which produces this pack."""
    if "skill" not in pack:
        return
    sk = pack["skill"]
    try:
        skill_pack(sk)
    except KeyError:
        bad("skill", f"unknown skill {sk}")
        return
    if _text(pack.get("pack")) and not pack_fits_skill(_ps_base_name(pack), sk):
        bad("skill", f"pack {pack['pack']} is not a pack or variant of skill {sk}")


LANG_RX = re.compile(r"^[a-z]{2,3}(-[A-Za-z0-9]{2,8})*$")       # BCP 47, as references/labels/<locale>.json


def _check_lang_dir(pack, bad):
    """Optional top-level `lang` (a BCP 47 tag such as en, hi or pt-BR; default en) and `dir` (ltr or rtl; default
    the labels' _dir), L1-08 and Ruling P4-15."""
    if "lang" in pack and not (isinstance(pack["lang"], str) and LANG_RX.fullmatch(pack["lang"])):
        bad("lang", "must be a language tag such as en, hi or pt-BR")
    if "dir" in pack and pack["dir"] not in ("ltr", "rtl"):
        bad("dir", "must be ltr or rtl")


LENSES = ("regulator", "insurer", "jv-partner", "client")      # P5-17: who the assurance is for (none: internal audit)


def _check_lens(pack, bad, soft):
    """Optional top-level `lens` (P5-17): one of LENSES. A pack with a lens needs a `lens` section holding a para on
    what that reader needs (a profile problem: soft, so a problem under --strict). A lens section in a pack with no
    `lens` (internal audit) is soft too: set the lens or drop the section."""
    if "lens" not in pack:
        secs = pack.get("sections") if isinstance(pack.get("sections"), list) else []
        if any(isinstance(s, dict) and s.get("id") == "lens" for s in secs):
            soft("lens", "a lens section needs the pack's lens field set (regulator, insurer, jv-partner or client); "
                         "for internal audit drop the section")
        return
    lens = pack["lens"]
    if lens not in LENSES:
        bad("lens", f"must be one of {', '.join(LENSES)} (leave it out for internal audit)")
        return
    secs = pack.get("sections") if isinstance(pack.get("sections"), list) else []
    sec = next((s for s in secs if isinstance(s, dict) and s.get("id") == "lens"), None)
    items = sec.get("items") if isinstance(sec, dict) and isinstance(sec.get("items"), list) else []
    if not any(isinstance(it, dict) and it.get("kind") == "para" for it in items):
        soft("lens", f"the {lens} lens needs a lens section with one para on what that reader needs")


ALERT_MODES = ("internal", "sister-site", "industry")          # P6-4: who a safety alert is for
GRADES = ("alert", "notice", "information")                    # P6-3: the alert grade, highest first


def _ps_check_alert_fields(pack, bad):
    """Optional top-level `mode`, `grade` and `grade_source` (Phase 6, P6-3/P6-4): a value outside its list is a
    problem whatever the profile."""
    from ..alert import GRADE_SOURCES                           # late: Task 2's alert module reads registers
    for key, allowed in (("mode", ALERT_MODES), ("grade", GRADES), ("grade_source", GRADE_SOURCES)):
        if key in pack and pack[key] not in allowed:
            bad(key, f"must be one of {', '.join(allowed)}")


def _ps_base_name(pack) -> str:
    """The name the pack-name and skill rules apply to: for a translation named <translation_of>-<lang> (P4-13),
    translation_of; else the pack's own name."""
    name, src, lang = pack.get("pack"), pack.get("translation_of"), pack.get("lang")
    if isinstance(src, str) and isinstance(lang, str) and name == f"{src}-{lang.lower()}":
        return src
    return name


def _ps_without_source(secs):
    """sections less each item's source_text and back_translation: their English IDs are not shown as text."""
    if not isinstance(secs, list):
        return secs
    return [dict(s, items=[{k: v for k, v in it.items() if k not in ("source_text", "back_translation")}
                           if isinstance(it, dict) else it for it in s["items"]])
            if isinstance(s, dict) and isinstance(s.get("items"), list) else s for s in secs]


def _ps_shape(pack) -> dict:
    """{path: value} of what a translation must keep (P4-14): the section ids, each section's item ids and kinds,
    and the IDs each item and bottom-line entry cites (in cites lists or inline)."""
    bl = pack.get("bottom_line") if isinstance(pack.get("bottom_line"), list) else []
    out = {"bottom_line": len(bl)}
    dq = pack.get("data_quality") if isinstance(pack.get("data_quality"), list) else []
    out["data_quality"] = [sorted(x for _, x in _walk_ids(e, "")) for e in dq]
    for i, e in enumerate(bl):
        out[f"bottom_line[{i}]"] = sorted(x for _, x in _walk_ids(e, ""))
    secs = [s for s in pack.get("sections") or [] if isinstance(s, dict)] if isinstance(pack.get("sections"), list) else []
    out["sections"] = [s.get("id") for s in secs]
    for si, s in enumerate(_ps_without_source(secs)):
        items = [it for it in s.get("items") if isinstance(it, dict)] if isinstance(s.get("items"), list) else []
        out[f"sections[{si}].items"] = [[it.get("id") or f"{s.get('id')}-{n}", it.get("kind")]
                                        for n, it in enumerate(items, 1)]
        for ii, it in enumerate(items):
            out[f"sections[{si}].items[{ii}]"] = sorted(x for _, x in _walk_ids(it, ""))
    return out


def _ps_check_translation(pack, source, bad, soft):
    """A pack with translation_of (P4-13, P4-14): a valid source name and a lang; source_text and back_translation
    well formed; a safety-critical item without a back_translation (soft); and, when the source pack is given, the
    same cites, ids, kinds and section ids (always a problem)."""
    if "translation_of" not in pack:
        return
    src = pack["translation_of"]
    if not (isinstance(src, str) and PACK_NAME_RX.fullmatch(src)):
        bad("translation_of", "must be a pack name")
        return
    if "lang" not in pack:
        bad("lang", "required in a translation (translation_of)")
    from ..strings import safety_critical
    for si, s in enumerate(pack.get("sections") if isinstance(pack.get("sections"), list) else []):
        items = s.get("items") if isinstance(s, dict) and isinstance(s.get("items"), list) else []
        for ii, it in enumerate(items):
            if not isinstance(it, dict):
                continue
            ip = f"sections[{si}].items[{ii}]"
            st = it.get("source_text")
            if st is not None and not (isinstance(st, dict) and all(isinstance(v, str) for v in st.values())):
                bad(f"{ip}.source_text", "must be an object of field -> English text")
            if "back_translation" in it and not _text(it["back_translation"]):
                bad(f"{ip}.back_translation", "must be non-empty text")
            if safety_critical(it) and not _text(it.get("back_translation")):
                iid = it.get("id") or (f"{s['id']}-{ii + 1}" if isinstance(s.get("id"), str) else ip)
                soft(ip, f"item {iid} is safety-critical: add back_translation")
    if isinstance(source, dict):
        want, got = _ps_shape(source), _ps_shape(pack)
        for k in want:
            if want[k] != got.get(k):
                bad(k, f"differs from the source pack {src}: {want[k]} -> {got.get(k)}")


def _ps_source_pack(a, pack):
    """For a translation: the source pack <translation_of>.json beside the translated file, else in the run's
    outputs; None when there is none (then only the translation itself is checked)."""
    src = pack.get("translation_of") if isinstance(pack, dict) else None
    if not (isinstance(src, str) and PACK_NAME_RX.fullmatch(src)):
        return None
    for d in (Path(a.pack).resolve().parent, outputs_dir(a.ws)):
        f = d / f"{src}.json"
        if f.is_file():
            got, err = load_pack(f)
            return got if not err and isinstance(got, dict) else None
    return None


def check_pack(pack, w, *, names=(), orgs=(), share=None, strict=False, register=None, source=None) -> Result:
    """Every problem that would make the pack wrong or unrenderable (problems), plus advice (warnings). register: a
    loaded Learnings Register, against which learning ids are checked (P3-12). source: for a translation (P4-14), the
    loaded pack it translates, whose cites, ids, kinds and section ids it must keep. strict (Ruling P3-5): pack-profile
    violations, padding, scope drift, an unknown learning id and an unknown clause are problems, not warnings."""
    P, W = [], []
    known_lr = register_ids(register) if register is not None else None
    seen_lr = []

    def bad(path, msg):
        P.append(f"{path}: {msg}")

    def warn(path, msg):
        W.append(f"{path}: {msg}")

    def soft(path, msg):
        (bad if strict else warn)(path, msg)

    if not isinstance(pack, dict):
        return Result(["(root): a pack must be a JSON object"], [], {})
    for k, typ in (("pack", str), ("title", str), ("audience", str), ("status", str),
                   ("bottom_line", list), ("sections", list)):
        v = pack.get(k)
        if k not in pack:
            bad(k, "required")
        elif not isinstance(v, typ) or not v or (typ is str and not v.strip()):
            bad(k, f"must be a non-empty {'list' if typ is list else 'string'}")
    if pack.get("schema") != SCHEMA_VERSION or isinstance(pack.get("schema"), bool):
        bad("schema", f"must be {SCHEMA_VERSION}")
    if _text(pack.get("pack")) and not PACK_NAME_RX.fullmatch(_ps_base_name(pack)):
        bad("pack", "must be lowercase words joined by hyphens (or dossier-F<nn>)")
    _check_skill(pack, bad)
    _check_lang_dir(pack, bad)
    _check_lens(pack, bad, soft)
    _ps_check_alert_fields(pack, bad)
    _ps_check_translation(pack, source, bad, soft)
    inc = pack.get("incident")
    if inc is not None:
        if not isinstance(inc, dict):
            bad("incident", "must be an object with title and/or date")
        else:
            for k in inc:
                if k not in ("title", "date"):
                    bad(f"incident.{k}", "unknown key; use title, date")
            if "title" in inc and not _text(inc["title"]):
                bad("incident.title", "must be non-empty text")
            if "date" in inc and not (isinstance(inc["date"], str) and len(inc["date"]) == 10 and _iso_partial(inc["date"])):
                bad("incident.date", "must be YYYY-MM-DD")
    bl = pack.get("bottom_line") if isinstance(pack.get("bottom_line"), list) else []
    if len(bl) > MAX_BOTTOM_LINE:
        bad("bottom_line", f"at most {MAX_BOTTOM_LINE} entries (got {len(bl)})")
    for i, e in enumerate(bl):
        if not isinstance(e, dict) or not _text(e.get("text")):
            bad(f"bottom_line[{i}].text", "required")
            continue
        if not (_id_list(e.get("cites")) and e.get("cites")):
            bad(f"bottom_line[{i}].cites", "every bottom-line entry needs at least one Finding or Evidence ID")
        _check_extras(e, f"bottom_line[{i}]", bad)
        _check_links(e, f"bottom_line[{i}]", bad, soft, known_lr, seen_lr)
    _check_scope(pack.get("scope"), w, bad)
    _check_notes(pack, w, bad)

    secs = pack.get("sections") if isinstance(pack.get("sections"), list) else []
    seen, n_items = set(), 0
    t1_pack = "T1" in tiers_in_scope(pack)
    for si, s in enumerate(secs):
        sp = f"sections[{si}]"
        if not isinstance(s, dict):
            bad(sp, "must be an object")
            continue
        sid = s.get("id")
        if not isinstance(sid, str) or not SLUG_RX.fullmatch(sid):
            bad(f"{sp}.id", "required: lowercase words joined by hyphens")
            sid = None
        elif sid in seen:
            bad(f"{sp}.id", f"duplicate id {sid!r}")
        else:
            seen.add(sid)
        if not _text(s.get("heading")):
            bad(f"{sp}.heading", "required")
        if "intro" in s and not _text(s.get("intro")):
            bad(f"{sp}.intro", "must be non-empty text when present")
        items = s.get("items")
        if not isinstance(items, list) or not items:
            bad(f"{sp}.items", "required: a non-empty list")
            continue
        for ii, it in enumerate(items):
            n_items += 1
            ip = f"{sp}.items[{ii}]"
            iid = it.get("id") if isinstance(it, dict) else None
            if iid is not None and not (isinstance(iid, str) and SLUG_RX.fullmatch(iid)):
                bad(f"{ip}.id", "must be lowercase words joined by hyphens")
                iid = None
            elif iid is None and sid:
                iid = f"{sid}-{ii + 1}"
            if iid is not None:
                if iid in seen:
                    bad(f"{ip}.id", f"duplicate id {iid!r}")
                seen.add(iid)
            _check_item(it, ip, bad, warn)
            if isinstance(it, dict):
                _check_links(it, ip, bad, soft, known_lr, seen_lr)
                if (it.get("kind") == "recommendation" and _text(it.get("hoc_tier"))
                        and norm_hoc(it["hoc_tier"]) in WEAK_HOC and not _text(it.get("why_not_stronger"))):
                    warn(ip, f"recommendation {iid or ip} is administrative or training only: say why_not_stronger")
            if (isinstance(it, dict) and it.get("kind") == "card" and not it.get("organisation_changing")
                    and t1_pack):
                warn(f"card {iid or ip}", "add organisation_changing (what the organisation is changing)")
            if (isinstance(it, dict) and it.get("kind") == "toolbox" and isinstance(it.get("warning_signs"), list)
                    and len(it["warning_signs"]) != TOOLBOX_SIGNS):
                warn(f"toolbox {iid or ip}", "a toolbox talk has two warning signs")
    if pack.get("pack") == "investigator-coach":
        _check_follow_up(secs, bad)
    _check_gaps_limits(pack, w, bad)
    if seen_lr and known_lr is None:
        W.append(NO_REGISTER)

    F = {f["id"] for f in w["findings"]}
    E = set(w.get("evidence", {}))
    cit_all = _citable(pack)
    ids, cit = set(), set()
    for path, x in _walk_ids(cit_all, ""):
        ids.add(x)
        cit.add((path, x))
        if x not in (F if x.startswith("FND-") else E):
            bad(path, f"{x} is not in this workspace")
    for path, x in _walk_ids({"data_quality": pack.get("data_quality"), "bottom_line": pack.get("bottom_line"),
                              "sections": _ps_without_source(pack.get("sections"))}, ""):
        if (path, x) not in cit:
            warn(path, f"{x} is shown as plain text, not a citation; put it in cites")
    downs = downgraded_findings(w)
    noted = {x for _, x in _walk_ids(cit_all["data_quality"], "data_quality") if x.startswith("FND-")}
    FM = {f["id"]: f for f in w["findings"]}
    units = [(f"bottom_line[{i}]", e) for i, e in enumerate(cit_all["bottom_line"])]
    for si, s in enumerate(cit_all["sections"]):
        units += [(f"sections[{si}].items[{ii}]", it) for ii, it in enumerate(s.get("items", []))]
    for upath, unit in units:
        found = list(_walk_ids(unit, upath))
        for p_, x in found:
            if x in downs and x not in noted:
                bad(p_, f"cites {x}, which has a reviewer downgrade vote; add a data_quality note citing it, or leave it out")
        fnds = {x for _, x in found if x.startswith("FND-") and x in FM}
        if fnds:
            linked = set().union(*(linked_evidence(FM[x]) for x in fnds))
            for x in dict.fromkeys(x for _, x in found if x.startswith("EVD-") and x in E and x not in linked):
                warn(upath, f"{x} is not linked to any finding this item cites")
    for i, x in enumerate(excluded_ids(pack)):
        if x in ids:
            at = min(p_ for p_, y in cit if y == x)
            bad(f"exclusions[{i}].id", f"{x} is also cited at {at}; a finding is either cited or left out on purpose: "
                                       f"remove it from that cite list, or from exclusions")
    prof, top = profiles.profile_for(pack.get("pack")), None
    if not P:
        rel = [x for x in relevant_findings(w, pack.get("scope")) if x not in excluded_ids(pack)]
        top = top_rated_of(w, rel)
        got, top_got, floor = len(set(rel) & ids), len(set(top) & ids), profiles.coverage_floor(prof)
        if top and top_got < floor * len(top):
            low = COVERAGE_WARNING.format(x=top_got, y=len(top))
            if floor != profiles.DEFAULT_COVERAGE_FLOOR:
                low = low.replace("a quarter", f"{floor:.0%}")
            W.append(f"coverage: cites {got} of {len(rel)} relevant findings; {low}")
    _check_comparator_refs(pack, w, bad, warn)
    strict_msgs = profiles.check(pack, prof, top, w=w) if prof else []
    strict_msgs += [f"items: {x}" for x in profiles.padding(pack)]
    strict_msgs += [f"scope: {x}" for x in profiles.scope_drift(pack, profiles.load_audiences())]
    (P if strict else W).extend(strict_msgs)
    P += profiles.hard(pack, prof, register) if prof else []       # no-owner-due (D7) and the Phase 6 problems
    W += profiles.advice(pack, prof) if prof else []               # grade-source: a warning even under --strict
    hp, hw = check_handling(pack)
    P += hp
    W += hw
    for h in lint.lint(pack, w, kind="pack", share=share, names=names, orgs=orgs,   # JC11 owns the status check
                       profile=prof):
        if h.rule != "JC11" or _text(pack.get("status")):
            (P if h.severity == "error" else W).append(lint.as_problem(h))
    return Result(P, W, {"sections": len(secs), "items": n_items, "cited": len(ids)})


def load_pack(path) -> tuple:
    """(parsed JSON, None) or (None, a problem line)."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, f"(file): {path} not found"
    except json.JSONDecodeError as e:
        return None, f"(json): invalid JSON at line {e.lineno} column {e.colno}: {e.msg}"
    except (OSError, UnicodeDecodeError, RecursionError) as e:
        return None, f"(file): cannot read {path} as UTF-8 JSON ({e.__class__.__name__})"


def load_register(a):
    """(register, None), (None, None) when there is none, or (None, a problem line). From --register FILE, else
    auto-detected at <run>/outputs/learnings-register.json (P3-12); an auto-detected file that cannot be read is
    reported with a warning and ignored, so it never blocks a pack."""
    path = getattr(a, "register", None)
    if not path:
        auto = outputs_dir(a.ws) / "learnings-register.json"
        if not auto.is_file():
            return None, None
        reg, err = _read_register(auto)
        if err:
            print(f"warning: {err}; ignored")
        return reg, None
    return _read_register(path)


def _read_register(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, f"(register): {path} not found"
    except json.JSONDecodeError as e:
        return None, f"(register): {path} is not valid JSON (line {e.lineno} column {e.colno}: {e.msg})"
    except (OSError, UnicodeDecodeError, RecursionError) as e:
        return None, f"(register): cannot read {path} as UTF-8 JSON ({e.__class__.__name__})"


def record_check(a, pack, res, w=None) -> None:
    """Record the check of a.pack in the workspace manifest, with its coverage when the workspace is given (a failed
    write is ignored)."""
    if isinstance(pack, dict) and isinstance(pack.get("pack"), str):
        try:
            cov = None
            if w is not None and not res.problems:
                from .markdown import coverage   # markdown imports this module
                cov = coverage(w, pack)
            record_pack_check(a.ws, pack["pack"], a.pack, not res.problems, len(res.problems), coverage=cov,
                              strict=bool(getattr(a, "strict", False)))
        except Exception:   # noqa: BLE001 - coverage is a nicety; it never blocks a check
            pass


def _checked(a, record_ok=True):
    """Load the workspace and pack, print warnings, exit listing every problem; else return (w, pack, result).
    record_ok=False leaves a passing check unrecorded for the caller to record (a share that is refused records
    nothing); a failing check is always recorded."""
    w = load_ws(a.ws)
    pack, err = load_pack(a.pack)
    register, rerr = (None, None) if err else load_register(a)
    err = err or rerr
    res = Result([err], [], {}) if err else check_pack(pack, w, **lint.cli_options(a),
                                                        strict=bool(getattr(a, "strict", False)), register=register,
                                                        source=_ps_source_pack(a, pack))
    if not err:
        res.warnings.extend(unsigned_warning(pack, w, a.pack, a.ws))
    if not err and (record_ok or res.problems):
        record_check(a, pack, res, w)
    from ..util import json_extra
    json_extra(problems=list(res.problems), warnings=list(res.warnings), stats=dict(res.stats))
    for x in res.warnings:
        print(f"warning: {x}")
    if res.problems:
        for x in res.problems:
            print(x, file=sys.stderr)
        sys.exit(f"{len(res.problems)} problem(s) in {a.pack}.{' Nothing written.' if a.cmd == 'pack' else ''}")
    return w, pack, res


def cmd_check_pack(a):
    _, _, res = _checked(a)
    s = res.stats
    print(f"OK: {s['sections']} sections, {s['items']} items, {s['cited']} cited IDs")
