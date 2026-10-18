---
name: safety-committee-guide
description: Produce a discussion guide from a ProbeMatrix investigation export for joint health and safety committees, workforce safety representatives and union safety reps - a plain-language account, the questions the workforce should raise with management, what to look for on site, and how to keep the discussion about systems rather than blame. Use when someone asks for safety committee material, a worker consultation pack, a guide for safety reps, a workforce engagement session or a town-hall discussion on an investigation.
---

# Safety Committee Guide

Audience: workforce representatives and joint safety committees. They give the workforce a voice, raise concerns and check that learning reaches the people who do the work. They need a fair account and good questions.

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py`. Read `learnings-coach/references/learning-principles.md`.

## Gather

```bash
PMLC profile <ws>
PMLC select <ws> --tier T1 T2 --brief
PMLC select <ws> --level 4 --top-rated --brief
PMLC select <ws> --relation norm_setter learner challenger --brief
```

## Write

1. **What happened**, in a page, in plain language, roles only.
2. **What the investigation says about the system**: the five learnings most relevant to the workforce, with a clear statement that the analysis places most causes at supervision and organisational level when the profile shows that.
3. **Questions to raise with management**: ten, about staffing, training, procedures, equipment, authority to stop work, and how concerns are handled.
4. **What to look for on site**: a walk-round prompt list drawn from the conditions in the findings.
5. **Running the discussion**: a 60-minute agenda, ground rules (no names, no blame, focus on conditions), and how to record and send concerns to management.
6. **Follow-up**: what the committee should ask to see at 30, 60 and 90 days.

## Output

Write the pack `<run>/outputs/safety-committee-guide.json` (schema: `learnings-coach/references/pack-schema.md`), then:

```bash
PMLC check-pack <ws> <run>/outputs/safety-committee-guide.json   # fix every problem it lists
PMLC pack <ws> <run>/outputs/safety-committee-guide.json         # -> safety-committee-guide.html (primary) and .md
```

Sections → kinds:
1. `para`.
2. `learning` ×5, plus a `para` on where the analysis places the causes.
3. `question` ×10, with `to` = the management role.
4. `check` items.
5. A `para` with the ground rules, then a `table` agenda with columns Minutes and Item.
6. `check` items, with `when` = "30 days", "60 days" or "90 days".

Set `"scope": {"tiers": ["T1", "T2"]}`. Put data-quality corrections in `data_quality`, findings left out on purpose in `exclusions`, and same-condition findings in `supporting_cites`.

```json
{"kind": "question", "question": "Who may stop a restart when the test record is missing?", "why": "…",
 "to": "Maintenance manager", "cites": ["FND-…"]}
```
