# nine-m-seed

## What it does

Scores every finding against the nine Ms (M1 Manpower/Mindpower to M9 Maintenance) and prints the M profile: for each M, the findings whose Nanocode points to it, split by HFACS level and by rating, how many are top-rated, how many carry it as a secondary M or only as a weaker signal, its most frequent Nanocodes and its top-rated findings. It ends with the unmapped findings, which should be none.

A finding scores 3 for its Nanocode's primary M, 1 for each secondary M of that Nanocode, 1 for an M whose keywords appear in its Instance Label or Short Description, and 1 for an M whose Learning Cluster entities it belongs to. The Nanocode's primary M is the finding's primary M. Any other M that two signals agree on joins its secondary list. The map is `references/nine-m-map.json`, and `references/nine-m.md` explains the Ms and how they overlap.

It writes `<ws>/nine_m_seed.json`, which `status` tracks: re-run it after a new `ingest` or `classify`.

## When to use it

At the start of a 9M analysis, before the first question to the user, so that the scope question can show which Ms the export already points to. Other skills can read the same file to look at findings through the 9M lens.

## Synopsis

```text
pmlc nine-m-seed ws [--map MAP] [--out OUT]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder. A ProbeMatrix CAPA Planner workbook is refused, and so is any other file: run `setup` on the findings export and pass the workspace it prints |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--map` | file | `references/nine-m-map.json` | Your own 9M map, in the same format (`prefixes`, `codes`, `keywords`, `entities`). Its `version` is recorded in the output |
| `--out` | file | `<ws>/nine_m_seed.json` | Where to write the seed. Only the default path is recorded for `status` |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E nine-m-seed $WS
```

On Hazira all 436 findings map to an M and none is unmapped. The primary split is M1 72, M2 13, M3 95, M4 40, M5 13, M6 130, M7 37, M8 9 and M9 27. Material (M8) and Maintenance (M9) are under-coded: few Nanocodes point to them, but their keywords appear in 144 and 217 findings. That is why the 9M skill asks about every M instead of reading only the codes.

```bash
python3 $E nine-m-seed $WS --map my-site-nine-m-map.json --out /tmp/seed.json
```

## Common problems

- **"This is a ProbeMatrix CAPA Planner workbook. nine-m-analysis reads the findings export only (Identified Findings); export that instead."** You passed the CAPA Planner download (exit code 2). Export the investigation's findings from ProbeMatrix, run `setup` on that file, and pass the workspace.
- **"nine-m-seed reads a workspace folder, not …".** You passed a file, such as the findings export itself (exit code 2). Run `setup` first.
- **"… not a 9M map (…)".** Your `--map` file names an M outside M1 to M9, has a keyword that is not a valid regular expression, or is missing an object. Start from `references/nine-m-map.json`.
- **"Unmapped: n".** A Nanocode prefix is not in the map. The note under the table names it. Add the prefix to your map and pass it with `--map`.
- **"No clusters.json: the entity signal was not used".** Run `classify` first. The seed still works on the Nanocode and keyword signals.

## Related

- [select](select.md) picks the findings for one audience or question.
- [classify](classify.md) builds the Learning Clusters that give the entity signal.
- [status](status.md) shows when `nine_m_seed.json` is stale.
