"""Field roles (Ruling P4-5): an item as labelled blocks in its kind's field order, for every renderer that has no
layout of its own for a kind; plus the pack's word count and reading time (P4-19) and the learner view (P4-9)."""
from __future__ import annotations

import collections
import copy
import math
import re
import unicodedata

from ..pack import schema as rf_schema          # rf_schema.KINDS: actions.py has its own KINDS (M-2)
from ..pack.schema import CITE_FIELDS, GENERIC_FIELDS, ID_RX

Block = collections.namedtuple("Block", "field role label value")   # value: str | list[str] | list[list] | dict
ROLES = ("title", "body", "list", "badge", "indicator", "table", "events", "graph", "segments", "choices", "injects")
LEARNER_DROP = ("answer", "good_evidence")                  # and every option's `correct` flag
WORDS_PER_MINUTE = 200
# Not words a reader reads: ids, citations, kinds and enum values (P4-19).
RF_SKIP_KEYS = {"kind", "id", "date", "time", "signal", "hold_point", "hoc_tier", "state", "type",
                "evidence_strength", "correct", "seconds", "offset", "learning", "clauses", "comparator_refs", "group",
                "lint_ok", "lang", "dir", "channel", *CITE_FIELDS,
                "source_text", "back_translation"}       # a translation's English, for its reviewer (FR-4)


def _rf_mark_class() -> str:
    """The combining marks of the Basic Multilingual Plane as a regex class body: \\w leaves out vowel signs such as
    Devanagari matras, which would split one Hindi word into several (FR-4)."""
    out, start, prev = [], None, None
    for c in range(0x300, 0x10000):
        if unicodedata.category(chr(c)).startswith("M"):
            if start is None:
                start = c
            prev = c
        elif start is not None:
            out.append(f"\\u{start:04x}-\\u{prev:04x}")
            start = None
    return "".join(out)


RF_WORD_CHARS = r"[\w" + _rf_mark_class() + "]"
RF_WORD_RX = re.compile(rf"{RF_WORD_CHARS}+(?:[-'’]{RF_WORD_CHARS}+)*")


def _rf_role(v) -> str:
    return "list" if isinstance(v, list) else "body"


def item_blocks(it: dict, labels: dict, *, view: str = "full") -> list:
    """The item's present fields as Blocks, in KINDS[kind]["fields"] order. view="learner" leaves out the answer
    fields. A kind KINDS does not know shows every non-generic field, labelled by its f.<field> key or its name."""
    spec = rf_schema.KINDS.get(it.get("kind")) if isinstance(it.get("kind"), str) else None
    if spec is not None:
        pairs = [(f, r, labels[f"f.{f}"]) for f, r in spec.get("fields", []) if f in it]
    else:
        pairs = [(f, _rf_role(v), labels.get(f"f.{f}", f)) for f, v in it.items()
                 if f not in GENERIC_FIELDS and f not in CITE_FIELDS]
    out = []
    for f, role, lab in pairs:
        v = it[f]
        if v is None or (view == "learner" and f in LEARNER_DROP):
            continue
        if view == "learner" and f == "options" and isinstance(v, list):
            if it.get("kind") == "question" and it.get("type") == "short":
                continue                                  # a short question's options ARE the accepted answers
            v = [{k: x for k, x in o.items() if k != "correct"} if isinstance(o, dict) else o for o in v]
        out.append(Block(f, role, lab, v))
    return out


def item_text(it: dict) -> str:
    """A one-line summary of an item: its first title or body field, whitespace collapsed ("" when it has none)."""
    spec = rf_schema.KINDS.get(it.get("kind")) if isinstance(it.get("kind"), str) else None
    for f, role in (spec or {}).get("fields", []):
        if role in ("title", "body") and isinstance(it.get(f), str) and it[f].strip():
            return " ".join(it[f].split())
    return ""


RF_NESTED_SKIP = {"from", "to"}                            # graph edge ends are node ids


def _rf_words(v, nested=False) -> int:
    if isinstance(v, str):
        return len(RF_WORD_RX.findall(ID_RX.sub(" ", v)))
    if isinstance(v, list):
        return sum(_rf_words(x, True) for x in v)
    if isinstance(v, dict):
        skip = RF_SKIP_KEYS | (RF_NESTED_SKIP if nested else set())
        return sum(_rf_words(x, True) for k, x in v.items() if k not in skip)
    return 0


def pack_words(pack: dict) -> int:
    """The words of every renderable string in the bottom line and the items (P4-19). Ids, cites, kinds and enum
    fields are skipped, and inline Finding and Evidence IDs are not words."""
    n = sum(_rf_words(b.get("text")) for b in pack.get("bottom_line") or [] if isinstance(b, dict))
    for s in pack.get("sections") or []:
        for it in s.get("items") or [] if isinstance(s, dict) else []:
            if isinstance(it, dict):
                n += _rf_words({k: v for k, v in it.items() if k not in RF_SKIP_KEYS})
    return n


def reading_minutes(pack: dict) -> int:
    """max(1, ceil(words / 200)) (P4-19)."""
    return max(1, math.ceil(pack_words(pack) / WORDS_PER_MINUTE))


def learner_view(pack: dict) -> dict:
    """A deep copy without answer, good_evidence, every option's correct flag and a short question's options (P4-9)."""
    p = copy.deepcopy(pack)
    for s in p.get("sections") or []:
        for it in s.get("items") or [] if isinstance(s, dict) else []:
            if not isinstance(it, dict):
                continue
            for f in LEARNER_DROP:
                it.pop(f, None)
            if it.get("kind") == "question" and it.get("type") == "short":
                it.pop("options", None)                   # the accepted answers are the key (P4-10)
            for o in it.get("options") or [] if isinstance(it.get("options"), list) else []:
                if isinstance(o, dict):
                    o.pop("correct", None)
    return p
