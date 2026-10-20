# compare

## What it does

Reads a **comparator inventory** (the numbered observations, root causes, recommendations or actions of another report, or of the organisation's own action plan) and a **comparison map** (which learning matches which comparator item), and prints ready-made tables for a pack: counts by item type, coverage in both directions (yes, partial, none), the control-tier profile of the comparator's recommendations, and a cross-tab of the comparator's groups against the learnings' owner entities.

It checks the inventory first: item ids must look like `OBS-01`, `RC-01`, `REC-01` or `ACT-01`, be unique and fit their type, and every mapping row must name a real item and a match of `yes`, `partial` or `none`. Any problem is listed and the command exits 1.

When `comparator.json` has `source.kind` set to `own-action-plan`, the output says "against the organisation's action plan".

## When to use it

In the [report-comparison](../skills/report-comparison.md) skill, after you have written `comparator.json` and `comparison-map.json` in the workspace. See `references/comparison-method.md` for the file shapes.

## Synopsis

```text
pmlc compare ws [--comparator COMPARATOR] [--mapping MAPPING] [--register REGISTER]
                [--client-safe PACK] [--main PACK] [--json]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--comparator` | file | `<ws>/comparator.json` | The comparator inventory |
| `--mapping` | file | `<ws>/comparison-map.json` | The learning-to-item map. A missing file counts every item as unmapped |
| `--register` | file | none | A Learnings Register JSON: all its learnings count (an unmapped learning is `none`), mapping rows must name its LR-IDs, and the owner cross-tab is printed |
| `--client-safe` | pack file | none | Check that this pack has the same section ids as the main pack. Needs `--main` |
| `--main` | pack file | none | The main pack `--client-safe` is compared with |
| `--json` | none | off | Print the tables as pack items (JSON) instead of Markdown |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E compare $WS --register $RUN/outputs/learnings-register.json
python3 $E compare $WS --json > compare-items.json
```

## Common problems

- **"id ... must look like OBS-01 ..."**. Renumber the item with its type prefix and at least two digits.
- **"client-safe pack lacks section ..."**. The client-safe variant must keep every section id of the main pack; change the content, not the structure.

## Related

- [select](select.md) (with its in-evidence option) finds the findings behind a comparator quotation.
- [check-pack](check-pack.md) validates `comparator_refs` against `comparator.json`.
