"""Privacy core: names, organisations, equipment tags and singleton roles, shared by check-language, scan-names,
make-public-sample and the share tools. The share transforms follow in a later task."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
TERMS_FILE = HERE.parent / "references" / "lint-terms.json"

PATTERNS = {"email": r"[\w.+-]+@[\w-]+\.[\w.-]+", "phone": r"\+?\d[\d\s-]{8,}\d",
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

# Equipment tags such as AO-101 or PSV12A: letters then digits. Finding, Evidence, LR and ML IDs are not tags.
TAG_RX = re.compile(r"\b(?!(?:FND|EVD|LR|ML)-)[A-Z]{1,5}-?\d{2,6}[A-Z]?\b")


def _list_file(path, env) -> list:
    """Stripped lines of a text file, skipping blank lines and lines starting with '#'. A staff ID is written
    'ID #4471', so it is kept. The path falls back to the environment variable env; neither gives []."""
    p = path or os.environ.get(env)
    if not p:
        return []
    out = []
    for line in Path(p).read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#") and s not in out:
            out.append(s)
    return out


def load_names(path=None) -> list:
    """Names from a names file (one per line), falling back to PMLC_NAMES."""
    return _list_file(path, "PMLC_NAMES")


def load_orgs(path=None) -> list:
    """Organisation names from an orgs file (one per line), falling back to PMLC_ORGS."""
    return _list_file(path, "PMLC_ORGS")


def _terms() -> dict:
    return json.loads(TERMS_FILE.read_text(encoding="utf-8"))


def name_variants(name: str) -> list:
    """The ways a person is named in text: the full name as given, surname only, initial plus surname, and an
    honorific plus surname for each honorific in lint-terms.json. 'Shri R. K. Sharma' gives 'Sharma', 'R. Sharma',
    'R K Sharma', 'Shri Sharma', 'Shri. Sharma' and so on. A line with a digit (a staff ID) has no variants."""
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
    for f in forms:
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


def name_pattern(names, variants=False):
    """One case-insensitive regex for a list of names (None for an empty list), bounded by (?<!\\w) and (?!\\w) so
    'Sharma' does not match inside 'Sharmaji' and a space matches any run of whitespace. variants=True adds the
    name_variants of each name."""
    xs = []
    for n in names:
        for v in (name_variants(n) if variants else [" ".join(n.split())]):
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
