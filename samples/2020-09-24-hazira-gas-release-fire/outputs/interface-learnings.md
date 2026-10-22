# Interface Learnings: Hazira gas terminal release and fire, 2020

**DRAFT**

Review: draft · Classification: internal · Version 1.0

Draft because: the investigation status is in progress; no finding is marked as edited by a person

*Learning purposes: not a statutory document; draft: the investigation status is in progress · Learnings drafted by an AI agent from AI-assisted findings*

*About 7 min read*

**Audience:** Maintenance and materials management; operations and emergency planning

**Incident:** Hazira gas terminal condensate release and fire · 2020-09-24

## Data quality and limits

- Draft learnings from an unreviewed analysis: the ProbeMatrix investigation status is in progress and no finding is marked as edited by a person. Validate before adoption.
- The export mentions regulator involvement but its summary sheet says 'Reportable to Regulator: No'. Confirm the reporting status with the organisation; this pack does not decide it.
- FND-44219027 (night-time darkness during the response) carries a reviewer downgrade vote. It appears here only inside an engine-generated table, pasted unchanged; no learning rests on it, as in the register. [FND-44219027]

## Bottom line

- The seam between Mechanical Maintenance (F02) and Materials Management (F06) carried the release source: 27 findings name both, and they describe one condition, a locally bought O-ring used as the regular substitute for a gasket whose specification was lost. [FND-B86F67F0; FND-8CE00707; EVD-8645] *(evidence: corroborated; learning: LR-01)*
- Neither side owned the part: no role owned the gasket specification, the quality control of its purchase, or the authority to approve a substitute. [FND-23139BF9; FND-DE30BD8B; EVD-8645] *(evidence: direct; learning: LR-01)*
- That seam sits on the prevention side, at pressure-boundary integrity. On the mitigation side, the seam between Operations & Control Room (F01) and Emergency Planning & Command (F09b) carried the isolation decision: 31 findings name both, and the plan gave neither side the criteria or the authority to isolate. [FND-82761CC5; FND-8DAFDADC; EVD-4052] *(evidence: corroborated; learning: LR-07)*
- The largest seams by shared findings are Operations & Control Room with Mechanical Maintenance (71) and Mechanical Maintenance with Asset Integrity, Corrosion & Inspection (40). Each needs its own joint review. [FND-4944554C; FND-69067A1C] *(evidence: direct)*

## Interface matrix

The 16 pairs with the most shared findings and cross-entity causal mentions; F02 with F06 is the last row. A causal mention is a finding owned by one entity that names a factor owned by the other.

| Interface | Shared findings | Cross-entity causal mentions | Cites |
|---|---|---|---|
| F01 Operations & Control Room - F02 Mechanical Maintenance | 71 | 391 | FND-314D34C5; FND-44219027; FND-4944554C; FND-8DA35CA9; FND-A9C42ABE |
| F01 Operations & Control Room - F13 Plant & Asset Leadership | 37 | 189 | FND-31405D96; FND-314D34C5; FND-36179046; FND-44219027; FND-82D49143 |
| F02 Mechanical Maintenance - F08 Work Management & Planning | 27 | 213 | FND-1662466D; FND-2FAB8D51; FND-50775B5A; FND-54180594; FND-56C66B96 |
| F02 Mechanical Maintenance - F07 Engineering, Design, Documents & MOC | 34 | 189 | FND-137BC719; FND-5EC15274; FND-6710C6BA; FND-72A7D26C; FND-72DCEE68 |
| F02 Mechanical Maintenance - F05 Asset Integrity, Corrosion & Inspection | 40 | 166 | FND-159C9FD7; FND-1F685360; FND-20034564; FND-5EC15274; FND-69067A1C |
| F02 Mechanical Maintenance - F13 Plant & Asset Leadership | 17 | 226 | FND-314D34C5; FND-44219027; FND-5919B328; FND-BDD73BA2; FND-D1DF4895 |
| F02 Mechanical Maintenance - F04 Instrumentation, Control & Calibration | 6 | 253 | FND-0B651843; FND-45363DCA; FND-B0BA0566; FND-D58142C9; FND-E94D563C |
| F02 Mechanical Maintenance - F09b Emergency Planning & Command | 10 | 230 | FND-314D34C5; FND-44219027; FND-8A8F94A5; FND-9B406A83; FND-AEA16F83 |
| F01 Operations & Control Room - F07 Engineering, Design, Documents & MOC | 30 | 169 | FND-137BC719; FND-3D785319; FND-733F5A1A; FND-7A10FF70; FND-8ACDE078 |
| F01 Operations & Control Room - F04 Instrumentation, Control & Calibration | 27 | 173 | FND-0C37BB1E; FND-2B5C46B9; FND-3D785319; FND-5134D887; FND-6163C9EB |
| F02 Mechanical Maintenance - F11 HSE, Process Safety & Audit | 16 | 203 | FND-1DF986F8; FND-535125C1; FND-611A8BFC; FND-63B6D260; FND-88D0E4B1 |
| F01 Operations & Control Room - F09b Emergency Planning & Command | 31 | 142 | FND-31405D96; FND-314D34C5; FND-44219027; FND-81E3EEA0; FND-82D49143 |
| F01 Operations & Control Room - F08 Work Management & Planning | 17 | 170 | FND-0B35D995; FND-267F1E09; FND-350C35AD; FND-678E51A3; FND-8071945B |
| F01 Operations & Control Room - F05 Asset Integrity, Corrosion & Inspection | 16 | 162 | FND-0F19C9FC; FND-350C35AD; FND-47B1702F; FND-7EB223DE; FND-82FC718D |
| F01 Operations & Control Room - F11 HSE, Process Safety & Audit | 16 | 133 | FND-33D32D4C; FND-4458E0C0; FND-500E0B2D; FND-53C9BDB5; FND-611A8BFC |
| F02 Mechanical Maintenance - F06 Materials Management (Stores / Procurement) | 27 | 96 | FND-2CEE8915; FND-2FAB8D51; FND-35861FFB; FND-3746C7B6; FND-59A2F497 |

Sources: [FND-0B35D995; FND-0B651843; FND-0C37BB1E; FND-0F19C9FC; FND-137BC719; FND-159C9FD7; FND-1662466D; FND-1DF986F8; FND-1F685360; FND-20034564; FND-267F1E09; FND-2B5C46B9; FND-2CEE8915; FND-2FAB8D51; FND-31405D96; FND-314D34C5; FND-33D32D4C; FND-350C35AD; FND-35861FFB; FND-36179046; FND-3746C7B6; FND-3D785319; FND-44219027; FND-4458E0C0; FND-45363DCA; FND-47B1702F; FND-4944554C; FND-500E0B2D; FND-50775B5A; FND-5134D887; FND-535125C1; FND-53C9BDB5; FND-54180594; FND-56C66B96; FND-5919B328; FND-59A2F497; FND-5EC15274; FND-611A8BFC; FND-6163C9EB; FND-63B6D260; FND-6710C6BA; FND-678E51A3; FND-69067A1C; FND-72A7D26C; FND-72DCEE68; FND-733F5A1A; FND-7A10FF70; FND-7EB223DE; FND-8071945B; FND-81E3EEA0; FND-82D49143; FND-82FC718D; FND-88D0E4B1; FND-8A8F94A5; FND-8ACDE078; FND-8DA35CA9; FND-9B406A83; FND-A9C42ABE; FND-AEA16F83; FND-B0BA0566; FND-BDD73BA2; FND-D1DF4895; FND-D58142C9; FND-E94D563C]

## F02 Mechanical Maintenance and F06 Materials Management

### The seam

What passes between them is a part: the seal for the retaining plate of the 1986 condensate meter. Stores and procurement buy and issue it; maintenance fits it to a flange machined for a rectangular-slot gasket [FND-6B3A6492; EVD-8645; EVD-0064]. [FND-6B3A6492; EVD-8645; EVD-0064] *(evidence: direct; learning: LR-01)*

### What went wrong at the seam

An ownership gap. The original gasket specification was not on file and no role owned re-establishing it, so locally bought round O-rings were purchased with no specification or quality check and fitted as a regular practice [FND-A0017E28; FND-B56701CA; FND-23139BF9; EVD-8645]. The switch was never recorded as a management-of-change decision [FND-5A5F6AB3; EVD-2986], and the job of 18 September 2020 was manned with no independent quality check of the part [FND-615DB819; EVD-2894]. [FND-A0017E28; FND-B56701CA; FND-23139BF9; EVD-8645; FND-5A5F6AB3; EVD-2986; FND-615DB819; EVD-2894] *(evidence: corroborated; learning: LR-01)*

### Why neither side saw it

With no recorded authority and a flat authority gradient, staff at the working level made the substitution, and the practice was authorised without being reviewed against a specification [FND-2CEE8915; FND-42BEF461]. Each side could reasonably take the part as settled: stores supplied what the job used, and the job used what stores supplied. Three replacements in 22 months did not prompt a review [FND-AC9A1E69; EVD-1494]. [FND-2CEE8915; FND-42BEF461; FND-AC9A1E69; EVD-1494] *(evidence: inferred; learning: LR-05)*

### Learning for each side

**Learning:** A pressure-boundary seal fitted without a written specification is an unreviewed change, however routine the substitute has become. [FND-7A32AC87; FND-852B7EC7; EVD-8645]

Maintenance fitted locally bought O-rings to a rectangular-slot flange across three replacements, with no specification, quality check or recorded authority [FND-7A32AC87; FND-852B7EC7; EVD-8645].

- Owner: Mechanical Maintenance (F02)

*(evidence: corroborated; learning: LR-01)*

**Learning:** Buying a substitute for a pressure part without a specification moves an engineering decision to the purchase order. [FND-6B3A6492; FND-A0017E28; EVD-8645]

The acquisition process supplied an unspecified round O-ring for a flange machined for a rectangular-slot gasket, with no specification or quality control [FND-6B3A6492; FND-A0017E28; EVD-8645].

- Owner: Materials Management (F06)

*(evidence: corroborated; learning: LR-01)*

### Joint fix

**Recommendation:** Re-establish the meter seal specification (manufacturer data or an engineered equivalent), hold it as a controlled item, and have stores issue pressure-boundary seals only against that specification reference. A substitute part needs an approved change record before it is issued. [FND-23139BF9; FND-8CE00707; FND-BC4FD086; EVD-8645]
- Control tier: substitution
- Barrier: pressure-boundary integrity (correct seal)
- Owner: Mechanical Maintenance (F02)
- Co-owner: Materials Management (F06)
- Leading indicator: Share of pressure-boundary seals issued from stores with a specification reference and a certificate, visible to both stores and maintenance.

*(evidence: corroborated; learning: LR-01)*

## F01 Operations & Control Room and F09b Emergency Planning & Command

### The seam

What passes between them is a decision: whether, when and by whom the plant is isolated in a major release. Emergency planning writes it into the on-site disaster management plan; the control room and the shift in-charges have to take it on the night [FND-500E0B2D; FND-82761CC5; EVD-4052; EVD-3932]. [FND-500E0B2D; FND-82761CC5; EVD-4052; EVD-3932] *(evidence: corroborated; learning: LR-07)*

### What went wrong at the seam

Authority with neither side. The plan named hydrocarbon leakage but gave no isolation or stoppage criteria [FND-446A7956; EVD-4052], isolation authority was not allocated to the on-shift operators [FND-8DAFDADC; EVD-7340], and the isolation intent was never passed to the night shift through the plan or standing orders [FND-BB4CC662]. The decision went up the chain by phone, and the first isolation valve was closed 46 minutes after the leak was first detected [FND-36179046; FND-AEA16F83; EVD-6414]. [FND-446A7956; EVD-4052; FND-8DAFDADC; EVD-7340; FND-BB4CC662; FND-36179046; FND-AEA16F83; EVD-6414] *(evidence: corroborated; learning: LR-07)*

### Why neither side saw it

The major-leak scenario was formally identified in the plan, but its isolation criteria were never defined and the risk of leaving them out was never assessed [FND-33D32D4C; FND-6472CD15]. Each side could reasonably take the decision as covered: the plan named the scenario, and the shift followed the escalation chain it knew [FND-D1DF4895; EVD-3932]. [FND-33D32D4C; FND-6472CD15; FND-D1DF4895; EVD-3932] *(evidence: inferred; learning: LR-07)*

### Learning for each side

**Learning:** An emergency plan that names a release scenario but not who may isolate, and on what criteria, leaves the decision to escalation. [FND-730D0DCA; FND-5C7B163D; EVD-4052]

The plan's hydrocarbon-leak guidance omitted isolation and stoppage criteria and delegated authority [FND-730D0DCA; FND-5C7B163D; EVD-4052].

- Owner: Emergency Planning & Command (F09b)

*(evidence: direct; learning: LR-07)*

**Learning:** When a release blocks access to the source, the shift's task changes from finding the leak to isolating from a distance, and it needs the authority to do so at once. [FND-BDD73BA2; FND-4245FBF2; EVD-9612]

Dense vapour stopped anyone approaching the source, while the isolation decision waited on senior staff who were called at about 02:35 [FND-BDD73BA2; FND-4245FBF2; EVD-9612].

- Owner: Operations & Control Room (F01)

*(evidence: corroborated; learning: LR-08)*

### Joint fix

**Recommendation:** Write isolation and stoppage criteria, the isolation valve list and delegated authority down to control-room shift level into the plan, as one jointly owned section, and test it in unannounced night-shift drills without senior staff present. [FND-82761CC5; FND-5C7B163D; FND-31405D96; EVD-4052; EVD-3932]
- Control tier: administrative
- Barrier: emergency command and decision authority
- Owner: Emergency Planning & Command (F09b)
- Co-owner: Operations & Control Room (F01)
- Leading indicator: Time from confirmed release to the isolation decision in night-shift drills, recorded in the drill record both sides read.
- Why not stronger: The stronger control, remote isolation of the gas terminal valves (LR-09), needs these criteria and this authority to be used without waiting for escalation; the two go together.

*(evidence: corroborated; learning: LR-07)*

*Language check JC6 accepted: the written criteria and delegated authority are the system fix for the plan (L4); the engineering control they pair with is the remote isolation of LR-09*

## Joint-review agenda

For the meetings each pair holds. F02 and F06 meet with the engineering authority present; F01 and F09b meet with plant leadership present.

| Interface | Roles who meet | Agenda item | Evidence to bring | Decision sought | Cites |
|---|---|---|---|---|---|
| F02 and F06 | Maintenance supervisor; stores and procurement lead; engineering authority | Which pressure-boundary parts on the metering skid have no specification on file | Spares list for the skid; purchase records for the seals | Who re-establishes each missing specification | FND-B56701CA; FND-D66ACA7B |
| F02 and F06 | Maintenance supervisor; stores and procurement lead; engineering authority | How a substitute part is approved before it is bought or fitted | The MOC procedure; purchase and issue records for the locally bought O-rings | One approval step, owned by one role, before a substitute is issued | FND-5A5F6AB3; FND-BC4FD086 |
| F02 and F06 | Maintenance planner; stores and procurement lead; quality or inspection role | Who checks a seal against its specification, and where | Job manning for the 18 September 2020 repair; receipt records | Where the independent check sits: at receipt, at issue or at the job | FND-615DB819; FND-F8C125D5 |
| F01 and F09b | Shift in-charges; control-room lead; emergency planner; plant leadership | Who may order isolation of the gas terminal on the night shift, and on what criteria | The disaster management plan's hydrocarbon-leak section; the plant organogram for the night shift | Delegated isolation authority written down to control-room shift level | FND-8DAFDADC; FND-82761CC5 |
| F01 and F09b | Control-room lead; emergency planner; fire service lead | Whether drills test isolation when the source cannot be approached | Drill records; the reconstructed response timeline for 24 September 2020 | A night-shift drill on the major-release scenario, with timed isolation | FND-500E0B2D; FND-6472CD15 |

## Who must meet whom

One line per seam in the matrix. Each pair reviews the record named.

- [ ] F02 and F06: maintenance supervisor and stores lead review the spares and purchase records for pressure-boundary seals. [FND-2CEE8915; FND-3746C7B6]
- [ ] F01 and F02: shift in-charge and maintenance supervisor review return-to-service records for pressure-boundary work. [FND-4944554C; FND-8DA35CA9]
- [ ] F02 and F05: maintenance and integrity engineers review the repeat-failure and wall-loss records together. [FND-69067A1C; FND-20034564]
- [ ] F02 and F07: maintenance and the engineering authority review changes made through work orders against the MOC log. [FND-137BC719; FND-72A7D26C]
- [ ] F02 and F08: maintenance supervisors and planners review open notifications on equipment back in service. [FND-50775B5A; FND-56C66B96]
- [ ] F01 and F09b: control-room leads and emergency planners review the plan's isolation criteria against the drill records. [FND-314D34C5; FND-81E3EEA0]
- [ ] F01 and F13: shift in-charges and plant leadership review who may isolate, on what criteria, at night. [FND-31405D96; FND-36179046]
- [ ] F01 and F04: control-room leads and instrument engineers review what the detection and pressure instruments actually send to the control room. [FND-3D785319; FND-2B5C46B9]
- [ ] F01 and F07: operations and engineering review the drawings and the emergency valve design together. [FND-733F5A1A; FND-8ACDE078]
- [ ] F02 and F11: maintenance and HSE review the permit and job safety plan records for pressure-boundary jobs. [FND-1DF986F8; FND-535125C1]

## Gaps in the evidence

- When the substitute O-ring practice began, and who first approved it, is not in the export. [FND-8CE00707; EVD-8645]
  - Evidence needed: Purchase and stores issue records for the meter seals since commissioning, and the first work order that used a locally bought O-ring.

## Limits of this pack

- This pack opens two seams: F02 with F06 (the 27 findings both name; the pack's scope) and, on the mitigation side, F01 with F09b (31 findings). The other seams in the matrix need their own sections.
- The export does not record who in stores or maintenance decided to use the O-rings, or when the practice began.

---

This pack cites 21 of 27 relevant findings.

19 of 25 top-rated relevant findings cited.

> Generated with ProbeMatrix Learnings Coach v2.0.0a6 (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
