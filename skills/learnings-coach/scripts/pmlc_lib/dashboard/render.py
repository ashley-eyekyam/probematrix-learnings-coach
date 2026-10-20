"""The dashboard command, rendered from templates/ with string.Template."""
from __future__ import annotations

import collections
import html
import json
import string
import sys
from pathlib import Path

from .. import BRAND, LEVEL_NAMES
from ..classify import TIER_LABELS
from ..dashboard.data import build_detail_data, DASHBOARD_ASSETS, embed_json, org_data, print_witness_note, resolve_embed
from ..handling import (
    effective_handling, HANDLING_CSS, handling_lines, is_draft, name_guard, public_records, RIBBON_HTML, share_ctx,
    share_gate, shared_copy, SHARED_LINE, shared_name, SHARED_SOURCE, status_line
)
from ..register.check import HOC_TIERS, norm_entity, norm_hoc
from ..register.xlsx import refuse_pack_as_register
from ..util import _int, _s
from ..workspace import load_ws, outputs_dir, warn_stale
from .. import privacy


PAGE_TOKENS_CSS = """:root{--bg:#f7f8fa;--fg:#111827;--mut:#5b6472;--card:#fff;--line:#e3e6eb;--acc:#0077b6}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#0d1117;--fg:#e6edf3;--mut:#9aa4b2;--card:#161b22;--line:#2a313c;--acc:#00bfff}}
:root[data-theme=dark]{--bg:#0d1117;--fg:#e6edf3;--mut:#9aa4b2;--card:#161b22;--line:#2a313c;--acc:#00bfff}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}"""
# Wide screens: containers use the space, prose keeps a readable measure (owner request 2026-10-15).
WIDE_CSS = "@media (min-width:1400px){main{max-width:min(calc(100vw - 32px),1600px)} main p,main li{max-width:75ch}}"
TEMPLATES = Path(__file__).resolve().parent / "templates"


def _render(name: str, **values) -> str:
    """templates/<name>.html with each $placeholder filled in ($$ is a literal $). The file's final newline is the
    editor's, not the page's, so it is dropped."""
    text = (TEMPLATES / f"{name}.html").read_text(encoding="utf-8")
    return string.Template(text[:-1] if text.endswith("\n") else text).substitute(values)


def org_section(org: dict) -> str:
    """Learnings x packs, pack reach and any organisation-file warnings, as the overview's last block."""
    esc = html.escape
    warn = "".join(f'<p class="m warn" role="alert" style="color:#b45309;font-weight:600">Warning: {esc(x)}</p>' for x in org["warnings"])
    packs = org["lr_pack_matrix"]["packs"]
    rows = [r for r in org["lr_pack_matrix"]["rows"] if r["cells"]]
    mx = max([v for r in rows for v in r["cells"].values()] or [1])
    if rows:
        matrix = ("<table><thead><tr><th>Learning</th>" + "".join(f"<th>{esc(p)}</th>" for p in packs)
                  + "</tr></thead><tbody>"
                  + "".join(f'<tr><th>{esc(r["lr_id"])} · {esc(r["title"][:90])}</th>'
                            + "".join(f'<td style="--o:{0.15 + 0.85 * r["cells"][p] / mx:.2f}"><span>{r["cells"][p]}</span></td>'
                                      if p in r["cells"] else '<td class="z">·</td>' for p in packs)
                            + "</tr>" for r in rows) + "</tbody></table>")
        matrix = f'<div class="wrap">{matrix}</div>'
    else:
        matrix = ('<p class="m">No pack item names a learning yet. Add a <code>learning</code> field (for example '
                  "LR-01) to pack items to see which learning each pack carries.</p>")
    names = packs + [p for p in org["reach"] if p not in packs]
    linked = collections.Counter()
    for r in org["lr_pack_matrix"]["rows"]:
        for p in r["cells"]:
            linked[p] += 1
    if names:
        def reach(p):
            x = org["reach"].get(p)
            return (f'{x["deliveries"]} deliveries · {x["attendees"]} attendees · {x["contractors_included"]} with contractors'
                    if x else "Not yet delivered")
        packlist = ('<div class="wrap"><table><thead><tr><th>Pack</th><th>Learnings</th><th>Reach</th></tr></thead><tbody>'
                    + "".join(f"<tr><th>{esc(p)}</th><td>{linked.get(p, 0)}</td><td>{esc(reach(p))}</td></tr>" for p in names)
                    + "</tbody></table></div>")
    else:
        packlist = '<p class="m">No learning packs have been written yet.</p>'
    return _render("packs", warnings=warn, matrix=matrix, packlist=packlist)


def cmd_dashboard(a):
    ws = Path(a.ws)
    w = load_ws(ws)
    if "clusters" not in w:
        sys.exit("Needs clusters.json. Run: pmlc.py classify <ws>")
    warn_stale(ws)
    reg0 = json.loads(Path(a.register).read_text(encoding="utf-8")) if a.register else None
    refuse_pack_as_register(reg0, a.register)
    hdoc0 = reg0 if isinstance(reg0, dict) else {}
    mode = share_gate(hdoc0, w, a, src=a.register, ws=ws)   # a dashboard without a signed register stays inside
    eh = effective_handling(hdoc0, w, src=a.register, ws=ws)
    share = share_ctx(a, w, mode) if mode != "internal" else None
    if share:
        w, reg0 = shared_copy(w, share, w), shared_copy(reg0, share, w)
        if isinstance(reg0, dict) and reg0.get("source"):
            reg0["source"] = SHARED_SOURCE
    F = {f["id"]: f for f in w["findings"]}
    cl = w["clusters"]
    names, tiers = cl["taxonomy"]["entities"], cl["taxonomy"]["tiers"]
    fields = dict(w.get("incident", {}).get("fields", {}))
    for k, v in (("Incident Title", a.title), ("Date", a.date), ("Location", a.location)):
        if v:
            fields[k] = privacy.share_text(v, share) if share else v
    ent_ids = [e for e in cl["entities"] if e != "F99"] + (["F99"] if "F99" in cl["entities"] else [])
    tier_ids = ["T1", "T2", "T3", "T4", "T5", "T9"]
    et = collections.Counter()
    el = collections.Counter()
    for fid, c in cl["findings"].items():
        for e in c["F"]:
            el[(e, F[fid]["level"])] += 1
            for t in c["T"]:
                et[(e, t)] += 1
    mx_et = max(et.values() or [1])
    mx_el = max(el.values() or [1])
    lvl = collections.Counter(f["level"] for f in F.values())
    rat = collections.Counter(f["rating"] for f in F.values())
    top_codes = collections.Counter(f"{f['code']} · {f['name']}" for f in F.values()).most_common(12)

    def cell(v, mx):
        if not v:
            return '<td class="z">·</td>'
        op = 0.15 + 0.85 * v / mx
        return f'<td style="--o:{op:.2f}"><span>{v}</span></td>'

    def table(rows, cols, colnames, counter, mx):
        h = ["<table><thead><tr><th></th>" + "".join(f"<th>{html.escape(colnames[c])}</th>" for c in cols) + "</tr></thead><tbody>"]
        for r in rows:
            h.append(f"<tr><th>{r} · {html.escape(names.get(r, r))}</th>" + "".join(cell(counter.get((r, c), 0), mx) for c in cols) + "</tr>")
        h.append("</tbody></table>")
        return "".join(h)

    tier_lab = {t: f"{t} {tiers.get(t, '')}" for t in tier_ids}
    lvl_lab = {k: f"L{k} {LEVEL_NAMES[k]}" for k in (1, 2, 3, 4)}
    n = len(F)
    up = lvl.get(3, 0) + lvl.get(4, 0)
    title = html.escape(fields.get("Incident Title", "ProbeMatrix investigation"))
    top = max((r for r in rat if r is not None), default=None)
    kpis = [("Findings", n), ("Evidence items", len(w.get("evidence", {}))),
            ("Learning clusters", len([e for e in ent_ids if e != "F99"])),
            ("At supervision + organisational level", f"{100*up/max(n,1):.0f}%"),
            ("Highest-rated findings", rat[top] if top is not None else 0)]
    bars = "".join(f'<div class="bar"><span>{html.escape(k)}</span><i style="width:{100*c/top_codes[0][1]:.0f}%"></i><b>{c}</b></div>'
                   for k, c in top_codes) if top_codes else ""
    learn_html = ""
    detail = None
    org = org_data(ws, [])
    if a.register:
        reg = reg0
        entries = reg["entries"] if isinstance(reg, dict) else reg
        entries = sorted(entries, key=lambda e: (_int(e.get("priority"), 9), _s(e.get("lr_id"))))
        embed = resolve_embed(a)
        detail = build_detail_data(w, reg, embed)
        org = org_data(ws, entries)
        detail["responses"], detail["closure"] = org["responses"], org["closure"]
        detail["compliance_count"] = sum(1 for e in entries if _s(e.get("regulatory_touchpoint")))
        if share and share.mode == "public":
            detail["findings"] = public_records(detail["findings"])
        print_witness_note(detail["evidence"], embed)
        recs = [r for e in entries for r in (e.get("recommendations") or [])]
        strong = sum(1 for r in recs if norm_hoc(r.get("hoc_tier")) in ("elimination", "substitution", "engineering"))
        kpis = [("Learnings", len(entries)),
                ("Priority-1 learnings", sum(1 for e in entries if _int(e.get("priority")) == 1)),
                ("Recommendations", len(recs)),
                ("Fixes above administrative tier", f"{100*strong/max(len(recs),1):.0f}%")] + kpis
        tiers_used = [t for t in TIER_LABELS if any(t in (e.get("tier_messages") or {}) for e in entries)]
        rows = []
        for e in entries:
            tm = e.get("tier_messages") or {}
            cells = "".join(
                f'<td style="--o:.55" title="{html.escape(tm[t])}"><span>●</span></td>' if t in tm else '<td class="z">·</td>'
                for t in tiers_used)
            lid = html.escape(_s(e.get("lr_id")))
            rows.append(f'<tr><th><a class="lr-link" href="#detail/{lid}">{lid} · {html.escape(_s(e.get("title"))[:90])}</a></th>'
                        f"<td>{html.escape(_s(e.get('priority')))}</td><td>{html.escape(norm_entity(e.get('owner_entity')))}</td>{cells}</tr>")
        matrix = ("<table><thead><tr><th>Learning</th><th>Priority</th><th>Owner</th>"
                  + "".join(f"<th>{t} {TIER_LABELS[t]}</th>" for t in tiers_used) + "</tr></thead><tbody>"
                  + "".join(rows) + "</tbody></table>")
        per_tier = []
        for t in tiers_used:
            items = "".join(f"<li><b>{html.escape(_s(e.get('lr_id')))}</b> {html.escape(e['tier_messages'][t])}</li>"
                            for e in entries if t in (e.get("tier_messages") or {}))
            n = sum(1 for e in entries if t in (e.get("tier_messages") or {}))
            per_tier.append(f"<details><summary>{t} {TIER_LABELS[t]} · {n} learnings</summary><ul>{items}</ul></details>")
        hoc = collections.Counter(norm_hoc(r.get("hoc_tier")) for r in recs)
        hoc_bars = "".join(f'<div class="bar"><span>{t}</span><i style="width:{100*hoc[t]/max(hoc.values()):.0f}%"></i><b>{hoc[t]}</b></div>'
                           for t in HOC_TIERS + ["unclassified"] if hoc.get(t))
        learn_html = _render("learnings", matrix=matrix, per_tier="".join(per_tier), hoc_bars=hoc_bars)
    for x in org["warnings"]:
        print(f"warning: {x}", file=sys.stderr)
    overview = _render("overview", org=org_section(org), kpis="".join(f"<div><b>{v}</b><span>{html.escape(k)}</span></div>" for k, v in kpis),
                       learnings=learn_html, entity_tier=table(ent_ids, tier_ids, tier_lab, et, mx_et),
                       entity_level=table(ent_ids, [1, 2, 3, 4], lvl_lab, el, mx_el), bars=bars)
    noscript_where = ("The same data is in the shared Learnings Register." if share else
                      "The same data is in learnings-register.xlsx and learnings-register.json.")
    if detail is not None:
        body = _render("tabs", overview=overview, noscript_where=noscript_where)
        extra_css = (DASHBOARD_ASSETS / "detail.css").read_text(encoding="utf-8")
        scripts = (f'<script type="application/json" id="pmlc-data">{embed_json(detail)}</script>\n'
                   f'<script>\n{(DASHBOARD_ASSETS / "detail.js").read_text(encoding="utf-8")}\n</script>')
    else:
        body = (overview + '\n<p class="m">Run <code>pmlc.py dashboard --register &lt;learnings-register.json&gt;</code> '
                "to add the detailed register tab.</p>")
        extra_css = scripts = ""
    ribbon = RIBBON_HTML + "\n" if is_draft(eh) else ""
    lines = handling_lines(eh)
    if share:
        lines = [privacy.share_text(x, share) for x in lines] + [SHARED_LINE.format(mode=mode)]
    handling = "".join(f'<p class="handling">{html.escape(x)}</p>' for x in lines)
    doc = _render("organisation-learning-map", title=title, page_tokens_css=PAGE_TOKENS_CSS, wide_css=WIDE_CSS,
                  handling_css=HANDLING_CSS, extra_css=extra_css, ribbon=ribbon, status=html.escape(status_line()),
                  handling=handling, location=html.escape(fields.get("Location", "")),
                  date=html.escape(fields.get("Date", "")), body=body, brand=html.escape(BRAND), scripts=scripts)
    name_guard([doc], a)
    out = Path(a.out) if a.out else shared_name(outputs_dir(ws) / "organisation-learning-map.html", mode)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    print(f"Dashboard written to {out}")
    if share:
        print(SHARED_LINE.format(mode=mode))
