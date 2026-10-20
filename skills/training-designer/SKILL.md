---
name: training-designer
description: Designs training from a ProbeMatrix investigation export for training managers, instructors and competence assessors - a training-needs map by role and tier, case-based modules for crews, supervisors and managers, scenario exercises, assessment questions with answer keys (also as a spreadsheet), and a cascade plan - so the investigation becomes curriculum rather than a one-off briefing. Use when someone has a ProbeMatrix export and asks for a training needs analysis, a training module, a lesson plan, e-learning content, assessment or quiz questions, competence gaps or case-study training from the incident. Not for short crew briefings or toolbox talks (use `frontline-learning-cards`).
---

# Training Designer

Audience: training and L&D. They turn learnings into competence that lasts. Training is the weakest control on
its own: design it alongside the system fixes, not instead of them.

## Before you start

Engine: `PMLC` as defined in `skill-common.md` §1 (needs the `learnings-coach` skill installed alongside it).

- Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions).
- Needs: **workspace** and **clusters** (tiers and entities for the needs map; never re-run `classify` here).
- Read `learnings-coach/references/learning-principles.md`. For the level questions use
  `learnings-coach/references/hfacs-levels.md` §1 and §4.
- **Start from the register if present.** `PMLC register-items <ws> --tier T1` (and `--tier T2`, `--tier T3`
  for supervisor and manager modules) prints the learnings as ready items: keep their wording and carry
  `learning: "LR-nn"` on the modules and questions that teach one.

## Gather

```bash
PMLC select <ws> --text "train|competen|qualif|knowledge|experience|familiar|skill" --brief   # competence words
PMLC select <ws> --level 1 2 --brief                    # crew modules: acts and individual conditions
PMLC select <ws> --tag people --level 3 4 --brief       # the competence system (HR, training and competence)
PMLC select <ws> --tier T2 T3 --level 3 4 --top-rated --brief --budget-chars 30000   # supervisor and manager modules
```

- **Budget drops.** When the last call says findings were dropped for budget, rerun it with `--entity <F-id>` for
  the function a supervisor or manager module is for, rather than relying on which top-rated findings survived.
- **Scope per module audience.** Crew modules draw on levels 1 and 2. Supervisor and manager modules draw on
  levels 3 and 4, where their competence gaps sit. Set the pack scope to the levels the modules cover:
  `{"levels": [1, 2]}` for crew modules only, `{"levels": [1, 2, 3, 4]}` when there is a supervisor or manager
  module.

## Write

Pack `<run>/outputs/training-designer.json` (shape: `learnings-coach/references/pack-schema.md`),
scope as above.

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | The competence gaps, and what training cannot fix | `bottom_line` | up to 5 |
| 1 | `needs-map` | Training-needs map | Columns Role group, Competence, Need ("Competence gap" or "System problem: send to manager-coach"), with `row_cites` | `table` | 1 |
| 2 | `modules` | Modules | title, observable objective, audience, duration, content, assessment; content holds the case material (roles only), the activities, and the competence-standard and refresher lines (below) | `module` | up to 6 |
| 3 | `scenarios` | Scenario exercises | Decision-point scenarios from the event, with facilitator notes in `prompts` | `scenario` | up to 3 |
| 4 | `assessment` | Assessment | `why` = what it tests, `answer` = the answer key, `good_evidence`, `cites` = the finding it tests; include questions on the level of a cause (L1–L4) | `question` | up to 15 |
| 5 | `cascade` | Cascade plan | Columns Who, Trains whom, Materials, Transfer measure at 90 days | `table` | 1 |

- **Competence standard and refresher.** Each module's `content` ends with two lines: "Competence standard:
  <the organisation's competence-standard id>" and "Refresher interval: <interval>". Use an id or interval only
  when the export or the user gives one; otherwise write "to be set by the competence system owner". Never
  invent an id, an interval or a pass mark.
- **Needs map.** Mark which needs are real competence gaps and which are system problems that training cannot
  fix (send those to `manager-coach`). Supervisor and manager rows come from the level 3 and 4 selections.

```json
{"kind": "module", "title": "Return to service", "objective": "…", "audience": "Fitters", "duration": "45 min",
 "content": ["…", "Competence standard: to be set by the competence system owner", "Refresher interval: …"],
 "assessment": ["…"], "learning": "LR-01", "cites": ["FND-…"]}
```

## If the evidence is thin

- **No competence findings** (the text and `people` selections are empty): say so in the needs map with one
  row, "No competence gap shown by the findings", and keep the modules to the case material the findings
  support.
- **Only system problems:** a needs map of "System problem" rows is a valid answer; write fewer modules.
- `skill-common.md` §6 covers the rest.

## Not covered here

- Short crew cards and toolbox talks: `frontline-learning-cards`.
- Staffing, rostering, selection and competence-framework changes: `manager-coach` (system problems).
- Slides, documents or e-learning packages: build them from this pack with the host's document tools.
- The training record: `distribution.csv` (below), not a table in this pack.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/training-designer.json --strict
PMLC pack <ws> <run>/outputs/training-designer.json
PMLC pack-xlsx <ws> <run>/outputs/training-designer.json --kind question   # the assessment as a spreadsheet
```

- `pack-xlsx` writes `<run>/outputs/training-designer-questions.xlsx` (question, what it tests, answer key, good
  evidence, cites) for a learning-management system or a quiz tool.
- **Training record.** Each session is recorded in `<run>/outputs/distribution.csv`: if the file does not
  exist, `PMLC templates <ws> distribution` writes it with one row per pack (it never overwrites; add a row for
  this pack instead). The organisation fills in the delivery columns; never fill them yourself.
- Next step: `frontline-learning-cards` for the crew briefing that accompanies the module.
