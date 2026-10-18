---
name: frontline-learning-cards
description: Turn a ProbeMatrix investigation export into frontline learning - one-page Learning Cards and five-minute toolbox talks for operators, technicians, fitters, crews, control-room staff and security personnel, in plain language, blame-free, with warning signs and "stop and ask" points. Use when someone wants toolbox talks, safety moments, shift briefings, learning cards, pre-job talk material or lessons for workers or crews from an investigation, even if they just say "make this useful for the guys on the floor".
---

# Frontline Learning Cards

Audience: T1 frontline. They control how the task is done today. They do not control procedures, budgets or design, so never hand them an organisational fix as if it were theirs.

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py` (this skill needs the `learnings-coach` skill installed alongside it). Read `learnings-coach/references/learning-principles.md` and the Learning Card and toolbox talk blocks in `learnings-coach/references/output-style.md`.

## Gather

```bash
PMLC select <ws> --tier T1 --brief                     # what frontline roles were involved in
PMLC select <ws> --tier T1 --level 1 2                  # acts and conditions at the sharp end
PMLC select <ws> --tier T1 --top-rated           # the ones that mattered most
```

If the user names a crew or trade ("maintenance fitters", "control-room operators"), add `--entity <F-id>`.

## Choose the learnings

Pick five to eight learnings that a frontline person can **notice or act on** during work: a warning sign, a hold point, a test that must not be skipped, a situation where they should stop and ask. Skip learnings that only managers can act on, but if one explains why the job felt normal (e.g. "this substitute part had been used for years"), mention it so people recognise the trap.

## Write

One **Learning Card** per learning (title, what happened, why it made sense at the time, warning signs, what good looks like, three discussion questions, evidence trail). Use the words crews use. Roles only, no names. Keep each card under 250 words.

Then two or three **toolbox talks** (five minutes each) that group the cards by task (e.g. "returning equipment to service", "first minutes of a gas release").

Close with a **"stop and ask" list**: the situations from this event where anyone on the crew should pause the job and ask a supervisor, with the support they should expect when they do.

## Output

Write the pack `<run>/outputs/frontline-learning-cards.json` (schema: `learnings-coach/references/pack-schema.md`), then:

```bash
PMLC check-pack <ws> <run>/outputs/frontline-learning-cards.json   # fix every problem it lists
PMLC pack <ws> <run>/outputs/frontline-learning-cards.json         # -> frontline-learning-cards.html (primary) and .md
```

Sections → kinds:
- Learning Cards: `card` ×5–8 (title, what_happened, why_made_sense, warning_signs, good_looks_like, discussion ×3; **must cite**).
- Toolbox talks: one `para` per talk, with `group` = the talk's task, then a `scenario` for its discussion.
- "Stop and ask": `check` items, with `when` = the situation.

Set `"scope": {"tiers": ["T1"]}`. Put data-quality corrections in `data_quality`, findings left out on purpose in `exclusions`, and same-condition findings in `supporting_cites`.

```json
{"kind": "card", "title": "Test what you disturb", "what_happened": "…", "why_made_sense": "…",
 "warning_signs": ["…"], "good_looks_like": "…", "discussion": ["…", "…", "…"], "cites": ["FND-…"]}
```

If translation is requested, translate the text fields and keep every ID unchanged.
