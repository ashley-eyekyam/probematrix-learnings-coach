---
name: learning-clusters
description: Classify every finding in a ProbeMatrix investigation export into Learning Clusters - the organisational entity that owns the learning (operations, maintenance, engineering, emergency response, HSE, leadership…), the tier that must learn (frontline to board) and the role's relation to the factor (actor, approver, owner, absent function…). Use when someone asks who in the organisation should learn from an investigation, wants findings grouped by department, role or level, or before producing any audience-specific learning from a ProbeMatrix export. Includes the LLM pass that resolves roles the rules cannot place.
---

# Learning Clusters

Step 1 of the Learnings Coach method: put every finding with the people who own its learning.

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py` (`<skills-root>` is the folder that contains this skill). If the workspace does not exist yet, follow Step 1 of the `learnings-coach` skill. Read `learnings-coach/references/ontology.md` §3 for the taxonomy.

## 1. Run the rules

```bash
PMLC classify <ws>
```

This writes `<ws>/clusters.json` and lists roles with no entity (F99) or no tier (T9) in `<ws>/unresolved_roles.json`.

## 2. Resolve the leftovers (the LLM pass)

Read `unresolved_roles.json`. For each role string decide:
- **F**: one or more entity IDs. A role can belong to several ("Operations / maintenance manager" → F01, F02, F13 if it is a site-level role).
- **T**: one tier. Infer from the wording: crews and technicians T1; supervisors, signatories, shift in-charges T2; managers, leads, authorities, owners T3; plant or site leadership T4; corporate, policy owners, directors T5.
- **R**: the relation from the qualifier in parentheses, else `actor`.

Then check the rule-based mappings that look wrong. Look especially at role strings that name a function and a rank together. When in doubt, read the findings that use the role: `PMLC select <ws> --text "<distinctive words>" --brief`.

Write the decisions to `<ws>/role_overrides.json` as `{"<role string>": {"F": ["F05"], "T": "T3", "R": "owner"}}` and re-run:

```bash
PMLC classify <ws> --overrides <ws>/role_overrides.json
```

Repeat until F99 and T9 are empty or each remaining case is explained.

## 3. Adapt the taxonomy (when the organisation is different)

If the user's organisation has different departments (e.g. a hospital, a mine, an airline), copy `learnings-coach/references/taxonomy.json`, edit the entities and regexes, and run `PMLC classify <ws> --taxonomy <file>`. Keep IDs stable once outputs are shared.

## 4. Report

Write the pack `<run>/outputs/learning-clusters.json` (schema: `learnings-coach/references/pack-schema.md`), then:

```bash
PMLC check-pack <ws> <run>/outputs/learning-clusters.json   # fix every problem it lists
PMLC pack <ws> <run>/outputs/learning-clusters.json         # -> learning-clusters.html (primary) and .md
```

Sections and the kinds that fill them:
- **Cluster table:** a `table` copied from `classify`, with columns Entity, Findings, L1, L2, L3 and L4, plus `row_cites`. Give the section an `intro` saying that a finding can touch several clusters, so the counts add up to more than the number of findings.
- **Tier table:** a `table`.
- **Relation mix:** a `table` with one example role per relation.
- **Top five clusters:** one `para` each, with `group` = the cluster.
- **Unresolved items:** a `table` with columns Role string, Decision and Reason. Write "(a personal name)", never the name.
- **Taxonomy adaptation:** a `para`, only if you did step 3.

The bottom line cites the highest-rated finding of each top cluster. Put data-quality corrections in `data_quality`.

```json
{"kind": "table", "columns": ["Entity", "Findings", "L1", "L2", "L3", "L4"],
 "rows": [["F02 Mechanical Maintenance", 2, 1, 0, 1, 0]], "row_cites": [["FND-…", "FND-…"]]}
```
