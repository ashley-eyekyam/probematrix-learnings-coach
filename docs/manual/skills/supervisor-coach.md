# supervisor-coach

Learning for first-line supervisors: shift in-charges, maintenance and operations supervisors, permit issuers, calibration signatories and foremen. It covers what to check before work starts, what to verify before equipment returns to service, what to escalate and what to refuse, as checklists and a coaching guide.

## What it is for

- "What should supervisors or shift leads learn?"
- Supervisor briefings, hold points and sign-off checks.
- Strengthening supervision after an incident.

Supervisors (tier T2) decide which work starts and which work is accepted. In most ProbeMatrix analyses the Supervision level (L3) is the largest, so much of the learning lives here.

## How to start it

- "What should our supervisors learn from this investigation?"
- "Give me a before-work checklist and the return-to-service hold points for the maintenance supervisors."
- "Prepare three coaching scenarios for a shift in-charge team meeting."

## What it needs

- `clusters.json`, with the supervisory roles placed (see [learning-clusters](learning-clusters.md)).

## Engine commands and flags

```bash
pmlc select <ws> --tier T2 --brief
pmlc select <ws> --level 3 --top-rated            # supervision factors that mattered most
pmlc select <ws> --tier T2 --relation approver    # sign-offs and acceptances
pmlc select <ws> --preset supervisor-coach        # all three calls at once
pmlc check-pack <ws> <run>/outputs/supervisor-coach.json
pmlc pack <ws> <run>/outputs/supervisor-coach.json
```

- [select](../commands/select.md): `--tier T2` keeps supervision-tier findings; `--level 3` the Supervision level; `--top-rated` the strongest; `--relation approver` the findings where a role approved or accepted something; `--brief` short entries. The preset runs the three calls in turn; add `--budget-chars` to cap the size.
- [check-pack](../commands/check-pack.md) and [pack](../commands/pack.md) render the pack. The page prints the checks as a checklist.

## What you get

`supervisor-coach.html` and `.md`, in eight parts:

1. the five supervisor learnings;
2. **before work starts**: six to ten checks, each citing its evidence;
3. **before equipment returns to service**: hold points and acceptance criteria;
4. **known problems**: how to treat repeats, and whom to escalate to;
5. **in an emergency**: decisions the site should settle on what a supervisor may do without waiting, written as questions;
6. **what to refuse**, and the support supervisors should expect from management;
7. **recommendations**, each with a leading indicator a supervisor can read from their own shift records;
8. three **coaching scenarios** for a team meeting.

Checks are grouped by four habits: oversee, plan, correct, and make the safe way the easy way.

## Worked example (Hazira)

`select --tier T2 --brief` returned 237 findings; `--level 3 --top-rated` returned 54; and `--tier T2 --relation approver` returned 28. A return-to-service hold point on Hazira would rest on the finding that the system was pressurised to operating pressure only after the gasket change, with no hydro test (FND-3AB996FC, EVD-2894).

## Related skills

- [frontline-learning-cards](frontline-learning-cards.md): what the crew sees at the same hold points.
- [manager-coach](manager-coach.md): the systems that make the checks possible.
- [emergency-response-learnings](emergency-response-learnings.md): the emergency decisions in depth.
