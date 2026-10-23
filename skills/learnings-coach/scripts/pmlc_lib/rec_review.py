"""rec-review: strength bands, level match, loops, SMART gaps and recipients of a Learnings Register's recommendations
(plan ruling P5-14). It reads a register only; it never writes an owner or a date (D7), so time-bound is not checked."""
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

from .register.check import norm_hoc, norm_level
from .util import _s

RR_CITE_RX = re.compile(r"\b(?:EVD-\d+|FND-[0-9A-Fa-f]+)\b")
RR_M_KEYS = tuple(f"M{i}" for i in range(1, 10))
REC_BANDS = ("stronger", "intermediate", "weaker", "unrated")
REC_REVIEW_REFUSAL = "rec-review reads a learnings register (check-register passes on it), not a pack"
_RR_CACHE = {}


def _rr_rules() -> dict:
    if "r" not in _RR_CACHE:
        p = Path(__file__).resolve().parents[2] / "references" / "rec-review.json"
        d = json.loads(p.read_text(encoding="utf-8"))

        def rx(words):
            return re.compile(r"(?<![a-z0-9])(?:" + "|".join(re.escape(x) for x in words) + r")(?:s|es|ed)?(?![a-z0-9])", re.I)
        d["_weak_rx"] = rx(d["weak_admin"])
        d["_double_rx"] = rx(d["double_loop"])
        _RR_CACHE["r"] = d
    return _RR_CACHE["r"]


def _rr_change(rec) -> str:
    return _s(rec.get("what") or rec.get("change"))


def band(rec: dict) -> str:
    """stronger | intermediate | weaker | unrated for one recommendation."""
    R = _rr_rules()
    tier = norm_hoc(rec.get("hoc_tier"))
    b = R["bands"].get(tier, "unrated")
    if tier == "administrative" and R["_weak_rx"].search(_rr_change(rec)):
        return "weaker"
    return b


def rr_is_double_loop(rec: dict) -> bool:
    return bool(_rr_rules()["_double_rx"].search(_rr_change(rec)))


def rr_smart_missing(rec: dict) -> list:
    """Which of specific / measurable / relevant the recommendation lacks. Time-bound is never checked (D7)."""
    miss = []
    if len(_rr_change(rec).split()) < _rr_rules()["min_change_words"]:
        miss.append("specific")
    if not _s(rec.get("leading_indicator") or rec.get("indicator")):
        miss.append("measurable")
    cites = rec.get("cites") or []
    cites = cites if isinstance(cites, list) else [cites]
    if not (RR_CITE_RX.search(_s(rec.get("evidence_basis"))) or any(RR_CITE_RX.search(_s(c)) for c in cites)):
        miss.append("relevant")
    return miss


def rr_is_register(reg) -> bool:
    entries = reg.get("entries") if isinstance(reg, dict) else reg
    return (isinstance(entries, list) and bool(entries) and all(isinstance(e, dict) for e in entries)
            and all(_s(e.get("lr_id")) for e in entries))


def _rr_rec_id(e, i, r) -> str:
    return _s(r.get("id")) or f"{e.get('lr_id')}-R{i}"


def review(register, nine_m_map=None) -> dict:
    R = _rr_rules()
    entries = register["entries"] if isinstance(register, dict) else register
    bands = collections.OrderedDict((b, 0) for b in REC_BANDS)
    causes, double, single, smart = [], [], [], []
    recip = collections.Counter()
    for e in entries:
        lid = _s(e.get("lr_id"))
        recs = [r for r in (e.get("recommendations") or []) if isinstance(r, dict)]
        got = []
        for i, r in enumerate(recs, 1):
            rid = _rr_rec_id(e, i, r)
            b = band(r)
            bands[b] += 1
            got.append(b)
            (double if rr_is_double_loop(r) else single).append(rid)
            miss = rr_smart_missing(r)
            if miss:
                smart.append({"rec": rid, "missing": miss})
            roles = ([_s(r.get("recipient_role"))] if _s(r.get("recipient_role")) else
                     [_s(e.get("recipient_role"))] if _s(e.get("recipient_role")) else
                     [_s(x) for x in (e.get("audiences") or []) if _s(x)])
            for role in roles:
                recip[role] += 1
        m = re.match(r"L([1-4])", norm_level(e.get("hfacs_level")))
        levels = [int(m.group(1))] if m else []
        best = next((b for b in ("stronger", "intermediate", "weaker") if b in got), "unrated" if got else "none")
        deep = any(lv in R["deep_levels"] for lv in levels)
        ok = not (deep and best not in ("stronger", "intermediate"))
        causes.append({"lr": lid, "levels": levels, "strongest_band": best, "level_match": ok,
                       "flag": "" if ok else R["deep_flag"]})
    spread = None
    if nine_m_map is not None:
        spread = collections.OrderedDict((k, 0) for k in RR_M_KEYS)
        by_lr = {_s(e.get("lr_id")): len([r for r in (e.get("recommendations") or []) if isinstance(r, dict)])
                 for e in entries}
        for c in (nine_m_map.get("conditions") or {}).values():
            m = _s(c.get("m"))
            if m in spread:
                ids = c.get("recommendation_ids")
                spread[m] += len(ids) if isinstance(ids, list) else by_lr.get(_s(c.get("learning_id")), 0)
    return {"reviewed": "register+9M" if nine_m_map is not None else "register",
            "causes": causes, "bands": dict(bands), "loops": {"double": double, "single": single},
            "spread": dict(spread) if spread is not None else None, "smart": smart,
            "recipients": [{"role": k, "n": n} for k, n in sorted(recip.items(), key=lambda kv: (-kv[1], kv[0]))]}


def rec_review_item(rv: dict, register, which: str) -> dict:
    """A ready table item (with row_cites) for a pack."""
    entries = register["entries"] if isinstance(register, dict) else register
    fids = {_s(e.get("lr_id")): list(e.get("finding_ids") or [])[:5] for e in entries}
    if which == "strength":
        rows = [[c["lr"], ",".join(f"L{x}" for x in c["levels"]) or "-", c["strongest_band"],
                 "yes" if c["level_match"] else "no", c["flag"]] for c in rv["causes"]]
        return _rr_table("rec-strength", ["Learning", "Level", "Strongest change", "Level match", "Flag"], rows,
                      [fids.get(c["lr"], []) for c in rv["causes"]])
    if which == "spread":
        if rv["spread"] is None:
            sys.exit("rec-review --table-item spread needs --nine-m (and outputs/nine-m-map.json)")
        rows = [[k, n] for k, n in rv["spread"].items()]
        return _rr_table("rec-spread", ["9M", "Recommendations"], rows, [[] for _ in rows])
    by_lr = {}
    for e in entries:
        for i, r in enumerate([r for r in (e.get("recommendations") or []) if isinstance(r, dict)], 1):
            by_lr[_rr_rec_id(e, i, r)] = _s(e.get("lr_id"))
    rows = [[s["rec"], ", ".join(s["missing"])] for s in rv["smart"]]
    return _rr_table("rec-smart", ["Recommendation", "Missing"], rows, [fids.get(by_lr.get(s["rec"], ""), []) for s in rv["smart"]])


def _rr_table(item_id, columns, rows, row_cites) -> dict:
    return {"kind": "table", "id": item_id, "columns": columns, "rows": rows, "row_cites": row_cites,
            "cites": sorted({x for c in row_cites for x in c})}


def _rr_fail(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


def cmd_rec_review(a):
    from .workspace import load_ws, outputs_dir
    load_ws(a.ws)
    p = Path(a.register)
    try:
        reg = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        _rr_fail(f"rec-review: cannot read {p} as a learnings register (JSON)")
    if not rr_is_register(reg):
        _rr_fail(REC_REVIEW_REFUSAL)
    nm = None
    if getattr(a, "nine_m", False):
        mp = outputs_dir(a.ws) / "nine-m-map.json"
        if not mp.is_file():
            _rr_fail(f"rec-review --nine-m reads {mp}, which does not exist yet: run the nine-m-analysis skill first")
        try:
            nm = json.loads(mp.read_text(encoding="utf-8"))
        except ValueError:
            _rr_fail(f"rec-review: cannot read {mp} as JSON")
    rv = review(reg, nm)
    if a.table_item:
        print(json.dumps(rec_review_item(rv, reg, a.table_item), indent=1, ensure_ascii=False))
    elif a.json:
        print(json.dumps(rv, indent=1, ensure_ascii=False, sort_keys=True))
    else:
        print(f"rec-review ({rv['reviewed']}): " + "; ".join(f"{k} {n}" for k, n in rv["bands"].items()))
        flagged = [c for c in rv["causes"] if not c["level_match"]]
        print(f"{len(flagged)} learning(s) flagged '{_rr_rules()['deep_flag']}'" + (": " + ", ".join(c["lr"] for c in flagged) if flagged else ""))
        print(f"double-loop {len(rv['loops']['double'])}, single-loop {len(rv['loops']['single'])}; "
              f"{len(rv['smart'])} recommendation(s) missing a SMART element")
        if rv["spread"] is not None:
            print("9M spread: " + ", ".join(f"{k} {n}" for k, n in rv["spread"].items()))
