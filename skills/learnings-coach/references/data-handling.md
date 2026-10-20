# Data handling

How the coach treats the personal data in a ProbeMatrix export, and what the organisation must decide. This is a product reference, not legal advice: the organisation, its data protection lead and its lawyers decide the lawful basis, the retention period and any sharing. Items marked *(unverified)* could not be confirmed against primary text.

What a run holds: the workspace JSON is a full copy of the export (findings, evidence quotes, the narrative and the Incident Summary sheet), and the outputs re-embed parts of it. Run folders (`pmlc-runs/`) are git-ignored so they never reach a repository.

## Lawful basis

The organisation chooses and records the lawful basis for using the export to draw learnings. The options the coach's research names:
- GDPR / UK GDPR Art. 6(1)(c) (legal obligation) or Art. 6(1)(f) (legitimate interests) for safety learning.
- GDPR Art. 9(2)(b) (employment and safety law) for health data such as injury details.
- DPDP Act 2023: the "legitimate uses" provision for employment and safety purposes *(unverified: check the exact clause)*.

The agent never decides the lawful basis. If the user does not know it, say so in the hand-over and continue only with roles-only outputs.

## Data minimisation

Use the least personal data the learning needs:
- Write roles, never personal names (`learning-principles.md`). `learning-clusters` writes "(a personal name)" in place of a name.
- Run `scan-names` with the organisation's names file before sharing. It reports files it could not scan and never counts them as zero hits.
- Choose what an HTML page embeds with `--embed cited|summary|full`. `--share external` and `--share public` default to `summary`, which drops evidence quotes; the engine notes when embedded evidence includes witness statements.
- Do not copy free text that holds health details (GDPR Art. 9) or disciplinary or offence matters (Art. 10) into a learning; describe the condition instead.

## Role identifiability

A role can still identify a person. "The shift in-charge on the night of the incident" at one site is usually one person, and under GDPR pseudonymised data is still personal data.
- Flag it when a role plus a date plus a site narrows to one person, and widen the wording (for example "the night shift") unless the audience already knows who it is and needs the precision.
- The Incident Summary fields `Investigating Officer`, `Supervisor at Time` and `Investigation Team` sit in `incident.json`. `profile` does not print them; never quote them in an output.

## Disclosure to the AI host

Running the coach sends the export's content to the AI host that runs the agent. Depending on the host, that may be a transfer to another country.
- The organisation needs to know, and record, which host processed the export.
- If the organisation's policy does not allow the export to go to that host, stop before `ingest`.

## Retention

Safety law wants records kept; privacy law wants personal data kept no longer than necessary. The anchors the coach's research names:
- OSHA PSM (m)(7) and EPA RMP 68.81: incident investigation reports kept five years.
- PSM (o)(5): the two most recent compliance audit reports.
- ISO 45001 10.2: documented information retained, for a period the organisation sets.
- GDPR Art. 5(1)(e) and the DPDP Act: no longer than necessary; erasure once the purpose is served is a core DPDP duty.

The organisation sets a retention review date for each run (`retention_review` in the pack `handling` block and the run manifest). When the review comes, delete the run's workspace and keep only the outputs the organisation has adopted.

## GDPR

GDPR (and UK GDPR) applies when the export holds data about identifiable people in the EU or the UK. The articles above are the ones the coach's research checked: Art. 5 (principles, including storage limitation), Art. 6 (lawful basis), Art. 9 (special categories, including health) and Art. 10 (criminal offence data).

## DPDP Act 2023

India's Digital Personal Data Protection Act 2023. The DPDP Rules 2025 were notified on 13 November 2025. Notice, consent, security and breach obligations apply from 13 May 2027. Erasure once the purpose is served is a core duty. The "legitimate uses" provision for employment and safety purposes is *(unverified)*: the organisation checks the exact clause.

## This is not the investigation record

The coach's outputs are learning material, marked "Learning purposes: not a statutory document". They are not the record of the investigation and not the statutory report (see `jurisdictions.md`). The ProbeMatrix investigation and the organisation's CAPA system remain the record. Deleting a run folder never deletes that record.
