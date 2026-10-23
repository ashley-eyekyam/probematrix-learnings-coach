---
name: precursor-timeline
description: Builds a precursor and weak-signal timeline from a ProbeMatrix investigation export - every dated warning, missed inspection, repeated repair, overdue action, audit finding or near-miss before the event, who received each signal, what was done with it and whether it was knowable then - with signal learnings and leading indicators. Use when someone with a ProbeMatrix export asks "did we see this coming", "what warnings were missed", wants a weak-signals or precursor analysis, a history of the asset before the incident, or material on normalisation of deviance. Not for how the factors connect (use `causal-map`).
---

# Precursor Timeline

Engine: `PMLC` as in `learnings-coach/references/skill-common.md` §1; this skill needs the `learnings-coach` skill installed alongside it.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions; run `PMLC setup`
when only an .xlsx was given). Needs: `workspace`, `timeline` (`setup` writes `timeline_candidates.json`).
Optional: the register. Read `learnings-coach/references/learning-principles.md`, especially the knowable-then
test in §1a, and `learnings-coach/references/indicators-and-effectiveness.md` for the indicators.

## Gather

```bash
PMLC timeline <ws> --before incident                     # every dated mention before the event, with snippets
PMLC timeline-item <ws> --before incident --top 12       # the same candidates as a ready timeline item
PMLC timeline <ws> --on incident                         # clock times on the day -> timeline_event_day.json
PMLC missed-opportunities <ws>                           # -> missed_opportunities.json: the three sets, counted
PMLC missed-opportunities <ws> --timeline-item --top 12  # the dated missed opportunities as a ready timeline item
```

The engine finds dates; you decide which are signals. Many candidates are duplicates or context dates (a
commissioning year). Start from the `timeline-item` output: keep each kept event's `date`, `received_by` and
`cites` exactly as printed, drop the events that are not signals, rewrite `text` as one line, and add the fields
below. The renderer computes "(N months before)" from the incident date and shows a year-only date as
"c. YYYY (about N years before)", so never write the distance yourself.

Keep an event only if it is a **signal**: something that could have told someone the risk was rising **and that
they could see then**. Examples: an inspection that found degradation, a repeated repair on the same item, a
skipped or overdue schedule, an audit recommendation left open, a procedure published but not used, a
configuration change not documented.

## Write

Write `<run>/outputs/precursor-timeline.json` in the shape in `learnings-coach/references/pack-schema.md`.

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/precursor-timeline.json (repository only).

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | The longest-running or most repeated signal, and what was done with it | `bottom_line` | up to 7 |
| 1 | `signals` | Signals before the event | One timeline. Each event: `date` (as precise as the source allows), `text` (the signal in one line), `signal: true`, `received_by` (entity and tier), `response` ("None recorded" is an answer), `knowable_then` (what the receiver could know at that moment; leave out hindsight-only signals), `cites` | `timeline` | 1 |
| 2 | `missed` | Missed opportunities | One timeline from `missed-opportunities --timeline-item` (below): each event a dated chance to learn, citing a finding that names a recommendation or a failure to correct, with `knowable_then` and `response` | `timeline` | optional, up to 1 |
| 3 | `event-day` | The event sequence | A second timeline, from `timeline_event_day.json` and the narrative: what happened on the day, in order; `knowable_then` on each event | `timeline` | 1 |
| 4 | `signal-learnings` | Signal learnings | Patterns in how signals were handled (no escalation path, closure without verification, schedules that slide when a job runs late, repeated repairs treated as normal); `owner` = the entity and tier that must change how it handles signals | `learning` | up to 6 |
| 4 | `signal-learnings` | Signal learnings | One leading indicator after each learning: what the owner will count, from which record | `indicator` | up to 6 |

Carry `learning: "LR-nn"` on a signal learning that expresses a register learning (`skill-common.md` §3).
Every event of every timeline carries `knowable_then` (profile rule `knowable-then`): text, or `true`/`false`.

**Missed opportunities** (`missed`). Start from the `--timeline-item` output: keep its `date`s and choose the events
whose `cites` hold a finding from `prior_recommendation` or `failure_to_correct` in `missed_opportunities.json`;
narrow `cites` to those findings plus their evidence. Rewrite `text` as the chance to learn, add `response` (what
was done with it) and replace `knowable_then: true` with what was on record then. A finding in the
`prior_recommendation` set may quote the investigation's own later recommendation: place the event for what was on
record at its date, and never present a later recommendation as one that existed then. Leave the section out when
the item is empty.

```json
{"date": "2022-03", "text": "Seals bought locally without a specification", "signal": true,
 "received_by": "Materials Management (F06, T1)", "response": "None recorded",
 "knowable_then": "The purchase record was visible to Stores at the time.", "cites": ["FND-0003", "EVD-0003"]}
```

## If the evidence is thin

Follow `skill-common.md` §6, and:
- **Undated export** (the profile flags no dated text, or `timeline` finds no candidates before the event): write
  the signal learnings from the undated L2–L4 findings, keep the `signals` timeline to the signals whose order
  the findings state, mark each unknown date as unknown, and add a `limits` line that the timeline is partial.
- **Year-only dates:** keep them as year-only (`"2019"`); never sharpen one to a month or a day. Say in the
  section intro that the order within a year is not known.
- **No times on the day:** the `event-day` timeline gives the order only, from the narrative; say so.
- **No response recorded anywhere:** write "None recorded" per event; do not read it as "ignored".

## Not covered here

- How the factors connect as a causal chain: `causal-map`.
- Which barriers were degraded on the day: `barrier-learnings`.
- Why earlier recommendations and failures to correct did not lead to change, step by step through the learning
  cycle: `failure-to-learn-review`. The same `missed-opportunities` engine feeds both; here they are placed on the
  timeline as the `missed` events that were knowable then.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/precursor-timeline.json --strict   # fix every problem it lists
PMLC pack <ws> <run>/outputs/precursor-timeline.json                  # -> precursor-timeline.html (vertical timeline) and .md
PMLC pack <ws> <run>/outputs/precursor-timeline.json --layout poster  # -> precursor-timeline.poster.html, one A3 page
```

The poster prints the bottom line, up to six signal learnings and the first timeline across one A3 landscape
page, for a control room or a canteen wall; add `--base-url <URL>` to print a QR code to the published pack.
Tell the user how many signals and missed opportunities were kept, how far back the earliest goes, and which had
no recorded response.
