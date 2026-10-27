---
name: manager-coach
description: Produces learning for department and function managers from a ProbeMatrix investigation export - maintenance, operations, engineering, integrity, HSE, procurement, training, planning and scheduling managers - on the systems, procedures, resources and priorities they own, with leading indicators, a 90-day agenda per function and a management-review input. Use when someone asks what managers or department heads should change after an investigation, for a management action agenda, departmental KPIs or a function's management-review input from a ProbeMatrix export. Not for site-wide leadership decisions (use `site-leadership-coach`) or every tier of one department (use `cluster-learning-dossier`).
---

# Manager Coach

Audience: T3 function and department management. They own procedures, resources and priorities inside a function. Their learning is mostly at Supervision (L3) and Organisational (L4) level. Read `learnings-coach/references/learning-principles.md` and `learnings-coach/references/indicators-and-effectiveness.md` §1.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 and §2.

Engine: `PMLC`, as `skill-common.md` §1 defines it (this skill needs the `learnings-coach` skill installed alongside it).

This skill needs the **workspace** and **clusters**. It uses, when present: the register (`<run>/outputs/learnings-register.json`), the interfaces and the adoption record.

Start from the register if present: `PMLC register-items <ws> --tier T3` gives the managers' learnings; carry `learning: "LR-nn"` on every item that expresses a register learning.

## Gather

```bash
PMLC select <ws> --tier T3 --count-by entity                # functions ranked by T3 findings: take the top 5
PMLC select <ws> --tier T3 --brief
PMLC select <ws> --tier T3 --level 3 4 --top-rated
PMLC select <ws> --relation owner absent --brief            # systems they own; functions that did not exist
PMLC select <ws> --entity F08 --level 3 4 --brief           # work management and planning (F08 in the default taxonomy)
PMLC select <ws> --prefix SVIO --brief                      # planned operations: crewing, risk assessment, missions beyond capability
PMLC interfaces <ws> --top 15                               # the seams with other functions
PMLC register-items <ws> --tier T3                          # the register's T3 learnings (needs the register)
```

`select --preset manager-coach` runs the select calls at once. If the user names a function, add `--entity <F-id>` and write only that function's section, plus the summary.

## Write

Write the pack `<run>/outputs/manager-coach.json` in the shape in `learnings-coach/references/pack-schema.md`. Set `"scope": {"tiers": ["T3"]}`. Write one section per function for the **top 5 functions** by T3 findings (`id` = the function, such as `mechanical-maintenance`), largest first, each part as a `group`; the other functions get a row in the summary table only.

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/manager-coach.json (repository only)

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | The learnings every manager should take away | `bottom_line` | up to 7 |
| 1–5 | `*` | What your system allowed (section per function) | Procedures missing or not used, schedules that slid, records that hid information, resources short, roles absent; `owner` = the function that owns the change | `learning` | up to 6 |
| 1–5 | `*` | Interfaces you share | From `interfaces`: the seams with other functions and what to agree with them | `para` | up to 3 |
| 1–5 | `*` | Recommendations | change, `hoc_tier`, barrier, indicator; `why_not_stronger` at the administrative or training tier | `recommendation` | up to 4 |
| 1–5 | `*` | Leading indicators | Measurable from systems the function already has (CMMS, permits, training records, audit tracker), each with `deterioration` | `indicator` | up to 4 |
| 1–5 | `*` | 90-day agenda | Columns Days, Action; `row_cites` (below) | `table` | 1 |
| 6 | `work-management` | Work management: planners and schedulers | What the planning system allowed (job plans without test steps, deferrals, backlog, permit coordination, crews and risk assessment the plan did not check) | `learning` | optional, up to 4 |
| 6 | `work-management` | (same section) | What the planning and scheduling function should change | `recommendation` | optional, up to 4 |
| 7 | `management-review` | Management review input | The six-row table (below) | `table` | optional, up to 1 |
| 8 | `summary` | Summary | Columns Function, Top learning, Top recommendation, Indicator: one row per function with T3 findings, the top 5 first | `table` | 1 |

Rules for the content:

- **90-day agenda.** First 30 days: verify the condition still exists, contain it. 60: the system change drafted with the people who do the work. 90: the indicator in the monthly report. No names or dates unless asked.
- **Work management.** Planners and schedulers decide what work is planned, with which steps, and what is deferred. Write the section when the work-management selection returns findings; the planning function then gets no separate function section. Use both selections: F08 gives the planning function's own findings, and `--prefix SVIO` (Planned Inappropriate Operations) gives work planned beyond the crew's capability, crews composed without the checks the job needed, and formal risk assessment skipped. Keep a crewing finding on the system that composed the crew, never on the people in it.
- **Management review input** (ISO 45001 9.3). Write it when the user asks for a management-review input. One `table`, columns Input, What this investigation shows, Indicator, Deterioration trigger, with **exactly six rows** in this order: Incidents and corrective actions; Monitoring results; Audit results; Risks and opportunities; Adequacy of resources; Consultation outcomes. Each row cites its findings in `row_cites`, or reads "not in this investigation" in the second cell with an empty cites list; every row with cites names an indicator and its deterioration trigger.
- **Calendar reminders.** Only when the user gives the day the agenda starts: set each recommendation's `by_when` to its agenda horizon ("30 days", "60 days" or "90 days") and add `--format ics --start <their date>` (below). Never pick the date yourself; without `--start` the engine writes no calendar.
- **Indicators.** Give each a baseline to establish and a deterioration trigger, in the terms of `indicators-and-effectiveness.md` §1; thresholds are for the owner to set.

```json
{"kind": "learning", "group": "What your system allowed", "lesson": "Return to service relied on memory, not a checklist.",
 "explanation": "…", "owner": "Maintenance function", "learning": "LR-01", "cites": ["FND-…"]}
```

## If the evidence is thin

- **Fewer than five functions have T3 findings:** write sections only for those; never promote another tier's findings into a function's section.
- **A function has one or two findings:** keep its section short (one learning, one recommendation, one indicator) or move it to the summary table only.
- **No work-management findings:** leave the work-management section out and say so in the summary.

## Not covered here

- Site-wide decisions, culture and the leadership workshop: `site-leadership-coach`.
- Every tier of one department in one reference file (practice, supervision, barriers, tier messages): `cluster-learning-dossier`. This skill writes only the T3 action agenda and may reuse dossier items.
- The interface review between two functions: `interface-learnings`.

## Check and hand over

Run `learnings-coach/references/skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/manager-coach.json --strict   # fix every problem it lists
PMLC pack <ws> <run>/outputs/manager-coach.json                  # -> manager-coach.html (open first) and manager-coach.md
PMLC pack <ws> <run>/outputs/manager-coach.json --format docx    # the agenda as a Word paper: manager-coach.docx
PMLC pack <ws> <run>/outputs/manager-coach.json --format csv     # manager-coach.actions.csv, owner columns blank
PMLC pack <ws> <run>/outputs/manager-coach.json --format ics --start YYYY-MM-DD   # only with the user's start date
```

The `.actions.csv` lists every recommendation, decision and indicator with the owner, due-date and status columns blank for the organisation to fill in. Once it exists the engine never replaces it: the command stops with exit 1 and writes nothing, so run `csv` on its own line and never delete a file the organisation may have filled in. The `.ics` holds one all-day reminder per recommendation with a `by_when` horizon, counted from the user's date, with no attendees (`skill-common.md` §8).

Also confirm: at most five function sections, every function with T3 findings in the summary, and the management-review table, if present, has exactly the six rows. Next: `PMLC export-actions <ws>` turns the recommendations and indicators into an action list with owners left blank.

For when and how to check that a learning took hold, use `learning-effectiveness-plan`.
