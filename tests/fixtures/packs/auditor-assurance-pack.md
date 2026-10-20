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

### Maintenance and testing

**Test point:** Seal changes are planned with a written test step [FND-0001]
- What to sample: 15 seal-change work orders
- Evidence of conformity: A test step in each job plan
- Red flags: Job plan with no test step

**Test point:** Test equipment for leak tests is available and in date [FND-0001]
- What to sample: Test-rig calibration records
- Evidence of conformity: A current calibration certificate
- Red flags: Overdue calibration

**Test point:** Supervisors sign the return-to-service record [FND-0002]
- What to sample: 10 return-to-service records
- Evidence of conformity: A supervisor signature on each
- Red flags: Unsigned release

### Procedures

**Test point:** The procedure index covers return to service [FND-0003]
- What to sample: The current procedure index
- Evidence of conformity: An entry for return to service
- Red flags: No entry, or a draft only

**Test point:** Procedures are reviewed after equipment changes [FND-0004]
- What to sample: Procedure review log since the last equipment change
- Evidence of conformity: A review date after each change
- Red flags: No review after a change

### Materials and spares

**Test point:** Substitute parts go through change control [FND-0004]
- What to sample: 10 substitute-part requests
- Evidence of conformity: A change-control reference on each
- Red flags: Substitution with no reference

**Test point:** Stores checks the specification at issue [FND-0001; EVD-0001]
- What to sample: Issue records for critical spares
- Evidence of conformity: A specification reference at issue
- Red flags: Issue with no specification check

**Test point:** Local purchases of critical spares are reported [FND-0001; EVD-0001]
- What to sample: Monthly purchasing reports
- Evidence of conformity: Local critical-spares purchases listed
- Red flags: Local purchases missing from the report

### Alarm management

**Test point:** Gas alarms are classed by the action they need [FND-0002; EVD-0002]
- What to sample: The alarm list for the area
- Evidence of conformity: An action class for each gas alarm
- Red flags: Display-only gas alarms with no action set

**Test point:** Alarm changes are approved by the technical authority [FND-0002; EVD-0002]
- What to sample: Alarm change records
- Evidence of conformity: An approval on each change
- Red flags: Change with no approval

### Management review

**Test point:** Management review covers spares and testing indicators [FND-0003; EVD-0003]
- What to sample: Last four management review minutes
- Evidence of conformity: The indicators discussed with actions
- Red flags: Indicators not reviewed

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
