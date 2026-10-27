# restorative-response-guide

A guide for the leaders and peer supporters who respond to the people involved after an incident: site and line leaders, peer supporters, and employee-assistance and occupational-health contacts. It follows Dekker's three restorative questions (who is hurt, what do they need, whose obligation is it to meet that need) and adds the conditions the findings show and support for second victims.

## What it is for

- "How should our leaders respond to the people who were involved?"
- Who was placed in harm's way, by role, and what to ask them.
- What the organisation owes the people involved, including putting right the conditions they worked in.
- Support for the people whose acts appear in the findings, who can be harmed by the event too (second victims).

The guide never says what a person feels, needs or did wrong. It opens with the fixed line "The export holds no information about the people affected. Every need here is a question to ask, or the organisation's own answer." Every item under "Who is hurt?" and "What do they need?" is a question: a statement such as "the crew need time off" is refused by `check-pack` ("needs are asked, never inferred"). Counterfactual wording such as "should have" (language rule JC3) and hindsight wording such as "obvious" (JC4) are errors in this pack.

## How to start it

- "We want a restorative, just-culture response for the people involved in this incident. What should our leaders ask them?"
- "How do we support the maintenance crew whose repair is at the centre of these findings, as second victims?"
- "Give our peer supporters a Word document with the questions to take into their conversations."

## What it needs

- The workspace only. The skill reads the findings that place people in harm's way, and the level 2 to 4 findings that show the conditions they worked in.
- Optional: the Learnings Register. Its entries that cite those findings keep their wording and their `LR-nn` ids in the conditions section.
- The default scope is HFACS levels 2 to 4: preconditions, supervision and organisation. Level 1 findings, the acts of a person, are never cited as conditions.
- The `first-48-hours` preset plans it as its last step, used only when the user asks how leaders should respond to and support the people involved. Otherwise ask for it by name, or plan it with `pmlc plan <ws> --skills restorative-response-guide`.

## Engine commands and flags

```bash
pmlc select <ws> --text "on foot|head.?count|shanty|civilian|injur|casualt|evacuat|muster" --fields label,level,short
pmlc select <ws> --level 2 3 4 --text "on foot|head.?count|shanty|civilian|injur|casualt|evacuat|muster" --brief
pmlc select <ws> --preset restorative-response-guide   # the two calls above at once
pmlc register-items <ws> --lr <LR-id> --lr <LR-id>      # with a register
pmlc check-pack <ws> <run>/outputs/restorative-response-guide.json --strict
pmlc pack <ws> <run>/outputs/restorative-response-guide.json --format docx
```

- [select](../commands/select.md): `--text` finds the findings that place people in harm's way (sent towards a release, mustered or counted, hurt); `--fields` keeps the label, level and short text, from which the skill takes the roles; `--level 2 3 4` keeps the conditions; `--brief` gives short entries.
- [register-items](../commands/register-items.md) `--lr` prints the register entries that cite those findings as ready items; the skill drops their level 1 cites.
- [check-pack](../commands/check-pack.md) with `--strict` checks the banner (`banner:restorative`), that needs are questions (`needs-are-questions`), that no owner or date is written (`no-owner-due`), and JC3 and JC4 as errors.
- [pack](../commands/pack.md) `--format docx` writes `restorative-response-guide.docx` for the leaders and peer supporters. The guide is internal by default.

## What you get

`restorative-response-guide.html` and `.md`:

1. **About this guide**: the fixed line;
2. **Who is hurt?**: one question per group of people the findings place in harm's way, named by role;
3. **What do they need?**: questions to ask the people themselves, each with the role who asks;
4. **Whose obligation is it?**: what the organisation and its roles owe the people involved;
5. **The conditions they worked in**: up to five learnings at levels 2 to 4, with their register ids;
6. **Support for the people involved**: concrete steps, second-victim support among them, kept apart from the investigation.

The answers people give stay with the organisation; they are never written into the pack.

## Worked example (Hazira)

`select --text` with the harm pattern returned 13 Hazira findings; 11 of them are at levels 2 to 4. The register entries that cite them are LR-07, LR-08, LR-12, LR-13 and LR-25. The guide asks after four groups: the two control-room engineers who walked towards the vapour cloud (FND-13708453, EVD-1460), the maintenance crew whose gasket repair was resourced with no inspector or test witness (FND-615DB819, EVD-2894), the shift leaders who had no standing authority to isolate (FND-82761CC5, EVD-3932) and the perimeter security staff who saw the release first (FND-2F736E5F, EVD-6234). Its conditions include emergency duty with no defined qualification (LR-12, EVD-5634) and a control room with ordinary doors (LR-25). The export's initial report states no injuries to plant personnel and on-shift contractors and was still verifying the area outside the perimeter; the guide records that it cannot say more.

## Related skills

- [people-workforce-learnings](people-workforce-learnings.md): HR's selection, qualification and staffing standards.
- `learning-team-facilitator`: a facilitated session where the team explains how the work is done.
- [investigator-coach](investigator-coach.md): interviews in a just culture, from the investigation side.
