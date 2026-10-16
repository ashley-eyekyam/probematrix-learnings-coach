# Engineering and Integrity Learnings: Synthetic pump fire, 2024

*Learning purposes: not a statutory document*

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

**Recommendation:** Route every substitute part through change control [FND-0003]
- Control tier: administrative
- Leading indicator: Substitutions approved through change control

## Engineering decisions pending

**Decision:** Which leak test applies after a seal change, and at what pressure? [FND-0001]
- Options: Set by the technical authority per pump class; One site-wide test standard
- Owner: Technical authority

## Data and records

- [ ] Each critical spare's record names its specification and approver. *(at receipt)* [FND-0003]

---

This pack cites 1 of 1 relevant findings.

> Generated with ProbeMatrix Learnings Coach (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
