"""Learning packs: the layered SVG layout of graph items."""
from __future__ import annotations

import collections
import html


# ----------------------------------------------------------------------------- graph layout

NODE_W, NODE_H, GAP_X, GAP_Y, PAD, CURVE = 190, 46, 70, 18, 12, 44
LABEL_MAX = 28


def _clip(s, n=LABEL_MAX):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1] + "…"


def layout_graph(nodes, edges, uid, max_nodes=60) -> dict:
    """Deterministic left-to-right layered drawing of a small graph as inline SVG (no library).
    Layers follow the longest path from the sources; back edges (found by depth-first search in input order)
    are ignored for layering and drawn as dashed curves below the nodes; a link that skips a layer arcs above them,
    so it never lies on a chain through the layers between; four barycentre passes order each layer.
    Over max_nodes, the nodes with the most links are kept and the rest counted in 'omitted'."""
    order = [n["id"] for n in nodes]
    label = {n["id"]: n.get("label") or n["id"] for n in nodes}
    deg = collections.Counter()
    for e in edges:
        deg[e["from"]] += 1
        deg[e["to"]] += 1
    omitted = max(0, len(order) - max_nodes)
    if omitted:
        first = {i: k for k, i in enumerate(order)}
        keep = set(sorted(order, key=lambda i: (-deg[i], first[i]))[:max_nodes])
        order = [i for i in order if i in keep]
    rank = {i: k for k, i in enumerate(order)}
    E, seen = [], set()
    for e in edges:
        u, v = e["from"], e["to"]
        if u in rank and v in rank and u != v and (u, v) not in seen:
            seen.add((u, v))
            E.append((u, v, e.get("label") or ""))

    succ = {i: [] for i in order}
    for u, v, _ in E:
        succ[u].append(v)
    state, back = {}, set()

    def dfs(u):
        state[u] = 1
        for v in succ[u]:
            if state.get(v) == 1:
                back.add((u, v))
            elif v not in state:
                dfs(v)
        state[u] = 2

    for i in order:
        if i not in state:
            dfs(i)
    fwd = [(u, v) for u, v, _ in E if (u, v) not in back]
    layer = {i: 0 for i in order}
    for _ in range(len(order)):                       # longest path by relaxation; n <= max_nodes
        changed = False
        for u, v in fwd:
            if layer[v] < layer[u] + 1:
                layer[v], changed = layer[u] + 1, True
        if not changed:
            break
    cols = collections.defaultdict(list)
    for i in order:
        cols[layer[i]].append(i)
    pos = {i: k for c in cols.values() for k, i in enumerate(c)}
    preds = collections.defaultdict(list)
    for u, v in fwd:
        preds[v].append(u)
    for _ in range(4):
        for c in sorted(cols)[1:]:
            cols[c].sort(key=lambda i: (sum(pos[p] for p in preds[i]) / len(preds[i]) if preds[i] else pos[i], rank[i]))
            for k, i in enumerate(cols[c]):
                pos[i] = k

    ncols = (max(cols) + 1) if cols else 0
    nrows = max((len(c) for c in cols.values()), default=0)
    curved = any((u, v) in back or layer[v] <= layer[u] for u, v, _ in E)
    skips = {(u, v) for u, v, _ in E if (u, v) not in back and layer[v] > layer[u] + 1}
    top = CURVE if skips else 0
    width = PAD * 2 + ncols * NODE_W + max(0, ncols - 1) * GAP_X
    height = PAD * 2 + nrows * NODE_H + max(0, nrows - 1) * GAP_Y + (CURVE if curved else 0) + top
    xy = {i: (PAD + layer[i] * (NODE_W + GAP_X), PAD + top + pos[i] * (NODE_H + GAP_Y)) for i in order}
    esc = html.escape
    out = [f'<svg class="graph" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="group" '
           f'aria-label="Graph of {len(order)} nodes and {len(E)} links">',
           f'<defs><marker id="arr-{esc(uid)}" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" '
           f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>']
    for u, v, lab in E:
        (x1, y1), (x2, y2) = xy[u], xy[v]
        if (u, v) in back or layer[v] <= layer[u]:
            sx, sy, ex, ey = x1 + NODE_W // 2, y1 + NODE_H, x2 + NODE_W // 2, y2 + NODE_H
            d, cls = f"M{sx},{sy} C{sx},{sy + CURVE} {ex},{ey + CURVE} {ex},{ey}", "edge back"
        elif (u, v) in skips:                         # top centre to top centre, through the room above row one
            sx, ex = x1 + NODE_W // 2, x2 + NODE_W // 2
            d, cls = f"M{sx},{y1} C{sx},0 {ex},0 {ex},{y2}", "edge skip"
        else:
            d, cls = f"M{x1 + NODE_W},{y1 + NODE_H // 2} L{x2},{y2 + NODE_H // 2}", "edge"
        tip = esc(label[u]) + " → " + esc(label[v]) + (": " + esc(str(lab)) if lab else "")
        out.append(f'<path class="{cls}" d="{d}" marker-end="url(#arr-{esc(uid)})"><title>{tip}</title></path>')
    for i in order:
        x, y = xy[i]
        out.append(f'<g class="node" tabindex="0" role="img" aria-label="{esc(label[i])}" transform="translate({x},{y})">'
                   f'<rect width="{NODE_W}" height="{NODE_H}" rx="8"/>'
                   f'<text x="10" y="{NODE_H // 2 + 5}">{esc(_clip(label[i]))}</text><title>{esc(label[i])}</title></g>')
    out.append("</svg>")
    return {"svg": "".join(out), "omitted": omitted, "shown": len(order)}
