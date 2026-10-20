# Barriers and controls

One vocabulary for barriers, barrier states, bow-tie terms, management-system elements and the hierarchy of controls. `barrier-learnings`, `engineering-integrity-learnings`, `emergency-response-learnings`, `auditor-assurance-pack`, `learnings-register`, `cluster-learning-dossier` (S7), `organisation-learning-map` and `interface-learnings` use these words, so a barrier named in one pack means the same thing in every other. The terms below are method vocabulary, never evidence about an incident: what a barrier did on the day comes only from cited findings and evidence.

## Contents
1. Barrier, control, safeguard
2. Bow-tie vocabulary
3. Barrier states
4. Critical controls
5. Barrier and element list
6. Hierarchy of controls
7. Borderline tiers
8. How the engine reads a tier (`norm_hoc`)

## 1. Barrier, control, safeguard

- **Barrier**: anything that stands between a hazard and harm, by preventing the loss of control or by limiting what follows it. A barrier has a function (what it stops), an owner and a state.
- **Control**: a measure that delivers or supports a barrier: a design feature, a device, a procedure, a check, a competence. One barrier usually rests on several controls (a gas detector is the device; its calibration and the response to its alarm are further controls).
- **Safeguard**: used as a synonym for barrier in process-hazard studies. In packs, prefer "barrier" and keep "safeguard" only when quoting a source that uses it.

## 2. Bow-tie vocabulary

| Term | Meaning |
|---|---|
| Hazard | The source of potential harm, e.g. a flammable gas under pressure. |
| Top event | The moment control of the hazard is lost, e.g. a loss of containment. |
| Threat | A way the top event can come about, e.g. a seal that does not hold. |
| Consequence | An outcome that can follow the top event, e.g. a fire. |
| Prevention barrier | Sits between a threat and the top event (left side). |
| Mitigation barrier | Sits between the top event and a consequence (right side). |
| Escalation factor | A condition that weakens a barrier, e.g. a detector out of service. |
| Escalation factor control | What keeps the escalation factor in check, e.g. a defect-reporting and repair system. |

**Barrier type** describes how the barrier works:
- **active**: it detects and acts, automatically or with a person (a trip, an alarm and response);
- **passive**: it works by being there (a bund, a fire wall, spacing);
- **procedural**: it works by people following a written method (a permit, a test before return to service);
- **behavioural**: it works through people's judgement and skill without a fixed procedure (a crew noticing an unusual smell).

To hand barrier items to a bow-tie tool, map: barrier → barrier, side → prevention or mitigation, `state` → barrier status, the L2–L4 findings behind the state → escalation factors, the fix → escalation factor control.

## 3. Barrier states

The pack `barrier` kind takes exactly these states. Choose the one the cited evidence supports; when the export does not say, write "[GAP]" rather than guess.

| State | Meaning |
|---|---|
| `absent` | The barrier did not exist, or was never provided, at the time of the event. |
| `degraded` | The barrier existed but was weaker than designed: out of calibration, partly maintained, under-resourced. |
| `defeated` | The barrier was in place but was bypassed, overridden or isolated, deliberately or as normal practice. |
| `worked partly` | The barrier acted but too late, too little or only for part of the event. |
| `worked` | The barrier did what it was designed to do. Include working barriers: they are learning too. |

## 4. Critical controls

A **critical control** is a control whose absence or failure would significantly raise the risk of a major event, even with the other controls in place. Call a control critical only when the findings show it was the main or the last line between the hazard and the outcome, or when the organisation's own documents name it so. Each critical control needs a named owner role, a performance standard and a leading indicator (`indicators-and-effectiveness.md`).

## 5. Barrier and element list

Use these names for `barrier` fields, register `barrier` and `org_system`, auditor test-point groups, engineering themes and emergency response phases. Add a site-specific barrier under the nearest heading rather than inventing a new heading.

**Prevention side** (before loss of control):
- design and specification (including substitution of parts and materials)
- maintenance and testing (including testing after maintenance)
- inspection and integrity (corrosion, thickness, ageing equipment)
- procedures and permits (permit-to-work, isolation, hold points)
- competence and staffing
- change management (MOC, documents and as-built records)
- materials and spares

**Mitigation side** (after loss of control):
- detection and alarm
- isolation and shutdown (including remote isolation)
- ignition control (hazardous-area equipment)
- communication and escalation
- emergency command and decision authority
- fire-water and fire protection
- escape, rescue and recovery

**Assurance** (keeps both sides healthy): audit and follow-up of recommendations, records, management review. These map to register `org_system` values and to auditor test-point groups.

## 6. Hierarchy of controls

Name the tier on every recommendation, using exactly these words. The order runs from strongest to weakest.

| Tier | What it does | Example |
|---|---|---|
| `elimination` | Removes the hazard. | Remove a redundant gas line instead of maintaining it. |
| `substitution` | Replaces the hazard with a lesser one. | Use a non-flammable test medium. |
| `engineering` | Designs the hazard away from people or acts on it automatically. **Isolation and separation** (physical isolation, spacing, enclosure, interlocks, automatic trips) count as engineering. | An interlock that blocks start-up until the isolation is proven. |
| `administrative` | Changes how work is organised: procedures, checks, permits, plans, reviews, audits, sign-offs, schedules. | A hold point before return to service, signed by the area authority. |
| `training` | Builds knowledge and skill. | A practical session on reading the new gas-detection display. |
| `ppe` | Protects the individual (personal protective equipment). | Flame-resistant clothing for the fire crew. |

Rules:
- Prefer the strongest tier the evidence and the organisation can credibly support. When the cited cause sits at level 3 or 4, add at least one change at the cause's level, not only training or a procedure (lint rule JC6).
- Level 3 (supervision) learnings often end in administrative fixes, because supervision is itself an administrative control. That is acceptable when the administrative change is the system fix (a new hold point, a resourced check). Say so in `why_not_stronger` when nothing above administrative is offered.
- Training is never the only fix for a condition the organisation created (see the competence-gap test in `indicators-and-effectiveness.md`).

## 7. Borderline tiers

| Wording | Tier | Why |
|---|---|---|
| Interlock, trip, automatic shutdown | `engineering` | It acts without a person. |
| Physical isolation, blinding, spacing, enclosure | `engineering` | Isolation is a form of engineering. |
| Isolation procedure, isolation certificate | `administrative` | The control is the written method, not the hardware. |
| "Engineering review of the procedure" | `administrative` | The output is a reviewed procedure; the word "engineering" names who reviews. |
| Checklist, audit, inspection schedule | `administrative` | They organise checking work. |
| Alarm that needs a person to respond | `administrative`, plus the engineering part named in the text | Its effect depends on the response; record the alarm hardware and the response as two controls where possible. |
| Alarm that triggers an automatic action | `engineering` | The action does not depend on a person. |
| Awareness campaign, toolbox talk, briefing | `training` | It changes knowledge, not the work. |
| Signage, labels, colour coding | `administrative` | Information that relies on people noticing it. |

## 8. How the engine reads a tier (`norm_hoc`)

`check-register` and the organisation map normalise free-text `hoc_tier` values. The rule (Ruling P3-4):
1. An exact tier name gives that tier (case-folded, trimmed, an optional trailing " control" or " controls" ignored). "Personal protective equipment" gives `ppe`.
2. Otherwise, text with exactly one tier word and none of the administrative cues gives that tier.
3. Text with an administrative cue gives `administrative`. The cues are `review`, `procedur`, `checklist`, `audit`, `permit`, `plan`, `instruction` and `sign`, each matched at the start of a word (so "design" does not count as `sign`).
4. Anything else gives `unclassified`, and `check-register` warns "hoc_tier '<v>' is ambiguous".

So "engineering control" gives `engineering`, "Engineering review of the procedure" gives `administrative`, and "engineering and training" gives `unclassified`. Write the tier as one exact word to avoid the warning.
