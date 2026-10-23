# emergency-response-learnings

Learning for emergency response and fire services: fire crews, fire-water and fire-pump maintainers, emergency planners, incident and site controllers, security and CCTV staff, the control-room roles who make the first response decisions, and external responders and neighbours where the evidence reaches them. It covers detection to isolation, alarm and communication, command and authority, plan coverage, drills and fire-protection readiness, with plan-review input written as change requests.

## What it is for

- "What should the fire service, the emergency team or incident command learn?"
- Input to an emergency plan review.
- Drill scenarios and response-time lessons.

Learnings are about the system and the plan, never a judgement on the people who responded under pressure. One-page cards for crews and security staff come from [frontline-learning-cards](frontline-learning-cards.md).

## How to start it

- "What should our emergency response team learn from this investigation?"
- "Build the response timeline from detection to isolation, with the gaps between steps."
- "Give me three drill scenarios built from this event, with the decision points to test."

## What it needs

- `clusters.json`. The skill selects the functions tagged `emergency`: in the default list F09a Fire-fighting Operations & Fire-water Systems, F09b Emergency Planning & Command and F10 Security & Surveillance.
- The incident narrative, for the order of the response steps.
- Optional: the Learnings Register (entries owned by an emergency function, with their `LR-nn` ids).

## Engine commands and flags

```bash
pmlc select <ws> --tag emergency --brief
pmlc select <ws> --tag emergency --top-rated
pmlc select <ws> --text "alarm|detect|isolat|MOV|valve|drill|fire.?water|pump|evacuat|command|CCTV" --brief
pmlc select <ws> --tag emergency --text "mutual.?aid|neighbour|villag|communit|off-?site|fire (brigade|service)|district" --brief   # external responders
pmlc select <ws> --preset emergency-response-learnings   # the four calls above at once
pmlc timeline-item <ws> --event-day                       # the narrative's clock times as a ready timeline item
pmlc timeline <ws> --on incident                          # writes timeline_event_day.json
pmlc check-pack <ws> <run>/outputs/emergency-response-learnings.json --strict
pmlc pack <ws> <run>/outputs/emergency-response-learnings.json
pmlc pack <ws> <run>/outputs/emergency-response-learnings.json --layout cards   # one inject card per page
pmlc pack <ws> <run>/outputs/emergency-response-learnings.json --format pptx    # the drill brief
```

- [select](../commands/select.md): `--tag emergency` every function tagged emergency; `--top-rated` the strongest; `--text` a regular expression over the finding text (words about detection, alarm, isolation and response, or, with `--tag emergency`, about mutual aid, neighbours and the community); `--brief` short entries.
- [timeline-item](../commands/timeline-item.md) with `--event-day` prints one event per distinct clock time in the incident narrative, in clock order, with the whole sentence and the findings whose text holds that time. The agent keeps the response steps, drops entries that are not steps (a note on sources, a time on another day), rewrites each step and narrows its citations to the findings that describe it. A step with no citing finding rests on the narrative alone and is marked so.
- [timeline](../commands/timeline.md) with `--on incident` writes every clock time on the incident day, with its sources, to `timeline_event_day.json`.
- [check-pack](../commands/check-pack.md) with `--strict` checks the pack against its profile; [pack](../commands/pack.md) renders it.
- [pack](../commands/pack.md) `--layout cards` prints each drill inject on its own page, in order, for the facilitator to hand out; `--format pptx` writes `emergency-response-learnings.pptx`, a deck for the pre-drill briefing and the debrief, with the citations in the speaker notes.

## What you get

`emergency-response-learnings.html` and `.md`:

1. a **response timeline**: detection, alarm, first call, decision, isolation, escalation and control, at the times the incident narrative gives;
2. optionally, **gaps between steps**: a table of From, To, Minutes and what the export says about each gap that matters (onset to detection, detection to isolation, ignition to cooling). Minutes are worked out from the two times on the timeline, never estimated;
3. **learnings by response phase**, where the evidence supports them, including an "external responders and neighbours" group (mutual aid, the public fire service, neighbouring sites, the community) only when the findings show it;
4. **plan review input** as a change request to the plan owner: a table of plan section, change and evidence (scenarios, decision criteria, delegated authority, remote isolation, communications), and a note that a change to a regulated plan may need review by, or notice to, an authority. The note names a regime only from the coach's [jurisdictions reference](https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/skills/learnings-coach/references/jurisdictions.md) and draws no legal conclusion;
5. up to three **drill scenarios**: the starting position, the time standard to measure, and timed **injects**, each with its offset from the start of the exercise (`+00:10`), what the players are told and, where it applies, the decision point it forces;
6. **readiness indicators**, such as detection-to-isolation time in drills.

## Worked example (Hazira)

`select --tag emergency --brief` returned 48 findings, `--tag emergency --top-rated` returned 10 and the response-words search returned 280. The external-responder search returned 0, so the pack leaves that group out. `timeline --on incident` printed `29 clock times on 2020-09-24 written to …/timeline_event_day.json`; 11 of them are narrative-only (in the incident narrative, with no citable source), so they order the steps but carry no `time` of their own. With `classify --overlay india-process-site`, F09b Emergency Planning & Command grew from 16 to 43 findings, because the overlay places site words such as ERDMP (the emergency plan) and SIC / CIC (the site and chief incident controllers); this skill benefits most from that overlay on Indian process sites.

`timeline-item --event-day` printed 26 events, one per distinct clock time in the narrative. The sample pack keeps 21 of them as response steps, from the last camera frame with no vapour (02:11) to the all clear (07:30); it drops the shift handover the evening before and the narrative's notes on its own sources. Its gaps table shows, among others, 46 minutes from the first sighting (02:15) to the first isolation valve (03:01) and 42 minutes from ignition (03:08) to the start of fire cooling (03:50).

One response learning could rest on the evidence that the emergency isolation valves had "no remote operation from control room during emergency" (FND-7D28BE30, EVD-3932).

These counts are from the base classification, before the resolution pass. After you place the remaining roles, or add an overlay, they will be higher, as the overlay figures in the worked example above show (F09b 16 to 43).

## Related skills

- [barrier-learnings](barrier-learnings.md): the mitigation barriers in depth.
- [supervisor-coach](supervisor-coach.md): what a supervisor may decide without waiting.
- [precursor-timeline](precursor-timeline.md): the warnings before the day.
- Recipe: [Add an industry overlay](../Workflows-and-recipes.md#add-an-industry-overlay).
