---
name: precursor-timeline
description: Build a precursor and weak-signal timeline from a ProbeMatrix investigation export - every dated warning, missed inspection, repeated repair, overdue action, audit finding or near-miss before the event - showing who received each signal and what was done with it. Use when someone asks "did we see this coming", "what warnings were missed", wants a weak-signals or precursor analysis, a history of the asset before the incident, or material on normalisation of deviance.
---

# Precursor Timeline

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py`.

## Gather candidates

```bash
PMLC timeline <ws> --before incident
```

This lists every dated mention in findings and evidence (`<ws>/timeline_candidates.json`), with snippets and sources. Many are duplicates or context dates (e.g. a commissioning year). The engine finds dates; you decide which are signals.

## Curate

For each candidate keep it only if it is a **signal**: something that could have told someone the risk was rising. Examples: an inspection that found degradation, a repeated repair on the same item, a skipped or overdue maintenance schedule, an audit recommendation left open, a procedure published but not used, a configuration change not documented. Record:

| Field | Content |
|---|---|
| Date | as precise as the source allows; mark year-only dates |
| Signal | what happened, in one line |
| Received by | entity and tier (from `clusters.json` of the citing findings) |
| Response | what was done with it, per the evidence ("none recorded" is an answer) |
| Distance to event | months or years before the incident |
| Evidence | finding and evidence IDs |

Add the event sequence on the day itself as a final block if the narrative gives it.

## Learn

Close with three to six **signal learnings**: patterns in how signals were handled (no escalation path, closure without verification, schedules that slide when a job is late, repeated repairs treated as normal). Each one names the entity and tier that must change the way it handles signals, and a leading indicator.

## Output

Write the pack `<run>/outputs/precursor-timeline.json` (schema: `learnings-coach/references/pack-schema.md`), then:

```bash
PMLC check-pack <ws> <run>/outputs/precursor-timeline.json   # fix every problem it lists
PMLC pack <ws> <run>/outputs/precursor-timeline.json         # -> precursor-timeline.html (primary, vertical timeline) and .md
```

Sections and the kinds that fill them:
- **Curated signals:** one `timeline`. Each row of the Curate table above becomes an event:
  - Date → `date`
  - Signal → `text`; do not write "(N months before)": the renderer computes it from the incident date and shows year-only dates as "c. YYYY (about N years before)"
  - `signal: true`
  - Received by → `received_by`
  - Response → `response` ("None recorded" is an answer)
  - Evidence → `cites`
- **Event sequence on the day:** a second `timeline`, in its own section.
- **Signal learnings:** `learning` ×3–6, with `owner` = the entity and tier that must change. Follow each with its `indicator`.

Put data-quality corrections in `data_quality`, findings left out on purpose in `exclusions`, and same-condition findings in `supporting_cites`.

```json
{"date": "2022-03", "text": "… (24 months before)", "signal": true, "received_by": "Materials Management (F06, T1)",
 "response": "None recorded", "cites": ["FND-…", "EVD-…"]}
```
