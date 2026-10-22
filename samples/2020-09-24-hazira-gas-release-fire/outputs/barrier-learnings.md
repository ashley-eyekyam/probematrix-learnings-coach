# Barrier Learnings: Hazira gas terminal release and fire, 2020

**DRAFT**

Review: draft · Classification: internal · Version 1.0

Draft because: the investigation status is in progress; no finding is marked as edited by a person

*Learning purposes: not a statutory document; draft: the investigation status is in progress · Learnings drafted by an AI agent from AI-assisted findings*

*About 7 min read*

**Audience:** Site leaders, process safety and the barrier owners

**Incident:** Hazira gas terminal condensate release and fire · 2020-09-24

## Data quality and limits

- Draft learnings from an unreviewed analysis: the ProbeMatrix investigation status is in progress and no finding is marked as edited by a person. Validate before adoption.
- The export mentions regulator involvement but its summary sheet says 'Reportable to Regulator: No'. Confirm the reporting status with the organisation; this pack does not decide it.

## Bottom line

- The prevention barriers at the seal were missing rather than weak: no specification for the part, no test after the repair, no independent check of the job and no review of repeat failures. [FND-B56701CA; FND-50C7319E; FND-615DB819; FND-1A251687; EVD-8645; EVD-2894] *(evidence: corroborated; learning: LR-02)*
- On the mitigation side, detection, isolation and communication all acted, but too late: the release was seen at 02:15, the alarm sounded at 02:20 and the first valve was closed at 03:01. [FND-AEA16F83; FND-B5C0CE8F; EVD-6414; EVD-8657; EVD-4286] *(evidence: corroborated; learning: LR-09)*
- The decisive mitigation gaps were an isolation that needed people at the valve and a plan that gave no one the criteria or the authority to order it. [FND-044D1DEC; FND-82761CC5; EVD-3932; EVD-4052] *(evidence: corroborated; learning: LR-07)*
- Fire water worked on the night, carried by the electric pumps, while three of four diesel pumps were unavailable or unreliable. [FND-B955FBD6; EVD-2432] *(evidence: direct; learning: LR-23)*
- Eleven of the twelve fixes are above the administrative tier (two substitution, nine engineering); the one administrative fix, the plan's isolation criteria, is paired with remote isolation. [FND-82761CC5; FND-02310148] *(evidence: inferred)*

## Barriers

One item per barrier the top-rated findings mention, by side. States follow the five barrier states; supporting findings are the register learning's other top-rated findings.

### Prevention

**Barrier:** design and specification (substitution of parts) [FND-B56701CA; FND-23139BF9; FND-8CE00707; EVD-8645]
- Failure mode: The original gasket specification for the 1986 meter was not on file and no role owned it, so locally bought O-rings with no specification or quality check were the regular substitute (L4).
- Type: procedural
- State on the day: absent
- Owner: Mechanical Maintenance (F02, T3)
- Control tier: substitution
- Fix: Re-establish the seal design (manufacturer data or an engineered equivalent), stock only certified parts against it and quarantine non-conforming seals.
- Leading indicator: Share of critical pressure-boundary spares with a specification and certificate on file.

*(evidence: corroborated; +28 supporting; learning: LR-01)*

**Barrier:** maintenance and testing (testing after maintenance) [FND-50C7319E; FND-5919B328; FND-3AB996FC; EVD-2894; EVD-0185]
- Failure mode: No procedure required a test to design pressure before a high-pressure meter returned to service; the replaced joint was pressurised to operating pressure only (L4, L3).
- Type: procedural
- State on the day: absent
- Owner: Mechanical Maintenance (F02, T3)
- Control tier: engineering
- Fix: Configure the work-order system so a pressure-boundary job cannot be closed, or the equipment released to operations, until a test result and witness are entered.
- Leading indicator: Share of pressure-boundary jobs closed with a recorded test result and witness; attempted closures blocked for missing test data.

*(evidence: direct; +21 supporting; learning: LR-02)*

**Barrier:** competence and staffing (independent verification) [FND-615DB819; FND-F8C125D5; FND-63B6D260; EVD-2894; EVD-5105]
- Failure mode: The seal job of 18 September 2020 was manned with no independent quality-control role, test witness or closing supervisor, and no job safety analysis (L4, L3).
- Type: procedural
- State on the day: absent
- Owner: Work Management & Planning (F08, T3)
- Control tier: engineering
- Fix: Add a safety-critical category to work planning that automatically adds inspection, test-witness and close-out steps signed by someone other than the performer.
- Leading indicator: Share of safety-critical jobs with every verification step signed by someone other than the performer.

*(evidence: corroborated; +4 supporting; learning: LR-03)*

**Barrier:** inspection and integrity (repeat failures on ageing equipment) [FND-1A251687; FND-82FC718D; FND-D14B8424; EVD-1494; EVD-0591]
- Failure mode: Repeat seal failures on the same meter were treated as routine repairs; no reliability role, root-cause review or repair-or-replace decision existed (L4, L3).
- Type: procedural
- State on the day: absent
- Owner: Mechanical Maintenance (F02, T3)
- Control tier: engineering
- Fix: Set an automatic repeat-failure trigger in the maintenance system that opens a root-cause task, and record a repair-or-replace decision for each repeat item.
- Leading indicator: Repeat-failure items flagged per quarter and the share with a completed root-cause analysis.

*(evidence: direct; +11 supporting; learning: LR-05)*

**Barrier:** change management (MOC) [FND-F7FE8463; FND-5A5F6AB3; EVD-2986; EVD-8645]
- Failure mode: The MOC procedure was published in August 2016 but not used after 2018, so the seal substitution never reached an engineering review (L4).
- Type: procedural
- State on the day: defeated
- Owner: Engineering, Design, Documents & MOC (F07, T3)
- Control tier: engineering
- Fix: Build an MOC trigger into the work-order and stores issue screens: a non-catalogue or substitute part needs an MOC reference.
- Leading indicator: MOCs raised per month, and the share of substitute-part issues with an MOC reference.

*(evidence: direct; +1 supporting; learning: LR-06)*

**Barrier:** inspection and integrity (acting on inspection results) [FND-C6992EAF; FND-ABDADA0C; EVD-5527; EVD-2397]
- Failure mode: Wall loss was measured but not acted on: no corrective plan three years after the 2017 report, and painting used for pitting found in July 2019 (L4, L3).
- Type: procedural
- State on the day: degraded
- Owner: Asset Integrity, Corrosion & Inspection (F05, T3)
- Control tier: engineering
- Fix: Carry out fitness-for-service assessments on the recorded wall-loss locations and repair, re-rate or replace as they require.
- Leading indicator: Open wall-loss findings without a fitness-for-service decision.

*(evidence: direct; learning: LR-17)*

### Mitigation

**Barrier:** ignition control (hazardous-area equipment) [FND-1280E788; FND-675D99DD; FND-0B35D995; EVD-6916; EVD-9999]
- Failure mode: A flame-proof lamp in the hazardous area had three bolts missing and its glass case open, under a breakdown-led electrical maintenance practice; the findings name it as the probable ignition source (L4, L3).
- Type: passive
- State on the day: degraded
- Owner: Electrical Maintenance (F03, T3)
- Control tier: substitution
- Fix: Replace the legacy flame-proof lamps in zoned areas with certified, lower-surface-temperature fittings, inspected under a risk-based programme.
- Leading indicator: Share of zoned-area light fittings replaced with certified fittings; inspection completion against plan.

*(evidence: direct; +9 supporting; learning: LR-11)*

**Barrier:** detection and alarm [FND-6155A1C2; FND-01C3DE98; FND-B5C0CE8F; EVD-3452; EVD-8657; EVD-4286]
- Failure mode: Gas detection lit an annunciator but started no shutdown or suppression, and it alarmed about 5 minutes after security staff saw the cloud (L4, L2).
- Type: active
- State on the day: worked partly
- Owner: Instrumentation, Control & Calibration (F04, T3)
- Control tier: engineering
- Fix: Add confirmed-gas voting logic that starts emergency shutdown and isolation automatically in the metering and gas terminal areas.
- Leading indicator: Share of major-release areas covered by automatic fire and gas action; proof-test records.

*(evidence: corroborated; +11 supporting; learning: LR-10)*

**Barrier:** isolation and shutdown (remote isolation) [FND-044D1DEC; FND-02310148; FND-AEA16F83; EVD-3932; EVD-9612; EVD-6414]
- Failure mode: The emergency isolation valves could be closed only by hand at the valve, inside the area the vapour made unreachable; the first was closed 46 minutes after the leak was first detected (L4, L2).
- Type: active
- State on the day: worked partly
- Owner: Operations & Control Room (F01, T3)
- Control tier: engineering
- Fix: Convert the gas terminal emergency isolation valves to remotely operated shutdown valves, operable from the control room and a safe second location.
- Leading indicator: Share of identified emergency isolation points with remote operation; shutdown valve proof-test pass rate.

*(evidence: corroborated; +13 supporting; learning: LR-09)*

**Barrier:** emergency command and decision authority [FND-82761CC5; FND-446A7956; FND-D1DF4895; EVD-4052; EVD-3932]
- Failure mode: The on-site disaster management plan named hydrocarbon leakage but gave no isolation or stoppage criteria and no delegated authority, so the decision travelled up the night-shift chain (L4).
- Type: procedural
- State on the day: absent
- Owner: Emergency Planning & Command (F09b, T3)
- Control tier: administrative
- Fix: Write isolation and stoppage criteria, valve lists and delegated authority down to control-room shift level into the plan, paired with the remote isolation above so the decision can be carried out from a safe place.
- Leading indicator: Share of release scenarios in the plan with written criteria, valves and authority; time to isolate in night-shift drills.

*(evidence: corroborated; +18 supporting; learning: LR-07)*

*Language check JC6 accepted: the written criteria and delegated authority are the system fix at the plan level (L4); the engineering control they pair with is the remote isolation barrier in this section*

**Barrier:** communication and escalation [FND-2F736E5F; FND-37BC45CF; EVD-8871; EVD-1460]
- Failure mode: Security staff saw the release first, but their reports went through the CCTV control room and reached the gas terminal control room as 'some vapour cloud or steam leakage' (L4, L2).
- Type: procedural
- State on the day: worked partly
- Owner: Operations & Control Room (F01, T2)
- Control tier: engineering
- Fix: Install a direct line from the perimeter posts and the CCTV room to each process control room, with a manual call point at the watch towers.
- Leading indicator: Time from first detection to control-room notification in joint drills.

*(evidence: corroborated; learning: LR-13)*

**Barrier:** fire-water and fire protection [FND-B955FBD6; FND-DF7337F2; EVD-2432]
- Failure mode: Tank level and fire-water header pressure stayed healthy and the electric pumps carried the fire cooling. Latent: three of four diesel pumps were under maintenance or tripping, with the cause not recorded (L4).
- Type: active
- State on the day: worked
- Owner: Fire-fighting Operations & Fire-water Systems (F09a, T3)
- Control tier: engineering
- Fix: Diagnose the tripping fault, restore the diesel pumps, and hold them to a performance standard with regular run tests and a maximum allowed outage.
- Leading indicator: Diesel fire-pump availability and test pass rate.

*(evidence: direct; learning: LR-23)*

## Summary

The weight sat on the prevention side. Five of the six prevention barriers were absent or bypassed at the seal: the specification, the test after maintenance, the independent check, the repeat-failure review and change management [FND-23139BF9; FND-50C7319E; FND-615DB819; FND-82FC718D; FND-F7FE8463]. Any one of them could have stopped an unspecified, untested joint going back into service. [FND-23139BF9; FND-50C7319E; FND-615DB819; FND-82FC718D; FND-F7FE8463] *(evidence: inferred)*

On the mitigation side, detection, isolation and communication acted only late or in part, the isolation criteria were absent and the ignition barrier was degraded. Detection informed but did not act [FND-6155A1C2], isolation needed people at the valve [FND-044D1DEC], and the plan gave no isolation criteria [FND-446A7956]. A damaged flame-proof lamp was the probable ignition source [FND-675D99DD]. Fire water was the one barrier that worked, with a latent weakness in the diesel pumps [FND-B955FBD6]. [FND-6155A1C2; FND-044D1DEC; FND-446A7956; FND-675D99DD; FND-B955FBD6] *(evidence: corroborated)*

The fixes are strong: two substitution and nine engineering, and one administrative change that is itself the system fix for the plan. In the register, training appears only paired with another change (LR-06, LR-07, LR-08, LR-12), never alone [FND-82761CC5; FND-337CB67F]. [FND-82761CC5; FND-337CB67F] *(evidence: inferred)*

## Critical controls to verify first

Ranked. Each was the main or the last line between the hazard and the outcome in the findings.

- [ ] Remote or automatic isolation of the gas terminal and metering lines: confirm each emergency isolation point can be closed from the control room or a safe place, and proof-test it. [FND-044D1DEC; FND-02310148; EVD-3932] *(Clauses: ICMM-CCM-8)*
- [ ] **Hold point:** Test after pressure-boundary maintenance: sample recent jobs for a recorded test to the written test pressure and an independent witness before return to service. [FND-50C7319E; FND-5919B328; EVD-2894] *(Clauses: ICMM-CCM-8)*
- [ ] Specification control for pressure-boundary seals: for every legacy pressure item, confirm a specification is on file and stores issue only against it. [FND-B56701CA; FND-23139BF9; EVD-8645] *(Clauses: ICMM-CCM-8)*
- [ ] Isolation criteria and delegated authority: confirm the emergency plan says who may isolate, on what criteria, on the night shift, and that drills test it. [FND-82761CC5; FND-446A7956; EVD-4052] *(Clauses: ICMM-CCM-8, SEVESO-AnnexIII(vi))*
- [ ] Fire and gas detection: confirm what each detector does on confirmed gas, and that alarms are historised and tested. [FND-6155A1C2; FND-01C3DE98; EVD-3452] *(Clauses: ICMM-CCM-8)*
- [ ] Hazardous-area electrical equipment: inspect the flame-proof fittings in zoned areas item by item and record each one's condition. [FND-1280E788; FND-0B35D995; EVD-6916] *(Clauses: ICMM-CCM-8, ICMM-CCM-9)*
- [ ] Repeat-failure response: confirm a second failure of the same pressure item opens a root-cause review, and that the result is acted on. [FND-1A251687; FND-D14B8424; EVD-1494] *(Clauses: ICMM-CCM-9, SEVESO-AnnexIII(vi))*

## Limits of this pack

- No organisation barrier register was supplied, so no barrier carries a barrier_id and the unmapped table is left out.
- Competence for emergency duty (LR-12) and the drill records (LR-24) are treated in the register; they support the emergency command barrier here rather than standing as barriers of their own.

## Supporting citations

- Barriers › 1: FND-8C0BB623; FND-7A32AC87; FND-89962239; FND-B356F15B; FND-91B45FF9; FND-DA67926D; FND-54180594; FND-82673283; FND-45363DCA; FND-A2048FB8; FND-FFE174D0; FND-A443D288; FND-72A7D26C; FND-CEE4B00B; FND-3746C7B6; FND-42BEF461; FND-D66ACA7B; FND-852B7EC7; FND-DEAA7F90; FND-A3D7D53F; FND-B86F67F0; FND-D40839C1; FND-BC4FD086; FND-EBB66554; FND-B440C1BF; FND-6B3A6492; FND-A0017E28; FND-DE30BD8B
- Barriers › 2: FND-7C5ED5B3; FND-FD617187; FND-212DC9B7; FND-15279F97; FND-7FA02383; FND-4944554C; FND-FDFA6FF5; FND-1662466D; FND-9174A5B0; FND-611A8BFC; FND-904FCA63; FND-C34A026C; FND-257C1100; FND-137BC719; FND-8ACDE078; FND-C4E06264; FND-86CB3683; FND-491EDE74; FND-B91D4A23; FND-7A10FF70; FND-71EE9734
- Barriers › 3: FND-2FAB8D51; FND-A6312B6B; FND-28F8790B; FND-59A2F497
- Barriers › 4: FND-8DA35CA9; FND-69067A1C; FND-71D631C1; FND-CEE3D4D7; FND-110F964C; FND-4EDE038A; FND-AC9A1E69; FND-FEC84761; FND-3A34BAD3; FND-E0AE86A6; FND-55F68376
- Barriers › 5: FND-8083ECAC
- Barriers › 7: FND-784A23E4; FND-74A80D24; FND-C7F16268; FND-554BFB4A; FND-1D61DC3A; FND-ADC25F29; FND-5E08D0F8; FND-ABF11182; FND-CCE6F868
- Barriers › 8: FND-A245072B; FND-94C28ACE; FND-9399FA02; FND-D45021AD; FND-4D7CF773; FND-119E6CF7; FND-5BC96E8A; FND-2D90823E; FND-4458E0C0; FND-5897D1E4; FND-15B4E60F
- Barriers › 9: FND-4C645CB5; FND-31405D96; FND-A7137BC4; FND-DE978BF5; FND-DBE08E73; FND-7D28BE30; FND-05841EDA; FND-322112EE; FND-6DB250E6; FND-9B406A83; FND-01ADF0AA; FND-594A80E9; FND-BDD73BA2
- Barriers › 10: FND-314D34C5; FND-DE132C95; FND-AE629313; FND-81E3EEA0; FND-500E0B2D; FND-8DAFDADC; FND-7505B1AF; FND-2EC435D0; FND-BB4CC662; FND-D4A3EF8A; FND-4F687CC5; FND-7A2429CE; FND-33D32D4C; FND-DF1144C3; FND-730D0DCA; FND-6472CD15; FND-E009D26B; FND-5C7B163D

---

This pack cites 143 of 150 relevant findings.

143 of 150 top-rated relevant findings cited.

> Generated with ProbeMatrix Learnings Coach v2.0.0a5 (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
