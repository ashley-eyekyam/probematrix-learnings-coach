---
name: emergency-response-learnings
description: Produces learning for emergency response and fire services from a ProbeMatrix investigation export - fire crews, fire-water and fire-pump maintainers, emergency planners, incident and site controllers, security and CCTV staff, and external responders where the evidence reaches them - covering detection to isolation, alarm and communication, command and authority, plan coverage, drills and fire-protection readiness, with plan-review input written as change requests. Use when someone has a ProbeMatrix export and asks what the fire service, emergency team, ERT or incident command should learn, for emergency plan (ERP/ERDMP/DMP) review input, drill scenarios, or response-time lessons. Not for one-page cards for crews or security staff (use `frontline-learning-cards`).
---

# Emergency Response Learnings

Audience: the Learning Clusters tagged `emergency` (in the default taxonomy F09a fire-fighting operations and
fire-water systems, F09b emergency planning and command, F10 security and surveillance), plus the control-room
roles who make the first response decisions. Learnings are for the system and the plan, not a judgement on the
people who responded under pressure.

## Before you start

Engine: `PMLC` as defined in `skill-common.md` §1 (needs the `learnings-coach` skill installed alongside it).

- Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions).
- Needs: **workspace** and **clusters**.
- Read `learnings-coach/references/learning-principles.md`; barrier words from
  `learnings-coach/references/barriers-and-controls.md`.
- **Start from the register if present.** In `<run>/outputs/learnings-register.json`, take the entries whose
  `owner_entity` is an `emergency` entity: keep their wording and carry `learning: "LR-nn"` on the items.

## Gather

```bash
PMLC select <ws> --tag emergency --brief                # the emergency functions' findings
PMLC select <ws> --tag emergency --top-rated            # the ones that mattered most
PMLC select <ws> --text "alarm|detect|isolat|MOV|valve|drill|fire.?water|pump|evacuat|command|CCTV" --brief
PMLC select <ws> --tag emergency --text "mutual.?aid|neighbour|villag|communit|off-?site|fire (brigade|service)|district" --brief   # external responders
PMLC timeline-item <ws> --event-day                     # the narrative's clock times as a ready timeline item
PMLC timeline <ws> --on incident                        # writes <ws>/timeline_event_day.json (sources per time)
```

- **Event-day sequence.** `timeline-item --event-day` prints one event per distinct clock time in the incident
  narrative, in clock order, with the whole sentence as `text` and as `cites` the findings whose text holds that
  time. Build the response timeline from it: keep each response step's `date` and `time` as printed, drop the
  entries that are not steps (a heading, a note on sources, a time on another day), rewrite `text` as the step,
  and narrow `cites` to the findings from the printed list that describe the step, plus their evidence. An event
  with empty `cites` rests on the narrative alone: keep its time, cite nothing, and say so in the section intro.

## Write

Pack `<run>/outputs/emergency-response-learnings.json` (shape: `learnings-coach/references/pack-schema.md`),
`"scope": {"tags": ["emergency"]}`.

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | The response learnings, one line each | `bottom_line` | up to 5 |
| 1 | `timeline` | Response timeline | Detection, alarm, first call, decision, isolation, ignition or escalation, control: one event per step from `timeline-item --event-day`, `received_by` = who got the alarm or call | `timeline` | 1 |
| 2 | `gaps-between-steps` | Gaps between steps | Columns From, To, Minutes, What the export says: one row per gap that matters (onset to detection, detection to alarm, alarm to decision, detection to isolation, ignition to cooling), with `row_cites` | `table` | optional, up to 1 |
| 3 | `by-phase` | Learnings by response phase | `group` = the phase: detection and alarm; communication and escalation; authority and decision to isolate; plan coverage; fire-water and fire-protection readiness; command structure; recovery; external responders and neighbours | `learning` | up to 15 |
| 4 | `plan-review` | Plan review input | A change request to the plan owner: columns Plan section, Change, Evidence; one row per gap (scenarios, decision criteria, delegated authority, remote isolation, communications), with `row_cites` | `table` | 1 |
| 4 | `plan-review` | Plan review input | The regulated-plan notification note (below) | `para` | 1 |
| 5 | `drills` | Drill scenarios | Drills from this event: the starting position in `situation`, the timed `injects` (below), the time standard to measure and facilitator notes in `prompts` | `scenario` | up to 3 |
| 6 | `readiness` | Readiness indicators | e.g. detection-to-isolation time in drills, fire-pump availability, plan scenarios with tested isolation steps | `indicator` | up to 6 |

- **Phases.** Up to three learnings per phase, and only the phases the evidence supports. Write the
  "External responders and neighbours" group (mutual aid, the public fire service, neighbouring sites and the
  community) only when the findings show it; otherwise leave it out.
- **Change request.** "Plan section" names the part of the emergency plan (e.g. "Isolation decision
  criteria"), "Change" says what the plan should add or say differently, and "Evidence" summarises the cited
  records. It is input for the plan owner's review, not a revised plan.
- **Regulated-plan notification note.** Say that where the emergency plan is a regulated plan, a change to it may
  need review by, or notice to, an authority, and that the plan owner should check this. Name a regime only from
  `learnings-coach/references/jurisdictions.md` for the run's jurisdiction (e.g. the ERDMP regulations for an
  Indian gas installation), marking an *(unverified)* item as such. State no legal conclusion.
- Events on the same day without a citable time keep your order.
- **Gaps between steps.** From and To are two event `time`s on the timeline; Minutes is To minus From, worked out
  from those times, never estimated. "What the export says" gives what the cited records say happened in that
  gap, in one line. Use only steps whose times are on the timeline; leave the table out when fewer than two are.
- **Injects.** Each drill's `injects` is the timed sequence a facilitator releases: `offset` is the time after
  the exercise starts (`+HH:MM`), `text` what the players are told, and `decision` the decision point it forces,
  taken from a decision the findings show. Offsets are exercise time, never the event's clock times.

```json
{"kind": "timeline", "events": [{"date": "YYYY-MM-DD", "time": "14:05", "text": "…", "received_by": "Control room operators",
 "cites": ["FND-…"]}]}
{"kind": "scenario", "situation": "…", "prompts": ["…"], "injects": [{"offset": "+00:00", "text": "…"},
 {"offset": "+00:10", "text": "…", "decision": "…"}], "cites": ["FND-…"]}
```

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/emergency-response-learnings.json (repository only)

## If the evidence is thin

- **No F09 findings** (the `emergency` selection returns no fire-fighting or emergency-planning findings): say so
  in the bottom line, keep the pack to the detection and alarm phase the other findings support, and add a
  `gaps` entry naming the response records that would settle it (drill reports, the emergency log).
- **No event-day times** (`timeline-item --event-day` prints an empty item and a note): build the timeline as an
  order of steps with no `time`, say in a `limits` line that the export gives no times, leave out
  `gaps-between-steps`, and drop any time-based indicator the evidence cannot support.
- `skill-common.md` §6 covers the rest.

## Not covered here

- One-page cards for crews and security staff: `frontline-learning-cards`.
- The barrier analysis behind detection and isolation: `barrier-learnings`.
- The years-long build-up before the day: `precursor-timeline`.
- Writing or revising the emergency plan itself: the plan owner, using the change requests above.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/emergency-response-learnings.json --strict
PMLC pack <ws> <run>/outputs/emergency-response-learnings.json
PMLC pack <ws> <run>/outputs/emergency-response-learnings.json --layout cards   # one inject card per page
PMLC pack <ws> <run>/outputs/emergency-response-learnings.json --format pptx    # the drill brief
```

- **Inject cards.** `emergency-response-learnings.cards.html` prints each inject on its own page, in order, for
  the facilitator to hand out at its offset. With no `injects`, the layout holds only the closing summary.
- **Drill brief.** `emergency-response-learnings.pptx` is a slide deck for the pre-drill briefing and the
  debrief: the response learnings, one slide per section, and the citations in the speaker notes.

- Check that every timeline `time` is one `timeline-item --event-day` printed, and that each gap's Minutes
  equals To minus From.
- Next step: send the plan-review table to the plan owner's review.
