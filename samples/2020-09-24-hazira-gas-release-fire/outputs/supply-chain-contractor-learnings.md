# Supply Chain and Contractor Learnings: Gas terminal release and fire, 2020

**DRAFT**

Review: draft · Classification: internal · Version 1.0

Draft because: the investigation status is in progress; no finding is marked as edited by a person

*Learning purposes: not a statutory document. Derived from a ProbeMatrix investigation export; learnings are evidence-linked but should be validated by the organisation before adoption. Draft learnings: the investigation status is in progress. · Learnings drafted by an AI agent from AI-assisted findings*

*About 5 min read*

**Audience:** Procurement, stores and materials management, vendors and equipment makers, and the functions that manage contractors

**Incident:** Hazira gas terminal condensate release and fire · 2020-09-24

## Data quality and limits

- Draft learnings from an unreviewed analysis: the export's investigation status is in progress and no finding is marked as edited by a person. Validate every item before adoption.

## Bottom line

- A seal with no specification and no quality check was bought, issued and fitted as regular practice; it is the probable source of the release. [FND-EBB66554; FND-7A32AC87; EVD-8645; EVD-0064] *(learning: LR-01)*
- No role owned the specification of the legacy part, or the approval of a substitute. [FND-23139BF9; EVD-8645] *(learning: LR-01)*
- The substitution never went through change review: a part chosen at the stores counter is a change. [FND-5A5F6AB3; EVD-2986] *(learning: LR-06)*
- A vendor-prepared drawing was used without the operator's check, and it did not match the field. [FND-82687B50; EVD-0933] *(learning: LR-19)*

## How the part reached the job

Sources: [FND-EBB66554; EVD-8645]

- c. 1986 (about 34 years before): The condensate meter is commissioned with a rectangular-slot gasket supplied by the original equipment maker. [FND-B86F67F0; FND-7A32AC87; EVD-0064; EVD-8645]
  - Received by: Original equipment maker
- 2018-11 (22 months before): The meters are cleaned, serviced and calibrated. The findings do not record when the original gasket specification was lost, or when and by whom buying from the equipment maker stopped. [FND-23139BF9; FND-B56701CA; EVD-8645; EVD-1494]
  - Received by: Maintenance function
  - Response: No record of the date or authority of the switch to local O-rings
- 2019-02-25 (18 months before): The meter is cleaned and its gasket changed, with the locally bought O-ring used as regular practice. [FND-8CE00707; EVD-1494; EVD-8645]
  - Received by: Maintenance crew
  - Response: No specification or quality check recorded
- 2020-09-17: A maintenance notification is raised for a malfunction of the meter. [FND-2FAB8D51; EVD-0591]
  - Received by: Maintenance planning
- 2020-09-18: Need met from stock: the gasket is replaced with a locally purchased round O-ring in place of the rectangular-slot gasket; the O-rings were bought with no specification and no quality control. [FND-EBB66554; FND-A0017E28; EVD-8645]
  - Received by: Stores and procurement
  - Response: No technical approval recorded
- 2020-09-18: Installation: the O-ring is fitted and the system is only pressurised to operating pressure; no change review is raised for the substitution. [FND-5A5F6AB3; FND-82673283; EVD-2986; EVD-2894]
  - Received by: Maintenance crew
  - Response: No change review recorded
- 2020-09-24: The installed seal fails and is the probable source of the release. [FND-BC4FD086; FND-7A32AC87; EVD-0064]
  - Received by: Operations

## Learnings

### Procurement and stores

**Learning:** If stores can buy and issue a pressure-boundary seal with no specification and no quality check, the substitute becomes the normal part. [FND-EBB66554; FND-A0017E28; FND-D66ACA7B; EVD-8645]

Locally purchased O-rings were bought and issued as regular practice in place of the original rectangular-slot gasket, with no specification or quality control at purchase. Nothing in the purchasing or issue step asked for a specification reference.

- Owner: Materials management function

*(evidence: direct; +10 supporting; learning: LR-01)*

**Learning:** If no role owns the specification of a legacy part, nobody re-establishes it when it is lost, and buying fills the gap by habit. [FND-23139BF9; FND-B56701CA; FND-DE30BD8B; EVD-8645]

No accountable owner or recorded authority existed for the gasket's material specification and its procurement, and no substitute specification or quality-control information reached the maintainers.

- Owner: Plant leadership, with the materials management and engineering functions

*(evidence: direct; +10 supporting; learning: LR-01)*

### Engineering at the supply interface

**Learning:** A substitute part chosen at the stores counter is a change, and it needs the change review even when it has been used before. [FND-5A5F6AB3; FND-B440C1BF; EVD-2986; EVD-8645]

The decision to use locally procured O-rings was never recorded or reviewed under management of change, and no change had gone through that procedure since 2018. People did not see a like-for-unlike replacement as a change.

- Owner: Engineering function (owner of management of change)

*(evidence: direct; learning: LR-06)*

### Vendors and OEMs

**Learning:** When the original maker's parts stop being bought for ageing equipment, the specification and the support go with them unless someone asks for them. [FND-B86F67F0; FND-8CE00707; EVD-8645; EVD-0064]

The meter dated from 1986, its gaskets were no longer procured from the original equipment maker, and the original specification was not available. The findings record no request to the maker or another supplier for the specification.

- Owner: Materials management function, with the engineering function

*(evidence: direct; +10 supporting; learning: LR-01)*

**Learning:** A drawing prepared by a vendor is not a controlled document until the operator has checked and approved it. [FND-82687B50; FND-583EB5FE; FND-72DCEE68; EVD-0933]

After the original metering drawings were lost, a vendor prepared new ones. They were not checked or approved, and the valve and meter configuration on them did not match the field.

- Owner: Engineering document control

*(evidence: direct; +3 supporting; learning: LR-19)*

### Contractors and outsourced roles

**Learning:** Work handed to a drawing contractor needs the same acceptance check as work done in-house; the contractor's drawing entered use because the host's acceptance step was missing. [FND-D25BF914; FND-107C8238; EVD-0933]

The replacement as-built drawing was prepared outside the organisation and not verified before it took the place of the original. The gap sits in the host's document control, not in the contractor.

- Owner: Engineering document control

*(evidence: direct; +4 supporting; learning: LR-19)*

## Recommendations and indicators

**Recommendation:** Make the stores system refuse to issue a pressure-boundary seal without a specification reference and an approved-substitute record. [FND-EBB66554; EVD-8645]
- Control tier: engineering
- Barrier: Procurement control of pressure-boundary parts
- Leading indicator: Pressure-part issues blocked or referred for engineering approval each quarter, and their closure time

*(+6 supporting; learning: LR-01)*

**Recommendation:** Re-establish the seal design for the meter flange from the maker's data or an engineered equivalent, stock only certified parts against that specification, and quarantine non-conforming seals. [FND-D66ACA7B; FND-B86F67F0; EVD-8645; EVD-0064]
- Control tier: substitution
- Barrier: Pressure-boundary integrity (correct seal)
- Leading indicator: % of critical pressure-boundary spares with a specification and certificate on file

*(+6 supporting; learning: LR-01)*

**Recommendation:** Survey legacy equipment for lost specifications, and plan replacement of items that can no longer be maintained to specification. [FND-B440C1BF; EVD-8645]
- Control tier: elimination
- Barrier: Equipment obsolescence management
- Leading indicator: % of legacy items surveyed, and the number with a replacement or re-specification decision recorded

*(+6 supporting; learning: LR-01)*

**Recommendation:** Build a change-review trigger into the stores issue and work-order screens: a non-catalogue or substitute part needs a management-of-change reference before issue. [FND-5A5F6AB3; EVD-2986]
- Control tier: engineering
- Barrier: Management of change
- Leading indicator: % of substitute-part issues with a management-of-change reference, and change reviews raised per month

*(learning: LR-06)*

**Recommendation:** Give one named function ownership of pressure-part specifications and of approving any substitute, with quality checks at receipt for those parts. [FND-23139BF9; FND-DE30BD8B; EVD-8645]
- Control tier: administrative
- Barrier: Procurement control of pressure-boundary parts
- Leading indicator: % of pressure-boundary part receipts with a recorded quality check against the specification
- Why not stronger: The stores interlock and the re-specification above are the stronger controls; they need an owner to keep the specifications they enforce up to date.

*(+6 supporting; learning: LR-01)*

*Language check JC6 accepted: Assigning the owner is the organisational fix for an L4 ownership gap and pairs with the engineering and substitution changes in this section.*

**Recommendation:** Require operator checking and approval of every vendor or contractor drawing before it becomes a controlled document, starting with a field check of the metering and emergency isolation drawings. [FND-82687B50; FND-D25BF914; EVD-0933]
- Control tier: administrative
- Barrier: Controlled as-built drawings
- Leading indicator: % of vendor drawings in use with a recorded operator approval
- Why not stronger: Drawing control is a records process; no engineering control replaces the check of a drawing against the field.

*(+4 supporting; learning: LR-19)*

*Language check JC6 accepted: Approval of vendor drawings is the document-control system fix for this L3/L4 gap; no stronger tier applies to a records process.*

## Gaps in the evidence

- [GAP] No record of when, or by whose authority, gasket purchasing switched from the equipment maker to locally bought O-rings. [FND-23139BF9; EVD-8645]
  - Evidence needed: Purchase orders and stores issue records for the meter's gaskets, and any approval of the substitute.

## Limits of this pack

- The findings involve no contractor or agency workers on the job, so the briefing for contractor crews is left out; the only contractor finding concerns a drawing prepared outside the organisation.
- Few findings carry the supply and contractor functions; most supply-chain conditions are recorded against maintenance, which is why the learnings cite maintenance findings alongside them.
- Written to be shared outside the organisation only after skill-common §7: run check-pack --share external and complete legal review first.

## Supporting citations

- Learnings › 1: FND-7A32AC87; FND-82673283; FND-A2048FB8; FND-FFE174D0; FND-CEE4B00B; FND-3746C7B6; FND-42BEF461; FND-852B7EC7; FND-DEAA7F90; FND-A3D7D53F
- Learnings › 2: FND-7A32AC87; FND-82673283; FND-A2048FB8; FND-FFE174D0; FND-CEE4B00B; FND-3746C7B6; FND-42BEF461; FND-D66ACA7B; FND-852B7EC7; FND-DEAA7F90
- Learnings › 4: FND-7A32AC87; FND-82673283; FND-A2048FB8; FND-FFE174D0; FND-CEE4B00B; FND-3746C7B6; FND-42BEF461; FND-D66ACA7B; FND-852B7EC7; FND-DEAA7F90
- Learnings › 5: FND-D25BF914; FND-83AD4621; FND-107C8238
- Learnings › 6: FND-72DCEE68; FND-82687B50; FND-583EB5FE; FND-83AD4621
- Recommendations and indicators › 1: FND-7A32AC87; FND-82673283; FND-A2048FB8; FND-FFE174D0; FND-CEE4B00B; FND-3746C7B6
- Recommendations and indicators › 2: FND-7A32AC87; FND-82673283; FND-A2048FB8; FND-FFE174D0; FND-CEE4B00B; FND-3746C7B6
- Recommendations and indicators › 3: FND-7A32AC87; FND-82673283; FND-A2048FB8; FND-FFE174D0; FND-CEE4B00B; FND-3746C7B6
- Recommendations and indicators › 5: FND-7A32AC87; FND-82673283; FND-A2048FB8; FND-FFE174D0; FND-CEE4B00B; FND-3746C7B6
- Recommendations and indicators › 6: FND-72DCEE68; FND-583EB5FE; FND-83AD4621; FND-107C8238

---

This pack cites 28 of 35 relevant findings.

22 of 27 top-rated relevant findings cited.

> Generated with ProbeMatrix Learnings Coach v2.0.0a7 (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
