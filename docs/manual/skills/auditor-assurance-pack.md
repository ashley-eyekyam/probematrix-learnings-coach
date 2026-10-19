# auditor-assurance-pack

An audit and assurance pack for anyone who tests whether controls work: internal audit, ISO 45001 and process-safety auditors, certification bodies, insurers and regulators' inspectors. It gives audit test points, what to sample, the evidence to request, the red flags this event showed, and a protocol to test whether the same conditions exist elsewhere.

## What it is for

- An audit checklist, an audit protocol or an assurance plan.
- Inspection focus areas.
- Verifying across other sites that the lessons have been applied.

Auditors need testable criteria and evidence to request, not narrative.

## How to start it

- "Turn this investigation into an audit checklist for our other sites."
- "What should an auditor sample, and what evidence should they request, to see whether these conditions exist elsewhere?"
- "Give me 12 to 20 audit test points grouped by management-system element."

## What it needs

- A workspace with `clusters.json`.

## Engine commands and flags

```bash
pmlc select <ws> --level 3 4 --top-rated --brief
pmlc select <ws> --tag assurance --brief                 # how existing audits performed
pmlc select <ws> --text "record|log|register|sign|closure|overdue|schedule|audit" --brief
pmlc select <ws> --preset auditor-assurance-pack         # the three calls above at once
pmlc check-pack <ws> <run>/outputs/auditor-assurance-pack.json
pmlc pack <ws> <run>/outputs/auditor-assurance-pack.json
```

- [select](../commands/select.md): `--level 3 4` the Supervision and Organisational levels; `--top-rated` the strongest; `--tag assurance` the HSE and audit functions; `--text` a regular expression over the finding text (here, words about records and follow-up); `--brief` short entries.
- [check-pack](../commands/check-pack.md) and [pack](../commands/pack.md) render the pack. Test points must cite their evidence.

## What you get

`auditor-assurance-pack.html` and `.md`:

1. **why existing assurance did not catch it**, stated as facts, with no blame;
2. twelve to twenty **audit test points**, grouped by element (maintenance and testing, change management, materials and spares, permits, competence, emergency preparedness, records, audit follow-up). Each gives the expectation, what to sample and how many, the evidence of conformity, and the red flags seen in this event;
3. a **cross-site verification protocol** for the top five conditions;
4. an **evidence request list** by function. Interviews follow the just-culture rules in the learning principles;
5. a grading scale and a blank results table.

If you ask for a spreadsheet, the agent builds it from the test points.

## Worked example (Hazira)

`select --level 3 4 --top-rated --brief` returned 101 findings and `--tag assurance --brief` returned 80. The records search matched 429 of 436 findings, because these words are common in the findings' text: the agent treats it as a wide net and reads the strongest matches first. A test point on change control could rest on the evidence that "no more MOCs are implemented in the plant since 2018" (EVD-2986).

## Related skills

- [board-brief](board-brief.md): the assurance the board should request.
- [barrier-learnings](barrier-learnings.md): the critical controls to test.
- [investigator-coach](investigator-coach.md): the interview rules and evidence gaps.
