# causal-item

## What it does

Prints the strongest links of the [causal](causal.md) graph as one ready-made **graph item** for a learning pack: a JSON object with `"kind": "graph"`, its nodes (each factor with its level and name), its edges (with the number of mentions) and the Finding IDs it cites. The agent pastes it into a pack section, so the causal picture in the pack is drawn from the data, not retyped.

It prints to the screen only; it writes no file.

## When to use it

While writing a pack that shows "what led to what": the causal-map, board-brief and barrier-learnings skills use it. Run [causal](causal.md) first.

## Synopsis

```text
pmlc causal-item ws [--top TOP]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--top` | number | 40 | How many links to keep, strongest first |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

The three strongest links in the Hazira graph:

```bash
python3 $E causal-item $WS --top 3
```

```text
{
 "kind": "graph",
 "id": "causal-map",
 "nodes": [
  {
   "id": "OIR 1.6",
   "label": "L4 OIR 1.6 Failure in Maintenance/ Spares/ Support Programme"
  },
  {
   "id": "SVF 3.4",
   "label": "L3 SVF 3.4 Failed to Mitigate/ Ineffective Action against Identified Risk"
  },
…
 ],
 "edges": [
  {
   "from": "OIR 1.6",
   "to": "SVF 3.4",
   "label": "7 mentions"
  },
…
 ],
 "cites": [
  "FND-0B651843",
  "FND-1A251687",
…
 ]
}
```

To save it for the agent to paste into a pack:

```bash
python3 $E causal-item $WS --top 12 > causal-item.json
```

## Common problems

- **"Needs causal_graph.json. Run: pmlc.py causal …".** Run [causal](causal.md) first.
- **"causal_graph.json has no links; tell the causal story in para items instead".** The export's causal explanations name no other factors. Describe the causal story in words, citing findings.
- **A crowded diagram.** Keep `--top` small (8 to 15) for a board or frontline audience.

## Related

- [causal](causal.md) builds the graph this reads.
- [check-pack](check-pack.md) checks the cited IDs once the item is in a pack.
- [pack](pack.md) draws the graph in HTML.
