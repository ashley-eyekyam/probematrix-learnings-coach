---
name: emergency-response-learnings
description: Produce learning for emergency response and fire services from a ProbeMatrix investigation export - fire crews, fire-water and fire-pump maintainers, emergency planners, incident and site controllers, security and CCTV staff - covering detection to isolation, alarm and communication, command and authority, plan coverage, drills and fire-protection readiness. Use when someone asks what the fire service, emergency team, ERT or incident command should learn, for emergency plan (ERP/ERDMP/DMP) review input, drill scenarios, or response-time lessons from an incident.
---

# Emergency Response Learnings

Audience: Learning Clusters F09a (fire-fighting operations and fire-water systems), F09b (emergency planning and command) and F10 (security and surveillance), plus control-room roles who make the first response decisions.

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py`. Read `learnings-coach/references/learning-principles.md`.

## Gather

```bash
PMLC select <ws> --entity F09a F09b F10 --brief
PMLC select <ws> --entity F09b --min-rating <top>
PMLC select <ws> --text "alarm|detect|isolat|MOV|valve|drill|fire.?water|pump|evacuat|command|CCTV" --brief
PMLC timeline <ws>                     # use the event-day sequence if present
```

Read the incident narrative for the response timeline.

## Write

1. **Response timeline**: detection → alarm → first call → decision → isolation → ignition / escalation → control, with the gap between each step and what drove it (evidence-linked).
2. **Learnings by response phase**: detection and alarm; communication and escalation; authority and decision to isolate; plan coverage (was the scenario in the plan, with actions?); fire-water and fire-protection readiness; command structure; recovery. Three to five learnings per phase where the evidence supports them.
3. **Plan review input**: specific gaps for the emergency plan owners (scenarios, decision criteria, delegated authority, remote isolation, communications), each with evidence.
4. **Drill scenarios**: three drills built from this event, with injects, the decision points tested, and the time standard to measure.
5. **Readiness indicators**: e.g. detection-to-isolation time in drills, fire-pump availability, plan scenarios with tested isolation steps.

## Output

`<run>/outputs/emergency-response-learnings.md`. Learnings are for the system and the plan, not a judgement on the people who responded under pressure.
