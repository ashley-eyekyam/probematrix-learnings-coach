---
name: supply-chain-contractor-learnings
description: Produce learning for procurement, stores, materials management, vendors, OEMs and contractors from a ProbeMatrix investigation export - part specifications and substitutions, local sourcing without quality control, OEM support for ageing equipment, vendor documents, contractor work control and agency or outsourced roles. Use when someone asks what procurement, stores, the supply chain, vendors, OEMs or contractors should learn, or wants a supplier or contractor briefing, spares policy input, or contractor-management lessons after an incident.
---

# Supply Chain & Contractor Learnings

Audience: the Learning Clusters tagged `supply` or `contractor` (in the default taxonomy F06 materials management, F16 vendors, OEMs and suppliers, F17 contractors), plus any agency roles named in the findings.

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py`. Read `learnings-coach/references/learning-principles.md`.

## Gather

```bash
PMLC select <ws> --tag supply contractor --brief
PMLC select <ws> --text "procure|stores|spare|OEM|vendor|supplier|local|substitut|contract|agency|outsourc" --brief
```

## Write

1. **How the part (or service) reached the job**: the path from need to installed item, with each decision point and who took it (roles), from the evidence. Mark points with no record.
2. **Learnings for procurement and stores**: specification, technical approval of substitutes, quality checks at receipt, storage and shelf-life, traceability.
3. **Learnings for engineering and maintenance at the supply interface**: who may approve a substitute, and how it is recorded (link to `interface-learnings`).
4. **Learnings for vendors and OEMs**: documents and support for legacy equipment; what to ask vendors for.
5. **Contractors and outsourced roles**: if findings involve contractor or agency staff (e.g. security, fire, inspection agencies), what reporting lines, competence and supervision the findings question.
6. **Recommendations and indicators**: e.g. "% of critical spares with an approved specification", "substitutions approved through change control".

## Output

Write the pack `<run>/outputs/supply-chain-contractor-learnings.json` (schema: `learnings-coach/references/pack-schema.md`), then:

```bash
PMLC check-pack <ws> <run>/outputs/supply-chain-contractor-learnings.json   # fix every problem it lists
PMLC pack <ws> <run>/outputs/supply-chain-contractor-learnings.json         # -> supply-chain-contractor-learnings.html (primary) and .md
```

Sections → kinds:
1. A `timeline` with one event per decision point: `received_by` = the role that took the decision, and `response` = "No record" where there is none.
2. `learning` items with `group` = Procurement and stores / Engineering at the supply interface / Vendors and OEMs / Contractors and outsourced roles (only the groups the evidence supports).
3. `recommendation` (change, hoc_tier, indicator).

Set `"scope": {"tags": ["supply", "contractor"]}`. Put data-quality corrections in `data_quality`, findings left out on purpose in `exclusions`, and same-condition findings in `supporting_cites`.

```json
{"kind": "timeline", "events": [{"date": "YYYY-MM", "text": "…", "received_by": "Stores/procurement officer",
 "response": "No technical approval recorded", "cites": ["FND-…"]}]}
```

If the export has few supply-chain findings, say so in a `para` and keep the pack short.
