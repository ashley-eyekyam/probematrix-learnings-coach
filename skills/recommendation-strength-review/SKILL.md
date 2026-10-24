---
name: recommendation-strength-review
description: Reviews the recommendations of a ProbeMatrix investigation's Learnings Register, and of its 9M analysis when there is one, as a set - how strong each change is on the hierarchy of controls (stronger, intermediate or weaker), whether every deep cause has at least one strong or intermediate fix, whether any fix questions an assumption or norm (double loop), how the fixes spread across the nine Ms and which lack a specific, measurable or relevant element - all banded by the engine, never judged, plus up to ten directions for stronger change with no owners and no dates. Use when someone with a ProbeMatrix export and its register asks how strong the corrective actions are, which are only training or procedures, whether a deep cause got a weak fix, or wants a CAPA critique before the actions are agreed. Not for designing the actions by M with the user (use `nine-m-analysis`) or writing the learnings and their recommendations (use `learnings-register`).
---

# Recommendation Strength Review

Engine: `PMLC` as in `learnings-coach/references/skill-common.md` §1; this skill needs the `learnings-coach` skill installed alongside it.

Audience: function managers, the people designing corrective actions, and HSE leads. The review shows where a
stronger change would remove more of the risk. It never grades the people who wrote the recommendations, and it
never sets an owner, a due date or a decision: those are the organisation's.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions; run `PMLC setup`
when only an .xlsx was given). Needs: `workspace` and the register (`<run>/outputs/learnings-register.json`; write it
with `learnings-register` first, and run `check-register` on it). Optional: `<run>/outputs/nine-m-map.json`, which
`nine-m-analysis` writes. Read `learnings-coach/references/learning-principles.md` (§3 system fixes before
retraining, §4 count honestly).

- **Never the CAPA Planner workbook.** The review reads the register and the 9M map only; a pack, or any other file
  in the register's place, is refused with one sentence naming the file it expects.
- **Which set:** with `nine-m-map.json` present, review the register and the 9M analysis together (`--nine-m`);
  without it, review the register only. Say which on the page (Write, `reviewed-set`).

## Gather

```bash
PMLC rec-review <ws> <run>/outputs/learnings-register.json --nine-m                       # the summary: bands, flags, loops, SMART
PMLC rec-review <ws> <run>/outputs/learnings-register.json --nine-m --table-item strength # per learning: ready to paste
PMLC rec-review <ws> <run>/outputs/learnings-register.json --nine-m --table-item spread   # recommendations per M: ready to paste
PMLC rec-review <ws> <run>/outputs/learnings-register.json --nine-m --table-item smart    # SMART gaps: ready to paste
PMLC rec-review <ws> <run>/outputs/learnings-register.json --nine-m --json                # causes, loops and recipients
```

Leave `--nine-m` off every line (and skip `spread`) when there is no `nine-m-map.json`. Paste each table item
unchanged; never retype a band, re-rate a tier or clear a flag. The bands are the engine's (`references/rec-review.json`):
`stronger` is elimination, substitution and engineering; `intermediate` is administrative; `weaker` is training,
PPE, or an administrative change whose text is a procedure, policy, reminder, memo, warning, sign, poster,
double-check or re-brief. A learning whose findings reach HFACS level 3 or 4 with nothing stronger than `weaker` is
flagged `weak fix for a deep cause`.

Then read the `--json` output: `loops.double` lists the changes that question an assumption, norm, design basis,
target, incentive or budget; `recipients` counts the recommendations each role receives. With `--nine-m`, read the
`nine-m-analysis` pack's recommendations too: the spread table counts them, and their `hoc_tier` shows how strong
they are. Read the register learnings behind each flag, each learning whose strongest change is `intermediate` or
`weaker`, and each learning the register marks double-loop.

## Write

Write `<run>/outputs/recommendation-strength-review.json` in the shape in `learnings-coach/references/pack-schema.md`.
Set `"scope": {"levels": [1, 2, 3, 4], "min_rating": "top"}`.

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/recommendation-strength-review.json (repository only).

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | The band counts, the flags, the loops and the spread, each with its count from the engine; no grade | `bottom_line` | 1–5 |
| 1 | `reviewed-set` | What was reviewed | Which set was reviewed, in the words below, and how many recommendations | `para` | 1 |
| 2 | `strength` | Strength of change for each learning | The `--table-item strength` output, unchanged | `table` | 1 |
| 3 | `spread` | Recommendations across the nine Ms | The `--table-item spread` output, unchanged; leave it out without a 9M map | `table` | optional, up to 1 |
| 4 | `loops` | Single-loop and double-loop change | What the loop count shows, against the learnings the register marks double-loop (below) | `para` | 1–3 |
| 5 | `directions` | Directions for stronger change | One `recommendation` per direction (below) | `recommendation` | 1–10 |
| 6 | `smart` | Recommendations missing a SMART element | The `--table-item smart` output, unchanged; leave it out when it has no rows | `table` | optional, up to 1 |

The `reviewed-set` para says either "the learnings register" or "the learnings register and the 9M analysis", word
for word, with the number of recommendations in each. When the 9M session was a replay (its pack carries the
demonstration banner), say the 9M answers were chosen for demonstration, not by the organisation: a review of
recommendations the coach shaped is circular unless the reader knows whose choices they were.

In `loops`, state the engine's double-loop and single-loop counts. Where the register marks a learning double-loop
but none of its changes questions an assumption or norm, name the learnings and say what was left unquestioned.

Each `directions` item is a `recommendation`: a direction of change, not a finished action.
- `change`: the stronger or double-loop change the review points to, for one learning, in one or two sentences;
- `hoc_tier`: the tier of the direction (`elimination`, `substitution`, `engineering`, `administrative`, ...);
- `indicator`: a leading indicator that would show the change working;
- `learning`: the register's `LR-nn`; `cites` that learning's findings and Evidence IDs;
- `why_not_stronger` (optional): when the direction is administrative, why a stronger tier does not fit.

Pick the directions in this order: flagged learnings; learnings whose strongest change is `intermediate`, when the
register gives no reason why it is not stronger (`why_not_stronger`); learnings the register marks double-loop with
no double-loop change. A `weaker` change beside a stronger one in the same learning needs no direction.

```json
{"kind": "recommendation", "change": "Make the test result a condition the system enforces: the work order for a pressure-boundary job cannot close without it.",
 "hoc_tier": "engineering", "indicator": "Share of pressure-boundary jobs closed with a test result entered",
 "learning": "LR-01", "cites": ["FND-0001", "EVD-0001"]}
```

No `owner` and no `by_when`: `check-pack` fails the pack on either, even without `--strict`. Write about the
recommendations, never about the people who wrote them: "the change is a reminder", not "the team chose a reminder".

## If the evidence is thin

Follow `skill-common.md` §6, and:
- **No register:** stop and write it with `learnings-register` first; the review reads recommendations, not findings.
- **No `nine-m-map.json`:** review the register only, leave out `spread`, and say so in `reviewed-set`.
- **No flag and no double-loop change:** keep the tables; write the directions for the `intermediate` learnings and
  the double-loop gaps, and say in the bottom line that no deep cause has only a weak fix.
- **Every recommendation `unrated`:** the register has no `hoc_tier`; ask for it in `learnings-register` first.

## Not covered here

- Designing corrective and preventive actions by M, with the user's answers: `nine-m-analysis`.
- Writing the learnings and their recommendations: `learnings-register`.
- Owners, due dates, approval and effectiveness checks: the organisation's, through `export-actions`.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/recommendation-strength-review.json --strict   # fix every problem it lists
PMLC pack <ws> <run>/outputs/recommendation-strength-review.json                  # -> recommendation-strength-review.html and .md
PMLC pack <ws> <run>/outputs/recommendation-strength-review.json --format docx    # -> a Word copy for the action review
PMLC pack-xlsx <ws> <run>/outputs/recommendation-strength-review.json --kind table   # -> the tables in Excel
```

Offer the docx for the meeting that agrees the actions, and the Excel view for sorting the strength table. Tell the
user the band counts, how many learnings are flagged, the double-loop count, and the first three directions.
