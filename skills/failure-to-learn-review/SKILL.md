---
name: failure-to-learn-review
description: Explains why earlier warnings did not lead to change, from a ProbeMatrix investigation export - the Failure-to-Correct findings, the findings that cite earlier recommendations or audits, the dated missed opportunities, and the culture findings and drift wording - and names which step of the five-phase learning cycle (reporting, investigation, planning interventions, intervening, evaluating) broke, with level-4 learnings for site leadership, top management and the board. Use when someone asks "why didn't we learn from the earlier leaks", "why were the audit recommendations never closed", wants a failure-to-learn or learning-from-incidents review, or material on drift and normalisation. Not for the dated list of warning signs (use `precursor-timeline`), nor for the site leadership team's decisions and workshop (use `site-leadership-coach`).
---

# Failure-to-Learn Review

Engine: `PMLC` as in `learnings-coach/references/skill-common.md` §1; this skill needs the `learnings-coach` skill installed alongside it.

Audience: site leadership, top management and the board. They own the systems that turn a warning into a change:
reporting routes, reviews, action tracking and the follow-up check. Read
`learnings-coach/references/learning-principles.md`, especially the knowable-then test in §1a and the sources in §1b.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions; run `PMLC setup`
when only an .xlsx was given).

Needs: `workspace`, `timeline` (`setup` writes `timeline_candidates.json`) and `missed-opportunities` (run
`PMLC missed-opportunities <ws>` below). Optional: the register (`<run>/outputs/learnings-register.json`); when it
exists, carry `learning: "LR-nn"` on every learning that expresses a register learning (`skill-common.md` §3).

## Gather

```bash
PMLC missed-opportunities <ws>                    # counts: earlier recommendations, Failure to Correct, dated, drift
PMLC missed-opportunities <ws> --timeline-item    # the dated missed opportunities as a ready timeline item
PMLC missed-opportunities <ws> --json             # the finding lists, including the drift-wording findings
PMLC select <ws> --subcategory "Failure to Correct Known Problem" --brief
PMLC select <ws> --subcategory "Organisational Climate/ Culture Influences" --brief
```

`select --preset failure-to-learn-review` runs the two select calls at once. The first command writes
`<ws>/missed_opportunities.json`: the findings whose justification cites an earlier recommendation, the
Failure-to-Correct findings, the dated candidates before the incident that cite either set, and the findings whose
justification uses drift wording (routine, normalised, informal, had become). The engine finds them; you decide
which step of the cycle each one shows.

## Write

Write `<run>/outputs/failure-to-learn-review.json` in the shape in `learnings-coach/references/pack-schema.md`.
Set `"scope": {"levels": [3, 4]}`.

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/failure-to-learn-review.json (repository only).

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | Which steps of the cycle broke, one sentence each | `bottom_line` | up to 5 |
| 1 | `cycle` | Where the learning cycle broke | The five-row cycle table (below) | `table` | 1 |
| 2 | `missed` | Missed opportunities | The `--timeline-item` output, curated (below); every event keeps `knowable_then` | `timeline` | 1 |
| 3 | `drift` | How practice drifted | What became normal and how, from the drift-wording and culture findings. Practices, not people | `para` | up to 3 |
| 4 | `learnings` | Learnings for the organisation | Why the system did not turn the warnings into change; every one cites at least one level-4 finding; `owner` = the function that owns the change | `learning` | up to 6 |
| 5 | `hindsight` | A note on hindsight | One paragraph: the review knows the outcome, the people then did not; what this pack does about it | `para` | 1 |

**The cycle table.** Columns `Phase` and `What the export shows`, and one row per phase of Drupsteen's
learning-from-incidents cycle, in this order: Reporting; Investigation and analysis; Planning interventions;
Intervening; Evaluating (`learning-principles.md` §1b). Put each row's citations in `row_cites`; the page shows them
as the Cites column. A phase the export says nothing about reads "Not in this export:" and what would show it, with
an empty cites list. Typical evidence for each phase:

- **Reporting:** a repeat failure or a near-miss recorded as routine work, not reported as a warning.
- **Investigation and analysis:** no root-cause review of the repeat; audits that recorded observations without checking them.
- **Planning interventions:** a finding or recommendation with no corrective plan, or a plan that chose a weaker fix.
- **Intervening:** an agreed action or procedure that was extended, overdue or never put into use.
- **Evaluating:** no check that a change worked: jobs closed without review, drills recorded without observations.

**The timeline.** Start from the `--timeline-item` output. Keep each kept event's `date` and `cites` exactly as
printed, drop duplicates and context dates (the year a plant was built), and rewrite `text` as one line in plain
words. Each event keeps `knowable_then`: leave `true`, or replace it with what the record showed at that moment.
Drop an event whose meaning was clear only after the incident. Add `response` ("None recorded" is an answer).

**The learnings.** Each one is about a step of the cycle, not about the people in it ("the extensions had no
approval route", not "the managers failed to close them"). Cite the level-4 finding that shows the organisational
condition, plus the Failure-to-Correct or dated findings that show the warning. Label `evidence_strength`.

```json
{"kind": "learning", "lesson": "An extended safety action needs an approval route, or the extension becomes the norm.",
 "explanation": "…", "owner": "Plant & Asset Leadership (F13, T4)", "learning": "LR-21", "cites": ["FND-…", "EVD-…"]}
```

**Language.** This pack makes hindsight wording an error: "failed to", "should have", "would have" (JC3) and
"obviously", "clearly should" (JC4) stop `check-pack` even without `--strict`. Rewrite them with the table in
`learning-principles.md` §1a. Snippets copied from findings often contain them: rewrite, do not quote.

## If the evidence is thin

Follow `skill-common.md` §6, and:
- **No dated missed opportunities** (`--timeline-item` prints an empty item): keep one `missed` timeline with the
  events whose order the findings state, mark an unknown date as unknown, and add a `limits` line.
- **No Failure-to-Correct findings and no earlier recommendations:** say so in the bottom line; the review then
  rests on the culture and drift findings, and the cycle table marks the phases it cannot show.
- **No level-4 finding in the export:** this review needs at least one, since its learnings are about the
  organisation. Tell the user, add a `gaps` entry for the organisational evidence that would show why the warnings
  went unanswered, and offer `precursor-timeline` for the warnings themselves.

## Not covered here

- The full dated list of warning signs, with who received each: `precursor-timeline`.
- The site leadership team's decisions, trade-offs and workshop: `site-leadership-coach`.
- How the factors connect as a causal chain: `causal-map`.

## Check and hand over

Run `learnings-coach/references/skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/failure-to-learn-review.json --strict   # fix every problem it lists
PMLC pack <ws> <run>/outputs/failure-to-learn-review.json                  # -> failure-to-learn-review.html (open first) and .md
PMLC pack <ws> <run>/outputs/failure-to-learn-review.json --format docx    # a Word paper for the leadership or board meeting
PMLC pack <ws> <run>/outputs/failure-to-learn-review.json --format pptx    # slides for a leadership review session
```

Also confirm: the cycle table has the five phases in order, every learning cites a level-4 finding, and every
timeline event carries `knowable_then`. Tell the user which phases broke, how many dated missed opportunities were
kept and how far back the earliest goes. Next: `site-leadership-coach` or `board-brief` to carry the learnings to
those audiences.
