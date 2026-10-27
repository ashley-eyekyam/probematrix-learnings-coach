"""Per-skill pack profiles (references/pack-profiles.json): which sections a pack has, the kinds that fill them,
how many items of each, the bottom-line count, word limits, the scope keys it must set and named rules. check-pack
reports a violation as a warning, and as a problem under --strict (Ruling P3-5).

Profile sections: each entry {"id", "kinds", "min", "max"} counts the items of its kinds in every pack section whose
id it matches. The id is exact, or a glob ("*", "s2-*", "t[1-5]") for sections the skill names per function, pair or
tier; a section takes the exact entries when there are any, otherwise the glob entries. Several entries may share an
id (one per kind with its own count). An entry with min 1 or more makes its section required; min 0 makes it
optional. A max of 99 means the skill states no count. The kinds a section may hold are the union of its entries'
kinds.

Named rules (P5-6): no-owner-due makes a non-empty owner or by_when on any item a problem even without --strict
(D7: the organisation sets owners and due dates); banner:<key> needs a para whose text equals BANNERS[key] exactly;
knowable-then needs knowable_then on every event of every timeline item. A profile's lint_errors (P5-5) lists the
JC rules that check-pack and check-language report as errors for that pack.

The 9M rules (Task 12, spec §7.3): nine-m-overview needs the nine-m-overview table with 9 rows, M1 to M9 in order,
and each M either as a section m<n> with a cited learning or as a row of the not-relevant table with a reason;
nine-m-cites flags a cite in a section m<n> that the workspace's nine_m_seed.json does not link to that M; m1-balance
flags M1 holding the most recommendations while another M has more level 3-4 findings in the seed (M1 is not the
people M). banner:nine-m-demo applies only when the workspace's nine_m_session.json is a replay (OD5-1).

The Phase 6 rules (Task 1): grade-source warns when grade or grade_source is missing, even under --strict (OD6-1:
advice()); alert-priority-1 (with a register), leading-lagging and inferred-banner are problems even without
--strict (hard()); needs-are-questions follows --strict, as the profile's kind check does.

A profile may set "pptx_slides": 1 (Task 2): the pptx renderer then puts every section on one content slide."""
from __future__ import annotations

import fnmatch
import json
import re

from ..util import DUE_DATE_RX, REFS

PROFILES_FILE = REFS / "pack-profiles.json"
DOSSIER_RX = re.compile(r"^dossier-F\d+[a-z]?$")
RULES = ("triplets", "assessment-answer", "follow-up-per-top", "same-sections-as:", "no-owner-due", "banner:",
         "knowable-then", "nine-m-overview", "nine-m-cites", "m1-balance",
         "grade-source", "alert-priority-1", "leading-lagging", "needs-are-questions", "inferred-banner")
NINE_M_CODES = tuple(f"M{i}" for i in range(1, 10))     # as pmlc_lib.ninem (not imported: it reads the workspace)
# Fixed copy (Phase 5, verbatim): a pack meets banner:<key> only with a para whose text equals the value exactly
BANNERS = {
    "crosswalk": "Aid to assurance, not a compliance opinion.",
    "people": "Learnings about systems, not individuals' records.",
    "risk": "Proposals for the risk owner to assess: no loss estimates and no rating decisions.",
    "evidence": "This scorecard shows where more evidence would strengthen confidence. It does not grade the "
                "investigation team.",
    "profile-limits": "For one incident these counts describe this investigation only. They are not rates, trends or "
                      "a benchmark.",
    "nine-m-demo": "Answers chosen for demonstration, not by the organisation.",
    # Phase 6 (verbatim)
    "alert-review-copy": "Review copy: not for distribution outside the organisation until it is approved and shared "
                         "with --share external.",
    "cihh": "A self-assessment for each site. Results show coverage and conditions, never a ranking of sites.",
    "learning-team": "The team supplies the answers. These are questions, not findings about people.",
    "restorative": "The export holds no information about the people affected. Every need here is a question to ask, "
                   "or the organisation's own answer.",
    "accimap-inferred": "Placements above the company level are inferred from codes and departments. A person confirms "
                        "them before this map is shared.",
    "effectiveness": "The organisation sets owners, dates and statuses. This plan sets out what to check and when, "
                     "counted from adoption.",
}
NEEDS_ARE_QUESTIONS = "needs are asked, never inferred"
NO_OWNER_DUE = "owner and due dates are set by the organisation, not in this pack"
NO_OWNER_DUE_DATE = ("names a date or a deadline; owner and due dates are set by the organisation, not in this pack: "
                     "take the date out")
DEFAULT_COVERAGE_FLOOR = 0.25
NO_LIMIT = 99                     # a max of 99 means the SKILL.md states no count
_ID_SPLIT = re.compile(r"[\s,;]+")
_cache: dict = {}


def load(path=None) -> dict:
    """The profiles, keyed by pack name (a dossier's key is its fixture name, dossier-F02)."""
    p = path or PROFILES_FILE
    key = str(p)
    if key not in _cache:
        _cache[key] = json.loads(p.read_text(encoding="utf-8"))
    return _cache[key]


def profile_for(name, profiles=None):
    """The profile for a pack name, or None. Every dossier-F<nn> pack shares the one dossier profile."""
    profiles = load() if profiles is None else profiles
    if not isinstance(name, str):
        return None
    if name in profiles:
        return profiles[name]
    if DOSSIER_RX.fullmatch(name):
        return next((v for k, v in profiles.items() if DOSSIER_RX.fullmatch(k)), None)
    return None


def coverage_floor(profile) -> float:
    v = profile.get("coverage_floor") if isinstance(profile, dict) else None
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else DEFAULT_COVERAGE_FLOOR


def _is_glob(x) -> bool:
    return any(c in x for c in "*?[")


def _entries_for(sid, entries) -> list:
    exact = [e for e in entries if e["id"] == sid]
    return exact or [e for e in entries if _is_glob(e["id"]) and fnmatch.fnmatchcase(sid, e["id"])]


def _range(e) -> str:
    if e["max"] >= NO_LIMIT:
        return f"at least {e['min']}"
    return str(e["min"]) if e["min"] == e["max"] else f"{e['min']}-{e['max']}"


def _words(it) -> int:
    n = 0
    for k, v in it.items():
        if k in ("kind", "id", "cites", "supporting_cites", "evidence_strength", "group", "lint_ok"):
            continue
        for x in (v if isinstance(v, list) else [v]):
            if isinstance(x, str):
                n += len(x.split())
    return n


def _items(pack):
    for s in pack.get("sections") or []:
        if isinstance(s, dict) and isinstance(s.get("items"), list):
            for n, it in enumerate(s["items"], 1):
                if isinstance(it, dict):
                    yield s, n, it


def _item_name(s, n, it) -> str:
    return it.get("id") if isinstance(it.get("id"), str) else f"{s.get('id')}-{n}"


def _check_sections(pack, profile, out):
    entries = [e for e in profile.get("sections") or [] if isinstance(e, dict) and isinstance(e.get("id"), str)]
    secs = [s for s in pack.get("sections") or [] if isinstance(s, dict) and isinstance(s.get("id"), str)]
    used = set()
    for s in secs:
        sid = s["id"]
        items = [it for it in s.get("items") if isinstance(it, dict) and isinstance(it.get("kind"), str)] \
            if isinstance(s.get("items"), list) else []
        mine = _entries_for(sid, entries)
        if not mine:
            out.append(f"section {sid}: not a section of the {pack.get('pack')} profile")
            continue
        used.update(id(e) for e in mine)
        allowed = {k for e in mine for k in e.get("kinds") or []}
        for k in dict.fromkeys(it.get("kind") for it in items if it.get("kind") not in allowed):
            out.append(f"section {sid}: {k} items do not belong here (expected {', '.join(sorted(allowed))})")
        for e in mine:
            n = sum(1 for it in items if it.get("kind") in (e.get("kinds") or []))
            if not e["min"] <= n <= e["max"]:
                out.append(f"section {sid}: {n} {'/'.join(e['kinds'])} items, expected {_range(e)}")
    for e in entries:
        if e.get("min", 0) >= 1 and id(e) not in used:
            what = f"a section matching {e['id']}" if _is_glob(e["id"]) else f"section {e['id']}"
            out.append(f"{what}: missing ({'/'.join(e['kinds'])} items, expected {_range(e)})")


def _check_triplets(pack, out):
    groups: dict = {}
    for s, n, it in _items(pack):
        if it.get("kind") in ("learning", "barrier", "recommendation") and isinstance(it["kind"], str):
            g = it.get("group")
            if not isinstance(g, str) or not g.strip():
                out.append(f"{_item_name(s, n, it)}: a {it['kind']} needs a group shared with its learning, "
                           "barrier and recommendation")
                continue
            groups.setdefault(g, set()).add(it["kind"])
    for g, kinds in groups.items():
        miss = [k for k in ("learning", "barrier", "recommendation") if k not in kinds]
        if miss:
            out.append(f"group {g}: needs a learning, a barrier and a recommendation (missing {', '.join(miss)})")


def _check_assessment(pack, out):
    for s, n, it in _items(pack):
        if it.get("kind") == "question":
            if not isinstance(it.get("answer"), str) or not it["answer"].strip():
                out.append(f"{_item_name(s, n, it)}: an assessment question needs an answer (the answer key)")
            if not (isinstance(it.get("cites"), list) and it["cites"]):
                out.append(f"{_item_name(s, n, it)}: an assessment question needs cites (the finding it tests)")


def top_rated_of(w, ids) -> list:
    """The findings among ids with the highest rating any of them has (top-rated within the pack's scope, L6-19)."""
    R = {f["id"]: (f.get("rating") or 0) for f in w["findings"]}
    top = max((R.get(x, 0) for x in ids), default=0)
    return [x for x in ids if top and R.get(x, 0) == top]


def _check_follow_up_per_top(pack, top, out):
    if top is None:
        return
    rows = [r for _, _, it in _items(pack) if it.get("id") == "follow-up" and isinstance(it.get("rows"), list)
            for r in it["rows"]]
    have = {x for r in rows if isinstance(r, list) and r and isinstance(r[0], str) for x in _ID_SPLIT.split(r[0]) if x}
    miss = [x for x in top if x not in have]
    if miss:
        out.append(f"follow-up: no row for top-rated finding(s) {', '.join(miss)}")


def _check_same_sections(pack, other, profiles, out):
    ref = profiles.get(other)
    if not isinstance(ref, dict):
        out.append(f"rules: same-sections-as:{other} names no profile")
        return
    want = list(dict.fromkeys(e["id"] for e in ref.get("sections") or [] if isinstance(e, dict)))
    got = [s.get("id") for s in pack.get("sections") or [] if isinstance(s, dict)]
    if got != want:
        out.append(f"sections: must be the same sections as {other} ({', '.join(want)}), got {', '.join(map(str, got))}")


def _check_max_words(pack, profile, out):
    lim = profile.get("max_words")
    if isinstance(lim, int) and not isinstance(lim, bool):
        from ..render.fields import pack_words          # imported late: render.fields imports pack.schema
        n = pack_words(pack)
        if n > lim:
            out.append(f"pack has {n} words; the {pack.get('pack')} profile allows {lim}")


def _check_banner(pack, key, out):
    want = BANNERS.get(key)
    if want is None:
        out.append(f"rules: banner:{key} names no banner (known: {', '.join(sorted(BANNERS))})")
    elif not any(it.get("kind") == "para" and it.get("text") == want for _, _, it in _items(pack)):
        out.append(f'banner {key}: needs a para whose text is exactly "{want}"')


def _check_knowable_then(pack, out):
    for s, n, it in _items(pack):
        if it.get("kind") == "timeline" and isinstance(it.get("events"), list):
            for i, e in enumerate(it["events"]):
                if isinstance(e, dict) and "knowable_then" not in e:
                    out.append(f"{_item_name(s, n, it)}: events[{i}] needs knowable_then (was it knowable then?)")


def _nm_sections(pack) -> dict:
    """{M3: section} for the pack sections with ids m1..m9."""
    out = {}
    for s in pack.get("sections") or []:
        hit = re.fullmatch(r"m([1-9])", s.get("id") or "") if isinstance(s, dict) and isinstance(s.get("id"), str) else None
        if hit:
            out[f"M{hit.group(1)}"] = s
    return out


def _nm_items(s):
    return [it for it in (s.get("items") if isinstance(s.get("items"), list) else []) if isinstance(it, dict)]


def _nm_cell(v) -> str:
    return v.strip() if isinstance(v, str) else "" if v is None else str(v).strip()


def _check_nine_m_overview(pack, out):
    tables = [it for s, _, it in _items(pack) if it.get("kind") == "table"
              and (s.get("id") == "nine-m-overview" or it.get("id") == "nine-m-overview")]
    if not tables:
        out.append("nine-m-overview: no table in a section nine-m-overview (one row per M, M1 to M9 in order)")
    else:
        rows = tables[0].get("rows") if isinstance(tables[0].get("rows"), list) else []
        if len(rows) != len(NINE_M_CODES):
            out.append(f"nine-m-overview: {len(rows)} rows, expected 9 (M1 to M9 in order)")
        for i, (r, m) in enumerate(zip(rows, NINE_M_CODES), 1):
            first = _nm_cell(r[0]) if isinstance(r, list) and r else ""
            code = re.match(r"M[1-9]\b", first)
            if not code or code.group(0) != m:
                out.append(f"nine-m-overview: row {i} is {first or '(blank)'}, expected {m}")
    secs = _nm_sections(pack)
    reasons: dict = {}
    for s in pack.get("sections") or []:
        if isinstance(s, dict) and s.get("id") == "not-relevant":
            for it in _nm_items(s):
                for r in it.get("rows") if it.get("kind") == "table" and isinstance(it.get("rows"), list) else []:
                    code = re.match(r"M[1-9]\b", _nm_cell(r[0])) if isinstance(r, list) and r else None
                    if code:
                        reasons[code.group(0)] = reasons.get(code.group(0)) or any(_nm_cell(c) for c in r[1:])
    for n, m in enumerate(NINE_M_CODES, 1):
        sec = secs.get(m)
        learned = sec is not None and any(it.get("kind") == "learning" and isinstance(it.get("cites"), list)
                                          and it["cites"] for it in _nm_items(sec))
        if sec is not None and m in reasons:
            out.append(f"{m}: both a section m{n} and a not-relevant row; an M is one or the other")
        elif learned or reasons.get(m):
            continue
        elif m in reasons:
            out.append(f"{m}: the not-relevant row needs a reason")
        else:
            out.append(f"{m}: needs a section m{n} with a cited learning, or a not-relevant row with a reason")


def _check_nine_m_cites(pack, w, out):
    seed = (w or {}).get("nine_m_seed")
    if not isinstance(seed, dict):
        out.append("nine-m-cites: the workspace has no nine_m_seed.json; run nine-m-seed <ws>")
        return
    S = seed.get("findings") or {}
    for m, s in _nm_sections(pack).items():
        for n, it in enumerate(_nm_items(s), 1):
            off = [x for x in it.get("cites") or [] if isinstance(x, str) and x.startswith("FND-")
                   and not ((S.get(x) or {}).get("scores") or {}).get(m)]
            if off:
                out.append(f"nine-m-cites: {_item_name(s, n, it)} cites {', '.join(off)}, which the seed does not link "
                           f"to {m}; check the M, or say why in the item")


def _check_m1_balance(pack, w, out):
    # Fires only when M1 holds strictly more recommendations than every other M: a tie for the most stays quiet.
    recs = {m: sum(1 for it in _nm_items(s) if it.get("kind") == "recommendation")
            for m, s in _nm_sections(pack).items()}
    n1 = recs.get("M1", 0)
    seed = (w or {}).get("nine_m_seed")
    if not n1 or any(recs.get(m, 0) >= n1 for m in NINE_M_CODES[1:]) or not isinstance(seed, dict):
        return
    prof = seed.get("profile") or {}

    def deep(m):
        lv = (prof.get(m) or {}).get("by_level") or {}
        return int(lv.get("3") or 0) + int(lv.get("4") or 0)
    ahead = [m for m in NINE_M_CODES[1:] if deep(m) > deep("M1")]
    if ahead:
        top = max(ahead, key=lambda m: (deep(m), -NINE_M_CODES.index(m)))
        out.append(f"m1-balance: M1 holds the most recommendations ({n1}) while {top} has more level 3-4 findings in "
                   f"the seed ({deep(top)} against {deep('M1')}); M1 is not the people M: check the system drivers")


def _filled(v) -> bool:
    return bool(v.strip()) if isinstance(v, str) else v not in (None, False, [], {})


def hard(pack, profile, register=None) -> list:
    """Profile violations that are problems even without --strict: no-owner-due (D7): owner, by_when, co_owner; and
    the Phase 6 rules alert-priority-1 (only with a register), leading-lagging and inferred-banner."""
    if not isinstance(pack, dict) or not isinstance(profile, dict):
        return []
    rules = profile.get("rules") or []
    out = []
    if "no-owner-due" in rules:
        out += [f"{_item_name(s, n, it)}: {NO_OWNER_DUE}" for s, n, it in _items(pack)
                if _filled(it.get("owner")) or _filled(it.get("by_when")) or _filled(it.get("co_owner"))]
    if "alert-priority-1" in rules and register is not None:
        _check_alert_priority_1(pack, register, out)
    if "leading-lagging" in rules:
        _check_leading_lagging(pack, out)
    if "inferred-banner" in rules:
        _check_inferred_banner(pack, out)
    return out


def advice(pack, profile) -> list:
    """Profile messages that stay warnings even under --strict: grade-source (OD6-1)."""
    if not isinstance(pack, dict) or not isinstance(profile, dict) or "grade-source" not in (profile.get("rules") or []):
        return []
    miss = [k for k in ("grade", "grade_source") if pack.get(k) in (None, "")]
    if not miss:
        return []
    return [f"grade-source: the pack has no {' or '.join(miss)}; record the grade and where it came from (the "
            "register's urgency, or chosen by the user)"]


def _p6_section_items(pack, sid):
    for s, n, it in _items(pack):
        if s.get("id") == sid:
            yield s, n, it


def _check_alert_priority_1(pack, register, out):
    entries = register.get("entries") if isinstance(register, dict) else register
    prio = {e["lr_id"]: e.get("priority") for e in (entries if isinstance(entries, list) else [])
            if isinstance(e, dict) and isinstance(e.get("lr_id"), str)}
    for s, n, it in _p6_section_items(pack, "learnings"):
        if it.get("kind") != "learning":
            continue
        lr = it.get("learning")
        if not isinstance(lr, str) or not lr.startswith("LR-"):
            out.append(f"alert-priority-1: {_item_name(s, n, it)} cites no learning; an alert carries priority-1 "
                       "learnings from the register (set learning to its LR- id)")
        elif lr in prio and prio[lr] != 1:
            out.append(f"alert-priority-1: {_item_name(s, n, it)} cites {lr}, whose priority is {prio[lr]}; an alert "
                       "carries priority-1 learnings only")


def _p6_col(columns, word):
    for i, c in enumerate(columns):
        if isinstance(c, str) and c.strip().lower().startswith(word):
            return i
    return None


def _check_leading_lagging(pack, out):
    for s, n, it in _p6_section_items(pack, "indicators"):
        if it.get("kind") != "table":
            continue
        cols = it.get("columns") if isinstance(it.get("columns"), list) else []
        name = _item_name(s, n, it)
        where = {w: _p6_col(cols, w.lower()) for w in ("Leading", "Lagging")}
        miss = [w for w, i in where.items() if i is None]
        if miss:
            out.append(f"leading-lagging: {name} needs {' and '.join(miss)} column{'s' if len(miss) > 1 else ''}")
            continue
        for r, row in enumerate(it.get("rows") if isinstance(it.get("rows"), list) else [], 1):
            cells = row if isinstance(row, list) else []
            empty = [w for w, i in where.items() if i >= len(cells) or not _filled(cells[i])]
            if empty:
                out.append(f"leading-lagging: {name} row {r} has no {' or '.join(empty)} indicator; every row needs "
                           "both")


def _check_inferred_banner(pack, out):
    inferred = any(isinstance(nd, dict) and nd.get("inferred") is True
                   for _, _, it in _items(pack) if it.get("kind") == "graph" and isinstance(it.get("nodes"), list)
                   for nd in it["nodes"])
    want = BANNERS["accimap-inferred"]
    if inferred and not any(it.get("kind") == "para" and it.get("text") == want for _, _, it in _items(pack)):
        out.append(f'inferred-banner: a graph has inferred placements; the pack needs a para whose text is exactly '
                   f'"{want}"')


def _check_needs_are_questions(pack, out):
    for s, n, it in _p6_section_items(pack, "needs"):
        if it.get("kind") != "question":
            out.append(f"section needs: {_item_name(s, n, it)} is a {it.get('kind')}; {NEEDS_ARE_QUESTIONS}: write "
                       "each need as a question")


def _check_due_dates(pack, out):
    # D7, final review I1: a due date written into the words of a change ("completes this by 30 June 2026") leaks past
    # the owner and by_when keys. A warning (a problem under --strict): the date pattern can match a fact.
    for s, n, it in _items(pack):
        keys = ("change", "text") if it.get("kind") == "recommendation" else ("change",)
        for k in keys:
            v = it.get(k)
            if isinstance(v, str) and DUE_DATE_RX.search(v):
                out.append(f"no-owner-due: {_item_name(s, n, it)} {k} {NO_OWNER_DUE_DATE}")


def check(pack, profile, top=None, profiles=None, w=None) -> list:
    """Profile violation messages for one pack. top: the top-rated relevant finding IDs (check_pack passes
    top_rated_of(w, relevant findings net of exclusions)); the follow-up-per-top rule is skipped without it. w: the
    workspace, for the 9M rules (its nine_m_seed and nine_m_session_mode)."""
    if not isinstance(pack, dict) or not isinstance(profile, dict):
        return []
    out: list = []
    name = pack.get("pack")
    _check_sections(pack, profile, out)
    _check_max_words(pack, profile, out)
    bl, lim = pack.get("bottom_line"), profile.get("bottom_line")
    if isinstance(bl, list) and isinstance(lim, dict) and not lim.get("min", 0) <= len(bl) <= lim.get("max", len(bl)):
        out.append(f"bottom_line: {len(bl)} entries, expected {lim.get('min', 0)}-{lim.get('max')}")
    sc = pack.get("scope") if isinstance(pack.get("scope"), dict) else {}
    for k in profile.get("required_scope") or []:
        if sc.get(k) in (None, [], ""):
            out.append(f"scope.{k}: required by the {name} profile")
    for kind, limit in (profile.get("word_limits") or {}).items():
        for s, n, it in _items(pack):
            if it.get("kind") == kind and _words(it) > limit:
                out.append(f"{kind} {_item_name(s, n, it)}: {_words(it)} words, at most {limit}")
    for r in profile.get("rules") or []:
        if r == "triplets":
            _check_triplets(pack, out)
        elif r == "assessment-answer":
            _check_assessment(pack, out)
        elif r == "follow-up-per-top":
            _check_follow_up_per_top(pack, top, out)
        elif isinstance(r, str) and r.startswith("same-sections-as:"):
            _check_same_sections(pack, r.split(":", 1)[1], load() if profiles is None else profiles, out)
        elif r == "no-owner-due":                   # owner, by_when, co_owner: a problem even without --strict: hard()
            _check_due_dates(pack, out)
        elif r == "banner:nine-m-demo":              # only a replayed session needs the demo banner (OD5-1)
            if (w or {}).get("nine_m_session_mode") == "replay":
                _check_banner(pack, "nine-m-demo", out)
        elif isinstance(r, str) and r.startswith("banner:"):
            _check_banner(pack, r.split(":", 1)[1], out)
        elif r == "knowable-then":
            _check_knowable_then(pack, out)
        elif r == "nine-m-overview":
            _check_nine_m_overview(pack, out)
        elif r == "nine-m-cites":
            _check_nine_m_cites(pack, w, out)
        elif r == "m1-balance":
            _check_m1_balance(pack, w, out)
        elif r == "needs-are-questions":
            _check_needs_are_questions(pack, out)
        elif r in ("grade-source", "alert-priority-1", "leading-lagging", "inferred-banner"):
            pass                                     # advice() and hard() report these, whatever --strict says
        else:
            out.append(f"rules: unknown profile rule {r!r}")
    return out


def padding(pack) -> list:
    """P3-7: three or more items in one section with the same non-empty cites set. Ruling X26: only within one
    section (sections answer different questions). Ruling X24: items that share one non-empty group (an engineering
    learning, barrier and recommendation; a decision and its indicator) count once."""
    seen: dict = {}
    for n, (s, _, it) in enumerate(_items(pack)):
        c, g = it.get("cites"), it.get("group")
        if isinstance(c, list) and c and all(isinstance(x, str) for x in c):
            unit = ("group", g) if isinstance(g, str) and g.strip() else ("item", n)
            seen.setdefault((id(s), tuple(sorted(set(c)))), []).append(unit)
    return [f"{len(v)} items share the same cites ({', '.join(k[1])}): possible padding" for k, v in seen.items()
            if len(set(v)) >= 3]


def _audience_name(a) -> str:
    """The audience id in the singular, as the drift message reads ("supervisors" -> "supervisor")."""
    x = a.get("id", "")
    return x[:-1] if x.endswith("s") else x


def _default_text(d) -> str:
    parts = list(d.get("tiers") or [])
    if d.get("levels"):
        parts.append("levels " + ", ".join(map(str, d["levels"])))
    if d.get("tags"):
        parts.append("tags " + ", ".join(d["tags"]))
    return "; ".join(parts)


def scope_drift(pack, audiences) -> list:
    """L3-12: the pack's scope against its audience's default_scope (references/audiences.json). On each of tiers,
    levels and tags that both set, every default value must be in the pack's scope; a pack that sets none of the
    dimensions its default sets has drifted too. min_rating is not compared."""
    if not isinstance(pack, dict):
        return []
    aud = next((a for a in audiences or [] if isinstance(a, dict) and a.get("skill") == pack.get("pack")), None)
    d = aud.get("default_scope") if aud else None
    if not isinstance(d, dict):
        return []
    dims = [k for k in ("tiers", "levels", "tags") if d.get(k)]
    if not dims:
        return []
    sc = pack.get("scope") if isinstance(pack.get("scope"), dict) else {}
    shared = [k for k in dims if isinstance(sc.get(k), list) and sc.get(k)]
    drift = not shared or any(x not in sc[k] for k in shared for x in d[k])
    return [f"scope differs from the {_audience_name(aud)} audience default ({_default_text(d)})"] if drift else []


def load_audiences() -> list:
    return load(REFS / "audiences.json")
