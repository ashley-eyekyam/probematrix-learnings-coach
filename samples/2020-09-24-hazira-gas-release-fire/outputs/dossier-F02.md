# Cluster Learning Dossier F02 Mechanical Maintenance: Hazira gas terminal release and fire, 2020

**DRAFT**

Review: draft · Classification: internal · Version 1.0

Draft because: the investigation status is in progress; no finding is marked as edited by a person

*Learning purposes: not a statutory document; draft: the investigation status is in progress · Learnings drafted by an AI agent from AI-assisted findings*

*About 14 min read*

**Audience:** Mechanical Maintenance (F02), all tiers

**Incident:** Hazira gas terminal condensate release and fire · 2020-09-24

## Data quality and limits

- Draft learnings from an unreviewed analysis: the ProbeMatrix investigation status is in progress and no finding is marked as edited by a person. Validate before adoption.
- The export mentions regulator involvement but its summary sheet says 'Reportable to Regulator: No'. Confirm the reporting status with the organisation; this pack does not decide it.

## Bottom line

- No one owned the specification for the meter seal, so a locally bought O-ring with no specification or quality check became the regular part. [FND-23139BF9; FND-B56701CA; EVD-8645] *(evidence: corroborated; learning: LR-01)*
- No procedure required a test to design pressure after the repair; the joint went back into service proved only at operating pressure. [FND-50C7319E; FND-4944554C; EVD-2894] *(evidence: direct; learning: LR-02)*
- The repair was planned and manned like routine work, with no independent check of the part, the method or the test. [FND-615DB819; FND-F8C125D5; EVD-2894] *(evidence: corroborated; learning: LR-03)*
- Repeat seal failures on the same meter were fixed one at a time and never escalated for root cause. [FND-1A251687; FND-D14B8424; EVD-1494] *(evidence: direct; learning: LR-05)*
- The notification for the malfunction stayed open after the repair, so no close-out review looked at the part or the test. [FND-FA807C69; FND-678E51A3; EVD-0591] *(evidence: direct; learning: LR-04)*

## Front sheet: decisions and indicators

### Seal specification

**Decision:** Give one function ownership of every pressure-part specification on the site and of approving any substitute. [FND-23139BF9; FND-B56701CA; EVD-8645]
- Options: Maintenance owns the specification and engineering approves substitutes; Engineering owns both, with maintenance and stores bound to its specification list
- Trade-offs: Ownership in maintenance sits close to the work; ownership in engineering keeps the design authority in one place. Either way the stores issue rule must follow it.

*(learning: LR-01)*

### Return to service

**Decision:** Make a test to design pressure, or an engineered equivalent, a hold point before any pressure-boundary joint returns to service. [FND-50C7319E; FND-137BC719; EVD-2894]
- Options: A written procedure with a hold point in the work order; The same, with the work-order system refusing release until a test result is entered
- Trade-offs: A system block is stronger than a procedure but needs the work-order system changed; both lengthen the return to service.

*(learning: LR-02)*

### Repeat failures

**Decision:** Decide how a repeat failure of the same pressure item is escalated, and when an item is replaced rather than repaired again. [FND-1A251687; FND-AC8FBB26; EVD-1494]
- Options: An automatic repeat-failure trigger in the maintenance system; A monthly repeat-failure review owned by a reliability role
- Trade-offs: A trigger catches every repeat but needs someone to own the analysis it opens; a review needs a role the site does not have today.

*(learning: LR-05)*

### Seal specification

**Indicator:** Pressure-boundary spares with a specification [FND-B56701CA]
- Measure: Share of critical pressure-boundary spares with a specification and certificate on file.
- Deterioration looks like: Any seal issued from stores without a specification reference.

### Return to service

**Indicator:** Returns to service with a test record [FND-50C7319E]
- Measure: Share of pressure-boundary jobs returned to service with a recorded test result and witness signature.
- Deterioration looks like: Any return to service on an operating-pressure check only.

### Repeat failures

**Indicator:** Repeat failures reviewed [FND-1A251687]
- Measure: Number of pressure items with a second corrective job within 12 months, and the share with a completed root-cause review.
- Deterioration looks like: A third repair of the same item with no review.

## S1 Profile

194 findings name Mechanical Maintenance: 22 at L1, 36 at L2, 86 at L3 and 50 at L4. A finding can name roles at several tiers.

| Tier | Name | Findings | L1 | L2 | L3 | L4 | Top-rated | Cites |
|---|---|---|---|---|---|---|---|---|
| T2 | First-line supervision / shift in-charge | 127 | 8 | 27 | 60 | 32 | 61 | FND-01ADF0AA; FND-110F964C; FND-1662466D; FND-257C1100; FND-28F8790B |
| T1 | Frontline / sharp end | 115 | 18 | 35 | 37 | 25 | 61 | FND-01ADF0AA; FND-15279F97; FND-1662466D; FND-212DC9B7; FND-28F8790B |
| T3 | Function / department management | 101 | 10 | 11 | 57 | 23 | 49 | FND-110F964C; FND-1280E788; FND-137BC719; FND-1A251687; FND-23139BF9 |
| T9 | Unresolved | 38 | 1 | 7 | 8 | 22 | 19 | FND-1A251687; FND-2FAB8D51; FND-3746C7B6; FND-3AB996FC; FND-42BEF461 |
| T4 | Plant / asset leadership | 16 | 3 | 6 | 6 | 1 | 10 | FND-1280E788; FND-314D34C5; FND-5919B328; FND-7505B1AF; FND-9B406A83 |

Sources: [FND-01ADF0AA; FND-110F964C; FND-1280E788; FND-137BC719; FND-15279F97; FND-1662466D; FND-1A251687; FND-212DC9B7; FND-23139BF9; FND-257C1100; FND-28F8790B; FND-2FAB8D51; FND-314D34C5; FND-3746C7B6; FND-3AB996FC; FND-42BEF461; FND-5919B328; FND-7505B1AF; FND-9B406A83]

Every sub-division has a grounded learning except S13 Comparison, which is left out: no comparator report was supplied for this dossier. Findings where mechanical staff took part in the emergency response (the isolation decision and control-room competence) are covered in S6, because their learning belongs to other functions. [FND-314D34C5; FND-2AA87E93]

## S2 Practice (L1)

**Learning:** Fitting the locally bought O-ring had become the normal way to do the job, so it did not feel like a choice. [FND-91B45FF9; FND-8C0BB623; EVD-8645]

The substitute was used as a regular practice, with no specification or quality check to compare it against [FND-91B45FF9; FND-8C0BB623; EVD-8645]. It made sense at the time: the job had to be done, the original part could not be specified, and nothing in the system said stop.

*(evidence: corroborated; +3 supporting; learning: LR-01)*

**Learning:** With no written test, the crew used the check it had: pressurising to operating pressure. [FND-FD617187; FND-4944554C; EVD-2894; EVD-0185]

After the gasket change on 18 September 2020 no hydro test was done; the system was pressurised to operating pressure and the meter went online the next day [FND-FD617187; FND-4944554C; EVD-2894; EVD-0185]. No procedure named a test pressure, so the quickest available check passed the joint.

*(evidence: direct; +4 supporting; learning: LR-02)*

**Learning:** Each seal failure was handled as a fresh repair. [FND-8DA35CA9; EVD-1494]

The recurring failures were read as routine and repaired the same way, so the pattern started no review [FND-8DA35CA9; EVD-1494]. Nothing on the job record asked whether this was a repeat.

*(evidence: direct; learning: LR-05)*

**Learning:** Notifications stayed open once the job was done. [FND-56C66B96; FND-50775B5A; EVD-0591]

Maintenance notifications were not closed after the work was completed [FND-56C66B96; FND-50775B5A; EVD-0591]. Closing them was not tied to returning the equipment, so leaving them open had no visible effect.

*(evidence: direct; learning: LR-04)*

**Learning:** Painting was chosen for metal loss on a line with no corrosion allowance. [FND-5EC15274; EVD-2397; FND-6D307E93; EVD-5527]

The July 2019 measurement found 1.03mm loss and heavy pitting, and painting was the corrective action [FND-5EC15274; EVD-2397]. The 2017 thickness findings had waited more than three years for a plan [FND-6D307E93; EVD-5527], so a painting job may have looked like progress.

*(evidence: inferred; learning: LR-17)*

## S3 Conditions (L2)

**Learning:** The job was set up without the information it needed: no specification and no quality check for the part. [FND-82673283; FND-54180594; EVD-8645]

The original gasket specification was lost and no substitute specification or quality check existed, so the 18 September 2020 repair used a locally bought O-ring without engineering guidance [FND-82673283; FND-54180594; EVD-8645].

*(evidence: corroborated; +1 supporting; learning: LR-01)*

**Learning:** There was no procedure for taking a high-pressure meter back into service. [FND-9174A5B0; FND-FDFA6FF5; EVD-2894]

No SOP covered calibration and return to service of the high-pressure meters, and no hydrostatic test followed the gasket replacement [FND-9174A5B0; FND-FDFA6FF5; EVD-2894].

*(evidence: direct; +1 supporting; learning: LR-02)*

**Learning:** The repair was planned and manned like routine work. [FND-2FAB8D51; FND-28F8790B; EVD-8645; EVD-2894]

The job was planned without the specification, part quality control, hydrostatic test or notification closure, and no material or quality verification roles were assigned [FND-2FAB8D51; FND-28F8790B; EVD-8645; EVD-2894].

*(evidence: corroborated; +1 supporting; learning: LR-03)*

**Learning:** A meter that kept failing stayed in service. [FND-69067A1C; EVD-1494; EVD-0591]

The meter was kept in service across three gasket replacements in 22 months [FND-69067A1C; EVD-1494; EVD-0591].

*(evidence: direct; learning: LR-05)*

**Learning:** A damaged flame-proof lamp stayed in service in the hazardous area. [FND-784A23E4; EVD-6916]

The lamp had three bolts missing and its glass case open, and was not repaired before ignition [FND-784A23E4; EVD-6916].

*(evidence: direct; learning: LR-11)*

**Learning:** The metering drawing did not match the field. [FND-72DCEE68; FND-733F5A1A; EVD-0933]

The original drawing was lost, the vendor replacement was not checked or approved, and the valve and meter configuration did not match [FND-72DCEE68; FND-733F5A1A; EVD-0933].

*(evidence: direct; learning: LR-19)*

## S4 Supervision (L3)

**Learning:** Supervisors had no rule to enforce on the seal, and the substitution became the modelled norm. [FND-A443D288; FND-42BEF461; FND-852B7EC7; EVD-8645]

Supervision tolerated and modelled the O-ring substitution, and authorised it as a regular practice, without any specification or quality control to hold it to [FND-A443D288; FND-42BEF461; FND-852B7EC7; EVD-8645]. What a supervisor should refuse: a pressure part with no specification behind it.

*(evidence: corroborated; +10 supporting; learning: LR-01)*

**Learning:** Return to service was authorised without the test, and the omission was not caught. [FND-5919B328; FND-8ACDE078; EVD-2894; EVD-0185]

The meter was released without a hydrostatic test, and no one identified or corrected the omission before it went back online [FND-5919B328; FND-8ACDE078; EVD-2894; EVD-0185]. What a supervisor should see before signing: the test result and who witnessed it.

*(evidence: direct; +8 supporting; learning: LR-02)*

**Learning:** Pressure-boundary work was ordered without an independent check or a job safety analysis. [FND-F8C125D5; FND-63B6D260; EVD-5105]

The job was authorised with no independent quality control, inspection or permit verification, and no formal risk assessment [FND-F8C125D5; FND-63B6D260; EVD-5105].

*(evidence: corroborated; +1 supporting; learning: LR-03)*

**Learning:** Repeat failures did not reach a supervisor as a pattern. [FND-110F964C; FND-D14B8424; FND-FEC84761; EVD-1494]

The recurring seal failures were not escalated into a root-cause investigation or a corrective engineering change [FND-110F964C; FND-D14B8424; FND-FEC84761; EVD-1494].

*(evidence: direct; +4 supporting; learning: LR-05)*

**Learning:** The notification for the repair was never closed or reviewed by supervision. [FND-FA807C69; FND-AE60859C; EVD-0591]

The notification raised on 17 September 2020 was left open with no supervisory closure review [FND-FA807C69; FND-AE60859C; EVD-0591].

*(evidence: direct; learning: LR-04)*

**Learning:** Integrity findings were accepted without a corrective plan. [FND-ABDADA0C; FND-C6992EAF; EVD-2397; EVD-5527]

Supervision accepted painting for the July 2019 pitting and left the 2017 thickness findings without a corrective plan [FND-ABDADA0C; FND-C6992EAF; EVD-2397; EVD-5527].

*(evidence: direct; learning: LR-17)*

**Learning:** Calibration work had no checklist, and the signed record did not show a setting change. [FND-D58142C9; FND-E94D563C; EVD-2506]

No checklist was provided for high-pressure calibration jobs, and the December 2019 setting change was not in the signed documents [FND-D58142C9; FND-E94D563C; EVD-2506].

*(evidence: direct; learning: LR-16)*

**Learning:** Permit and job safety plan gaps were left uncorrected. [FND-A3D2773A; FND-EFC192D7; EVD-5105]

Missing permits were not tracked and job safety plans were not attached, and supervision did not correct either [FND-A3D2773A; FND-EFC192D7; EVD-5105].

*(evidence: direct; learning: LR-22)*

## S5 System (L4)

**Learning:** No one owned pressure-part specifications or the approval of substitutes. [FND-23139BF9; FND-B56701CA; FND-D40839C1; EVD-8645]

No role owned the gasket specification, the quality control of its purchase or the authority to approve a substitute, and the organisation came to trust the locally bought O-ring as a valid seal [FND-23139BF9; FND-B56701CA; FND-D40839C1; EVD-8645].

*(evidence: corroborated; +5 supporting; learning: LR-01)*

**Learning:** The organisation trusted operating pressure to prove a repaired joint. [FND-50C7319E; FND-86CB3683; EVD-2894]

There was no return-to-service SOP for high-pressure meter work, and operating-pressure pressurisation was taken as enough [FND-50C7319E; FND-86CB3683; EVD-2894].

*(evidence: direct; +3 supporting; learning: LR-02)*

**Learning:** Safety-critical maintenance was resourced like routine work. [FND-615DB819; EVD-2894; EVD-8645]

The job was manned with no independent quality-control role, test witness or closing supervisor [FND-615DB819; EVD-2894; EVD-8645].

*(evidence: corroborated; learning: LR-03)*

**Learning:** There was no reliability programme for ageing pressure equipment. [FND-1A251687; FND-55F68376; EVD-1494; EVD-0064]

The meter was left to routine resealing, with no manufacturer spares, root-cause work or replacement programme, and kept in service with a 1986 pressure boundary [FND-1A251687; FND-55F68376; EVD-1494; EVD-0064].

*(evidence: direct; +3 supporting; learning: LR-05)*

**Learning:** The change procedure existed but was not used. [FND-F7FE8463; EVD-2986]

The MOC policy was not implemented after 2018, which allowed an unapproved material substitution [FND-F7FE8463; EVD-2986].

*(evidence: direct; learning: LR-06)*

**Learning:** Electrical equipment in hazardous areas was maintained on breakdown. [FND-1280E788; EVD-9999; EVD-6916]

A breakdown-maintenance philosophy for flame-proof equipment in Zone 1 left a damaged fitting in service [FND-1280E788; EVD-9999; EVD-6916].

*(evidence: direct; learning: LR-11)*

**Learning:** The inspection programme ran off its schedule with no escalation. [FND-A3DCEBD8; FND-C4842890; EVD-8307]

The four-year thickness cycle was not kept, and the 2017 findings stayed unplanned [FND-A3DCEBD8; FND-C4842890; EVD-8307].

*(evidence: direct; learning: LR-18)*

**Learning:** Backup fire-water pumps were left degraded. [FND-B955FBD6; FND-DF7337F2; EVD-2432]

Two diesel fire-water pumps were under maintenance and one had an undiagnosed tripping fault [FND-B955FBD6; FND-DF7337F2; EVD-2432].

*(evidence: direct; learning: LR-23)*

## S6 Interfaces

Mechanical Maintenance shares findings with almost every function. The largest seams are with Operations & Control Room (71 shared findings), Asset Integrity, Corrosion & Inspection (40), Engineering, Design, Documents & MOC (34), Work Management & Planning (27) and Materials Management (27) [FND-4944554C; FND-69067A1C; FND-137BC719; FND-1662466D; FND-2CEE8915]. [FND-4944554C; FND-69067A1C; FND-137BC719; FND-1662466D; FND-2CEE8915]

### F06 Materials Management

**Learning:** The seal fell between maintenance and stores: each could take the part as settled by the other. [FND-23139BF9; FND-6B3A6492; EVD-8645]

Stores bought locally available O-rings and maintenance fitted them, with no specification or approval on either side [FND-23139BF9; FND-6B3A6492; EVD-8645].

- Owner: Mechanical Maintenance (F02) with Materials Management (F06)

*(evidence: corroborated; +27 supporting; learning: LR-01)*

### F01 Operations & Control Room

**Learning:** Operations accepted the meter back with no test record to look at. [FND-491EDE74; FND-3AB996FC; EVD-0185]

Return to service after the gasket change went ahead without design-pressure validation, and operations took the meter online the next day [FND-491EDE74; FND-3AB996FC; EVD-0185].

- Owner: Mechanical Maintenance (F02) with Operations & Control Room (F01)

*(evidence: direct; +22 supporting; learning: LR-02)*

### F08 Work Management & Planning

**Learning:** The closure of the job sat with no one between maintenance and work management. [FND-646BAC1F; FND-678E51A3; EVD-0591]

The notification close-out had no assigned review owner and was left open after the repair [FND-646BAC1F; FND-678E51A3; EVD-0591].

- Owner: Mechanical Maintenance (F02) with Work Management & Planning (F08)

*(evidence: direct; learning: LR-04)*

### F05 Asset Integrity, Corrosion & Inspection

**Learning:** Repeat failures and wall-loss findings sat between maintenance and integrity, with no reliability owner. [FND-AC8FBB26; FND-1F685360; EVD-1494; EVD-5527]

Reliability planning across the seal-replacement history was missing, and the 2017 thickness findings had no corrective plan [FND-AC8FBB26; FND-1F685360; EVD-1494; EVD-5527].

- Owner: Mechanical Maintenance (F02) with Asset Integrity (F05)

*(evidence: direct; +14 supporting; learning: LR-05)*

### F07 Engineering, Design, Documents & MOC

**Learning:** A change made through a work order never reached engineering. [FND-5A5F6AB3; FND-CAF9833D; EVD-2986]

The decision to use locally bought O-rings was never recorded or communicated under MOC [FND-5A5F6AB3; FND-CAF9833D; EVD-2986].

- Owner: Mechanical Maintenance (F02) with Engineering (F07)

*(evidence: direct; +1 supporting; learning: LR-06)*

### F09b Emergency Planning & Command

**Learning:** Mechanical staff on the night shift were part of an isolation response that had no criteria. [FND-314D34C5; FND-2AA87E93; EVD-4052; EVD-5634]

The plan gave the control room no isolation decision criteria, and the night-shift crew included mechanical staff with general training only [FND-314D34C5; FND-2AA87E93; EVD-4052; EVD-5634].

- Owner: Emergency Planning & Command (F09b) with Mechanical Maintenance (F02)

*(evidence: corroborated; +4 supporting; learning: LR-07)*

## S7 Barriers

**Barrier:** design and specification (substitution of parts) [FND-B56701CA; FND-23139BF9; EVD-8645]
- Failure mode: No specification for the seal and no owner to re-establish it.
- Type: procedural
- State on the day: absent
- Control tier: substitution
- Fix: Re-establish the seal design and stock only certified parts against it.

*(learning: LR-01)*

**Barrier:** maintenance and testing (testing after maintenance) [FND-50C7319E; FND-5919B328; EVD-2894]
- Failure mode: No procedure required a test to design pressure; operating pressure only.
- Type: procedural
- State on the day: absent
- Control tier: engineering
- Fix: Block release of pressure-boundary jobs in the work-order system until a test result is entered.

*(learning: LR-02)*

**Barrier:** competence and staffing (independent verification) [FND-615DB819; FND-F8C125D5; EVD-2894]
- Failure mode: No independent check of part, method or test was manned.
- Type: procedural
- State on the day: absent
- Control tier: engineering
- Fix: A safety-critical work category that adds inspection, witness and close-out steps.

*(learning: LR-03)*

**Barrier:** inspection and integrity (repeat failures on ageing equipment) [FND-1A251687; FND-82FC718D; EVD-1494]
- Failure mode: No reliability review of repeat failures; the same repair each time.
- Type: procedural
- State on the day: absent
- Control tier: engineering
- Fix: An automatic repeat-failure trigger and a repair-or-replace decision per item.

*(learning: LR-05)*

**Barrier:** inspection and integrity (thickness inspection) [FND-A3DCEBD8; FND-5ABEE30B; EVD-8307]
- Failure mode: Thickness surveys ran six years apart against a four-year schedule, without baseline data.
- Type: procedural
- State on the day: degraded
- Control tier: administrative
- Fix: Schedule inspections in the maintenance system with automatic escalation when overdue.

*(learning: LR-18)*

*Language check JC6 accepted: the scheduling and escalation change is itself the system fix for an inspection cycle that slipped; no elimination, substitution or engineering control applies to a schedule*

## S8 Precursors

The dated signals that reached Mechanical Maintenance. A year-only date means the source gives only the year.

Sources: [EVD-1494; EVD-2397; EVD-2506; EVD-8307; FND-065439DE; FND-0B651843; FND-0BA85877; FND-10FEDDD8; FND-110F964C; FND-13E2037D; FND-159C9FD7; FND-1A251687; FND-20034564; FND-350C35AD; FND-3A34BAD3; FND-403FD778; FND-4722A2B8; FND-4DAC9500; FND-4EDE038A; FND-54180594; FND-55F68376; FND-5ABEE30B; FND-6381588B; FND-69067A1C; FND-693FEDD2; FND-6E13192C; FND-6FA2CEDE; FND-71D631C1; FND-75CEBE09; FND-7C8ADD7C; FND-7D59D47D; FND-7F829BEB; FND-82FC718D; FND-85748D86; FND-89A8965A; FND-89D53630; FND-8B4A5414; FND-8D744668; FND-8EFDE3D9; FND-98F7C845; FND-999326F0; FND-A3D7D53F; FND-A3DCEBD8; FND-A534A1C3; FND-ABDADA0C; FND-AC8FBB26; FND-B0BA0566; FND-B2B200D4; FND-B412FF47; FND-B5D6A73E; FND-B86F67F0; FND-B8E1F804; FND-C2B4989C; FND-C4842890; FND-C90FA7A2; FND-CEE3D4D7; FND-D14B8424; FND-E0AE86A6; FND-E5C4209D; FND-E87DC506; FND-E94D563C; FND-F0D015E1; FND-F9D69EC8; FND-FA73D914; FND-FCCB9505; FND-FD98468B; FND-FEC84761]

- c. 2011 (about 9 years before): Pipe-wall thickness measured in 2011, then not again until 2017, against a four-year schedule. *(weak signal)* [EVD-8307; FND-10FEDDD8; FND-5ABEE30B; FND-6FA2CEDE; FND-75CEBE09; FND-A3DCEBD8; FND-B8E1F804; FND-C4842890; FND-E87DC506; FND-F9D69EC8; FND-FCCB9505]
  - Received by: Mechanical Maintenance (F02, T1)
  - Response: None recorded: the schedule slipped with no escalation.
  - Knowable then: The schedule and the dates of the last measurements were in the inspection records.
- 2018-11 (22 months before): The two condensate meters are cleaned, serviced and calibrated: the first entry in the seal-repair history of the meter that later failed. *(weak signal)* [EVD-1494; FND-065439DE; FND-110F964C; FND-1A251687; FND-350C35AD; FND-3A34BAD3; FND-4EDE038A; FND-54180594; FND-55F68376; FND-69067A1C; FND-71D631C1; FND-82FC718D; FND-8B4A5414; FND-A3D7D53F; FND-AC8FBB26; FND-B86F67F0; FND-CEE3D4D7; FND-D14B8424; FND-E0AE86A6; FND-F0D015E1; FND-FEC84761]
  - Received by: Mechanical Maintenance (F02, T2)
  - Response: Routine service; no review of the seal design recorded.
  - Knowable then: The service record was in the maintenance history.
- 2019-02-25 (18 months before): The same meter is cleaned and its gasket changed, with a locally bought O-ring as the usual substitute. *(weak signal)* [EVD-1494; FND-065439DE; FND-110F964C; FND-1A251687; FND-350C35AD; FND-3A34BAD3; FND-4EDE038A; FND-54180594; FND-55F68376; FND-69067A1C; FND-71D631C1; FND-82FC718D; FND-8B4A5414; FND-A3D7D53F; FND-AC8FBB26; FND-B86F67F0; FND-CEE3D4D7; FND-D14B8424; FND-E0AE86A6; FND-F0D015E1; FND-FEC84761]
  - Received by: Mechanical Maintenance (F02, T2)
  - Response: Repaired like for like; no root-cause review or escalation recorded.
  - Knowable then: A repeat job on the same meter was in the maintenance history, and the substitute O-ring practice was known to the crew and its supervisors.
- 2019-07 (14 months before): A spot ultrasonic measurement finds 1.03mm wall loss with heavy pitting on a segment of the 36-inch pipeline at the gas terminal. *(weak signal)* [EVD-2397; FND-159C9FD7; FND-20034564; FND-4722A2B8; FND-4DAC9500; FND-6E13192C; FND-7D59D47D; FND-8EFDE3D9; FND-999326F0; FND-ABDADA0C; FND-B2B200D4; FND-B412FF47; FND-B5D6A73E; FND-C90FA7A2; FND-E5C4209D; FND-FA73D914]
  - Received by: Mechanical Maintenance (F02, T2)
  - Response: Painting only, completed in December 2019.
  - Knowable then: The measurement and the line's design thickness were on record when the painting-only repair was chosen.
- 2019-12-18 (9 months before): During calibration a setting on the meter is changed and later changed back, with no mention in the signed calibration documents. *(weak signal)* [EVD-2506; FND-0B651843; FND-0BA85877; FND-13E2037D; FND-403FD778; FND-6381588B; FND-693FEDD2; FND-7C8ADD7C; FND-7F829BEB; FND-85748D86; FND-89A8965A; FND-89D53630; FND-8D744668; FND-98F7C845; FND-A534A1C3; FND-B0BA0566; FND-C2B4989C; FND-E94D563C; FND-FD98468B]
  - Received by: Mechanical Maintenance (F02, T1)
  - Response: None recorded: no checklist was used for the job.
  - Knowable then: Only the calibration team knew of the change; the signed record did not show it.

## S9 Tier messages

From the register's tier messages for the seal (LR-01) and the return-to-service test (LR-02).

### T1

If you cannot confirm a seal or gasket matches the specification for a pressure part, stop and ask for the spec. Do not fit 'what we normally use'. After any work that opens a pressure boundary, ask: what test proves this joint, and who witnessed it? Write the answer on the job record. [FND-8C0BB623; FND-FD617187]

### T2

Before signing off pressure-boundary work, check the part against a written specification. No spec means no sign-off. Do not accept equipment back from maintenance without a recorded leak/pressure test to the written test pressure. [FND-852B7EC7; FND-C4E06264]

### T3

Find every pressure-boundary item with no specification on file and re-establish it (OEM, reverse engineering or an engineered substitute). Write and issue a return-to-service procedure for high-pressure equipment that sets test type, test pressure and witness. [FND-DE30BD8B; FND-137BC719]

### T4

Give one named function ownership of pressure-part specifications and of approving any substitute. Treat return to service after pressure-boundary work as a hold point that operations must accept in writing. [FND-23139BF9; FND-50C7319E]

### T5

Ask for assurance that legacy (pre-2000) pressure equipment has current part specifications and controlled spares. [FND-55F68376]

## S10 Recommendations

**Recommendation:** Re-establish the seal design for the meter flange (OEM data or engineered equivalent) and stock only certified parts against that specification; quarantine non-conforming seals. [FND-B56701CA; FND-6B3A6492; EVD-8645; EVD-1494]
- Control tier: substitution
- Barrier: design and specification
- Leading indicator: Share of critical pressure-boundary spares with a specification and certificate on file (target 100%).

*(evidence: corroborated; learning: LR-01)*

**Recommendation:** Make the stores system refuse to issue a pressure-boundary seal without a specification reference and an approved-substitute record. [FND-A0017E28; FND-8CE00707; EVD-8645]
- Control tier: engineering
- Barrier: materials and spares
- Leading indicator: Number of pressure-part issues blocked or referred for engineering approval per quarter, and their closure time.

*(evidence: corroborated; learning: LR-01)*

**Recommendation:** Survey legacy equipment for lost specifications and plan replacement of meters that can no longer be maintained to specification. [FND-55F68376; FND-6B3A6492; EVD-8645; EVD-0064]
- Control tier: elimination
- Barrier: design and specification
- Leading indicator: Percentage of legacy items surveyed; number with a replacement or re-specification decision recorded.

*(evidence: corroborated; learning: LR-01)*

**Recommendation:** Issue a return-to-service procedure for pressure-boundary work stating test medium, test pressure (design-based), hold time and independent witness, with a hold point in the work order. [FND-50C7319E; FND-137BC719; EVD-2894]
- Control tier: administrative
- Barrier: maintenance and testing
- Leading indicator: Share of pressure-boundary work orders closed with a recorded test result and witness signature (audited sample).
- Why not stronger: Paired with the engineering block in the work-order system below; the procedure sets the test the block enforces.

*(evidence: direct; learning: LR-02)*

*Language check JC6 accepted: Paired with the engineering block in the work-order system below; the procedure sets the test the block enforces.*

**Recommendation:** Configure the work-order system so a pressure-boundary job cannot be closed or the equipment released to operations until a test result is entered. [FND-5919B328; FND-491EDE74; EVD-2894; EVD-0185]
- Control tier: engineering
- Barrier: maintenance and testing
- Leading indicator: Number of attempted closures blocked for missing test data; trend to zero over two quarters.

*(evidence: direct; learning: LR-02)*

**Recommendation:** Introduce a safety-critical maintenance category in work planning that automatically adds inspection, test-witness and close-out review steps. [FND-615DB819; FND-F8C125D5; EVD-8645; EVD-2894]
- Control tier: engineering
- Barrier: competence and staffing
- Leading indicator: Share of safety-critical jobs with all verification steps signed by someone other than the performer.

*(evidence: corroborated; learning: LR-03)*

**Recommendation:** Require a job safety analysis and permit review for any work opening a hydrocarbon pressure boundary, separate from the maintenance notification. [FND-63B6D260; EVD-5105]
- Control tier: administrative
- Barrier: procedures and permits
- Leading indicator: Audited share of pressure-boundary jobs with a completed JSA attached in the work system.
- Why not stronger: A job safety analysis is a planning control; the engineering part of this learning is the safety-critical work category above.

*(evidence: corroborated; learning: LR-03)*

*Language check JC6 accepted: A job safety analysis is a planning control; the engineering part of this learning is the safety-critical work category above.*

**Recommendation:** Set an automatic repeat-failure trigger in the CMMS (e.g. two corrective jobs on one tag in 12 months) that opens a root-cause investigation task. [FND-1A251687; FND-D14B8424; EVD-1494]
- Control tier: engineering
- Barrier: inspection and integrity
- Leading indicator: Number of bad actors flagged per quarter and share with a completed root-cause analysis within 60 days.

*(evidence: direct; learning: LR-05)*

## S11 Competence

| Tier | Competence | Cites |
|---|---|---|
| T1 | Recognise a pressure-boundary part with no specification on file and stop the job until one is provided; record the test that proves the joint and who witnessed it. | FND-54180594; FND-212DC9B7 |
| T2 | Check the part against a written specification and the test record before signing off pressure-boundary work; raise a root-cause request when the same item fails twice. | FND-3746C7B6; FND-110F964C |
| T3 | Plan pressure-boundary work as safety-critical, with inspection and witness points; run the repeat-failure report. | FND-2FAB8D51; FND-D14B8424 |
| T4 | Hold ownership of pressure-part specifications in one function, and treat return to service as a hold point. | FND-23139BF9; FND-491EDE74 |

## S12 Transferability

| Learning | Reach | Reason | Cites |
|---|---|---|---|
| LR-01 Seal specification | Industry-wide | Any site with legacy pressure equipment whose original part data is lost | FND-23139BF9 |
| LR-02 Test after maintenance | Industry-wide | Any pressure-boundary work returned to service | FND-50C7319E |
| LR-03 Independent verification | Industry-wide | Any high-consequence job resourced as routine work | FND-615DB819 |
| LR-05 Repeat failures | Industry-wide | Any maintenance system that does not count repeats | FND-1A251687 |
| LR-04 Notification close-out | Other sites | Sites using the same work-management system and closure practice | FND-646BAC1F |

## S14 Formats

| Learning | Format (skill and engine flag) | Cites |
|---|---|---|
| LR-01 Seal specification | frontline-learning-cards --layout cards; frontline-learning-cards --layout toolbox; board-brief --layout paper --format docx | FND-A0017E28 |
| LR-02 Test after maintenance | frontline-learning-cards --layout cards; frontline-learning-cards --layout toolbox; supervisor-coach --layout checklist | FND-FDFA6FF5 |
| LR-03 Independent verification | frontline-learning-cards --layout cards; manager-coach --format docx | FND-28F8790B |
| LR-05 Repeat failures | frontline-learning-cards --layout cards; training-designer --format gift; board-brief --layout paper | FND-55F68376 |
| LR-04 Notification close-out | supervisor-coach --layout checklist; training-designer --format gift | FND-56C66B96 |

## Limits of this pack

- Written from the labels and short texts of all 194 F02 findings and the full text of the highest-rated; the register's grouping of findings into learnings was reused.
- No comparator report was supplied, so S13 is left out.
- Owners and dates for the decisions and recommendations are for the organisation to set.

## Supporting citations

- S2 Practice (L1) › 1: FND-7A32AC87; FND-89962239; FND-B356F15B
- S2 Practice (L1) › 2: FND-7C5ED5B3; FND-212DC9B7; FND-15279F97; FND-7FA02383
- S3 Conditions (L2) › 1: FND-DA67926D
- S3 Conditions (L2) › 2: FND-1662466D
- S3 Conditions (L2) › 3: FND-A6312B6B
- S4 Supervision (L3) › 1: FND-45363DCA; FND-A2048FB8; FND-FFE174D0; FND-72A7D26C; FND-CEE4B00B; FND-3746C7B6; FND-D66ACA7B; FND-DEAA7F90; FND-A3D7D53F; FND-DE30BD8B
- S4 Supervision (L3) › 2: FND-611A8BFC; FND-904FCA63; FND-C34A026C; FND-257C1100; FND-137BC719; FND-C4E06264; FND-7A10FF70; FND-71EE9734
- S4 Supervision (L3) › 3: FND-59A2F497
- S4 Supervision (L3) › 4: FND-71D631C1; FND-CEE3D4D7; FND-4EDE038A; FND-AC9A1E69
- S5 System (L4) › 1: FND-B86F67F0; FND-BC4FD086; FND-8CE00707; FND-6B3A6492; FND-A0017E28
- S5 System (L4) › 2: FND-3AB996FC; FND-491EDE74; FND-B91D4A23
- S5 System (L4) › 4: FND-82FC718D; FND-3A34BAD3; FND-E0AE86A6
- S6 Interfaces › 2: FND-8C0BB623; FND-7A32AC87; FND-89962239; FND-B356F15B; FND-91B45FF9; FND-DA67926D; FND-54180594; FND-82673283; FND-45363DCA; FND-A2048FB8; FND-FFE174D0; FND-A443D288; FND-72A7D26C; FND-CEE4B00B; FND-3746C7B6; FND-42BEF461; FND-D66ACA7B; FND-852B7EC7; FND-DEAA7F90; FND-A3D7D53F; FND-B86F67F0; FND-D40839C1; FND-BC4FD086; FND-8CE00707; FND-A0017E28; FND-B56701CA; FND-DE30BD8B
- S6 Interfaces › 3: FND-7C5ED5B3; FND-FD617187; FND-212DC9B7; FND-15279F97; FND-7FA02383; FND-4944554C; FND-FDFA6FF5; FND-1662466D; FND-9174A5B0; FND-611A8BFC; FND-904FCA63; FND-C34A026C; FND-257C1100; FND-137BC719; FND-8ACDE078; FND-5919B328; FND-C4E06264; FND-86CB3683; FND-50C7319E; FND-B91D4A23; FND-7A10FF70; FND-71EE9734
- S6 Interfaces › 5: FND-8DA35CA9; FND-69067A1C; FND-71D631C1; FND-CEE3D4D7; FND-D14B8424; FND-110F964C; FND-4EDE038A; FND-AC9A1E69; FND-FEC84761; FND-82FC718D; FND-3A34BAD3; FND-E0AE86A6; FND-1A251687; FND-55F68376
- S6 Interfaces › 6: FND-F7FE8463
- S6 Interfaces › 7: FND-DE132C95; FND-7505B1AF; FND-D4A3EF8A; FND-D1DF4895

---

This pack cites 129 of 194 relevant findings.

85 of 91 top-rated relevant findings cited.

> Generated with ProbeMatrix Learnings Coach v2.0.0a6 (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
