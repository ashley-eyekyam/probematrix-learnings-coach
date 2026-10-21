---
name: learning-clusters
description: Classifies every finding in a ProbeMatrix investigation export into Learning Clusters - the organisational entity that owns the learning (operations, maintenance, engineering, emergency response, HSE, leadership…), the tier that must learn (frontline to board) and the role's relation to the factor (actor, approver, owner, absent function…) - including the pass that resolves roles the rules cannot place, an organisation's own departments and the statutory posts named. Use when someone with a ProbeMatrix export asks who in the organisation should learn from it, wants findings grouped by department, role or level, or before any audience-specific learning. Not for the dashboard or the organisation-wide learning plan (use `organisation-learning-map`).
---

# Learning Clusters

Step 1 of the Learnings Coach method: put every finding with the people who own its learning.

Engine: `PMLC` as in `learnings-coach/references/skill-common.md` §1; this skill needs the `learnings-coach` skill installed alongside it.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions; run `PMLC setup`
when only an .xlsx was given: it runs `classify` too). Needs: `workspace`. Read
`learnings-coach/references/learning-principles.md` and `learnings-coach/references/ontology.md` §3 (the
taxonomy: entities with their `tags`, tiers, relations).

## Gather

```bash
PMLC classify <ws>                                       # -> clusters.json, unresolved_roles.json, singleton_roles.json
PMLC select <ws> --text "<distinctive words>" --brief    # read the findings that use a doubtful role
PMLC table-item <ws> clusters                            # cluster table, ready to paste
PMLC table-item <ws> tiers                               # tier table
PMLC table-item <ws> relations                           # relation table
```

`classify` lists roles with no entity (F99) or no tier (T9) in `<ws>/unresolved_roles.json`, and roles that could
identify one person, each with a generalised label, in `<ws>/singleton_roles.json`. `clusters.json` also lists
`statutory_roles`: roles that name a statutory post (an occupier or factory manager, a COMAH operator, a mine
manager), each with its regime and findings. Each is a prompt to check the statutory duty, not a finding.

**Resolve the leftovers.** For each role string in `unresolved_roles.json` decide:
- **F**: one or more entity IDs ("Operations / maintenance manager" → F01, F02, F13 if it is a site-level role).
- **T**: one tier. Crews and technicians T1; supervisors, signatories, shift in-charges T2; managers, leads,
  authorities, owners T3; plant or site leadership T4; corporate functions, policy owners, directors, the board
  T5. Rank words beat the word "policy": a plant manager who owns a policy is T4.
- **R**: the relation from the qualifier in parentheses, else `actor`.

Check rule mappings that look wrong too, especially role strings naming a function and a rank together. Write
`<ws>/role_overrides.json` as `{"<role string>": {"F": ["F05"], "T": "T3", "R": "owner"}}` and re-run
`PMLC classify <ws>`: every later `classify` re-applies it (`--no-overrides` ignores it).

**Stop rule.** Repeat until F99 and T9 are empty or each remaining role is explained. If after two passes more
than 10% of findings still sit in F99 (the profile's "high F99 share"), stop: list the leftovers in the pack and
tell the user that tier and entity packs will miss those findings.

**The organisation's own structure.** If its departments differ (a hospital, a mine, an airline), give
`classify` the organisation's chart, a CSV with columns `department`, `entity` (optional F-id to extend),
`match` (keywords separated by `;`, or a regex) and `tier` (optional):

```bash
PMLC classify <ws> --org-chart <departments.csv>         # rows without an entity become F20, F21, …
PMLC classify <ws> --overlay india-process-site          # site or country role words (references/overlays/)
```

Both are remembered by later `classify` runs (`--no-org-chart`, `--no-overlay` forget them). For a full custom
taxonomy, copy `learnings-coach/references/taxonomy.json` and pass `--taxonomy <file>`; keep IDs stable once
outputs are shared, and give new entities `tags` (`emergency`, `supply`, `contractor` …) so the audience
skills, which select by tag, still find them.

## Write

Write `<run>/outputs/learning-clusters.json` in the shape in `learnings-coach/references/pack-schema.md`.

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/learning-clusters.json (repository only).

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | Where the learning sits; cite the highest-rated finding of each top cluster | `bottom_line` | up to 7 |
| 1 | `clusters` | Learning clusters | The `table-item clusters` table, with an `intro`: a finding can touch several clusters, so the counts add up to more than the findings | `table` | 1 |
| 2 | `tiers` | Tiers that must learn | The `table-item tiers` table | `table` | 1 |
| 3 | `relations` | Relation mix | The `table-item relations` table, with one example role per relation | `table` | 1 |
| 4 | `top-clusters` | Top clusters | One `para` per cluster, `group` = the cluster: what it owns and its highest-rated finding | `para` | up to 5 |
| 5 | `leftovers` | Unresolved items | Role string, Decision, Reason; write "(a personal name)", never the name | `table` | 1 |
| 6 | `statutory` | Statutory posts named | From `clusters.json` `statutory_roles`: Role, Statutory post, Regime, Findings; a prompt to check the duty, not a conclusion | `table` | optional, up to 1 |
| 7 | `taxonomy` | Taxonomy adaptation | Only if you used an org chart, overlay or custom taxonomy: what changed and why | `para` | optional |

## If the evidence is thin

Follow `skill-common.md` §6, and:
- **Few roles in the export:** the tables are short; say so, and do not split an entity to look fuller.
- **F99 stays high** (stop rule above): publish the pack with the leftovers listed, and name the share in the
  bottom line.
- **No statutory posts found:** leave the `statutory` section out.

## Not covered here

- The dashboard and the organisation-wide learning plan: `organisation-learning-map`.
- One cluster's learning in depth: `cluster-learning-dossier`.
- The seams between clusters: `interface-learnings`.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/learning-clusters.json --strict   # fix every problem it lists
PMLC pack <ws> <run>/outputs/learning-clusters.json                  # -> learning-clusters.html and .md
PMLC pack <ws> <run>/outputs/learning-clusters.json --format docx    # -> learning-clusters.docx, the tables as Word tables
```

Tell the user the F99 and T9 shares after resolution, and which audience packs the largest clusters point to.
