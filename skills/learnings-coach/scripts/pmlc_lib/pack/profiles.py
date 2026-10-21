"""Per-skill pack profiles (references/pack-profiles.json): which sections a pack has, the kinds that fill them,
how many items of each, the bottom-line count, word limits, the scope keys it must set and named rules. check-pack
reports a violation as a warning, and as a problem under --strict (Ruling P3-5).

Profile sections: each entry {"id", "kinds", "min", "max"} counts the items of its kinds in every pack section whose
id it matches. The id is exact, or a glob ("*", "s2-*", "t[1-5]") for sections the skill names per function, pair or
tier; a section takes the exact entries when there are any, otherwise the glob entries. Several entries may share an
id (one per kind with its own count). An entry with min 1 or more makes its section required; min 0 makes it
optional. A max of 99 means the skill states no count. The kinds a section may hold are the union of its entries'
kinds."""
from __future__ import annotations

import fnmatch
import json
import re

from ..util import REFS

PROFILES_FILE = REFS / "pack-profiles.json"
DOSSIER_RX = re.compile(r"^dossier-F\d+[a-z]?$")
RULES = ("triplets", "assessment-answer", "follow-up-per-top", "same-sections-as:")
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


def check(pack, profile, top=None, profiles=None) -> list:
    """Profile violation messages for one pack. top: the top-rated relevant finding IDs (check_pack passes
    top_rated_of(w, relevant findings net of exclusions)); the follow-up-per-top rule is skipped without it."""
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
