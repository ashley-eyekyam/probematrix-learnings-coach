---
name: auditor-assurance-pack
description: Turn a ProbeMatrix investigation export into an audit and assurance pack for internal auditors, ISO 45001 / process-safety auditors, certification bodies, insurers and regulators' inspectors - audit test points, what to sample, evidence to request, red flags this event showed, and an audit checklist to test whether the same conditions exist elsewhere. Use when someone asks for an audit checklist, audit protocol, assurance plan, inspection focus areas, or wants to verify across other sites that the lessons of an investigation have been applied.
---

# Auditor Assurance Pack

Audience: anyone who tests whether controls work: internal audit, HSE audit teams, certification and regulatory inspectors, insurers. They need **testable criteria** and **evidence to request**, not narrative.

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py`. Read `learnings-coach/references/learning-principles.md` and the audit test point block in `output-style.md`.

## Gather

```bash
PMLC select <ws> --level 3 4 --min-rating <top> --brief
PMLC select <ws> --entity F11 --brief                      # how existing audits performed
PMLC select <ws> --text "record|log|register|sign|closure|overdue|schedule|audit" --brief
```

## Write

1. **Why existing assurance did not catch it**: what the findings say about audits, inspections and records before the event (generic checklists, open recommendations, closures without data). Factual, no blame.
2. **Audit test points**: twelve to twenty, grouped by management-system element (maintenance and testing, change management, materials and spares, permits, competence, emergency preparedness, records, audit follow-up). Each: expectation → what to sample (and how many) → evidence of conformity → red flags seen in this event → evidence trail.
3. **Cross-site verification protocol**: a short plan to test whether the top five conditions exist at other sites (sampling approach, records to pull, interviews by role, a site visit walk-path).
4. **Evidence request list**: the documents and records an auditor should request, by function.
5. **Reporting**: a grading scale (conforming / partly / not / not tested) and a results table template.

## Output

`<ws>/outputs/auditor-assurance-pack.md`, and if asked, the test points as an .xlsx (one row per test point).
