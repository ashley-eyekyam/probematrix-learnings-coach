# nine-m-analysis

A 9M analysis of one investigation, done with you one question at a time. Where HFACS asks at which level a condition sat, the nine Ms ask which part of the work system it belongs to: Manpower/Mindpower, Medium, Method, Mission, Measurement, Management/Money, Machine, Material and Maintenance. For each M that matters, the skill writes one learning, the state of the barrier and a direction of change, then a blank actions sheet the organisation fills in, and a 9M map that the learnings register and the recommendation review read. It never writes an owner or a due date.

## What it is for

- "Work through the 9Ms with me."
- Designing corrective and preventive actions grouped by M, before they go into an action tracker.
- Seeing which Ms the findings point to, including the ones the codes under-count (Material and Maintenance).
- Pre-filling the register's 9M column.

## How to start it

- "Do a nine Ms analysis of this ProbeMatrix export, one question at a time."
- "Which of the 9Ms does this investigation point to, and what should change in each?"
- "Take me through material and maintenance: did they play a part?"

## What it needs

- A workspace from [learnings-coach](learnings-coach.md).
- The `nine_m_seed.json` artefact, which the first command below writes. A CAPA Planner workbook is refused: give the findings export.
- You, to answer the questions. Each question offers 2 to 4 suggestions, the recommended one first, and always "None / unknown (record as a gap)"; your own words are always allowed.
- Optional: the Learnings Register. With it, each learning carries the register learning (`LR-nn`) that holds its first finding.

## Engine commands and flags

```bash
pmlc nine-m-seed <ws>                                        # score every finding per M; print the M profile
pmlc nine-m-suggest <ws> --step scope --record               # which Ms to work through
pmlc nine-m-suggest <ws> --m M8 --step relevance --record    # one question for one M
pmlc nine-m-suggest <ws> --m M8 --step condition --subcategory M8.03 --record
pmlc nine-m-answer <ws> --q Q02 --choice 1                   # the suggestion you picked
pmlc nine-m-answer <ws> --q Q03 --text "your own words"      # or free text
pmlc select <ws> --code "OIR 1.5" --brief                    # the findings behind a code a suggestion names
pmlc check-pack <ws> <run>/outputs/nine-m-analysis.json --strict
pmlc pack <ws> <run>/outputs/nine-m-analysis.json            # also writes outputs/nine-m-map.json
pmlc pack <ws> <run>/outputs/nine-m-analysis.json --format docx   # a Word paper
pmlc pack <ws> <run>/outputs/nine-m-analysis.json --format csv    # the recommendations as a CSV
pmlc nine-m-actions-template <ws> <run>/outputs/nine-m-analysis.json   # the blank actions sheet (xlsx; --format csv)
```

- [nine-m-seed](../commands/nine-m-seed.md) scores each finding for each M from its Nanocode, its wording and its clusters, and prints the profile: findings per level and rating, top codes and top-rated findings.
- [nine-m-suggest](../commands/nine-m-suggest.md) prints the suggestions for one question; `--record` appends it to `<ws>/nine_m_session.json`. `--step` is `scope`, `relevance`, `subcategory`, `condition`, `driver`, `barrier`, `change`, `cross-m` or `gaps`; `--subcategory` brings that subcategory's findings forward.
- [nine-m-answer](../commands/nine-m-answer.md) records the answer, by `--choice` or `--text`.
- [select](../commands/select.md) with `--code` shows the findings for one code, and `--brief` keeps them short. `select --m M8` lists the findings the seed puts under one M.
- [check-pack](../commands/check-pack.md) with `--strict` applies the profile: an overview of exactly 9 rows, each M a section or a not-relevant row with a reason (rule `nine-m-overview`), cites inside the M's seeded findings (`nine-m-cites`), the M1-balance warning (`m1-balance`) and no owners or dates (`no-owner-due`, a problem even without `--strict`). On a replayed session it also needs the demonstration banner. Then [pack](../commands/pack.md) renders it, and [nine-m-actions-template](../commands/nine-m-actions-template.md) writes the sheet.

**The interview.** One question per turn, in the order M1 to M9: relevance, subcategory, condition, the system driver (why it made sense at the time), the barrier's state, and the direction of change, strongest first, with you saying whether it is corrective or preventive. The leading indicator is not asked (the six questions are used): the analyst derives it and says so in the data quality notes. Then two global questions: whether Ms that a causal link joins are one learning, and what evidence would settle each "unknown". The budget is 6 questions per M plus 4, and an M you judge not relevant stops after its first question. For M1 the driver question is answered before any M1 learning is written: M1 is not the people M. Discipline, "accountability" and "consequences" are never offered. Facts you add that the export does not hold go in the "Context supplied by the organisation" section, without a finding citation.

**M1 balance.** `m1-balance` warns when M1 holds strictly more recommendations than every other M while another M has more level 3 and 4 findings in the seed. A tie for the most stays quiet.

## What you get

`nine-m-analysis.html` and `nine-m-analysis.md`, with these sections:

- **nine-m-overview:** one row per M, M1 to M9: relevance, conditions, top subcategory and the findings the seed links to it;
- **m1 to m9:** for each relevant M, a learning (the condition, its subcategory, the system driver and the barrier state), a barrier and a recommendation, grouped by condition, and evidence questions where needed;
- **not-relevant:** the Ms judged not relevant, each with its reason (left out when every M is relevant);
- **cross-m:** a graph of the conditions that cross Ms;
- **organisation-context:** facts the organisation supplied, uncited.

`pack` also writes `outputs/nine-m-map.json`: each cited finding with its M, subcategory and condition, and each condition with its M, subcategory, learning and recommendations. `--format docx` gives the same content as a Word paper, and `--format csv` the recommendations as a CSV. `nine-m-actions-template` writes `nine-m-analysis.actions-template.xlsx` (or `.csv`) with the columns Recommendation ID, M, Change, HoC tier, Corrective/Preventive, Indicator, Owner, Due date, Status and Notes. Owner, Due date and Status are blank, and it never overwrites a sheet that exists.

## Worked example (Hazira)

`nine-m-seed` maps all 436 findings, with none unmapped. By primary M: Management/Money 130, Method 95, Manpower/Mindpower 72, Mission 40, Machine 37, Maintenance 27, Medium 13, Measurement 13 and Material 9.

The golden is a scripted session: `nine-m-replay --accept-recommended` took the recommended suggestion at all 57 questions, so the pack carries the line "Answers chosen for demonstration, not by the organisation." All nine Ms came out relevant. Material and Maintenance reach a condition through the relevance question even though their codes route only 9 and 27 findings: 162 and 301 findings point to them once their wording and clusters count. The cross-M answer keeps one link as one learning: the maintenance and spares programme (OIR 1.6, M9) feeding risks identified but not mitigated (SVF 3.4, M6). The M learnings carry LR-03, LR-09, LR-06, LR-07, LR-08, LR-10, LR-01 and LR-05; the M6 learning, on three programmes whose risks were never assessed, has no single register learning.

The pack is `samples/2020-09-24-hazira-gas-release-fire/outputs/nine-m-analysis.json` in the repository, beside the session (`nine-m-session.json`) and the map (`nine-m-map.json`). The owner's own interview replaces the scripted answers at the release-candidate test.

## Related skills

- [learnings-register](learnings-register.md): copies each learning's `nine_m` and `nine_m_subcategory` from `nine-m-map.json`.
- [barrier-learnings](barrier-learnings.md): which barriers failed, and how strong the fixes should be.
- [learning-clusters](learning-clusters.md): who in the organisation should learn each condition.
- [causal-map](causal-map.md): the causal links the driver and cross-M questions come from.
