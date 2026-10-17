# Learnings Register: Hazira gas terminal condensate release and fire, 24 September 2020 (draft)

**Source:** `2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx`. This is a desk analysis of the investigation export; it does not replace site access, interviews or physical examination.

## At a glance

- **25 learnings** from 435 of 436 findings (findings are instances; several describe one condition).
- **11 priority-1 learnings**, 12 priority 2, 2 priority 3.
- **44 recommendations.**

Recommendations at administrative or training tier: **20 of 44 (45%)**. Above administrative (elimination, substitution, engineering): 24 of 44. Every priority-1 learning has at least one recommendation above administrative tier, except LR-08 and LR-12. Those are about decision-making and competence; their stronger controls are the engineering recommendations in LR-07, LR-09 and LR-10 (remote and automatic isolation).

## Summary

### By owner entity

| Owner entity | Learnings |
|---|---:|
| F01 Operations & Control Room | 4 |
| F02 Mechanical Maintenance | 4 |
| F04 Instrumentation, Control & Calibration | 3 |
| F07 Engineering, Design, Documents & MOC | 3 |
| F11 HSE, Process Safety & Audit | 3 |
| F05 Asset Integrity, Corrosion & Inspection | 2 |
| F03 Electrical Maintenance | 1 |
| F08 Work Management & Planning | 1 |
| F09a Fire-fighting Operations & Fire-water Systems | 1 |
| F09b Emergency Planning & Command | 1 |
| F10 Security & Surveillance | 1 |
| F13 Plant & Asset Leadership | 1 |

### By HFACS level

| Level | Learnings |
|---|---:|
| L2 Preconditions | 1 |
| L3 Supervision | 5 |
| L4 Organisational Influences | 19 |

### By organisational system

A learning can touch more than one system.

| Organisational system | Learnings |
|---|---:|
| maintenance regime | 9 |
| assurance and audit | 5 |
| design and human-machine interface | 5 |
| emergency preparedness | 4 |
| procedures | 4 |
| management of change | 2 |
| supervision | 2 |
| training and competence | 2 |
| communication and handover | 1 |
| contractor and supply chain | 1 |
| staffing and fatigue | 1 |

### Recommendations by hierarchy of controls

| HoC tier | Recommendations |
|---|---:|
| elimination | 2 |
| substitution | 2 |
| engineering | 20 |
| administrative | 16 |
| training | 4 |
| ppe | 0 |

### Learning plan: messages by tier

Number of learnings with a message for each tier (full text in the workbook's Learning Plan sheet).

| Tier | Learnings |
|---|---:|
| T1 Frontline | 18 |
| T2 Supervision / shift in-charge | 16 |
| T3 Function management | 24 |
| T4 Plant leadership | 19 |
| T5 Corporate / board | 8 |

## Priority-1 learnings

### LR-01: A legacy pressure-boundary seal was replaced with an unspecified local part because no one held or owned the specification

**Lesson.** If the original specification for a pressure-boundary part is lost and no role owns re-establishing it, maintainers will fit whatever part is to hand, and the substitute becomes normal practice, because the job has to be done and nothing in the system says 'stop'.

**Context.** The 1986 condensate meter used a rectangular-slot gasket. Its OEM specification was not on file, so locally bought round O-rings had been used as a 'regular practice' with no specification, quality check or recorded approval, across replacements in Nov 2018, Feb 2019 and Sep 2020. The 18 Sep 2020 seal failed on 24 Sep 2020 and was the release source. Maintainers were working in a gap the organisation had left: no spec, no approved substitute, no owner.

- **Owner:** F02 Mechanical Maintenance (co-owners: F06, F07). **Tiers:** T1, T2, T3, T4, T5.
- **HFACS:** L4 Resource Management (equipment, spares and technical information). **Causal role:** initiating. **Barrier:** prevention: pressure-boundary integrity (correct seal).
- **Organisational system:** maintenance regime; contractor and supply chain. **Transferability:** industry-wide.
- **Evidence:** EVD-8645, EVD-1494, EVD-0064 (corroborated; confidence high). Supported by 37 findings.
- **Worst credible case:** Flange seal failure releasing condensate vapour that finds an ignition source: major fire or vapour cloud explosion.

| Recommendation | HoC tier | Leading indicator |
|---|---|---|
| Re-establish the seal design for the meter flange (OEM data or engineered equivalent) and stock only certified parts against that specification; quarantine non-conforming seals. | substitution | Share of critical pressure-boundary spares with a specification and certificate on file (target 100%). |
| Make the stores system refuse to issue a pressure-boundary seal without a specification reference and an approved-substitute record. | engineering | Number of pressure-part issues blocked or referred for engineering approval per quarter, and their closure time. |
| Survey legacy equipment for lost specifications and plan replacement of meters that can no longer be maintained to specification. | elimination | Percentage of legacy items surveyed; number with a replacement or re-specification decision recorded. |

**What each tier should do:**

- **T1 Frontline:** If you cannot confirm a seal or gasket matches the specification for a pressure part, stop and ask for the spec. Do not fit 'what we normally use'.
- **T2 Supervision / shift in-charge:** Before signing off pressure-boundary work, check the part against a written specification. No spec means no sign-off.
- **T3 Function management:** Find every pressure-boundary item with no specification on file and re-establish it (OEM, reverse engineering or an engineered substitute).
- **T4 Plant leadership:** Give one named function ownership of pressure-part specifications and of approving any substitute.
- **T5 Corporate / board:** Ask for assurance that legacy (pre-2000) pressure equipment has current part specifications and controlled spares.

### LR-02: Pressure-boundary work went back into service without a test to design pressure, because no procedure required one

**Lesson.** If no procedure defines how a high-pressure joint is tested before return to service, crews will use the quickest available check (pressurising to operating pressure), and a weak joint will pass, because operating pressure does not prove the joint against the pressures it must withstand.

**Context.** After the 18 Sep 2020 gasket replacement, the system was pressurised to operating pressure with both meters isolated; no hydrostatic test to design pressure was done, and no SOP covered calibration or return to service of these meters. The meter went back online about 46 hours later and was in service when it failed.

- **Owner:** F02 Mechanical Maintenance (co-owners: F01, F07). **Tiers:** T1, T2, T3, T4.
- **HFACS:** L4 Organisational Process: procedures (no return-to-service SOP). **Causal role:** initiating. **Barrier:** prevention: post-maintenance pressure test / return-to-service verification.
- **Organisational system:** procedures. **Transferability:** industry-wide.
- **Evidence:** EVD-2894, EVD-0185 (direct; confidence high). Supported by 24 findings.
- **Worst credible case:** Joint failure in service at full pressure with a large release.

| Recommendation | HoC tier | Leading indicator |
|---|---|---|
| Issue a return-to-service procedure for pressure-boundary work stating test medium, test pressure (design-based), hold time and independent witness, with a hold point in the work order. | administrative | Share of pressure-boundary work orders closed with a recorded test result and witness signature (audited sample). |
| Configure the work-order system so a pressure-boundary job cannot be closed or the equipment released to operations until a test result is entered. | engineering | Number of attempted closures blocked for missing test data; trend to zero over two quarters. |

**What each tier should do:**

- **T1 Frontline:** After any work that opens a pressure boundary, ask: what test proves this joint, and who witnessed it? Write the answer on the job record.
- **T2 Supervision / shift in-charge:** Do not accept equipment back from maintenance without a recorded leak/pressure test to the written test pressure.
- **T3 Function management:** Write and issue a return-to-service procedure for high-pressure equipment that sets test type, test pressure and witness.
- **T4 Plant leadership:** Treat return to service after pressure-boundary work as a hold point that operations must accept in writing.

### LR-03: A high-consequence repair depended on one person's judgement, with no independent check of part, method or test

**Lesson.** If a job that can cause a major release is planned and resourced like routine work, with no inspector, test witness or close-out reviewer, then the only barrier is the fitter's knowledge, and any gap in it goes straight into service.

**Context.** The 18 Sep 2020 job was planned without the OEM specification, part QC, a hydrotest or a closing review, and it ran on a SAP notification with no job safety analysis or permit-based risk review. No one was assigned to verify seal specification, quality or post-installation integrity.

- **Owner:** F02 Mechanical Maintenance (co-owners: F08, F06). **Tiers:** T1, T2, T3, T4.
- **HFACS:** L3 Planned Inappropriate Operations (team and job resourcing). **Causal role:** contributory. **Barrier:** prevention: independent verification of critical maintenance.
- **Organisational system:** maintenance regime; supervision. **Transferability:** industry-wide.
- **Evidence:** EVD-8645, EVD-2894, EVD-5105 (corroborated; confidence high). Supported by 9 findings.
- **Worst credible case:** Undetected defect in a pressure joint released straight to service.

| Recommendation | HoC tier | Leading indicator |
|---|---|---|
| Introduce a safety-critical maintenance category in work planning that automatically adds inspection, test-witness and close-out review steps. | engineering | Share of safety-critical jobs with all verification steps signed by someone other than the performer. |
| Require a job safety analysis and permit review for any work opening a hydrocarbon pressure boundary, separate from the maintenance notification. | administrative | Audited share of pressure-boundary jobs with a completed JSA attached in the work system. |

**What each tier should do:**

- **T1 Frontline:** On safety-critical jobs, expect a second person to check your part and your test. Ask for it if no one comes.
- **T2 Supervision / shift in-charge:** Assign a named checker for part, method and test on every safety-critical pressure job before work starts.
- **T3 Function management:** Classify maintenance on hydrocarbon pressure boundaries as safety-critical and plan it with inspection and witness points.
- **T4 Plant leadership:** Fund an independent QC/inspection role for safety-critical maintenance.

### LR-05: Repeat failures of the same seal were treated as routine repairs, not as a reliability warning

**Lesson.** If nothing in the maintenance system counts repeat failures on the same item, each failure is fixed as if it were the first, and the same inadequate repair is repeated until it fails in the worst conditions.

**Context.** The meter's gasket was replaced in Nov 2018, Feb 2019 and Sep 2020, and a malfunction notification was raised on 17 Sep 2020. None of these triggered root-cause analysis, an engineering review, OEM spares recovery or replacement of the meter. There was no reliability function to see the pattern.

- **Owner:** F02 Mechanical Maintenance (co-owners: F05, F08). **Tiers:** T1, T2, T3, T4.
- **HFACS:** L4 Organisational Climate/Culture (inconsistent risk management of known problems). **Causal role:** contributory. **Barrier:** prevention: reliability / bad-actor management.
- **Organisational system:** maintenance regime. **Transferability:** industry-wide.
- **Evidence:** EVD-1494, EVD-0591 (direct; confidence high). Supported by 19 findings.
- **Worst credible case:** Known bad-actor fails during a high-consequence condition.

| Recommendation | HoC tier | Leading indicator |
|---|---|---|
| Set an automatic repeat-failure trigger in the CMMS (e.g. two corrective jobs on one tag in 12 months) that opens a root-cause investigation task. | engineering | Number of bad actors flagged per quarter and share with a completed root-cause analysis within 60 days. |
| Retire or replace pressure equipment that cannot be kept to specification after repeated failures. | elimination | Count of bad-actor items with a recorded repair-or-replace decision. |

**What each tier should do:**

- **T1 Frontline:** If you are fixing the same fault again, say so on the job record. That note is what starts a root-cause review.
- **T2 Supervision / shift in-charge:** Raise a root-cause request when the same item fails twice in a year.
- **T3 Function management:** Run a monthly repeat-failure report from the CMMS and assign a root-cause analysis to each bad actor.
- **T4 Plant leadership:** Establish a reliability function (or role) that owns bad-actor review across disciplines.

### LR-06: The management-of-change procedure existed on paper but had not been used since 2018

**Lesson.** If a management-of-change procedure is published but never triggered, changes in parts, materials and pipework happen without risk review, because people do not recognise a 'like-for-unlike' replacement as a change.

**Context.** An MOC SOP was published in Aug 2016, but no MOC had been implemented since 2018. The gasket-to-O-ring substitution, and earlier header changes in 2013 and 2018, went through without change review.

- **Owner:** F07 Engineering, Design, Documents & MOC (co-owners: F02, F13). **Tiers:** T1, T2, T3, T4, T5.
- **HFACS:** L4 Organisational Process: oversight of programmes (MOC not implemented). **Causal role:** contributory. **Barrier:** prevention: management of change.
- **Organisational system:** management of change. **Transferability:** industry-wide.
- **Evidence:** EVD-2986, EVD-8645 (direct; confidence high). Supported by 14 findings.
- **Worst credible case:** Any unreviewed change in hydrocarbon service introduces a new failure mode.

| Recommendation | HoC tier | Leading indicator |
|---|---|---|
| Build an MOC trigger into the work order and stores issue screens: a non-catalogue or substitute part requires an MOC reference. | engineering | MOCs raised per month (non-zero, trending stable) and share of substitute-part issues with an MOC reference. |
| Relaunch the MOC procedure with a short 'replacement in kind' guide and briefing for maintenance, stores and operations. | training | Share of maintenance and stores staff briefed; MOC quality audit score. (Training alone is weak; pairs with the engineering trigger above.) |

**What each tier should do:**

- **T1 Frontline:** A different part, material or size than the original is a change. Ask for an MOC before fitting it.
- **T2 Supervision / shift in-charge:** Check that any non-like-for-like replacement has an MOC number before you authorise the job.
- **T3 Function management:** Define 'replacement not in kind' with examples (seals, gaskets, materials) and make it trigger MOC.
- **T4 Plant leadership:** Track the number of MOCs raised per month; zero over a long period means the system is not being used.
- **T5 Corporate / board:** Ask for evidence that MOC is in active use at each site, not only that a procedure exists.

### LR-07: The emergency plan named the major-leak scenario but gave no isolation criteria and no delegated authority to isolate

**Lesson.** If an emergency plan names a release scenario but not who may isolate, and on what criteria, isolation waits for escalation up the chain, because people at the scene reasonably believe they need permission to shut in a major supply.

**Context.** The on-site DMP covered hydrocarbon leakage but did not include isolation or stoppage decision criteria. No standing authority below the Plant Manager to close the emergency valves is recorded. The response escalated serially (control room, shift in-charges, Commander-in-Charge) with a mid-incident hand-off; the first isolation valve (MOV 54) closed at 03:01, about 46 minutes after the leak began at 02:12:50.

- **Owner:** F09b Emergency Planning & Command (co-owners: F01, F13). **Tiers:** T1, T2, T3, T4, T5.
- **HFACS:** L4 Organisational Process: procedures and policy (emergency plan). **Causal role:** escalating. **Barrier:** mitigation: emergency isolation.
- **Organisational system:** emergency preparedness. **Transferability:** industry-wide.
- **Evidence:** EVD-4052, EVD-6414, EVD-3932, EVD-9612, EVD-7340 (corroborated; confidence high). Supported by 24 findings.
- **Worst credible case:** Vapour cloud grows for tens of minutes and ignites: fire or vapour cloud explosion with off-site impact.

| Recommendation | HoC tier | Leading indicator |
|---|---|---|
| Add scenario-specific isolation and stoppage criteria, isolation valve lists and delegated authority (down to control-room shift level) to the DMP/ERDMP. | administrative | Share of release scenarios in the plan with written criteria, valves and authority; time-to-isolate in drills. |
| Pair the written authority with remote or automatic isolation so the decision can be executed from a safe place (see the isolation-valve learning). | engineering | Drill time from confirmed release to isolation (target set by consequence study). |
| Run unannounced night-shift drills on the major-release scenario that test isolation without senior staff present. | training | Number of night-shift isolation drills per quarter and median time to isolation. |

**What each tier should do:**

- **T1 Frontline:** On a confirmed major hydrocarbon release, isolation is your first job. You are authorised to do it; report while you act.
- **T2 Supervision / shift in-charge:** Know the isolation trigger and the valves for each release scenario on your unit. Do not wait for the call chain to isolate.
- **T3 Function management:** Write isolation and stoppage criteria, valve lists and delegated authority into the emergency plan for every release scenario.
- **T4 Plant leadership:** Give shift crews standing written authority to isolate and shut down on defined criteria, and back them when they do.
- **T5 Corporate / board:** Ask whether every site's emergency plan says who may isolate, on what criteria, without calling up.

### LR-08: When the vapour cloud blocked access, the shift response stayed on 'find the leak' rather than switching to upstream isolation

**Lesson.** If responders are not trained to switch from 'locate and fix' to 'isolate from a distance' as soon as a release blocks access, they keep trying to approach and escalate by phone, because that is what normal leak response looks like.

**Context.** Control-room engineers went out to find the source and were driven back by gas density. Senior shift staff arrived at about 02:35 and could not enter the area; first isolation came at 03:01 and the 36-inch line control valve at 03:04. Responders had no isolation criteria, no remote valves and limited emergency training (see related learnings), so this is a learning about decision support, not individual blame.

- **Owner:** F01 Operations & Control Room (co-owners: F13, F09b). **Tiers:** T1, T2, T3, T4.
- **HFACS:** L3 Supervision Inadequate (failure to respond to critical information). **Causal role:** escalating. **Barrier:** mitigation: emergency isolation decision.
- **Organisational system:** emergency preparedness; training and competence. **Transferability:** industry-wide.
- **Evidence:** EVD-9612, EVD-7340, EVD-1460, EVD-9220, EVD-6414 (corroborated; confidence medium). Supported by 13 findings.
- **Worst credible case:** Isolation delayed until ignition.

| Recommendation | HoC tier | Leading indicator |
|---|---|---|
| Provide control-room decision aids (isolation matrices by area) for major releases, showing which valves isolate each section and where they can be operated from. | administrative | Isolation matrices in place for all hydrocarbon areas; tested in drills. |
| Scenario training (simulator or tabletop) where access to the source is denied, measuring time to the isolate decision. | training | Share of shift leaders who completed the scenario in the last 12 months; decision time trend. |

**What each tier should do:**

- **T1 Frontline:** If you cannot reach the source safely, stop trying. Isolate upstream and downstream from where you can.
- **T2 Supervision / shift in-charge:** Your first decision on a major release is which valves isolate it from a safe place. Make it before you arrive on scene.
- **T3 Function management:** Train and drill the switch from 'locate' to 'isolate remotely', with decision aids at the control-room console.

### LR-09: Emergency isolation valves could only be closed by hand at the valve, inside the area the release made unreachable

**Lesson.** If the valves that stop a release can only be operated at the valve, they will be unreachable in exactly the event they exist for, because a large release fills the area around them.

**Context.** MOV 54 and the other Gas Terminal emergency valves had no remote operation from the control room. The dense vapour cloud stopped people approaching from about 02:15; the first valve closed at 03:01. The risk that the valves would be inaccessible during a release had not been assessed.

- **Owner:** F01 Operations & Control Room (co-owners: F13, F07). **Tiers:** T1, T2, T3, T4, T5.
- **HFACS:** L4 Resource Management (equipment design). **Causal role:** escalating. **Barrier:** mitigation: emergency isolation (hardware).
- **Organisational system:** design and human-machine interface. **Transferability:** industry-wide.
- **Evidence:** EVD-3932, EVD-9612, EVD-1460, EVD-9220, EVD-9941 (corroborated; confidence high). Supported by 18 findings.
- **Worst credible case:** Release continues unchecked until ignition or inventory exhaustion.

| Recommendation | HoC tier | Leading indicator |
|---|---|---|
| Convert the Gas Terminal emergency isolation valves to remotely operated ESD valves, operable from the control room and a safe secondary location. | engineering | Share of identified emergency isolation points with remote operation; ESD valve proof-test pass rate. |
| Assess every major-hazard area for access-denied isolation (vapour, fire, toxic) and record the isolation strategy. | administrative | Number of areas with an access-denied isolation assessment completed. |

**What each tier should do:**

- **T2 Supervision / shift in-charge:** Know which emergency valves on your unit can only be shut locally, and how you would isolate if you could not reach them.
- **T3 Function management:** List emergency isolation valves that are local-only and assess for each whether a release would deny access.
- **T4 Plant leadership:** Fund remote-operated (and where justified, automatic) emergency isolation for inventories that can produce a large vapour cloud.
- **T5 Corporate / board:** Ask for a fleet-wide inventory of local-only emergency isolation valves on major hazard sites.

### LR-10: Gas detection only displayed an alarm; it did not trigger shutdown or protection, and it alarmed after people had already seen the cloud

**Lesson.** If fire and gas detection only lights an annunciator, every protective action depends on people noticing, verifying and deciding, which takes minutes to tens of minutes, because the system was designed to inform rather than act.

**Context.** Hydrocarbon/H2S detectors were configured annunciator-only, without DCS history and without automatic shutdown or suppression interlocks. The first control-room alarm came at about 02:20, about 7 minutes after CCTV showed the leak and 5 minutes after security staff saw it. The plant relied on a manual chain that took 46 minutes to isolate.

- **Owner:** F04 Instrumentation, Control & Calibration (co-owners: F01, F11). **Tiers:** T1, T2, T3, T4, T5.
- **HFACS:** L4 Organisational Climate/Culture (risk accepted in design of protective systems). **Causal role:** escalating. **Barrier:** mitigation: detection and automatic protective action.
- **Organisational system:** design and human-machine interface. **Transferability:** industry-wide.
- **Evidence:** EVD-8657, EVD-3452, EVD-1284 (corroborated; confidence high). Supported by 19 findings.
- **Worst credible case:** Large release detected late and not acted on automatically.

| Recommendation | HoC tier | Leading indicator |
|---|---|---|
| Implement confirmed-gas voting logic that automatically initiates ESD isolation (and deluge where designed) in the metering and Gas Terminal areas. | engineering | Share of major-release areas covered by executive F&G action; spurious-trip and proof-test records. |
| Historise all F&G detector signals in the DCS and review detector coverage against credible release locations. | engineering | Share of detectors historised; detector coverage study completed and gaps closed. |

**What each tier should do:**

- **T1 Frontline:** Treat a gas alarm as late news: the release has already started. Act on it as confirmed until proved otherwise.
- **T2 Supervision / shift in-charge:** Know which gas alarms on your unit trigger automatic action and which do not. For those that do not, the response is yours.
- **T3 Function management:** Review F&G cause-and-effect: which detectors should trip ESD, start deluge or isolate, and where history should be kept.
- **T4 Plant leadership:** Approve and fund F&G voting logic with automatic executive action for major-release areas.

### LR-11: A damaged flameproof light fitting stayed in service in a hazardous area under breakdown-led electrical maintenance

**Lesson.** If electrical maintenance in hazardous areas responds to breakdowns instead of inspecting explosion-protected equipment, defects that do not stop the equipment working (missing bolts, open enclosures) stay in service until a release finds them.

**Context.** The investigating committee identified as the probable ignition source an HPMV flameproof lamp at the skid with three bolts missing and its glass case open about 5-6 cm. Electrical PM was breakdown-skewed, and the post-incident audit grouped all nine lamps into one generic status. Confidence is medium because the ignition source is 'probable', not proven.

- **Owner:** F03 Electrical Maintenance (co-owners: F11, F02). **Tiers:** T1, T2, T3, T4, T5.
- **HFACS:** L4 Organisational Process: maintenance programme (hazardous-area equipment). **Causal role:** contributory. **Barrier:** prevention: ignition source control.
- **Organisational system:** maintenance regime; assurance and audit. **Transferability:** industry-wide.
- **Evidence:** EVD-6916, EVD-9999, EVD-0496 (direct; confidence medium). Supported by 22 findings.
- **Worst credible case:** Any release in a zoned area finds an ignition source.

| Recommendation | HoC tier | Leading indicator |
|---|---|---|
| Replace legacy HPMV flameproof lamps in zoned areas with certified, lower-surface-temperature LED fittings. | substitution | Share of zoned-area luminaires replaced with certified fittings. |
| Introduce a risk-based Ex inspection programme (initial, periodic and sample detailed inspections) with item-level records. | administrative | Ex inspection completion against plan; defects found and closed per quarter. |

**What each tier should do:**

- **T1 Frontline:** A flameproof fitting with a missing bolt or open cover is not flameproof. Report it and make it safe the same shift.
- **T2 Supervision / shift in-charge:** Include Ex-equipment checks (bolts, covers, glands) in area rounds and record them by item, not as a group.
- **T3 Function management:** Set up a hazardous-area (Ex) inspection programme with item-level records and competent inspectors.
- **T4 Plant leadership:** Fund replacement of old HPMV fittings in zoned areas with certified LED fittings.

### LR-12: Control-room staff held emergency duties after a four-day general course, with no defined qualification or simulator practice

**Lesson.** If no qualification is defined for control-room operators, people are assigned to emergency duty after general training only, and a rare, time-critical event becomes their first practice, because rostering fills posts with whoever is available.

**Context.** Control-room training was a four-day general course, with no defined qualification in HR/Operations policy and no simulator practice; the committee recommended at least one month on simulators. The night-shift two-person crew had no member with practised emergency-isolation competence.

- **Owner:** F01 Operations & Control Room (co-owners: F12, F02). **Tiers:** T1, T2, T3, T4, T5.
- **HFACS:** L3 Supervision Inadequate (training and qualification). **Causal role:** contributory. **Barrier:** mitigation: competent emergency response.
- **Organisational system:** training and competence; staffing and fatigue. **Transferability:** industry-wide.
- **Evidence:** EVD-5634, EVD-1460, EVD-9220 (direct; confidence high). Supported by 24 findings.
- **Worst credible case:** Crew cannot execute the emergency response the plant relies on.

| Recommendation | HoC tier | Leading indicator |
|---|---|---|
| Define a control-room operator qualification with simulator-based emergency scenarios and a pass standard; make it a rostering prerequisite. | administrative | Share of control-room positions filled by qualified staff on each shift. |
| Deliver at least one month of simulator training (as the committee recommends) with annual emergency refreshers. | training | Simulator hours per operator per year; scenario pass rate. (Training supports, but does not replace, the engineering controls in LR-09 and LR-10.) |

**What each tier should do:**

- **T1 Frontline:** Ask for practice on the emergencies you are expected to handle. If you have never practised one, tell your supervisor.
- **T2 Supervision / shift in-charge:** Do not roster anyone alone on emergency duty who has not passed the emergency-response assessment for that unit.
- **T3 Function management:** Define a control-room qualification (knowledge, simulator scenarios, assessment, refresher interval).
- **T4 Plant leadership:** Require that every shift has at least one qualified emergency-competent person in each control room.
- **T5 Corporate / board:** Ask for control-room competence assurance (qualified share by site) as a standing board metric.

## Priority-2 and priority-3 learnings

| ID | P | Learning | Owner | HFACS | Findings | Recommendations (HoC) |
|---|---:|---|---|---|---:|---|
| LR-04 | 2 | The malfunction notification was never closed or reviewed, so the last administrative check before return to service did not happen | F08 Work Management & Planning | L3 | 15 | engineering; administrative |
| LR-13 | 2 | People saw the release first, but their warnings reached the control room late and diluted | F01 Operations & Control Room | L2 | 12 | engineering; administrative |
| LR-14 | 2 | One panning camera was the only view of the skid; it gave intermittent coverage and was lost seconds after ignition | F10 Security & Surveillance | L4 | 11 | engineering |
| LR-15 | 2 | Pressure transmitters at the leak point sent no data, and control-room clocks disagreed by up to 12 minutes | F04 Instrumentation, Control & Calibration | L4 | 15 | engineering; engineering |
| LR-16 | 2 | A calibration setting on the failed meter was changed and reversed without any record or checklist | F04 Instrumentation, Control & Calibration | L3 | 26 | administrative; engineering |
| LR-17 | 2 | Known pipe-wall loss was measured but not acted on: no corrective plan for three years, and painting used as the fix | F05 Asset Integrity, Corrosion & Inspection | L4 | 33 | engineering; administrative |
| LR-18 | 2 | The four-year thickness inspection cycle slipped to six years, and original baseline data and pipe schedules were missing | F05 Asset Integrity, Corrosion & Inspection | L4 | 17 | administrative |
| LR-19 | 2 | The metering P&ID was a lost original replaced by an unapproved vendor drawing that did not match the field | F07 Engineering, Design, Documents & MOC | L4 | 12 | administrative |
| LR-20 | 2 | Safety audits used generic checklists and recorded compliance without site data, so they could not find plant-specific defects | F11 HSE, Process Safety & Audit | L4 | 26 | administrative |
| LR-21 | 3 | External-audit recommendations were extended without the required approval, so overdue safety actions had no accountable owner | F13 Plant & Asset Leadership | L4 | 8 | engineering |
| LR-22 | 2 | Maintenance notifications were treated as work permits, permits went missing untracked, and job safety plans were absent | F11 HSE, Process Safety & Audit | L4 | 14 | engineering |
| LR-23 | 2 | Three of four diesel fire-water pumps were unavailable or unreliable; electric pumps happened to carry the incident | F09a Fire-fighting Operations & Fire-water Systems | L4 | 13 | administrative; engineering |
| LR-24 | 3 | Fire drill records held no actions or observations, so drills could not show whether readiness was improving | F11 HSE, Process Safety & Audit | L4 | 8 | administrative |
| LR-25 | 2 | The new control room had blast-proof walls but ordinary doors, in an area that filled with vapour | F07 Engineering, Design, Documents & MOC | L4 | 2 | engineering |

Full fields, finding IDs and tier messages for every learning are in `learnings-register.xlsx` and in the Detailed register tab of `organisation-learning-map.html`.

## What this analysis could not see

- The export is AI-assisted and the human review status is not confirmed (no finding is marked as user-edited).
- The ignition source is the committee's *probable* source (LR-11), not a proven one.
- LR-17, LR-18 and LR-25 concern conditions that did not cause this release; they are kept because they show the same pattern of known risks left open.
- Comparison with an official report has not been done (`comparison` = not compared).

---

> Generated with ProbeMatrix Learnings Coach (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
