# table-item

## What it does

Prints one ready-made **table item** for a learning pack, built from the workspace: a JSON object with `"kind": "table"`, its `columns`, `rows`, one list of Finding or Evidence IDs per row in `row_cites`, and `cites` (all of them together). The agent pastes it into a pack section, so the counts in the pack come from the data, not from retyping.

The kinds are `clusters`, `tiers` and `relations` (findings counted per learning cluster, tier or relation), `entity-tier` (one cluster's findings by tier), `hubs` (factors with the most causal links out), `interfaces` (pairs of clusters that share findings), `evidence-types`, `hoc` (recommendations by hierarchy-of-controls tier), `adoption` (what your organisation recorded in `adoption.csv`) and `nine-m` (the register's learnings per M of the 9M lens, from their `nine_m` values). Rows are sorted by count, ties by ID, except `nine-m`, which keeps M1 to M9 in order. Each row cites at most five findings, the highest rated first.

It prints to the screen only; it writes no file.

## When to use it

While writing a pack that shows a count or a comparison. Run [classify](classify.md) first for the cluster tables, [causal](causal.md) for `hubs` and [interfaces](interfaces.md) for `interfaces`.

## Synopsis

```text
pmlc table-item ws {clusters,tiers,relations,hubs,interfaces,evidence-types,entity-tier,hoc,adoption,nine-m} [--entity F] [--level N [N ...]] [--top TOP] [--register REGISTER] [--pack PACK]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |
| `kind` | Which table: `clusters`, `tiers`, `relations`, `hubs`, `interfaces`, `evidence-types`, `entity-tier`, `hoc`, `adoption` or `nine-m` |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--entity` | cluster ID such as `F02` | none | The cluster for `entity-tier` (required for that kind) |
| `--level` | one or more of 1 to 4 | all | Count only findings of these HFACS levels (`clusters`, `tiers`, `relations`, `entity-tier`) or factors of these levels (`hubs`) |
| `--top` | number | 15 | Rows to keep |
| `--register` | file | `<run>/outputs/learnings-register.json` for `adoption` and `nine-m` | Register whose recommendations `hoc` counts, whose findings `adoption` cites, or whose learnings `nine-m` counts per M |
| `--pack` | file | none | Pack whose recommendation and barrier items `hoc` counts (`hoc` needs `--register` or `--pack`). For every kind, the ids that pack lists in `exclusions` are removed from `row_cites` and `cites`, so the table never cites a finding the pack leaves out; a row left with no cites keeps an empty list |
| `-h`, `--help` | none | | Show the flags and stop |

The `kind` argument takes one of `clusters`, `tiers`, `relations`, `hubs`, `interfaces`, `evidence-types`, `entity-tier`, `hoc`, `adoption` or `nine-m`.

## Examples

```bash
python3 $E table-item $WS tiers --level 3 4
python3 $E table-item $WS entity-tier --entity F02
python3 $E table-item $WS hoc --register $RUN/outputs/learnings-register.json
```

With no `adoption.csv` yet, `adoption` prints one row that reads `No adoption record yet: run PMLC templates <ws> adoption and fill it in`.

`nine-m` has the columns M, Name, Learnings, Priority 1 and LR-IDs: nine rows, M1 to M9, with an M that holds no learning kept as a row of zeros (LR-IDs `none`), and a last row `none`, "No 9M value recorded", when some learnings have no `nine_m`. Each row cites the first five findings of its learnings.

```bash
python3 $E table-item $WS nine-m --register $RUN/outputs/learnings-register.json
```

## Common problems

- **"Needs clusters.json. Run: pmlc.py classify <ws>".** Run [classify](classify.md) first.
- **"table-item hoc needs --register or --pack".** Say where the recommendations are.
- **"The register has no nine_m values".** `nine-m` counts the register's `nine_m` field (`M1` to `M9`), which the `learnings-register` skill copies from the `nine-m-analysis` outputs. Without any value there is no table to print; the command exits 1.
- **check-pack says "FND-0007 is also cited at …".** A table row cites a finding that the pack leaves out in `exclusions`. Run `table-item` again with `--pack` pointing at the pack: it drops excluded ids from the table's cites. The message also gives the path of the cite; remove the id there, or remove it from `exclusions`. A pack either cites a finding or leaves it out on purpose.
- **A count is a number of findings, not a measure of strength.** Count learnings, not findings.

## Related

- [templates](templates.md) writes the blank `adoption.csv`.
- [causal-item](causal-item.md), [timeline-item](timeline-item.md) and [register-items](register-items.md) are the other ready-made items.
- [check-pack](check-pack.md) checks the item once it is in a pack.
