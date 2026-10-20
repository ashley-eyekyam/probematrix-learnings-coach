"""Learning packs: ready-made items (causal-item)."""
from __future__ import annotations

import json
import sys

from ..util import _abs


# ----------------------------------------------------------------------------- causal graph -> graph item

def causal_graph_item(g, top=40) -> dict:
    """A ready graph item from <ws>/causal_graph.json: the top links by mentions (ties by code), their end
    nodes in first-seen order, and the findings behind those links as cites."""
    edges = sorted(g.get("edges", []), key=lambda e: (-e["mentions"], e["from"], e["to"]))[:max(top, 1)]
    names = {n["code"]: n for n in g.get("nodes", [])}
    used = []
    for e in edges:
        for c in (e["from"], e["to"]):
            if c not in used:
                used.append(c)
    nodes = [{"id": c, "label": f"L{names[c]['level']} {c} {names[c]['name']}" if c in names else c} for c in used]
    it = {"kind": "graph", "id": "causal-map", "nodes": nodes,
          "edges": [{"from": e["from"], "to": e["to"],
                     "label": f"{e['mentions']} mention" + ("" if e["mentions"] == 1 else "s")} for e in edges]}
    cites = sorted({x for e in edges for x in e.get("findings", [])})
    if cites:
        it["cites"] = cites
    return it


def cmd_causal_item(a):
    ws = _abs(a.ws)
    src = ws / "causal_graph.json"
    if not src.exists():
        sys.exit(f"Needs {src.name}. Run: pmlc.py causal {a.ws}")
    it = causal_graph_item(json.loads(src.read_text(encoding="utf-8")), a.top)
    if not it["edges"]:
        sys.exit("causal_graph.json has no links; tell the causal story in para items instead")
    print(json.dumps(it, indent=1, ensure_ascii=False))
