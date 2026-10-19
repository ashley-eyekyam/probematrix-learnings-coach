# training-designer

Training designed from the investigation, for training managers, instructors and competence assessors: a training-needs map by role and tier, case-based modules, scenario exercises, assessment questions with answer keys, and a cascade plan. The investigation becomes curriculum rather than a one-off briefing.

## What it is for

- A training needs analysis.
- A training module, a lesson plan or e-learning content.
- Assessment or quiz questions, and competence gaps.
- Case-study training from an incident.

Training is the weakest control on its own. This skill designs it alongside the system fixes, never instead of them, and sends needs that training cannot fix to [manager-coach](manager-coach.md).

## How to start it

- "Design a training module for fitters from this investigation, with an assessment."
- "What are the training needs by role, and which of them are really system problems?"
- "Write ten assessment questions with answer keys, including some on the level of each cause."

## What it needs

- `clusters.json`, which the hub's classify step builds. This skill reads it but never re-runs classify.

## Engine commands and flags

```bash
pmlc select <ws> --text "train|competen|qualif|knowledge|experience|familiar|skill" --brief
pmlc select <ws> --level 1 2 --brief           # acts and individual conditions
pmlc select <ws> --preset training-designer    # the two calls above at once
pmlc check-pack <ws> <run>/outputs/training-designer.json
pmlc pack <ws> <run>/outputs/training-designer.json
```

- [select](../commands/select.md): `--text` a regular expression over the finding text (words about training and competence); `--level 1 2` the Unsafe Acts and Preconditions levels; `--brief` short entries.
- [check-pack](../commands/check-pack.md) and [pack](../commands/pack.md) render the pack.

## What you get

`training-designer.html` and `.md`:

1. a **training-needs map**: role groups against competences, each cell citing findings, and each need marked "Competence gap" or "System problem: send to manager-coach";
2. three to six **modules**: audience, observable objectives, duration, case material (roles only), activities and how competence is checked;
3. three **scenario exercises** with facilitator notes;
4. ten to fifteen **assessment questions** with answer keys and the finding each tests;
5. a **cascade plan**: who trains whom, the materials, and a measure of transfer at 90 days.

For slides or a document, the agent builds them from this pack with the host's tools.

## Worked example (Hazira)

The training-words search returned 122 findings and `--level 1 2 --brief` returned 128. A scenario could start from the return-to-service gap: "the gasket is replaced and no design-pressure test is arranged: what do you do?", built on FND-3AB996FC. Where the cause is that no procedure required the test, the map marks it as a system problem, not a competence gap.

## Related skills

- [frontline-learning-cards](frontline-learning-cards.md): the cards a module can build on.
- [manager-coach](manager-coach.md): where system problems go.
- [investigator-coach](investigator-coach.md): exercises for investigators.
