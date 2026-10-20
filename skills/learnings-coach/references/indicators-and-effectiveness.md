# Indicators and learning effectiveness

How to design a leading indicator, and how to tell whether a lesson has been learned rather than only identified. Cite this file from any skill that writes `indicator` items, `recommendation.indicator`, follow-up agendas, training transfer measures or the register's `learning_level` and `verification` fields.

## Contents
1. Indicator design
2. Lead and lag
3. Method sources
4. Lesson identified versus lesson learned
5. Verification levels and Kirkpatrick levels
6. Follow-up patterns
7. Single-loop and double-loop learning
8. Competence gap or system problem

## 1. Indicator design

Every indicator a pack proposes should be specified well enough that its owner could start measuring it next month. Write these fields, in the indicator's `name`, `measure`, `deterioration` and `owner`, or in the register's `leading_indicator` text:

| Field | What to write | Example |
|---|---|---|
| Owner role | The role that collects it and acts on it. Never a person's name. | maintenance planning lead |
| Data source | The system or record it comes from, preferably one the function already has (CMMS, permit system, training records, audit tracker, shift log). | permit-to-work register |
| Numerator / denominator | What is counted, over what. A count without a denominator cannot show a trend. | pump restarts with a leak-test record / all pump restarts |
| Threshold | The value that counts as healthy. | 100% each month |
| Deterioration trigger | The value or pattern that starts a response, and what that response is. | any month below 95%, or two months falling: area authority reviews the open cases within a week |
| Lead or lag | Whether it measures the health of a barrier before harm (lead) or outcomes after it (lag). See §2. | lead |
| Gaming risk | How the number could improve without the barrier improving, and how to check for that. | records filled in after the fact: sample five restarts a month against the shift log |

Rules:
- Tie each indicator to one barrier or one learning (`barriers-and-controls.md` §5), so a change in the number means something.
- Prefer two to four indicators a function will really use over a long list.
- Take no figures from outside the export: thresholds are proposals for the owner to set, written as "for the owner to set" when the evidence gives no basis.

## 2. Lead and lag

- **Leading indicators** measure the condition of barriers and the activities that keep them healthy: tests done on time, overdue defects, permits audited, drills completed with all roles present. They change before harm happens.
- **Lagging indicators** count outcomes: releases, fires, injuries, barrier demands. They confirm a trend after the fact.
- A pack's indicators are leading by default. Name a lagging indicator only as the outcome the leading set is meant to move.

## 3. Method sources

These are well-known sources of indicator method. Name them only as method references, never as evidence about the incident, and only when the audience would recognise them.
- API RP 754 tiered process-safety event indicators, Tier 1 to Tier 4 (unverified).
- UK HSE HSG254 dual assurance: a leading and a lagging indicator for each risk control system (unverified).
- IOGP 456 process-safety recommended practice on key performance indicators (unverified).

"(unverified)" means the Learnings Coach has not checked the current edition. Check the edition before citing it in a pack for an external audience.

## 4. Lesson identified versus lesson learned

- A **lesson identified** is a learning written down: in a register row, a pack, a briefing.
- A **lesson learned** is a learning that has changed how work is done, and the change has been checked to hold. Until then, call it identified.
- Packs from this coach produce lessons identified. They become learned only through the organisation's own follow-up, recorded in `verification.jsonl` (written blank by the engine and filled in by the organisation).

## 5. Verification levels and Kirkpatrick levels

Each learning moves through four verification levels. Record the level reached, the date and the evidence, with the assessing role, never a name.

| Level | Meaning | Typical evidence |
|---|---|---|
| communicated | The intended audiences received the learning. | distribution record, attendance |
| understood | They can explain what it means for their work. | short questions at a toolbox talk, a supervisor conversation |
| applied | The changed practice or system is in use. | sampled records, field observation, a revised procedure in use |
| effective | The barrier is healthier and the indicator shows it. | the leading indicator at threshold for an agreed period |

For training, the Kirkpatrick levels say the same thing from the learner's side:
1. **Reaction**: did participants find it relevant?
2. **Learning**: can they show the knowledge or skill afterwards?
3. **Behaviour**: do they use it at work (transfer)?
4. **Results**: has the targeted condition or barrier improved?

Kirkpatrick 1–2 support "understood"; Kirkpatrick 3 supports "applied"; Kirkpatrick 4 supports "effective". A course completion rate is level 1 at best.

## 6. Follow-up patterns

Use one of these, so different skills do not invent their own:
- **30/60/90 days** (functions and supervisors): by day 30, verify the condition still exists and contain it; by day 60, draft the system change with the people who do the work; by day 90, the leading indicator appears in the regular management report.
- **3/6/12 months** (leadership, board, training transfer): at 3 months, communicated and understood across the audiences; at 6 months, applied, checked by sampling; at 12 months, effective, shown by the indicator over time, or the learning reopened.

Write the windows as relative horizons, not calendar dates, unless the user asks for dates. The engine leaves owner and due-date columns blank.

## 7. Single-loop and double-loop learning

The register's `learning_level` names one of these. Use the written criteria, not a feel for the learning's importance.

- **Single-loop**: the fix corrects the work within the existing rules, goals and assumptions. Criteria, all of which hold:
  1. the change restores or tightens an existing control (repair, re-test, re-brief, enforce an existing check);
  2. no policy, standard, resource allocation or decision right changes;
  3. the question answered is "are we doing things right?".
- **Double-loop**: the fix changes the rules, goals, assumptions or norms that let the condition arise. Criteria, at least one of which holds:
  1. a policy, standard, design basis or acceptance criterion changes;
  2. resources, staffing or decision rights move;
  3. an assumption that the findings show was wrong is named and replaced (for example, "a passed audit means the barrier is healthy");
  4. the question answered is "are we doing the right things?".

A level 4 finding usually needs double-loop learning; a single-loop fix for it is worth stating as a limit.

## 8. Competence gap or system problem

Before proposing training, test whether the issue is a competence gap or a system problem. It is a **competence gap** only when all of these hold:
1. the right way of working is defined, available and workable in the real conditions;
2. other people in the same role, with the same tools and time, do it correctly;
3. what was missing was knowledge or skill, not time, equipment, information or authority.

If any condition fails, it is a **system problem**: fix the procedure, the design, the resourcing or the supervision, and treat training as support for that fix, not as the fix. `training-designer` sends system problems to `manager-coach`.
