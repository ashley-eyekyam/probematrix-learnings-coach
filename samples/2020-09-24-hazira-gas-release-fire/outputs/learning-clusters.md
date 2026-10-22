# Learning Clusters: Hazira gas terminal release and fire, 2020

**DRAFT**

Review: draft · Classification: internal · Version 1.0

Draft because: the investigation status is in progress; no finding is marked as edited by a person

*Learning purposes: not a statutory document; draft: the investigation status is in progress · Learnings drafted by an AI agent from AI-assisted findings*

*About 10 min read*

**Audience:** Investigation and learning leads

**Incident:** Hazira gas terminal condensate release and fire · 2020-09-24

## Data quality and limits

- Draft learnings from an unreviewed analysis: the ProbeMatrix investigation status is in progress and no finding is marked as edited by a person. Validate before adoption.
- The export mentions regulator involvement but its summary sheet says 'Reportable to Regulator: No'. Confirm the reporting status with the organisation; this pack does not decide it.
- 87 role strings could not be placed by the rules: 14 findings sit in F99 (no entity) and 87 in T9 (no tier). The Unresolved items table proposes a decision for each; the tables above it are the engine's counts before those proposals are applied.

## Bottom line

- Mechanical Maintenance (F02) holds the largest share of the learning: 194 findings, 91 of them top-rated. Its highest-rated findings are the lost seal specification and the missing return-to-service test on the condensate meter. [FND-A0017E28; FND-50C7319E; EVD-8645; EVD-2894] *(evidence: corroborated; learning: LR-01)*
- Operations & Control Room (F01) comes next with 170 findings, 72 top-rated. Its highest-rated findings sit after the release: isolation valves that could only be closed by hand at the valve, and gas detection with no automatic shutdown. [FND-044D1DEC; FND-6155A1C2; EVD-3932; EVD-3452] *(evidence: corroborated; learning: LR-09)*
- Engineering, Design, Documents & MOC (F07, 84 findings) owns the change and specification learning: a management-of-change procedure not used since 2018, and a gasket specification no one held. [FND-F7FE8463; FND-B56701CA; EVD-2986; EVD-8645] *(evidence: direct; learning: LR-06)*
- HSE, Process Safety & Audit (F11, 80 findings) and Asset Integrity, Corrosion & Inspection (F05, 70 findings) carry the assurance and integrity learning: an emergency plan with no isolation criteria, and repeated seal failures treated as routine repairs. [FND-446A7956; FND-1A251687; EVD-4052; EVD-1494] *(evidence: direct)*
- Learning reaches every tier, but the board tier rests on one finding (T5), and 87 findings carry a role the rules could not place in a tier (T9). Entity placement is nearly complete: 14 findings sit in F99. [FND-2A77BAFB; FND-91B45FF9] *(evidence: direct)*

## Learning clusters

A finding can touch several clusters, so the counts add up to more than the 436 findings. Three small clusters are not in the table: F16 Vendors, OEMs & Suppliers (7), F14 Corporate & Board (2) and F17 Contractors (2).

| Cluster | Name | Findings | L1 | L2 | L3 | L4 | Top-rated | Cites |
|---|---|---|---|---|---|---|---|---|
| F02 | Mechanical Maintenance | 194 | 22 | 36 | 86 | 50 | 91 | FND-01ADF0AA; FND-110F964C; FND-1280E788; FND-137BC719; FND-15279F97 |
| F01 | Operations & Control Room | 170 | 13 | 46 | 49 | 62 | 72 | FND-01ADF0AA; FND-01C3DE98; FND-02310148; FND-044D1DEC; FND-05841EDA |
| F07 | Engineering, Design, Documents & MOC | 84 | 3 | 11 | 32 | 38 | 30 | FND-01C3DE98; FND-02310148; FND-05841EDA; FND-119E6CF7; FND-137BC719 |
| F11 | HSE, Process Safety & Audit | 80 | 1 | 10 | 35 | 34 | 21 | FND-119E6CF7; FND-2D90823E; FND-2EC435D0; FND-33D32D4C; FND-4458E0C0 |
| F05 | Asset Integrity, Corrosion & Inspection | 70 | 3 | 5 | 35 | 27 | 14 | FND-1A251687; FND-1D61DC3A; FND-55F68376; FND-5E08D0F8; FND-69067A1C |
| F13 | Plant & Asset Leadership | 63 | 5 | 14 | 30 | 14 | 34 | FND-1280E788; FND-15B4E60F; FND-1A251687; FND-2EC435D0; FND-305216AF |
| F04 | Instrumentation, Control & Calibration | 62 | 6 | 15 | 17 | 24 | 16 | FND-01C3DE98; FND-02310148; FND-119E6CF7; FND-15B4E60F; FND-2D90823E |
| F08 | Work Management & Planning | 59 | 4 | 13 | 26 | 16 | 24 | FND-0B35D995; FND-15B4E60F; FND-1662466D; FND-28F8790B; FND-2EC435D0 |
| F09b | Emergency Planning & Command | 43 | 5 | 11 | 14 | 13 | 31 | FND-044D1DEC; FND-15B4E60F; FND-2EC435D0; FND-31405D96; FND-314D34C5 |
| F06 | Materials Management (Stores / Procurement) | 29 | 1 | 4 | 14 | 10 | 27 | FND-23139BF9; FND-2FAB8D51; FND-3746C7B6; FND-42BEF461; FND-59A2F497 |
| F03 | Electrical Maintenance | 26 | 0 | 3 | 15 | 8 | 12 | FND-0B35D995; FND-1280E788; FND-1D61DC3A; FND-554BFB4A; FND-5E08D0F8 |
| F12 | HR, Training & Competence | 22 | 0 | 1 | 12 | 9 | 1 | FND-337CB67F; FND-02B682F3; FND-057E89A7; FND-14D093BD; FND-268CA069 |
| F10 | Security & Surveillance | 19 | 0 | 11 | 0 | 8 | 0 | FND-1ABF45B7; FND-2E2F2A38; FND-2F736E5F; FND-37BC45CF; FND-38F0B929 |
| F09a | Fire-fighting Operations & Fire-water Systems | 17 | 0 | 3 | 7 | 7 | 0 | FND-075C4510; FND-20CC87C0; FND-26BF96E1; FND-332DC593; FND-4317808B |
| F99 | Unmapped | 14 | 2 | 6 | 2 | 4 | 3 | FND-91B45FF9; FND-ABF11182; FND-B5C0CE8F; FND-4108DB15; FND-4DAC9500 |

Sources: [FND-01ADF0AA; FND-01C3DE98; FND-02310148; FND-02B682F3; FND-044D1DEC; FND-057E89A7; FND-05841EDA; FND-075C4510; FND-0B35D995; FND-110F964C; FND-119E6CF7; FND-1280E788; FND-137BC719; FND-14D093BD; FND-15279F97; FND-15B4E60F; FND-1662466D; FND-1A251687; FND-1ABF45B7; FND-1D61DC3A; FND-20CC87C0; FND-23139BF9; FND-268CA069; FND-26BF96E1; FND-28F8790B; FND-2D90823E; FND-2E2F2A38; FND-2EC435D0; FND-2F736E5F; FND-2FAB8D51; FND-305216AF; FND-31405D96; FND-314D34C5; FND-332DC593; FND-337CB67F; FND-33D32D4C; FND-3746C7B6; FND-37BC45CF; FND-38F0B929; FND-4108DB15; FND-42BEF461; FND-4317808B; FND-4458E0C0; FND-4DAC9500; FND-554BFB4A; FND-55F68376; FND-59A2F497; FND-5E08D0F8; FND-69067A1C; FND-91B45FF9; FND-ABF11182; FND-B5C0CE8F]

## Tiers that must learn

A finding can name roles at several tiers. T9 counts findings with at least one role the rules could not place in a tier.

| Tier | Name | Findings | L1 | L2 | L3 | L4 | Top-rated | Cites |
|---|---|---|---|---|---|---|---|---|
| T3 | Function / department management | 247 | 15 | 32 | 111 | 89 | 93 | FND-02310148; FND-044D1DEC; FND-05841EDA; FND-0B35D995; FND-110F964C |
| T1 | Frontline / sharp end | 227 | 25 | 73 | 65 | 64 | 82 | FND-01ADF0AA; FND-01C3DE98; FND-044D1DEC; FND-15279F97; FND-1662466D |
| T2 | First-line supervision / shift in-charge | 219 | 12 | 43 | 107 | 57 | 86 | FND-01ADF0AA; FND-01C3DE98; FND-0B35D995; FND-110F964C; FND-15B4E60F |
| T9 | Unresolved | 87 | 2 | 15 | 14 | 56 | 32 | FND-05841EDA; FND-1A251687; FND-2D90823E; FND-2FAB8D51; FND-3746C7B6 |
| T4 | Plant / asset leadership | 63 | 5 | 15 | 29 | 14 | 35 | FND-044D1DEC; FND-1280E788; FND-15B4E60F; FND-2EC435D0; FND-305216AF |
| T5 | Corporate / policy owner / board | 1 | 0 | 0 | 0 | 1 | 0 | FND-2A77BAFB |

Sources: [FND-01ADF0AA; FND-01C3DE98; FND-02310148; FND-044D1DEC; FND-05841EDA; FND-0B35D995; FND-110F964C; FND-1280E788; FND-15279F97; FND-15B4E60F; FND-1662466D; FND-1A251687; FND-2A77BAFB; FND-2D90823E; FND-2EC435D0; FND-2FAB8D51; FND-305216AF; FND-3746C7B6]

## Relation mix

Almost every finding has an actor. One example role string per relation, from the export: actor, Maintenance team - gasket replacement crew; owner, Electrical Maintenance Team (FLP lamp owners); approver, Maintenance supervisor - approval authority; absent, Reliability Engineering (absent); learner, Maintenance Fitters (learners); norm-setter, Maintenance Supervisor (role model); challenger, Engineering authority (the role expected to challenge the deviation).

| Relation | Name | Findings | L1 | L2 | L3 | L4 | Top-rated | Cites |
|---|---|---|---|---|---|---|---|---|
| actor | actor / participant | 417 | 32 | 88 | 159 | 138 | 146 | FND-01ADF0AA; FND-01C3DE98; FND-02310148; FND-044D1DEC; FND-05841EDA |
| owner | owner / custodian | 70 | 4 | 7 | 37 | 22 | 23 | FND-0B35D995; FND-1280E788; FND-137BC719; FND-23139BF9; FND-257C1100 |
| approver | approver / authoriser | 43 | 6 | 3 | 21 | 13 | 18 | FND-1662466D; FND-322112EE; FND-3AB996FC; FND-42BEF461; FND-491EDE74 |
| absent | absent / not provided | 5 | 1 | 0 | 3 | 1 | 5 | FND-1A251687; FND-91B45FF9; FND-D14B8424; FND-F8C125D5; FND-FEC84761 |
| learner | learner / norm-receiver | 3 | 0 | 0 | 3 | 0 | 2 | FND-71EE9734; FND-A443D288; FND-9CED3B55 |
| norm_setter | role model / norm-setter | 2 | 0 | 0 | 2 | 0 | 1 | FND-A443D288; FND-9CED3B55 |
| challenger | expected challenger | 1 | 0 | 0 | 1 | 0 | 1 | FND-42BEF461 |

Sources: [FND-01ADF0AA; FND-01C3DE98; FND-02310148; FND-044D1DEC; FND-05841EDA; FND-0B35D995; FND-1280E788; FND-137BC719; FND-1662466D; FND-1A251687; FND-23139BF9; FND-257C1100; FND-322112EE; FND-3AB996FC; FND-42BEF461; FND-491EDE74; FND-71EE9734; FND-91B45FF9; FND-9CED3B55; FND-A443D288; FND-D14B8424; FND-F8C125D5; FND-FEC84761]

## Top clusters

### F02 Mechanical Maintenance

Owns the release source: the meter seal and the work on it. The highest-rated findings say the original gasket specification was lost and never re-established, so locally bought O-rings with no specification or quality check became the regular substitute [FND-A0017E28; EVD-8645], and that no procedure required a hydrostatic test before the meter went back into service [FND-50C7319E; EVD-2894]. [FND-A0017E28; FND-50C7319E; EVD-8645; EVD-2894] *(evidence: corroborated; learning: LR-01)*

### F01 Operations & Control Room

Owns the response once the release began. The highest-rated findings say the emergency isolation valves were local-manual only, with no remote operation from the control room [FND-044D1DEC; EVD-3932], and that the fire and gas detection system had no automatic shutdown or suppression interlock [FND-6155A1C2; EVD-3452]. Its lower-tier findings cover accepting the meter back into service without a test. [FND-044D1DEC; FND-6155A1C2; EVD-3932; EVD-3452; FND-491EDE74] *(evidence: corroborated; learning: LR-09)*

### F07 Engineering, Design, Documents & MOC

Owns the design and change record. The highest-rated findings say the management-of-change procedure published in August 2016 had not been used since 2018, so the seal substitution was never reviewed [FND-F7FE8463; EVD-2986], and that the metering drawing was a vendor replacement, never approved, that did not match the field [FND-9D19BE37; EVD-0933]. [FND-F7FE8463; FND-9D19BE37; EVD-2986; EVD-0933] *(evidence: direct; learning: LR-06)*

### F11 HSE, Process Safety & Audit

Owns the plans and the assurance around them. The highest-rated findings say the on-site disaster management plan gave no isolation or stoppage criteria for a major hydrocarbon leak [FND-446A7956; EVD-4052], and a breakdown-led electrical maintenance culture left a damaged flame-proof lamp in service [FND-5E08D0F8; EVD-6916]. Its audit findings show generic checklists that could not find plant-specific defects [FND-C0466EB3; EVD-9692]. [FND-446A7956; FND-5E08D0F8; FND-C0466EB3; EVD-4052; EVD-6916; EVD-9692] *(evidence: direct; learning: LR-07)*

### F05 Asset Integrity, Corrosion & Inspection

Owns the evidence that the equipment was deteriorating. The highest-rated findings say the meter kept failing at the seal and was left to routine resealing, with no root-cause or replacement programme [FND-1A251687; EVD-1494], and that pipe-wall loss found in 2017 had no corrective plan three years later [FND-C6992EAF; EVD-5527]. [FND-1A251687; FND-C6992EAF; EVD-1494; EVD-5527] *(evidence: direct; learning: LR-05)*

## Unresolved items

Each role string the rules could not place, with the engine's current mapping and a proposed decision. No role string in the export is a personal name. Apply a decision by writing it to role_overrides.json and re-running classify; the counts above then change.

| Role string | Decision | Reason | Cites |
|---|---|---|---|
| Area Supervisor | Proposed F01 / T2 / actor (engine: F99 / T2) | area supervision of permit work; a supervisor rank is T2 | FND-7E1F2B3F |
| Area auditors | Proposed F11 / T1 / actor (engine: F11 / T9) | audit team members who carry out the checks | FND-675D99DD |
| Audit procedure authors | Proposed F11 / T3 / owner (engine: F11 / T9) | own the audit procedure | FND-459B7917 |
| CCTV/Telecom Maintenance | Proposed F10 / T1 / actor (engine: F02, F10 / T9) | technicians who maintain the cameras and links | FND-2E2F2A38 |
| CCTV/security system designers | Proposed F07, F10 / T3 / actor (engine: F07, F10 / T9) | design authority for the surveillance system | FND-E63EB689 |
| CISF | Proposed F10 / T1 / actor (engine: F10 / T9) | the site security force on its posts | FND-0A64F629 |
| Commissioning/Testing Reviewer | Proposed F07 / T2 / approver (engine: F07 / T9) | a signatory who reviews tests | FND-8ACDE078 |
| Communications architecture designers | Proposed F07 / T3 / actor (engine: F07 / T9) | design authority for the alarm and call routes | FND-0A64F629 |
| Control Room System Administrators | Proposed F01, F04 / T3 / owner (engine: F01 / T9) | own the control-room systems | FND-EE34220F |
| Control-room training/HR function | Proposed F12 / T3 / owner (engine: F01, F12 / T9) | a department that owns control-room training | FND-E4596837 |
| Corrosion/integrity engineering | Proposed F05 / T3 / actor (engine: F05 / T9) | an engineering function | FND-7D59D47D |
| DCS / Control Systems Administrator | Proposed F04 / T3 / owner (engine: F04 / T9) | owns the DCS configuration | FND-FECC34C0 |
| DCS administrators | Proposed F04 / T3 / owner (engine: F04 / T9) | own the DCS configuration | FND-1A5ECA30 |
| DMP authors | Proposed F09b / T3 / owner (engine: F09b / T9) | own the emergency plan text | FND-6472CD15; FND-E009D26B |
| Document control | Proposed F07 / T3 / owner (engine: F07 / T9) | custodian of controlled drawings | FND-583EB5FE; FND-64864239; FND-C048B355 |
| Electrical Maintenance (pump diagnostics) | Proposed F03 / T1 / actor (engine: F03 / T9) | technicians diagnosing the pump trips | FND-26BF96E1 |
| Emergency Response Drill Administrator | Proposed F09b / T2 / actor (engine: F09b / T9) | runs and records drills | FND-BFABC63C |
| Emergency response training record keepers | Proposed F12 / T2 / actor (engine: F09b, F12 / T9) | keep training records | FND-BC32F8F7 |
| Engineering Document Control | Proposed F07 / T3 / owner (engine: F07 / T9) | custodian of controlled drawings | FND-637706CD; FND-6710C6BA; FND-9D19BE37 |
| Engineering document control | Proposed F07 / T3 / owner (engine: F07 / T9) | custodian of controlled drawings | FND-7A10FF70; FND-83AD4621 |
| Engineering documentation control | Proposed F07 / T3 / owner (engine: F07 / T9) | custodian of controlled drawings | FND-107C8238; FND-F131C1B1 |
| F&G System / Instrumentation Engineering | Proposed F04 / T3 / actor (engine: F04 / T9) | an engineering function | FND-C5000A82 |
| F&G System Designers | Proposed F04, F07 / T3 / actor (engine: F04, F07 / T9) | design authority for fire and gas detection | FND-9399FA02 |
| Fire Water System Maintenance | Proposed F09a / T1 / actor (engine: F09a / T9) | technicians on the fire-water pumps | FND-4317808B |
| HSE Assurance Function | Proposed F11 / T3 / actor (engine: F11 / T9) | a department | FND-9E1AB5BA |
| HSE/Area Inspections | Proposed F11 / T1 / actor (engine: F05, F11 / T9) | inspectors in the plant areas | FND-5E08D0F8 |
| HSE/Process Safety function | Proposed F11 / T3 / actor (engine: F11 / T9) | a department | FND-7A2429CE |
| HSE/audit planning function | Proposed F11 / T3 / actor (engine: F11 / T9) | a department | FND-48967DB2 |
| Hazira inspection functions | Proposed F05 / T3 / actor (engine: F05 / T9) | the site's inspection departments | FND-FD533742 |
| Instrumentation / DCS Engineering | Proposed F04 / T3 / actor (engine: F04 / T9) | an engineering function | FND-0D4C2C13 |
| Instrumentation/Control Systems | Proposed F04 / T3 / actor (engine: F04 / T9) | a department | FND-7D28BE30 |
| Instrumentation/Control Systems maintenance | Proposed F04 / T1 / actor (engine: F04 / T9) | technicians who maintain the instruments | FND-D9A35E88 |
| Instrumentation/controls engineering | Proposed F04 / T3 / actor (engine: F04 / T9) | an engineering function | FND-1A5ECA30; FND-2D90823E |
| Integrity/Inspection engineering | Proposed F05 / T3 / actor (engine: F05 / T9) | an engineering function | FND-4DAC9500; FND-A3DCEBD8 |
| Internal Safety Audit Committee (2018 and 2019) | Proposed F11 / T3 / actor (engine: F11 / T9) | a standing audit committee | FND-BB34B250 |
| Internal audit committee | Proposed F11 / T3 / actor (engine: F11 / T9) | a standing audit committee | FND-5BA62765 |
| Internal audit committees | Proposed F11 / T3 / actor (engine: F11 / T9) | a standing audit committee | FND-5C07D424 |
| Local suppliers | Proposed F16 / T1 / actor (engine: F16 / T9) | outside suppliers of the substitute seals | FND-EBB66554 |
| Maintenance Engineering | Proposed F02 / T3 / actor (engine: F02 / T9) | an engineering function | FND-9D19BE37 |
| Maintenance Organization | Proposed F02 / T3 / actor (engine: F02 / T9) | the maintenance department as a whole | FND-D40839C1 |
| Maintenance engineering | Proposed F02 / T3 / actor (engine: F02 / T9) | an engineering function | FND-107C8238 |
| Maintenance planning | Proposed F08 / T3 / actor (engine: F08 / T9) | a department | FND-922A04DB; FND-98A4D631; FND-D25BF914 |
| Maintenance planning/reliability function | Proposed F05, F08 / T3 / actor (engine: F05, F08 / T9) | a department | FND-AC8FBB26 |
| Maintenance procedure authors | Proposed F02 / T3 / owner (engine: F02 / T9) | own the maintenance procedures | FND-B91D4A23 |
| Maintenance/Projects Department | Proposed F02, F07 / T3 / actor (engine: F02 / T9) | a department | FND-E87DC506 |
| Management (implicit through lack of approval enforcement) | Proposed F07 / T3 / approver (engine: F99 / T3) | approval of the drawings; the qualifier names an approval role | FND-99B3F80E |
| Materials/Procurement Officer | Proposed F06 / T2 / actor (engine: F06 / T9) | an officer who signs purchases | FND-615DB819 |
| Materials/Procurement function | Proposed F06 / T3 / actor (engine: F06 / T9) | a department | FND-42BEF461 |
| ONGC engineering | Proposed F07 / T3 / actor (engine: F99 / T9) | the operator's engineering department | FND-72DCEE68 |
| ONGC engineering/document control | Proposed F07 / T3 / owner (engine: F07 / T9) | custodian of controlled drawings | FND-D25BF914 |
| Operations | Proposed F01 / T3 / actor (engine: F01 / T9) | the operations department as a whole | FND-86CB3683 |
| Operations (Gas Terminal Control Room) | Proposed F01 / T1 / actor (engine: F01 / T9) | the control-room crew | FND-6163C9EB |
| Operations (return-to-service acceptance) | Proposed F01 / T2 / approver (engine: F01 / T9) | the shift that accepts equipment back | FND-491EDE74 |
| Operations (return-to-service approval) | Proposed F01 / T2 / approver (engine: F01 / T9) | the shift that accepts equipment back | FND-3AB996FC |
| Operations recipient | Proposed F01 / T2 / actor (engine: F01 / T9) | the shift that receives the notification | FND-646BAC1F |
| Operations/engineering function responsible for MOV capability | Proposed F01, F07 / T3 / owner (engine: F01 / T9) | the qualifier names an owner | FND-A19F3D9C |
| Permit Office/Operations | Proposed F01, F11 / T2 / actor (engine: F01, F11 / T9) | issues permits for the shift | FND-53C9BDB5 |
| Permit-to-Work Issuers | Proposed F11 / T2 / approver (engine: F11 / T9) | permit signatories | FND-0A8B8BCC |
| Permit-to-work administrators | Proposed F11 / T2 / actor (engine: F11 / T9) | keep the permit records | FND-D93C5262 |
| Pipeline integrity / inspection scheduler | Proposed F05 / T2 / actor (engine: F05 / T9) | plans the inspections | FND-6FA2CEDE |
| Plant Design/Engineering | Proposed F07 / T3 / actor (engine: F07 / T9) | an engineering function | FND-38F0B929; FND-DE978BF5 |
| Plant design/engineering | Proposed F07 / T3 / actor (engine: F07 / T9) | an engineering function | FND-05841EDA |
| Plant monitoring management | Proposed F10 / T3 / actor (engine: F99 / T3) | managers of the CCTV monitoring the finding is about | FND-A528DBE5 |
| Procurement | Proposed F06 / T3 / actor (engine: F06 / T9) | a department | FND-2CEE8915 |
| Procurement/Stores | Proposed F06 / T3 / actor (engine: F06 / T9) | a department | FND-B440C1BF; FND-B56701CA; FND-DEAA7F90 |
| Project/facilities engineering | Proposed F07 / T3 / actor (engine: F07 / T9) | an engineering function | FND-D871D980 |
| Quality Control/Inspection function (not provided) | Proposed F05, F06 / T3 / absent (engine: F05, F06 / T9) | the qualifier says absent | FND-F8C125D5 |
| Reliability Engineering (absent) | Proposed F05 / T3 / absent (engine: F05 / T9) | the qualifier says absent | FND-1A251687 |
| Reliability/Engineering Function | Proposed F05 / T3 / actor (engine: F05 / T9) | an engineering function | FND-82FC718D |
| SAP maintenance users | Proposed F02, F08 / T1 / actor (engine: F02, F08 / T9) | technicians and planners using the work system | FND-62EF1667 |
| SAP/work-control administrator | Proposed F08 / T3 / owner (engine: F08 / T9) | owns the work-control configuration | FND-678E51A3 |
| SAP/workflow administrator | Proposed F08 / T3 / owner (engine: F08 / T9) | owns the work-control configuration | FND-646BAC1F |
| Security/CCTV design | Proposed F07, F10 / T3 / actor (engine: F07, F10 / T9) | design authority for the surveillance system | FND-A528DBE5 |
| Senior Officers (closure check) | Proposed F02, F08 / T3 / approver (engine: F99 / T2) | a rank above the supervisor; the qualifier names a closure check | FND-C59DCD29 |
| Senior management | Proposed F13 / T4 / actor (engine: F99 / T3) | plant leadership | FND-856F80CE |
| Senior officers responsible for sample checks | Proposed F02, F08 / T3 / owner (engine: F99 / T2) | a rank above the supervisor; the qualifier names an owner | FND-AE60859C |
| Stores/Procurement (material sourcing) | Proposed F06 / T1 / actor (engine: F06 / T9) | staff who source the parts | FND-3746C7B6; FND-8CE00707 |
| Stores/Procurement (responsible for substitute O-ring sourcing) | Proposed F06 / T3 / owner (engine: F06 / T9) | the qualifier names an owner | FND-7A32AC87 |
| Stores/Procurement Officer | Proposed F06 / T2 / actor (engine: F06 / T9) | an officer who signs purchases | FND-2FAB8D51; FND-D66ACA7B |
| Supervision/management (implicit through lack of corrective action) | Proposed F02 / T2 / actor (engine: F99 / T3) | present but took no corrective action, so actor rather than absent | FND-91B45FF9 |
| Supervisor approving the painting-only action | Proposed F05 / T2 / approver (engine: F99 / T2) | a supervisor who approved a repair | FND-4DAC9500 |
| Training Department | Proposed F12 / T3 / actor (engine: F12 / T9) | a department | FND-E3D07562 |
| Training Function | Proposed F12 / T3 / actor (engine: F12 / T9) | a department | FND-268CA069 |
| Vendor drafting | Proposed F16 / T1 / actor (engine: F07, F16 / T9) | an outside drafting supplier | FND-583EB5FE |
| Vendor/Contractor (drawing preparation) | Proposed F16, F17 / T1 / actor (engine: F07, F16, F17 / T9) | an outside drafting supplier | FND-107C8238 |
| Vendor/drawing contractor | Proposed F16, F17 / T1 / actor (engine: F07, F16, F17 / T9) | an outside drafting supplier | FND-D25BF914 |
| Zone/Area Inspectors | Proposed F03, F11 / T1 / actor (engine: F99 / T9) | inspectors of the zoned areas' electrical fittings | FND-ABF11182 |

## Taxonomy adaptation

The workspace was classified with taxonomy 2.0 and the india-process-site overlay. The overlay adds the role words of an Indian public-sector process site: the site security force posts (constable, sub-inspector) go to Security & Surveillance (F10), the emergency plans (DMP, ERDMP) and the site and chief incident controllers go to Emergency Planning & Command (F09b), and GM, CGM and resident engineer ranks are read as plant leadership (T4). These are the roles of the night-shift command chain in the witness statements and the plant organogram [FND-4245FBF2; FND-82761CC5; EVD-3932]. [FND-4245FBF2; FND-82761CC5; EVD-3932] *(evidence: inferred)*

## Limits of this pack

- The proposed role decisions are not applied in this sample, so that its tables match a fresh setup of the export; an organisation running the coach applies them and re-runs classify.
- No statutory posts were found in the role strings, so the Statutory posts section is left out.
- Counts are finding instances, not learnings: one condition is often described by many findings.

---

This pack cites 73 of 150 relevant findings.

73 of 150 top-rated relevant findings cited.

> Generated with ProbeMatrix Learnings Coach v2.0.0a6 (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
