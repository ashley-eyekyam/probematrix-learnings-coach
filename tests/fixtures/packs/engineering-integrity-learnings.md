# Engineering and Integrity Learnings: Synthetic pump fire, 2024

**DRAFT**

Review: draft · Classification: internal · Version 1.0

Draft because: no finding is marked as edited by a person

*Learning purposes: not a statutory document · Learnings drafted by an AI agent from AI-assisted findings*

*About 1 min read*

**Audience:** Engineering, integrity, MOC and I&C

**Incident:** Synthetic pump fire · 2024-03-20

## Bottom line

- Seals bought without a specification entered service with no technical approval. [FND-0003]

## Technical learnings by theme

### Specification and substitution

**Learning:** A part without a specification is an unreviewed design change. [FND-0003]

Seals were bought locally without a specification from March 2022 [FND-0003; EVD-0003].

- Owner: Reliability engineering

**Barrier:** Technical approval of substitute parts [FND-0003]
- Failure mode: No approval step existed for local purchases
- Type: prevention
- State on the day: absent
- Owner: Reliability engineer (absent)
- Control tier: engineering
- Fix: Block critical-spares orders without a specification in the purchasing system
- Leading indicator: % of critical-spares orders with a specification reference

**Recommendation:** Route: MOC. Put every substitute part through change control before it is bought [FND-0003]
- Control tier: administrative
- Leading indicator: Substitutions approved through change control

## Alarms and automation

### Gas alarm with no executive action

**Learning:** A gas alarm that only lights a display leaves the shutdown to whoever notices it. [FND-0004; EVD-0002]

The DCS list shows no shutdown on the gas detector [FND-0004; EVD-0002].

- Owner: Instrument engineering

**Barrier:** Gas detection that starts isolation [FND-0004]
- Failure mode: The detector alarmed on the display; nothing tripped
- Type: mitigation
- State on the day: worked partly
- Owner: Instrument engineering
- Control tier: engineering
- Fix: Confirmed-gas logic that starts isolation
- Leading indicator: % of gas detectors with an executive action

**Recommendation:** Route: MOC. Add confirmed-gas logic that starts isolation of the pump [FND-0004; EVD-0002]
- Control tier: engineering
- Leading indicator: Detectors with a tested executive action

## Engineering decisions pending

**Decision:** Which leak test applies after a seal change, and at what pressure? [FND-0001]
- Options: Set by the technical authority per pump class; One site-wide test standard
- Owner: Technical authority

*(learning: LR-01)*

## Data and records

- [ ] Each critical spare's record names its specification and approver. *(at receipt)* [FND-0003]

---

This pack cites 1 of 1 relevant findings.

1 of 1 top-rated relevant findings cited.

> Generated with ProbeMatrix Learnings Coach v2.0.0a6 (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
