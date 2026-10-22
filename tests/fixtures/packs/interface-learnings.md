# Interface Learnings: Synthetic pump fire, 2024

**DRAFT**

Review: draft · Classification: internal · Version 1.0

Draft because: no finding is marked as edited by a person

*Learning purposes: not a statutory document · Learnings drafted by an AI agent from AI-assisted findings*

*About 2 min read*

**Audience:** Department managers

**Incident:** Synthetic pump fire · 2024-03-20

## Bottom line

- Maintenance fitted what stores bought, and the findings show no one owned the specification between them. [FND-0003; FND-0001]

## Interface matrix

| Interface | Shared findings | Cross-entity causal mentions | Cites |
|---|---|---|---|
| F02 Mechanical Maintenance × F06 Materials Management | 0 | 3 | FND-0001; FND-0003 |
| F05 Asset Integrity × F13 Plant & Asset Leadership | 1 | 0 | FND-0003 |

## Mechanical Maintenance and Materials Management

### The seam

A seal passes from stores to the fitters [FND-0003].

### What went wrong at the seam

The seal had no specification, and the restart had no test to catch a bad part [FND-0003; FND-0001].

### Why neither side saw it

The findings show no check by either side [FND-0003; FND-0001].

### The learning for each side

**Learning:** Stores: a critical spare needs a specification before purchase. [FND-0003]

- Owner: Materials Management (F06)

**Learning:** Maintenance: no restart without a leak test, whatever the part. [FND-0001]

- Owner: Mechanical Maintenance (F02)

### Joint fix

**Recommendation:** Add a specification check at the stores issue counter [FND-0003]
- Control tier: administrative
- Owner: Materials Management (F06)
- Co-owner: Mechanical Maintenance (F02)
- Leading indicator: % of critical spares issued with a specification reference

## Control Room and Emergency Planning (mitigation side)

### The seam

A gas alarm passes from the control room display to the emergency plan [FND-0004].

### What went wrong at the seam

The alarm displayed only, and the findings show no defined response step owned by either side [FND-0004].

### The learning for each side

**Learning:** Control room: every gas alarm needs a written first response. [FND-0004]

- Owner: Operations & Control Room (F01)

**Learning:** Emergency planning: the plan starts at the alarm, not at the call-out. [FND-0004; EVD-0002]

- Owner: Emergency Planning & Command (F09b)

### Joint fix

**Recommendation:** Add an automatic shutdown on the gas alarm, with a joint response card [FND-0004]
- Control tier: engineering
- Owner: Operations & Control Room (F01)
- Co-owner: Emergency Planning & Command (F09b)
- Leading indicator: Share of gas alarms with a tested shutdown and response step

## Joint-review agenda

| Interface | Roles who meet | Agenda item | Evidence to bring | Decision sought | Cites |
|---|---|---|---|---|---|
| F02-F06 | Maintenance planner; stores lead | Critical-spares substitutions | Purchase records for the last quarter | Who signs off a substitute part | FND-0003 |
| F01-F09b | Shift in-charge; emergency planning lead | First response to a gas alarm | Alarm list and the emergency plan | Which alarms trip and who acts | FND-0004 |

## Who must meet whom

- [ ] Maintenance planner and stores lead: monthly review of critical-spares substitutions [FND-0003]
- [ ] Shift in-charge and emergency planning lead: review the gas-alarm response cards together [FND-0004]

---

This pack cites 1 of 2 relevant findings.

1 of 2 top-rated relevant findings cited.

> Generated with ProbeMatrix Learnings Coach v2.0.0a6 (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
