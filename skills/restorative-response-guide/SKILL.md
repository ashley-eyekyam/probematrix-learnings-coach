---
name: restorative-response-guide
description: Produces a restorative response guide from a ProbeMatrix investigation export for the leaders and peer supporters who respond to the people involved after an incident - Dekker's restorative questions (who is hurt, what do they need, whose obligation is it to meet the need) written as questions to ask the people themselves, never as answers about them, the organisation's obligations, the system conditions the findings show and second-victim support. Use when someone has a ProbeMatrix export and asks how leaders should respond to the people involved, how to support the crew or the people whose acts appear in the findings, what a restorative or just-culture response looks like, or how to look after a second victim. Not for HR's selection, qualification or staffing systems (use `people-workforce-learnings`) or a facilitated session where the team explains how the work is really done (use `learning-team-facilitator`).
---

# Restorative Response Guide

Audience: leaders and peer support (`leaders-and-peer-support`): the site and line leaders who respond to the people
involved, peer supporters, and employee-assistance and occupational-health contacts. The guide helps them **ask**;
it never tells them what the people involved feel, need or did wrong.

## Before you start

Engine: `PMLC` as defined in `skill-common.md` §1 (needs the `learnings-coach` skill installed alongside it).

- Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions).
- Needs: **workspace**. Optional: the register (`<run>/outputs/learnings-register.json`).
- Read `learnings-coach/references/learning-principles.md`: section 1 with its part "After the event: a restorative
  response to the people involved" (Dekker's three questions and the second victim), and section 1a.
- **The export holds no information about the people affected**: not their health, their feelings or what they
  want. It shows the conditions they worked in. Everything about the people is a question for a person to ask.

## Gather

```bash
PMLC select <ws> --text "on foot|head.?count|shanty|civilian|injur|casualt|evacuat|muster" --fields label,level,short   # who was in harm's way
PMLC select <ws> --level 2 3 4 --text "on foot|head.?count|shanty|civilian|injur|casualt|evacuat|muster" --brief   # the conditions they worked in
PMLC register-items <ws> --lr <LR-id> --lr <LR-id>   # with a register: its entries that cite those findings
```

- **The first call** finds the people the findings place in harm's way: those sent towards the release, those
  mustered or counted, anyone hurt. Read each label for the **role** only. On Hazira it gives 13 findings.
- **The second call** keeps levels 2-4: preconditions, supervision and organisation, the conditions people worked
  in. Level 1 findings describe the acts of a person: they never go in `system-conditions`. On Hazira it gives 11.
- **With a register**, take the entries whose `finding_ids` include any finding from the first call (on Hazira
  LR-07, LR-08, LR-12, LR-13 and LR-25), keep their wording and carry `learning: "LR-nn"`. Without one, write the
  conditions from the second call.
- Also read the incident narrative in `<ws>/incident.json` for who was on site and any stated casualties; quote it
  only as the export states it.

## Write

Pack `<run>/outputs/restorative-response-guide.json` (shape: `learnings-coach/references/pack-schema.md`),
`"scope": {"tiers": [], "levels": [2, 3, 4], "tags": []}`.

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | What leaders should do first, one line each | `bottom_line` | 1–3 |
| 1 | `banner` | About this guide | Exactly the fixed `restorative` banner (below) | `para` | 1 |
| 2 | `who-is-hurt` | Who is hurt? | One question per group of people the findings place in harm's way, named by role | `question` | 1–4 |
| 3 | `needs` | What do they need? | Questions to ask the people themselves; `to` = the role who asks | `question` | 2–6 |
| 4 | `obligations` | Whose obligation is it? | The organisation's obligations, by role, tied to the conditions | `para` | 1–3 |
| 5 | `system-conditions` | The conditions they worked in | Level 2-4 conditions only, with `learning: "LR-nn"` where the register has one | `learning` | 1–5 |
| 6 | `support` | Support for the people involved | Concrete support steps, second-victim support included | `check` | 2–6 |

- **Banner.** The first section holds exactly: "The export holds no information about the people affected. Every
  need here is a question to ask, or the organisation's own answer." (`banner:restorative`.)
- **Needs are asked, never inferred.** Every item in `who-is-hurt` and `needs` is a `question`; a statement such
  as "the crew need time off" is refused (`needs-are-questions`). The `why` says what in the findings makes the
  question worth asking; never answer it.
- **Obligations** belong to the organisation and its roles (site leadership, line leaders, HR and occupational
  health), never to the people involved.
- **System conditions.** Cite level 2-4 findings that show a condition (no defined qualification, no authority to
  isolate, a warning route that softened the message); drop every level 1 cite from register items. No owners and
  no dates (`no-owner-due`).
- **Support** names the second victim: the people whose acts appear in the findings can be harmed by the event too.
  Keep support apart from the investigation, and say so.
- **Language.** Counterfactual (JC3, "should have", "failed to") and hindsight (JC4, "obvious") wording are errors
  in this pack (`lint_errors`); rewrite with learning-principles.md §1a, never quiet them with `lint_ok`.

```json
{"kind": "question", "question": "How are the two control-room engineers who walked towards the vapour cloud now, and what would help?",
 "why": "They were sent on foot towards a dense cloud [EVD-1460].", "to": "Site leader, with a peer supporter",
 "cites": ["FND-13708453", "EVD-1460"]}
```

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/restorative-response-guide.json (repository only)

## If the evidence is thin

- **Nobody is placed in harm's way by the findings:** one `who-is-hurt` question about everyone on shift is a
  valid pack; say in `limits` that the export does not say who was exposed.
- **No register:** write the conditions from the second call and leave `learning` out.
- `skill-common.md` §6 covers the rest.

## Not covered here

- HR's selection, qualification and staffing standards: `people-workforce-learnings`.
- A facilitated session where the team explains how the work is done: `learning-team-facilitator`.
- Any review of a named person's conduct, any welfare record or medical detail: outside this skill and outside
  ProbeMatrix.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/restorative-response-guide.json --strict
PMLC pack <ws> <run>/outputs/restorative-response-guide.json
PMLC pack <ws> <run>/outputs/restorative-response-guide.json --format docx   # Word, for the leaders' meeting
```

- **Word** (`restorative-response-guide.docx`) for the leaders and peer supporters to take into their
  conversations. It is internal by default: it speaks about people who work here, so do not share it outside.
- The answers the people give stay with the organisation. Never write them into the pack.
