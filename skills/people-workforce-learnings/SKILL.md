---
name: people-workforce-learnings
description: Produces learning for HR and workforce planning from a ProbeMatrix investigation export - HR business partners, workforce planners, rostering and fatigue owners and competence-framework owners - on the people systems the findings question - selection and placement standards, role qualifications, who may authorise whom for which task, crew and team composition, manning of safety-critical jobs, rosters and workload - with the competence-framework changes to make and a hand-off to training design. Use when someone has a ProbeMatrix export and asks what HR or workforce planning should learn, whether staffing, qualification, crew composition or rostering played a part, or what to change in a role's competence framework after an incident. Not for training content, modules or assessments (use `training-designer`) or a function manager's own action agenda (use `manager-coach`).
---

# People & Workforce Learnings

Audience: HR and workforce planning (`hr-workforce`, tier T3): the people who set selection and staffing standards,
role qualifications, crew composition, rosters and workload. The pack is about **systems, not people**: it never
reviews an individual's record, competence or conduct.

## Before you start

Engine: `PMLC` as defined in `skill-common.md` §1 (needs the `learnings-coach` skill installed alongside it).

- Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions).
- Needs: **workspace** and **clusters**.
- Read `learnings-coach/references/learning-principles.md`.
- **Start from the register if present.** In `<run>/outputs/learnings-register.json`, take the entries whose
  `org_system` names training and competence or staffing and fatigue, or whose `owner_entity` names F12: keep their
  wording and carry `learning: "LR-nn"`.

## Gather

```bash
PMLC select <ws> --code "OIS 4.1" "OIS 4.2" "PTF 1.1" "PTF 1.6" "SVIO 2.2" "SVIO 2.5" "SVIO 2.6" "SVV 4.4" --brief   # people codes
PMLC select <ws> --entity F12 --brief                   # HR, Training & Competence
```

- **The `--code` list** is every code in this export whose name matches
  `selection|staffing|crew|manning|qualif|authori|roster|fatigue|workload`, written out as literal codes. For
  another export, rebuild it from the `code` and `name` of each finding in `<ws>/findings.json`.
  On Hazira it is 8 codes and 18 findings; `--entity F12` gives 22; together 38 distinct findings.
- Read each finding's justification for the people system it describes. A code name can match on a word alone
  ("Authorised Unnecessary Hazard" matches `authori`): leave out a finding that says nothing about a people system.
- F12 is one entity for HR, training and competence (no F12a/F12b split in v2.0). Training content belongs to
  `training-designer`; keep only the standard, the qualification and the staffing decision here.

## Write

Pack `<run>/outputs/people-workforce-learnings.json` (shape: `learnings-coach/references/pack-schema.md`),
`"scope": {"tiers": ["T3", "T4"], "levels": [2, 3, 4], "tags": ["people"], "entities": ["F12"]}`.

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | The people-system learnings, one line each | `bottom_line` | up to 5 |
| 1 | `banner` | About this pack | Exactly "Learnings about systems, not individuals' records." | `para` | 1 |
| 2 | `system` | People-system learnings | `group` = Selection and placement / Qualification and authorisation / Crew and team composition / Oversight of people standards (only the groups the evidence supports); `owner` = the HR or workforce-planning role | `learning` | up to 8 |
| 3 | `competence-framework` | Competence framework: what to define | One row per role the findings name: Role, What the export shows, What the framework should define; `row_cites` per row | `table` | 1 |
| 4 | `rostering` | Rostering, manning and workload | Who is rostered, how many and with which roles, for routine and safety-critical work | `learning` | optional, up to 4 |
| 5 | `handoff` | Hand-off to training design | One paragraph: the training needs this pack found, for `training-designer` to turn into content | `para` | 1 |

- **Systems, not individuals.** Write "the qualification for the control-room role was not defined", never "the
  operator was not qualified". No appraisal, warning, sanction or "accountable" wording: JC2 is an error in this
  pack (`lint_errors`), and `check-language` reports it too.
- **No personal data.** Roles only. Never list who attended which course, ages, service years or health.
- **Competence framework.** Each row names the role, what the export shows about its standard (cite the findings),
  and what the framework should define: the qualification, how it is assessed, who may authorise the person for
  the task, and when it is renewed. Leave out a role the findings do not name.
- **Rostering.** Only what the findings support: crew composition on a shift, the roles a safety-critical job is
  manned with (an independent checker, a test witness), workload. With no evidence on fatigue or hours, say so in
  `limits`; do not infer fatigue.
- **Recommendations** stay with `manager-coach` and the register; a learning's `explanation` may name the change.

```json
{"kind": "table", "columns": ["Role", "What the export shows", "What the framework should define"],
 "rows": [["Control-room operator", "Four-day general course; qualification not defined", "…"]],
 "row_cites": [["FND-…", "EVD-…"]]}
```

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/people-workforce-learnings.json (repository only)

## If the evidence is thin

- **No people codes and few F12 findings:** one `system` learning and a one-row framework table are a valid pack;
  say in `limits` that the export holds little on people systems.
- **Nothing on rosters or manning:** leave the `rostering` section out.
- `skill-common.md` §6 covers the rest.

## Not covered here

- Course content, modules, assessments and quizzes: `training-designer`.
- A function manager's action agenda and indicators: `manager-coach`.
- Any review of a named person's competence, conduct or record: outside this skill, and outside ProbeMatrix.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/people-workforce-learnings.json --strict
PMLC pack <ws> <run>/outputs/people-workforce-learnings.json
PMLC pack <ws> <run>/outputs/people-workforce-learnings.json --format docx,email   # Word, and an email digest
```

- **Word** (`people-workforce-learnings.docx`) for the HR policy or workforce-planning review; **email**
  (`.email.html` and `.email.txt`) to send the learnings to HR business partners. Attach or link the full page.
- `check-language` treats sanction wording (JC2) as an error here; fix the wording, never quiet it with `lint_ok`.
- Next step: `training-designer`, with the hand-off paragraph as its brief.
