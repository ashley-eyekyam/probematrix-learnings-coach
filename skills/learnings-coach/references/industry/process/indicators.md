# Process industries: leading indicator starters

Method reference, not evidence. Each row is a starting point that follows the indicator template in `../../indicators-and-effectiveness.md` §1. A pack proposes an indicator only when a cited finding supports it; thresholds are proposals "for the owner to set", never figures from the export or from outside it. Lead indicators come first; a lagging counterpart is named only as the outcome the set is meant to move.

Field order: Owner role, Data source, Numerator / denominator, Threshold, Deterioration trigger, Lead or lag, Gaming risk.

## Contents
1. Indicator starters
2. Method sources
3. Reading a set

## 1. Indicator starters

| Barrier | Indicator | Owner role | Data source | Numerator / denominator | Threshold | Deterioration trigger | Lead or lag | Gaming risk |
|---|---|---|---|---|---|---|---|---|
| Safety instrumented functions | Proof tests completed in the interval | instrumentation lead | maintenance system, test records | tests done on time / tests due | for the owner to set | any month below the threshold, or a critical test overdue: review of open items by the function head | lead | tests closed without results; sample the records against the work order |
| Bypass control | Active bypasses past their expiry | operations manager | bypass register | bypasses past expiry / active bypasses | for the owner to set | any critical bypass past expiry: shift review that day | lead | bypasses held outside the register; walk the control room panel against the register |
| Mechanical integrity | Overdue inspections on critical items | integrity lead | inspection plan | overdue critical inspections / critical inspections due | for the owner to set | a rising count two months running: planning review | lead | due dates reset instead of work done; track original due date |
| Relief devices | Devices tested within their interval | integrity lead | relief device register | devices in date / devices on register | for the owner to set | any device past interval with no deferral approval | lead | register gaps; reconcile the register with a plant walk |
| Alarm health | Standing alarms and alarm rate per operator hour | control systems lead | alarm system log | alarms above the agreed rate / operator hours sampled | for the owner to set | a sustained rise: alarm review | lead | alarms suppressed rather than resolved; count suppressions |
| Permit-to-work | Permits audited at the work site with isolation proved | HSE lead | permit audit sheets | permits audited with no gap / permits audited | for the owner to set | any permit with an unproved isolation: stop and review | lead | audits arranged in advance; unannounced sampling |
| Management of change | Changes closed out before start-up and temporary changes past expiry | engineering manager | MOC register | changes with a recorded pre-start-up check / changes started | for the owner to set | any change started without review; any temporary change past expiry | lead | checks signed without a site visit; sample sign-offs |
| Shift handover | Handovers recording open permits and bypasses | operations manager | shift log | handovers with the record complete / handovers sampled | for the owner to set | a pattern of gaps on one shift or unit | lead | pre-filled forms; compare with the permit register |
| Emergency response | Drills with every named role present | emergency planning lead | drill reports | drills with all roles / drills held | for the owner to set | a role absent from two drills in a row | lead | drills held at easy times; vary the scenario and time |
| Recommendation tracking | Actions from past events and studies closed with a check | HSE lead | action tracker | closed with a verification / closed | for the owner to set | actions closed with no check of effect | lead | closure by re-dating; check the verification field |
| Process safety events | Loss-of-containment events by size band | HSE lead | incident system | events in the period | not set: trend only | a rise in the lower band is a signal before a larger event | lag | under-reporting of small events; compare with the near-miss rate |

## 2. Method sources

Name these as method references only, never as evidence about the incident, and only when the audience would recognise them. "(unverified)" means the edition has not been checked by the Learnings Coach.
- API RP 754 tiered process-safety event indicators (unverified).
- UK HSE HSG254 dual assurance: a leading and a lagging indicator for each risk control system (unverified).
- IOGP 456 process-safety recommended practice on key performance indicators (unverified).
- CCPS process safety metrics guidance (unverified).

## 3. Reading a set

- Keep two to four indicators a function will really use.
- Tie each to one barrier or one learning (`barriers.md`).
- A set that all moves together can mean a shared weakness, such as one overloaded planner, rather than five problems.
