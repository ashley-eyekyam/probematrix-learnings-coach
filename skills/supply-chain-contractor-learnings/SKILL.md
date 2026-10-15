---
name: supply-chain-contractor-learnings
description: Produce learning for procurement, stores, materials management, vendors, OEMs and contractors from a ProbeMatrix investigation export - part specifications and substitutions, local sourcing without quality control, OEM support for ageing equipment, vendor documents, contractor work control and agency or outsourced roles. Use when someone asks what procurement, stores, the supply chain, vendors, OEMs or contractors should learn, or wants a supplier or contractor briefing, spares policy input, or contractor-management lessons after an incident.
---

# Supply Chain & Contractor Learnings

Audience: Learning Clusters F06 (materials management) and F14 (corporate, external and vendors), plus any contractor or agency roles named in the findings.

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py`. Read `learnings-coach/references/learning-principles.md`.

## Gather

```bash
PMLC select <ws> --entity F06 F14 --brief
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

`<run>/outputs/supply-chain-contractor-learnings.md`. If the export has few supply-chain findings, say so and keep the pack short.
