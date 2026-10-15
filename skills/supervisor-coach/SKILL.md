---
name: supervisor-coach
description: Produce learning for first-line supervisors from a ProbeMatrix investigation export - shift in-charges, maintenance and operations supervisors, permit issuers, calibration signatories, foremen - covering what to check before work starts, what to verify before equipment returns to service, what to escalate and what to refuse, as checklists and a coaching guide. Use when someone asks what supervisors or shift leads should learn, for supervisor briefings, hold points, sign-off checks, or how to strengthen supervision after an incident.
---

# Supervisor Coach

Audience: T2 first-line supervision. They decide which work starts and which work is accepted. In most ProbeMatrix analyses the Supervision level (L3) is the largest; this is where much of the learning lives.

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py`. Read `learnings-coach/references/learning-principles.md`.

## Gather

```bash
PMLC select <ws> --tier T2 --brief
PMLC select <ws> --level 3 --min-rating <top>                  # supervision factors that mattered most
PMLC select <ws> --tier T2 --relation approver                 # sign-offs and acceptances
```

Group L3 findings by sub-category: inadequate supervision, planned inappropriate operations, failure to correct a known problem, supervisory violations. These map to four supervisor habits: **oversee, plan, correct, enforce**.

## Write

1. **Bottom line**: the five supervisor learnings from this event.
2. **Before work starts**: a checklist of six to ten checks drawn from the findings (spec of parts, test requirements, permit scope, competence of the crew, known history of the equipment). Each check cites its evidence.
3. **Before equipment returns to service**: hold points and acceptance criteria.
4. **Known problems**: how to treat repeats (a third repair on the same item is a signal, not a routine) and when to escalate. Include who to escalate to.
5. **In an emergency**: decisions a supervisor should be authorised and prepared to take without waiting, if the findings show delay from escalation. Present them as questions for the site to settle, not as authority the supervisor already has.
6. **What to refuse**: situations from this event where a supervisor should decline to start or accept work, and the support they should expect from management.
7. **Recommendations and how supervisors will know they are working**: one row per recommendation: what should change, the barrier, the hierarchy-of-controls tier, and a **leading indicator a supervisor can read from their own shift records** (e.g. "% of pressure-boundary jobs released with a design-pressure test record", "repeat repairs on the same tag escalated within 7 days", "notifications closed with materials and test data entered"). Every recommendation needs one; a recommendation without an indicator is not finished.
8. **Coaching conversations**: three short scenarios from the event for supervisors to discuss in a team meeting, with prompts.

## Output

`<ws>/outputs/supervisor-coach.md`, with a one-page printable checklist at the end.
