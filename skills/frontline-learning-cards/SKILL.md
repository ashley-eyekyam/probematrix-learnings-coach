---
name: frontline-learning-cards
description: Turns a ProbeMatrix investigation export into frontline learning - one-page Learning Cards and five-minute toolbox talks for operators, technicians, fitters, crews, control-room staff, security personnel and contractor crews, in plain language, blame-free, with warning signs, "stop and ask" points and the supervisor who delivers each card. Use when someone has a ProbeMatrix export and wants toolbox talks, safety moments, shift briefings, learning cards or pre-job talk material for workers or crews. Not for the supervisors' own checks and hold points (use `supervisor-coach`), training modules and assessments (use `training-designer`), or response-phase learning for fire and emergency teams (use `emergency-response-learnings`).
---

# Frontline Learning Cards

Audience: T1 frontline. They control how the task is done today. They do not control procedures, budgets or
design, so never hand them an organisational fix as if it were theirs. Supervisors usually deliver the cards.

## Before you start

Engine: `PMLC` as defined in `skill-common.md` §1 (needs the `learnings-coach` skill installed alongside it).

- Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions).
- Needs: **workspace** and **clusters** (the frontline roles placed; run the `learning-clusters` resolution pass
  first if many roles are unplaced).
- Read `learnings-coach/references/learning-principles.md`, and the Learning Card and toolbox talk blocks in
  `learnings-coach/references/output-style.md`.
- **Start from the register if present.** `PMLC register-items <ws> --tier T1` prints the T1 learnings as ready
  items: keep their wording and carry `learning: "LR-nn"` on each card that expresses one.

## Gather

```bash
PMLC select <ws> --tier T1 --brief                      # what frontline roles were involved in
PMLC select <ws> --tier T1 --level 1 2 --top-rated      # sharp-end acts and conditions that mattered most
PMLC select <ws> --tag contractor --brief               # contractor crews (the contractor-workforce option)
PMLC register-items <ws> --tier T1                      # register learnings, when the register exists
```

- If the user names a crew or trade ("maintenance fitters", "control-room operators"), add `--entity <F-id>`.
- **Contractor-workforce option.** When the cards are for contractor crews (or the user asks to include them),
  use the contractor selection too and set `"scope": {"tiers": ["T1"], "tags": ["contractor"]}`. The host
  organisation's system owns the contractor's briefing and supervision: write "the contractor crew was not
  briefed on…", never "the contractor failed".
- **Primary cite at L1 or L2.** T1 selections surface many level 3 and 4 findings. The first Finding ID in each
  card's `cites` must be a level 1 or 2 finding (an act or condition at the sharp end). A level 3 or 4 finding
  may follow it when it explains why the job felt normal ("this substitute part had been used for years"); say
  so in `why_made_sense`. Levels: `learnings-coach/references/hfacs-levels.md` §1.

## Choose the learnings

Pick up to eight learnings that a frontline person can **notice or act on** during work: a warning sign, a hold
point, a test that must not be skipped, a situation where they should stop and ask. Skip learnings that only
managers can act on, unless one explains the trap; then mention it so people recognise it.

## Write

Pack `<run>/outputs/frontline-learning-cards.json` (shape: `learnings-coach/references/pack-schema.md`),
`"scope": {"tiers": ["T1"]}` (plus the contractor tag above).

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | The learnings a crew should take away, one line each | `bottom_line` | up to 5 |
| 1 | `delivery` | Using these cards | Facilitator note (below), then who delivers what | `para` | 1 |
| 1 | `delivery` | Using these cards | Columns Card, Delivered by, Pair with (supervisor-coach scenario), Contractor crews; one row per card, `row_cites` = the card's cites | `table` | 1 |
| 2 | `cards` | Learning Cards | title, what_happened, `why_made_sense`, `organisation_changing` (both required here), warning_signs, good_looks_like, three `discussion` questions; under 250 words; primary cite L1 or L2 | `card` | up to 8 |
| 3 | `toolbox-talks` | Toolbox talks | One `para` per five-minute talk, `group` = the task ("returning equipment to service") | `para` | up to 3 |
| 3 | `toolbox-talks` | Toolbox talks | One discussion `scenario` per talk, same `group` | `scenario` | up to 3 |
| 4 | `stop-and-ask` | Stop and ask | Situations from this event where anyone should pause the job and ask, with the support to expect; `when` = the situation | `check` | up to 10 |

- **Deliverer.** Each card names who delivers it, usually the crew's supervisor (a role, never a person), in the
  delivery table. "Pair with" names the `supervisor-coach` coaching scenario to run alongside it (its item id,
  such as `coaching-2`, when that pack exists; otherwise "supervisor-coach coaching scenarios").
- **Facilitator note.** These cards are read by the people whose acts appear in the findings. Consult those
  involved before wide release. Never single out "the" operator of a small crew: if only one person held a role,
  write the task, not the post. Do not close a card with "be more careful" or "stay vigilant"; say what the
  organisation is changing instead (`organisation_changing`).
- Use the words crews use. Roles only, no names.

```json
{"kind": "card", "title": "Test what you disturb", "what_happened": "…", "why_made_sense": "…",
 "organisation_changing": "…", "warning_signs": ["…"], "good_looks_like": "…", "discussion": ["…", "…", "…"],
 "learning": "LR-01", "cites": ["FND-…"]}
```

## If the evidence is thin

- **Few L1/L2 findings in T1:** write fewer cards, each with an L1 or L2 primary cite; do not promote a level 3
  or 4 finding into a crew instruction. Put the organisational conditions in a `limits` line pointing to
  `supervisor-coach` and `manager-coach`.
- **No contractor findings** (the contractor selection returns none): leave the contractor tag out of the scope
  and write "Not covered by the findings" in the Contractor crews column.
- `skill-common.md` §6 covers the rest.

## Not covered here

- The supervisors' checks, hold points and crew briefing plan: `supervisor-coach`.
- Training modules, scenarios with answer keys and assessment: `training-designer`.
- Response-phase learning for fire, emergency and security teams: `emergency-response-learnings`.
- Procurement, vendor and contractor-management learning: `supply-chain-contractor-learnings`.
- The delivery record itself: `distribution.csv` (below), not a table in this pack.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/frontline-learning-cards.json --strict
PMLC pack <ws> <run>/outputs/frontline-learning-cards.json
```

- Check that each card's first cite is a level 1 or 2 finding.
- **Delivery record.** Record each briefing in `<run>/outputs/distribution.csv`: if the file does not exist,
  `PMLC templates <ws> distribution` writes it with one row per pack (it never overwrites an existing file; add
  a row for this pack instead). The organisation fills in the channel, date, deliverer role, attendees,
  `contractors_included`, questions raised and concerns escalated; never fill those yourself.
- If translation is requested, follow `skill-common.md` §3 (text fields only; IDs unchanged).
- Next step: `supervisor-coach` for the crew briefing plan, if it has not been written.
