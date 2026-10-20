---
name: auditor-assurance-pack
description: Produces an audit and assurance pack from a ProbeMatrix investigation export for internal auditors, ISO 45001 and process-safety auditors, certification bodies, insurers and regulators' inspectors - test points grouped by the framework the auditor picks, what to sample, evidence to request, red flags this event showed, critical-control verification and a results template with NC/OFI grades. Use when someone asks for an audit checklist, audit protocol, assurance plan, inspection focus areas, or to verify across other sites that the lessons of an investigation with a ProbeMatrix export have been applied. Not for executive decisions (use `top-management-brief`) or directors' oversight questions (use `board-brief`).
---

# Auditor Assurance Pack

Audience: anyone who tests whether controls work: internal audit, HSE audit teams, certification and regulatory inspectors, insurers. They need **testable criteria** and **evidence to request**, not narrative. Read `learnings-coach/references/learning-principles.md` (including "Interviews in a just culture") and the audit test point block in `learnings-coach/references/output-style.md`.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 and §2.

Engine: `PMLC`, as `skill-common.md` §1 defines it (this skill needs the `learnings-coach` skill installed alongside it).

This skill needs the **workspace** and **clusters**. It uses, when present: the register (`<run>/outputs/learnings-register.json`), the adoption, distribution and verification records, and the organisation's barrier or critical-control register (a CSV the user supplies).

- **Ask which framework** the test points should follow, one question: ISO 45001 (`iso45001`), OSHA PSM (`psm`), CCPS RBPS (`rbps`), Seveso III / COMAH (`seveso`), ICMM critical control management (`icmm`), the Indian regimes (`india`), or the organisation's own management-system elements. Default: the organisation's elements, grouped as in section 2.
- Start from the register if present: carry `learning: "LR-nn"` on test points that test a register learning.

## Gather

```bash
PMLC select <ws> --level 3 4 --top-rated --brief
PMLC select <ws> --tag assurance --brief                    # how existing audits performed
PMLC select <ws> --text "record|log|register|sign|closure|overdue|schedule|audit" --brief
PMLC table-item <ws> hoc --register <run>/outputs/learnings-register.json   # control tiers of the register's fixes
```

`select --preset auditor-assurance-pack` runs the three select calls at once. Requirement ids and titles for the chosen framework are in `learnings-coach/references/standards-crosswalk.json`; the regimes per jurisdiction are in `learnings-coach/references/jurisdictions.md`.

## Write

Write the pack `<run>/outputs/auditor-assurance-pack.json` in the shape in `learnings-coach/references/pack-schema.md`. Set `"scope": {"levels": [3, 4], "min_rating": "top"}`.

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | What an auditor should test first | `bottom_line` | up to 7 |
| 1 | `why-missed` | Why existing assurance did not catch it | What the findings say about audits, inspections and records before the event (generic checklists, open recommendations, closures without data). Factual, no blame | `para` | up to 4 |
| 2 | `test-points` | Audit test points | requirement, sample, conformity_evidence, red_flags; **must cite**. `group` = the framework clause or element; `clause` and `clauses` (below) | `test_point` | up to 20 (at least one per management-system element the evidence touches) |
| 3 | `cross-site` | Cross-site verification protocol | Columns Condition, Records to pull, Interview, Walk-path stop; `row_cites`. Tests whether the top five conditions exist at other sites | `table` | 1 |
| 4 | `critical-controls` | Critical-control verification | Columns Critical control, Barrier register id, Performance requirement, Verification activity, Verifier role; `row_cites` (below) | `table` | optional, up to 1 |
| 5 | `evidence-requests` | Evidence request list | Documents and records to request, `group` = the function | `check` | at least 1 |
| 6 | `reporting` | Reporting | The grading scale (below) | `para` | up to 2 |
| 6 | `reporting` | (same section) | Results template: columns Test point, Clause, Grade, Response to finding, Notes; one row per test point, Grade, Response and Notes left blank | `table` | 1 |

Rules for the content:

- **Group by framework.** With a framework chosen, set each test point's `group` to the clause it tests (such as "ISO 45001 9.2 Internal audit" or "PSM (m)(5) Resolving findings"), in clause order, and its `clauses` to the crosswalk ids (`ISO45001-9.2`, `PSM-(m)(5)`). `clause` is the free-text badge for wording the crosswalk does not hold (an organisation's own element number, "OSHA 1910.119(j)"). Without a framework, group by element: maintenance and testing, change management, materials and spares, permits, competence, emergency preparedness, records, audit follow-up.
- **Sampling.** State a sampling basis ("the last ten restarts after pressure-boundary work"), not statistics the evidence cannot support.
- **Grading.** The `reporting` para gives the scale: conforming; major nonconformity (NC); minor nonconformity; opportunity for improvement (OFI); not tested. The results template's Response to finding column is for the audited organisation's documented response to each finding (PSM (o)(4)): the engine and the coach leave it blank.
- **Critical controls.** Write section 4 when the user picks `icmm`, or supplies a barrier or critical-control register. For each critical control the evidence touches, state the verification activity and the verifier role (ICMM step 8, `ICMM-CCM-8`). Map each to the register's own id in Barrier register id; write "unmapped" where the register has no entry, and list the unmapped controls in `limits`.
- **Interviews** follow "Interviews in a just culture" in `learning-principles.md`.

```json
{"kind": "test_point", "group": "ISO 45001 9.2 Internal audit", "requirement": "…", "sample": "…",
 "conformity_evidence": "…", "red_flags": ["…"], "clause": "ISO 45001 9.2", "clauses": ["ISO45001-9.2"],
 "learning": "LR-02", "cites": ["FND-…", "EVD-…"]}
```

## If the evidence is thin

- **Few L3–L4 findings at the top rating:** one test point per management-system element the evidence touches, and no more; never pad toward 20.
- **The chosen framework has no clause the evidence touches:** say so in `limits` and group the remaining test points by element.
- **No barrier register supplied:** leave the Barrier register id column out of section 4, or leave section 4 out.

## Not covered here

- Executive decisions and enterprise standards: `top-management-brief`. Directors' oversight questions: `board-brief`.
- A full clause-by-clause compliance crosswalk: planned for a later phase (`compliance-crosswalk`).
- Legal conclusions: the pack tests conditions; it never says a requirement was breached.

## Check and hand over

Run `learnings-coach/references/skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/auditor-assurance-pack.json --strict   # fix every problem it lists
PMLC pack <ws> <run>/outputs/auditor-assurance-pack.json                  # -> auditor-assurance-pack.html (open first) and .md
PMLC pack-xlsx <ws> <run>/outputs/auditor-assurance-pack.json --kind test_point   # the test points as an Excel sheet
```

Tell the user, with the hand-over: an audit of other sites against this event's conditions creates new findings that must each be answered, and they may be discoverable. Agree the cross-site audit's scope and its handling with the organisation's legal and compliance advisers before it starts. Next: `PMLC templates <ws> verification` records whether each learning was applied.
