---
name: manager-coach
description: Produce learning for department and function managers from a ProbeMatrix investigation export - maintenance, operations, engineering, integrity, HSE, procurement or training managers - focused on the systems, procedures, resources, priorities and leading indicators they own, with a 90-day improvement agenda per function. Use when someone asks what managers or department heads should change after an investigation, wants a management action agenda, departmental lessons, KPIs or leading indicators, or a management-review input from an incident.
---

# Manager Coach

Audience: T3 function and department management. They own procedures, resources and priorities inside a function. Their learning is mostly at Supervision (L3) and Organisational (L4) level.

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py`. Read `learnings-coach/references/learning-principles.md` and the leading-indicator guidance in `output-style.md`.

## Gather

```bash
PMLC select <ws> --tier T3 --brief
PMLC select <ws> --tier T3 --level 3 4 --min-rating <top>
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

`<run>/outputs/manager-coach.md`, with a one-page summary table at the end: function, top learning, top recommendation, indicator.
