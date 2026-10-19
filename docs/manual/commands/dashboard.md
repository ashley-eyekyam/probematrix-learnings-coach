# dashboard

## What it does

Writes the **organisation learning map**: one self-contained HTML page (it works offline and can be emailed) that shows the whole investigation by part of the organisation, tier and HFACS level, the interfaces between teams and the causal links. With a Learnings Register it adds the learnings, a plan by tier and the strength of the proposed controls, with a detailed register tab.

The page is built from the workspace; it adds nothing that is not in the export or the register.

## When to use it

For an overview meeting, a safety committee, or anyone who asks "where in the organisation does this investigation point?". Run [classify](classify.md) first. Add `--register` once a register has passed [check-register](check-register.md).

## Synopsis

```text
pmlc dashboard ws [--out OUT] [--register REGISTER] [--title TITLE] [--date DATE] [--location LOCATION]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--out` | file | `<run>/outputs/organisation-learning-map.html` | Where to write the page |
| `--register` | file | none | A Learnings Register JSON: adds the learnings, tier plan and control-strength sections |
| `--title` | text | the export's incident title | The incident title in the page header |
| `--date` | `YYYY-MM-DD` | the export's date | The incident date in the header. Use it when the summary sheet is wrong |
| `--location` | text | the export's location | The location in the header |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

The learning map with the sample register, as published in the repository's sample folder:

```bash
python3 $E dashboard $WS --register $OUT/learnings-register.json
```

```text
Dashboard written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/organisation-learning-map.html
```

A second copy with a clearer title than the export's "Hazira 2020":

```bash
python3 $E dashboard $WS --title "Hazira gas terminal release and fire" --out $OUT/map-retitled.html
```

```text
Dashboard written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/map-retitled.html
```

## Common problems

- **"Needs clusters.json".** Run [classify](classify.md) first.
- **The header shows the wrong date or title.** The export's summary sheet is wrong. Override it with `--date`, `--title` or `--location`; better, correct it in ProbeMatrix and export again.
- **The register sections are missing.** Pass `--register`. Check the register first with [check-register](check-register.md).
- **The page says draft.** Its status follows the investigation and the register's sign-off, as for a pack. See [Review and sharing](../Review-and-sharing.md).

## Related

- [check-register](check-register.md) and [register-xlsx](register-xlsx.md) for the register.
- [interfaces](interfaces.md) and [causal](causal.md) give the same data as tables.
- [Skills](../Skills.md): the `organisation-learning-map` skill explains the map to its readers.
