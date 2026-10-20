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
- Clause: Site element 4.2 Return to service
- What to sample: The last 10 restarts after pressure-boundary work, from the CMMS
- Evidence of conformity: A signed test record on each work order
- Red flags: Work order closed with no test entry

*(learning: LR-01)*

### Materials and spares

**Test point:** Critical spares are bought to a specification [FND-0003; EVD-0003]
- Clause: ISO 45001 9.2
- What to sample: 20 critical-spares purchase orders
- Evidence of conformity: A specification reference on each order
- Red flags: Local purchase with no technical approval

*(Clauses: ISO45001-9.2)*

## Cross-site verification protocol

| Condition | Records to pull | Interview | Walk-path stop | Cites |
|---|---|---|---|---|
| Restart without a test | Last 10 restart work orders | Maintenance supervisor | Pump bay | FND-0002 |

## Critical-control verification

| Critical control | Barrier register id | Performance requirement | Verification activity | Verifier role | Cites |
|---|---|---|---|---|---|
| Leak test before return to service | unmapped | Every restart has a signed test record | Monthly sample of restart work orders | Area maintenance lead | FND-0002 |

*(Clauses: ICMM-CCM-8)*

## Evidence request list

### Maintenance

- [ ] Return-to-service procedure and its revision history [FND-0002]

### Procurement

- [ ] Critical-spares purchase orders since March 2022 [FND-0003]

## Reporting

Grade each test point: conforming, major nonconformity (NC), minor nonconformity, opportunity for improvement (OFI), or not tested.

| Test point | Clause | Grade | Response to finding | Notes |
|---|---|---|---|---|
| Restart leak-test record | Site element 4.2 |  |  |  |
| Spares to specification | ISO 45001 9.2 |  |  |  |

## Limits of this pack

- One critical control has no entry in the organisation's barrier register (unmapped).

---

This pack cites 2 of 2 relevant findings.

2 of 2 top-rated relevant findings cited.

> Generated with ProbeMatrix Learnings Coach v2.0.0a5 (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
