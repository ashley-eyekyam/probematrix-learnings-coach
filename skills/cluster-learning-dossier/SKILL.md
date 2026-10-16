---
name: cluster-learning-dossier
description: Build the complete learning dossier for one department or function (a Learning Cluster) from a ProbeMatrix investigation export - its practices, conditions, supervisory and organisational learnings, interfaces, barriers, warning signs, messages for each level from frontline to leadership, recommendations, training needs and transferability. Use when someone asks "what does maintenance (or operations, engineering, fire services, HSE, procurement…) need to learn from this investigation", wants a department-level lessons pack, or wants every learning for one function in one place.
---

# Cluster Learning Dossier

Steps 2 and 3 of the method for one Learning Cluster: open it along sub-divisions S1–S14 (`learnings-coach/references/ontology.md` §4) and write one learning piece per sub-division.

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py`. Needs `<ws>/clusters.json` (see `learning-clusters`). Read `learnings-coach/references/learning-principles.md` first.

## Gather

```bash
PMLC select <ws> --entity <F-id> --out <ws>/sel-<F-id>.md              # full text
PMLC select <ws> --entity <F-id> --level 1 --brief                      # per level as needed
PMLC interfaces <ws>                                                     # for S6
PMLC timeline <ws> --before <incident date>                              # for S8
```

For large clusters (more than ~60 findings) work level by level so each pass stays grounded; read the full justification and causal text of the highest-rated findings first.

## Write one piece per sub-division

| Piece | Grounded in | Content |
|---|---|---|
| S1 Profile | `classify` output | counts by level, top-rated count, tiers and relations involved |
| S2 Practice (L1) | L1 findings | the practices that contributed, why each made sense at the time |
| S3 Conditions (L2) | L2 findings | the conditions this entity created or tolerated |
| S4 Supervision (L3) | L3 findings | what supervisors should see, check, correct and refuse |
| S5 System (L4) | L4 findings | systems, resources, policies, norms that must change |
| S6 Interfaces | `interfaces.json` pairs involving this entity | what fell between this entity and others; who must talk to whom |
| S7 Barriers | all | barriers this entity owns, prevention or mitigation, how each failed |
| S8 Precursors | timeline candidates mentioning this entity's work | dated warnings and what was done with them |
| S9 Tier messages | all | one short message each for T1, T2, T3, T4 (and T5 if relevant) |
| S10 Recommendations | S2–S8 | what should change, barrier, evidence, control tier, leading indicator |
| S11 Competence | S2–S5 | competences to build, by tier |
| S12 Transferability | all | same site / other sites / industry-wide, with reason |
| S13 Comparison | only if a comparator report is supplied | counterpart yes/partial/none (use `report-comparison`) |
| S14 Formats | S9, S10 | which learnings become Cards, Brief paragraphs, toolbox talks |

Each piece: three to eight learnings, each one sentence of lesson plus two to four sentences of explanation, with the evidence trail. Merge findings that describe the same condition into one learning.

## Output

Write the pack `<run>/outputs/dossier-<F-id>.json` (schema: `learnings-coach/references/pack-schema.md`; `pack` = `dossier-<F-id>`, e.g. `dossier-F02` or `dossier-F09b`), then:

```bash
PMLC check-pack <ws> <run>/outputs/dossier-<F-id>.json   # fix every problem it lists
PMLC pack <ws> <run>/outputs/dossier-<F-id>.json         # -> dossier-<F-id>.html (primary) and .md
```

The bottom line holds the top five learnings for this entity. Give each sub-division its own section, with `id` = `s<n>-<name>`. The engine adds the evidence trail. Sections and the kinds that fill them:
- **S1:** a `table` of counts.
- **S2–S5:** `learning` ×3–8 each (lesson, explanation).
- **S6:** `para` and `learning`.
- **S7:** `barrier` (type, state, failure_mode, hoc_tier, fix).
- **S8:** a `timeline` with `signal`, `received_by` and `response`.
- **S9:** `para`, with `group` = the tier.
- **S10:** `recommendation`.
- **S11:** a `table` with columns Tier and Competence.
- **S12:** a `table` with columns Learning, Reach and Reason.
- **S13:** `para`, only when there is a comparator report.
- **S14:** a `table` with columns Learning and Format.

Set `"scope": {"entities": ["<F-id>"]}`. Put data-quality corrections in `data_quality`, findings left out on purpose in `exclusions`, and same-condition findings in `supporting_cites`. For all clusters, write one dossier per cluster, largest first, plus a pack `dossier-index` with one `table` (Cluster, Findings, Top learning, File).

```json
{"kind": "learning", "lesson": "Supervisors had no checklist to refuse a restart against.", "explanation": "…", "cites": ["FND-…"]}
```
