"""The causal command."""
from __future__ import annotations

import collections
import html
from pathlib import Path

from .. import LEVEL_NAMES
from ..util import CODE_RX, norm_code, write_json
from ..workspace import file_sha256, load_ws, record_derived


# ----------------------------------------------------------------------------- causal

HUB_COLUMNS = ["Factor", "Level", "Links out", "Mentions"]


def hub_rows(g: dict) -> list:
    """Out-degree of every factor in a causal_graph.json document: dicts with code, name, level, links (distinct
    links out), mentions (their total) and findings (the Finding IDs behind them). Most links first; ties by
    mentions, then by code, so the order never depends on the hash seed (X14)."""
    names = {n["code"]: n for n in g.get("nodes", [])}
    out = {}
    for e in g.get("edges", []):
        h = out.setdefault(e["from"], {"code": e["from"], "links": 0, "mentions": 0, "findings": []})
        h["links"] += 1
        h["mentions"] += e["mentions"]
        h["findings"] += [x for x in e.get("findings", []) if x.startswith("FND-")]
    for c, h in out.items():
        h["name"] = names.get(c, {}).get("name", "")
        h["level"] = names.get(c, {}).get("level")
        h["findings"] = sorted(set(h["findings"]))
    return sorted(out.values(), key=lambda h: (-h["links"], -h["mentions"], h["code"]))


def cmd_causal(a):
    ws = Path(a.ws)
    w = load_ws(ws)
    F = w["findings"]
    present = {f["code"]: f["level"] for f in F}
    names = {f["code"]: f["name"] for f in F}
    edges = collections.Counter()
    evid = collections.defaultdict(list)
    for f in F:
        text = f["causal"] + " " + (f["justification"] if a.include_justification else "")
        refs = {norm_code(p, n) for p, n in CODE_RX.findall(text)} - {f["code"]}
        for r in refs:
            if r not in present:
                continue
            a_, b_ = f["code"], r
            la, lb = present[a_] or 0, present[b_] or 0
            # Convention: higher HFACS level (organisational) -> lower level (acts) = "enables".
            src, dst = (a_, b_) if la >= lb else (b_, a_)
            edges[(src, dst)] += 1
            evid[(src, dst)].append(f["id"])
    for row in w.get("incident", {}).get("causal_chain_sheet", []):
        k = (row.get("From Code"), row.get("To Code"))
        edges[k] += 1
        evid[k].append("causal-chain-sheet")
    items = [{"from": s, "to": t, "from_level": present.get(s), "to_level": present.get(t),
              "mentions": c, "findings": evid[(s, t)][:12]}
             for (s, t), c in sorted(edges.items(), key=lambda kv: (-kv[1], kv[0]))]
    write_json(ws / "causal_graph.json", {"nodes": [{"code": c, "name": names[c], "level": present[c]}
                                                    for c in sorted(present)], "edges": items})
    top = items[: a.top]
    M = ["flowchart TB"]
    used = {e["from"] for e in top} | {e["to"] for e in top}
    for lv in (4, 3, 2, 1):
        nodes = sorted(c for c in used if present.get(c) == lv)
        if nodes:
            M.append(f'  subgraph L{lv}["L{lv} {LEVEL_NAMES[lv]}"]')
            for c in nodes:
                M.append(f'    {c.replace(" ", "_").replace(".", "_")}["{c}<br/>{html.escape(names[c][:40])}"]')
            M.append("  end")
    for e in top:
        s = e["from"].replace(" ", "_").replace(".", "_")
        t = e["to"].replace(" ", "_").replace(".", "_")
        M.append(f"  {s} -->|{e['mentions']}| {t}")
    (ws / "causal_graph.mmd").write_text("\n".join(M), encoding="utf-8")
    ins = {n: file_sha256(ws / n) for n in ("findings.json", "incident.json") if (ws / n).exists()}
    for n in ("causal_graph.json", "causal_graph.mmd"):
        record_derived(ws, n, ins)
    linked = sum(1 for f in F if ({norm_code(p, n) for p, n in CODE_RX.findall(f['causal'])} - {f['code']}) & set(present))
    print(f"{linked} of {len(F)} findings name other factors in their causal explanation. "
          f"{len(items)} distinct links. Wrote causal_graph.json and causal_graph.mmd (top {a.top}).")
    print("\n| From | To | Mentions |\n|---|---|---:|")
    for e in top[:25]:
        print(f"| {e['from']} (L{e['from_level']}) | {e['to']} (L{e['to_level']}) | {e['mentions']} |")
    if getattr(a, "hubs", False):
        print("\nHubs: factors with the most links out (a count of links, not a measure of strength)\n")
        print("| " + " | ".join(HUB_COLUMNS) + " | Name |\n|---|---|---:|---:|---|")
        for h in hub_rows({"nodes": [{"code": c, "name": names[c], "level": present[c]} for c in present],
                           "edges": items})[:15]:
            print(f"| {h['code']} | L{h['level']} | {h['links']} | {h['mentions']} | {h['name'][:60]} |")
