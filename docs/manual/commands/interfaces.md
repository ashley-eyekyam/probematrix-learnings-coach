# interfaces

## What it does

Finds the **interfaces** between parts of the organisation: pairs of entities (for example Operations and Mechanical Maintenance) that the investigation links. Many incidents grow in the gaps between teams, so these pairs are where shared learning matters most. For each pair it counts:

- **shared findings**: findings whose roles include both entities;
- **cross-entity causal mentions**: a finding of one entity names, in its causal explanation, a factor that belongs to the other entity.

Unmapped roles (F99) are left out. It writes `interfaces.json` to the workspace (every pair, with up to ten example Finding IDs) and prints the strongest pairs.

## When to use it

For the interface-learnings skill, a site leadership brief, or any question about "who needs to talk to whom". Run [classify](classify.md) first.

## Synopsis

```text
pmlc interfaces ws [--top TOP]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--top` | number | 25 | How many pairs to print. The file always holds every pair |
| `--json` | none | off | Print one JSON object on stdout instead of the report: `{command, ok, exit_code, output}` plus, for this command, `pairs` (`a`, `b`, `shared_findings`, `cross_causal_mentions`, `examples`) and `written`, read back from `interfaces.json`. On failure `ok` is false and `error` holds the reason. Messages go to stderr. The exit code is the same as without `--json` |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E interfaces $WS --top 6
```

```text
| Interface | Shared findings | Cross-entity causal mentions |
|---|---:|---:|
| F01 Operations & Control Room ↔ F02 Mechanical Maintenance | 71 | 391 |
| F02 Mechanical Maintenance ↔ F08 Work Management & Planning | 27 | 213 |
| F02 Mechanical Maintenance ↔ F07 Engineering, Design, Documents & MOC | 34 | 189 |
| F02 Mechanical Maintenance ↔ F05 Asset Integrity, Corrosion & Inspection | 40 | 166 |
| F02 Mechanical Maintenance ↔ F13 Plant & Asset Leadership | 18 | 227 |
| F02 Mechanical Maintenance ↔ F04 Instrumentation, Control & Calibration | 6 | 253 |

Wrote hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/workspace/interfaces.json (125 pairs across 17 entities).
```

The pairs are ranked by three times the shared findings plus the causal mentions, so a pair the investigation names together often comes first.

To read the findings behind the first pair:

```bash
python3 $E select $WS --entity F01 F02 --entity-mode all --brief
```

## Common problems

- **"Needs clusters.json. Run: pmlc.py classify <ws>".** Run [classify](classify.md) first.
- **Many pairs include one large entity.** In Hazira, Mechanical Maintenance appears in most pairs because most findings involve it. Look at the shared findings, not only the order.
- **Counts are of mentions, not of separate problems.** Several findings can describe one condition. Count learnings, not finding instances.

## Related

- [select](select.md) (`select --entity-mode all`) lists the shared findings of a pair.
- [classify](classify.md) decides which entities a finding touches.
- [Skills](../Skills.md): `interface-learnings` and `supply-chain-contractor-learnings` use this.
