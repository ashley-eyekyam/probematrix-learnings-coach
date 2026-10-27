---
name: learning-effectiveness-plan
description: Plans how an organisation will check that the learnings of a ProbeMatrix investigation took hold - for each learning in the Learnings Register, what to check and when, counted from adoption (30, 60 and 90 days, 6 and 12 months for priority 1; 3, 6 and 12 months otherwise), the Kirkpatrick level of each check (communicated, understood, applied, effective), a leading and a lagging indicator, and one audit question each - with no owners, dates or statuses, which the organisation sets in its own verification log. Use when someone with a ProbeMatrix export and its register asks how to verify that lessons were learned, when to check effectiveness, what to measure after the actions close, or for a follow-up plan. Not for writing the learnings and their recommendations (use `learnings-register`), a function manager's briefing and actions (use `manager-coach`) or the committee's own review agenda (use `safety-committee-guide`).
---

# Learning Effectiveness Plan

Engine: `PMLC` as in `learnings-coach/references/skill-common.md` §1; this skill needs the `learnings-coach` skill installed alongside it.

Audience: the HSE lead, the safety committee and the function managers who will follow the learnings up. The plan
says what to check and when, as offsets from the day the organisation adopts each learning. It never sets an owner,
a calendar date or a status: those belong to the organisation, in its verification log.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions; run `PMLC setup`
when only an .xlsx was given). Needs: `workspace`, the register (`<run>/outputs/learnings-register.json`; write it
with `learnings-register` first and run `check-register` on it) and `effect-plan` (the first Gather line writes
`<ws>/effect_plan.json`). Read `learnings-coach/references/learning-principles.md` (§2 ground every sentence, §4
count honestly, §6 recommendations, not action plans).

The engine reads the register only, and refuses a pack or any other file in its place. The schedule follows plan
ruling P6-8 (`learnings-coach/references/effectiveness.json`): Kirkpatrick's four levels (L1 communicated, L2
understood, L3 applied, L4 effective) and Jacobsson's spread (from `transferability`), depth (from the strongest
recommendation's `hoc_tier`) and duration.

## Gather

```bash
PMLC effect-plan <ws> --register <run>/outputs/learnings-register.json                          # writes effect_plan.json; prints the count and notes
PMLC effect-plan <ws> --register <run>/outputs/learnings-register.json --table-item schedule    # every check, ready to paste
PMLC effect-plan <ws> --register <run>/outputs/learnings-register.json --table-item levels      # learnings per Kirkpatrick level
PMLC effect-plan <ws> --register <run>/outputs/learnings-register.json --table-item indicators  # LR, Leading; Lagging blank
PMLC effect-plan <ws> --register <run>/outputs/learnings-register.json --items audit            # one audit question per learning
PMLC effect-plan <ws> --register <run>/outputs/learnings-register.json --json                   # rows, spread, depth, duration, notes
```

Paste the `schedule` and `levels` tables and the audit questions unchanged: never retype an offset, a Kirkpatrick
level, a count or a cite, and never turn an offset into a date. From `--json`, read `learnings` (Jacobsson spread,
depth and duration per learning) and `notes` (a learning with no priority takes the priority-2 schedule).

Then read each register learning's `lesson`, `recommendations` (`what`, `hoc_tier`, `leading_indicator`) and
`worst_case`. The lagging indicator you write is the outcome the learning should reduce, counted after the event:
the release, failure, trip or finding the learning is about, never a measure of people.

## Write

Write `<run>/outputs/learning-effectiveness-plan.json` in the shape in `learnings-coach/references/pack-schema.md`.

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/learning-effectiveness-plan.json (repository only).

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | How many checks for how many learnings, the priority-1 cadence, and the Jacobsson spread and depth; cite the findings | `bottom_line` | 1–3 |
| 1 | `banner` | Who sets owners, dates and statuses | The banner `para` (below), with no cites | `para` | 1 |
| 2 | `schedule` | What to check and when | The `--table-item schedule` table, whole | `table` | 1 |
| 3 | `levels` | Checks at each level | The `--table-item levels` table, whole | `table` | 1 |
| 4 | `indicators` | Leading and lagging indicators | The `--table-item indicators` table with every `Lagging` cell filled (below) | `table` | 1 |
| 5 | `audit` | What an auditor would see | The `--items audit` questions, each with a `good_evidence` added (below) | `question` | 3–25 |
| 6 | `verification-log` | Recording the checks | One `para`: the organisation records each check in its own log, made with `PMLC templates <ws> verification`; statuses come only from the organisation | `para` | 1 |

**The banner.** The pack needs one `para` whose `text` is exactly, character for character:
`The organisation sets owners, dates and statuses. This plan sets out what to check and when, counted from adoption.`
Put it alone in `banner`; `check-pack` reports it missing (rule `banner:effectiveness`).

**Indicators.** Keep the engine's `LR` and `Leading` cells, the rows and the `row_cites` as printed. Fill `Lagging`
for every row with one outcome measure for that learning, from its lesson and worst case: "Pressure-boundary seal
leaks at substituted parts (count per year)", not "operators who made errors". A blank `Lagging` or `Leading` cell
is a problem even without `--strict` (rule `leading-lagging`). When the register gives no leading indicator, write
one from the strongest recommendation and say so in a `data_quality` note.

**Audit questions.** Keep each engine `question`, `why` and `cites` unchanged; add `good_evidence`: what an auditor
can see or hear when the learning is applied, from that learning's recommendations ("Certificates on file for every
pressure-boundary spare; a sample of seals checked against the specification in stores"). Keep all of them when there
are 25 or fewer; with more, keep every priority-1 learning and as many others as fit, and say which were left out.

```json
{"kind": "question", "question": "What would an auditor see that shows LR-01 is applied?",
 "why": "An auditor checks that the learning is applied, by what they can see or hear, not by what is written.",
 "good_evidence": "A specification and certificate on file for each pressure-boundary spare.", "cites": ["FND-8C0BB623"]}
```

Every item but the banner cites. Leave `owner` and `by_when` out of every item, write no calendar date anywhere
(only offsets such as "90 days after adoption") and never write a status ("done", "verified", "effective") for a
learning: the organisation records those in its verification log.

## If the evidence is thin

Follow `skill-common.md` §6, and:
- **Register with no priority** (a v0.3 register; `notes` says so): keep the priority-2 schedule the engine used, say
  so in the bottom line, and suggest the user sets priorities with `learnings-register`.
- **No leading indicator in the register:** the engine leaves `Leading` blank; write one as above and add a
  `data_quality` note naming the learnings.
- **A learning with no `finding_ids`:** its rows carry no cites; name it in a `data_quality` note and keep its checks.

## Not covered here

- Writing the learnings, their recommendations and indicators: `learnings-register`.
- A function manager's briefing and the actions in their area: `manager-coach`.
- The safety committee's review agenda and questions: `safety-committee-guide`.
- How strong the recommendations are on the hierarchy of controls: `recommendation-strength-review`.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/learning-effectiveness-plan.json --strict --register <run>/outputs/learnings-register.json   # fix every problem it lists
PMLC pack <ws> <run>/outputs/learning-effectiveness-plan.json                     # -> learning-effectiveness-plan.html and .md
PMLC pack <ws> <run>/outputs/learning-effectiveness-plan.json --format docx,csv   # a Word plan; one actions.csv row per check
PMLC templates <ws> verification                                                  # the organisation's blank verification log
```

Offer the docx for the committee and the csv (`<pack>.actions.csv`, owner, due and status blank, never replaced) to
load the checks into the organisation's action system. Tell the
user how many checks the plan sets for how many learnings, that every check is counted from adoption, and that the
organisation fills in owners, dates and statuses in `verification.jsonl`, which the model never fills in.
