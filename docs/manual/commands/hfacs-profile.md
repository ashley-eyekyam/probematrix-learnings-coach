# hfacs-profile

## What it does

Counts the findings of a workspace by HFACS level and subcategory (a heat map with the top-rated findings split out), lists the codes that recur in two or more findings, and counts, for each code, the causal links out and in from `causal_graph.json`. It writes `workspace/hfacs_profile.json` and records it in the manifest, so `status` marks it stale after a re-ingest. A prefix that is not in `hfacs-codes.json` is listed under `unresolved` and noted; it never stops the run. Without a causal graph, `feeds` is empty and a note says so.

For one incident these counts describe this investigation only. They are not rates, trends or a benchmark.

## When to use it

Before writing about latent conditions: it gives the level 3 and 4 share, the recurring codes and the codes that feed many others, each with the Finding IDs behind the number.

## Synopsis

```text
pmlc hfacs-profile ws [--json] [--table-item {heatmap,feeds,recurrence}]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder (run `causal` first for the feed counts) |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--json` | none | off | Print the profile as JSON instead of the summary |
| `--table-item` | `heatmap`, `feeds` or `recurrence` | none | Print a ready `table` item for a pack, with `row_cites` on every row |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E hfacs-profile $WS
python3 $E hfacs-profile $WS --table-item feeds
```

On Hazira, SVI 1.4 recurs in 21 findings and OIC 2.1 has 36 links out in the causal graph.

## Common problems

- **"The feeds table has no rows".** The workspace has no causal graph or it holds no links. Run `causal` first.
- **A prefix under `unresolved`.** The export uses a Nanocode prefix this version does not know. The findings are still counted at the level the export gives.

## Related

- [causal](causal.md) builds the graph the feed counts come from.
- [table-item](table-item.md) prints the other ready tables.
- [profile](profile.md) is the wider workspace profile.
