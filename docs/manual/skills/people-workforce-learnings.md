# people-workforce-learnings

Learning for HR and workforce planning: HR business partners, workforce planners, rostering and fatigue owners, and the owners of competence frameworks. It covers the people systems the findings question: selection and placement standards, role qualifications, who may authorise whom for which task, crew and team composition, the manning of safety-critical jobs, rosters and workload. It ends with the competence-framework changes to make and a hand-off to training design.

## What it is for

- "What should HR and workforce planning learn from this investigation?"
- Whether staffing, qualification, crew composition or rostering played a part.
- What to change in a role's competence framework after an incident.
- A brief for `training-designer`, so that course content follows the standard rather than replacing it.

The pack is about systems, not individuals. It opens with the fixed line "Learnings about systems, not individuals' records." and never reviews a named person's competence, conduct or record. Sanction wording such as a performance review or disciplinary action (language rule JC2) is an error in this pack, through both `check-pack` and `check-language`.

## How to start it

- "What should HR and our workforce planners take from this ProbeMatrix export?"
- "Did staffing, qualification or crew composition play a part, and what should our competence framework define?"
- "Give me the people-system learnings from this investigation as a Word document for the HR policy review."

## What it needs

- `clusters.json`. The skill reads the HR, Training & Competence entity (F12, tagged `people`) and a list of people codes.
- Optional: the Learnings Register. Entries whose organisational system is training and competence or staffing and fatigue, or that F12 co-owns, keep their wording and their `LR-nn` ids.
- The default scope is tiers T3 and T4, HFACS levels 2 to 4, the `people` tag and F12.

## Engine commands and flags

```bash
pmlc select <ws> --code "OIS 4.1" "OIS 4.2" "PTF 1.1" "PTF 1.6" "SVIO 2.2" "SVIO 2.5" "SVIO 2.6" "SVV 4.4" --brief
pmlc select <ws> --entity F12 --brief
pmlc select <ws> --preset people-workforce-learnings   # the two calls above at once
pmlc check-pack <ws> <run>/outputs/people-workforce-learnings.json --strict
pmlc pack <ws> <run>/outputs/people-workforce-learnings.json
pmlc pack <ws> <run>/outputs/people-workforce-learnings.json --format docx,email   # Word, and an email digest
```

- [select](../commands/select.md): `--code` takes the literal codes whose names match `selection|staffing|crew|manning|qualif|authori|roster|fatigue|workload` in this export (rebuild the list for another export from `findings.json`); `--entity F12` adds the HR, Training & Competence findings; `--brief` gives short entries.
- [check-pack](../commands/check-pack.md) with `--strict` checks the pack against its profile: the banner line (`banner:people`), a scope with tiers, and JC2 as an error. [pack](../commands/pack.md) renders the pack.
- [pack](../commands/pack.md) `--format docx,email` writes `people-workforce-learnings.docx` for a policy review and a self-contained email digest (`.email.html` and `.email.txt`) for HR business partners.
- [check-language](../commands/check-language.md) reports sanction wording (JC2) as an error for this pack.

## What you get

`people-workforce-learnings.html` and `.md`:

1. **About this pack**: the fixed line "Learnings about systems, not individuals' records.";
2. **people-system learnings**, grouped under selection and placement, qualification and authorisation, crew and team composition, and oversight of people standards, only where the evidence supports them;
3. a **competence-framework table**: one row per role the findings name, with what the export shows and what the framework should define (the qualification, how it is assessed, who may authorise the person for the task, and when it is renewed);
4. optional **rostering, manning and workload** learnings: who is rostered, how many and with which roles;
5. a **hand-off to training design**: the training needs found, for `training-designer` to turn into content.

The pack never infers fatigue: with no evidence on hours or overtime, it says so in its limits.

## Worked example (Hazira)

`select --code` with the 8 Hazira people codes returned 18 findings, and `select --entity F12` returned 22; together they give 38 distinct findings, 2 of them in both. The pack carries six people-system learnings: the control-room qualification was not defined in HR or operations policy, and staff held emergency duty after a four-day general course (FND-6CBACB54, EVD-5634, LR-12); the authority to isolate sat with senior roles (FND-7505B1AF, EVD-4052, LR-07). Its rostering section finds that the night-shift crew had no member with practised emergency-isolation competence (FND-0AEE9898) and that the gasket replacement was manned with no inspector, test witness or close-out reviewer (FND-615DB819, LR-03). Three findings matched the code list on the word "authorised" alone and are excluded with a reason. The export holds nothing on working hours or fatigue, and the pack says so.

## Related skills

- [training-designer](training-designer.md): the course content, modules and assessments; this skill hands its training needs there.
- [manager-coach](manager-coach.md): each function manager's own changes and indicators.
- [safety-committee-guide](safety-committee-guide.md): the questions workforce representatives may raise about staffing and competence.
