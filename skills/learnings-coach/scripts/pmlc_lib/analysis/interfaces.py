"""The interfaces command."""
from __future__ import annotations

import collections
import sys
from pathlib import Path

from ..util import CODE_RX, norm_code, write_json
from ..workspace import file_sha256, load_ws, record_derived


# ----------------------------------------------------------------------------- interfaces

def cmd_interfaces(a):
    ws = Path(a.ws)
    w = load_ws(ws)
    if "clusters" not in w:
        sys.exit("Needs clusters.json. Run: pmlc.py classify <ws>")
    cl = w["clusters"]
    names = cl["taxonomy"]["entities"]
    pair = collections.Counter()
    examples = collections.defaultdict(list)
    for fid, c in cl["findings"].items():
        ents = [e for e in c["F"] if e != "F99"]
        for i, x in enumerate(ents):
            for y in ents[i + 1:]:
                k = tuple(sorted((x, y)))
                pair[k] += 1
                examples[k].append(fid)
    code_ents = collections.defaultdict(set)
    for f in w["findings"]:
        code_ents[f["code"]].update(e for e in cl["findings"][f["id"]]["F"] if e != "F99")
    # Cross-entity causal mention: finding f (owned by entity x) names factor r in its causal
    # explanation, and r is owned (in this investigation) by entity y != x. Counted once per
    # (finding, referenced factor, entity pair).
    cross = collections.Counter()
    present = {f["code"] for f in w["findings"]}
    for f in w["findings"]:
        own = {e for e in cl["findings"][f["id"]]["F"] if e != "F99"}
        refs = {norm_code(p, n) for p, n in CODE_RX.findall(f["causal"])} & present - {f["code"]}
        seen = set()
        for r in refs:
            for x in own:
                for y in code_ents[r] - own:
                    k = tuple(sorted((x, y)))
                    if (r, k) not in seen:
                        seen.add((r, k))
                        cross[k] += 1
    ents = sorted({e for k in pair for e in k} | {e for k in cross for e in k})
    out = {"pairs": [{"a": k[0], "b": k[1], "shared_findings": pair[k], "cross_causal_mentions": cross.get(k, 0),
                      "examples": examples[k][:10]} for k in sorted(set(pair) | set(cross),
                                                                    key=lambda k: (-(pair.get(k, 0) * 3 + cross.get(k, 0)), k))]}
    write_json(ws / "interfaces.json", out)
    record_derived(ws, "interfaces.json", {n: file_sha256(ws / n) for n in ("findings.json", "clusters.json")})
    print("| Interface | Shared findings | Cross-entity causal mentions |\n|---|---:|---:|")
    for p in out["pairs"][: a.top]:
        print(f"| {p['a']} {names.get(p['a'], '')} ↔ {p['b']} {names.get(p['b'], '')} | "
              f"{p['shared_findings']} | {p['cross_causal_mentions']} |")
    print(f"\nWrote {ws/'interfaces.json'} ({len(out['pairs'])} pairs across {len(ents)} entities).")
