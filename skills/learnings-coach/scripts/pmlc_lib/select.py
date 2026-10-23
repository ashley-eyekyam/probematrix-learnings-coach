"""Finding filters, presets, the character budget and the select command."""
from __future__ import annotations

import collections
import json
import re
import sys
import types
from pathlib import Path

from .classify import entities_for_tags
from .util import _n, REFS
from .workspace import downgraded_findings, linked_evidence, load_ws, top_rating


# ----------------------------------------------------------------------------- select

def _evidence_for(f, E, max_quote=400):
    out = []
    for eid in f["evidence"]:
        e = E.get(eid)
        if not e:
            out.append({"id": eid})
            continue
        link = next((lk for lk in e["links"] if lk["code"] == f["code"]), e["links"][0] if e["links"] else {})
        out.append({"id": eid, "type": e["type"], "relevance": link.get("relevance", ""),
                    "reference": (link.get("reference", "") or "")[:max_quote]})
    return out


def _evidence_text(f, E):
    """Descriptions and Specific References of the evidence a finding is linked to (its own link rows first)."""
    out = []
    for eid in sorted(linked_evidence(f)):
        e = E.get(eid)
        if not e:
            continue
        links = [lk for lk in e["links"] if lk["code"] == f["code"]] or e["links"]
        out += [e.get("description", "")] + [lk.get("reference", "") for lk in links]
    return out


SELECT_DEFAULTS = dict(entity=None, tag=None, tier=None, relation=None, level=None, code=None, text=None,
                       subcategory=None, prefix=None, min_rating=None, top_rated=False, entity_mode="any",
                       exclude_downgraded=False, max=None, in_evidence=False, m=None, m_secondary=False)


def select_args(**kw) -> types.SimpleNamespace:
    """The namespace _filter reads, with every filter at its default; callers pass only what they set."""
    unknown = set(kw) - set(SELECT_DEFAULTS)
    if unknown:
        raise TypeError(f"unknown select filter(s): {', '.join(sorted(unknown))}")
    return types.SimpleNamespace(**{**SELECT_DEFAULTS, **kw})


def _filter(w, a):
    F = w["findings"]
    clusters = w.get("clusters", {})
    cl = clusters.get("findings", {})
    entity = set(a.entity or [])
    tag_sets = [set(entities_for_tags(clusters, [t])) for t in (a.tag or [])]
    all_mode = a.entity_mode == "all"
    if not all_mode:
        entity = entity.union(*tag_sets)
    prefixes = {p.upper() for p in a.prefix or []}
    subs = {x.lower() for x in a.subcategory or []}
    top = top_rating(w) if a.top_rated else None
    dropped = downgraded_findings(w) if a.exclude_downgraded else set()
    ms = set(getattr(a, "m", None) or [])
    seed9 = (w.get("nine_m_seed") or {}).get("findings", {}) if ms else {}
    out = []
    for f in F:
        c = cl.get(f["id"], {"F": [], "T": [], "R": []})
        have = set(c["F"])
        if all_mode:
            if (entity or tag_sets) and not (entity <= have and all(ts & have for ts in tag_sets)):
                continue
        elif entity and not entity & have:
            continue
        if a.tier and not set(a.tier) & set(c["T"]):
            continue
        if a.relation and not set(a.relation) & set(c["R"]):
            continue
        if a.level and f["level"] not in a.level:
            continue
        if a.min_rating and (f["rating"] or 0) < a.min_rating:
            continue
        if top is not None and (f["rating"] or 0) != top:
            continue
        if a.code and f["code"] not in a.code:
            continue
        if prefixes and f["code"].split(" ")[0].upper() not in prefixes:
            continue
        if subs and f["subcategory"].lower() not in subs:
            continue
        if f["id"] in dropped:
            continue
        if ms:
            s9 = seed9.get(f["id"]) or {}
            if s9.get("m_primary") not in ms and not (getattr(a, "m_secondary", False)
                                                      and ms & set(s9.get("m_secondary") or [])):
                continue
        if a.text:
            blob = [f["short"], f["justification"], f["causal"], f["label"]]
            if a.in_evidence:
                blob += _evidence_text(f, w.get("evidence", {}))
            if not re.search(a.text, " ".join(blob), re.I):
                continue
        out.append((f, c))
    out.sort(key=lambda fc: (-(fc[0]["rating"] or 0), -(fc[0]["level"] or 0), fc[0]["code"]))
    return out[: a.max] if a.max else out


SELECT_FIELDS = ["label", "short", "justification", "causal", "roles", "clusters", "evidence", "code", "name",
                 "level", "subcategory", "rating"]
COUNT_BY = ["entity", "tier", "relation", "level", "subcategory", "code"]


def _group_keys(f, c, how):
    """The group(s) a finding falls in; an entity/tier/relation key repeats the finding once per value."""
    if how == "level":
        return [f"L{f['level']}"]
    if how == "subcategory":
        return [f["subcategory"] or "(none)"]
    if how == "code":
        return [f["code"]]
    return list(c[{"entity": "F", "tier": "T", "relation": "R"}[how]]) or ["(none)"]


def _md_block(f, c, E, fields, brief, head):
    def on(k):
        return fields is None or k in fields

    parts = [f["id"]]
    cn = " ".join(str(f[k]) for k in ("code", "name") if on(k))
    lv = " ".join(x for x in ([f"L{f['level']}"] if on("level") else []) + ([f["subcategory"]] if on("subcategory") else []))
    for p in (cn, lv, f"rating {f['rating']}" if on("rating") else ""):
        if p:
            parts.append(p)
    L = [f"{head} " + " · ".join(parts)]
    if on("label"):
        L.append(f"**Instance:** {f['label']}\n")
    if on("short"):
        L.append(f"**Short:** {f['short']}\n")
    if not brief:
        if on("justification"):
            L.append(f"**Justification:** {f['justification']}\n")
        if on("causal"):
            L.append(f"**Causal explanation:** {f['causal']}\n")
    if on("roles"):
        L.append(f"**Roles:** {'; '.join(f['roles'])}  ")
    if on("clusters"):
        L.append(f"**Clusters:** F={','.join(c['F'])} T={','.join(c['T'])} R={','.join(c['R'])}\n")
    if not brief and on("evidence"):
        for e in _evidence_for(f, E):
            L.append(f"- `{e['id']}` ({e.get('type', '?')}): {e.get('relevance', '')} "
                     f"Quote: \"{e.get('reference', '')}\"")
    L.append("")
    return "\n".join(L)


def _json_item(f, c, E, fields):
    d = {k: f[k] for k in ("id", "code", "name", "level", "subcategory", "rating", "label", "short",
                           "justification", "causal", "roles")}
    d["clusters"] = c
    if fields is None or "evidence" in fields:
        d["evidence"] = _evidence_for(f, E)
    return d if fields is None else {k: v for k, v in d.items() if k == "id" or k in fields}


def _fit_count(n, fits):
    """The largest k in 0..n with fits(k) (0 when even nothing fits); fits is near-monotone in k."""
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi + 1) // 2
        lo, hi = (mid, hi) if fits(mid) else (lo, mid - 1)
    while lo and not fits(lo):
        lo -= 1
    return lo


SELECT_FILTER_FLAGS = ("--entity", "--tier", "--relation", "--level", "--min-rating", "--top-rated", "--code",
                       "--text", "--tag", "--subcategory", "--prefix", "--entity-mode", "--exclude-downgraded", "--max", "--in-evidence",
                       "--m", "--m-secondary")
PRESET_FILE = REFS / "select-presets.json"
SELECT_LINE = re.compile(r"PMLC select <ws>((?: [^`\n]*)?)")


def strip_comment(line: str) -> str:
    """The line before its shell comment: as in bash, `#` starts a comment only at the start of a word and outside
    quotes, so `--text "a # b"` and `--text a#b` keep their `#`."""
    quote, escaped, word_start = None, False, True
    for i, ch in enumerate(line):
        if escaped:  # the character after a backslash is literal
            escaped, word_start = False, False
        elif ch == "\\" and quote != "'":
            escaped = True
        elif quote:
            quote = None if ch == quote else quote
        elif ch in "'\"":
            quote, word_start = ch, False
        elif ch.isspace():
            word_start = True
        elif ch == "#" and word_start:
            return line[:i]
        else:
            word_start = False
    return line


def split_command(line: str) -> list[str]:
    """Shell-like split of one command line, without its trailing `# comment` (see strip_comment)."""
    import shlex
    return shlex.split(strip_comment(line))


def skill_select_lines(text: str) -> list[list[str]]:
    """The argument lists of the `PMLC select <ws> ...` gather calls in a SKILL.md, in order.

    Each call runs to the end of its line or its closing backtick. A trailing `# comment` (outside quotes) and
    any `--out ...` are dropped. A call with a `<...>` placeholder left (such as <F-id>) is a template, not a
    preset. An unbalanced quote raises ValueError naming the call."""
    calls = []
    for m in SELECT_LINE.finditer(text):
        try:
            args = split_command(m.group(1))
        except ValueError as e:
            raise ValueError(f"{e} in: PMLC select <ws>{m.group(1)}") from None
        if "--out" in args:
            i = args.index("--out")
            del args[i:i + 2]
        if any(re.search(r"<[^>]*>", t) for t in args):
            continue
        calls.append(args)
    return calls


def load_presets() -> dict:
    return json.loads(PRESET_FILE.read_text(encoding="utf-8"))


def _select_presets(a):
    """select --preset skill[:name]: run the skill's recorded gather calls with the real select parser."""
    from .cli import build_parser   # cli imports this module
    given = [t for t in getattr(a, "_argv", []) if t.split("=")[0] in SELECT_FILTER_FLAGS]
    changed = [k for k, v in SELECT_DEFAULTS.items() if getattr(a, k) != v]
    if given or changed:  # a usage error, so exit 2 as argparse does
        print("--preset cannot be combined with filters; edit the preset or drop --preset.", file=sys.stderr)
        sys.exit(2)
    skill, _, name = a.preset.partition(":")
    presets = load_presets()
    if skill not in presets:
        sys.exit(f"Unknown preset skill {skill}. Skills with presets: {', '.join(sorted(presets))}")
    calls = [p for p in presets[skill] if not name or p["name"] == name]
    if not calls:
        sys.exit(f"Unknown preset {a.preset}. Names for {skill}: {', '.join(p['name'] for p in presets[skill])}")
    out_flags = []
    if any(t.split("=")[0] == "--format" for t in getattr(a, "_argv", [])):
        out_flags += ["--format", a.format]
    for flag, val in (("--fields", a.fields), ("--group-by", a.group_by), ("--count-by", a.count_by)):
        if val is not None:
            out_flags += [flag, str(val)]
    if a.brief:
        out_flags.append("--brief")
    import contextlib
    import io
    parts = []
    for p in calls:
        head = f"# Preset {skill}: {p['name']}\n\n"
        budget = []
        if a.budget_chars is not None:  # one budget for the whole bundle: each call gets what the earlier ones left
            used = sum(len(x) for x in parts) + len(parts) + len(head)
            budget = ["--budget-chars", str(max(0, a.budget_chars - used))]
        sub = build_parser().parse_args(["select", a.ws, *p["args"], *out_flags, *budget])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cmd_select(sub)
        parts.append(head + buf.getvalue())
    text = "\n".join(parts)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"Wrote {len(calls)} preset bundle(s) to {a.out}")
    else:
        sys.stdout.write(text)


def cmd_select(a):
    if getattr(a, "preset", None):
        return _select_presets(a)
    if getattr(a, "in_evidence", False) and not a.text:
        sys.exit("--in-evidence extends --text; give --text too.")
    if getattr(a, "m_secondary", False) and not getattr(a, "m", None):
        print("--m-secondary extends --m; give --m too.", file=sys.stderr)
        sys.exit(2)
    w = load_ws(a.ws)
    if getattr(a, "m", None) and "nine_m_seed" not in w:
        print(f"select --m reads {Path(a.ws) / 'nine_m_seed.json'}: run nine-m-seed first", file=sys.stderr)
        sys.exit(2)
    grouping = a.group_by or a.count_by
    if (a.entity or a.tag or a.tier or a.relation or grouping in ("entity", "tier", "relation")) \
            and "clusters" not in w:
        sys.exit("Filtering or grouping by entity/tag/tier/relation needs clusters.json. "
                 "Run: pmlc.py classify <ws>")
    fields = None
    if a.fields:
        fields = {x.strip() for x in a.fields.split(",") if x.strip()}
        bad = fields - set(SELECT_FIELDS) - {"id"}
        if bad:
            sys.exit(f"Unknown --fields value(s): {', '.join(sorted(bad))}. Allowed: {', '.join(SELECT_FIELDS)}")
    E = w.get("evidence", {})
    sel = _filter(w, a)
    skipped = []
    if a.exclude_downgraded:
        would = {f["id"] for f, _ in _filter(w, types.SimpleNamespace(**{**vars(a), "exclude_downgraded": False,
                                                                         "max": None}))}
        skipped = sorted(downgraded_findings(w) & would)
    note = f"Excluded (reviewer downgrade): {', '.join(skipped) or 'none'}"
    nsel = len(sel)
    if a.count_by:
        ignored = [n for n, v in (("--budget-chars", a.budget_chars), ("--fields", a.fields),
                                  ("--group-by", a.group_by)) if v]
        if ignored:
            print(f"note: --count-by ignores {', '.join(ignored)}", file=sys.stderr)
        counts = collections.Counter(k for f, c in sel for k in _group_keys(f, c, a.count_by))
        rows = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        if a.format == "json":
            text = json.dumps(dict(rows), indent=1, ensure_ascii=False) + "\n"
        else:
            text = "\n".join([f"# Findings by {a.count_by} ({nsel} selected)\n", f"| {a.count_by} | findings |",
                              "|---|---:|"] + [f"| {k} | {n} |" for k, n in rows] + [""])
        kept = nsel
    else:
        md = a.format != "json"
        head = "###" if a.group_by else "##"
        blocks = [_md_block(f, c, E, fields, a.brief, head) if md else _json_item(f, c, E, fields) for f, c in sel]

        def render(k):
            if md:
                els = [f"# Selected findings ({k})\n",
                       f"Filters: entity={a.entity} tag={a.tag} tier={a.tier} relation={a.relation} level={a.level} "
                       f"min_rating={a.min_rating} top_rated={a.top_rated} entity_mode={a.entity_mode} "
                       f"code={a.code} prefix={a.prefix} subcategory={a.subcategory} text={a.text}"
                       + (f" m={a.m}" + (" (with secondary)" if a.m_secondary else "") if getattr(a, "m", None) else "")
                       + "\n"]
                if a.group_by:
                    groups = {}
                    for (f, c), b in zip(sel[:k], blocks[:k]):
                        for g in _group_keys(f, c, a.group_by):
                            groups.setdefault(g, []).append(b)
                    for g in sorted(groups):
                        els.append(f"## {g}\n")
                        els.extend(groups[g])
                else:
                    els.extend(blocks[:k])
                els.extend(footers_for(k))
                return "\n".join(els) + "\n"
            if a.group_by:
                groups = {}
                for (f, c), b in zip(sel[:k], blocks[:k]):
                    for g in _group_keys(f, c, a.group_by):
                        groups.setdefault(g, []).append(b)
                data = {g: groups[g] for g in sorted(groups)}
            else:
                data = blocks[:k]
            return json.dumps(data, indent=1, ensure_ascii=False) + "\n"

        def dropped_line(k):
            ids = [f["id"] for f, _ in sel[k:]]
            low = sel[k - 1][0]["rating"] if k else "none"
            return (f"Dropped for budget: {_n(len(ids), 'finding')} (lowest kept rating {low}): "
                    f"{', '.join(ids[:20])}{'…' if len(ids) > 20 else ''}")

        def footers_for(k):
            out = [dropped_line(k)] if k < nsel else []
            return out + ([note] if a.exclude_downgraded else [])

        kept = nsel
        if a.budget_chars is not None:
            kept = _fit_count(nsel, lambda k: len(render(k)) <= a.budget_chars)
        text = render(kept)
        if kept < nsel:
            print(dropped_line(kept), file=sys.stderr)
        if kept == 0 and nsel and a.budget_chars is not None and len(text) > a.budget_chars:
            print(f"select: budget {a.budget_chars} is below the minimum output ({len(text)} chars); "
                  "no findings kept", file=sys.stderr)
        if not md and a.exclude_downgraded:
            print(note, file=sys.stderr)
    if a.count_by and a.exclude_downgraded:
        if a.format == "json":
            print(note, file=sys.stderr)
        else:
            text += note + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"Wrote {_n(kept, 'finding')} to {a.out}")
    else:
        sys.stdout.write(text)
    print(f"select: {_n(kept, 'finding')}, {len(text)} chars", file=sys.stderr)
