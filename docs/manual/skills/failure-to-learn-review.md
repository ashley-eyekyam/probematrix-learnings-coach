# failure-to-learn-review

A review of why earlier warnings did not lead to change. It reads the findings that describe a known problem left uncorrected, the findings that cite an earlier recommendation or audit, the dated warnings before the event, and the culture findings, and it names which step of the learning cycle broke: reporting, investigation and analysis, planning interventions, intervening or evaluating. Its learnings are about the organisation (level 4), not about the people who were there.

## What it is for

- "Why didn't we learn from the earlier leaks?" and "Why were the audit recommendations never closed?"
- A learning-from-incidents or failure-to-learn review for site leadership, top management or the board.
- Material on drift and normalisation: how a practice moved away from the procedure in small steps.

## How to start it

- "Why did none of the earlier warnings before this fire lead to a change?"
- "Where did our learning process break down: reporting, analysis, planning, action or follow-up?"
- "Show the board why the overdue audit actions and the repeat repairs were never acted on."

## What it needs

- A workspace with `timeline_candidates.json` (`setup` writes it).
- `missed_opportunities.json`, which the skill writes with `missed-opportunities` in its first step.
- Optional: the Learnings Register, so each learning carries its `LR-` id.

## Engine commands and flags

```bash
pmlc missed-opportunities <ws>                    # the four sets and their counts
pmlc missed-opportunities <ws> --timeline-item    # the dated missed opportunities as a ready timeline item
pmlc missed-opportunities <ws> --json             # the finding lists, including the drift-wording findings
pmlc select <ws> --subcategory "Failure to Correct Known Problem" --brief
pmlc select <ws> --subcategory "Organisational Climate/ Culture Influences" --brief
pmlc check-pack <ws> <run>/outputs/failure-to-learn-review.json --strict
pmlc pack <ws> <run>/outputs/failure-to-learn-review.json --format docx   # a Word paper
pmlc pack <ws> <run>/outputs/failure-to-learn-review.json --format pptx   # a slide deck
```

- [missed-opportunities](../commands/missed-opportunities.md) writes `missed_opportunities.json`: the findings that cite an earlier recommendation, the Failure-to-Correct findings, the dated candidates before the incident that cite them, and the findings whose justification uses drift wording. `--timeline-item` prints the dated ones as a timeline with `knowable_then` on every event; `--top` keeps the entries that cite the most findings.
- [select](../commands/select.md) with `--subcategory` reads the Failure-to-Correct and culture findings; `--brief` leaves out the long text. `select --preset failure-to-learn-review` runs both calls at once.
- [check-pack](../commands/check-pack.md) with `--strict` and [pack](../commands/pack.md) check and render the pack.

In this pack the hindsight wording rules are errors, not warnings: "failed to", "should have" (JC3) and "obviously", "clearly should" (JC4) stop `check-pack` even without `--strict`. Every event on the timeline must say what was knowable then.

## What you get

`failure-to-learn-review.html` and `.md`, and with `--format docx` or `pptx` a Word paper or a slide deck:

- **Where the learning cycle broke:** a table with one row per phase of the five-phase cycle, what the export shows at that phase, and its citations. A phase the export says nothing about says so.
- **Missed opportunities:** the dated warnings before the event, each with the response recorded and what was knowable at that moment.
- **How practice drifted:** what became normal, and how, from the drift wording and the culture findings.
- **Learnings for the organisation:** up to six, each citing at least one level-4 finding, with the function that owns the change.
- **A note on hindsight:** what the review knows that the people at the time did not.

## Worked example (Hazira)

`missed-opportunities` found 107 findings that cite an earlier recommendation, 40 Failure-to-Correct findings, 34 dated candidates before 24 September 2020 that cite them, and 41 findings with drift wording. The two `select` calls returned the 40 Failure-to-Correct findings and 51 culture findings.

The golden pack keeps 11 of the 34 dated entries, from the thickness measurements of 2011 to the gasket job of 18 September 2020, and leaves out the context dates (the meter's 1986 build) and a repair date the evidence itself doubts. Its cycle table shows a break at every phase: repeat seal jobs closed as routine (reporting), audits without filled checklists (investigation), the 2017 wall-loss report with no corrective plan (planning), external-audit actions extended without the required approval (intervening), and jobs and drills closed with no check that they worked (evaluating). Its six learnings carry `LR-04`, `LR-05`, `LR-06`, `LR-17`, `LR-20` and `LR-21` from the register. It also notes that some findings cite the post-incident committee's recommendations, which are not missed opportunities.

## Related skills

- [precursor-timeline](precursor-timeline.md): the dated warning signs on their own, with who received each.
- [site-leadership-coach](site-leadership-coach.md): the site leadership team's decisions and workshop.
- [board-brief](board-brief.md) and [top-management-brief](top-management-brief.md): carry the learnings to those audiences.
