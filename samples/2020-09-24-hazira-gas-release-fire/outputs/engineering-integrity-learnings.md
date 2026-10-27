# Engineering and Integrity Learnings: Gas terminal release and fire, 2020

**DRAFT**

Review: draft · Classification: internal · Version 1.0

Draft because: the investigation status is in progress; no finding is marked as edited by a person

*Learning purposes: not a statutory document. Derived from a ProbeMatrix investigation export; learnings are evidence-linked but should be validated by the organisation before adoption. Draft learnings: the investigation status is in progress. · Learnings drafted by an AI agent from AI-assisted findings*

*About 11 min read*

**Audience:** Engineering, asset integrity, instrumentation, electrical and management-of-change functions, and the technical authority

**Incident:** Hazira gas terminal condensate release and fire · 2020-09-24

## Data quality and limits

- Draft learnings from an unreviewed analysis: the export's investigation status is in progress and no finding is marked as edited by a person. Validate every item before adoption.

## Bottom line

- The release came from a seal fitted with no specification and returned to service without a test to design pressure; neither condition had an engineering owner. [FND-72A7D26C; FND-137BC719; EVD-8645; EVD-2894] *(learning: LR-01)*
- The management-of-change procedure existed but was not used, so the substitution had no review. [FND-F7FE8463; EVD-2986] *(learning: LR-06)*
- Detection only informed and the isolation valves were local-only: the design left the response to people who could not reach the valves. [FND-01C3DE98; FND-322112EE; EVD-8657; EVD-9612] *(learning: LR-09)*
- The probable ignition source was a flameproof lamp with missing bolts, under breakdown-led electrical maintenance. [FND-CCE6F868; EVD-6916] *(learning: LR-11)*
- Integrity warnings and drawings were recorded but not acted on or approved; the records themselves need owners. [FND-30D45EFE; FND-583EB5FE; EVD-5527; EVD-0933] *(learning: LR-17)*

## Technical learnings by theme

### Specification and substitution of parts

**Learning:** If the specification for a pressure-boundary part is lost and no function owns re-establishing it, a substitute part becomes normal practice. [FND-72A7D26C; FND-FFE174D0; FND-B56701CA; EVD-8645]

The 1986 meter was built for a rectangular-slot gasket. Its original specification was not on file, and no material specification or procurement policy existed for these gaskets, so locally bought O-rings were fitted as regular practice. The condition persisted because no function owned the specification or the approval of a substitute.

- Owner: Technical authority (engineering function)

*(evidence: corroborated; +7 supporting; learning: LR-01)*

**Barrier:** Pressure-boundary integrity: the correct seal to a written specification [FND-72A7D26C; FND-D40839C1; EVD-8645]
- Failure mode: No specification on file and no approved substitute, so a non-specified O-ring was fitted as regular practice.
- Type: prevention
- State on the day: absent
- Owner: Technical authority (engineering function)
- Control tier: substitution
- Fix: Re-establish the seal specification and stock only certified parts against it.
- Leading indicator: % of critical pressure-boundary spares with a specification on file

*(learning: LR-01)*

**Recommendation:** Route: technical query. Re-establish the seal design for the meter flange from the maker's data or an engineered equivalent, and quarantine non-conforming seals. [FND-FFE174D0; FND-B56701CA; EVD-8645]
- Control tier: substitution
- Barrier: Pressure-boundary integrity: the correct seal
- Owner: Technical authority (engineering function)
- Leading indicator: % of critical pressure-boundary spares with a specification and certificate on file

*(learning: LR-01)*

### Testing after maintenance

**Learning:** If no standard defines the test for a high-pressure joint before return to service, the quickest available check becomes the test, and a weak joint passes. [FND-137BC719; FND-8ACDE078; FND-7A10FF70; EVD-2894; EVD-0185]

After the gasket change on 18 Sep 2020 the system was only pressurised to operating pressure; no hydro test to design pressure was done, and there was no procedure for calibration or return to service of these high-pressure meters. The metering-skid workspace had no specifications, procedures or checklists.

- Owner: Technical authority (engineering function)

*(evidence: direct; learning: LR-02)*

**Barrier:** Return-to-service pressure test [FND-137BC719; FND-8ACDE078; EVD-2894]
- Failure mode: No procedure required a test to design pressure, so pressurising to operating pressure was taken as proof of the joint.
- Type: prevention
- State on the day: absent
- Owner: Technical authority (engineering function)
- Control tier: administrative
- Fix: A return-to-service standard that sets the test, the test pressure and the witness, enforced in the work-order system.
- Leading indicator: % of pressure-boundary jobs closed with a recorded test result and witness

*(learning: LR-02)*

*Language check JC6 accepted: A pressure test is a procedural barrier by nature; its tier is stated honestly, and the engineering enforcement is the recommendation beside it.*

**Recommendation:** Route: MOC. Configure the work-order system so a pressure-boundary job cannot be closed, or the equipment released, until a test result against the technical authority's return-to-service standard is entered. [FND-7A10FF70; FND-8ACDE078; EVD-2894]
- Control tier: engineering
- Barrier: Return-to-service pressure test
- Owner: Technical authority (engineering function)
- Leading indicator: Attempted closures blocked for missing test data, trending to zero

*(learning: LR-02)*

### Change management

**Learning:** A management-of-change procedure that is published but never triggered lets changes in parts and materials through without review. [FND-F7FE8463; FND-8083ECAC; FND-ADF96860; EVD-2986; EVD-8645]

The procedure was published in August 2016, but no change had been taken through it since 2018. The switch from the maker's gasket to locally bought O-rings had no change review, and people did not recognise a like-for-unlike replacement as a change.

- Owner: Technical authority (engineering function)

*(evidence: direct; +9 supporting; learning: LR-06)*

**Barrier:** Management of change [FND-8083ECAC; FND-ADF96860; EVD-2986]
- Failure mode: The procedure existed on paper but was not used; the substitution had no risk review.
- Type: prevention
- State on the day: absent
- Owner: Technical authority (engineering function)
- Control tier: administrative
- Fix: A trigger in the stores and work-order systems that asks for a change reference for any substitute part.
- Leading indicator: Change reviews raised per month; a long run of zero is a warning

*(learning: LR-06)*

*Language check JC6 accepted: Change review is a management-system barrier; its tier is stated honestly, and the engineering trigger is the recommendation beside it.*

**Recommendation:** Route: MOC. Build a change-review trigger into the work-order and stores issue screens, so a non-catalogue or substitute part needs a change reference before it is issued. [FND-F7FE8463; EVD-2986]
- Control tier: engineering
- Barrier: Management of change
- Owner: Technical authority (engineering function)
- Leading indicator: % of substitute-part issues with a change reference

*(learning: LR-06)*

### Emergency isolation design

**Learning:** Emergency isolation valves that can only be worked at the valve are out of reach in the event they exist for. [FND-7D28BE30; FND-02310148; FND-322112EE; EVD-3932; EVD-9612]

The gas terminal emergency valves were supplied as local-manual valves with no remote operation from the control room, and were never upgraded. The vapour cloud kept people away, and the first valve was closed by hand once the shift in-charge reached it.

- Owner: Technical authority (engineering function)

*(evidence: corroborated; +4 supporting; learning: LR-09)*

**Barrier:** Emergency isolation of the gas terminal inventory [FND-7D28BE30; FND-322112EE; EVD-9612]
- Failure mode: Isolation needed a person at the valve, inside the area the release made unreachable.
- Type: mitigation
- State on the day: defeated
- Owner: Technical authority (engineering function)
- Control tier: engineering
- Fix: Remote-operated emergency isolation, worked from the control room and a safe secondary location.
- Leading indicator: % of identified emergency isolation points with remote operation

*(learning: LR-09)*

**Recommendation:** Route: MOC. Convert the gas terminal emergency isolation valves to remotely operated emergency shutdown valves, worked from the control room and a safe secondary location. [FND-02310148; EVD-3932]
- Control tier: engineering
- Barrier: Emergency isolation of the gas terminal inventory
- Owner: Technical authority (engineering function)
- Leading indicator: % of identified emergency isolation points with remote operation; valve proof-test pass rate

*(learning: LR-09)*

### Hazardous-area equipment integrity

**Learning:** If electrical maintenance in hazardous areas answers breakdowns instead of inspecting explosion protection, defects that do not stop the equipment working stay in service. [FND-ADC25F29; FND-1D61DC3A; FND-CCE6F868; EVD-6916; EVD-9999]

A flameproof lamp at the skid had three bolts missing and its glass case open; the committee named it the probable ignition source. Electrical maintenance leaned towards breakdown work with little systematic inspection, and the post-incident audit grouped all nine lamps under one status. The ignition source is probable, not proven.

- Owner: Electrical engineering function

*(evidence: direct; +10 supporting; learning: LR-11)*

**Barrier:** Ignition control: flameproof integrity of lighting in the hazardous area [FND-CCE6F868; FND-1D61DC3A; EVD-6916; EVD-0496]
- Failure mode: A flameproof fitting with missing bolts and an open case stayed in service without inspection.
- Type: prevention
- State on the day: defeated
- Owner: Electrical engineering function
- Control tier: substitution
- Fix: Certified replacement fittings, and an inspection programme for explosion-protected equipment with records for each item.
- Leading indicator: % of zoned-area fittings with an item-level inspection record in the current cycle

*(learning: LR-11)*

**Recommendation:** Route: MOC. Replace the old high-pressure mercury vapour flameproof lamps in zoned areas with certified fittings with a lower surface temperature. [FND-ADC25F29; EVD-6916]
- Control tier: substitution
- Barrier: Ignition control: flameproof integrity of lighting
- Owner: Electrical engineering function
- Leading indicator: % of zoned-area luminaires replaced with certified fittings

*(learning: LR-11)*

### Inspection and corrosion programmes

**Learning:** If inspection results are recorded but nobody owns turning them into a decision, the organisation knows about degradation and keeps operating with it. [FND-ABDADA0C; FND-154134EA; FND-30D45EFE; FND-C4842890; EVD-2397; EVD-5527; EVD-8307]

Wall loss found in 2017 had no corrective plan three years later; pitting found in July 2019 on a zero-corrosion-allowance 36-inch line was treated by painting, with no fitness-for-service review; the four-year thickness schedule slipped. These lines did not cause this release: the learning is about how integrity warnings are handled.

- Owner: Asset integrity function

*(evidence: direct; +10 supporting; learning: LR-17)*

**Barrier:** Thickness monitoring and corrective action [FND-0F19C9FC; FND-B412FF47; FND-C4842890; EVD-5527; EVD-2397; EVD-8307]
- Failure mode: Measurements were taken but not turned into corrective plans or fitness-for-service decisions, and the inspection schedule slipped.
- Type: prevention
- State on the day: degraded
- Owner: Asset integrity function
- Control tier: engineering
- Fix: A fitness-for-service decision for every wall-loss finding, tracked to closure, with inspection due dates that escalate when overdue.
- Leading indicator: Open wall-loss findings without a fitness-for-service decision

*(learning: LR-17)*

**Recommendation:** Route: technical query. Carry out fitness-for-service assessments on the 2017 and July 2019 wall-loss locations, and repair, re-rate or replace as the technical authority decides. [FND-ABDADA0C; FND-30D45EFE; EVD-2397; EVD-5527]
- Control tier: engineering
- Barrier: Thickness monitoring and corrective action
- Owner: Technical authority (engineering function)
- Leading indicator: Open wall-loss findings without a fitness-for-service decision, reviewed monthly

*(learning: LR-17)*

### Documents and as-built records

**Learning:** If drawings drift from the field and vendor drawings are not approved, maintenance and emergency isolation are planned from a picture that is wrong. [FND-583EB5FE; FND-82687B50; FND-A1F9AC94; EVD-0933]

The original metering drawings were lost; a vendor prepared replacements that were not checked or approved, and the valve and meter configuration on them did not match the field. No function owned keeping the as-built record true.

- Owner: Engineering document control

*(evidence: direct; +9 supporting; learning: LR-19)*

**Barrier:** Controlled as-built drawings [FND-583EB5FE; FND-A1F9AC94; EVD-0933]
- Failure mode: An unapproved vendor drawing that did not match the field was the only drawing in use.
- Type: prevention
- State on the day: degraded
- Owner: Engineering document control
- Control tier: administrative
- Fix: Field-verified, approved drawings for safety-critical systems, with approval required for every vendor drawing.
- Leading indicator: % of safety-critical drawings field-verified and approved

*(learning: LR-19)*

*Language check JC6 accepted: Drawing control is a records barrier; no stronger tier applies to keeping a drawing true to the field.*

**Recommendation:** Route: engineering standard revision. Require operator checking and approval of every vendor drawing before it is controlled, and field-verify and re-issue the gas terminal drawings, starting with metering and emergency isolation. [FND-82687B50; EVD-0933]
- Control tier: administrative
- Barrier: Controlled as-built drawings
- Owner: Engineering document control
- Leading indicator: % of safety-critical drawings field-verified and approved; vendor drawings in use without approval
- Why not stronger: Drawing control is a records process; no engineering control replaces checking a drawing against the field.

*(learning: LR-19)*

*Language check JC6 accepted: The document-control standard is the system fix for this L3/L4 records gap; no stronger tier applies.*

## Alarms and automation

From the 48 findings coded to the technological environment (PTE): how detection, automatic action and the control-room displays shaped what operators could see and do.

### Detection, alarm and shutdown design

**Learning:** If fire and gas detection is designed to inform rather than act, every protective action waits on people noticing, checking and deciding. [FND-119E6CF7; FND-4D7CF773; FND-01C3DE98; EVD-3452; EVD-8657]

The hydrocarbon and H2S detectors were configured to the annunciator panel only, with no history in the control system and no automatic shutdown or suppression. No policy required the interlock, and the system was never upgraded, so the first alarm came after people had already seen the cloud.

- Owner: Technical authority (engineering function)

*(evidence: corroborated; +10 supporting; learning: LR-10)*

**Barrier:** Fire and gas detection with automatic executive action [FND-01C3DE98; FND-119E6CF7; EVD-8657]
- Failure mode: Detection lit an annunciator only: no shutdown, isolation or suppression, and no signal history.
- Type: mitigation
- State on the day: worked partly
- Owner: Instrumentation and control engineering
- Control tier: engineering
- Fix: Confirmed-gas logic that starts isolation, and deluge where designed, with every detector signal kept in history.
- Leading indicator: % of major-release areas covered by automatic executive action

*(learning: LR-10)*

**Recommendation:** Route: MOC. Implement confirmed-gas logic that starts isolation by itself (and deluge where designed) in the metering and gas terminal areas, and keep every detector signal in history. [FND-4D7CF773; EVD-3452]
- Control tier: engineering
- Barrier: Fire and gas detection with automatic executive action
- Owner: Instrumentation and control engineering
- Leading indicator: % of detectors with signal history; proof-test and spurious-trip records reviewed each quarter

*(learning: LR-10)*

### Process signals at the control-room display

**Learning:** If transmitters at a leak point send nothing to the control system and its clocks disagree, operators lose the pressure trend that could show a leak, and the sequence has to be rebuilt afterwards from other records. [FND-2B5C46B9; FND-4108DB15; FND-EE34220F; EVD-6470; EVD-5532]

Three pressure transmitters on the metering lines were shown on the drawing but had no data in the control system, so operators had no pressure trend at the source. Clocks across the control rooms differed by 2 to 12 minutes, so times on the day had to be taken from the camera and witness statements.

- Owner: Instrumentation and control engineering

*(evidence: corroborated; +2 supporting; learning: LR-15)*

**Barrier:** Pressure monitoring at the leak point, shown and kept in the control system [FND-6163C9EB; FND-0C37BB1E; EVD-6470; EVD-5532]
- Failure mode: Transmitters on the drawing delivered no data, so no trend or alarm on pressure was possible, and the control-room clocks disagreed.
- Type: mitigation
- State on the day: absent
- Owner: Instrumentation and control engineering
- Control tier: engineering
- Fix: Live, retained data from every transmitter on the drawing, an alarm on pressure loss, and one time source for all control-system clocks.
- Leading indicator: % of safety-relevant transmitters on the drawings with live, retained data

*(learning: LR-15)*

**Recommendation:** Route: MOC. Connect the metering-line pressure transmitters to the control system with signal history and an alarm on pressure loss, and set every control-system clock to one time source. [FND-2B5C46B9; FND-0C37BB1E; EVD-6470; EVD-5532]
- Control tier: engineering
- Barrier: Pressure monitoring at the leak point
- Owner: Instrumentation and control engineering
- Leading indicator: Transmitters with live, retained data; the clock offset between control rooms, checked each month

*(learning: LR-15)*

## Engineering decisions pending

Options only: the technical authority settles these. No engineering value is set here beyond what the cited records state.

**Decision:** What test, and what test pressure, must a joint on these high-pressure meters pass after pressure-boundary work before it returns to service? [FND-137BC719; EVD-2894]
- Options: A hydro test to design pressure; Another test method the technical authority approves; A change to the joint design that allows a different test
- Trade-offs: The cited records show only that operating pressure was used and a hydro test to design pressure was not; the test values are for the technical authority to set.
- Owner: Technical authority (engineering function)

*(learning: LR-02)*

**Decision:** How is the seal for the 1986 meter flange to be specified, and is a substitute acceptable? [FND-D40839C1; EVD-8645]
- Options: Recover the original maker's specification; Approve an engineered equivalent; Replace the meter with one that can be kept to specification
- Trade-offs: Recovering the maker's data may not be possible for equipment of this age; replacement removes the problem but takes longer.
- Owner: Technical authority (engineering function)

*(learning: LR-01)*

**Decision:** Is the pitted zero-corrosion-allowance section of the 36-inch line fit for service after painting? [FND-ABDADA0C; EVD-2397]
- Options: Repair; Re-rate; Replace
- Trade-offs: The record gives the measured loss and the design thickness with zero corrosion allowance, and asks whether painting suffices; it gives no fitness-for-service result.
- Owner: Technical authority (engineering function)

*(learning: LR-17)*

**Decision:** Which executive actions should confirmed gas detection start in the metering and gas terminal areas, and on what voting logic? [FND-4D7CF773; EVD-3452]
- Options: Isolation only; Isolation and deluge where designed; Alarm with remote manual isolation from the control room
- Trade-offs: Automatic action shortens the response but needs voting logic to limit spurious trips.
- Owner: Technical authority (engineering function)

*(learning: LR-10)*

**Decision:** Which emergency isolation valves become remotely operated, and from where? [FND-02310148; EVD-3932]
- Options: From the control room; From the control room and a safe secondary location; Automatically on confirmed gas, with remote override
- Trade-offs: The records show the valves were local-only and unreachable; the choice of location depends on where a release could deny access.
- Owner: Technical authority (engineering function)

*(learning: LR-09)*

**Decision:** How is the thickness inspection schedule restored, and what serves as the baseline where the original data is lost? [FND-C048B355; FND-C4842890; EVD-8287; EVD-8307]
- Options: Restore the laid-down four-year schedule; Set a risk-based interval; Use the first surviving measurements as the baseline
- Trade-offs: Most pipes have only two measurements on file, which limits any corrosion-rate estimate.
- Owner: Asset integrity function

*(learning: LR-18)*

## Data and records

- [ ] A specification reference for the part is on file, with any approved substitute recorded. *(before a pressure-boundary part is bought or issued)* [FND-72A7D26C; EVD-8645] *(learning: LR-01)*
- [ ] The test record shows the test, the test pressure, the result and the witness. *(at return to service after pressure-boundary work)* [FND-8ACDE078; EVD-2894] *(learning: LR-02)*
- [ ] Every setting change, including one reversed, is recorded with as-found and as-left values on a checklist. *(during and after calibration of a critical meter)* [FND-4B8F9B10; FND-D58142C9; EVD-2506] *(learning: LR-16)*
- [ ] The drawing is approved and matches the field configuration. *(before a drawing is used to plan work or an isolation)* [FND-A1F9AC94; EVD-0933] *(learning: LR-19)*
- [ ] Every fire and gas detector signal is kept in history in the control system. *(in operation)* [FND-789D5D60; EVD-8657] *(learning: LR-10)*
- [ ] Every pressure transmitter shown on the drawing delivers live, retained data, and control-system clocks agree. *(in operation)* [FND-0FFC03BB; FND-D9A35E88; EVD-6470; EVD-5532] *(learning: LR-15)*
- [ ] The baseline and each measurement are recorded, with the corrective decision for every loss found. *(at each thickness survey)* [FND-F696F4E0; FND-C048B355; EVD-8287] *(learning: LR-18)*
- [ ] Each fitting has its own record of condition, not one status for a group. *(at each inspection of hazardous-area electrical equipment)* [FND-02C51A67; FND-30EC643B; EVD-9999; EVD-0496] *(learning: LR-11)*

## Limits of this pack

- The barriers here are written in this pack because barrier-learnings has not been run for this sample; barrier-learnings is the next step, and should become their source.
- The ignition source is probable, not proven, and the wall-loss lines did not cause this release.

## Supporting citations

- Technical learnings by theme › 1: FND-45363DCA; FND-42BEF461; FND-D40839C1; FND-BC4FD086; FND-23139BF9; FND-B440C1BF; FND-DE30BD8B
- Technical learnings by theme › 7: FND-5A5F6AB3; FND-CDE8E62D; FND-07080447; FND-6ECCE231; FND-EB48C68C; FND-9F8CA896; FND-3FEE59DF; FND-922A04DB; FND-EEC2407A
- Technical learnings by theme › 10: FND-A7137BC4; FND-DE978BF5; FND-DBE08E73; FND-05841EDA
- Technical learnings by theme › 13: FND-784A23E4; FND-74A80D24; FND-C7F16268; FND-554BFB4A; FND-0B35D995; FND-5E08D0F8; FND-675D99DD; FND-1280E788; FND-ABF11182; FND-76BE46EF
- Technical learnings by theme › 16: FND-98A4D631; FND-6D307E93; FND-5EC15274; FND-47B1702F; FND-E5C4209D; FND-C6992EAF; FND-B2B200D4; FND-1F685360; FND-B5D6A73E; FND-256214D9
- Technical learnings by theme › 19: FND-72DCEE68; FND-D25BF914; FND-9D19BE37; FND-99B3F80E; FND-733F5A1A; FND-6710C6BA; FND-73312E54; FND-83AD4621; FND-107C8238
- Alarms and automation › 1: FND-A245072B; FND-94C28ACE; FND-9399FA02; FND-D45021AD; FND-5BC96E8A; FND-2D90823E; FND-6155A1C2; FND-4458E0C0; FND-5897D1E4; FND-15B4E60F
- Alarms and automation › 4: FND-6163C9EB; FND-0C37BB1E

---

This pack cites 99 of 203 relevant findings.

48 of 58 top-rated relevant findings cited.

> Generated with ProbeMatrix Learnings Coach v2.0.0a8 (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
