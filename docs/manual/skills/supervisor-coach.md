# supervisor-coach

Learning for first-line supervisors: shift in-charges, maintenance and operations supervisors, permit issuers, calibration signatories and foremen. It covers what to check before work starts, what to verify before equipment returns to service, what to escalate and what to refuse, and how to brief the crew, as checklists and a coaching guide.

## What it is for

- "What should supervisors or shift leads learn?"
- Supervisor briefings, hold points and sign-off checks.
- Strengthening supervision after an incident, and planning how supervisors brief their crews.

Supervisors (tier T2) decide which work starts and which work is accepted, and they usually deliver the frontline cards. In most ProbeMatrix analyses the Supervision level (L3) is the largest, so much of the learning lives here. The crew's own cards come from [frontline-learning-cards](frontline-learning-cards.md).

## How to start it

- "What should our supervisors learn from this investigation?"
- "Give me a before-work checklist and the return-to-service hold points for the maintenance supervisors."
- "Plan how the shift in-charges brief their crews on the learning cards, and where each check should live."

## What it needs

- `clusters.json`, with the supervisory roles placed (see [learning-clusters](learning-clusters.md)).
- Optional: the Learnings Register (its T2 learnings and `LR-nn` ids), and the [frontline-learning-cards](frontline-learning-cards.md) pack, whose card titles fill "Brief your crew".

## Engine commands and flags

```bash
pmlc select <ws> --tier T2 --brief
pmlc select <ws> --level 3 --top-rated            # supervision factors that mattered most
pmlc select <ws> --tier T2 --relation approver    # sign-offs and acceptances
pmlc select <ws> --preset supervisor-coach        # all three calls at once
pmlc register-items <ws> --tier T2                # the register's T2 learnings, as ready items
pmlc check-pack <ws> <run>/outputs/supervisor-coach.json --strict
pmlc pack <ws> <run>/outputs/supervisor-coach.json
pmlc templates <ws> distribution                  # the delivery record, once per run
```

- [select](../commands/select.md): `--tier T2` keeps supervision-tier findings; `--level 3` the Supervision level; `--top-rated` the strongest; `--relation approver` the findings where a role approved or accepted something; `--brief` short entries. The preset runs the three calls in turn; add `--budget-chars` to cap the size.
- [register-items](../commands/register-items.md) prints the register's learnings for a tier.
- [check-pack](../commands/check-pack.md) with `--strict` checks the pack against its profile; [pack](../commands/pack.md) renders it. The page prints the checks as a checklist.
- [templates](../commands/templates.md) `distribution` writes `distribution.csv`, where each crew briefing is recorded. It never overwrites an existing file.

## What you get

`supervisor-coach.html` and `.md`:

1. the supervisor learnings (up to five);
2. **before work starts**: up to ten checks, each citing its evidence;
3. **before equipment returns to service**: hold points and acceptance criteria;
4. **known problems**: how to treat repeats, and whom to escalate to;
5. **in an emergency**: decisions the site should settle on what a supervisor may do without waiting, written as questions;
6. **what to refuse**, the support supervisors should expect from management, and a short note that some regimes give a right to stop work or to warn of imminent danger. The note names a regime only from the coach's [jurisdictions reference](https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/skills/learnings-coach/references/jurisdictions.md) and draws no legal conclusion;
7. **recommendations**, each with a leading indicator a supervisor can read from their own shift records;
8. up to three **coaching scenarios** for a team meeting;
9. **brief your crew**: which frontline cards to run, in what order, what to bring back, and where each check should live (the permit form, the return-to-service certificate, the shift log), so the check becomes a form change rather than a reminder.

Checks are grouped by four habits: oversee, plan, correct, and make the safe way the easy way.

## Worked example (Hazira)

`select --tier T2 --brief` returned 237 findings; `--level 3 --top-rated` returned 54; and `--tier T2 --relation approver` returned 28. A return-to-service hold point on Hazira would rest on the finding that the system was pressurised to operating pressure only after the gasket change, with no hydro test (FND-3AB996FC, EVD-2894); in "Brief your crew" that check would live on the return-to-service certificate.

These counts are from the base classification, before the resolution pass. After you place the remaining roles they will be higher, most for T3 (in one trial pass on Hazira, roughly T1 222→231, T2 237→238, T3 211→257; your numbers depend on how you place roles).

## Related skills

- [frontline-learning-cards](frontline-learning-cards.md): what the crew sees at the same hold points.
- [manager-coach](manager-coach.md): the systems that make the checks possible.
- [emergency-response-learnings](emergency-response-learnings.md): the emergency decisions in depth.
