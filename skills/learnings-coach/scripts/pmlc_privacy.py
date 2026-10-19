"""Privacy core: names, organisations, equipment tags and singleton roles, shared by check-language, scan-names,
make-public-sample and the share tools, plus the --share transforms (share_text, share_doc)."""
from __future__ import annotations

import calendar
import collections
import copy
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TERMS_FILE = HERE.parent / "references" / "lint-terms.json"

# A phone number is a run of digits, spaces and hyphens; it never starts inside another number and never starts
# with a date shape (2020-09-24, 24-09-2020, 24/09/2020), so ISO dates are not phone numbers (ruling X21).
PATTERNS = {"email": r"[\w.+-]+@[\w-]+\.[\w.-]+",
            "phone": r"(?<![\w+-])(?!\d{4}-\d{2}-\d{2}(?!\d))(?!\d{1,2}[-/.]\d{1,2}[-/.]\d{4}(?!\d))"
                     r"\+?\d[\d\s-]{8,}\d(?![\w-])",
            "staff_no": r"(?i)\b(staff|emp(loyee)?|CPF|badge|ID)\s*(no\.?|number|#)\s*\w+"}
# An organisation name ends in a company suffix: "Acme Pumps Ltd".
ORG_SUFFIX_RX = re.compile(r"\b(?:[A-Z][\w&'-]*\s+){1,4}(?:Ltd|Pvt|Inc|GmbH|LLC|Limited)\b\.?")
# A role string that carries an instance identifier: a qualifier word plus a number or letter id ('Gate 3',
# 'CR-2', 'Shift A', 'No. 4'), '#<digits>', or a ' - X' / '(X)' suffix that contains a digit. A bare 'control room',
# 'shift', '(owner)' or '- Operations' does not identify one person.
QUALIFIER_RX = re.compile(r"\b(?i:post|gate|shift|grade|no\.?|desk|cabin|CR|control room)[\s-]*(?:\d+|[A-Z]\b)"
                          r"|#\s*\d|\s-\s[^()]*\d[^()]*$|\([^()]*\d[^()]*\)\s*$")
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


def name_variants(name: str, skip_role_words=False) -> list:
    """The ways a person is named in text: the full name as given, surname only, initial plus surname, and an
    honorific plus surname for each honorific in lint-terms.json. 'Shri R. K. Sharma' gives 'Sharma', 'R. Sharma',
    'R K Sharma', 'Shri Sharma', 'Shri. Sharma' and so on. A line with a digit (a staff ID) has no variants.
    skip_role_words=True (share masking and scan-names --variants, M1) leaves out a one-word variant that is a role
    noun or a lint vocabulary word ('Officer', 'Field'), so it never masks a role; --redact keeps it and warns (X17)."""
    name = " ".join(name.split())
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
    be followed directly by the next token, so 'R. K. Sharma' also matches 'R.K. Sharma' and 'R K Sharma'."""
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
    'Sharma' does not match inside 'Sharmaji' and a space matches any run of whitespace. variants=True adds the
    name_variants of each name (skip_role_words: see name_variants)."""
    xs = []
    for n in names:
        for v in (name_variants(n, skip_role_words) if variants else [" ".join(n.split())]):
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
        reason = "qualifier" if QUALIFIER_RX.search(r) else "single-holder" if r in sole else None
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
TIME_RX = re.compile(r"(?:\bat\s+(?:about\s+|around\s+|approximately\s+)?)?(?<![\w:.])"
                     r"(?:(?P<clock>(?:[01]?\d|2[0-3]):[0-5]\d)(?P<sec>:[0-5]\d)?"
                     r"(?P<suf>\s*(?:hrs?\b|hours?\b|[ap]\.?m\b\.?))?(?![\d:])"
                     r"|(?:[01]\d|2[0-3])[0-5]\d\s*(?:hrs?|hours?)\b"
                     r"|(?:[01]?\d|2[0-3])\.[0-5]\d\s*(?:hrs\b|[ap]\.?m\b\.?))", re.I)
# A bare HHMM (0000-2359) after a preposition, which goes with it: "At 0216", "at about 0300", "from 0200 until 0415".
# Years are kept: after about, around, approximately, by, from, until or till, 1900-2099 reads as a year ("from 2017",
# "by 2020"); only "at" takes those as times ("at 1930"). "in" and "since" are never followed by a time. A following
# unit ("at 1500 rpm", "about 1200 m") makes it a quantity, also kept.
PREP_HHMM_RX = re.compile(r"\b(?P<prep>at\s+(?:about\s+|around\s+|approximately\s+|approx\.\s*)?"
                          r"|(?:about|around|approximately|by|from|until|till)\s+|approx\.\s*)"
                          r"(?P<hhmm>(?:[01]\d|2[0-3])[0-5]\d)(?:\s*[-–]\s*(?:[01]\d|2[0-3])[0-5]\d)?(?![-/:]|[.,]\d|\w)", re.I)
_UNIT_AFTER = re.compile(r"\s*([A-Za-z]+\d?|%|°[CF]?)(?!\w)")
UNIT_WORDS = {"rpm", "kpa", "mpa", "pa", "bar", "barg", "psi", "psig", "mm", "cm", "m", "km", "kg", "g", "t", "te",
              "tonnes", "tons", "l", "litres", "liters", "ml", "m3", "nm3", "scm", "ppm", "kw", "mw", "w", "v", "kv",
              "a", "hz", "metres", "meters", "feet", "ft", "units", "people", "%", "°", "°c", "c", "k"}
RATIO_WORDS = {"ratio", "ratios", "slope", "slopes", "scale", "odds", "mix", "mixture", "dilution", "dilutions"}
_WORD_BEFORE = re.compile(r"([A-Za-z]+)\W*(?:\bof\W*)?$")      # "ratio 1:10" and "a ratio of 1:10"
_WORD_AFTER = re.compile(r"^\W*([A-Za-z]+)")
ISO_DATE_RX = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})(?:[T ](?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d(?:\.\d+)?)?"
                         r"(?:Z|[+-]\d{2}:?\d{2})?)?(?![\d-])")
DMY_TEXT_RX = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?[ -]" + _MON_RX + r",?[ -](\d{4})\b", re.I)
MDY_TEXT_RX = re.compile(r"\b" + _MON_RX + r" (\d{1,2})(?:st|nd|rd|th)?,? (\d{4})\b", re.I)
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
    """ISO dates and date-times, 'D Month YYYY', 'Month D, YYYY' and D/M/YYYY become 'Month YYYY'."""
    text = ISO_DATE_RX.sub(lambda m: _month(m.group(1), m.group(2)) or m.group(0), text)
    text = DMY_TEXT_RX.sub(lambda m: _month(m.group(3), _MON[m.group(2).lower()]), text)
    text = MDY_TEXT_RX.sub(lambda m: _month(m.group(3), _MON[m.group(1).lower()]), text)
    return NUM_DATE_RX.sub(_num_date, text)


def strip_times(text: str) -> str:
    """Clock times (HH:MM, with an optional :SS and 'hrs') removed, and the spacing they leave tidied."""
    def drop(m):
        if m.group("clock") and not (m.group("sec") or m.group("suf")):
            before = _WORD_BEFORE.search(text, 0, m.start())
            after = _WORD_AFTER.search(text[m.end():])
            near = {x.group(1).lower() for x in (before, after) if x}
            if near & RATIO_WORDS:
                return m.group(0)
        return ""

    def drop_hhmm(m):
        unit = _UNIT_AFTER.match(m.string, m.end())
        if unit and unit.group(1).lower() in UNIT_WORDS:
            return m.group(0)
        if 1900 <= int(m.group("hhmm")) <= 2099 and not m.group("prep").lower().startswith("at"):
            return m.group(0)
        return ""

    out = PREP_HHMM_RX.sub(drop_hhmm, TIME_RX.sub(drop, text))
    if out == text:
        return text
    out = re.sub(r"[ \t]{2,}", " ", out)
    out = re.sub(r"[ \t]+([,.;:)])", r"\1", out)
    if not re.match(r"\s*[,.;:]", text):                 # "At 0216. He ..." reads "He ...", not ". He ..."
        out = re.sub(r"^(\s*)[,.;:]+[ \t]*", r"\1", out)
    if ".." not in text:                                    # "rang. At 0216. He" reads "rang. He"
        out = re.sub(r"(?<!\.)([.!?])[ \t]*[.,;:](?!\.)", r"\1", out)
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
            return {share_text(k, ctx): x for k, x in out.items()} if key in ROLE_KEYED else out
        return copy.deepcopy(v)

    return walk(obj)
