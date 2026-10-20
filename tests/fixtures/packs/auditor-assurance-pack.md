# Auditor Assurance Pack: Synthetic pump fire, 2024

**DRAFT**

Review: draft · Classification: internal · Version 1.0

Draft because: no finding is marked as edited by a person

*Learning purposes: not a statutory document · Learnings drafted by an AI agent from AI-assisted findings*

**Audience:** Internal and external auditors

**Incident:** Synthetic pump fire · 2024-03-20

## Bottom line

- Restarts and spares purchases can both be tested from existing records. [FND-0002; FND-0003]

## Why existing assurance did not catch it

The findings record no check of purchase records against specifications [FND-0003; EVD-0003].

## Audit test points

### Maintenance and testing

**Test point:** Every restart after pressure-boundary work has a leak-test record [FND-0002; EVD-0001]
- What to sample: 10 recent restarts from the CMMS
- Evidence of conformity: A signed test record on each work order
- Red flags: Work order closed with no test entry

### Materials and spares

**Test point:** Critical spares are bought to a specification [FND-0003; EVD-0003]
- What to sample: 20 critical-spares purchase orders
- Evidence of conformity: A specification reference on each order
- Red flags: Local purchase with no technical approval

## Cross-site verification protocol

| Condition | Records to pull | Interview | Walk-path stop | Cites |
|---|---|---|---|---|
| Restart without a test | Last 10 restart work orders | Maintenance supervisor | Pump bay | FND-0002 |

## Evidence request list

### Maintenance

- [ ] Return-to-service procedure and its revision history [FND-0002]

### Procurement

- [ ] Critical-spares purchase orders since March 2022 [FND-0003]

## Reporting

Grade each test point: conforming, partly, not, or not tested.

| Test point | Grade | Notes |
|---|---|---|
| Restart leak-test record |  |  |
| Spares to specification |  |  |

---

This pack cites 2 of 2 relevant findings.

2 of 2 top-rated relevant findings cited.

> Generated with ProbeMatrix Learnings Coach v2.0.0a4 (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
