# Barrier Learnings: Synthetic pump fire, 2024

**DRAFT**

Review: draft · Classification: internal · Version 1.0

Draft because: no finding is marked as edited by a person

*Learning purposes: not a statutory document · Learnings drafted by an AI agent from AI-assisted findings*

**Audience:** Engineers and HSE

**Incident:** Synthetic pump fire · 2024-03-20

## Bottom line

- Two prevention barriers were absent and one mitigation barrier was degraded. [FND-0002; FND-0003; FND-0004]

## Barriers

### Prevention

**Barrier:** materials and spares: specification of critical spares [FND-0003; EVD-0003]
- Failure mode: Local purchase without a specification since March 2022
- Barrier ID: BR-12
- Type: procedural
- State on the day: absent
- Owner: Materials Management (F06)
- Control tier: engineering
- Fix: Purchasing system blocks critical-spares orders without a specification
- Leading indicator: % of critical-spares orders with a specification

**Barrier:** maintenance and testing: leak test before return to service [FND-0002; FND-0001]
- Failure mode: No checklist required the test
- Barrier ID: BR-07
- Type: procedural
- State on the day: absent
- Owner: Maintenance supervision (F02, T2)
- Control tier: administrative
- Fix: Signed hold point
- Leading indicator: % of restarts with a test record

### Mitigation

**Barrier:** detection and alarm: gas detection with shutdown [FND-0004]
- Failure mode: Alarm displayed only; no automatic action
- Type: active
- State on the day: degraded
- Control tier: engineering
- Fix: [GAP] the export does not say whether a trip was intended

## What the barriers show

Failures cluster on the prevention side. Of the two fixes the export supports, one is above the administrative tier; the mitigation fix is still a gap [FND-0002; FND-0003; FND-0004].

## Critical controls to verify first

- [ ] Leak test before return to service [FND-0002] *(Clauses: ICMM-CCM-8)*
- [ ] Specification of critical spares [FND-0003]

## Barriers not in the organisation's register

| Barrier | Side | Why unmapped | Cites |
|---|---|---|---|
| detection and alarm: gas detection with shutdown | Mitigation | The register lists the detector but no shutdown function | FND-0004 |

---

This pack cites 2 of 2 relevant findings.

2 of 2 top-rated relevant findings cited.

> Generated with ProbeMatrix Learnings Coach v2.0.0a5 (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
