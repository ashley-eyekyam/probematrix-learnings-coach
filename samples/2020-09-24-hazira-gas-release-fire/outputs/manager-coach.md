# Manager Coach: Hazira gas terminal release and fire, 2020

**DRAFT**

Review: draft · Classification: internal · Version 1.0

Draft because: the investigation status is in progress; no finding is marked as edited by a person

*Learning purposes: not a statutory document. Draft learnings from a ProbeMatrix investigation export; validate them before adoption. · Learnings drafted by an AI agent from AI-assisted findings*

*About 16 min read*

**Audience:** T3 function and department managers

**Incident:** Hazira 2020 · 2020-09-24

## Data quality and limits

- Draft learnings from an unreviewed analysis: the export's Investigation Status is in_progress and no finding is marked as edited by a person, so this pack stays a draft until the investigation is completed and reviewed.

## Bottom line

- Several controls existed only on paper: a change procedure not used since 2018, an emergency plan without isolation criteria, and audits that recorded compliance without data. [FND-8083ECAC; FND-314D34C5; FND-303495E9; EVD-2986; EVD-4052; EVD-9692] *(learning: LR-06)*
- No function owned the specification for a legacy pressure seal, so a substitute part became regular practice. [FND-A2048FB8; EVD-8645] *(learning: LR-01)*
- No procedure required a design-pressure test before pressure-boundary work went back into service. [FND-257C1100; EVD-2894] *(learning: LR-02)*
- Records held the warnings (repeat seal changes, wall loss, an open notification), but no system turned them into a decision. [FND-71D631C1; FND-47B1702F; FND-56C66B96; EVD-1494; EVD-5527; EVD-0591] *(learning: LR-05)*
- Emergency isolation depended on reaching hand-operated valves inside the release area. [FND-4C645CB5; EVD-3932] *(learning: LR-09)*

## Operations & Control Room

### What your system allowed

**Learning:** Emergency isolation depended on reaching valves that could only be closed by hand inside the release area. [FND-4C645CB5; FND-31405D96; EVD-3932; EVD-9612]

The gas terminal isolation valves had no remote operation from the control room. When the vapour cloud denied access, the first isolation came only after a senior role reached the gate and the valve could be closed by hand. The operating system assumed access would be possible.

- Owner: Operations function

*(evidence: corroborated; +8 supporting; learning: LR-09)*

**Learning:** Once the cloud blocked access, the shift response stayed on locating the leak rather than switching to upstream isolation. [FND-36179046; FND-305216AF; FND-BDD73BA2; EVD-9612; EVD-1460; EVD-9220]

Nothing in the plan or at the console told the shift when to stop searching and isolate from a distance. Each report went up the chain while people tried to approach the source on foot in very poor visibility.

- Owner: Operations function

*(evidence: corroborated; +5 supporting; learning: LR-08)*

**Learning:** Control-room staff held emergency duties without a defined qualification. [FND-337CB67F; FND-02B682F3; EVD-5634]

New and transferred staff received a four-day general course and then on-the-job training; no qualification was defined in the HR or operations policy and there was no simulator practice. The rostering system had nothing to check against.

- Owner: Operations function

*(evidence: direct; +8 supporting; learning: LR-12)*

### Interfaces you share

With Mechanical Maintenance (the largest interface, 71 shared findings): agree that operations accepts a pressure-boundary job back into service only against a signed test record; the meter went back online after an operating-pressure soak [FND-FD617187; FND-611A8BFC; EVD-2894; EVD-0185].

With Emergency Planning & Command: agree the isolation criteria, the valve list and the shift roles that may isolate without calling up the chain, and drill them together [FND-314D34C5; FND-AE629313; EVD-4052; EVD-3932].

### Recommendations

**Recommendation:** Convert the gas terminal emergency isolation valves to remotely operated valves, operable from the control room and a safe secondary location. [FND-4C645CB5; FND-DE978BF5; EVD-3932]
- Control tier: engineering
- Barrier: mitigation: emergency isolation
- Owner: Engineering function
- Leading indicator: Share of identified emergency isolation points with remote operation; proof-test pass rate.

*(learning: LR-09)*

**Recommendation:** Provide control-room isolation matrices for major releases, showing which valves isolate each section and where each can be operated from. [FND-36179046; FND-20217957; EVD-6414]
- Control tier: administrative
- Barrier: mitigation: emergency isolation decision
- Owner: Operations function
- Leading indicator: Isolation matrices in place for every hydrocarbon area and used in drills.
- Why not stronger: The decision aid is the system fix for the switch from locating to isolating; the engineering fix (remote isolation) is the recommendation above, and the matrix is needed to use it.

*(learning: LR-08)*

*Language check JC6 accepted: the administrative change is itself the system fix here, as why\_not\_stronger explains*

**Recommendation:** Define a control-room operator qualification with simulator-based emergency scenarios and a pass standard, and make it a rostering prerequisite. [FND-337CB67F; EVD-5634]
- Control tier: administrative
- Barrier: mitigation: emergency response competence
- Owner: Operations function
- Leading indicator: Share of control-room positions on each shift filled by qualified staff.
- Why not stronger: Competence is the condition here; the rostering prerequisite turns training into a check the system enforces, and the engineering isolation fixes are recommended separately.

*(learning: LR-12)*

*Language check JC6 accepted: the administrative change is itself the system fix here, as why\_not\_stronger explains*

### Leading indicators

**Indicator:** Time to isolation in drills [FND-4C645CB5; FND-36179046; EVD-6414]
- Measure: Time from a confirmed release to first isolation in each drill; baseline from the next two drills
- Deterioration looks like: Any drill where isolation waits for someone to reach a valve in the release area
- Owner: Operations function

*(learning: LR-09)*

**Indicator:** Qualified control-room cover [FND-337CB67F; EVD-5634]
- Measure: Share of shifts with every control-room position filled by a qualified person, from the roster and training records
- Deterioration looks like: Any shift rostered without a qualified person in the control room
- Owner: Operations function

*(learning: LR-12)*

### 90-day agenda

| Days | Action | Cites |
|---|---|---|
| 1-30 | Confirm which isolation valves are local-only and which control-room staff hold no defined qualification; brief each shift on isolating from a distance | FND-4C645CB5; FND-337CB67F |
| 31-60 | Draft the isolation matrices and the qualification with control-room operators and shift in-charges | FND-36179046; FND-02B682F3 |
| 61-90 | Report time to isolation in drills and qualified cover in the monthly operations report | FND-305216AF |

## Mechanical Maintenance

### What your system allowed

**Learning:** A pressure-boundary seal was replaced with an unspecified local part because no one held the specification. [FND-91B45FF9; FND-A2048FB8; EVD-8645]

The 1986 meter's original gasket specification was not on file, so locally bought O-rings were fitted as regular practice, with no specification or quality check at purchase and no recorded decision to switch. The job had to be done, and the export shows nothing in the system that said stop.

- Owner: Maintenance function

*(evidence: corroborated; +8 supporting; learning: LR-01)*

**Learning:** Pressure-boundary work went back into service without a test to design pressure, because no procedure required one. [FND-FD617187; FND-257C1100; EVD-2894; EVD-0185]

After the gasket change on 18 September 2020 the system was pressurised to operating pressure only, and the meter was taken online the next day. No procedure set a test type, pressure or witness for these high-pressure meters.

- Owner: Maintenance function

*(evidence: direct; +6 supporting; learning: LR-02)*

**Learning:** Repeat failures of the same seal were treated as routine repairs, not as a reliability warning. [FND-71D631C1; FND-CEE3D4D7; EVD-1494]

The gasket was changed in November 2018, February 2019 and September 2020. Each job closed as a repair; no repeat-failure review existed to open a root-cause investigation.

- Owner: Maintenance function

*(evidence: direct; +8 supporting; learning: LR-05)*

**Learning:** A high-consequence repair depended on one person's judgement, with no independent check of part, method or test. [FND-F8C125D5; FND-63B6D260; EVD-5105]

The gasket job was planned with no inspection, test-witness or close-out role and without a job safety analysis, so the substitute part and the missing test reached service unchecked.

- Owner: Maintenance function

*(evidence: corroborated; +2 supporting; learning: LR-03)*

### Interfaces you share

With Work Management & Planning: agree that pressure-boundary jobs are planned as safety-critical, with test and witness steps written into the job plan [FND-F8C125D5; EVD-5105].

With Engineering, Design, Documents & MOC: agree who re-establishes a lost specification and who approves a substitute part, and that a substitute triggers a change review [FND-A2048FB8; FND-5A5F6AB3; EVD-8645; EVD-2986].

### Recommendations

**Recommendation:** Configure the work-order system so a pressure-boundary job cannot be closed, or the equipment released to operations, until a test result is entered. [FND-FD617187; FND-611A8BFC; EVD-2894]
- Control tier: engineering
- Barrier: prevention: return-to-service test
- Owner: Maintenance function
- Leading indicator: Attempted closures blocked for missing test data, trending to zero.

*(learning: LR-02)*

**Recommendation:** Set an automatic repeat-failure trigger in the maintenance system that opens a root-cause investigation task for a repeat corrective job on the same item. [FND-71D631C1; FND-CEE3D4D7; EVD-1494]
- Control tier: engineering
- Barrier: prevention: reliability review
- Owner: Maintenance function
- Leading indicator: Bad actors flagged per quarter and the share with a completed root-cause analysis.

*(learning: LR-05)*

**Recommendation:** Re-establish the seal design for the meter flange (OEM data or an engineered equivalent), stock only certified parts against it and quarantine non-conforming seals. [FND-91B45FF9; FND-54180594; EVD-8645]
- Control tier: substitution
- Barrier: prevention: pressure-boundary integrity
- Owner: Maintenance function
- Leading indicator: Share of critical pressure-boundary spares with a specification and certificate on file.

*(learning: LR-01)*

### Leading indicators

**Indicator:** Pressure-boundary jobs with a test record [FND-FD617187; EVD-2894]
- Measure: Share of pressure-boundary work orders closed with a recorded test result and witness; baseline from a sample of current work orders
- Deterioration looks like: Any pressure-boundary job closed without a test result
- Owner: Maintenance function

*(learning: LR-02)*

**Indicator:** Repeat failures reviewed [FND-71D631C1; EVD-1494]
- Measure: Share of repeat corrective jobs on the same item that opened a root-cause review
- Deterioration looks like: A repeat failure closed as a routine repair
- Owner: Maintenance function

*(learning: LR-05)*

### 90-day agenda

| Days | Action | Cites |
|---|---|---|
| 1-30 | List pressure-boundary items with no specification on file and every repeat-failure item; hold any substitute seal for engineering approval | FND-91B45FF9; FND-71D631C1 |
| 31-60 | Draft the return-to-service procedure and the work-order block with the fitters and supervisors who do the work | FND-257C1100 |
| 61-90 | Report test-record share and repeat failures reviewed in the monthly maintenance report | FND-FD617187; FND-CEE3D4D7 |

## Engineering, Design, Documents & MOC

### What your system allowed

**Learning:** The management-of-change procedure existed on paper but had not been used since 2018. [FND-5A5F6AB3; FND-8083ECAC; EVD-2986]

The procedure was published in August 2016, yet no change went through it after 2018, including the switch from the original gasket to a local O-ring. The export shows no prompt in the work or stores systems that treats a like-for-unlike part as a change.

- Owner: Engineering function

*(evidence: direct; +8 supporting; learning: LR-06)*

**Learning:** The metering P&ID was a lost original replaced by an unapproved vendor drawing that did not match the field. [FND-D25BF914; FND-583EB5FE; EVD-0933]

Old drawings were lost and a vendor drew new ones, which were never approved and did not match the valves and meters on site. Maintainers had no verified reference for the gasket job.

- Owner: Engineering function

*(evidence: direct; +4 supporting; learning: LR-19)*

### Interfaces you share

With Mechanical Maintenance and Materials Management: agree that a non-catalogue or substitute part cannot be issued without a change reference, and who in engineering approves it [FND-5A5F6AB3; FND-8083ECAC; EVD-2986; EVD-8645].

With Operations & Control Room: agree which safety-critical drawings operations relies on in an emergency, so those are field-verified first [FND-583EB5FE; EVD-0933].

### Recommendations

**Recommendation:** Build a change trigger into the work-order and stores issue screens, so a non-catalogue or substitute part needs a management-of-change reference. [FND-5A5F6AB3; FND-8083ECAC; EVD-2986]
- Control tier: engineering
- Barrier: prevention: change control
- Owner: Engineering function
- Leading indicator: MOC records raised per month, and the share of substitute-part issues with an MOC reference.

*(learning: LR-06)*

**Recommendation:** Field-verify and re-issue controlled P&IDs for the gas terminal, starting with metering and emergency isolation systems. [FND-D25BF914; EVD-0933]
- Control tier: administrative
- Barrier: prevention: accurate technical information
- Owner: Engineering function
- Leading indicator: Share of safety-critical P&IDs field-verified.
- Why not stronger: Drawing control is itself the system fix for lost and unapproved drawings; no engineering control replaces a verified drawing.

*(learning: LR-19)*

*Language check JC6 accepted: the administrative change is itself the system fix here, as why\_not\_stronger explains*

### Leading indicators

**Indicator:** Change control in use [FND-8083ECAC; EVD-2986]
- Measure: MOC records opened and closed per month; baseline from the records since 2018
- Deterioration looks like: A month with no MOC records while field changes are made
- Owner: Engineering function

*(learning: LR-06)*

**Indicator:** Verified safety-critical drawings [FND-583EB5FE; EVD-0933]
- Measure: Share of safety-critical P&IDs field-verified and approved
- Deterioration looks like: Any vendor drawing in use without approval
- Owner: Engineering function

*(learning: LR-19)*

### 90-day agenda

| Days | Action | Cites |
|---|---|---|
| 1-30 | Confirm which changes since 2018 had no MOC record and which safety-critical drawings are unapproved | FND-8083ECAC; FND-D25BF914 |
| 31-60 | Draft the change trigger and the 'replacement not in kind' examples with maintenance, stores and operations | FND-5A5F6AB3 |
| 61-90 | Report MOC activity and drawings verified in the monthly engineering report | FND-583EB5FE |

## Asset Integrity, Corrosion & Inspection

### What your system allowed

**Learning:** Known pipe-wall loss was measured but not acted on: no corrective plan for three years, and painting used as the fix. [FND-47B1702F; FND-6D307E93; FND-5EC15274; EVD-5527; EVD-2397]

The 2017 thickness survey found pipes needing corrective action, and three years later there was no plan. A July 2019 spot check found 1.03 mm of wall loss with heavy pitting on the 36-inch line, and painting was the corrective action. Measuring was in place; deciding was not.

- Owner: Asset integrity function

*(evidence: direct; +8 supporting; learning: LR-17)*

**Learning:** The four-year thickness inspection cycle slipped to six years, and baseline data and pipe schedules were missing. [FND-5ABEE30B; FND-2F99FB62; EVD-8307; EVD-8287]

The last two surveys were in 2011 and 2017, and for many gas terminal pipes the baseline thickness and original drawings were not available. The schedule had no escalation when it slipped.

- Owner: Asset integrity function

*(evidence: direct; +8 supporting; learning: LR-18)*

### Interfaces you share

With Mechanical Maintenance: agree that every wall-loss finding gets a repair, re-rate or replace decision before any painting closes it [FND-47B1702F; FND-5EC15274; EVD-2397].

With Operations & Control Room: agree how overdue integrity actions on lines in service are reported to the shift and to site leadership [FND-6D307E93; EVD-5527].

### Recommendations

**Recommendation:** Carry out fitness-for-service assessments on the 2017 and 2019 wall-loss locations, then repair, re-rate or replace as required. [FND-47B1702F; FND-6D307E93; FND-5EC15274; EVD-5527; EVD-2397]
- Control tier: engineering
- Barrier: prevention: pipeline integrity
- Owner: Asset integrity function
- Leading indicator: Open wall-loss findings without a fitness-for-service decision, trending to zero.

*(learning: LR-17)*

**Recommendation:** Schedule thickness inspections in the maintenance system with automatic escalation when overdue, and use the 2011 data as the baseline where originals are lost. [FND-5ABEE30B; EVD-8307]
- Control tier: administrative
- Barrier: prevention: inspection scheduling
- Owner: Asset integrity function
- Leading indicator: Inspections done on time against the plan.
- Why not stronger: Scheduling with automatic escalation is the system fix for a slipped inspection cycle; the engineering fix for the measured wall loss is the fitness-for-service recommendation above.

*(learning: LR-18)*

*Language check JC6 accepted: the administrative change is itself the system fix here, as why\_not\_stronger explains*

### Leading indicators

**Indicator:** Wall-loss findings without a decision [FND-47B1702F; EVD-5527]
- Measure: Count and age of wall-loss findings with no fitness-for-service decision; baseline from the 2017 and 2019 findings
- Deterioration looks like: Any finding older than one inspection cycle without a decision
- Owner: Asset integrity function

*(learning: LR-17)*

**Indicator:** Inspections on time [FND-5ABEE30B; EVD-8307]
- Measure: Share of scheduled thickness inspections done in their interval
- Deterioration looks like: Any overdue inspection not escalated
- Owner: Asset integrity function

*(learning: LR-18)*

### 90-day agenda

| Days | Action | Cites |
|---|---|---|
| 1-30 | List every open wall-loss finding and every overdue inspection; confirm the 36-inch segment's condition | FND-47B1702F; FND-5ABEE30B |
| 31-60 | Draft the integrity action register and the escalation rule with the inspectors and maintenance planners | FND-6D307E93 |
| 61-90 | Report overdue integrity actions and inspection compliance in the monthly report to site leadership | FND-2F99FB62 |

## HSE, Process Safety & Audit

### What your system allowed

**Learning:** Safety audits used generic checklists and recorded compliance without site data, so they could not find plant-specific defects. [FND-303495E9; FND-48967DB2; EVD-9692; EVD-7681]

The self-safety audit checklist was not related to the specific plant and recorded compliance where the data was later found incomplete; internal audits kept no filled checklists. The audit method could not have found the seal, test or isolation gaps.

- Owner: HSE and process safety function

*(evidence: direct; +8 supporting; learning: LR-20)*

**Learning:** Maintenance notifications were treated as work permits, permits went missing untracked, and job safety plans were absent. [FND-7E1F2B3F; FND-A3D2773A; EVD-5105]

Some work permits were missing with no tracking, and job safety plans were not attached in the work system, so hazardous maintenance went ahead without a documented hazard analysis.

- Owner: HSE and process safety function

*(evidence: direct; +5 supporting; learning: LR-22)*

**Learning:** Fire drill records held no actions or observations, so drills could not show whether readiness was improving. [FND-B8B75D91; FND-BFABC63C; EVD-2130]

Drill reports in the work system held dates only, and a separate record was not in line with the approved guidelines.

- Owner: HSE and process safety function

*(evidence: direct; +5 supporting; learning: LR-24)*

### Interfaces you share

With Mechanical Maintenance: agree that work opening a hydrocarbon pressure boundary needs its own permit and job safety analysis, separate from the maintenance notification [FND-7E1F2B3F; EVD-5105].

With Emergency Planning & Command: agree one drill record with timings for detection, notification and isolation, so drills test the isolation decision [FND-B8B75D91; EVD-2130].

### Recommendations

**Recommendation:** Make the electronic permit mandatory for hydrocarbon work with an attached job safety analysis, and reconcile issued against closed permits daily. [FND-7E1F2B3F; FND-A3D2773A; EVD-5105]
- Control tier: engineering
- Barrier: prevention: permit to work
- Owner: HSE and process safety function
- Leading indicator: Unreconciled permits per week, trending to zero; share of permits with a job safety analysis attached.

*(learning: LR-22)*

**Recommendation:** Replace generic checklists with site-specific, barrier-based audit protocols that need evidence (a photo, record or reading) for each compliance claim. [FND-303495E9; EVD-9692]
- Control tier: administrative
- Barrier: assurance: audit
- Owner: HSE and process safety function
- Leading indicator: Share of audit items with recorded evidence; plant-specific defects found per audit.
- Why not stronger: The audit method is the condition; an evidence requirement is the system fix for audit quality, and no engineering control audits a plant.

*(learning: LR-20)*

*Language check JC6 accepted: the administrative change is itself the system fix here, as why\_not\_stronger explains*

### Leading indicators

**Indicator:** Audit claims with evidence [FND-303495E9; EVD-9692]
- Measure: Share of audit compliance claims with recorded evidence; baseline from the last self-safety audit
- Deterioration looks like: Any audit recording compliance without evidence
- Owner: HSE and process safety function

*(learning: LR-20)*

**Indicator:** Permits reconciled [FND-A3D2773A; EVD-5105]
- Measure: Issued permits not matched to a closed permit at the end of each week
- Deterioration looks like: Any missing permit not investigated
- Owner: HSE and process safety function

*(learning: LR-22)*

### 90-day agenda

| Days | Action | Cites |
|---|---|---|
| 1-30 | Re-test a sample of last year's 'compliant' audit items and reconcile current permits | FND-303495E9; FND-A3D2773A |
| 31-60 | Draft the plant-specific audit protocol and the permit reconciliation with the auditors and permit issuers | FND-48967DB2 |
| 61-90 | Report audit evidence share and permit reconciliation in the monthly HSE report | FND-7E1F2B3F |

## Work management: planners and schedulers

**Learning:** The malfunction notification was never closed or reviewed, so the last administrative check before return to service did not happen. [FND-50775B5A; FND-56C66B96; EVD-0591]

A notification for the meter was raised on 17 September 2020 and was not closed after the gasket job; no one was assigned to review the closure.

- Owner: Work management function

*(evidence: direct; learning: LR-04)*

**Learning:** Pressure-boundary work was planned like any other repair, without inspection, witness or job safety steps. [FND-F8C125D5; FND-63B6D260; EVD-5105]

The gasket job plan had no independent check, test witness or job safety analysis, so the planning system did not put a verification step between the fitter and the restart.

- Owner: Work management function

*(evidence: corroborated; learning: LR-03)*

**Learning:** Repeat failures were planned as routine repairs: the same seal was replaced three times in 22 months, and each time the planning system scheduled another like-for-like job with no trigger for a reliability review. [FND-8B4A5414; FND-F0D015E1; EVD-1494]

No rule in the work-management system escalated a second or third corrective job on the same tag to root-cause analysis, OEM seal restoration or meter replacement, so the inadequate repair was planned again until the fourth failure.

- Owner: Work management function

*(learning: LR-05)*

**Learning:** Planned inspection slipped without a deferral decision: the four-year thickness survey ran in 2011 and 2017 only, and the next one was already overdue by 2020. [FND-FCCB9505; EVD-8307]

The schedule let a mandated inspection move by years with no recorded deferral, approval or risk assessment, so the slip was invisible to the people who could have resourced it.

- Owner: Work management function

*(learning: LR-18)*

**Recommendation:** Link equipment status to notification status in the maintenance system, so equipment cannot be set available while its corrective notification is open. [FND-50775B5A; FND-56C66B96; EVD-0591]
- Control tier: engineering
- Barrier: prevention: work close-out
- Owner: Work management function
- Leading indicator: In-service equipment with an open corrective notification, by age.

*(learning: LR-04)*

**Recommendation:** Introduce a safety-critical maintenance category in work planning that adds inspection, test-witness and close-out review steps automatically. [FND-F8C125D5; FND-63B6D260]
- Control tier: engineering
- Barrier: prevention: independent verification
- Owner: Work management function
- Leading indicator: Share of safety-critical jobs with every verification step signed by someone other than the performer.

*(learning: LR-03)*

**Recommendation:** Add a repeat-failure trigger to the maintenance system: a second corrective job on the same tag within an interval the owning function sets opens a reliability review that must be closed before the next job on that tag is scheduled. [FND-8B4A5414; FND-F0D015E1]
- Control tier: engineering
- Barrier: prevention: reliability review of repeat failures
- Owner: Work management function
- Leading indicator: Tags with two or more corrective jobs within that interval and no closed reliability review.

*(learning: LR-05)*

**Recommendation:** Schedule mandated inspections as fixed-interval work orders that cannot be moved without a deferral record: the reason, a risk assessment and the approval of the integrity function's manager. [FND-FCCB9505; EVD-8307]
- Control tier: administrative
- Barrier: prevention: inspection and deferral control
- Owner: Work management function
- Leading indicator: Mandated inspections past their due interval, and deferrals without an approved record.
- Why not stronger: Deferral control is a management-system rule; the stronger fix for known wall loss, repair or fitness-for-service assessment, belongs to asset integrity (LR-17) and is in that function's section.

*(learning: LR-18)*

*Language check JC6 accepted: Deferral control is a management-system barrier; its tier is stated honestly, and the stronger fix for the wall loss itself is in the asset-integrity section.*

## Summary

| Function | Top learning | Top recommendation | Indicator | Cites |
|---|---|---|---|---|
| F01 Operations & Control Room | LR-09 Isolation depended on reaching hand-operated valves | Remote operation of emergency isolation valves | Time to isolation in drills | FND-4C645CB5 |
| F02 Mechanical Maintenance | LR-02 Return to service without a design-pressure test | Work-order block until a test result is entered | Pressure-boundary jobs with a test record | FND-FD617187 |
| F07 Engineering, Design, Documents & MOC | LR-06 Change procedure not used since 2018 | Change trigger in work-order and stores screens | MOC records per month | FND-8083ECAC |
| F05 Asset Integrity, Corrosion & Inspection | LR-17 Wall loss measured but not acted on | Fitness-for-service assessments on known wall loss | Wall-loss findings without a decision | FND-47B1702F |
| F11 HSE, Process Safety & Audit | LR-20 Generic audits recorded unsupported compliance | Evidence-based, plant-specific audit protocols | Audit claims with evidence | FND-303495E9 |
| F13 Plant & Asset Leadership | LR-21 Audit recommendations extended without approval | Tracker refuses an extension without the approver's record | Extensions without approval | FND-850B270C |
| F09b Emergency Planning & Command | LR-07 No isolation criteria or delegated authority | Isolation criteria and delegated authority in the plan | Release scenarios with written criteria | FND-314D34C5 |
| F08 Work Management & Planning | LR-04 Notification not closed or reviewed | Equipment status linked to notification status | In-service equipment with open notifications (see work management) | FND-56C66B96 |
| F04 Instrumentation, Control & Calibration | LR-10 Gas detection only displayed an alarm | Confirmed-gas voting with executive action | Major-release areas with executive action | FND-D45021AD |
| F12 HR, Training & Competence | LR-12 No defined control-room qualification | Qualification as a rostering prerequisite | Qualified control-room cover | FND-02B682F3 |
| F06 Materials Management (Stores / Procurement) | LR-01 Unspecified local seal used as regular practice | Stores refuse a seal without a specification | Seals issued against a specification | FND-A2048FB8 |
| F03 Electrical Maintenance | LR-11 Damaged flameproof fitting left in service | Replace legacy fittings with certified fittings | Zoned fittings inspected in interval | FND-C7F16268 |
| F09a Fire-fighting Operations & Fire-water Systems | LR-23 Diesel fire-water pumps unavailable or unreliable | Diesel pumps as safety-critical elements with a performance standard | Diesel fire-pump availability | FND-D8BC7096 |
| F10 Security & Surveillance | LR-13 Warnings reached the control room late | Direct line from security posts to the control room | Time from detection to control-room notice in drills | FND-BC00FF3A |
| F99 Unmapped | Roles not yet placed in a function | Place the roles (learning-clusters) | Not set |  |
| F14 Corporate & Board | LR-21 Extensions without the required approval | Approval record required for every extension | Extensions without approval | FND-2A77BAFB |
| F16 Vendors, OEMs & Suppliers | LR-19 Unapproved vendor drawing in use | Approve every vendor drawing before it is controlled | Verified safety-critical drawings | FND-82687B50 |

## Gaps in the evidence

- [GAP] The export does not show the functions' own backlog, deferral or resourcing data for the period before the event. [FND-71D631C1; FND-5ABEE30B]
  - Evidence needed: Maintenance and inspection backlog reports, deferral records and staffing levels by function for 2018 to 2020.

## Limits of this pack

- Function sections cover the five functions with the most T3 findings; F11 and F13 tie at 55 findings and F11 is written out because F13 (plant leadership) is served by site-leadership-coach.
- A management-review input table is not included; add it when the coach feeds a management review.
- The analysis is a desk review of the published enquiry report; it had no site access or interviews.

## Supporting citations

- Operations & Control Room › 1: FND-DE978BF5; FND-DBE08E73; FND-7D28BE30; FND-05841EDA; FND-322112EE; FND-044D1DEC; FND-02310148; FND-6DB250E6
- Operations & Control Room › 2: FND-20217957; FND-4245FBF2; FND-C92C29DB; FND-5F3E97E1; FND-AEA16F83
- Operations & Control Room › 3: FND-4B285961; FND-7885BCF5; FND-FA1C9404; FND-78ED8552; FND-8EC441F3; FND-E44E0EDA; FND-42043FE6; FND-F6B552F6
- Mechanical Maintenance › 1: FND-54180594; FND-FFE174D0; FND-72A7D26C; FND-3746C7B6; FND-42BEF461; FND-D66ACA7B; FND-852B7EC7; FND-DEAA7F90
- Mechanical Maintenance › 2: FND-611A8BFC; FND-137BC719; FND-8ACDE078; FND-50C7319E; FND-B91D4A23; FND-7A10FF70
- Mechanical Maintenance › 3: FND-8DA35CA9; FND-D14B8424; FND-110F964C; FND-4EDE038A; FND-AC9A1E69; FND-82FC718D; FND-E0AE86A6; FND-1A251687
- Mechanical Maintenance › 4: FND-7DF14ADB; FND-31459031
- Engineering, Design, Documents & MOC › 1: FND-F7FE8463; FND-ADF96860; FND-CDE8E62D; FND-07080447; FND-6ECCE231; FND-EB48C68C; FND-9F8CA896; FND-3FEE59DF
- Engineering, Design, Documents & MOC › 2: FND-82687B50; FND-99B3F80E; FND-A1F9AC94; FND-73312E54
- Asset Integrity, Corrosion & Inspection › 1: FND-98A4D631; FND-E5C4209D; FND-C6992EAF; FND-B2B200D4; FND-1F685360; FND-B5D6A73E; FND-256214D9; FND-9FAAE764
- Asset Integrity, Corrosion & Inspection › 2: FND-75CEBE09; FND-C4B133AA; FND-6FA2CEDE; FND-C4842890; FND-B8E1F804; FND-64864239; FND-C048B355; FND-F9D69EC8
- HSE, Process Safety & Audit › 1: FND-C2CB60DC; FND-2F5482CD; FND-B93AE333; FND-304A499A; FND-DFB39372; FND-76A6DEC1; FND-35279095; FND-C9C77FB7
- HSE, Process Safety & Audit › 2: FND-AA571C63; FND-1DF986F8; FND-031A3738; FND-535125C1; FND-E885ED4C
- HSE, Process Safety & Audit › 3: FND-DC0751CF; FND-332DC593; FND-BC32F8F7; FND-7F27ED51; FND-A532B8F8

---

This pack cites 125 of 246 relevant findings.

55 of 93 top-rated relevant findings cited.

Left out on purpose:
- FND-44219027: Left out of the Learnings Register after a reviewer downgrade vote; the vote is recorded in the register's source note, not in this export. Left out here for the same reason.

> Generated with ProbeMatrix Learnings Coach v2.0.0a8 (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
