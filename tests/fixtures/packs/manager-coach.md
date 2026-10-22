# Manager Coach: Synthetic pump fire, 2024

**DRAFT**

Review: draft · Classification: internal · Version 1.0

Draft because: no finding is marked as edited by a person

*Learning purposes: not a statutory document · Learnings drafted by an AI agent from AI-assisted findings*

*About 2 min read*

**Audience:** Function and department managers (T3)

**Incident:** Synthetic pump fire · 2024-03-20

## Bottom line

- Maintenance had no return-to-service checklist, so a skipped leak test went unseen. [FND-0002] *(learning: LR-01)*

## Mechanical Maintenance (F02)

### What your system allowed

**Learning:** Return to service relied on memory, not a checklist. [FND-0002]

The procedure index has no return-to-service entry [EVD-0002].

- Owner: Maintenance function

*(learning: LR-01)*

### Interfaces you share

Stores buys the seals that maintenance fits; agree who approves a substitute part [FND-0003].

### Recommendations

**Recommendation:** Add a signed leak-test hold point to every return to service [FND-0002; FND-0001]
- Control tier: administrative
- Barrier: Return-to-service test
- Owner: Maintenance function
- Leading indicator: % of restarts with a signed leak-test record
- Why not stronger: A start interlock on a test record needs a control-system change; the hold point is the first step.

### Leading indicators

**Indicator:** Restarts with a test record [FND-0001]
- Measure: % of pump restarts in the CMMS with a leak-test record attached
- Deterioration looks like: Any restart without one

### 90-day agenda

| Days | Action | Cites |
|---|---|---|
| 0-30 | Check whether restarts still happen without a test record | FND-0001 |
| 31-60 | Draft the checklist with the fitters | FND-0002 |
| 61-90 | Report the indicator monthly | FND-0002 |

## Work management: planners and schedulers

**Learning:** The seal-change job plan had no test step for the planner to schedule. [FND-0001; EVD-0001]

The work order shows no test [EVD-0001].

- Owner: Work planning function

**Recommendation:** Add a leak-test step to every pressure-boundary job plan template [FND-0002; EVD-0002]
- Control tier: administrative
- Barrier: Return-to-service test
- Leading indicator: % of pressure-boundary job plans with a test step
- Why not stronger: Job plan templates are the planning function's own control; an interlock sits with maintenance.

## Management review input

| Input | What this investigation shows | Indicator | Deterioration trigger | Cites |
|---|---|---|---|---|
| Incidents and corrective actions | A restart without a leak test led to the fire | % of restarts with a test record | Any restart without one | FND-0001 |
| Monitoring results | Not in this investigation |  |  |  |
| Audit results | Not in this investigation |  |  |  |
| Risks and opportunities | Unspecified local seals were a standing risk | % of critical spares to specification | Any month below target | FND-0003 |
| Adequacy of resources | Not in this investigation |  |  |  |
| Consultation outcomes | Not in this investigation |  |  |  |

## Summary

| Function | Top learning | Top recommendation | Indicator | Cites |
|---|---|---|---|---|
| Mechanical Maintenance | Return to service relied on memory | Signed leak-test hold point | % of restarts with a test record | FND-0002 |

---

This pack cites 1 of 1 relevant findings.

1 of 1 top-rated relevant findings cited.

> Generated with ProbeMatrix Learnings Coach v2.0.0a6 (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
