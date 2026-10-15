---
name: interface-learnings
description: Find the learnings that fall between departments in a ProbeMatrix investigation - handovers, shared ownership, unclear authority and assumptions one function made about another (operations and maintenance, maintenance and procurement, engineering and integrity, security and control room, leadership and emergency command…). Use when someone asks what fell through the cracks, about silos, handovers, cross-functional or interface failures, who should have been talking to whom, or how to design a cross-department review after an incident.
---

# Interface Learnings

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py`. Needs `clusters.json`.

## Gather

```bash
PMLC interfaces <ws> --top 25
```

Each pair has **shared findings** (both entities named on the same finding) and **cross-entity causal mentions** (a finding owned by one entity names a factor owned by the other in its causal explanation). Rank interfaces by both. Take the top eight to twelve.

For each interface read the examples: `PMLC select <ws> --entity <A> <B> --brief`, then the full text of the highest-rated ones.

## For each interface, write

- **The seam**: what passes between the two functions (a work order, a part, a test, an alarm, a decision, a document).
- **What went wrong at the seam**: assumption, gap in ownership, missing hand-back, conflicting priorities, authority that sat with neither.
- **Why neither side saw it** on its own.
- **The learning** for each side in one sentence.
- **A joint fix**: a hold point, a shared check, a single owner, a handover record, a joint review. Name the control tier.
- **A leading indicator** both sides can see.
- Evidence trail.

## Output

`<run>/outputs/interface-learnings.md`: an interface matrix (entity × entity, top pairs highlighted), then one section per interface, then a short "who must meet whom" list that a site leader could turn into standing meetings or joint procedures.
