# Auditor Assurance Pack: Hazira gas release and fire, 2020

**DRAFT**

Review: draft · Classification: internal · Version 1.0

Draft because: the investigation status is in progress; no finding is marked as edited by a person

*Learning purposes: not a statutory document. Derived from a ProbeMatrix investigation export; learnings are evidence-linked but should be validated by the organisation before adoption. · Learnings drafted by an AI agent from AI-assisted findings*

*About 11 min read*

**Audience:** Internal audit, HSE audit teams, certification and regulatory inspectors, insurers

**Incident:** Hazira 2020 · 2020-09-24

## Data quality and limits

- Draft learnings from an unreviewed analysis: the export's Investigation Status is in progress and no finding is marked as edited by a person.

## Bottom line

- Test returns to service first: pressure-boundary work went back into service tested only at operating pressure, with no procedure requiring more. [FND-611A8BFC; FND-904FCA63; EVD-2894] *(learning: LR-02)*
- Test spares control: a seal with a lost specification was replaced by locally bought parts as normal practice, with no function owning the specification. [FND-45363DCA; FND-A2048FB8; EVD-8645] *(learning: LR-01)*
- Test emergency isolation on paper and in the field: the plan gave no isolation criteria or delegated authority, and the valves could be closed only at the valve. [FND-2EC435D0; FND-BB4CC662; FND-DBE08E73; EVD-4052] *(learning: LR-07)*
- Test what detection does: fire and gas detection only lit an annunciator; it started no shutdown or suppression. [FND-D45021AD; FND-4D7CF773; EVD-8657] *(learning: LR-10)*
- Test hazardous-area electrical inspection fitting by fitting: a damaged flameproof fitting stayed in service under breakdown-led maintenance. [FND-554BFB4A; FND-1D61DC3A; EVD-6916] *(learning: LR-11)*
- Test the audits themselves: generic checklists recorded compliance without site data, and audit recommendations were extended without the required approval. [FND-C2CB60DC; EVD-9692; FND-1D713648; EVD-6852] *(learning: LR-20)*

## Why existing assurance did not catch it

Self-audits used a location checklist that was not specific to each plant and recorded compliance on most items, but the data behind the entries was incomplete; the internal audits gave observations without the filled checklists, so nobody could check what had been looked at. [FND-C2CB60DC; FND-2F5482CD; EVD-9692; EVD-7681] *(learning: LR-20)*

Recommendations from the external safety audit were extended without the approval the procedure requires, so overdue safety actions had no governance step that forced a decision. [FND-1D713648; FND-850B270C; EVD-6852] *(learning: LR-21)*

The records an audit would sample did not show the conditions: the malfunction notification for the meter was left open after the work and the signed calibration record did not show a setting change; the committee's report adds that electrical maintenance records listed only repaired items, not the inspection of the rest (OBS-27). [FND-AE60859C; FND-2B53492C; EVD-0591; FND-D4BB5251; EVD-2506; FND-554BFB4A; EVD-6916] *(learning: LR-04)*

Drill records held no observations or actions, so drills could not reveal readiness gaps such as the missing isolation criteria. [FND-DC0751CF; FND-B8B75D91; EVD-2130] *(learning: LR-24)*

## Audit test points

Grouped by management-system element (no framework was chosen); clauses are given where the evidence touches a requirement in the standards crosswalk.

### Maintenance and testing

**Test point:** Pressure-boundary work is proved by a test to design pressure, under a written return-to-service procedure, before the equipment goes back into service. [FND-611A8BFC; FND-904FCA63; EVD-2894]
- What to sample: The last ten returns to service after work on a flange, seal or gasket in high-pressure hydrocarbon service.
- Evidence of conformity: For each job: the procedure in force, a test record stating the test pressure against the design pressure, and the signature of the person accepting the equipment back.
- Red flags: Test recorded only as 'pressurised to operating pressure'; No return-to-service procedure for the equipment type; Test record dated after the equipment went back online

*(evidence: direct; +13 supporting; learning: LR-02)*

**Test point:** Maintenance that can cause a major release has an independent check of part, method and test before close-out. [FND-59A2F497; FND-F8C125D5; EVD-8645]
- What to sample: The same ten jobs, plus the planning record for each.
- Evidence of conformity: A named check role (by post) on the work order, a hold point for the check, and its signed result.
- Red flags: Fitter is the only signature on the job; No inspection or test-witness role exists in the maintenance plan

*(evidence: corroborated; +2 supporting; learning: LR-03)*

**Test point:** Repeat failures on the same item are counted and trigger a reliability review. [FND-71D631C1; FND-CEE3D4D7; EVD-1494]
- What to sample: Work-order history for the meters and seals on the condensate metering skid and two other high-pressure skids.
- Evidence of conformity: A repeat-failure report or bad-actor list, and review minutes that name the item and the decision taken.
- Red flags: Three or more repairs of the same kind on one item with no review; Each repair closed as routine with the same part

*(evidence: direct; +10 supporting; learning: LR-05)*

**Test point:** Explosion-protected equipment in hazardous areas is inspected item by item on schedule, and defects are recorded against each item. [FND-554BFB4A; FND-1D61DC3A; EVD-6916]
- What to sample: A walk-down of the flameproof fittings in one Zone 1 area, matched to the last two inspection records.
- Evidence of conformity: A register of fittings with unique identities, inspection records per fitting, and closed defects with dates.
- Red flags: Inspection records that list only repaired items; Scheduled inspection skipped with no recorded reason; Fittings in the field with missing bolts or open enclosures

*(evidence: direct; +7 supporting; learning: LR-11)*

**Test point:** Calibration of safety-relevant instruments follows a checklist, and every setting change is recorded on the signed calibration record. [FND-D4BB5251; FND-89D53630; EVD-2506]
- What to sample: The last two calibration records for each meter in the metering skids.
- Evidence of conformity: Checklists completed per job; as-found and as-left settings; the reason and approval for any change.
- Red flags: Settings differ between consecutive records with no recorded change; No checklist for high-pressure meter work

*(evidence: direct; learning: LR-16)*

**Test point:** Inspection results that show wall loss beyond limits lead to a corrective plan with an owner role and a decision record. [FND-47B1702F; FND-E5C4209D; EVD-5527]
- What to sample: Lines flagged with significant thickness loss in the last two inspection reports.
- Evidence of conformity: For each line: the assessment, the corrective option chosen and why, and evidence that it was done.
- Red flags: Wall loss recorded with no corrective plan; Painting recorded as the fix for metal loss

*(evidence: direct; learning: LR-17)*

**Test point:** The thickness inspection programme runs on its stated interval, with baseline data, and slippage is escalated. [FND-10FEDDD8; FND-A3DCEBD8; EVD-8307]
- What to sample: The inspection schedule against actual survey dates for the gas-terminal piping.
- Evidence of conformity: Survey dates, baseline readings per line, and escalation records for any late survey.
- Red flags: Survey interval exceeded with no escalation; No baseline thickness for lines in service

*(evidence: direct; learning: LR-18)*

**Test point:** Fire-water pumps are available as designed; trips are diagnosed and outages are limited and approved. [FND-D8BC7096; FND-694B2DA0; EVD-2432]
- What to sample: Availability and test records for every diesel and electric fire-water pump over the last quarter.
- Evidence of conformity: Run-test records, trip diagnoses with actions, and approvals for each pump out of service.
- Red flags: A pump that trips with no recorded diagnosis; More than one diesel pump out of service at a time with no approval

*(evidence: direct; learning: LR-23)*

### Change management

**Test point:** Changes of part, material or pipework, including like-for-unlike replacements, go through management of change. [FND-5A5F6AB3; FND-8083ECAC; EVD-2986]
- What to sample: Changes made in the last year (purchase records for non-original spares, modification work orders).
- Evidence of conformity: A management-of-change record for each, with a risk review and an approval.
- Red flags: No management-of-change record raised in a year with known changes; Non-original spares bought without a change record

*(evidence: direct; +1 supporting; learning: LR-06)*

**Test point:** Drawings used for maintenance and emergency response match the field and are approved. [FND-82687B50; FND-D25BF914; EVD-0933]
- What to sample: The P&IDs for the metering skids and two other high-pressure systems, checked in the field.
- Evidence of conformity: Approval status on each drawing, and a field check signed against the drawing.
- Red flags: Vendor-made drawings with no approval; Valves or instruments on the drawing that are not in the field

*(evidence: direct; learning: LR-19)*

### Materials and spares

**Test point:** Every pressure-boundary spare has a specification owned by a named function, and parts are checked against it before fitting. [FND-45363DCA; FND-A2048FB8; EVD-8645]
- What to sample: Stock and recent purchases of seals and gaskets for high-pressure service.
- Evidence of conformity: The specification for each part, the owning function, and receipt inspection or certificate records.
- Red flags: Parts bought locally with no specification; No function owns re-establishing a lost specification

*(evidence: corroborated; +21 supporting; learning: LR-01)*

### Permits

**Test point:** Hazardous work is done under a permit with a job safety plan, and missing permits are tracked. [FND-7E1F2B3F; FND-A3D2773A; EVD-5105]
- What to sample: Permits for non-routine maintenance in the last month, against the maintenance notifications for the same work.
- Evidence of conformity: Serially filed permits, attached job safety plans, and a log of missing permits with follow-up.
- Red flags: Work done against a notification with no permit; Permits missing from the file with no record of them

*(evidence: direct; learning: LR-22)*

### Competence

**Test point:** Control-room operators hold a defined qualification, including emergency practice, before being rostered. [FND-337CB67F; FND-02B682F3; EVD-5634]
- What to sample: Training and qualification records for every control-room operator on the current roster.
- Evidence of conformity: The defined qualification, each operator's record against it, and emergency practice or simulator sessions.
- Red flags: Operators rostered after general training only; No qualification defined in policy

*(evidence: direct; learning: LR-12; Clauses: ISO45001-7.2)*

### Emergency preparedness

**Test point:** The emergency plan states, for a major release, who may isolate, on what criteria, without waiting for escalation. [FND-2EC435D0; FND-BB4CC662; EVD-4052]
- What to sample: The current emergency response and disaster management plan and the shift standing orders.
- Evidence of conformity: Isolation criteria, the delegated authority by post, and evidence the night shift has been briefed on them.
- Red flags: The release scenario is named but no isolation decision is stated; Authority to isolate sits only with senior posts

*(evidence: corroborated; +12 supporting; learning: LR-07; Clauses: IN-ERDMP)*

**Test point:** Valves needed for emergency isolation can be operated from a place that stays reachable during a release. [FND-DBE08E73; FND-7D28BE30; EVD-3932]
- What to sample: The isolation valves for each high-pressure inventory in the gas terminal.
- Evidence of conformity: For each valve: the operating location, remote operation where provided, and a function test record.
- Red flags: Isolation valves operable only at the valve; No function test of remote operation

*(evidence: corroborated; +5 supporting; learning: LR-09)*

**Test point:** Fire and gas detection starts a defined protective action, not only an alarm. [FND-D45021AD; FND-4D7CF773; EVD-8657]
- What to sample: The fire and gas cause-and-effect chart for the gas terminal and the last function test.
- Evidence of conformity: The defined action for each confirmed detection, and test records showing the action works.
- Red flags: Detectors wired to an annunciator only; No detector history in the control system

*(evidence: corroborated; +8 supporting; learning: LR-10)*

**Test point:** Drills are recorded with observations and actions, and the actions are tracked to closure. [FND-DC0751CF; FND-B8B75D91; EVD-2130]
- What to sample: Drill records for the last year.
- Evidence of conformity: Observations, actions with an owner role, and closure records for each drill.
- Red flags: Drill records with no observations or actions; Drill data kept outside the approved system

*(evidence: direct; learning: LR-24; Clauses: IN-ERDMP)*

### Records

**Test point:** Maintenance notifications are closed with a record of the work and a close-out review before or at return to service. [FND-AE60859C; FND-2B53492C; EVD-0591]
- What to sample: Notifications for work on high-pressure equipment closed or still open in the last quarter.
- Evidence of conformity: Close-out entries naming the work done and parts used, and the reviewer's sign-off.
- Red flags: Notifications left open after the equipment returned to service; Closures with no record of the work done

*(evidence: direct; learning: LR-04; Clauses: ISO45001-10.2)*

### Audit follow-up

**Test point:** Self-audits and internal audits use plant-specific checklists, and the completed checklists are kept with the evidence behind each compliance entry. [FND-C2CB60DC; FND-2F5482CD; EVD-9692]
- What to sample: The last self-audit and the last internal audit of the gas terminal.
- Evidence of conformity: Plant-specific checklists, completed and signed, with the data or observation behind each compliance entry.
- Red flags: Generic checklists; Compliance recorded without site data; Completed checklists not kept

*(evidence: direct; learning: LR-20; Clauses: ISO45001-9.2)*

**Test point:** Extensions of due dates on audit recommendations are approved as the procedure requires, and each finding has a documented response. [FND-1D713648; FND-850B270C; EVD-6852]
- What to sample: All open recommendations from the last external safety audit.
- Evidence of conformity: For each extension: the approval by the post the procedure names, and the documented response to the finding.
- Red flags: Due dates extended with no approval document; Overdue actions with no owning function

*(evidence: direct; learning: LR-21; Clauses: ISO45001-10.2, PSM-(o)(4))*

## Cross-site verification protocol

| Condition | Records to pull | Interview | Walk-path stop | Cites |
|---|---|---|---|---|
| Pressure-boundary spares fitted without a specification (LR-01) | Purchase records for seals and gaskets; specifications on file; receipt inspection records | Maintenance planner and stores supervisor: how a part is chosen when the original is not available | Stores bins for high-pressure seals; one recently repaired flange | FND-45363DCA; FND-A2048FB8; EVD-8645 (+21 supporting) |
| Return to service without a test to design pressure (LR-02) | Return-to-service records and test certificates for recent pressure-boundary work | Maintenance supervisor and shift operator who accepts equipment back: what test is normal and why | A recently repaired high-pressure joint and its test record | FND-611A8BFC; FND-904FCA63; EVD-2894 (+13 supporting) |
| No isolation criteria or delegated authority in the emergency plan (LR-07) | The emergency plan, shift standing orders and the last drill record | Shift in-charge and control-room operator: who may isolate a major supply at night, and on what signal | The control room and the nearest isolation valve for a major inventory | FND-2EC435D0; FND-BB4CC662; EVD-4052 (+12 supporting) |
| Fire and gas detection that alarms but does not act (LR-10) | Cause-and-effect charts and the last detector function test | Control-room operator and instrument engineer: what happens after a detector alarms | The annunciator or control-system alarm display | FND-D45021AD; FND-4D7CF773; EVD-8657 (+8 supporting) |
| Hazardous-area electrical defects left in service (LR-11) | Flameproof equipment register and the last two inspection records | Electrical maintenance supervisor: how a fitting is picked for inspection and how defects are recorded | Lighting and junction boxes in one Zone 1 area | FND-554BFB4A; FND-1D61DC3A; EVD-6916 (+7 supporting) |

## Evidence request list

### Mechanical maintenance

- [ ] Return-to-service records and pressure-test certificates for pressure-boundary work in high-pressure hydrocarbon service. [FND-611A8BFC; EVD-2894] *(learning: LR-02)*
- [ ] Work-order history and any repeat-failure report for the metering skids. [FND-71D631C1; EVD-1494] *(learning: LR-05)*

### Stores and procurement

- [ ] Specifications, purchase records and receipt inspection records for seals and gaskets. [FND-45363DCA; EVD-8645] *(learning: LR-01)*

### Engineering and documents

- [ ] Management-of-change register, and approval status of the P&IDs for the metering skids. [FND-5A5F6AB3; EVD-2986] *(learning: LR-06)*

### Instrumentation and control

- [ ] Calibration records and checklists for the metering-skid meters; fire and gas cause-and-effect charts and function tests. [FND-D4BB5251; EVD-2506] *(learning: LR-16)*

### Electrical maintenance

- [ ] Flameproof equipment register and inspection records for the Zone 1 areas. [FND-554BFB4A; EVD-6916] *(learning: LR-11)*

### Asset integrity

- [ ] Thickness survey reports, baseline data and corrective plans for gas-terminal piping. [FND-47B1702F; EVD-5527] *(learning: LR-17)*

### Operations and emergency planning

- [ ] Emergency response and disaster management plan, shift standing orders, drill records and control-room qualification records. [FND-2EC435D0; EVD-4052] *(learning: LR-07)*

### Work management

- [ ] Open and closed maintenance notifications with close-out entries, and the permit file with job safety plans. [FND-AE60859C; EVD-0591] *(learning: LR-04)*

### HSE and audit

- [ ] Self-audit and internal audit checklists, and the external audit action tracker with extension approvals. [FND-C2CB60DC; EVD-9692] *(learning: LR-20)*

## Reporting

Grade each test point on this scale: conforming; major nonconformity (NC); minor nonconformity; opportunity for improvement (OFI); not tested. Record the sample actually taken. Response to finding is for the audited organisation's documented response to each finding; leave it blank for them.

| Test point | Clause | Grade | Response to finding | Notes |
|---|---|---|---|---|
| tp-01 Return-to-service test | Maintenance and testing |  |  |  |
| tp-02 Independent check of critical repairs | Maintenance and testing |  |  |  |
| tp-03 Repeat-failure review | Maintenance and testing |  |  |  |
| tp-04 Hazardous-area electrical inspection | Maintenance and testing |  |  |  |
| tp-05 Calibration records | Maintenance and testing |  |  |  |
| tp-06 Corrective plans for wall loss | Maintenance and testing |  |  |  |
| tp-07 Thickness inspection interval | Maintenance and testing |  |  |  |
| tp-08 Fire-water pump availability | Maintenance and testing |  |  |  |
| tp-09 Management of change | Change management |  |  |  |
| tp-10 Drawings match the field | Change management |  |  |  |
| tp-11 Spares specification | Materials and spares |  |  |  |
| tp-12 Permits and job safety plans | Permits |  |  |  |
| tp-13 Control-room qualification | ISO45001-7.2 |  |  |  |
| tp-14 Isolation criteria and authority | IN-ERDMP |  |  |  |
| tp-15 Isolation from a safe place | Emergency preparedness |  |  |  |
| tp-16 Detection starts protective action | Emergency preparedness |  |  |  |
| tp-17 Drill records | IN-ERDMP |  |  |  |
| tp-18 Notification close-out | ISO45001-10.2 |  |  |  |
| tp-19 Audit checklists | ISO45001-9.2 |  |  |  |
| tp-20 Approval of extensions | ISO45001-10.2, PSM-(o)(4) |  |  |  |

## Limits of this pack

- The test points come from one event at one site, analysed from the enquiry committee's report; they test whether these conditions exist, not the whole management system.
- No barrier or critical-control register was supplied, so the critical-control verification section is left out.
- Clause ids are given only where the crosswalk holds a matching requirement; most test points are grouped by element instead.

## Supporting citations

- Audit test points › 1: FND-C34A026C; FND-257C1100; FND-137BC719; FND-8ACDE078; FND-5919B328; FND-C4E06264; FND-3AB996FC; FND-86CB3683; FND-491EDE74; FND-50C7319E; FND-B91D4A23; FND-7A10FF70; FND-71EE9734
- Audit test points › 2: FND-615DB819; FND-63B6D260
- Audit test points › 3: FND-D14B8424; FND-110F964C; FND-4EDE038A; FND-AC9A1E69; FND-FEC84761; FND-82FC718D; FND-3A34BAD3; FND-E0AE86A6; FND-1A251687; FND-55F68376
- Audit test points › 4: FND-ADC25F29; FND-0B35D995; FND-5E08D0F8; FND-675D99DD; FND-1280E788; FND-ABF11182; FND-CCE6F868
- Audit test points › 9: FND-F7FE8463
- Audit test points › 11: FND-FFE174D0; FND-A443D288; FND-72A7D26C; FND-CEE4B00B; FND-3746C7B6; FND-42BEF461; FND-D66ACA7B; FND-852B7EC7; FND-DEAA7F90; FND-A3D7D53F; FND-B86F67F0; FND-D40839C1; FND-BC4FD086; FND-23139BF9; FND-EBB66554; FND-B440C1BF; FND-8CE00707; FND-6B3A6492; FND-A0017E28; FND-B56701CA; FND-DE30BD8B
- Audit test points › 14: FND-D4A3EF8A; FND-4F687CC5; FND-D1DF4895; FND-7A2429CE; FND-33D32D4C; FND-DF1144C3; FND-82761CC5; FND-730D0DCA; FND-6472CD15; FND-E009D26B; FND-5C7B163D; FND-446A7956
- Audit test points › 15: FND-05841EDA; FND-322112EE; FND-044D1DEC; FND-02310148; FND-6DB250E6
- Audit test points › 16: FND-119E6CF7; FND-5BC96E8A; FND-2D90823E; FND-01C3DE98; FND-6155A1C2; FND-4458E0C0; FND-5897D1E4; FND-15B4E60F
- Cross-site verification protocol › 1, row 1: FND-FFE174D0; FND-A443D288; FND-72A7D26C; FND-CEE4B00B; FND-3746C7B6; FND-42BEF461; FND-D66ACA7B; FND-852B7EC7; FND-DEAA7F90; FND-A3D7D53F; FND-B86F67F0; FND-D40839C1; FND-BC4FD086; FND-23139BF9; FND-EBB66554; FND-B440C1BF; FND-8CE00707; FND-6B3A6492; FND-A0017E28; FND-B56701CA; FND-DE30BD8B
- Cross-site verification protocol › 1, row 2: FND-C34A026C; FND-257C1100; FND-137BC719; FND-8ACDE078; FND-5919B328; FND-C4E06264; FND-3AB996FC; FND-86CB3683; FND-491EDE74; FND-50C7319E; FND-B91D4A23; FND-7A10FF70; FND-71EE9734
- Cross-site verification protocol › 1, row 3: FND-D4A3EF8A; FND-4F687CC5; FND-D1DF4895; FND-7A2429CE; FND-33D32D4C; FND-DF1144C3; FND-82761CC5; FND-730D0DCA; FND-6472CD15; FND-E009D26B; FND-5C7B163D; FND-446A7956
- Cross-site verification protocol › 1, row 4: FND-119E6CF7; FND-5BC96E8A; FND-2D90823E; FND-01C3DE98; FND-6155A1C2; FND-4458E0C0; FND-5897D1E4; FND-15B4E60F
- Cross-site verification protocol › 1, row 5: FND-ADC25F29; FND-0B35D995; FND-5E08D0F8; FND-675D99DD; FND-1280E788; FND-ABF11182; FND-CCE6F868

---

This pack cites 98 of 101 relevant findings.

98 of 101 top-rated relevant findings cited.

> Generated with ProbeMatrix Learnings Coach v2.0.0a5 (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
