---
name: manager-coach
description: Produce learning for department and function managers from a ProbeMatrix investigation export - maintenance, operations, engineering, integrity, HSE, procurement or training managers - focused on the systems, procedures, resources, priorities and leading indicators they own, with a 90-day improvement agenda per function. Use when someone asks what managers or department heads should change after an investigation, wants a management action agenda, departmental lessons, KPIs or leading indicators, or a management-review input from an incident.
---

# Manager Coach

Audience: T3 function and department management. They own procedures, resources and priorities inside a function. Their learning is mostly at Supervision (L3) and Organisational (L4) level.

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py` (this skill needs the `learnings-coach` skill installed alongside it). Read `learnings-coach/references/learning-principles.md` and the leading-indicator guidance in `output-style.md`.

## Gather

```bash
PMLC select <ws> --tier T3 --brief
PMLC select <ws> --tier T3 --level 3 4 --top-rated
PMLC select <ws> --relation owner absent --brief          # systems they own; functions that did not exist
PMLC interfaces <ws> --top 15
```

If the user names a function, add `--entity <F-id>`; otherwise produce one section per function with T3 findings, largest first.

## For each function, write

- **What your system allowed**: three to six system learnings (procedures missing or not used, schedules that slid, records that hid information, resources short, roles absent).
- **Interfaces you share**: from `interfaces`, the seams with other functions and what to agree with them.
- **Recommendations**: what should change, control tier, evidence.
- **Leading indicators**: two to four, measurable from systems the function already has (CMMS, permits, training records, audit tracker).
- **90-day agenda**: first 30 days (verify the condition still exists, quick containment), 60 (system change drafted with the people who do the work), 90 (indicator in the monthly report). No names or dates unless asked.

## Output

Write the pack `<run>/outputs/manager-coach.json` (schema: `learnings-coach/references/pack-schema.md`), then:

```bash
PMLC check-pack <ws> <run>/outputs/manager-coach.json   # fix every problem it lists
PMLC pack <ws> <run>/outputs/manager-coach.json         # -> manager-coach.html (primary) and manager-coach.md
```

Sections → kinds. Write one section per function (`id` = the function, e.g. `mechanical-maintenance`), with each part as a `group`:
- What your system allowed: `learning` ×3–6 (`owner` = the role that owns the system).
- Interfaces you share: `para`.
- Recommendations: `recommendation` (change, hoc_tier, barrier, indicator).
- Leading indicators: `indicator` ×2–4.
- 90-day agenda: `table` (Days, Action; `row_cites`).

End with a `summary` section: one `table` with columns Function, Top learning, Top recommendation and Indicator.

Set `"scope": {"tiers": ["T3"]}`. Put data-quality corrections in `data_quality`, findings left out on purpose in `exclusions`, and same-condition findings in `supporting_cites`.

```json
{"kind": "learning", "group": "What your system allowed", "lesson": "Return to service relied on memory, not a checklist.",
 "explanation": "…", "owner": "Maintenance manager", "cites": ["FND-…"]}
```
