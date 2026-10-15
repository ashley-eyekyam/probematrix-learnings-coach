---
name: training-designer
description: Design training from a ProbeMatrix investigation export for training managers, instructors and competence assessors - a training-needs map by role and tier, case-based modules, scenario exercises, assessment questions with answer keys, and a cascade plan - so the investigation becomes curriculum rather than a one-off briefing. Use when someone asks for training needs analysis, a training module, a lesson plan, e-learning content, assessment or quiz questions, competence gaps or case-study training from an incident.
---

# Training Designer

Audience: training and L&D. They turn learnings into competence that lasts. Training is the weakest control on its own: design it alongside the system fixes, not instead of them.

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py`. Read `learnings-coach/references/learning-principles.md`.

## Gather

```bash
PMLC select <ws> --text "train|competen|qualif|knowledge|experience|familiar|skill" --brief
PMLC select <ws> --level 1 2 --brief            # acts and individual conditions
PMLC classify <ws>                               # tiers and entities for the needs map
```

## Write

1. **Training-needs map**: rows = role groups (entity × tier), columns = competences implicated by the findings; each cell cites findings. Mark which needs are real competence gaps and which are system problems that training cannot fix (send those to `manager-coach`).
2. **Modules** (three to six), each: audience, objectives (observable), duration, the case material used (de-identified, roles only), activities, and how competence is checked.
3. **Scenario exercises**: three decision-point scenarios from the event ("the meter is back from repair and the test rig is unavailable: what do you do?"), with facilitator notes.
4. **Assessment**: ten to fifteen questions with answer keys and the finding each tests; include questions that ask for the level of a cause (L1–L4).
5. **Cascade plan**: who trains whom, materials, and a measure of transfer at 90 days.

## Output

`<run>/outputs/training-designer.md`. If the user wants slides or a document, build them from this file with the host's document tools.
