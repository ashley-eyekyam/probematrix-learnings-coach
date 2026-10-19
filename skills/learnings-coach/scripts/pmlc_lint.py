"""check-language: the grounding and just-culture lint (rules JC1-JC12) over a pack or a Learnings Register.
`pmlc.py check-language`, `check-pack` and `check-register` call into this module. Terms: references/lint-terms.json."""
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

import pmlc as core
import pmlc_privacy as privacy

STATUS_PHRASE = core.STATUS_PHRASE
TERMS_FILE = core.REFS / "lint-terms.json"
Hit = collections.namedtuple("Hit", "rule severity path match hint")
SKIP_KEYS = {"kind", "id", "cites", "supporting_cites", "row_cites", "row_supporting_cites", "lr_id", "ml_id",
             "finding_ids", "evidence_ids", "hfacs_level", "performance_mode", "handling", "scope", "lint_ok"}
RETRAIN_ONLY = {"training", "administrative"}
# Targets and measures are the coach's proposals, not claims about the incident, so JC8 does not check them.
JC8_SKIP_FIELDS = {"leading_indicator", "indicator", "measure", "deterioration"}
CAP_PAIR_RX = re.compile(r"(?<![\w'’-])(?=([A-Z][a-z]+(?:['’-][A-Za-z]+)*) ([A-Z][a-z]+(?:['’-][A-Za-z]+)*)(?![\w'’-]))")
WORD_RX = re.compile(r"[A-Za-z]+")
EXTERNAL = ("external", "public")
_TERMS = None


def load_terms() -> dict:
    global _TERMS
    if _TERMS is None:
        _TERMS = json.loads(TERMS_FILE.read_text(encoding="utf-8"))
    return _TERMS


def share_mode(doc, share=None) -> str:
    """P2-2: --share when given, otherwise handling.classification; external and public give external rules."""
    if share is None:
        h = doc.get("handling") if isinstance(doc, dict) else None
        share = h.get("classification") if isinstance(h, dict) else None
    return "external" if share in EXTERNAL else "internal"


def _words(s) -> set:
    return {x.lower() for x in WORD_RX.findall(s or "")}


def _vocabulary(w, terms) -> set:
    """P2-4: words that exempt a pair of capitalised tokens from JC1."""
    v = {x.lower() for x in terms["name_vocabulary"] + terms["role_nouns"]}
    hon = re.compile(r"\b(?:" + "|".join(map(re.escape, terms["honorifics"])) + r")\b\.?\s")
    cl = w.get("clusters", {})
    unresolved = set(cl.get("unresolved_roles", []))
    for r in cl.get("role_map", {}):
        if r not in unresolved and not hon.search(r):         # a role string that is a name exempts nothing
            v |= _words(r)
    tax = cl.get("taxonomy", {})
    for k in ("entities", "tiers", "relations"):
        for x in (tax.get(k) or {}).values():
            v |= _words(x if isinstance(x, str) else x.get("name", "") if isinstance(x, dict) else "")
    for f in w.get("findings", []):
        for k in ("name", "level_name", "category", "subcategory"):
            v |= _words(f.get(k))
    fields = w.get("incident", {}).get("fields", {})
    for k in ("Incident Title", "Location"):
        v |= _words(fields.get(k))
    return v


def _strings(v):
    if isinstance(v, (str, int, float)) and not isinstance(v, bool):
        yield str(v)
    elif isinstance(v, (list, tuple)):
        for x in v:
            yield from _strings(x)
    elif isinstance(v, dict):
        for x in v.values():
            yield from _strings(x)


def _record_texts(w) -> dict:
    """ID -> all text of that finding or evidence record, for JC8."""
    out = {f["id"]: " ".join(_strings(f)) for f in w.get("findings", [])}
    out.update({eid: " ".join(_strings(e)) for eid, e in (w.get("evidence") or {}).items()})
    return out


class _Ctx:
    def __init__(self, w, kind, share, names, orgs):
        t = load_terms()
        self.t, self.w, self.kind, self.share = t, w, kind, share
        self.hits = []
        self.rx = {}
        for rule, spec in t["rules"].items():
            fl = 0 if spec.get("case") == "sensitive" else re.I
            self.rx[rule] = [re.compile(p, fl) for p in spec.get("patterns", [])]
        hon = "|".join(map(re.escape, t["honorifics"]))
        self.hon_rx = re.compile(r"\b(?:" + hon + r")\b\.?(?:\s+(?:[A-Z][\w'’-]+|[A-Z]\.?(?![\w])))+")
        self.names_rx = self._list_rx(names)
        self.orgs_rx = self._list_rx(orgs)
        self.allow = [re.compile(r"\b" + re.escape(a) + r"\b", re.I) for a in t.get("allow", [])]
        self.vocab = _vocabulary(w, t)
        single = getattr(privacy, "load_singletons", None)
        self.singles_rx = self._list_rx(list(single(w)) if single else [])
        self.records = None
        self.levels = {f["id"]: f.get("level") for f in w.get("findings", [])}

    @staticmethod
    def _list_rx(xs):
        xs = [x for x in xs if x]
        if not xs:
            return None
        return re.compile(r"(?<!\w)(?:" + "|".join(re.escape(x) for x in sorted(xs, key=len, reverse=True)) + r")(?!\w)",
                          re.I)

    def hit(self, rule, path, match, severity=None, quiet=()):
        if rule in quiet:
            return
        spec = self.t["rules"][rule]
        self.hits.append(Hit(rule, severity or spec["severity"], path, match, spec["hint"]))

    def allowed(self, s, m):
        return any(a.start() <= m.start() and m.end() <= a.end() for rx in self.allow for a in rx.finditer(s))

    def number_known(self, num, ids):
        if self.records is None:
            self.records = _record_texts(self.w)
        rx = re.compile(r"(?<![\d.])" + re.escape(num) + r"(?!\.?\d)")
        return any(rx.search(self.records.get(x, "")) for x in ids)


def _t1(doc) -> bool:
    sc = doc.get("scope") if isinstance(doc, dict) else None
    return isinstance(sc, dict) and sc.get("tiers") == ["T1"]


def _jc1(c, s, path, quiet):
    spans = []
    for rx in (c.hon_rx, c.names_rx):
        for m in rx.finditer(s) if rx else ():
            spans.append((m.start(), m.end()))
            c.hit("JC1", path, m.group(0).strip(), quiet=quiet)
    for m in CAP_PAIR_RX.finditer(s):
        a, b = m.group(1), m.group(2)
        st, en = m.start(), m.start() + len(a) + 1 + len(b)
        if any(x <= st < y or x < en <= y for x, y in spans):
            continue
        if not any(tok.lower() in c.vocab or re.sub("s$", "", tok.lower()) in c.vocab for tok in (a, b)):
            c.hit("JC1", path, f"{a} {b}", quiet=quiet)


def _jc9(c, s, path, quiet, ext):
    seen = []
    for m in [*(c.orgs_rx.finditer(s) if c.orgs_rx else ()), *(m for rx in c.rx["JC9"] for m in rx.finditer(s))]:
        if not any(x < m.end() and m.start() < y for x, y in seen):     # one hit per organisation name
            seen.append((m.start(), m.end()))
            c.hit("JC9", path, m.group(0).strip(), severity="error" if ext else "warning", quiet=quiet)


def _lint_string(c, s, path, ids, quiet, t1):
    ext = c.share == "external"
    _jc1(c, s, path, quiet)
    for rule in ("JC2", "JC3", "JC4", "JC5", "JC12"):
        for rx in c.rx[rule]:
            for m in rx.finditer(s):
                if not c.allowed(s, m):
                    sev = "error" if rule == "JC12" and t1 else None
                    c.hit(rule, path, m.group(0), severity=sev, quiet=quiet)
    if c.singles_rx:
        for m in c.singles_rx.finditer(s):
            c.hit("JC7", path, m.group(0), severity="error" if ext else "warning", quiet=quiet)
    for rx in c.rx["JC8"] if re.sub(r"\[\d+\]$", "", path).rsplit(".", 1)[-1] not in JC8_SKIP_FIELDS else ():
        for m in rx.finditer(s):
            num = re.match(r"\d+(?:\.\d+)?", m.group(0)).group(0)
            if not c.number_known(num, ids):
                c.hit("JC8", path, m.group(0), quiet=quiet)
    _jc9(c, s, path, quiet, ext)
    if ext:
        for m in privacy.TAG_RX.finditer(s):
            c.hit("JC10", path, m.group(0), quiet=quiet)


def _lint_ok(c, d, path):
    """(rules an item's lint_ok suppresses, problem hits, [(path, reason)]): {rule, reason}, or a list of them; an
    empty reason or an unknown rule suppresses nothing and is an error."""
    ok, rules, bad, reasons = d.get("lint_ok"), set(), [], []
    for i, x in enumerate(ok if isinstance(ok, list) else [] if ok is None else [ok]):
        p = f"{path}.lint_ok" + (f"[{i}]" if isinstance(ok, list) else "")
        rule = x.get("rule") if isinstance(x, dict) else None
        reason = x.get("reason") if isinstance(x, dict) else None
        if not isinstance(rule, str) or rule not in c.t["rules"]:
            bad.append(Hit("lint_ok", "error", f"{p}.rule", str(rule), "name one rule, JC1 to JC12"))
        elif not (isinstance(reason, str) and reason.strip()):
            bad.append(Hit("lint_ok", "error", f"{p}.reason", "", "give the reason the rule does not apply here"))
        else:
            rules.add(rule)
            reasons.append((f"{p}.reason", reason))
    return rules, bad, reasons


def _suppressed(c, d, path, quiet) -> frozenset:
    """The rules this dict's lint_ok adds to quiet. The reason is rendered on the page, so it is checked for names
    (JC1) and organisations (JC9) itself, and no lint_ok quiets that check (ruling X14)."""
    rules, bad, reasons = _lint_ok(c, d, path)
    c.hits += bad
    for rp, reason in reasons:
        _jc1(c, reason, rp, ())
        _jc9(c, reason, rp, (), c.share == "external")
    return quiet | frozenset(rules)


def _ids_of(d) -> list:
    """Finding and Evidence IDs a pack item, bottom-line entry or register entry cites or names."""
    if not isinstance(d, dict):
        return []
    out = []
    for k in ("cites", "supporting_cites", "finding_ids", "evidence_ids", "row_cites", "row_supporting_cites"):
        v = d.get(k)
        for x in (v if isinstance(v, list) else []):
            out += x if isinstance(x, list) else [x]
    out += [x for _, x in _walk_ids(d)]
    return [x for x in out if isinstance(x, str)]


def _walk_ids(v, path=""):
    if isinstance(v, str):
        for m in re.finditer(r"\b(FND-[0-9A-Za-z]{4,}|EVD-\d{3,})\b", v):
            yield path, m.group(1)
    elif isinstance(v, list):
        for x in v:
            yield from _walk_ids(x, path)
    elif isinstance(v, dict):
        for k, x in v.items():
            if k != "lint_ok":
                yield from _walk_ids(x, path)


def _walk(c, v, path, ids, quiet, t1):
    if isinstance(v, str):
        _lint_string(c, v, path, ids, quiet, t1)
    elif isinstance(v, list):
        for i, x in enumerate(v):
            _walk(c, x, f"{path}[{i}]", ids, quiet, t1)
    elif isinstance(v, dict):
        quiet = _suppressed(c, v, path, quiet)
        for k, x in v.items():
            if k not in SKIP_KEYS:
                _walk(c, x, f"{path}.{k}", ids, quiet, t1)


def _units(doc, kind):
    """(path, unit) for each item, bottom-line entry or register entry: the scope of cites and of lint_ok."""
    if kind == "register":
        es = doc.get("entries") if isinstance(doc, dict) else doc
        base = "$.entries" if isinstance(doc, dict) else "$"
        return [(f"{base}[{i}]", e) for i, e in enumerate(es if isinstance(es, list) else [])]
    if not isinstance(doc, dict):
        return []
    bl = doc.get("bottom_line") if isinstance(doc.get("bottom_line"), list) else []
    out = [(f"$.bottom_line[{i}]", e) for i, e in enumerate(bl)]
    for si, s in enumerate(doc.get("sections") if isinstance(doc.get("sections"), list) else []):
        items = s.get("items") if isinstance(s, dict) else None
        out += [(f"$.sections[{si}].items[{ii}]", it) for ii, it in enumerate(items if isinstance(items, list) else [])]
    return out


def _retrain_only(c, unit, tiers, path, t1):
    """JC6: every hoc_tier is training or administrative while a cited finding sits at level 3 or 4. An
    administrative change that is itself the system fix is cleared with the item's lint_ok."""
    tiers = [core.norm_hoc(x) for x in tiers]
    if not tiers or any(x not in RETRAIN_ONLY for x in tiers):
        return
    if any(c.levels.get(x) in (3, 4) for x in _ids_of(unit)):
        c.hit("JC6", path, ", ".join(dict.fromkeys(tiers)), severity="error" if t1 else None,
              quiet=_lint_ok(c, unit, path)[0])


def lint(doc, w, *, kind: str, share: str | None = None, names=(), orgs=()) -> list:
    """Every JC1-JC12 hit in a pack (kind "pack") or a Learnings Register (kind "register"), as Hit tuples.
    share is internal, external or public; None reads handling.classification (P2-2)."""
    c = _Ctx(w, kind, share_mode(doc, share), names, orgs)
    t1 = kind == "pack" and _t1(doc)
    units = _units(doc, kind)
    unit_ids = {id(u) for _, u in units}
    all_ids = [x for _, u in units for x in _ids_of(u)]

    def walk_top(v, path, quiet):
        """Walk outside the units with every cited ID; walk each unit with its own."""
        if isinstance(v, (dict, list)) and id(v) in unit_ids:
            _walk(c, v, path, _ids_of(v) or all_ids, quiet, t1)
        elif isinstance(v, list):
            for i, x in enumerate(v):
                walk_top(x, f"{path}[{i}]", quiet)
        elif isinstance(v, dict):
            for k, x in v.items():
                if k not in SKIP_KEYS:
                    walk_top(x, f"{path}.{k}", quiet)
        else:
            _walk(c, v, path, all_ids, quiet, t1)

    walk_top(doc, "$", frozenset())
    for path, u in units:
        if not isinstance(u, dict):
            continue
        if kind == "pack" and u.get("kind") in ("recommendation", "barrier") and isinstance(u.get("hoc_tier"), str):
            _retrain_only(c, u, [u["hoc_tier"]], f"{path}.hoc_tier", t1)
        elif kind == "register" and isinstance(u.get("recommendations"), list):
            recs = [r for r in u["recommendations"] if isinstance(r, dict)]
            if recs and all(isinstance(r.get("hoc_tier"), str) for r in recs):
                _retrain_only(c, u, [r["hoc_tier"] for r in recs], f"{path}.recommendations", False)
    status = doc.get("status") if isinstance(doc, dict) else None
    if not (isinstance(status, str) and STATUS_PHRASE in status):
        c.hit("JC11", "$.status", "", severity="error" if kind == "pack" else "warning")
    return c.hits


def format_hits(hits) -> str:
    lines = [f'{h.severity.upper()} {h.rule} {h.path}: "{h.match}": {h.hint}' for h in hits]
    e = sum(h.severity == "error" for h in hits)
    lines.append(f"check-language: {e} errors, {len(hits) - e} warnings")
    return "\n".join(lines)


def as_problem(h) -> str:
    """A hit as a check-pack or check-register line, with the path written without the leading '$.'."""
    p = h.path[2:] if h.path.startswith("$.") else h.path
    if h.rule == "JC11":
        return f'{p}: must contain "{STATUS_PHRASE}" (JC11)'
    return f'{p}: {h.rule} "{h.match}": {h.hint}'


def doc_kind(doc) -> str:
    return "register" if isinstance(doc, list) or (isinstance(doc, dict) and "entries" in doc) else "pack"


def cli_options(a) -> dict:
    """names, orgs and share from --names, --orgs and --share (or PMLC_NAMES and PMLC_ORGS)."""
    return {"names": privacy.load_names(getattr(a, "names", None)), "orgs": privacy.load_orgs(getattr(a, "orgs", None)),
            "share": getattr(a, "share", None)}


def cmd_check_language(a):
    w = core.load_ws(a.ws)
    try:
        doc = json.loads(Path(a.json).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as e:
        sys.exit(f"(file): cannot read {a.json} as UTF-8 JSON ({e.__class__.__name__})")
    except json.JSONDecodeError as e:
        sys.exit(f"(json): invalid JSON at line {e.lineno} column {e.colno}: {e.msg}")
    hits = lint(doc, w, kind=doc_kind(doc), **cli_options(a))
    print(format_hits(hits))
    sys.exit(1 if any(h.severity == "error" for h in hits) else 0)
