---
name: investigator-coach
description: Coaches incident investigators and HSE professionals from a ProbeMatrix investigation export - evidence gaps and conflicts, the investigation process against requirements, key questions and interviews still to pursue, causal hypotheses to test, and method lessons on reaching supervisory and organisational causes. Fills the export's Evidence to Collect, Key Questions, Suggested Interviews and Causal Hypothesis columns when they are empty. Use when someone asks how to deepen or strengthen an investigation with a ProbeMatrix export, what evidence is missing, who else to interview, how good the investigation is, or wants investigator training material from a real case.
---

# Investigator Coach

Audience: investigators, HSE advisers and process-safety engineers who run or review investigations. Read `learnings-coach/references/learning-principles.md` (including "Interviews in a just culture") and `learnings-coach/references/export-schema.md`.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 and §2.

Engine: `PMLC`, as `skill-common.md` §1 defines it (this skill needs the `learnings-coach` skill installed alongside it).

This skill needs the **workspace** only. It uses, when present: the register (`<run>/outputs/learnings-register.json`), the comparator (`<ws>/comparator.json`) and the gaps other packs recorded (`<run>/outputs/gaps.json`).

- **Ask about privilege first**, one question, before you write the interview plan or the follow-up table: "Is litigation, a prosecution or a regulator's inquiry in prospect?" If yes, or the user does not know, produce the interview plan and follow-up only at the direction of the organisation's legal adviser, title the pack "Working papers", and say that `follow-up.json` is pasted back only when the adviser agrees. These outputs create no legal privilege (`skill-common.md` §7).
- Start from the register if present: carry `learning: "LR-nn"` on method lessons and follow-up rows that test a register learning.

## Gather

```bash
PMLC select <ws> --top-rated --format json --out <ws>/top.json   # the high-rated findings the follow-up must cover
PMLC table-item <ws> evidence-types                              # evidence items by type, ready to paste
PMLC run-path <ws>                                               # top rating and incident date
```

`select --preset investigator-coach` runs the select call. The profile (`<ws>/profile.md`, printed by `setup`) says whether the follow-up columns are empty. Read:
- the incident narrative and the Incident Summary fields in `<ws>/incident.json` (`fields`: Date, Investigation Status, Investigation Team, Due Date, Completed Date where the export has them);
- the evidence descriptions in `<ws>/evidence.json`;
- `<run>/outputs/gaps.json` when it exists: the gaps the other packs could not close. Each one is a candidate follow-up row or interview question.

## Write

Write the pack `<run>/outputs/investigator-coach.json` in the shape in `learnings-coach/references/pack-schema.md`. **Leave `scope` out**: coverage is then measured against the top-rated findings, which are exactly what the follow-up table must cover.

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/investigator-coach.json (repository only).

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | The gaps that would most change the analysis | `bottom_line` | up to 7 |
| 1 | `evidence-audit` | Evidence base audit | The `table-item evidence-types` output, pasted unchanged | `table` | 1 |
| 1 | `evidence-audit` | (same section) | Absent kinds of evidence; conflicts between sources (dates, times, identifiers) and whether they were resolved; findings that rest on a single source | `para` | up to 4 |
| 2 | `process` | Investigation process against requirements | One `check` per requirement (below), with `clauses`; [GAP] where the export does not show it | `check` | up to 6 |
| 3 | `follow-up-per-finding` | Follow-up per high-rated finding | The follow-up table: `"id": "follow-up"`, one row per condition (`investigator-coach/references/follow-up.md`) | `table` | 1 |
| 4 | `interview-plan` | Interview plan | Roles the evidence never heard from, ordered by how much they could change the analysis, five questions each; `to` = the role, `group` = the role | `question` | up to 30 (six roles) |
| 5 | `method` | Method lessons | Where the analysis reached L3–L4 and how; findings coded too low (an organisational condition recorded as an individual act); single-source findings | `para` | up to 5 |
| 6 | `training` | Training use | Exercises from this case for investigator training (such as "move this L1 finding to the level where it belongs") | `scenario` | up to 3 |

Rules for the content:

- **Investigation process against requirements.** Check, from the Incident Summary fields and the narrative: the investigation began promptly (within 48 hours under PSM (m)(2) and RMP 68.81; `PSM-(m)(2)`, `RMP-68.81`); the team included someone who knows the process, and a contract employee where contractor work was involved (`PSM-(m)(3)`); the report holds the minimum fields: date of incident, date the investigation began, description, contributing factors, recommendations (`PSM-(m)(4)`); a system exists to resolve the recommendations (`PSM-(m)(5)`); the report will be reviewed with affected personnel, contractors included (`PSM-(m)(6)`); causes, actions and effectiveness review are planned (`ISO45001-10.2`). Where a field is absent, write the check with "[GAP]" and a top-level `gaps` entry naming the record that would show it. State what the export shows; never that a requirement was breached.
- **Follow-up table.** The contract is in `investigator-coach/references/follow-up.md` (`check-pack` enforces it). Keep each cell specific to the finding's evidence. `pack` writes `follow-up.json` from it, ready to paste back into the investigation.
- **Interviews** follow "Interviews in a just culture": non-disciplinary, a representative present, local rationality, no leading questions. Add one question for validating the account with the people involved before learnings are published.

```json
{"kind": "check", "text": "The report records the date the investigation began. [GAP] The export has no Incident Summary date for it.",
 "clauses": ["PSM-(m)(4)"], "cites": ["FND-…"]}
```

## If the evidence is thin

- **No Evidence Links sheet:** the evidence audit says so in one `para`; the follow-up table still covers every top-rated finding, with Evidence to collect stating what record would ground it.
- **No Incident Summary timeline fields:** every process check carries [GAP]; do not infer dates from the narrative unless it states them.
- **Hundreds of top-rated findings:** one row per condition, not per finding; group findings that describe the same condition into one row.

## Not covered here

- Comparing this investigation with an official report: `report-comparison`.
- The learnings themselves and their recommendations: `learnings-register`.
- Legal advice on privilege or disclosure: the organisation's legal adviser.

## Check and hand over

Run `learnings-coach/references/skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/investigator-coach.json --strict   # fix every problem it lists
PMLC pack <ws> <run>/outputs/investigator-coach.json                  # -> investigator-coach.html, .md, follow-up.json and follow-up.csv
```

Also confirm: the privilege question was asked and answered, every top-rated finding has a follow-up row, and the pack stays internal (`pack` keeps interview plans out of any shared copy). Next: paste `follow-up.json` back into the investigation, when the answer to the privilege question allows it;
`follow-up.csv` holds the same rows in the export's column order, for a spreadsheet.
