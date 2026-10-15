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

Produce `<run>/outputs/learning-clusters.md`:
- the cluster table printed by `classify` (entity, findings touching, L1/L2/L3/L4)
- the tier table
- the relation mix, with one example role per relation
- the top five clusters by highest-rated findings, with one sentence each on what kind of learning they own
- unresolved items and the decision taken on each

Note that a finding can touch several clusters, so cluster counts add up to more than the number of findings.
