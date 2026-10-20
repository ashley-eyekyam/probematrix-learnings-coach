# causal

## What it does

Builds a **causal graph**: which factors the investigation says led to which. ProbeMatrix writes a causal explanation for each finding ("Enabled by SV 1.4 and OR 2.2"); causal reads every explanation, picks out the factor codes it names, and counts each link from one factor to another. A link always points from the higher HFACS level to the lower one (from the organisation towards the act), whichever finding mentions it. If the export has a Causal Chain sheet, its rows are added.

It writes `causal_graph.json` (every link) and `causal_graph.mmd` (a Mermaid diagram of the top links) to the workspace, and prints the top links as a table.

## When to use it

Before writing a causal map, a board brief or a barrier analysis, to see which upstream conditions (levels 3 and 4) most often enabled the acts and conditions at levels 1 and 2. [causal-item](causal-item.md) turns the same links into a ready graph for a pack.

## Synopsis

```text
pmlc causal ws [--top TOP] [--include-justification] [--hubs]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--top` | number | 60 | How many links to print and to draw in the Mermaid file. `causal_graph.json` always holds every link |
| `--include-justification` | none | off | Also read factor codes from the AI justification text, not only the causal explanation. This finds more links, but some are mentions rather than causes |
| `--hubs` | none | off | Also print the factors with the most links out, with their level and mentions |
| `--json` | none | off | Print one JSON object on stdout instead of the report: `{command, ok, exit_code, output, ...}`, where `output` holds the report's lines and some commands add fields (`problems`, `warnings`, `stats`, `hits`). Messages go to stderr. The exit code is the same as without `--json` |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E causal $WS --top 8
```

```text
287 of 436 findings name other factors in their causal explanation. 555 distinct links. Wrote causal_graph.json and causal_graph.mmd (top 8).

| From | To | Mentions |
|---|---|---:|
| OIR 1.6 (L4) | SVF 3.4 (L3) | 7 |
| OIR 1.6 (L4) | SVV 4.1 (L3) | 6 |
| SVI 1.1 (L3) | ASBE 1.2 (L1) | 6 |
| SVI 1.4 (L3) | ASBE 1.2 (L1) | 6 |
| SVI 1.4 (L3) | PTE 2.7 (L2) | 6 |
| OIC 2.1 (L4) | AV 1.1 (L1) | 5 |
| OIC 2.7 (L4) | AJDE 2.11 (L1) | 5 |
| OIC 2.7 (L4) | ASBE 1.2 (L1) | 5 |
```

Read as: "a failure in the maintenance, spares and support programme (OIR 1.6, level 4) is named seven times as leading to an ineffective action against an identified risk (SVF 3.4, level 3)".

Adding the justification text:

```bash
python3 $E causal $WS --top 3 --include-justification
```

```text
287 of 436 findings name other factors in their causal explanation. 675 distinct links. Wrote causal_graph.json and causal_graph.mmd (top 3).

| From | To | Mentions |
|---|---|---:|
| SVI 1.4 (L3) | ASBE 1.2 (L1) | 8 |
| SVI 1.4 (L3) | PTE 2.7 (L2) | 8 |
| OIR 1.6 (L4) | SVF 3.4 (L3) | 7 |
```

Ties in the tables are ordered by factor code, so two runs print the same order.

## Common problems

- **A count is a number of mentions, not a measure of strength.** Several findings can describe the same link in different words. Count learnings, not mentions.
- **The graph changed after a run with `--include-justification`.** Each run overwrites `causal_graph.json`. Run causal again without the flag to go back.
- **Few links.** The export's causal explanations name few factor codes. The profile's data-quality flags say whether the Causal Chain sheet is empty.

## Related

- [causal-item](causal-item.md) gives the top links as a pack graph item.
- [table-item](table-item.md) prints the hubs as a pack table.
- [interfaces](interfaces.md) counts causal links that cross between departments.
- [Skills](../Skills.md): `causal-map` and `barrier-learnings` use this graph.
