---
name: supervisor-coach
description: Produces learning for first-line supervisors from a ProbeMatrix investigation export - shift in-charges, maintenance and operations supervisors, permit issuers, calibration signatories, foremen - covering what to check before work starts, what to verify before equipment returns to service, what to escalate and what to refuse, how to brief the crew, as checklists and a coaching guide. Use when someone has a ProbeMatrix export and asks what supervisors or shift leads should learn, for supervisor briefings, hold points, sign-off checks, or how to strengthen supervision after an incident. Not for the crew's own cards and toolbox talks (use `frontline-learning-cards`).
---

# Supervisor Coach

Audience: T2 first-line supervision. They decide which work starts and which work is accepted, and they are
the delivery channel for frontline learning. In most ProbeMatrix analyses the Supervision level (L3) is the
largest; this is where much of the learning lives.

## Before you start

Engine: `PMLC` as defined in `skill-common.md` §1 (needs the `learnings-coach` skill installed alongside it).

- Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions).
- Needs: **workspace** and **clusters**.
- Read `learnings-coach/references/learning-principles.md`. The L3 sub-categories are in
  `learnings-coach/references/hfacs-levels.md` §2.
- **Start from the register if present.** `PMLC register-items <ws> --tier T2` prints the T2 learnings as ready
  items: keep their wording and carry `learning: "LR-nn"` on the items that express one.

## Gather

```bash
PMLC select <ws> --tier T2 --brief                      # what supervisors were involved in
PMLC select <ws> --level 3 --top-rated                  # supervision factors that mattered most
PMLC select <ws> --tier T2 --relation approver          # sign-offs and acceptances
PMLC register-items <ws> --tier T2                      # register learnings, when the register exists
```

- Group the L3 findings by sub-category: inadequate supervision, planned inappropriate operations, failure to
  correct a known problem, supervisory violations. These map to four supervisor habits: **oversee, plan,
  correct, make the safe way the easy way**. The last is about the system around the crew (tools, parts, time,
  clear hold points), not about policing people.
- If `<run>/outputs/frontline-learning-cards.json` exists, read its card titles for "Brief your crew".

## Write

Pack `<run>/outputs/supervisor-coach.json` (shape: `learnings-coach/references/pack-schema.md`),
`"scope": {"tiers": ["T2"]}`. Give each check a `group`, one of the four habits:
Oversee, Plan, Correct, Make the safe way the easy way. The page prints the checks as a checklist.

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | The supervisor learnings from this event | `bottom_line` | up to 5 |
| 1 | `before-work` | Before work starts | Checks drawn from the findings (spec of parts, test requirements, permit scope, crew competence, known history of the equipment), each citing its evidence | `check` | up to 10 |
| 2 | `return-to-service` | Before equipment returns to service | Hold points and acceptance criteria, `"hold_point": true` | `check` | up to 8 |
| 3 | `known-problems` | Known problems | How to treat repeats (a third repair on the same item is a signal, not a routine), when and to whom to escalate | `para` | up to 3 |
| 4 | `emergency` | In an emergency | Decisions a supervisor should be authorised and prepared to take without waiting, if the findings show delay from escalation; questions for the site to settle, `to` the site role | `question` | up to 5 |
| 5 | `refuse` | What to refuse | Situations from this event where a supervisor should decline to start or accept work, and the support to expect from management | `check` | up to 6 |
| 5 | `refuse` | What to refuse | The stop-work and right-to-warn note (below) | `para` | 1 |
| 6 | `recommendations` | Recommendations and how supervisors will know they are working | change, barrier, `hoc_tier`, and a leading `indicator` a supervisor can read from their own shift records | `recommendation` | up to 6 |
| 7 | `coaching` | Coaching conversations | Short scenarios from the event for a team meeting, with prompts | `scenario` | up to 3 |
| 8 | `brief-crew` | Brief your crew | Columns Order, Card, Bring back, Where the check should live; one row per frontline card | `table` | 1 |

- **Indicators.** Every recommendation needs one, readable from shift records (e.g. "% of pressure-boundary jobs
  released with a design-pressure test record", "repeat repairs on the same tag escalated within 7 days"). A
  recommendation without an indicator is not finished.
- **Emergency authority** is a question for the site to settle, never authority the supervisor already has.
- **Brief your crew.** Which frontline cards to run, in what order (the task the crew does next first),
  what to bring back (questions raised, concerns, a check the crew could not do), and where each check should
  live so it becomes a form change rather than a reminder: the permit form, the return-to-service certificate,
  the shift log or the job card. Use the card titles from `frontline-learning-cards` when that pack exists;
  otherwise name the learnings and add "run frontline-learning-cards" in a `limits` line.
- **Stop-work and right-to-warn note.** Say that some regimes give workers and supervisors a right to stop work
  or to warn of imminent danger, and that the site should confirm which apply and how a refusal is supported.
  Name a regime only from `learnings-coach/references/jurisdictions.md` for the run's jurisdiction, marking an
  *(unverified)* item as such. State no legal conclusion: never say a right was breached or a duty unmet.

```json
{"kind": "check", "text": "Leak-test record attached and signed.", "hold_point": true,
 "when": "before return to service", "cites": ["FND-…"]}
```

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/supervisor-coach.json (repository only)

## If the evidence is thin

- **Few L3 findings:** write fewer checks; each must cite. Do not turn a level 1 act into a supervisor rule.
- **No delay from escalation in the findings:** keep "In an emergency" to one question that says the findings do
  not show it, citing the findings that show the response.
- **No frontline cards yet:** fill "Brief your crew" from the T1 learnings and say the cards are still to come.
- `skill-common.md` §6 covers the rest.

## Not covered here

- The crew's own cards, toolbox talks and stop-and-ask list: `frontline-learning-cards`.
- Management decisions on staffing, budgets and procedures: `manager-coach`.
- Training modules and assessment: `training-designer`.
- The delivery record: `distribution.csv` (below), not a table in this pack.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/supervisor-coach.json --strict
PMLC pack <ws> <run>/outputs/supervisor-coach.json
PMLC pack <ws> <run>/outputs/supervisor-coach.json --layout checklist      # the printable checklist
```

- **Checklist layout.** `supervisor-coach.checklist.html` prints every `check`, grouped by section, each with a
  tick box; a `hold_point: true` check is marked "Hold point", and each section ends with a "Checked by (role),
  Date, Shift" line for the supervisor to fill in by hand. It is a working copy for the shift, not the record of
  who was briefed: that is `distribution.csv` (below).
- **Distribution record.** Each crew briefing is recorded in `<run>/outputs/distribution.csv`: if the file does
  not exist, `PMLC templates <ws> distribution` writes it with one row per pack (it never overwrites; add a row
  for this pack instead). The organisation fills in the delivery columns; never fill them yourself.
- Next step: `frontline-learning-cards`, if the crew cards have not been written.
