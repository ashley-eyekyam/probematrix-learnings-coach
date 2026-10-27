# Report Comparison: Hazira gas release and fire, 2020

**DRAFT**

Review: draft · Classification: internal · Version 1.0

Draft because: the investigation status is in progress; no finding is marked as edited by a person

*Learning purposes: not a statutory document. Derived from a ProbeMatrix investigation export; learnings are evidence-linked but should be validated by the organisation before adoption. · Learnings drafted by an AI agent from AI-assisted findings*

*About 18 min read*

**Audience:** HSE and investigation leads

**Incident:** Hazira 2020 · 2020-09-24

## Data quality and limits

- Draft learnings from an unreviewed analysis: the export's Investigation Status is in progress and no finding is marked as edited by a person.

## Bottom line

- Same evidence, different analytical architecture: the export was built from the enquiry committee's own report, so this compares how far each analysis takes the same facts, not the quality of either investigation. [FND-23139BF9; EVD-8645]
- Coverage is close both ways: every one of the 25 register learnings has a counterpart in the committee's report (21 at the same level, 4 in part), and 76 of its 84 items map to a learning (46 fully, 30 in part). [FND-82FC718D; EVD-1494]
- What the second look adds is the organisational reason behind four conditions: no independent check on a high-consequence repair (LR-03), repeat seal failures not read as a warning (LR-05), a response that stayed on finding the leak (LR-08), and warnings softened as they were relayed (LR-13). [FND-F8C125D5; FND-82FC718D; FND-36179046; FND-BC00FF3A]
- Control strength differs: 25 of the committee's 35 recommendations are administrative and 8 engineering; the register's 44 recommendations hold 20 engineering and 4 elimination or substitution changes. [FND-23139BF9; FND-02310148]
- The committee is stronger on plant-specific engineering and testing detail, such as the fire-pump test regime, incident classification, logbooks and control-room layout, which the export does not code as conditions of their own. [FND-A4B843EB; EVD-2432] *(learning: LR-23)*

## Basis of the comparison

Comparison against the other report: Enquiry committee report on the major fire at the Hazira gas processing plant on 24.09.2020 (enquiry committee constituted by the national petroleum and natural gas regulator; regulator-constituted enquiry under an office order of 30.09.2020; the report does not name the statutory provision). The comparison covers analysis coverage, not the quality of either investigation.

Sighted comparison. The evidence behind the export is the committee's report itself: 8 of the 46 evidence items quote or point to its recommendations, and 92 of the 436 findings refer to them in their reasoning (a search of each finding's label, summary, justification and causal text for pages 34 to 36, a recommendation number such as B.5, or the committee recommending). This is report coverage, not independent discovery. The committee had site access, eyewitness interviews, CCTV and control-room records; the export re-analyses the committee's account of them through the four HFACS levels. [EVD-0185; EVD-2506; EVD-5634; EVD-9692; EVD-3452; EVD-0210; EVD-2752; EVD-5105] *(evidence: direct)*

Conflict of interest: this comparison was written with the ProbeMatrix learnings coach, so one of the two compared analyses is the toolmaker's own. Read the counts with that in mind, and review the match judgments in comparison-map.json before relying on them. The operator is not a compared party.

## Coverage both ways

Counts from the compare engine, then one mapping table per direction.

| Item type | Items |
|---|---|
| observation | 43 |
| root_cause | 6 |
| recommendation | 35 |
| action | 0 |

| Direction | Yes | Partial | None |
|---|---|---|---|
| Learnings against comparator items | 21 | 4 | 0 |
| Comparator items against learnings | 46 | 30 | 8 |

| Comparator group | Learning owner entity | Matches |
|---|---|---|
| Facilities | F01 | 2 |
| Facilities | F04 | 7 |
| Facilities | F07 | 2 |
| Fire fighting | F09a | 11 |
| General | F01 | 6 |
| General | F04 | 1 |
| General | F07 | 3 |
| General | F10 | 2 |
| Maintenance | F02 | 6 |
| Maintenance | F03 | 1 |
| Maintenance | F04 | 2 |
| Maintenance | F05 | 3 |
| Maintenance | F08 | 4 |
| Maintenance: corrosion | F05 | 7 |
| Maintenance: electrical | F03 | 6 |
| Provisioning | F02 | 2 |
| Provisioning | F07 | 1 |
| Root cause | F01 | 1 |
| Root cause | F02 | 4 |
| Root cause | F03 | 2 |
| Root cause | F09b | 1 |
| Safety | F09b | 2 |
| Safety | F11 | 8 |
| Safety | F13 | 2 |

| ProbeMatrix learning | Other report | Match | Reason if none | Cites |
|---|---|---|---|---|
| LR-01 A legacy pressure-boundary seal was replaced with an unspecified local part because no one held or owned the specification | RC-03, REC-25, REC-26 (yes); OBS-22, RC-01, RC-02 (partial) | yes |  | FND-8C0BB623; FND-7A32AC87; FND-89962239; EVD-8645 (+34 supporting) |
| LR-02 Pressure-boundary work went back into service without a test to design pressure, because no procedure required one | OBS-22 (yes); RC-01, REC-18 (partial) | yes |  | FND-7C5ED5B3; FND-FD617187; FND-212DC9B7; EVD-2894 (+21 supporting) |
| LR-03 A high-consequence repair depended on one person's judgement, with no independent check of part, method or test | OBS-21, REC-18 (partial) | partial |  | FND-2FAB8D51; FND-A6312B6B; FND-28F8790B; EVD-8645 (+6 supporting) |
| LR-04 The malfunction notification was never closed or reviewed, so the last administrative check before return to service did not happen | OBS-22, REC-20 (yes); OBS-24, REC-19 (partial) | yes |  | FND-50775B5A; FND-56C66B96; FND-267F1E09; EVD-0591 (+12 supporting) |
| LR-05 Repeat failures of the same seal were treated as routine repairs, not as a reliability warning | OBS-23 (partial) | partial |  | FND-8DA35CA9; FND-69067A1C; FND-71D631C1; EVD-1494 (+16 supporting) |
| LR-06 The management-of-change procedure existed on paper but had not been used since 2018 | OBS-42 (yes); REC-25 (partial) | yes |  | FND-5A5F6AB3; FND-8083ECAC; FND-F7FE8463; EVD-2986 (+11 supporting) |
| LR-07 The emergency plan named the major-leak scenario but gave no isolation criteria and no delegated authority to isolate | OBS-13 (yes); RC-06, REC-10 (partial) | yes |  | FND-314D34C5; FND-DE132C95; FND-AE629313; EVD-4052 (+21 supporting) |
| LR-08 When the vapour cloud blocked access, the shift response stayed on 'find the leak' rather than switching to upstream isolation | RC-06, REC-32 (partial) | partial |  | FND-20217957; FND-36179046; FND-305216AF; EVD-9612 (+10 supporting) |
| LR-09 Emergency isolation valves could only be closed by hand at the valve, inside the area the release made unreachable | OBS-04, REC-03 (yes) | yes |  | FND-4C645CB5; FND-31405D96; FND-A7137BC4; EVD-3932 (+15 supporting) |
| LR-10 Gas detection only displayed an alarm; it did not trigger shutdown or protection, and it alarmed after people had already seen the cloud | OBS-06, REC-02 (yes); OBS-05, REC-29 (partial) | yes |  | FND-A245072B; FND-B5C0CE8F; FND-94C28ACE; EVD-8657 (+16 supporting) |
| LR-11 A damaged flameproof light fitting stayed in service in a hazardous area under breakdown-led electrical maintenance | OBS-27, OBS-28, OBS-29, OBS-30, RC-05, REC-24 (yes); OBS-25, OBS-26, RC-04 (partial) | yes |  | FND-784A23E4; FND-74A80D24; FND-C7F16268; EVD-6916 (+19 supporting) |
| LR-12 Control-room staff held emergency duties after a four-day general course, with no defined qualification or simulator practice | OBS-40, REC-32 (yes); REC-33 (partial) | yes |  | FND-337CB67F; EVD-5634 (+23 supporting) |
| LR-13 People saw the release first, but their warnings reached the control room late and diluted | OBS-38, REC-28 (partial) | partial |  | FND-BC00FF3A; FND-5AB5DFA3; FND-1ABF45B7; EVD-4286 (+9 supporting) |
| LR-14 One panning camera was the only view of the skid; it gave intermittent coverage and was lost seconds after ignition | OBS-41, REC-34 (yes) | yes |  | FND-F91D4A48; FND-B59A077E; FND-6A00BC2F; EVD-0210 (+8 supporting) |
| LR-15 Pressure transmitters at the leak point sent no data, and control-room clocks disagreed by up to 12 minutes | OBS-01, OBS-02 (yes); OBS-03, REC-02 (partial) | yes |  | FND-2B5C46B9; FND-4108DB15; FND-B6C89A9C; EVD-6470 (+12 supporting) |
| LR-16 A calibration setting on the failed meter was changed and reversed without any record or checklist | OBS-21, REC-17 (yes) | yes |  | FND-85748D86; FND-8F0CB4F9; FND-1E35B220; EVD-2506 (+23 supporting) |
| LR-17 Known pipe-wall loss was measured but not acted on: no corrective plan for three years, and painting used as the fix | OBS-35, OBS-36, OBS-37, REC-22 (yes) | yes |  | FND-98A4D631; FND-6D307E93; FND-5EC15274; EVD-5527 (+30 supporting) |
| LR-18 The four-year thickness inspection cycle slipped to six years, and original baseline data and pipe schedules were missing | OBS-32, OBS-33 (yes); OBS-31, OBS-34, REC-21, REC-23 (partial) | yes |  | FND-172D2FE4; FND-75CEBE09; FND-2F99FB62; EVD-8307 (+14 supporting) |
| LR-19 The metering P&ID was a lost original replaced by an unapproved vendor drawing that did not match the field | OBS-01, REC-01 (yes) | yes |  | FND-72DCEE68; FND-82687B50; FND-D25BF914; EVD-0933 (+9 supporting) |
| LR-20 Safety audits used generic checklists and recorded compliance without site data, so they could not find plant-specific defects | OBS-07, OBS-08, REC-04 (yes) | yes |  | FND-C0466EB3; FND-4215704E; FND-303495E9; EVD-9692 (+23 supporting) |
| LR-21 External-audit recommendations were extended without the required approval, so overdue safety actions had no accountable owner | OBS-09, REC-05 (yes) | yes |  | FND-1D713648; FND-850B270C; FND-5A742738; EVD-6852 (+5 supporting) |
| LR-22 Maintenance notifications were treated as work permits, permits went missing untracked, and job safety plans were absent | OBS-12, REC-08, REC-09 (yes) | yes |  | FND-7E1F2B3F; FND-AA571C63; FND-A3D2773A; EVD-5105 (+11 supporting) |
| LR-23 Three of four diesel fire-water pumps were unavailable or unreliable; electric pumps happened to carry the incident | OBS-17, REC-15 (yes); OBS-15, OBS-16, OBS-18, OBS-19, REC-11, REC-12, REC-13, REC-14, REC-16 (partial) | yes |  | FND-A4B843EB; FND-814A8889; FND-B6BB0738; EVD-2432 (+10 supporting) |
| LR-24 Fire drill records held no actions or observations, so drills could not show whether readiness was improving | OBS-10, REC-06 (yes) | yes |  | FND-DC0751CF; FND-B8B75D91; FND-BFABC63C; EVD-2130 (+5 supporting) |
| LR-25 The new control room had blast-proof walls but ordinary doors, in an area that filled with vapour | OBS-39, REC-30 (yes) | yes |  | FND-D871D980; FND-1B3355D5; EVD-1460 |

| Other report | ProbeMatrix learning | Match | Reason if none | Cites |
|---|---|---|---|---|
| OBS-01 The metering-system drawing does not match the field configuration of valves and meters | LR-15, LR-19 | yes |  | FND-2B5C46B9; FND-4108DB15 |
| OBS-02 Time stamps in the control systems of the different control rooms vary by 2 to 12 minutes, which makes matching the data difficult | LR-15 | yes |  | FND-2B5C46B9; FND-4108DB15 |
| OBS-03 An instrument shown on the drawing is not shown or configured in the control system | LR-15 | partial |  | FND-2B5C46B9; FND-4108DB15 |
| OBS-04 Motor-operated valves in the gas-terminal station are for local operation only, with no remote operation from the control room during an emergency | LR-09 | yes |  | FND-4C645CB5; FND-31405D96 |
| OBS-05 Hydrocarbon and H2S detectors are configured to the annunciator panel for display, not to the control system for history | LR-10 | partial |  | FND-A245072B; FND-B5C0CE8F |
| OBS-06 The fire and gas detection system has no provision for automatic plant shutdown or for activating fire suppression | LR-10 | yes |  | FND-A245072B; FND-B5C0CE8F |
| OBS-07 The safety self-audit uses a comprehensive location checklist that is not specific to each plant, so many observations are missed | LR-20 | yes |  | FND-C0466EB3; FND-4215704E |
| OBS-08 Internal safety audits in 2018 and 2019 (4 and 3 days, by a three-member committee) gave observations without the filled checklist | LR-20 | yes |  | FND-C0466EB3; FND-4215704E |
| OBS-09 External audit due dates were extended without the approval document the procedure requires | LR-21 | yes |  | FND-1D713648; FND-850B270C |
| OBS-10 Fire drill reports in the maintenance system hold no data on actions taken or recommendations | LR-24 | yes |  | FND-DC0751CF; FND-B8B75D91 |
| OBS-11 Incidents are not classified properly, NIL reports are sent, and no review by HSE, operations or the plant head is in place | — | none | evidence present in the source report, not extracted or coded |  |
| OBS-12 Some original work permits are missing and no record is kept of the missing permits | LR-22 | yes |  | FND-7E1F2B3F; FND-AA571C63 |
| OBS-13 The emergency response and disaster management plan considers heavy product and gas leaks from pipelines and tanks, but does not state the decision on isolating or shutting down the plant or pipelines | LR-07 | yes |  | FND-314D34C5; FND-DE132C95 |
| OBS-14 Fire-water storage and pumping capacity in Phase I, and the pumps being commissioned in Phase II, are described | — | none | evidence present in the source report, not extracted or coded |  |
| OBS-15 Electric and diesel fire pumps are run for 30 minutes per week, which does not meet the applicable industry norms | LR-23 | partial |  | FND-A4B843EB; FND-814A8889 |
| OBS-16 Capacity tests of the fire pumps are not conducted, and no records explain the deviation | LR-23 | partial |  | FND-A4B843EB; FND-814A8889 |
| OBS-17 Of four diesel fire pumps, two are under maintenance, one ran for 30 minutes and the fourth trips after 2 minutes | LR-23 | yes |  | FND-A4B843EB; FND-814A8889 |
| OBS-18 Diesel consumption for running the diesel pumps is not recorded in the log sheet | LR-23 | partial |  | FND-A4B843EB; FND-814A8889 |
| OBS-19 Operation and maintenance of fire pumps, tanks, pipelines, hydrants and monitors is split between several departments, so the functioning of the equipment is not ensured and fire-fighting effectiveness is affected | LR-23 | partial |  | FND-A4B843EB; FND-814A8889 |
| OBS-20 During shifts the fire crews report to the operator's shift in-charge, not to the fire chief | — | none | evidence present in the source report, not extracted or coded |  |
| OBS-21 During the December 2019 calibration, a condensate meter's calibration range was changed and later changed back, with no mention in the signed calibration documents | LR-16 | yes |  | FND-85748D86; FND-8F0CB4F9 |
| OBS-22 After the September 2020 meter work: local O-rings without quality control, a test at operating pressure only, no SOP, and the notification left open | LR-02, LR-04 | yes |  | FND-7C5ED5B3; FND-FD617187 |
| OBS-23 The meter was serviced in November 2018, cleaned and its gasket changed in February 2019, and the gasket changed again in September 2019, which leaked within one year | LR-05 | partial |  | FND-8DA35CA9; FND-69067A1C |
| OBS-24 Of 7935 notifications this year, 1060 are pending, 252 older than three months are incomplete and 79 have no action initiated | LR-04 | partial |  | FND-50775B5A; FND-56C66B96 |
| OBS-25 The maintenance system records no reasons for overrun of scheduled preventive maintenance and has no escalation for delayed jobs | LR-11 | partial |  | FND-784A23E4; FND-74A80D24 |
| OBS-26 Most of the gas-terminal area is Zone 1, so its electrical equipment and lighting are flameproof, with a half-yearly inspection and maintenance schedule | LR-11 | partial |  | FND-784A23E4; FND-74A80D24 |
| OBS-27 When a scheduled lighting job is delayed, the next notification shifts by six months | LR-11 | yes |  | FND-784A23E4; FND-74A80D24 |
| OBS-28 The job against the April 2020 notification was not done, with no record of the reason and no escalation | LR-11 | yes |  | FND-784A23E4; FND-74A80D24 |
| OBS-29 Flameproof fittings carry no unique identification, so it cannot be known whether a given fitting was inspected | LR-11 | yes |  | FND-784A23E4; FND-74A80D24 |
| OBS-30 The post-incident electrical audit was generic and short | LR-11 | yes |  | FND-784A23E4; FND-74A80D24 |
| OBS-31 Pipe-wall thickness is to be measured every four years by a contracted agency, which also analyses and compares the results | LR-18 | partial |  | FND-172D2FE4; FND-75CEBE09 |
| OBS-32 The last two thickness surveys were in 2011 and 2017, so the four-year schedule is not strictly followed | LR-18 | yes |  | FND-172D2FE4; FND-75CEBE09 |
| OBS-33 For many pipes, especially in the gas-terminal area, baseline thickness data and the original drawings and pipe schedules are not available, which makes decisions on corrective action difficult | LR-18 | yes |  | FND-172D2FE4; FND-75CEBE09 |
| OBS-34 The spot-selection procedure does not ensure the same spot is measured each time, so the analysis may not be fully correct | LR-18 | partial |  | FND-172D2FE4; FND-75CEBE09 |
| OBS-35 The 2017 survey identified several pipes with significant thickness loss needing corrective action, but after three years no corrective plan had been developed | LR-17 | yes |  | FND-98A4D631; FND-6D307E93 |
| OBS-36 Thickness loss with heavy pitting on a segment of the trunk line in July 2019 was corrected by painting, on a line with zero corrosion allowance | LR-17 | yes |  | FND-98A4D631; FND-6D307E93 |
| OBS-37 Spot ultrasonic surveys are in place, but follow-up in decision making, planning and execution is lacking | LR-17 | yes |  | FND-98A4D631; FND-6D307E93 |
| OBS-38 Important telephone numbers are on a small sheet hanging in the control panel and are difficult to read | LR-13 | partial |  | FND-BC00FF3A; FND-5AB5DFA3 |
| OBS-39 In the recently built blast-proof gas-terminal control room the panel layout is not well planned (the annunciator panel is behind the main panel) and the doors are not blast-proof and not properly fixed | LR-25 | yes |  | FND-D871D980; FND-1B3355D5 |
| OBS-40 Control-room operations are carried out by people inadequately trained for operations and emergencies | LR-12 | yes |  | FND-337CB67F |
| OBS-41 Pan-tilt-zoom cameras are provided at a few places and take about 90 seconds to turn around | LR-14 | yes |  | FND-F91D4A48; FND-B59A077E |
| OBS-42 The management-of-change procedure published in August 2016 was not followed for gas-header changes in 2013 and 2018 | LR-06 | yes |  | FND-5A5F6AB3; FND-8083ECAC |
| OBS-43 Logbooks are ordinary registers; alarms and events are not logged properly and handover is not recorded | — | none | evidence present in the source report, not extracted or coded |  |
| RC-01 Loss of containment in the condensate metering area from failure of the O-ring of the orifice retaining plate | LR-01, LR-02 | partial |  | FND-8C0BB623; FND-7A32AC87 |
| RC-02 Use of a non-standard O-ring | LR-01 | partial |  | FND-8C0BB623; FND-7A32AC87 |
| RC-03 Lack of control over material sourcing | LR-01 | yes |  | FND-8C0BB623; FND-7A32AC87 |
| RC-04 Ignition of the gas cloud by an exposed electrical fitting | LR-11 | partial |  | FND-784A23E4; FND-74A80D24 |
| RC-05 Inadequate preventive maintenance systems | LR-11 | yes |  | FND-784A23E4; FND-74A80D24 |
| RC-06 Non-isolation or stoppage of the trunk-line operation | LR-07, LR-08 | partial |  | FND-314D34C5; FND-DE132C95 |
| REC-01 Check and approve all vendor-made drawings against the as-built configuration, and preferably digitise them | LR-19 | yes |  | FND-72DCEE68; FND-82687B50 |
| REC-02 Configure all field instruments (pressure transmitters, hydrocarbon and H2S detectors, densitometer) in the control system with alarms, events and history | LR-10 | yes |  | FND-A245072B; FND-B5C0CE8F |
| REC-03 Make all motor-operated valves remotely operable from the control room | LR-09 | yes |  | FND-4C645CB5; FND-31405D96 |
| REC-04 Develop plant-specific self-audit checklists | LR-20 | yes |  | FND-C0466EB3; FND-4215704E |
| REC-05 Report the status of external audit recommendations, and take the competent authority's approval for any extension | LR-21 | yes |  | FND-1D713648; FND-850B270C |
| REC-06 Record all fire drill actions, observations and recommendations in the maintenance system | LR-24 | yes |  | FND-DC0751CF; FND-B8B75D91 |
| REC-07 Analyse and report all incidents per the operator's corporate policy, categorise near misses and minor incidents correctly, review them quarterly and circulate lessons to all plants | — | none | evidence present in the source report, not extracted or coded |  |
| REC-08 Carry out all non-routine and hazardous work under a permit to work with proper authorisation | LR-22 | yes |  | FND-7E1F2B3F; FND-AA571C63 |
| REC-09 File completed permits serially, document any missing permits, introduce sample checks of permits by senior staff, and check the permit system in self-audits | LR-22 | yes |  | FND-7E1F2B3F; FND-AA571C63 |
| REC-10 Consider including heavy product or gas leaks from pipelines and tank rupture as a scenario in the emergency plan, with a documented action plan | LR-07 | partial |  | FND-314D34C5; FND-DE132C95 |
| REC-11 Run fire pumps twice a week as the industry standard requires | LR-23 | partial |  | FND-A4B843EB; FND-814A8889 |
| REC-12 Capacity-test each fire pump as the industry standard requires | LR-23 | partial |  | FND-A4B843EB; FND-814A8889 |
| REC-13 Record diesel consumption, start and stop times and maintenance data such as trips and overheating in the logbook | LR-23 | partial |  | FND-A4B843EB; FND-814A8889 |
| REC-14 Inspect and maintain fire-water pumps periodically and keep the records, as the industry standard requires | LR-23 | partial |  | FND-A4B843EB; FND-814A8889 |
| REC-15 Commission pumps under maintenance and new pumps at the earliest | LR-23 | yes |  | FND-A4B843EB; FND-814A8889 |
| REC-16 Consider a dedicated fire group to operate and maintain all fire-fighting equipment, with single-point responsibility | LR-23 | partial |  | FND-A4B843EB; FND-814A8889 |
| REC-17 Record the master calibrator, actions, replacements and any deviation from procedure in the calibration certificate | LR-16 | yes |  | FND-85748D86; FND-8F0CB4F9 |
| REC-18 Develop an SOP with a checklist for maintenance work on high-pressure gas and liquid metering systems | LR-02, LR-03 | partial |  | FND-7C5ED5B3; FND-FD617187 |
| REC-19 Develop an escalation method for notifications not attended in time, with quarterly monitoring after classifying notifications as critical, non-critical or urgent | LR-04 | partial |  | FND-50775B5A; FND-56C66B96 |
| REC-20 Introduce sample checks and approval of notification closure by senior officers, to ensure the actions taken are recorded | LR-04 | yes |  | FND-50775B5A; FND-56C66B96 |
| REC-21 Use the 2011 and 2017 thickness data as a baseline, measure again in 2020 and 2021, and run a correlation study to find corrosion areas | LR-18 | partial |  | FND-172D2FE4; FND-75CEBE09 |
| REC-22 Take prompt corrective action where metal loss is beyond acceptable limits | LR-17 | yes |  | FND-98A4D631; FND-6D307E93 |
| REC-23 Give the ultrasonic meter and master meter details in the thickness report | LR-18 | partial |  | FND-172D2FE4; FND-75CEBE09 |
| REC-24 Give every flameproof fitting and junction box a unique identification tag | LR-11 | yes |  | FND-784A23E4; FND-74A80D24 |
| REC-25 Document any decision to source spares locally, when original spares are not available, with authorisation from the appropriate authority, preferably through management of change | LR-01 | yes |  | FND-8C0BB623; FND-7A32AC87 |
| REC-26 Ensure proper specifications and quality-control checks for gaskets and other spares sourced on the open market | LR-01 | yes |  | FND-8C0BB623; FND-7A32AC87 |
| REC-27 Formalise storage and inventory management of rubber items, with documentation | — | none | evidence present in the source report, not extracted or coded |  |
| REC-28 Display important telephone numbers properly in the control room | LR-13 | partial |  | FND-BC00FF3A; FND-5AB5DFA3 |
| REC-29 Display plant trips and alarms in the relevant control rooms and the master control room | LR-10 | partial |  | FND-A245072B; FND-B5C0CE8F |
| REC-30 Fit proper blast-proof doors to the gas-terminal control room, and educate staff to keep them closed | LR-25 | yes |  | FND-D871D980; FND-1B3355D5 |
| REC-31 Lay out the panels in the gas-terminal control room to improve visibility and access | — | none | evidence present in the source report, not extracted or coded |  |
| REC-32 Train control-room operating staff for at least one month, preferably on simulators, before assigning control-room duties | LR-12 | yes |  | FND-337CB67F |
| REC-33 Develop basic and refresher training programmes and provide them to all staff regularly | LR-12 | partial |  | FND-337CB67F |
| REC-34 Provide CCTV for each plant, with displays in the plant control rooms and at the master control and security stations | LR-14 | yes |  | FND-F91D4A48; FND-B59A077E |
| REC-35 Develop plant-wise control-room logbooks and an SOP for logging records, events and alarms, including handover details | — | none | evidence present in the source report, not extracted or coded |  |

## Depth and ownership

| Dimension | Other report | ProbeMatrix | Cites |
|---|---|---|---|
| Levels reached | Observations grouped by subject and six root causes: the failed seal, the non-standard part, sourcing control, the ignition source, preventive maintenance and non-isolation (RC-01 to RC-06) | 436 findings across all four HFACS levels, drawn into 25 learnings: 19 at level 4, 5 at level 3 and 1 at level 2 | FND-23139BF9; FND-82FC718D; FND-DF1144C3 |
| Ownership | Recommendations are addressed to the operator as a whole; one names an owning function (a dedicated fire group, REC-16) and one an approval authority (REC-05) | Each learning names an owning function and co-owners, for example the seal specification across maintenance, engineering and stores (LR-01) | FND-23139BF9; EVD-8645 |
| Actionability | 35 recommendations, each a stated change | 44 recommendations, each with a control tier and a leading indicator | FND-02310148; FND-1A251687 |
| Evidence basis | First-hand: site inspection, eyewitness interviews, CCTV, control-room data and records | Second-hand: every finding cites the committee's quoted text through 46 evidence items | FND-9B406A83; EVD-9220; EVD-9612 |
| Interfaces | Separate sections by subject (facilities, safety, fire fighting, maintenance, general) report separately | Learnings name the seams between functions, such as the security-to-control-room warning route (LR-13) and the maintenance, procurement and engineering seam on the seal specification (LR-01) | FND-BC00FF3A; FND-23139BF9 |

## Control-tier profile

| Control tier | Other report recommendations | ProbeMatrix register recommendations | Cites |
|---|---|---|---|
| Elimination | 0 | 2 | FND-065439DE; FND-110F964C; FND-1A251687; FND-23139BF9; FND-2B0A49CB |
| Substitution | 0 | 2 | FND-02C51A67; FND-0B35D995; FND-1280E788; FND-198069BD; FND-1D61DC3A |
| Engineering | 8 | 20 | FND-01ADF0AA; FND-01C3DE98; FND-02310148; FND-031A3738; FND-044D1DEC |
| Administrative | 25 | 16 | FND-01ADF0AA; FND-02310148; FND-02B682F3; FND-02C51A67; FND-044D1DEC |
| Training | 2 | 4 | FND-02B682F3; FND-057E89A7; FND-07080447; FND-0AEE9898; FND-13708453 |
| PPE | 0 | 0 |  |

## Side by side

| Topic | Other report says | ProbeMatrix says | Cites |
|---|---|---|---|
| Seal substitution | Use of a non-standard O-ring and lack of control over material sourcing (RC-02, RC-03); document local sourcing decisions, preferably through management of change (REC-25) | LR-01: no role owned re-establishing the lost specification, so the substitute became normal practice; the register adds substitution and engineering controls | FND-8C0BB623; FND-7A32AC87; FND-89962239; EVD-8645 |
| Isolation | Non-isolation of the trunk line (RC-06); the emergency plan does not state the isolation decision (OBS-13); add a leak scenario and action plan (REC-10) and remote valve operation (REC-03) | LR-07, LR-08, LR-09: no isolation criteria or delegated authority, a response that stayed on locating the leak, and valves reachable only inside the cloud | FND-314D34C5; FND-DE132C95; FND-AE629313; EVD-4052 |
| Repeat seal failures | The seal changes are listed in the maintenance history (OBS-23) | LR-05: nothing counted repeat failures on the same item, so each was fixed as if it were the first | FND-8DA35CA9; FND-69067A1C; FND-71D631C1; EVD-1494 |
| Fire and gas detection | Interlock detection to automatic shutdown and fire suppression (REC-02) | LR-10 reaches the same engineering fix and states why: the system was designed to inform, not to act | FND-A245072B; FND-B5C0CE8F; FND-94C28ACE; EVD-8657 |
| Warnings to the control room | Telephone numbers hard to read; display them properly (OBS-38, REC-28) | LR-13: perimeter staff had no direct line or standard words, so warnings were relayed and softened | FND-BC00FF3A; FND-5AB5DFA3; FND-1ABF45B7; EVD-4286 |

## Where the other report is stronger

The committee's fire-fighting section is more specific than the export: pump run frequency and capacity tests against the industry standard, diesel logs, maintenance split across departments, and the reporting line of the fire crews (OBS-15 to OBS-20, REC-11 to REC-16). The export codes the unavailable diesel pumps (LR-23) but not the test regime [FND-A4B843EB; EVD-2432]. *(learning: LR-23)*

It also covers topics the export does not code as conditions of their own: incident classification and review (OBS-11, REC-07), logbooks and handover records (OBS-43, REC-35), control-room panel layout (REC-31) and storage of rubber spares (REC-27). They rest on the committee's own review of records and its site inspection, which the export does not reproduce.

Its evidence is first-hand: the site inspection, eyewitness interviews, CCTV frames and control-room data. Several recommendations are direct plant changes the operator can act on, such as unique tags on every flameproof fitting (REC-24) and remote operation of all motor-operated valves (REC-03) [FND-ABF11182; EVD-0496; FND-02310148; EVD-3932].

## Limits of this comparison

Desk analysis: the export saw only what the committee wrote. It could not see the plant, the people or the records, and its findings inherit the committee's facts and any gaps in them. The committee's report gives two different years for one seal change, and the export follows the later one [FND-82FC718D; EVD-1494].

Transcription: the comparator inventory was typed by hand from the text layer of the report PDF, with roles in place of names and functions in place of company names. Recommendations were split by their sub-numbers (A.1 into its drawing and control-system parts; B.5, C.1, C.2 and D.1 to D.3 by sub-item). The control tiers of the committee's recommendations are this comparison's classification, not the committee's. Section 11's narrative conclusions and its reconstruction are not inventoried as separate items; its six numbered root causes stand for them.

Two findings quote recommendation text, numbered D.2.iii and D.2.iv, that the committee's report does not contain [FND-7A32AC87; FND-212DC9B7]; the comparison uses the report's own wording. Counts here are learnings and comparator items, not finding instances.

## Supporting citations

- Coverage both ways › 4, row 1: FND-B356F15B; FND-91B45FF9; FND-DA67926D; FND-54180594; FND-82673283; FND-45363DCA; FND-A2048FB8; FND-FFE174D0; FND-A443D288; FND-72A7D26C; FND-CEE4B00B; FND-3746C7B6; FND-42BEF461; FND-D66ACA7B; FND-852B7EC7; FND-DEAA7F90; FND-A3D7D53F; FND-B86F67F0; FND-D40839C1; FND-BC4FD086; FND-23139BF9; FND-EBB66554; FND-B440C1BF; FND-8CE00707; FND-6B3A6492; FND-A0017E28; FND-B56701CA; FND-2B0A49CB; FND-35861FFB; FND-2CEE8915; FND-48C48354; FND-9A8F3D7A; FND-7832DDF6; FND-DE30BD8B
- Coverage both ways › 4, row 2: FND-15279F97; FND-7FA02383; FND-4944554C; FND-FDFA6FF5; FND-1662466D; FND-9174A5B0; FND-611A8BFC; FND-904FCA63; FND-C34A026C; FND-257C1100; FND-137BC719; FND-8ACDE078; FND-5919B328; FND-C4E06264; FND-3AB996FC; FND-86CB3683; FND-491EDE74; FND-50C7319E; FND-B91D4A23; FND-7A10FF70; FND-71EE9734
- Coverage both ways › 4, row 3: FND-59A2F497; FND-F8C125D5; FND-615DB819; FND-7DF14ADB; FND-31459031; FND-63B6D260
- Coverage both ways › 4, row 4: FND-8071945B; FND-C59DCD29; FND-AE60859C; FND-2B53492C; FND-96DB7E93; FND-FA807C69; FND-977FABA2; FND-6D3446CD; FND-646BAC1F; FND-62EF1667; FND-30C43927; FND-678E51A3
- Coverage both ways › 4, row 5: FND-CEE3D4D7; FND-D14B8424; FND-110F964C; FND-4EDE038A; FND-AC9A1E69; FND-FEC84761; FND-82FC718D; FND-3A34BAD3; FND-E0AE86A6; FND-1A251687; FND-55F68376; FND-350C35AD; FND-AC8FBB26; FND-F0D015E1; FND-8B4A5414; FND-065439DE
- Coverage both ways › 4, row 6: FND-7838175A; FND-ADF96860; FND-CDE8E62D; FND-07080447; FND-CAF9833D; FND-6ECCE231; FND-EB48C68C; FND-9F8CA896; FND-3FEE59DF; FND-922A04DB; FND-EEC2407A
- Coverage both ways › 4, row 7: FND-81E3EEA0; FND-500E0B2D; FND-8DAFDADC; FND-7505B1AF; FND-2EC435D0; FND-BB4CC662; FND-D4A3EF8A; FND-4F687CC5; FND-D1DF4895; FND-7A2429CE; FND-33D32D4C; FND-DF1144C3; FND-82761CC5; FND-730D0DCA; FND-6472CD15; FND-E009D26B; FND-5C7B163D; FND-446A7956; FND-D4A6F6B6; FND-A206DFD6; FND-8A8F94A5
- Coverage both ways › 4, row 8: FND-4245FBF2; FND-C92C29DB; FND-5F3E97E1; FND-82D49143; FND-AEA16F83; FND-744032B6; FND-13708453; FND-969D104C; FND-61129BB8; FND-F887999D
- Coverage both ways › 4, row 9: FND-DE978BF5; FND-DBE08E73; FND-7D28BE30; FND-05841EDA; FND-322112EE; FND-044D1DEC; FND-02310148; FND-6DB250E6; FND-A19F3D9C; FND-9B406A83; FND-01ADF0AA; FND-594A80E9; FND-BDD73BA2; FND-FD0EF0F5; FND-097AB964
- Coverage both ways › 4, row 10: FND-9399FA02; FND-D45021AD; FND-4D7CF773; FND-119E6CF7; FND-5BC96E8A; FND-2D90823E; FND-01C3DE98; FND-6155A1C2; FND-4458E0C0; FND-5897D1E4; FND-3D785319; FND-A31F75EF; FND-5134D887; FND-789D5D60; FND-C5000A82; FND-15B4E60F
- Coverage both ways › 4, row 11: FND-554BFB4A; FND-1D61DC3A; FND-ADC25F29; FND-0B35D995; FND-5E08D0F8; FND-675D99DD; FND-1280E788; FND-ABF11182; FND-CCE6F868; FND-76BE46EF; FND-E6759E06; FND-D1709E71; FND-198069BD; FND-9066FB74; FND-5C43E7A3; FND-FD533742; FND-02C51A67; FND-B1D1AAC1; FND-30EC643B
- Coverage both ways › 4, row 12: FND-E4596837; FND-4C146B0E; FND-02B682F3; FND-D2343F46; FND-4B285961; FND-7885BCF5; FND-F2D32B1D; FND-E3D07562; FND-FA1C9404; FND-78ED8552; FND-8EC441F3; FND-0AEE9898; FND-64E24A9E; FND-2AA87E93; FND-E44E0EDA; FND-42043FE6; FND-F6B552F6; FND-268CA069; FND-6CBACB54; FND-14D093BD; FND-47E58DF8; FND-057E89A7; FND-954553FD
- Coverage both ways › 4, row 13: FND-C75F81B9; FND-57281AC5; FND-37BC45CF; FND-95F9205E; FND-439E0DF7; FND-2F736E5F; FND-0A64F629; FND-A9C42ABE; FND-35636BDF
- Coverage both ways › 4, row 14: FND-38F0B929; FND-934DCBE1; FND-FBC20DA0; FND-2E2F2A38; FND-A528DBE5; FND-E63EB689; FND-D515D5E4; FND-AA71AC71
- Coverage both ways › 4, row 15: FND-0D4C2C13; FND-0FFC03BB; FND-C38CFC44; FND-6163C9EB; FND-FECC34C0; FND-D95B00BD; FND-1A5ECA30; FND-EE34220F; FND-0C37BB1E; FND-2B215AA5; FND-D9A35E88; FND-28F6EE8A
- Coverage both ways › 4, row 16: FND-DC3D4F71; FND-0BA85877; FND-13E2037D; FND-C2B4989C; FND-8D744668; FND-6381588B; FND-D4BB5251; FND-89D53630; FND-E94D563C; FND-9CED3B55; FND-D58142C9; FND-1DA75FF5; FND-89A8965A; FND-693FEDD2; FND-7C8ADD7C; FND-403FD778; FND-A534A1C3; FND-FD98468B; FND-B0BA0566; FND-7F829BEB; FND-98F7C845; FND-4B8F9B10; FND-0B651843
- Coverage both ways › 4, row 17: FND-47B1702F; FND-E5C4209D; FND-C6992EAF; FND-B2B200D4; FND-1F685360; FND-B5D6A73E; FND-256214D9; FND-20034564; FND-9FAAE764; FND-4722A2B8; FND-2E589CCA; FND-4F81E96C; FND-ABDADA0C; FND-7EB223DE; FND-0F19C9FC; FND-6E13192C; FND-B412FF47; FND-5EA23B17; FND-FA73D914; FND-154134EA; FND-30D45EFE; FND-4DAC9500; FND-E87DC506; FND-159C9FD7; FND-540A0904; FND-C90FA7A2; FND-7D59D47D; FND-AA826948; FND-999326F0; FND-8EFDE3D9
- Coverage both ways › 4, row 18: FND-5ABEE30B; FND-C4B133AA; FND-FCCB9505; FND-6FA2CEDE; FND-C4842890; FND-B8E1F804; FND-64864239; FND-C048B355; FND-F9D69EC8; FND-F696F4E0; FND-F131C1B1; FND-637706CD; FND-10FEDDD8; FND-A3DCEBD8
- Coverage both ways › 4, row 19: FND-583EB5FE; FND-9D19BE37; FND-99B3F80E; FND-733F5A1A; FND-6710C6BA; FND-A1F9AC94; FND-73312E54; FND-83AD4621; FND-107C8238
- Coverage both ways › 4, row 20: FND-48967DB2; FND-BB34B250; FND-C2CB60DC; FND-2F5482CD; FND-B93AE333; FND-304A499A; FND-DFB39372; FND-76A6DEC1; FND-35279095; FND-9E1AB5BA; FND-C9C77FB7; FND-459B7917; FND-0621F920; FND-FC482A83; FND-78D4704E; FND-D5242E3B; FND-FE78954C; FND-9F27F129; FND-5BA62765; FND-5C07D424; FND-97325867; FND-9AFEE699; FND-88D0E4B1
- Coverage both ways › 4, row 21: FND-B2AC0F8C; FND-2A77BAFB; FND-856F80CE; FND-81AAC878; FND-9078AFA4
- Coverage both ways › 4, row 22: FND-EFC192D7; FND-1DF986F8; FND-031A3738; FND-535125C1; FND-53C9BDB5; FND-14E2A4B5; FND-D93C5262; FND-78F0BFCF; FND-D5A1CDD9; FND-E885ED4C; FND-0A8B8BCC
- Coverage both ways › 4, row 23: FND-D8BC7096; FND-694B2DA0; FND-26BF96E1; FND-20CC87C0; FND-075C4510; FND-E7FB469A; FND-D9E0CE71; FND-DF7337F2; FND-B955FBD6; FND-4317808B
- Coverage both ways › 4, row 24: FND-C69E0C67; FND-332DC593; FND-BC32F8F7; FND-7F27ED51; FND-A532B8F8

---

This pack cites 150 of 150 relevant findings.

150 of 150 top-rated relevant findings cited.

> Generated with ProbeMatrix Learnings Coach v2.0.0a8 (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
