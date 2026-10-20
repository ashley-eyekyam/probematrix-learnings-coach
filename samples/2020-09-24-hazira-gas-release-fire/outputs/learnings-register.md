# Learnings Register: Hazira gas terminal condensate release and fire, 24 September 2020 (draft)

**DRAFT**

Review: draft · Classification: internal · Version 1.0

Draft because: the investigation status is in progress; no finding is marked as edited by a person

*Learning purposes: not a statutory document; draft: the investigation status is in progress · Learnings drafted by an AI agent from AI-assisted findings*

## Summary

25 learning(s) and 44 recommendation(s); 24 of 44 recommendation(s) above the administrative tier.

**Learnings by cluster**

| Value | Count |
|---|---|
| F01 | 4 |
| F02 | 4 |
| F03 | 1 |
| F04 | 3 |
| F05 | 2 |
| F07 | 3 |
| F08 | 1 |
| F09a | 1 |
| F09b | 1 |
| F10 | 1 |
| F11 | 3 |
| F13 | 1 |

**Learnings by HFACS level**

| Value | Count |
|---|---|
| L2 Preconditions | 1 |
| L3 Supervision | 5 |
| L4 Organisational Influences | 19 |

**Learnings by priority**

| Value | Count |
|---|---|
| 1 | 11 |
| 2 | 12 |
| 3 | 2 |

**Learnings by counterpart**

| Value | Count |
|---|---|
| not compared | 25 |

**Learnings by tier that must act**

| Value | Count |
|---|---|
| T1 | 18 |
| T2 | 16 |
| T3 | 24 |
| T4 | 19 |
| T5 | 8 |

**Recommendations by control tier**

| Value | Count |
|---|---|
| administrative | 16 |
| elimination | 2 |
| engineering | 20 |
| substitution | 2 |
| training | 4 |

## Priority 1 learnings

### LR-01: A legacy pressure-boundary seal was replaced with an unspecified local part because no one held or owned the specification

**Lesson:** If the original specification for a pressure-boundary part is lost and no role owns re-establishing it, maintainers will fit whatever part is to hand, and the substitute becomes normal practice, because the job has to be done and nothing in the system says 'stop'.

**Context:** The 1986 condensate meter used a rectangular-slot gasket. Its OEM specification was not on file, so locally bought round O-rings had been used as a 'regular practice' with no specification, quality check or recorded approval, across replacements in Nov 2018, Feb 2019 and Sep 2020. The 18 Sep 2020 seal failed on 24 Sep 2020 and was the release source. Maintainers were working in a gap the organisation had left: no spec, no approved substitute, no owner.

Owner entity: F02 Mechanical Maintenance (co-owners: F06, F07) · HFACS level: L4 Resource Management (equipment, spares and technical information)

| What should change | Control tier | Leading indicator |
|---|---|---|
| Re-establish the seal design for the meter flange (OEM data or engineered equivalent) and stock only certified parts against that specification; quarantine non-conforming seals. | substitution | Share of critical pressure-boundary spares with a specification and certificate on file (target 100%). |
| Make the stores system refuse to issue a pressure-boundary seal without a specification reference and an approved-substitute record. | engineering | Number of pressure-part issues blocked or referred for engineering approval per quarter, and their closure time. |
| Survey legacy equipment for lost specifications and plan replacement of meters that can no longer be maintained to specification. | elimination | Percentage of legacy items surveyed; number with a replacement or re-specification decision recorded. |

**Findings:** FND-8C0BB623; FND-7A32AC87; FND-89962239; FND-B356F15B; FND-91B45FF9; FND-DA67926D; FND-54180594; FND-82673283; FND-45363DCA; FND-A2048FB8; FND-FFE174D0; FND-A443D288; FND-72A7D26C; FND-CEE4B00B; FND-3746C7B6; FND-42BEF461; FND-D66ACA7B; FND-852B7EC7; FND-DEAA7F90; FND-A3D7D53F; FND-B86F67F0; FND-D40839C1; FND-BC4FD086; FND-23139BF9; FND-EBB66554; FND-B440C1BF; FND-8CE00707; FND-6B3A6492; FND-A0017E28; FND-B56701CA; FND-2B0A49CB; FND-35861FFB; FND-2CEE8915; FND-48C48354; FND-9A8F3D7A; FND-7832DDF6; FND-DE30BD8B · **Evidence:** EVD-8645; EVD-1494; EVD-0064

**Tiers:** T1: If you cannot confirm a seal or gasket matches the specification for a pressure part, stop and ask for the spec. Do not fit 'what we normally use'.; T2: Before signing off pressure-boundary work, check the part against a written specification. No spec means no sign-off.; T3: Find every pressure-boundary item with no specification on file and re-establish it (OEM, reverse engineering or an engineered substitute).; T4: Give one named function ownership of pressure-part specifications and of approving any substitute.; T5: Ask for assurance that legacy (pre-2000) pressure equipment has current part specifications and controlled spares.

### LR-02: Pressure-boundary work went back into service without a test to design pressure, because no procedure required one

**Lesson:** If no procedure defines how a high-pressure joint is tested before return to service, crews will use the quickest available check (pressurising to operating pressure), and a weak joint will pass, because operating pressure does not prove the joint against the pressures it must withstand.

**Context:** After the 18 Sep 2020 gasket replacement, the system was pressurised to operating pressure with both meters isolated; no hydrostatic test to design pressure was done, and no SOP covered calibration or return to service of these meters. The meter went back online about 46 hours later and was in service when it failed.

Owner entity: F02 Mechanical Maintenance (co-owners: F01, F07) · HFACS level: L4 Organisational Process: procedures (no return-to-service SOP)

| What should change | Control tier | Leading indicator |
|---|---|---|
| Issue a return-to-service procedure for pressure-boundary work stating test medium, test pressure (design-based), hold time and independent witness, with a hold point in the work order. | administrative | Share of pressure-boundary work orders closed with a recorded test result and witness signature (audited sample). |
| Configure the work-order system so a pressure-boundary job cannot be closed or the equipment released to operations until a test result is entered. | engineering | Number of attempted closures blocked for missing test data; trend to zero over two quarters. |

**Findings:** FND-7C5ED5B3; FND-FD617187; FND-212DC9B7; FND-15279F97; FND-7FA02383; FND-4944554C; FND-FDFA6FF5; FND-1662466D; FND-9174A5B0; FND-611A8BFC; FND-904FCA63; FND-C34A026C; FND-257C1100; FND-137BC719; FND-8ACDE078; FND-5919B328; FND-C4E06264; FND-3AB996FC; FND-86CB3683; FND-491EDE74; FND-50C7319E; FND-B91D4A23; FND-7A10FF70; FND-71EE9734 · **Evidence:** EVD-2894; EVD-0185

**Tiers:** T1: After any work that opens a pressure boundary, ask: what test proves this joint, and who witnessed it? Write the answer on the job record.; T2: Do not accept equipment back from maintenance without a recorded leak/pressure test to the written test pressure.; T3: Write and issue a return-to-service procedure for high-pressure equipment that sets test type, test pressure and witness.; T4: Treat return to service after pressure-boundary work as a hold point that operations must accept in writing.

### LR-03: A high-consequence repair depended on one person's judgement, with no independent check of part, method or test

**Lesson:** If a job that can cause a major release is planned and resourced like routine work, with no inspector, test witness or close-out reviewer, then the only barrier is the fitter's knowledge, and any gap in it goes straight into service.

**Context:** The 18 Sep 2020 job was planned without the OEM specification, part QC, a hydrotest or a closing review, and it ran on a SAP notification with no job safety analysis or permit-based risk review. No one was assigned to verify seal specification, quality or post-installation integrity.

Owner entity: F02 Mechanical Maintenance (co-owners: F08, F06) · HFACS level: L3 Planned Inappropriate Operations (team and job resourcing)

| What should change | Control tier | Leading indicator |
|---|---|---|
| Introduce a safety-critical maintenance category in work planning that automatically adds inspection, test-witness and close-out review steps. | engineering | Share of safety-critical jobs with all verification steps signed by someone other than the performer. |
| Require a job safety analysis and permit review for any work opening a hydrocarbon pressure boundary, separate from the maintenance notification. | administrative | Audited share of pressure-boundary jobs with a completed JSA attached in the work system. |

**Findings:** FND-2FAB8D51; FND-A6312B6B; FND-28F8790B; FND-59A2F497; FND-F8C125D5; FND-615DB819; FND-7DF14ADB; FND-31459031; FND-63B6D260 · **Evidence:** EVD-8645; EVD-2894; EVD-5105

**Tiers:** T1: On safety-critical jobs, expect a second person to check your part and your test. Ask for it if no one comes.; T2: Assign a named checker for part, method and test on every safety-critical pressure job before work starts.; T3: Classify maintenance on hydrocarbon pressure boundaries as safety-critical and plan it with inspection and witness points.; T4: Fund an independent QC/inspection role for safety-critical maintenance.

### LR-05: Repeat failures of the same seal were treated as routine repairs, not as a reliability warning

**Lesson:** If nothing in the maintenance system counts repeat failures on the same item, each failure is fixed as if it were the first, and the same inadequate repair is repeated until it fails in the worst conditions.

**Context:** The meter's gasket was replaced in Nov 2018, Feb 2019 and Sep 2020, and a malfunction notification was raised on 17 Sep 2020. None of these triggered root-cause analysis, an engineering review, OEM spares recovery or replacement of the meter. There was no reliability function to see the pattern.

Owner entity: F02 Mechanical Maintenance (co-owners: F05, F08) · HFACS level: L4 Organisational Climate/Culture (inconsistent risk management of known problems)

| What should change | Control tier | Leading indicator |
|---|---|---|
| Set an automatic repeat-failure trigger in the CMMS (e.g. two corrective jobs on one tag in 12 months) that opens a root-cause investigation task. | engineering | Number of bad actors flagged per quarter and share with a completed root-cause analysis within 60 days. |
| Retire or replace pressure equipment that cannot be kept to specification after repeated failures. | elimination | Count of bad-actor items with a recorded repair-or-replace decision. |

**Findings:** FND-8DA35CA9; FND-69067A1C; FND-71D631C1; FND-CEE3D4D7; FND-D14B8424; FND-110F964C; FND-4EDE038A; FND-AC9A1E69; FND-FEC84761; FND-82FC718D; FND-3A34BAD3; FND-E0AE86A6; FND-1A251687; FND-55F68376; FND-350C35AD; FND-AC8FBB26; FND-F0D015E1; FND-8B4A5414; FND-065439DE · **Evidence:** EVD-1494; EVD-0591

**Tiers:** T1: If you are fixing the same fault again, say so on the job record. That note is what starts a root-cause review.; T2: Raise a root-cause request when the same item fails twice in a year.; T3: Run a monthly repeat-failure report from the CMMS and assign a root-cause analysis to each bad actor.; T4: Establish a reliability function (or role) that owns bad-actor review across disciplines.

### LR-06: The management-of-change procedure existed on paper but had not been used since 2018

**Lesson:** If a management-of-change procedure is published but never triggered, changes in parts, materials and pipework happen without risk review, because people do not recognise a 'like-for-unlike' replacement as a change.

**Context:** An MOC SOP was published in Aug 2016, but no MOC had been implemented since 2018. The gasket-to-O-ring substitution, and earlier header changes in 2013 and 2018, went through without change review.

Owner entity: F07 Engineering, Design, Documents & MOC (co-owners: F02, F13) · HFACS level: L4 Organisational Process: oversight of programmes (MOC not implemented)

| What should change | Control tier | Leading indicator |
|---|---|---|
| Build an MOC trigger into the work order and stores issue screens: a non-catalogue or substitute part requires an MOC reference. | engineering | MOCs raised per month (non-zero, trending stable) and share of substitute-part issues with an MOC reference. |
| Relaunch the MOC procedure with a short 'replacement in kind' guide and briefing for maintenance, stores and operations. | training | Share of maintenance and stores staff briefed; MOC quality audit score. (Training alone is weak; pairs with the engineering trigger above.) |

**Findings:** FND-5A5F6AB3; FND-8083ECAC; FND-F7FE8463; FND-7838175A; FND-ADF96860; FND-CDE8E62D; FND-07080447; FND-CAF9833D; FND-6ECCE231; FND-EB48C68C; FND-9F8CA896; FND-3FEE59DF; FND-922A04DB; FND-EEC2407A · **Evidence:** EVD-2986; EVD-8645

**Tiers:** T1: A different part, material or size than the original is a change. Ask for an MOC before fitting it.; T2: Check that any non-like-for-like replacement has an MOC number before you authorise the job.; T3: Define 'replacement not in kind' with examples (seals, gaskets, materials) and make it trigger MOC.; T4: Track the number of MOCs raised per month; zero over a long period means the system is not being used.; T5: Ask for evidence that MOC is in active use at each site, not only that a procedure exists.

### LR-07: The emergency plan named the major-leak scenario but gave no isolation criteria and no delegated authority to isolate

**Lesson:** If an emergency plan names a release scenario but not who may isolate, and on what criteria, isolation waits for escalation up the chain, because people at the scene reasonably believe they need permission to shut in a major supply.

**Context:** The on-site DMP covered hydrocarbon leakage but did not include isolation or stoppage decision criteria. No standing authority below the Plant Manager to close the emergency valves is recorded. The response escalated serially (control room, shift in-charges, Commander-in-Charge) with a mid-incident hand-off; the first isolation valve (MOV 54) closed at 03:01, about 46 minutes after the leak began at 02:12:50.

Owner entity: F09b Emergency Planning & Command (co-owners: F01, F13) · HFACS level: L4 Organisational Process: procedures and policy (emergency plan)

| What should change | Control tier | Leading indicator |
|---|---|---|
| Add scenario-specific isolation and stoppage criteria, isolation valve lists and delegated authority (down to control-room shift level) to the DMP/ERDMP. | administrative | Share of release scenarios in the plan with written criteria, valves and authority; time-to-isolate in drills. |
| Pair the written authority with remote or automatic isolation so the decision can be executed from a safe place (see the isolation-valve learning). | engineering | Drill time from confirmed release to isolation (target set by consequence study). |
| Run unannounced night-shift drills on the major-release scenario that test isolation without senior staff present. | training | Number of night-shift isolation drills per quarter and median time to isolation. |

**Findings:** FND-314D34C5; FND-DE132C95; FND-AE629313; FND-81E3EEA0; FND-500E0B2D; FND-8DAFDADC; FND-7505B1AF; FND-2EC435D0; FND-BB4CC662; FND-D4A3EF8A; FND-4F687CC5; FND-D1DF4895; FND-7A2429CE; FND-33D32D4C; FND-DF1144C3; FND-82761CC5; FND-730D0DCA; FND-6472CD15; FND-E009D26B; FND-5C7B163D; FND-446A7956; FND-D4A6F6B6; FND-A206DFD6; FND-8A8F94A5 · **Evidence:** EVD-4052; EVD-6414; EVD-3932; EVD-9612; EVD-7340

**Tiers:** T1: On a confirmed major hydrocarbon release, isolation is your first job. You are authorised to do it; report while you act.; T2: Know the isolation trigger and the valves for each release scenario on your unit. Do not wait for the call chain to isolate.; T3: Write isolation and stoppage criteria, valve lists and delegated authority into the emergency plan for every release scenario.; T4: Give shift crews standing written authority to isolate and shut down on defined criteria, and back them when they do.; T5: Ask whether every site's emergency plan says who may isolate, on what criteria, without calling up.

### LR-08: When the vapour cloud blocked access, the shift response stayed on 'find the leak' rather than switching to upstream isolation

**Lesson:** If responders are not trained to switch from 'locate and fix' to 'isolate from a distance' as soon as a release blocks access, they keep trying to approach and escalate by phone, because that is what normal leak response looks like.

**Context:** Control-room engineers went out to find the source and were driven back by gas density. Senior shift staff arrived at about 02:35 and could not enter the area; first isolation came at 03:01 and the 36-inch line control valve at 03:04. Responders had no isolation criteria, no remote valves and limited emergency training (see related learnings), so this is a learning about decision support, not individual blame.

Owner entity: F01 Operations & Control Room (co-owners: F13, F09b) · HFACS level: L3 Supervision Inadequate (failure to respond to critical information)

| What should change | Control tier | Leading indicator |
|---|---|---|
| Provide control-room decision aids (isolation matrices by area) for major releases, showing which valves isolate each section and where they can be operated from. | administrative | Isolation matrices in place for all hydrocarbon areas; tested in drills. |
| Scenario training (simulator or tabletop) where access to the source is denied, measuring time to the isolate decision. | training | Share of shift leaders who completed the scenario in the last 12 months; decision time trend. |

**Why no stronger fix:** The gap this learning names is the shift's switch from locating the source on foot to isolating it once dense vapour blocked access (FND-744032B6, FND-C92C29DB, EVD-6414), which decision aids and practised scenarios address. The engineering change for the same response, isolation that does not depend on reaching the valve (FND-F887999D), is recommended in LR-09.

**Findings:** FND-20217957; FND-36179046; FND-305216AF; FND-4245FBF2; FND-C92C29DB; FND-5F3E97E1; FND-82D49143; FND-AEA16F83; FND-744032B6; FND-13708453; FND-969D104C; FND-61129BB8; FND-F887999D · **Evidence:** EVD-9612; EVD-7340; EVD-1460; EVD-9220; EVD-6414

**Tiers:** T1: If you cannot reach the source safely, stop trying. Isolate upstream and downstream from where you can.; T2: Your first decision on a major release is which valves isolate it from a safe place. Make it before you arrive on scene.; T3: Train and drill the switch from 'locate' to 'isolate remotely', with decision aids at the control-room console.

### LR-09: Emergency isolation valves could only be closed by hand at the valve, inside the area the release made unreachable

**Lesson:** If the valves that stop a release can only be operated at the valve, they will be unreachable in exactly the event they exist for, because a large release fills the area around them.

**Context:** MOV 54 and the other Gas Terminal emergency valves had no remote operation from the control room. The dense vapour cloud stopped people approaching from about 02:15; the first valve closed at 03:01. The risk that the valves would be inaccessible during a release had not been assessed.

Owner entity: F01 Operations & Control Room (co-owners: F13, F07) · HFACS level: L4 Resource Management (equipment design)

| What should change | Control tier | Leading indicator |
|---|---|---|
| Convert the Gas Terminal emergency isolation valves to remotely operated ESD valves, operable from the control room and a safe secondary location. | engineering | Share of identified emergency isolation points with remote operation; ESD valve proof-test pass rate. |
| Assess every major-hazard area for access-denied isolation (vapour, fire, toxic) and record the isolation strategy. | administrative | Number of areas with an access-denied isolation assessment completed. |

**Findings:** FND-4C645CB5; FND-31405D96; FND-A7137BC4; FND-DE978BF5; FND-DBE08E73; FND-7D28BE30; FND-05841EDA; FND-322112EE; FND-044D1DEC; FND-02310148; FND-6DB250E6; FND-A19F3D9C; FND-9B406A83; FND-01ADF0AA; FND-594A80E9; FND-BDD73BA2; FND-FD0EF0F5; FND-097AB964 · **Evidence:** EVD-3932; EVD-9612; EVD-1460; EVD-9220; EVD-9941

**Tiers:** T2: Know which emergency valves on your unit can only be shut locally, and how you would isolate if you could not reach them.; T3: List emergency isolation valves that are local-only and assess for each whether a release would deny access.; T4: Fund remote-operated (and where justified, automatic) emergency isolation for inventories that can produce a large vapour cloud.; T5: Ask for a fleet-wide inventory of local-only emergency isolation valves on major hazard sites.

### LR-10: Gas detection only displayed an alarm; it did not trigger shutdown or protection, and it alarmed after people had already seen the cloud

**Lesson:** If fire and gas detection only lights an annunciator, every protective action depends on people noticing, verifying and deciding, which takes minutes to tens of minutes, because the system was designed to inform rather than act.

**Context:** Hydrocarbon/H2S detectors were configured annunciator-only, without DCS history and without automatic shutdown or suppression interlocks. The first control-room alarm came at about 02:20, about 7 minutes after CCTV showed the leak and 5 minutes after security staff saw it. The plant relied on a manual chain that took 46 minutes to isolate.

Owner entity: F04 Instrumentation, Control & Calibration (co-owners: F01, F11) · HFACS level: L4 Organisational Climate/Culture (risk accepted in design of protective systems)

| What should change | Control tier | Leading indicator |
|---|---|---|
| Implement confirmed-gas voting logic that automatically initiates ESD isolation (and deluge where designed) in the metering and Gas Terminal areas. | engineering | Share of major-release areas covered by executive F&G action; spurious-trip and proof-test records. |
| Historise all F&G detector signals in the DCS and review detector coverage against credible release locations. | engineering | Share of detectors historised; detector coverage study completed and gaps closed. |

**Findings:** FND-A245072B; FND-B5C0CE8F; FND-94C28ACE; FND-9399FA02; FND-D45021AD; FND-4D7CF773; FND-119E6CF7; FND-5BC96E8A; FND-2D90823E; FND-01C3DE98; FND-6155A1C2; FND-4458E0C0; FND-5897D1E4; FND-3D785319; FND-A31F75EF; FND-5134D887; FND-789D5D60; FND-C5000A82; FND-15B4E60F · **Evidence:** EVD-8657; EVD-3452; EVD-1284

**Tiers:** T1: Treat a gas alarm as late news: the release has already started. Act on it as confirmed until proved otherwise.; T2: Know which gas alarms on your unit trigger automatic action and which do not. For those that do not, the response is yours.; T3: Review F&G cause-and-effect: which detectors should trip ESD, start deluge or isolate, and where history should be kept.; T4: Approve and fund F&G voting logic with automatic executive action for major-release areas.

### LR-11: A damaged flameproof light fitting stayed in service in a hazardous area under breakdown-led electrical maintenance

**Lesson:** If electrical maintenance in hazardous areas responds to breakdowns instead of inspecting explosion-protected equipment, defects that do not stop the equipment working (missing bolts, open enclosures) stay in service until a release finds them.

**Context:** The investigating committee identified as the probable ignition source an HPMV flameproof lamp at the skid with three bolts missing and its glass case open about 5-6 cm. Electrical PM was breakdown-skewed, and the post-incident audit grouped all nine lamps into one generic status. Confidence is medium because the ignition source is 'probable', not proven.

Owner entity: F03 Electrical Maintenance (co-owners: F11, F02) · HFACS level: L4 Organisational Process: maintenance programme (hazardous-area equipment)

| What should change | Control tier | Leading indicator |
|---|---|---|
| Replace legacy HPMV flameproof lamps in zoned areas with certified, lower-surface-temperature LED fittings. | substitution | Share of zoned-area luminaires replaced with certified fittings. |
| Introduce a risk-based Ex inspection programme (initial, periodic and sample detailed inspections) with item-level records. | administrative | Ex inspection completion against plan; defects found and closed per quarter. |

**Findings:** FND-784A23E4; FND-74A80D24; FND-C7F16268; FND-554BFB4A; FND-1D61DC3A; FND-ADC25F29; FND-0B35D995; FND-5E08D0F8; FND-675D99DD; FND-1280E788; FND-ABF11182; FND-CCE6F868; FND-76BE46EF; FND-E6759E06; FND-D1709E71; FND-198069BD; FND-9066FB74; FND-5C43E7A3; FND-FD533742; FND-02C51A67; FND-B1D1AAC1; FND-30EC643B · **Evidence:** EVD-6916; EVD-9999; EVD-0496

**Tiers:** T1: A flameproof fitting with a missing bolt or open cover is not flameproof. Report it and make it safe the same shift.; T2: Include Ex-equipment checks (bolts, covers, glands) in area rounds and record them by item, not as a group.; T3: Set up a hazardous-area (Ex) inspection programme with item-level records and competent inspectors.; T4: Fund replacement of old HPMV fittings in zoned areas with certified LED fittings.

### LR-12: Control-room staff held emergency duties after a four-day general course, with no defined qualification or simulator practice

**Lesson:** If no qualification is defined for control-room operators, people are assigned to emergency duty after general training only, and a rare, time-critical event becomes their first practice, because rostering fills posts with whoever is available.

**Context:** Control-room training was a four-day general course, with no defined qualification in HR/Operations policy and no simulator practice; the committee recommended at least one month on simulators. The night-shift two-person crew had no member with practised emergency-isolation competence.

Owner entity: F01 Operations & Control Room (co-owners: F12, F02) · HFACS level: L3 Supervision Inadequate (training and qualification)

| What should change | Control tier | Leading indicator |
|---|---|---|
| Define a control-room operator qualification with simulator-based emergency scenarios and a pass standard; make it a rostering prerequisite. | administrative | Share of control-room positions filled by qualified staff on each shift. |
| Deliver at least one month of simulator training (as the committee recommends) with annual emergency refreshers. | training | Simulator hours per operator per year; scenario pass rate. (Training supports, but does not replace, the engineering controls in LR-09 and LR-10.) |

**Why no stronger fix:** The gap this learning names is competence: control-room staff held emergency duties after a four-day general course with no defined qualification or simulator practice (FND-7885BCF5, FND-337CB67F, EVD-5634), which only a qualification standard and training can close. The engineering controls that reduce reliance on that competence are recommended in LR-09 and LR-10.

**Findings:** FND-337CB67F; FND-E4596837; FND-4C146B0E; FND-02B682F3; FND-D2343F46; FND-4B285961; FND-7885BCF5; FND-F2D32B1D; FND-E3D07562; FND-FA1C9404; FND-78ED8552; FND-8EC441F3; FND-0AEE9898; FND-64E24A9E; FND-2AA87E93; FND-E44E0EDA; FND-42043FE6; FND-F6B552F6; FND-268CA069; FND-6CBACB54; FND-14D093BD; FND-47E58DF8; FND-057E89A7; FND-954553FD · **Evidence:** EVD-5634; EVD-1460; EVD-9220

**Tiers:** T1: Ask for practice on the emergencies you are expected to handle. If you have never practised one, tell your supervisor.; T2: Do not roster anyone alone on emergency duty who has not passed the emergency-response assessment for that unit.; T3: Define a control-room qualification (knowledge, simulator scenarios, assessment, refresher interval).; T4: Require that every shift has at least one qualified emergency-competent person in each control room.; T5: Ask for control-room competence assurance (qualified share by site) as a standing board metric.

## All learnings

| LR-ID | Title | Priority | HFACS level | Owner entity | Tiers |
|---|---|---|---|---|---|
| LR-01 | A legacy pressure-boundary seal was replaced with an unspecified local part because no one held or owned the specification | 1 | L4 Resource Management (equipment, spares and technical information) | F02 Mechanical Maintenance (co-owners: F06, F07) | T1; T2; T3; T4; T5 |
| LR-02 | Pressure-boundary work went back into service without a test to design pressure, because no procedure required one | 1 | L4 Organisational Process: procedures (no return-to-service SOP) | F02 Mechanical Maintenance (co-owners: F01, F07) | T1; T2; T3; T4 |
| LR-03 | A high-consequence repair depended on one person's judgement, with no independent check of part, method or test | 1 | L3 Planned Inappropriate Operations (team and job resourcing) | F02 Mechanical Maintenance (co-owners: F08, F06) | T1; T2; T3; T4 |
| LR-04 | The malfunction notification was never closed or reviewed, so the last administrative check before return to service did not happen | 2 | L3 Supervision Inadequate (close-out review) | F08 Work Management & Planning (co-owners: F02, F01) | T1; T2; T3; T4 |
| LR-05 | Repeat failures of the same seal were treated as routine repairs, not as a reliability warning | 1 | L4 Organisational Climate/Culture (inconsistent risk management of known problems) | F02 Mechanical Maintenance (co-owners: F05, F08) | T1; T2; T3; T4 |
| LR-06 | The management-of-change procedure existed on paper but had not been used since 2018 | 1 | L4 Organisational Process: oversight of programmes (MOC not implemented) | F07 Engineering, Design, Documents & MOC (co-owners: F02, F13) | T1; T2; T3; T4; T5 |
| LR-07 | The emergency plan named the major-leak scenario but gave no isolation criteria and no delegated authority to isolate | 1 | L4 Organisational Process: procedures and policy (emergency plan) | F09b Emergency Planning & Command (co-owners: F01, F13) | T1; T2; T3; T4; T5 |
| LR-08 | When the vapour cloud blocked access, the shift response stayed on 'find the leak' rather than switching to upstream isolation | 1 | L3 Supervision Inadequate (failure to respond to critical information) | F01 Operations & Control Room (co-owners: F13, F09b) | T1; T2; T3; T4 |
| LR-09 | Emergency isolation valves could only be closed by hand at the valve, inside the area the release made unreachable | 1 | L4 Resource Management (equipment design) | F01 Operations & Control Room (co-owners: F13, F07) | T1; T2; T3; T4; T5 |
| LR-10 | Gas detection only displayed an alarm; it did not trigger shutdown or protection, and it alarmed after people had already seen the cloud | 1 | L4 Organisational Climate/Culture (risk accepted in design of protective systems) | F04 Instrumentation, Control & Calibration (co-owners: F01, F11) | T1; T2; T3; T4; T5 |
| LR-11 | A damaged flameproof light fitting stayed in service in a hazardous area under breakdown-led electrical maintenance | 1 | L4 Organisational Process: maintenance programme (hazardous-area equipment) | F03 Electrical Maintenance (co-owners: F11, F02) | T1; T2; T3; T4; T5 |
| LR-12 | Control-room staff held emergency duties after a four-day general course, with no defined qualification or simulator practice | 1 | L3 Supervision Inadequate (training and qualification) | F01 Operations & Control Room (co-owners: F12, F02) | T1; T2; T3; T4; T5 |
| LR-13 | People saw the release first, but their warnings reached the control room late and diluted | 2 | L2 Personnel Factors: communication and coordination | F01 Operations & Control Room (co-owners: F10, F02) | T1; T2; T3 |
| LR-14 | One panning camera was the only view of the skid; it gave intermittent coverage and was lost seconds after ignition | 2 | L4 Resource Management (surveillance equipment) | F10 Security & Surveillance (co-owners: F01, F07) | T1; T3; T4 |
| LR-15 | Pressure transmitters at the leak point sent no data, and control-room clocks disagreed by up to 12 minutes | 2 | L4 Resource Management (operational information) | F04 Instrumentation, Control & Calibration (co-owners: F01, F07) | T1; T2; T3; T5 |
| LR-16 | A calibration setting on the failed meter was changed and reversed without any record or checklist | 2 | L3 Supervision Inadequate (calibration oversight) | F04 Instrumentation, Control & Calibration (co-owners: F02, F07) | T1; T2; T3 |
| LR-17 | Known pipe-wall loss was measured but not acted on: no corrective plan for three years, and painting used as the fix | 2 | L4 Organisational Climate/Culture (deferred integrity actions) | F05 Asset Integrity, Corrosion & Inspection (co-owners: F02, F07) | T1; T2; T3; T4; T5 |
| LR-18 | The four-year thickness inspection cycle slipped to six years, and original baseline data and pipe schedules were missing | 2 | L4 Organisational Process: programme oversight (inspection) | F05 Asset Integrity, Corrosion & Inspection (co-owners: F07, F02) | T1; T2; T3; T4; T5 |
| LR-19 | The metering P&ID was a lost original replaced by an unapproved vendor drawing that did not match the field | 2 | L4 Resource Management (technical information) | F07 Engineering, Design, Documents & MOC (co-owners: F02, F14) | T1; T2; T3; T4 |
| LR-20 | Safety audits used generic checklists and recorded compliance without site data, so they could not find plant-specific defects | 2 | L4 Organisational Process: oversight (assurance) | F11 HSE, Process Safety & Audit (co-owners: F13, F01) | T1; T2; T3; T4; T5 |
| LR-21 | External-audit recommendations were extended without the required approval, so overdue safety actions had no accountable owner | 3 | L4 Organisational Process: oversight (action tracking) | F13 Plant & Asset Leadership (co-owners: F11, F14) | T2; T3; T4; T5 |
| LR-22 | Maintenance notifications were treated as work permits, permits went missing untracked, and job safety plans were absent | 2 | L4 Organisational Process: procedures (permit to work) | F11 HSE, Process Safety & Audit (co-owners: F02, F01) | T1; T2; T3 |
| LR-23 | Three of four diesel fire-water pumps were unavailable or unreliable; electric pumps happened to carry the incident | 2 | L4 Resource Management (maintenance of emergency equipment) | F09a Fire-fighting Operations & Fire-water Systems (co-owners: F03, F08) | T1; T2; T3; T4 |
| LR-24 | Fire drill records held no actions or observations, so drills could not show whether readiness was improving | 3 | L4 Organisational Process: oversight (emergency readiness) | F11 HSE, Process Safety & Audit (co-owners: F09b, F12) | T1; T2; T3 |
| LR-25 | The new control room had blast-proof walls but ordinary doors, in an area that filled with vapour | 2 | L4 Organisational Climate/Culture (acceptance of incomplete protection) | F07 Engineering, Design, Documents & MOC (co-owners: F01) | T1; T3; T4 |

---

> Generated with ProbeMatrix Learnings Coach v2.0.0a4 (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
