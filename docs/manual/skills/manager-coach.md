# manager-coach

Learning for department and function managers: maintenance, operations, engineering, integrity, HSE, procurement or training. It focuses on the systems, procedures, resources, priorities and leading indicators each function owns, with a 90-day improvement agenda per function.

## What it is for

- "What should managers or department heads change after this investigation?"
- A management action agenda, departmental lessons, KPIs or leading indicators.
- An input to a management review.

Managers (tier T3) own procedures, resources and priorities inside a function. Their learning is mostly at the Supervision (L3) and Organisational Influences (L4) levels.

## How to start it

- "What should our department managers change after this investigation?"
- "Give the maintenance manager a 90-day agenda with leading indicators."
- "Which systems did each function own that allowed this, and what should change?"

## What it needs

- `clusters.json` from [learning-clusters](learning-clusters.md).
- Optionally the name of one function. Otherwise the pack has one section per function with tier T3 findings, largest first.

## Engine commands and flags

```bash
pmlc select <ws> --tier T3 --brief
pmlc select <ws> --tier T3 --level 3 4 --top-rated
pmlc select <ws> --relation owner absent --brief    # systems they own; functions that did not exist
pmlc select <ws> --preset manager-coach             # the three calls above at once
pmlc interfaces <ws> --top 15
pmlc check-pack <ws> <run>/outputs/manager-coach.json
pmlc pack <ws> <run>/outputs/manager-coach.json
```

- [select](../commands/select.md): `--tier T3` keeps management-tier findings; `--level 3 4` the Supervision and Organisational levels; `--top-rated` the strongest; `--relation owner absent` the findings where a role owned a system, or where a function that should exist was absent; `--brief` short entries. Add `--entity <F-id>` for one function.
- [interfaces](../commands/interfaces.md) gives the seams each function shares.
- [check-pack](../commands/check-pack.md) and [pack](../commands/pack.md) render the pack.

## What you get

`manager-coach.html` and `.md`, one section per function:

- **What your system allowed:** three to six system learnings. The `owner` is the function that owns the change, not who "was involved".
- **Interfaces you share**, and what to agree with the other functions.
- **Recommendations**, with the control tier and evidence.
- **Leading indicators:** two to four, measurable from systems the function already has (maintenance system, permits, training records, audit tracker).
- **90-day agenda:** verify and contain in the first 30 days, draft the system change with the people who do the work by 60, and put the indicator in the monthly report by 90. No names or dates unless you ask.

A summary table closes the pack: function, top learning, top recommendation and indicator.

## Worked example (Hazira)

`select --tier T3 --brief` returned 211 findings; `--tier T3 --level 3 4 --top-rated` returned 60; and `--relation owner absent --brief` returned 75. `interfaces --top 15` lists the seams to agree between managers; the strongest is between Operations & Control Room and Mechanical Maintenance.

## Related skills

- [supervisor-coach](supervisor-coach.md): the checks the managers' systems should support.
- [site-leadership-coach](site-leadership-coach.md): the decisions above the functions.
- [cluster-learning-dossier](cluster-learning-dossier.md): everything for one function.
