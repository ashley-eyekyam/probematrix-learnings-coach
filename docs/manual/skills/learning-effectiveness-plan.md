# learning-effectiveness-plan

A plan for checking that each learning took hold, for the HSE lead, the safety committee and the function managers who follow the learnings up. For every learning in the Learnings Register it sets out what to check and when, counted from the day the organisation adopts the learning: five checks in the first 12 months for a priority-1 learning, three for the others. Each check carries its Kirkpatrick level (communicated, understood, applied, effective), each learning a leading and a lagging indicator, and one question an auditor can answer by what they see. The plan never sets an owner, a calendar date or a status: the organisation records those in its own verification log. The schedule follows Kirkpatrick's four levels and Jacobsson, Ek and Akselsson's (2011, unverified) spread and depth of learning; `references/effectiveness.json` holds the rules.

## What it is for

- "How do we check these lessons actually took hold?"
- When to check each learning after it is adopted, and what to look for at each check.
- Leading and lagging indicators for every learning, to track in the organisation's own system.
- A follow-up plan for the safety committee once the actions are agreed.

## How to start it

- "Give me an effectiveness plan for this register: when to check each learning and what to measure."
- "How will we know in a year whether these learnings worked?"
- "Plan the follow-up: the 30, 60 and 90-day checks and the indicators."

## What it needs

- A workspace from [learnings-coach](learnings-coach.md) and the Learnings Register from [learnings-register](learnings-register.md), checked with [check-register](../commands/check-register.md).
- The `effect_plan.json` artefact, which the first command below writes. [effect-plan](../commands/effect-plan.md) reads the register only, and refuses a pack or any other file in its place.

## Engine commands and flags

```bash
pmlc effect-plan <ws> --register <run>/outputs/learnings-register.json                          # writes effect_plan.json
pmlc effect-plan <ws> --register <run>/outputs/learnings-register.json --table-item schedule    # every check
pmlc effect-plan <ws> --register <run>/outputs/learnings-register.json --table-item levels      # learnings per Kirkpatrick level
pmlc effect-plan <ws> --register <run>/outputs/learnings-register.json --table-item indicators  # Leading filled, Lagging blank
pmlc effect-plan <ws> --register <run>/outputs/learnings-register.json --items audit            # one audit question per learning
pmlc effect-plan <ws> --register <run>/outputs/learnings-register.json --json                   # spread, depth, duration, notes
pmlc check-pack <ws> <run>/outputs/learning-effectiveness-plan.json --strict --register <run>/outputs/learnings-register.json
pmlc pack <ws> <run>/outputs/learning-effectiveness-plan.json --format docx,csv
pmlc templates <ws> verification                                                                # the organisation's blank log
```

- [effect-plan](../commands/effect-plan.md) builds one row per check. Priority 1: 30 days (communicated), 60 days (understood), 90 days and 6 months (applied), 12 months (effective). Priorities 2 and 3, and a register with no priority: 3 months (communicated and understood), 6 months (applied), 12 months (effective). The leading indicator comes from the register (`verification.indicator`, else the first recommendation's indicator); the lagging column is left blank for the skill to fill.
- [check-pack](../commands/check-pack.md) with `--strict` checks the pack against its profile: the fixed banner (rule `banner:effectiveness`), no owner or due date (rule `no-owner-due`) and a filled `Leading` and `Lagging` cell on every indicator row (rule `leading-lagging`, a problem even without `--strict`). Then [pack](../commands/pack.md) renders it.
- [templates](../commands/templates.md) `verification` writes `verification.jsonl`, one line per learning with the check date, level, evidence and assessing role left blank for the organisation.

The skill pastes the schedule, the levels table and the audit questions whole, and never turns an offset into a date.

## What you get

`learning-effectiveness-plan.html` and `learning-effectiveness-plan.md`, with these sections:

- **banner:** the fixed text "The organisation sets owners, dates and statuses. This plan sets out what to check and when, counted from adoption.";
- **schedule:** every check, by learning, with its offset from adoption and its Kirkpatrick level;
- **levels:** how many learnings are checked at each Kirkpatrick level;
- **indicators:** the leading indicator from the register and a lagging indicator the skill writes for each learning: the outcome the learning should reduce, never a measure of people;
- **audit:** "What would an auditor see that shows LR-nn is applied?", with what good evidence looks like, drawn from the learning's recommendations;
- **verification-log:** where the organisation records each check, and that statuses come only from the organisation.

`--format docx` gives a Word plan for the committee; `--format csv` writes `learning-effectiveness-plan.actions.csv`, one row per check ("Check that LR-01 is communicated (Kirkpatrick L1), 30 days after adoption") with its leading indicator, in the columns the export-actions command uses; owner, due, status and effectiveness check stay blank, and an existing file is never replaced. No owners, dates or statuses are written.

## Worked example (Hazira)

`effect-plan` printed:

```text
effect-plan: 97 checks for 25 learning(s) written to <ws>/effect_plan.json.
Every check is counted from adoption; the organisation sets owners, dates and statuses.
```

The 11 priority-1 learnings get five checks each and the other 14 three each: 97 rows. On Jacobsson's measures 16 learnings spread to the industry and 9 to the organisation; 19 change the system and 6 change a procedure (LR-08, LR-12, LR-18, LR-19, LR-20 and LR-24). The golden pack pastes the schedule, the levels table and the 25 audit questions, and fills a lagging indicator for each learning, for example "Pressure-boundary seal or gasket leaks (count per year), and leaks at substituted parts" for LR-01. It is `samples/2020-09-24-hazira-gas-release-fire/outputs/learning-effectiveness-plan.json` in the repository.

## Related skills

- [learnings-register](learnings-register.md): the learnings, their recommendations and leading indicators that this plan reads.
- [manager-coach](manager-coach.md): a function manager's briefing and the actions in their area.
- [safety-committee-guide](safety-committee-guide.md): the committee's review agenda and questions.
- [recommendation-strength-review](recommendation-strength-review.md): how strong the recommendations are on the hierarchy of controls.
