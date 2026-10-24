# Risk Register Update: Hazira gas terminal release and fire, 2020

**DRAFT**

Review: draft · Classification: internal · Version 1.0

Draft because: the investigation status is in progress; no finding is marked as edited by a person

*Learning purposes: not a statutory document. Draft learnings from a ProbeMatrix investigation export; validate them before adoption. · Learnings drafted by an AI agent from AI-assisted findings*

*About 8 min read*

**Audience:** Enterprise risk management: ERM leads, risk owners and insurers' risk engineers

**Incident:** Hazira 2020 · 2020-09-24

## Data quality and limits

- Draft learnings from an unreviewed analysis: the export's Investigation Status is in_progress and no finding is marked as edited by a person, so this pack stays a draft until the investigation is completed and reviewed.

## Bottom line

- Add the threat of a non-specified seal on the 1986 metering skid: the original gasket was replaced by locally bought O-rings as regular practice, with no record of who decided it. [FND-EBB66554; FND-B440C1BF; EVD-8645] *(learning: LR-01)*
- Revisit the rating of the emergency isolation controls: the plan gave no isolation criteria or authority, and the isolation valves could be closed only by hand inside the vapour cloud. [FND-730D0DCA; FND-05841EDA; EVD-4052; EVD-3932] *(learning: LR-07)*
- Revisit the rating of management of change: the procedure was published in 2016 but not used after 2018. [FND-3FEE59DF; EVD-2986] *(learning: LR-06)*
- Twelve external-audit actions were carried past their dates without the approval the procedure requires: record them as risks accepted without authority. [FND-856F80CE; FND-850B270C; EVD-6852] *(learning: LR-21)*
- Add key risk indicators for repeat failures, overdue integrity inspections and changes made without an MOC record, so the register shows these conditions before the next event. [FND-E0AE86A6; FND-B8E1F804; FND-CDE8E62D; EVD-1494; EVD-8307; EVD-2986] *(learning: LR-05)*

## About this pack

Proposals for the risk owner to assess: no loss estimates and no rating decisions.

## Proposed risk-register changes

### Missing threats

**Risk:** Loss of containment at the gas metering skid
**Type of change:** missing-threat
**Current assumption:** A seal change on the meter is routine maintenance with no risk of its own.
**What the evidence says:** The same meter had its gasket changed in February 2019 and September 2019, and the joint leaked again within a year [EVD-1494]; the malfunction notification raised in September 2020 was not closed after the job [EVD-0591]. The recurrence was never assessed as a risk.
**Proposed change:** Add repeat seal failure on ageing pressure-boundary equipment as a threat to this risk, with the reliability review that should follow a second failure as its control. [FND-E0AE86A6; FND-3A34BAD3; FND-FEC84761; EVD-1494; EVD-0591]

*(evidence: corroborated; +6 supporting; learning: LR-05)*

**Risk:** Escalation of a major hydrocarbon release
**Type of change:** missing-threat
**Current assumption:** Emergency isolation valves can be reached and closed by hand during a release.
**What the evidence says:** The isolation valves had no remote operation from the control room [EVD-3932]; the shift in-charge had to reach the gas terminal gate before the first valve was closed, 46 minutes after first detection [EVD-9612].
**Proposed change:** Add a vapour cloud that denies access to manual isolation as a threat, and review whether remote or automatic isolation is needed as its control. [FND-05841EDA; EVD-3932; EVD-9612]

*(evidence: corroborated; +4 supporting; learning: LR-09)*

**Risk:** Escalation of a major hydrocarbon release
**Type of change:** missing-threat
**Current assumption:** Anyone who sees a release can warn the operating control room at once.
**What the evidence says:** Perimeter security staff saw the vapour first but could tell only the CCTV control room and the main gate; the gas terminal control room heard of it after a further check by camera [EVD-6234] [EVD-8871].
**Proposed change:** Add an indirect warning path from the people most likely to see a release as a threat to early response. [FND-0A64F629; EVD-6234; EVD-8871]

*(evidence: direct; learning: LR-13)*

### Control ratings to revisit

**Risk:** Uncontrolled change to hydrocarbon equipment
**Type of change:** control-rating
**Current assumption:** Changes to plant and materials go through the management-of-change procedure published in August 2016.
**What the evidence says:** The procedure was not followed for changes in 2013 and 2018, and no MOC had been carried out since 2018 [EVD-2986]; the seal substitution never reached a change review [EVD-8645].
**Proposed change:** Reassess the rating of the MOC control against its actual use since 2018, not against the existence of the procedure. [FND-3FEE59DF; FND-CDE8E62D; FND-8083ECAC; EVD-2986; EVD-8645]

*(evidence: direct; +1 supporting; learning: LR-06)*

**Risk:** Escalation of a major hydrocarbon release
**Type of change:** control-rating
**Current assumption:** The on-site disaster management plan and the ERDMP control the major-leak scenario.
**What the evidence says:** Both documents named hydrocarbon leakage but neither gave isolation or stoppage criteria, nor who may decide to isolate [EVD-4052] [EVD-6414].
**Proposed change:** Revisit the rating of the emergency plan as a control for this scenario until it holds isolation criteria and the authority to act on them. [FND-730D0DCA; FND-6472CD15; FND-33D32D4C; EVD-4052; EVD-6414]

*(evidence: corroborated; +6 supporting; learning: LR-07)*

**Risk:** Escalation of a major hydrocarbon release
**Type of change:** control-rating
**Current assumption:** Fixed gas detection protects the plant when a release occurs.
**What the evidence says:** The detectors were wired to an annunciator for display only, with no automatic shutdown or fire suppression [EVD-8657] [EVD-3452].
**Proposed change:** Rate gas detection as an alarm that depends on people acting, not as an automatic protective control, and review the threats it is credited against. [FND-2D90823E; EVD-8657; EVD-3452]

*(evidence: corroborated; +4 supporting; learning: LR-10)*

**Risk:** Ignition of a hydrocarbon release
**Type of change:** control-rating
**Current assumption:** Electrical equipment in the hazardous area keeps its flameproof protection.
**What the evidence says:** A flameproof lamp had three bolts missing and its glass case open by 5 to 6 cm [EVD-6916]; electrical maintenance was skewed towards breakdowns, and the post-incident audit was one generic page [EVD-0496] [EVD-9999].
**Proposed change:** Reassess the rating of hazardous-area ignition control against inspection records for the fittings, not against the equipment's certification. [FND-FD533742; FND-0B35D995; FND-675D99DD; EVD-6916; EVD-0496; EVD-9999]

*(evidence: corroborated; +4 supporting; learning: LR-11)*

**Risk:** Loss of containment from pipeline wall loss
**Type of change:** control-rating
**Current assumption:** Thickness surveys find wall loss and the findings are acted on.
**What the evidence says:** The 2017 report found pipes needing corrective action, and three years later no plan existed [EVD-5527]; 1.03 mm of pitted wall loss on a segment with no corrosion allowance was treated with paint [EVD-2397].
**Proposed change:** Reassess the integrity control's rating on whether findings are closed, not on whether surveys are done. [FND-5EA23B17; FND-AA826948; FND-FA73D914; FND-7D59D47D; EVD-5527; EVD-2397]

*(evidence: corroborated; learning: LR-17)*

**Risk:** Escalation of a hydrocarbon fire
**Type of change:** control-rating
**Current assumption:** The diesel fire-water pumps back up the electric pumps.
**What the evidence says:** Of four diesel pumps, two were under maintenance, one ran for 30 minutes and one tripped after two minutes, with no cause found or action recorded [EVD-2432]. The electric pumps carried the incident.
**Proposed change:** Revisit the rating of the fire-water backup against the diesel pumps' recorded availability. [FND-E7FB469A; FND-D9E0CE71; FND-694B2DA0; EVD-2432]

*(evidence: direct; +1 supporting; learning: LR-23)*

### Risks accepted without authority

**Risk:** Loss of containment at the gas metering skid
**Type of change:** accepted-without-authority
**Current assumption:** Parts on a hydrocarbon pressure boundary match the original specification, or a change is approved.
**What the evidence says:** The original gasket specification was lost; locally bought O-rings were used as regular practice with no specification or quality check, and there is no record of the date or the authority of the decision to switch [EVD-8645].
**Proposed change:** Record the substitute seal as a risk carried without an approval, and ask the risk owner to decide whether it is accepted, changed or stopped. [FND-EBB66554; FND-B440C1BF; FND-FFE174D0; EVD-8645]

*(evidence: direct; +3 supporting; learning: LR-01)*

**Risk:** Open safety actions from the 2018 external audit
**Type of change:** accepted-without-authority
**Current assumption:** Audit actions are closed by their dates, or an extension is approved as the procedure requires.
**What the evidence says:** 296 of 308 recommendations were complied with; the other 12 had dates extended to 30 April 2021 with no record of the approval the procedure requires [EVD-6852].
**Proposed change:** List each extended action as a risk carried without authority until the required approval is recorded or the action is closed. [FND-856F80CE; FND-850B270C; EVD-6852]

*(evidence: direct; learning: LR-21)*

### Indicators to add

**Risk:** Loss of containment from pipeline wall loss
**Type of change:** kri
**Current assumption:** The four-year thickness-measurement cycle is kept.
**What the evidence says:** The last two surveys were in 2011 and 2017, a six-year gap [EVD-8307], and baseline thickness data and pipe schedules were missing for many gas terminal pipes [EVD-8287].
**Proposed change:** Add an indicator of integrity inspections overdue against their cycle, reported with the risk. [FND-B8E1F804; FND-64864239; EVD-8307; EVD-8287]

*(evidence: corroborated; learning: LR-18)*

**Risk:** Uncontrolled hazardous maintenance work
**Type of change:** kri
**Current assumption:** Every hazardous job has a permit and a job safety plan on record.
**What the evidence says:** Some work permits were missing with no record kept of them, and job safety plans were not attached in SAP [EVD-5105].
**Proposed change:** Add an indicator of permits not accounted for and jobs with no job safety plan, reported with the risk. [FND-D93C5262; FND-14E2A4B5; EVD-5105]

*(evidence: direct; learning: LR-22)*

## Key risk and control indicators

**Indicator:** Repeat failures on safety-critical equipment [FND-E0AE86A6; EVD-1494]
- Measure: Count of second and later failures of the same item within 24 months, from the maintenance notification history.
- Deterioration looks like: Any item with a third failure and no reliability review on record.

*(learning: LR-05)*

**Indicator:** Integrity inspections overdue [FND-B8E1F804; EVD-8307]
- Measure: Share of thickness and integrity inspections past their scheduled cycle, from the inspection plan.
- Deterioration looks like: Any inspection more than one cycle overdue.

*(learning: LR-18)*

**Indicator:** Inspection findings without a corrective plan [FND-5EA23B17; FND-FA73D914; EVD-5527; EVD-2397]
- Measure: Number and age of inspection findings that call for corrective action and have no approved plan.
- Deterioration looks like: A finding open across two survey cycles, or closed by a coating where wall loss was found.

*(learning: LR-17)*

**Indicator:** Changes with an MOC record [FND-CDE8E62D; EVD-2986]
- Measure: Share of material, equipment and setting changes in the work-order system that carry an MOC record.
- Deterioration looks like: No MOC record raised in a quarter in which changes were made.

*(learning: LR-06)*

**Indicator:** Fire-water pump availability [FND-E7FB469A; EVD-2432]
- Measure: Share of time each fire-water pump is available, from test runs and maintenance records.
- Deterioration looks like: A pump out of service, or a trip with no cause found, beyond the period the site allows.

*(learning: LR-23)*

**Indicator:** Audit actions past their date [FND-856F80CE; EVD-6852]
- Measure: Number of audit actions past their target date, and how many of the extensions carry the required approval.
- Deterioration looks like: Any extension with no approval on record.

*(learning: LR-21)*

## Barriers for the bow-tie

### Prevention

**Barrier:** design and specification (substitution of parts) [FND-EBB66554; FND-B440C1BF; EVD-8645]
- Failure mode: No gasket specification was held for the 1986 meter, so locally bought O-rings with no specification or quality check were the regular substitute (L4).
- Type: procedural
- State on the day: absent
- Control tier: administrative
- Fix: Hold the specification for each pressure-boundary seal and block the issue of parts without one.

*(learning: LR-01)*

*Language check JC6 accepted: the administrative change is the system fix at the level of the cause: a held specification and a stores block on unspecified parts*

**Barrier:** change management (MOC) [FND-3FEE59DF; FND-CDE8E62D; EVD-2986]
- Failure mode: The MOC procedure existed but was not used after 2018, so the seal substitution never reached an engineering review (L4).
- Type: procedural
- State on the day: defeated
- Control tier: administrative
- Fix: Raise an MOC from the work-order and stores systems whenever a part differs from its specification.

*(learning: LR-06)*

*Language check JC6 accepted: the administrative change is the system fix at the level of the cause: the MOC trigger is built into the work-order and stores systems*

**Barrier:** maintenance and testing (testing after maintenance) [FND-904FCA63; FND-8ACDE078; EVD-2894]
- Failure mode: No test to design pressure was required or done after the September 2020 gasket change, and no procedure covered the return to service (L3).
- Type: procedural
- State on the day: absent
- Control tier: administrative
- Fix: Make a recorded pressure test a hold point before a pressure-boundary item returns to service.

*(learning: LR-02)*

*Language check JC6 accepted: the administrative change is the system fix at the level of the cause: a recorded test as a hold point before return to service*

**Barrier:** inspection and integrity (acting on inspection results) [FND-5EA23B17; FND-FA73D914; EVD-5527; EVD-2397]
- Failure mode: Wall loss was measured but not acted on for three years, and painting was used for pitted wall loss (L4, L3).
- Type: procedural
- State on the day: degraded
- Control tier: administrative
- Fix: Require a fitness-for-service decision on every wall-loss finding, with the risk owner told of any finding left open.

*(learning: LR-17)*

*Language check JC6 accepted: the administrative change is the system fix at the level of the cause: a fitness-for-service decision on every wall-loss finding*

### Mitigation

**Barrier:** detection and alarm [FND-2D90823E; EVD-3452; EVD-8657]
- Failure mode: Gas detection lit an annunciator but started no shutdown or suppression (L4).
- Type: active
- State on the day: worked partly
- Control tier: engineering
- Fix: Link confirmed gas detection to automatic shutdown and fire suppression.

*(learning: LR-10)*

**Barrier:** isolation and shutdown (remote isolation) [FND-05841EDA; EVD-3932; EVD-9612]
- Failure mode: The isolation valves could be closed only by hand at the valve; the first was closed 46 minutes after first detection (L4).
- Type: active
- State on the day: worked partly
- Control tier: engineering
- Fix: Provide remote isolation from the control room for the valves that isolate the metering skid.

*(learning: LR-09)*

**Barrier:** emergency command and decision authority [FND-730D0DCA; FND-6472CD15; EVD-4052; EVD-6414]
- Failure mode: The emergency plans named the leak scenario but gave no isolation criteria and no delegated authority to isolate (L4).
- Type: procedural
- State on the day: absent
- Control tier: administrative
- Fix: Write isolation criteria into the emergency plans and delegate the authority to the control-room role on shift.

*(learning: LR-07)*

*Language check JC6 accepted: the administrative change is the system fix at the level of the cause: isolation criteria and delegated authority written into the plans*

**Barrier:** ignition control (hazardous-area equipment) [FND-FD533742; FND-0B35D995; EVD-6916; EVD-0496]
- Failure mode: A flameproof lamp with three bolts missing and its glass case open stayed in service under breakdown-led electrical maintenance (L4, L3).
- Type: passive
- State on the day: degraded
- Control tier: administrative
- Fix: Schedule detailed inspection of every hazardous-area fitting and record each one's state.

*(learning: LR-11)*

*Language check JC6 accepted: the administrative change is the system fix at the level of the cause: a scheduled detailed inspection of every hazardous-area fitting*

**Barrier:** fire-water and fire protection [FND-E7FB469A; FND-D9E0CE71; EVD-2432]
- Failure mode: The electric pumps carried the fire cooling. Latent: three of four diesel pumps were under maintenance or tripping, with no cause found (L4, L3).
- Type: active
- State on the day: worked
- Control tier: engineering
- Fix: Restore the diesel pumps and find the cause of the trip before the backup is counted again.

*(learning: LR-23)*

## Limits of this pack

- The export holds no cost, loss or insurance data, so this pack gives no loss estimate and no cost figure.
- The pack proposes changes; it rates no risk and decides nothing. Ratings, acceptance and every decision stay with the risk owner, who fills the risk_owner_decision column of the CSV.
- The organisation's risk register and bow-ties were not available to this analysis, so each risk is named plainly rather than by its register id.
- The analysis is a desk review of the published enquiry report; it had no access to the site's risk assessments or interviews.

## Supporting citations

- Proposed risk-register changes › 1: FND-AC9A1E69; FND-CEE3D4D7; FND-F0D015E1; FND-69067A1C; FND-D14B8424; FND-110F964C
- Proposed risk-register changes › 2: FND-31405D96; FND-A7137BC4; FND-4C645CB5; FND-BDD73BA2
- Proposed risk-register changes › 4: FND-F7FE8463
- Proposed risk-register changes › 5: FND-7A2429CE; FND-8DAFDADC; FND-81E3EEA0; FND-500E0B2D; FND-D4A3EF8A; FND-D1DF4895
- Proposed risk-register changes › 6: FND-9399FA02; FND-94C28ACE; FND-A245072B; FND-4D7CF773
- Proposed risk-register changes › 7: FND-C7F16268; FND-784A23E4; FND-74A80D24; FND-1D61DC3A
- Proposed risk-register changes › 9: FND-20CC87C0
- Proposed risk-register changes › 10: FND-82673283; FND-A443D288; FND-5A5F6AB3

---

This pack cites 62 of 400 relevant findings.

43 of 133 top-rated relevant findings cited.

> Generated with ProbeMatrix Learnings Coach v2.0.0a6 (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
