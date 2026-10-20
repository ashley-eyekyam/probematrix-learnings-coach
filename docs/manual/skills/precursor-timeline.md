# precursor-timeline

A timeline of the warnings before the event: dated inspections that found degradation, repeated repairs, overdue schedules, open audit recommendations and near-misses. For each signal it shows who received it and what was done with it, and it keeps only signals that someone could actually have seen at the time.

## What it is for

- "Did we see this coming?" and "What warnings were missed?"
- A weak-signals or precursor analysis.
- The history of an asset before the incident.
- Material on normalisation of deviance: how a repeated deviation came to feel normal.

## How to start it

- "Build a precursor timeline of the warnings before this event."
- "What signals did the organisation receive in the years before the fire, and what happened to them?"
- "Show the history of the meter before the incident, with who knew what and when."

## What it needs

- A workspace with `clusters.json`, so each signal can name the function and tier that received it.
- The incident date. The engine uses the summary-sheet date, or the `--date` given at ingest.

## Engine commands and flags

```bash
pmlc timeline <ws> --before incident                  # every dated mention before the event
pmlc timeline-item <ws> --before incident --top 12    # the same candidates as a ready timeline item
pmlc timeline <ws> --on incident                      # clock times on the day -> timeline_event_day.json
pmlc check-pack <ws> <run>/outputs/precursor-timeline.json --strict
pmlc pack <ws> <run>/outputs/precursor-timeline.json
```

- [timeline](../commands/timeline.md) lists every dated mention in findings and evidence in `timeline_candidates.json`. `--before incident` keeps only dates up to the incident date, and `--on incident` writes the clock times of the day. Other flags: `--entity` (one function's findings), `--min-precision` (drop year-only dates), `--per-date` and `--show` (how much it prints).
- [timeline-item](../commands/timeline-item.md) prints the candidates as a ready `timeline` item, with each event's date, the function that received it and its citations. The agent keeps the dates and citations as printed, drops the events that are not signals and adds the response and what was knowable then. `--top` sets how many events it keeps.
- [check-pack](../commands/check-pack.md) with `--strict` and [pack](../commands/pack.md) check and render the pack.

The engine finds dates; the agent decides which are signals. Many candidates are duplicates or context dates, such as the year a plant was built. This skill uses no `select` filters.

## What you get

`precursor-timeline.html` (a vertical timeline) and `.md`:

- **Signals before the event:** each with its date, what happened, who received it, the response ("None recorded" is an answer), what was knowable then and its evidence. The page works out "N months before" from the incident date, and shows year-only dates as "c. YYYY".
- **The event sequence:** a second timeline for the day itself.
- **Signal learnings:** up to six patterns in how signals were handled, each with the function and tier that must change and a leading indicator.

On an export with no dated text, or only year-only dates, the timeline shows the order the findings state, marks unknown dates as unknown, and says it is partial.

## Worked example (Hazira)

`timeline --before incident` wrote 92 dated precursor candidates (98 without `--before`). The earliest is 1986, from evidence that says "the meter is very old (1986)": a context date, not a signal. Later candidates include the thickness measurements of 2011 and 2017, and the change-control procedure published in August 2016 but not used since 2018. These are the kind of entries the agent keeps as signals, after checking what each receiver could know at that moment.

`timeline-item --before incident --top 12` printed a timeline item with 12 events; the first, dated 2018-11, is the recurring sealing failures on the meters, received by Mechanical Maintenance (F02, T2).

## Related skills

- [causal-map](causal-map.md): the same conditions as links rather than dates.
- [board-brief](board-brief.md) and [site-leadership-coach](site-leadership-coach.md): use the signals that reached senior levels.
- [emergency-response-learnings](emergency-response-learnings.md): the clock times on the day itself.
