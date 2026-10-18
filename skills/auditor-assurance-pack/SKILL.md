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
PMLC select <ws> --tag assurance --brief                    # how existing audits performed
PMLC select <ws> --text "record|log|register|sign|closure|overdue|schedule|audit" --brief
```

## Write

1. **Why existing assurance did not catch it**: what the findings say about audits, inspections and records before the event (generic checklists, open recommendations, closures without data). Factual, no blame.
2. **Audit test points**: twelve to twenty, grouped by management-system element (maintenance and testing, change management, materials and spares, permits, competence, emergency preparedness, records, audit follow-up). Each: expectation → what to sample (and how many) → evidence of conformity → red flags seen in this event → evidence trail.
3. **Cross-site verification protocol**: a short plan to test whether the top five conditions exist at other sites (sampling approach, records to pull, interviews by role, a site visit walk-path).
4. **Evidence request list**: the documents and records an auditor should request, by function.
5. **Reporting**: a grading scale (conforming / partly / not / not tested) and a results table template.

## Output

Write the pack `<run>/outputs/auditor-assurance-pack.json` (schema: `learnings-coach/references/pack-schema.md`), then:

```bash
PMLC check-pack <ws> <run>/outputs/auditor-assurance-pack.json   # fix every problem it lists
PMLC pack <ws> <run>/outputs/auditor-assurance-pack.json         # -> auditor-assurance-pack.html (primary) and .md
```

Sections → kinds:
1. `para`.
2. `test_point` ×12–20 (requirement, sample, conformity_evidence, red_flags; **must cite**), with `group` = the management-system element.
3. `table` with columns Condition, Records to pull, Interview and Walk-path stop, plus `row_cites`.
4. `check` items, with `group` = the function.
5. A `para` giving the grading scale, then a `table` results template with empty Grade and Notes cells.

Set `"scope": {"levels": [3, 4], "min_rating": <top rating>}`. Put data-quality corrections in `data_quality`, findings left out on purpose in `exclusions`, and same-condition findings in `supporting_cites`. If asked for an .xlsx, build it from the `test_point` items (one row each) with the host's spreadsheet tools.

```json
{"kind": "test_point", "group": "Maintenance and testing", "requirement": "…", "sample": "…",
 "conformity_evidence": "…", "red_flags": ["…"], "cites": ["FND-…", "EVD-…"]}
```
