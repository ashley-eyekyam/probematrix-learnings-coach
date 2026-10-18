---
name: interface-learnings
description: Find the learnings that fall between departments in a ProbeMatrix investigation - handovers, shared ownership, unclear authority and assumptions one function made about another (operations and maintenance, maintenance and procurement, engineering and integrity, security and control room, leadership and emergency command…). Use when someone asks what fell through the cracks, about silos, handovers, cross-functional or interface failures, who should have been talking to whom, or how to design a cross-department review after an incident.
---

# Interface Learnings

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py` (this skill needs the `learnings-coach` skill installed alongside it). Needs `clusters.json`.

## Gather

```bash
PMLC interfaces <ws> --top 25
```

Each pair has **shared findings** (both entities named on the same finding) and **cross-entity causal mentions** (a finding owned by one entity names a factor owned by the other in its causal explanation). Rank interfaces by both. Take the top eight to twelve.

For each interface read the examples: `PMLC select <ws> --entity <A> <B> --entity-mode all --brief` (the findings both entities share), then the full text of the highest-rated ones.

## For each interface, write

- **The seam**: what passes between the two functions (a work order, a part, a test, an alarm, a decision, a document).
- **What went wrong at the seam**: assumption, gap in ownership, missing hand-back, conflicting priorities, authority that sat with neither.
- **Why neither side saw it** on its own.
- **The learning** for each side in one sentence.
- **A joint fix**: a hold point, a shared check, a single owner, a handover record, a joint review. Name the control tier.
- **A leading indicator** both sides can see.
- Evidence trail.

## Output

Write the pack `<run>/outputs/interface-learnings.json` (schema: `learnings-coach/references/pack-schema.md`), then:

```bash
PMLC check-pack <ws> <run>/outputs/interface-learnings.json   # fix every problem it lists
PMLC pack <ws> <run>/outputs/interface-learnings.json         # -> interface-learnings.html (primary) and .md
```

Sections and the kinds that fill them:
- **Matrix:** a `table` with columns Interface, Shared findings and Cross-entity causal mentions. Use the top pairs from `interfaces`, with their examples as `row_cites`.
- **One section per interface**, with `id` = the pair (e.g. `f02-f06`):
  - `para` items with `group` = "The seam", "What went wrong at the seam" or "Why neither side saw it".
  - A `learning` for each side, with `owner` = that side.
  - The joint fix as a `recommendation`, with a hoc_tier and an indicator both sides can see.
- **Who must meet whom:** a closing section of `check` items.

Put data-quality corrections in `data_quality`, findings left out on purpose in `exclusions`, and same-condition findings in `supporting_cites`.

```json
{"kind": "learning", "group": "The learning for each side", "lesson": "Stores: …", "owner": "Materials Management (F06)",
 "cites": ["FND-…"]}
```
