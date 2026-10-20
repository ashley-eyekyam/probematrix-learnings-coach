"""Privacy core: names, organisations, equipment tags and singleton roles, shared by check-language, scan-names,
make-public-sample and the share tools, plus the --share transforms (share_text, share_doc).
Also the scan-names core (names, Office and PDF metadata)."""
from __future__ import annotations

import calendar
import collections
import copy
import html
import json
import os
import re
import sys
from pathlib import Path

from . import BRAND
from .util import _need_openpyxl, HERE


TERMS_FILE = HERE.parent / "references" / "lint-terms.json"

# A phone number is a run of digits, spaces and hyphens; it never starts inside another number and never starts
# with a date shape (2020-09-24, 24-09-2020, 24/09/2020), so ISO dates are not phone numbers (ruling X21).
PATTERNS = {"email": r"[\w.+-]+@[\w-]+\.[\w.-]+",
            "phone": r"(?<![\w+-])(?!\d{4}-\d{2}-\d{2}(?!\d))(?!\d{1,2}[-/.]\d{1,2}[-/.]\d{4}(?!\d))"
                     r"\+?\d[\d\s-]{8,}\d(?![\w-])",
            "staff_no": r"(?i)\b(staff|emp(loyee)?|CPF|badge|ID)\s*(no\.?|number|#)\s*\w+"}
BRAND_EMAIL = re.search(PATTERNS["email"], BRAND).group(0).lower()
# An organisation name ends in a company suffix: "Acme Pumps Ltd".
ORG_SUFFIX_RX = re.compile(r"\b(?:[A-Z][\w&'-]*\s+){1,4}(?:Ltd|Pvt|Inc|GmbH|LLC|Limited)\b\.?")
# A role string that carries an instance identifier: a qualifier word plus a number or letter id ('Gate 3',
# 'CR-2', 'Shift A', 'No. 4'), '#<digits>', or a ' - X' / '(X)' suffix that contains a digit. A bare 'control room',
# 'shift', '(owner)' or '- Operations' does not identify one person.
QUALIFIER_RX = re.compile(r"\b(?i:post|gate|shift|grade|no\.?|desk|cabin|CR|control room)[\s-]*(?:\d+|[A-Z]\b)"
                          r"|#\s*\d|\s-\s[^()]*\d[^()]*$|\([^()]*\d[^()]*\)\s*$")
# A date ('Dec-2019', '24 May 2020', '12/03/2020', '2020-03-12', a bare year) is no qualifier: it does not point at
# one person, so QUALIFIER_RX is read with dates removed (A31).
DATE_QUALIFIER_RX = re.compile(r"(?i)\b(?:\d{1,2}(?:st|nd|rd|th)?[\s./-]+)?(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)"
                               r"[a-z]*\.?[\s,./-]*(?:\d{1,2}(?:st|nd|rd|th)?,?[\s./-]+)?(?:19|20)\d{2}\b"
                               r"|\b\d{1,4}[./-]\d{1,2}[./-]\d{1,4}\b|\b(?:19|20)\d{2}\b")
# A group role (the crew, not a person) is never a singleton.
GROUP_RX = re.compile(r"(?i)\b(?:operators|crew|team|staff|workers|personnel)\s*$")

# Equipment tags such as AO-101 or PSV12A: letters then digits. Finding, Evidence, LR and ML IDs are not tags, and
# neither are Learning Cluster entity IDs (F02, F99) or tier IDs (T4) (ruling X21). The lookbehinds keep the tail of a
# hex ID (FND-AE629313) from matching after its hyphen.
TAG_RX = re.compile(r"\b(?<!FND-)(?<!EVD-)(?<!LR-)(?<!ML-)(?!(?:FND|EVD|LR|ML)-)(?!(?:F\d{2}|T\d)\b)"
                    r"[A-Z]{1,5}-?\d{2,6}[A-Z]?\b")
# Keys whose values are IDs or taxonomy labels, not prose: share_doc keeps them as they are (and the lint skips them).
ID_KEYS = {"id", "kind", "pack", "schema", "cites", "supporting_cites", "row_cites", "row_supporting_cites",
           "finding_ids", "evidence_ids", "lr_id", "ml_id", "owner_entity", "entities", "scope", "content_hash",
           "rule"}                                       # a lint_ok rule ID (JC10) is not an equipment tag
# Inside a graph item's edges, from and to are node IDs (elsewhere `to` is display text, e.g. a message's audience).
EDGE_ID_KEYS = ("from", "to")
# Dicts whose keys are role strings (clusters.json role_map): share_doc masks their keys as well as their values.
ROLE_KEYED = {"role_map"}


def _list_file(path, env, flag) -> list:
    """Stripped lines of a text file, skipping blank lines and lines starting with '#'. A staff ID is written
    'ID #4471', so it is kept. The path falls back to the environment variable env; neither gives []. A missing
    file exits with a one-line message naming the flag (or the variable) it came from."""
    p = path or os.environ.get(env)
    if not p:
        return []
    if not Path(p).is_file():
        sys.exit(f"{flag if path else env}: file not found: {p}")
    out = []
    for line in Path(p).read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#") and s not in out:
            out.append(s)
    return out


def load_names(path=None) -> list:
    """Names from a names file (one per line), falling back to PMLC_NAMES."""
    return _list_file(path, "PMLC_NAMES", "--names")


def load_orgs(path=None) -> list:
    """Organisation names from an orgs file (one per line), falling back to PMLC_ORGS."""
    return _list_file(path, "PMLC_ORGS", "--orgs")


def _terms() -> dict:
    return json.loads(TERMS_FILE.read_text(encoding="utf-8"))


def _spread_initials(name: str) -> str:
    """'R.K. Vandermere' as 'R. K. Vandermere': initials written without spaces are separate initials (A32)."""
    return re.sub(r"(?<![A-Za-z])([A-Za-z])\.(?=[A-Za-z])", r"\1. ", name)


def name_variants(name: str, skip_role_words=False) -> list:
    """The ways a person is named in text: the full name as given, surname only, initial plus surname, and an
    honorific plus surname for each honorific in lint-terms.json. 'Shri R. K. Vandermere' (or 'R.K. Vandermere')
    gives 'Vandermere', 'R. Vandermere', 'R K Vandermere', 'Shri Vandermere', 'Shri. Vandermere' and so on. A line with a digit (a staff ID) has no variants.
    skip_role_words=True (share masking and scan-names --variants, M1) leaves out a one-word variant that is a role
    noun or a lint vocabulary word ('Officer', 'Field'), so it never masks a role; --redact keeps it and warns (X17)."""
    name = " ".join(_spread_initials(name).split())
    out = [name]
    if not name or any(ch.isdigit() for ch in name):
        return out
    hons = {h.lower() for h in _terms()["honorifics"]}
    toks = name.split()
    while toks and toks[0].rstrip(".").lower() in hons:
        toks = toks[1:]
    words = [t for t in toks if len(t.rstrip(".")) > 1]
    initials = [t.rstrip(".")[0] for t in toks if len(t.rstrip(".")) == 1]
    if not words:
        return out
    sur = words[-1]
    if not initials and len(words) > 1:
        initials = [words[0][0]]
    forms = [sur]
    for ini in ([initials[:1], initials] if initials else []):
        forms += [" ".join(f"{i}." for i in ini) + " " + sur, " ".join(ini) + " " + sur]
    for h in _terms()["honorifics"]:
        forms += [f"{h} {sur}", f"{h}. {sur}"]
    role_words = {x.lower() for x in _terms()["role_nouns"] + _terms()["name_vocabulary"]} if skip_role_words else ()
    for f in forms:
        if " " not in f and f.lower() in role_words:     # M1: "Officer" alone is a role word, not this person
            continue
        if f not in out:
            out.append(f)
    return out


def _alt(x: str) -> str:
    """Regex for one name form. Whitespace matches any run; an initial ('R.' or 'R') has an optional dot and may
    be followed directly by the next token, so 'R. K. Vandermere' also matches 'R.K. Vandermere' and 'R K Vandermere'."""
    out, prev_initial = [], False
    for i, t in enumerate(x.split()):
        initial = bool(re.fullmatch(r"[A-Za-z]\.?", t))
        if i:
            out.append(r"\s*" if prev_initial else r"\s+")
        out.append(re.escape(t[0]) + r"\.?" if initial else re.escape(t))
        prev_initial = initial
    return "".join(out)


def name_pattern(names, variants=False, skip_role_words=False):
    """One case-insensitive regex for a list of names (None for an empty list), bounded by (?<!\\w) and (?!\\w) so
    'Vandermere' does not match inside 'Vandermeres' and a space matches any run of whitespace. variants=True adds the
    name_variants of each name (skip_role_words: see name_variants)."""
    xs = []
    for n in names:
        for v in (name_variants(n, skip_role_words) if variants else [" ".join(_spread_initials(n).split())]):
            if v and v not in xs:
                xs.append(v)
    if not xs:
        return None
    alts = "|".join(_alt(x) for x in sorted(xs, key=len, reverse=True))
    return re.compile(r"(?<!\w)(?:" + alts + r")(?!\w)", re.I)


def build_singletons(role_map: dict, findings: list, tax: dict, tier_labels: dict) -> dict:
    """The singleton_roles.json document for a classify run. role_map is {role: {F, T, R, source}}, tax carries the
    entity labels. A role is a 'qualifier' when its string has a grade, post or location qualifier, and a
    'single-holder' when it is the only role mapped to a top-post entity and tier."""
    ents = {e["id"]: e["name"] for e in tax["entities"]}
    holders = set(_terms().get("single_holder_entities", []))
    count = {r: sum(1 for f in findings if r in f["roles"]) for r in role_map}
    by_slot = {}
    for r, m in role_map.items():
        for e in m["F"]:
            if e in holders:
                by_slot.setdefault((e, m["T"]), []).append(r)
    sole = {rs[0]: slot for slot, rs in by_slot.items() if len(rs) == 1}
    roles = []
    for r in sorted(role_map):
        if GROUP_RX.search(re.split(r"\s-\s|\(", r)[0].strip()):
            continue
        reason = "qualifier" if QUALIFIER_RX.search(DATE_QUALIFIER_RX.sub("", r)) else "single-holder" if r in sole else None
        if not reason:
            continue
        m = role_map[r]
        e = sole[r][0] if r in sole else (m["F"] or ["F99"])[0]
        label = f"{ents.get(e, 'Unmapped')} ({tier_labels.get(m['T'], 'Unresolved')})"
        roles.append({"role": r, "reason": reason, "findings": count[r], "generalised": label})
    return {"version": 1, "roles": roles}


def load_singletons(w) -> dict:
    """{role: generalised label} from the workspace's singleton_roles.json (w["singletons"], a list of entries)."""
    return {e["role"]: e["generalised"] for e in w.get("singletons", []) or []}


# ----------------------------------------------------------------------------- --share external|public (L5-08)

ShareCtx = collections.namedtuple("ShareCtx", "mode names orgs singletons")
SHARE_MASKED = ("external", "public")
# Keys share_doc removes at any depth (compared after lower-casing and joining words with "_").
SHARE_DROP_KEYS = {"suggested_interviews", "key_questions", "causal_hypothesis", "evidence_to_collect", "generated",
                   "run"}
NAME_MASK, ORG_MASK, TAG_MASK = "[name]", "[organisation]", "[equipment tag]"
MONTH_NAMES = list(calendar.month_name)[1:]
_MON = {m[:3].lower(): i for i, m in enumerate(MONTH_NAMES, 1)}
_MON_RX = r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?"
# A clock time, with the "at" (or "at about") that introduces it, so "restarted at 14:05 on" reads "restarted on":
# H:MM or HH:MM (optional :SS, optional am/pm or hrs), and HHMM only with hrs or hours ("1405 hrs"). A colon time
# with no seconds and no suffix ("bare") is kept when a ratio word sits next to it, e.g. "ratio 1:10" (X23).
# H.MM or HH.MM counts only with am, pm or hrs ("9.15 am", "21.30 hrs"), so "2.50 hours" stays a duration.
AMPM = r"(?:[ap]m\b|[ap]\.m\b\.?)"                  # "pm" leaves a sentence full stop alone; "p.m." takes its own
TIME_RX = re.compile(r"(?:\bat\s+(?:about\s+|around\s+|approximately\s+)?)?(?<![\w:.])"
                     r"(?:(?P<clock>(?:[01]?\d|2[0-3]):[0-5]\d)(?P<sec>:[0-5]\d)?"
                     r"(?P<suf>\s*(?:hrs?\b|hours?\b|" + AMPM + r"))?(?![\d:])"
                     r"|(?:[01]\d|2[0-3])[0-5]\d\s*(?:hrs?|hours?)\b"
                     r"|(?:[01]?\d|2[0-3])\.[0-5]\d\s*(?:hrs\b|" + AMPM + r"))", re.I)
# A bare HHMM (0000-2359) after a preposition, which goes with it: "At 0216", "at about 0300", "from 0200 until 0415",
# "since 0300". Years are kept: after about, around, approximately, by, from, since, until or till, 1900-2099 reads as
# a year ("from 2017", "by 2020", "since 2018"); only "at" takes those as times ("at 1930"). "in" is never followed
# by a time. A following unit ("at 1500 rpm", "about 1200 m") makes it a quantity, also kept, and so does a number
# after a bare about/around/approximately that starts without a zero and is followed by a plural noun ("about 1200
# workers"); "at about 1200" and "around 0220" are times.
PREP_HHMM_RX = re.compile(r"\b(?P<prep>at\s+(?:about\s+|around\s+|approximately\s+|approx\.\s*)?"
                          r"|(?:about|around|approximately|by|from|since|until|till)\s+|approx\.\s*)"
                          r"(?P<hhmm>(?:[01]\d|2[0-3])[0-5]\d)(?:\s*[-–]\s*(?:[01]\d|2[0-3])[0-5]\d)?(?![-/:]|[.,]\d|\w)", re.I)
_UNIT_AFTER = re.compile(r"\s*([A-Za-z]+\d?|%|°[CF]?)(?!\w)")
UNIT_WORDS = {"rpm", "kpa", "mpa", "pa", "bar", "barg", "psi", "psig", "mm", "cm", "m", "km", "kg", "g", "t", "te",
              "tonnes", "tons", "l", "litres", "liters", "ml", "m3", "nm3", "scm", "ppm", "kw", "mw", "w", "v", "kv",
              "a", "hz", "metres", "meters", "feet", "ft", "units", "people", "%", "°", "°c", "c", "k"}
RATIO_WORDS = {"ratio", "ratios", "slope", "slopes", "scale", "odds", "mix", "mixture", "dilution", "dilutions"}
_WORD_BEFORE = re.compile(r"([A-Za-z]+)\s*(?:\bof\s*)?$")      # "ratio 1:10" and "a ratio of 1:10", not across a full stop
_WORD_AFTER = re.compile(r"^\s*([A-Za-z]+)")
_NOT_PLURAL = {"was", "has", "is", "as", "his", "this", "its", "us", "yes", "always", "across", "press"}
_SENTINEL = "\ue000"                                                # marks a removed time while strip_times tidies it
ISO_DATE_RX = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})(?:[T ](?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d(?:\.\d+)?)?"
                         r"(?:Z|[+-]\d{2}:?\d{2})?)?(?![\d-])")
DMY_TEXT_RX = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?[ -]" + _MON_RX + r",?[ -](\d{4})\b", re.I)
MDY_TEXT_RX = re.compile(r"\b" + _MON_RX + r" (\d{1,2})(?:st|nd|rd|th)?,? (\d{4})\b", re.I)
SLUG_DATE_RX = re.compile(r"(?<![\w-])(\d{4})-\d{2}-\d{2}-(?=[A-Za-z])")       # '2020-09-24-hazira-...' (a run slug)
NUM_DATE_RX = re.compile(r"\b(\d{1,2})[./](\d{1,2})[./](\d{4})\b")


def _month(year, month) -> str | None:
    m = int(month)
    return f"{MONTH_NAMES[m - 1]} {year}" if 1 <= m <= 12 else None


def _num_date(m) -> str:
    """D/M/YYYY as the engine reads it (day first), else M/D/YYYY; the year alone if neither is a date."""
    d, mo, y = int(m.group(1)), int(m.group(2)), m.group(3)
    if 1 <= mo <= 12 and 1 <= d <= 31:
        return _month(y, mo)
    return _month(y, d) if 1 <= d <= 12 and 1 <= mo <= 31 else y


def coarsen_dates(text: str) -> str:
    """ISO dates and date-times, 'D Month YYYY', 'Month D, YYYY' and D/M/YYYY become 'Month YYYY'. The ISO date that
    starts a slug ('2020-09-24-hazira-...') keeps its year only ('2020-hazira-...')."""
    text = SLUG_DATE_RX.sub(lambda m: m.group(1) + "-", text)
    text = ISO_DATE_RX.sub(lambda m: _month(m.group(1), m.group(2)) or m.group(0), text)
    text = DMY_TEXT_RX.sub(lambda m: _month(m.group(3), _MON[m.group(2).lower()]), text)
    text = MDY_TEXT_RX.sub(lambda m: _month(m.group(3), _MON[m.group(1).lower()]), text)
    return NUM_DATE_RX.sub(_num_date, text)


def _tidy_removed(out: str) -> str:
    """Remove the spacing and punctuation a removed time (marked _SENTINEL) leaves, around the mark only, so text
    elsewhere ('e.g.,', a double space) is untouched."""
    run_rx = re.compile(r"[ \t]*(?:" + _SENTINEL + r"[ \t]*)+")
    while True:
        m = run_rx.search(out)
        if not m:
            return out
        left, right = out[:m.start()], out[m.end():]
        lp = left.rstrip(" \t")
        if not right:
            out = lp
        elif not lp or lp.endswith("\n"):                     # the time opened the text or a line
            out = left + (right.lstrip(",.;:").lstrip(" \t") if right[0] in ",.;:" else right)
        elif right[0] in ",.;:!?)":
            if lp[-1] in ".!?":                               # "rang. At 0216. He": the stray stop ended the time
                out = lp + right.lstrip(",.;:")
            elif lp[-1] in ",;:" and right[0] in ".!?":       # "The tank, at 14:05. Then"
                out = lp[:-1].rstrip(" \t") + right
            else:
                out = lp + right
        else:
            out = lp + (" " if lp[-1] not in "([{" else "") + right


def strip_times(text: str) -> str:
    """Clock times (HH:MM, with an optional :SS, 'hrs' or am/pm; a bare HHMM after a preposition) removed with the
    'at' that introduced them, and the spacing and punctuation they leave tidied around the gap only."""
    def drop(m):
        if m.group("clock") and not (m.group("sec") or m.group("suf")) and not m.group(0).lower().startswith("at"):
            before = _WORD_BEFORE.search(text, 0, m.start())
            after = _WORD_AFTER.search(text[m.end():])
            near = {x.group(1).lower() for x in (before, after) if x}
            if near & RATIO_WORDS:
                return m.group(0)
        stop = bool(re.search(r"(?i)[ap]\.m\.$", m.group(0))) and re.match(r"\s*$|\s+[A-Z]", text[m.end():])
        return _SENTINEL + ("." if stop else "")

    def drop_hhmm(m):
        unit = _UNIT_AFTER.match(m.string, m.end())
        if unit and unit.group(1).lower() in UNIT_WORDS:
            return m.group(0)
        prep, hhmm = m.group("prep").lower(), m.group("hhmm")
        if 1900 <= int(hhmm) <= 2099 and not prep.startswith("at"):
            return m.group(0)
        if prep.startswith(("about", "around", "approx")) and not hhmm.startswith("0"):
            nxt = _WORD_AFTER.search(m.string[m.end():])
            if nxt and len(nxt.group(1)) > 3 and nxt.group(1).lower().endswith("s") and nxt.group(1).lower() not in _NOT_PLURAL:
                return m.group(0)                             # "about 1200 workers"
        return _SENTINEL

    out = PREP_HHMM_RX.sub(drop_hhmm, TIME_RX.sub(drop, text))
    if _SENTINEL not in out:
        return text
    out = _tidy_removed(out)
    return out.strip() if text == text.strip() else out


_RX_CACHE = {}


def _share_rxs(ctx):
    key = (tuple(ctx.names), tuple(ctx.orgs), tuple(sorted(ctx.singletons.items())))
    if key not in _RX_CACHE:
        hon = "|".join(map(re.escape, _terms()["honorifics"]))
        # An honorific with the name after it, including a name step 1 already masked ("Mr [name]" -> "[name]").
        hon_rx = re.compile(r"\b(?:" + hon + r")\b\.?(?:\s+(?:" + re.escape(NAME_MASK)
                            + r"|[A-Z][\w'’-]+|[A-Z]\.?(?![\w])))+")
        names_rx, orgs_rx = name_pattern(ctx.names, variants=True, skip_role_words=True), name_pattern(ctx.orgs)
        # A singleton role is matched as it reads after the earlier steps, so a role holding a tag still matches.
        singles = {}
        for role, label in ctx.singletons.items():
            singles.setdefault(_mask_ids(role, names_rx, hon_rx, orgs_rx).lower(), label)
        single_rx = (re.compile(r"(?<!\w)(?:" + "|".join(re.escape(r) for r in sorted(singles, key=len, reverse=True))
                                + r")(?!\w)", re.I) if singles else None)
        _RX_CACHE[key] = (names_rx, hon_rx, orgs_rx, single_rx, singles)
    return _RX_CACHE[key]


def _mask_ids(text, names_rx, hon_rx, orgs_rx) -> str:
    if names_rx:
        text = names_rx.sub(NAME_MASK, text)
    text = hon_rx.sub(NAME_MASK, text)
    text = ORG_SUFFIX_RX.sub(ORG_MASK, text)          # first, so "Acme Pumps Ltd" is one mask even when Acme is listed
    if orgs_rx:
        text = orgs_rx.sub(ORG_MASK, text)
    text = re.sub(re.escape(ORG_MASK) + r"(?:\s+" + re.escape(ORG_MASK) + ")+", ORG_MASK, text)
    return TAG_RX.sub(TAG_MASK, text)


def share_text(text: str, ctx) -> str:
    """One string as a --share external|public copy shows it, in this order: names (the names list with its
    variants, and honorific forms) become [name]; listed organisations and company-suffix names [organisation];
    equipment tags [equipment tag]; singleton roles their generalised label; clock times are removed; full dates
    become 'Month YYYY'. Internal mode returns the text unchanged."""
    if ctx.mode not in SHARE_MASKED or not isinstance(text, str) or not text:
        return text
    names_rx, hon_rx, orgs_rx, single_rx, singles = _share_rxs(ctx)
    text = _mask_ids(text, names_rx, hon_rx, orgs_rx)
    if single_rx:
        text = single_rx.sub(lambda m: singles[m.group(0).lower()], text)
    return coarsen_dates(strip_times(text))


def _merge_role(a, b):
    """Two role_map values whose keys masked to the same text: lists are joined without repeats, a scalar keeps the
    first value, and a key only one of them has is kept (A43)."""
    if not (isinstance(a, dict) and isinstance(b, dict)):
        return a
    out = dict(a)
    for k, v in b.items():
        if k not in out:
            out[k] = v
        elif isinstance(out[k], list) and isinstance(v, list):
            out[k] = out[k] + [x for x in v if x not in out[k]]
    return out


def _norm(k) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(k).lower()).strip("_")


def share_doc(obj, ctx, owners=None):
    """A deep copy of obj as a shared copy carries it: share_text on every string outside ID_KEYS; the keys in SHARE_DROP_KEYS and
    reviewer votes' reasons removed; and each `owner` value that owners(value) generalises (a T4 or T5 role, L5-21)
    replaced by that function label. Internal mode returns a plain deep copy."""
    if ctx.mode not in SHARE_MASKED:
        return copy.deepcopy(obj)

    def owner(v):
        if isinstance(v, list):
            return [owner(x) for x in v]
        return (owners(v) or v) if owners and isinstance(v, str) else v

    def walk(v, key=None):
        if isinstance(v, str):
            return share_text(v, ctx)
        if isinstance(v, list):
            if _norm(key) == "votes":
                v = [{k: x for k, x in d.items() if k != "reason"} if isinstance(d, dict) else d for d in v]
            if key == "edges":
                return [dict(walk(d), **{k: copy.deepcopy(d[k]) for k in EDGE_ID_KEYS if k in d})
                        if isinstance(d, dict) else walk(d) for d in v]
            return [walk(x) for x in v]
        if isinstance(v, dict):
            out = {k: copy.deepcopy(x) if k in ID_KEYS else walk(owner(x) if k == "owner" else x, k)
                   for k, x in v.items() if _norm(k) not in SHARE_DROP_KEYS}
            if key in ROLE_KEYED:
                masked = {}
                for k, x in out.items():
                    mk = share_text(k, ctx)
                    masked[mk] = _merge_role(masked[mk], x) if mk in masked else x
                return masked
            return out
        return copy.deepcopy(v)

    return walk(obj)


# ----------------------------------------------------------------------------- scan-names

TEXT_TYPES = (".md", ".txt", ".json", ".csv", ".html", ".mmd", ".py", ".yaml", ".yml")


def _scan_files(path: Path):
    if path.is_dir():
        return [p for p in sorted(path.rglob("*")) if p.is_file() and not any(x.startswith(".git") for x in p.parts)]
    return [path]


_OFFICE_ZIP = (".docx", ".pptx", ".xlsx", ".xlsm")
_MAX_MEMBER = 50 * 1024 * 1024
_XML_BREAK = re.compile(r"<(?:w:(?:tab|br|cr)|a:br)\b[^>]*>")
_XML_PARA_END = re.compile(r"</(?:w|a):p>")
_XML_RUN_TAG = re.compile(r"</?(?:w|a):[^>]*>")
_XML_TAG = re.compile(r"<[^>]+>")
# Parts that can carry a name beyond the cell/body text: properties, comments, people, headers/footers, notes.
_META_PART = re.compile(r"(?i)^docProps/.*\.xml$|(?:^|/)(?:threaded|modern)?comments?[^/]*\.xml$"
                        r"|(?:^|/)modernComment_[^/]*\.xml$|^word/people\.xml$|^ppt/authors\.xml$|^xl/persons/person[^/]*\.xml$"
                        r"|/(?:header|footer)\d*\.xml$|/(?:footnotes|endnotes|notesSlide\d*)\.xml$")
_BODY_PART = re.compile(r"(?i)^(?:word/document|ppt/slides/slide\d+)\.xml$")


_NAME_ATTR = re.compile(r"""(?<![\w.:-])(?:[\w.-]+:)?(?:author|name|displayName|initials|creator|lastModifiedBy)\s*=\s*(?:"([^"]*)"|'([^']*)')""",
                        re.I)


def _xml_attr_names(raw: str) -> str:
    """The values of author, name, displayName, initials, creator and lastModifiedBy attributes (any namespace
    prefix), one per line: comment and people parts often hold a name only in an attribute."""
    return "\n".join(html.unescape(m.group(1) if m.group(1) is not None else m.group(2))
                      for m in _NAME_ATTR.finditer(raw))


def _xml_text(raw: str) -> str:
    """Plain text of an Office XML part. Run text inside a paragraph is joined with no separator, so a name split
    across runs ('Quil' + 'lon Vale') is whole again; a paragraph end is a newline; other tags become a space."""
    raw = _XML_BREAK.sub(" ", raw)
    raw = _XML_PARA_END.sub("\n", raw)
    raw = _XML_RUN_TAG.sub("", raw)
    return html.unescape(_XML_TAG.sub(" ", raw))


def _office_xml_texts(path: Path, unread: list):
    """(location, text) for the metadata, comment, header/footer parts of an Office zip, plus the body of a .docx or
    .pptx (an .xlsx body is read cell by cell). A file that cannot be read, or has an oversize member, goes on
    the unread list so it is never reported as clean."""
    import zipfile
    body = path.suffix.lower() in (".docx", ".pptx")
    try:
        with zipfile.ZipFile(path) as z:
            for zi in z.infolist():
                n = zi.filename
                if not (_META_PART.search(n) or (body and _BODY_PART.search(n))):
                    continue
                with z.open(zi) as fh:                       # the cap counts bytes read, not the size the header declares
                    data = fh.read(_MAX_MEMBER + 1)
                if len(data) > _MAX_MEMBER:
                    print(f"warning: {path}:{n} is over 50 MB and was skipped")
                    unread.append(str(path))
                    continue
                raw = data.decode("utf-8", errors="ignore")
                text = _xml_text(raw)
                if _META_PART.search(n):
                    text += "\n" + _xml_attr_names(raw)
                yield f"{path}:{n}", text
    except Exception as e:
        print(f"warning: {path} could not be read ({type(e).__name__})")
        unread.append(str(path))


def _iter_texts(path: Path, unread: list):
    if path.is_dir():
        for p in _scan_files(path):
            yield from _iter_texts(p, unread)
        return
    ext = path.suffix.lower()
    if ext in (".xlsx", ".xlsm"):
        try:
            openpyxl = _need_openpyxl()
            wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
            cells = [(f"{path}:{ws.title}!{c.coordinate}", c.value) for ws in wb.worksheets
                     for row in ws.iter_rows() for c in row if isinstance(c.value, str)]
        except SystemExit:
            raise
        except Exception as e:
            print(f"warning: {path} could not be read ({type(e).__name__})")
            unread.append(str(path))
            cells = []
        yield from cells
    if ext in _OFFICE_ZIP:
        yield from _office_xml_texts(path, unread)
    elif ext in TEXT_TYPES:
        for i, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            yield f"{path}:{i}", line


def _pdf_meta(path: Path):
    """(location, text) for the Author and Creator lines of a PDF, from pdfinfo. None when pdfinfo is absent,
    False when it failed or timed out."""
    import shutil
    import subprocess
    exe = shutil.which("pdfinfo")
    if not exe:
        return None
    try:
        r = subprocess.run([exe, str(path.resolve())], capture_output=True, text=True, errors="ignore", timeout=30)
    except (subprocess.TimeoutExpired, OSError):
        return False
    if r.returncode != 0:
        return False
    out = []
    for line in r.stdout.splitlines():
        k, _, v = line.partition(":")
        if k.strip() in ("Author", "Creator"):
            out.append((f"{path}:pdf:{k.strip()}", v.strip()))
    return out


def cmd_scan_names(a):
    names = load_names(a.names)
    if not names:
        sys.exit("Names file is empty.")
    scans = [("", name_pattern(names, variants=a.variants, skip_role_words=True))]
    if a.patterns:
        scans += [(f"pattern:{k}", re.compile(v)) for k, v in PATTERNS.items()]
    hits = 0

    def check(loc, text):
        nonlocal hits
        for label, rx in scans:
            for m in rx.finditer(text):
                if label == "pattern:email" and m.group(0).lower().rstrip(".") == BRAND_EMAIL:
                    continue                                    # the brand address every output carries (A49)
                hits += 1
                if hits <= a.show:
                    tag = f" [{label}]" if label else ""
                    print(f"HIT{tag} {loc}: '{m.group(0)}' … {text[max(0, m.start()-50):m.end()+50]!r}")

    pdf_missing = False
    bad = []
    for target in a.paths:
        for loc, text in _iter_texts(Path(target), bad):
            check(loc, text)
        for f in _scan_files(Path(target)):
            if f.suffix.lower() == ".pdf":
                meta = _pdf_meta(f)
                if meta is None:
                    pdf_missing = True
                elif meta is False:
                    print(f"note: pdfinfo failed or timed out on {f}: PDF metadata not checked")
                else:
                    for loc, text in meta:
                        check(loc, text)
    if pdf_missing:
        print("note: pdfinfo not found: PDF metadata not checked")
    print(f"\n{hits} hit(s).")
    readable = TEXT_TYPES + _OFFICE_ZIP
    unread = [str(f) for t in a.paths for f in _scan_files(Path(t)) if f.suffix.lower() not in readable]
    unread += [f for f in dict.fromkeys(bad) if f not in unread]
    if unread:
        print(f"{len(unread)} file(s) not scanned (this type cannot be read), so zero hits does not cover them:")
        for f in unread:
            print(" -", f)
        print("Scan their text instead, e.g. `pdftotext -layout report.pdf report.txt`, then scan report.txt.")
    sys.exit(1 if hits else 2 if unread else 0)
