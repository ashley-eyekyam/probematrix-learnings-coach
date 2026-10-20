# auditor-assurance-pack

An audit and assurance pack for internal auditors, ISO 45001 and process-safety auditors, certification bodies, insurers and regulators' inspectors. It gives audit test points grouped by the framework the auditor picks, what to sample, the evidence to request, the red flags this event showed, a critical-control verification table, a cross-site protocol, and a results template with NC and OFI grades.

## What it is for

- An audit checklist, an audit protocol or an assurance plan.
- Inspection focus areas after an incident.
- Verifying across other sites that the lessons have been applied.

Auditors need testable criteria and evidence to request, not narrative. Executive decisions belong to [top-management-brief](top-management-brief.md), and directors' questions to [board-brief](board-brief.md).

## How to start it

- "Give me audit test points to check whether the same conditions exist at our other plants."
- "Turn this investigation into an ISO 45001 audit protocol, grouped by clause."
- "What should our PSM auditors sample, and what evidence should they request?"

## What it needs

- `clusters.json` from [learning-clusters](learning-clusters.md).
- An answer to one question: which framework the test points follow (ISO 45001, OSHA PSM, CCPS RBPS, Seveso III / COMAH, ICMM critical control management, the Indian regimes, or the organisation's own elements).
- Optional: the Learnings Register, the adoption, distribution and verification records, and the organisation's barrier or critical-control register.

## Engine commands and flags

```bash
pmlc select <ws> --level 3 4 --top-rated --brief
pmlc select <ws> --tag assurance --brief
pmlc select <ws> --text "record|log|register|sign|closure|overdue|schedule|audit" --brief
pmlc select <ws> --preset auditor-assurance-pack   # the three calls above at once
pmlc table-item <ws> hoc --register <run>/outputs/learnings-register.json
pmlc check-pack <ws> <run>/outputs/auditor-assurance-pack.json --strict
pmlc pack <ws> <run>/outputs/auditor-assurance-pack.json
pmlc pack-xlsx <ws> <run>/outputs/auditor-assurance-pack.json --kind test_point
pmlc templates <ws> verification
```

- [select](../commands/select.md): `--level 3 4` Supervision and Organisational Influences; `--top-rated` the strongest; `--tag assurance` the functions tagged assurance (how existing audits performed); `--text` searches for records, logs, registers, sign-offs, closures, overdue items, schedules and audits; `--brief` short entries.
- [table-item](../commands/table-item.md) `hoc` with `--register` shows the control tiers of the register's fixes.
- [check-pack](../commands/check-pack.md) with `--strict` checks every test point's `clauses` against the standards crosswalk and that each one cites its evidence. [pack](../commands/pack.md) renders the pack, and the free-text `clause` shows as a badge.
- [pack-xlsx](../commands/pack-xlsx.md) with `--kind test_point` writes the test points as an Excel sheet, one row each.
- [templates](../commands/templates.md) `verification` writes the blank record of whether each learning was applied.

## What you get

`auditor-assurance-pack.html` and `.md`:

1. **why existing assurance did not catch it**: what the findings say about audits, inspections and records before the event;
2. up to twenty **audit test points**, at least one for each management-system element the evidence touches, grouped by the chosen framework's clauses: expectation, what to sample (a sampling basis, not invented statistics), evidence of conformity, red flags seen in this event;
3. a **cross-site verification protocol**: records to pull, interviews by role and a walk-path;
4. optionally, **critical-control verification** (ICMM step 8): each critical control with its verification activity and verifier role, mapped to the organisation's barrier register, with unmapped controls listed;
5. an **evidence request list** by function;
6. **reporting**: a grading scale (conforming, major or minor nonconformity, opportunity for improvement, not tested) and a results template with a blank "response to finding" column for the audited organisation's documented response (PSM (o)(4)).

An audit of other sites against this event's conditions creates new findings that must each be answered, and they may be discoverable: agree its scope and handling with legal and compliance advisers first.

## Worked example (Hazira)

On the base classification, `select --level 3 4 --top-rated --brief` returned 101 findings and `--tag assurance --brief` returned 80. The records search matched 429 of 436 findings, because these words are common in the findings' text: the agent treats it as a wide net and reads the strongest matches first. With the sample register, `table-item hoc` showed 45% of the register's fixes at the engineering tier. A test point on change control could rest on the evidence that "no more MOCs are implemented in the plant since 2018" (EVD-2986), grouped under ISO 45001 9.2 when the auditor picks that framework.

These counts are from the base classification, before the resolution pass. After you place the remaining roles, or add an overlay, the tag counts can change.

## Related skills

- [board-brief](board-brief.md): the assurance the board should request.
- [barrier-learnings](barrier-learnings.md): the critical controls to test.
- [investigator-coach](investigator-coach.md): the interview rules and evidence gaps.
