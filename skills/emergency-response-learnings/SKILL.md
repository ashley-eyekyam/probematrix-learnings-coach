---
name: emergency-response-learnings
description: Produce learning for emergency response and fire services from a ProbeMatrix investigation export - fire crews, fire-water and fire-pump maintainers, emergency planners, incident and site controllers, security and CCTV staff - covering detection to isolation, alarm and communication, command and authority, plan coverage, drills and fire-protection readiness. Use when someone asks what the fire service, emergency team, ERT or incident command should learn, for emergency plan (ERP/ERDMP/DMP) review input, drill scenarios, or response-time lessons from an incident.
---

# Emergency Response Learnings

Audience: the Learning Clusters tagged `emergency` (in the default taxonomy F09a fire-fighting operations and fire-water systems, F09b emergency planning and command, F10 security and surveillance), plus control-room roles who make the first response decisions.

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py`. Read `learnings-coach/references/learning-principles.md`.

## Gather

```bash
PMLC select <ws> --tag emergency --brief
PMLC select <ws> --tag emergency --top-rated
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

Write the pack `<run>/outputs/emergency-response-learnings.json` (schema: `learnings-coach/references/pack-schema.md`), then:

```bash
PMLC check-pack <ws> <run>/outputs/emergency-response-learnings.json   # fix every problem it lists
PMLC pack <ws> <run>/outputs/emergency-response-learnings.json         # -> emergency-response-learnings.html (primary) and .md
```

Run `PMLC timeline <ws> --on incident` first: it writes `timeline_event_day.json`, the clock times on the day (each with its sources) to build the sequence from.

Sections → kinds:
1. A `timeline` with one event per step: `time` (HH:MM) where the evidence gives it, `received_by` = who got the alarm or call, and the gap since the previous step in `text`. Events on the same day without times keep your order.
2. `learning` items, with `group` = the response phase.
3. One `para` per gap.
4. `scenario` ×3: injects in `situation`, decision points and the time standard in `prompts`.
5. `indicator`.

Set `"scope": {"tags": ["emergency"]}`. Put data-quality corrections in `data_quality`, findings left out on purpose in `exclusions`, and same-condition findings in `supporting_cites`.

```json
{"kind": "timeline", "events": [{"date": "YYYY-MM-DD", "time": "14:05", "text": "…", "received_by": "Control room operators",
 "cites": ["FND-…"]}]}
```

Learnings are for the system and the plan, not a judgement on the people who responded under pressure.
