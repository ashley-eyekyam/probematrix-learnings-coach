# emergency-response-learnings

Learning for emergency response and fire services: fire crews, fire-water and fire-pump maintainers, emergency planners, incident and site controllers, security and CCTV staff, and the control-room roles who make the first response decisions. It covers detection to isolation, alarm and communication, command and authority, plan coverage, drills and fire-protection readiness.

## What it is for

- "What should the fire service, the emergency team or incident command learn?"
- Input to an emergency plan review.
- Drill scenarios and response-time lessons.

Learnings are about the system and the plan, never a judgement on the people who responded under pressure.

## How to start it

- "What should our emergency response team learn from this investigation?"
- "Build the response timeline from detection to isolation, with the gaps between steps."
- "Give me three drill scenarios built from this event, with the decision points to test."

## What it needs

- `clusters.json`. The skill selects the functions tagged `emergency`: in the default list F09a Fire-fighting Operations & Fire-water Systems, F09b Emergency Planning & Command and F10 Security & Surveillance.
- The incident narrative, for the response timeline.

## Engine commands and flags

```bash
pmlc select <ws> --tag emergency --brief
pmlc select <ws> --tag emergency --top-rated
pmlc select <ws> --text "alarm|detect|isolat|MOV|valve|drill|fire.?water|pump|evacuat|command|CCTV" --brief
pmlc select <ws> --preset emergency-response-learnings   # the three calls above at once
pmlc timeline <ws> --on incident                          # writes timeline_event_day.json
pmlc check-pack <ws> <run>/outputs/emergency-response-learnings.json
pmlc pack <ws> <run>/outputs/emergency-response-learnings.json
```

- [select](../commands/select.md): `--tag emergency` every function tagged emergency; `--top-rated` the strongest; `--text` a regular expression over the finding text (words about detection, alarm, isolation and response); `--brief` short entries.
- [timeline](../commands/timeline.md) with `--on incident` writes every clock time on the incident day, with its sources, to build the sequence from.
- [check-pack](../commands/check-pack.md) and [pack](../commands/pack.md) render the pack.

## What you get

`emergency-response-learnings.html` and `.md`:

1. a **response timeline**: detection, alarm, first call, decision, isolation, escalation and control, with the time between steps and what drove it;
2. **learnings by response phase**, where the evidence supports them;
3. **plan review input**: specific gaps for the plan owners (scenarios, decision criteria, delegated authority, remote isolation, communications);
4. three **drill scenarios** with injects, decision points and the time standard to measure;
5. **readiness indicators**, such as detection-to-isolation time in drills.

## Worked example (Hazira)

`select --tag emergency --brief` returned 48 findings, `--tag emergency --top-rated` returned 10 and the response-words search returned 280. `timeline --on incident` printed `29 clock times on 2020-09-24 written to …/timeline_event_day.json`. With `classify --overlay india-process-site`, F09b Emergency Planning & Command grew from 16 to 43 findings, because the overlay places site words such as ERDMP (the emergency plan) and SIC / CIC (the site and chief incident controllers); this skill benefits most from that overlay on Indian process sites.

One response learning could rest on the evidence that the emergency isolation valves had "no remote operation from control room during emergency" (FND-7D28BE30, EVD-3932).

These counts are from the base classification, before the resolution pass. After you place the remaining roles, or add an overlay, they will be higher, as the overlay figures in the worked example above show (F09b 16 to 43).

## Related skills

- [barrier-learnings](barrier-learnings.md): the mitigation barriers in depth.
- [supervisor-coach](supervisor-coach.md): what a supervisor may decide without waiting.
- [precursor-timeline](precursor-timeline.md): the warnings before the day.
- Recipe: [Add an industry overlay](../Workflows-and-recipes.md#add-an-industry-overlay).
