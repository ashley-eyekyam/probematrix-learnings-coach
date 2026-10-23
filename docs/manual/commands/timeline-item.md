# timeline-item

## What it does

Turns the dated candidates that [timeline](timeline.md) found into one **timeline item** for a learning pack: events up to a date, in date order, each with the finding and evidence IDs it came from and, when the clusters are known, `received_by` (the cluster and tier of the first finding that mentions it). The pack renderer adds the "(N months before)" label from the incident date.

The candidates are not curated: you decide which are signals, and you add the response and what was knowable then.

With `--event-day` it builds the incident day instead, from the incident narrative: one event per distinct clock time (`hh:mm` or `hh.mm`, so `09.05` and `9:05` are the same time), in clock order. Each event is dated the incident date, shows the whole sentence that first holds the time (a table row counts as one sentence, without its time-only cells), cites the findings whose text holds the same time, and carries `knowable_then: true`. A long candidate snippet is cut at the last space before 240 characters and ends with `…`, so no word is cut in half.

It prints to the screen only; it writes no file.

## When to use it

At the start of a precursor timeline, to have the dates, sources and receivers filled in. Run [timeline](timeline.md) first.

Use `--event-day` for the sequence of the incident day in an emergency-response or precursor pack. It needs no other command first.

## Synopsis

```text
pmlc timeline-item ws [--before BEFORE] [--top TOP] [--event-day]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--before` | `YYYY-MM-DD` or `incident` | required unless `--event-day` | Keep candidates up to this date |
| `--top` | number | 12 | Events to keep: those with the most sources first |
| `--event-day` | none | off | Print the incident-day sequence from the narrative instead of the dated candidates |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E timeline-item $WS --before incident --top 8
python3 $E timeline-item $WS --event-day
```

On Hazira `--event-day` gives 26 events, from 02:11 to 20:00 (the 20:00 event is the night shift taking over on the evening before; clock order puts it last).

## Common problems

- **"Needs timeline_candidates.json. Run: pmlc.py timeline …".** Run [timeline](timeline.md) first.
- **"No incident date in this workspace; pass --date to ingest."** Give an explicit date to `--before`. For the event-day item, ingest the export again and give it the incident date.
- **"timeline-item needs --before YYYY-MM-DD|incident, or --event-day …".** Give one of the two.
- **"No hh:mm times in the incident narrative …".** The `--event-day` item is empty; tell the sequence in `para` items instead.

## Related

- [timeline](timeline.md) finds the candidates.
- [missed-opportunities](missed-opportunities.md) prints the dated candidates that cite an earlier recommendation or a Failure-to-Correct finding.
- [table-item](table-item.md) and [causal-item](causal-item.md) print the other ready-made items.
