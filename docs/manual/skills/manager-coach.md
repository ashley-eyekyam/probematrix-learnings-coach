# manager-coach

Learning for department and function managers: maintenance, operations, engineering, integrity, HSE, procurement, training, and planning and scheduling. It covers the systems, procedures, resources, priorities and leading indicators they own, with a 90-day agenda for each of the five functions with the most findings, a work-management section for planners and schedulers, and, on request, a management-review input.

## What it is for

- "What should our managers change after this investigation?"
- A management action agenda, or departmental lessons.
- KPIs or leading indicators for a function.
- A function's management-review input from an incident.

Function managers (tier T3) own procedures, resources and priorities inside a function. Site-wide decisions belong to [site-leadership-coach](site-leadership-coach.md); every tier of one department, in one reference file, belongs to [cluster-learning-dossier](cluster-learning-dossier.md).

## How to start it

- "What should our maintenance, procurement and training managers change?"
- "Give me a 90-day agenda and leading indicators for each function."
- "What should our planners and schedulers change after this investigation?"

## What it needs

- `clusters.json` from [learning-clusters](learning-clusters.md).
- The interface matrix, which `setup` writes.
- Optional: the Learnings Register; its T3 learnings are reused with their `LR-nn` ids.

## Engine commands and flags

```bash
pmlc select <ws> --tier T3 --count-by entity          # functions ranked by T3 findings: take the top 5
pmlc select <ws> --tier T3 --brief
pmlc select <ws> --tier T3 --level 3 4 --top-rated
pmlc select <ws> --relation owner absent --brief
pmlc select <ws> --entity F08 --level 3 4 --brief      # work management and planning
pmlc select <ws> --preset manager-coach                # the five select calls above at once
pmlc interfaces <ws> --top 15
pmlc register-items <ws> --tier T3
pmlc check-pack <ws> <run>/outputs/manager-coach.json --strict
pmlc pack <ws> <run>/outputs/manager-coach.json
pmlc pack <ws> <run>/outputs/manager-coach.json --format docx   # the agenda as a Word paper
pmlc pack <ws> <run>/outputs/manager-coach.json --format csv    # manager-coach.actions.csv, owner columns blank
pmlc pack <ws> <run>/outputs/manager-coach.json --format ics --start YYYY-MM-DD   # only with your start date
pmlc export-actions <ws>                               # the recommendations and indicators as an action list
```

- [select](../commands/select.md): `--tier T3` keeps function management findings; `--count-by entity` prints only a count per function, which ranks the functions; `--level 3 4` Supervision and Organisational Influences; `--top-rated` the strongest; `--relation owner absent` the systems managers own and the functions that did not exist; `--entity F08` Work Management & Planning in the default taxonomy (use its id in yours); `--brief` short entries. A named function adds `--entity` with its id.
- [interfaces](../commands/interfaces.md) lists the seams between functions.
- [check-pack](../commands/check-pack.md) with `--strict` and [pack](../commands/pack.md) render the pack. The pack's scope is tier T3.
- [export-actions](../commands/export-actions.md) writes `actions.csv` with owners and due dates left blank for the organisation.

## What you get

`manager-coach.html` and `.md`. One section for each of the top five functions, each with:

- **What your system allowed**: up to six system learnings;
- **Interfaces you share**: up to three paragraphs on the seams with other functions and what to agree with them;
- up to four **recommendations**, each with its control tier and indicator;
- up to four **leading indicators**, each with a deterioration trigger;
- a **90-day agenda**: verify and contain in the first 30 days, draft the system change with the people who do the work by 60, report the indicator by 90.

Then a **work-management** section for planners and schedulers when the evidence supports it, an optional **management review input** (exactly six rows, each citing its findings or reading "not in this investigation"), and a **summary** table with a row for every function, the top five first.

**Formats.** `--format docx` writes the agenda as a Word paper. `--format csv` writes `manager-coach.actions.csv`, the recommendations, decisions and indicators with the owner, due-date and status columns blank; once it exists it is never replaced (the command stops with exit 1). `--format ics --start <date>` writes calendar reminders for the 30, 60 and 90-day horizons, counted from the date you give; the skill sets each recommendation's `by_when` to its horizon only when you give that date, and never picks one itself. See [pack](../commands/pack.md).

## Worked example (Hazira)

On the base classification, `select --tier T3 --count-by entity` ranked Mechanical Maintenance (90), Operations & Control Room (80), Engineering, Design, Documents & MOC (62), Asset Integrity (58) and HSE, Process Safety & Audit (55) as the top five, so the other functions go in the summary table. `--tier T3 --brief` returned 219 findings, `--tier T3 --level 3 4 --top-rated` 63, `--relation owner absent --brief` 75, and the work-management call 42 (26 at level 3, 16 at level 4). `interfaces --top 15` lists the seams to agree; the strongest is between Operations & Control Room and Mechanical Maintenance (71 shared findings).

These counts are from the base classification, before the resolution pass. After you place the remaining roles they will change.

## Related skills

- [supervisor-coach](supervisor-coach.md): the checks the managers' systems should support.
- [site-leadership-coach](site-leadership-coach.md): the decisions above the functions.
- [cluster-learning-dossier](cluster-learning-dossier.md): everything for one function, at every tier.
