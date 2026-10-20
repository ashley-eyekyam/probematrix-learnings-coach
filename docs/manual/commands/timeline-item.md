# timeline-item

## What it does

Turns the dated candidates that [timeline](timeline.md) found into one **timeline item** for a learning pack: events up to a date, in date order, each with the finding and evidence IDs it came from and, when the clusters are known, `received_by` (the cluster and tier of the first finding that mentions it). The pack renderer adds the "(N months before)" label from the incident date.

The candidates are not curated: you decide which are signals, and you add the response and what was knowable then.

It prints to the screen only; it writes no file.

## When to use it

At the start of a precursor timeline, to have the dates, sources and receivers filled in. Run [timeline](timeline.md) first.

## Synopsis

```text
pmlc timeline-item ws --before BEFORE [--top TOP]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--before` | `YYYY-MM-DD` or `incident` | required | Keep candidates up to this date |
| `--top` | number | 12 | Events to keep: those with the most sources first |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E timeline-item $WS --before incident --top 8
```

## Common problems

- **"Needs timeline_candidates.json. Run: pmlc.py timeline …".** Run [timeline](timeline.md) first.
- **"No incident date in this workspace; pass --date to ingest."** Give an explicit date to `--before`.

## Related

- [timeline](timeline.md) finds the candidates.
- [table-item](table-item.md) and [causal-item](causal-item.md) print the other ready-made items.
