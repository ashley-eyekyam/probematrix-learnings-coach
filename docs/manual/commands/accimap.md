# accimap

## What it does

Places every finding on one of Rasmussen's six AcciMap levels, numbered 1 (government policy and budgeting) to 6 (equipment and surroundings), and writes `workspace/accimap.json`. The rules are in `references/accimap.json`. Entities come first: a finding tagged to regulators (F15) goes to level 2; corporate and board (F14), vendors (F16) and contractors (F17) go to level 3, with a `contractor` tag for the last two. Then the HFACS level decides: level 4 goes to 3, level 3 to 4, level 2 with a technological or physical environment subcategory to 6, any other level 2 to 5, and level 1 to 5.

Placements at levels 1 to 3 are marked `inferred`, because they come from codes and entity tags, not from what the export says about the organisation. A level with no placement is listed in `gaps` and drawn as an empty band. Government (level 1) has no default rule, so it is a gap unless a map adds one. The run is recorded in the manifest, so `status` marks the file stale after a re-ingest. A thin export with no corporate or regulator findings still runs: levels 2 and 3 come from the codes only, and a note says so.

## When to use it

Before drawing a systemic AcciMap: it shows which levels the findings reach and which are empty, with the Finding IDs behind each count. A pack that uses the graph item needs the fixed banner about inferred placements, and a person confirms the placements before the map is shared.

## Synopsis

```text
pmlc accimap ws [--map FILE] [--graph-item] [--table-item {levels}] [--json]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder (run `classify` and `causal` first for the entity rules and the links) |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--map` | file | none | A JSON file merged over the built-in rules. It may hold `keywords` (level to a list of regular expressions, matched against a finding's roles and label), and may replace entries under `entities`, `subcategories` or `hfacs_levels`. A bad file stops with one sentence and exit 2 |
| `--graph-item` | none | off | Print a ready `graph` item: one node per level, up to four code nodes under each, and the causal links between them |
| `--table-item` | `levels` | none | Print a ready `table` item with `row_cites` on every row |
| `--json` | none | off | Print the placement as JSON |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E accimap $WS
python3 $E accimap $WS --graph-item
python3 $E accimap $WS --map my-levels.json
```

On Hazira, the placements per level are in the table of the worked example, and levels 1 and 2 are gaps.

## Common problems

- **"Cannot use the AcciMap map".** The map file has a pattern that does not compile, a level outside 1 to 6, or a value of the wrong type. The message names the entry.
- **Levels 1 to 3 look wrong.** They are inferred. Add a `--map` with `keywords`, or correct the placement by hand before the map is shared.
- **"The levels table has no rows".** No finding has an HFACS level the rules can place.

## Related

- [hfacs-profile](hfacs-profile.md) counts the same findings by HFACS level.
- [causal](causal.md) builds the links the graph item draws.
- [causal-item](causal-item.md) prints the plain causal graph.
