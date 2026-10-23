# Risk Register Update: Synthetic pump fire, 2024

**DRAFT**

Review: draft · Classification: internal · Version 1.0

Draft because: no finding is marked as edited by a person

*Learning purposes: not a statutory document · Learnings drafted by an AI agent from AI-assisted findings*

*About 1 min read*

**Audience:** Enterprise risk management

**Incident:** Synthetic pump fire · 2024-03-20

## Bottom line

- Add the threat of an unspecified seal on the pump, and revisit the rating of the leak test after maintenance. [FND-0002; FND-0003; EVD-0002] *(learning: LR-01)*

## About this pack

Proposals for the risk owner to assess: no loss estimates and no rating decisions.

## Proposed risk-register changes

**Risk:** Loss of containment at the pump
**Type of change:** missing-threat
**Current assumption:** Seals match the original specification.
**What the evidence says:** Seals were bought locally without a specification [EVD-0003].
**Proposed change:** Add an unspecified seal as a threat to this risk. [FND-0003; EVD-0003]

**Risk:** Loss of containment at the pump
**Type of change:** control-rating
**Current assumption:** A leak test is done before every restart.
**What the evidence says:** The procedure index has no return-to-service entry [EVD-0002].
**Proposed change:** Reassess the rating of the leak-test control against its records. [FND-0002; EVD-0002]

*(learning: LR-01)*

## Key risk and control indicators

**Indicator:** Restarts with a leak-test record [FND-0002]
- Measure: Share of pump restarts with a signed test record
- Deterioration looks like: Any restart without a record

## Barriers for the bow-tie

### Prevention

**Barrier:** maintenance and testing: leak test before return to service [FND-0002; FND-0001]
- Failure mode: No checklist required the test
- Type: procedural
- State on the day: absent
- Control tier: engineering
- Fix: Interlock the restart on a signed test record

## Limits of this pack

- The synthetic export holds no cost or loss data, so the pack gives no loss estimate.

---

This pack cites 2 of 3 relevant findings.

2 of 2 top-rated relevant findings cited.

> Generated with ProbeMatrix Learnings Coach v2.0.0a6 (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
