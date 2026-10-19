# learning-clusters

Puts every finding with the people who own its learning: the function (the **entity**), the level of the organisation (the **tier**) and the kind of involvement (the **relation**). Together these make a **Learning Cluster**. See the [Glossary](../Glossary.md) for each term.

## What it is for

- Answering "who in the organisation should learn from this investigation?"
- Grouping findings by department, role or level.
- Placing the role strings that the rules could not place (the resolution pass), so that tier-based packs are complete.
- Adapting the list of functions to an organisation that is not a process plant, such as a hospital, a mine or an airline.

Most audience skills need this step first.

## How to start it

- "Which departments and levels does this investigation say should learn?"
- "Resolve the unplaced roles before we make the supervisor pack."
- "Our site uses Indian process-plant titles. Apply the site overlay and re-check the clusters."

## What it needs

- A workspace made by [learnings-coach](learnings-coach.md) (`ingest`).
- For the resolution pass: your knowledge of the site's job titles. The agent proposes a function, a tier and a relation for each unplaced role, and you can correct them.
- Optionally, your own copy of the taxonomy (the list of functions) or an overlay file of site-specific role words.

## Engine commands and flags

```bash
pmlc classify <ws>                                   # rules first
pmlc select <ws> --text "<distinctive words>" --brief  # read the findings that use a puzzling role
pmlc classify <ws>                                   # again, after writing role_overrides.json
pmlc classify <ws> --overlay india-process-site      # add site role words (remembered next time)
pmlc classify <ws> --taxonomy my-taxonomy.json       # a different list of functions
pmlc classify <ws> --no-overlay                      # drop the overlay again
```

- [classify](../commands/classify.md) writes `clusters.json`, `unresolved_roles.json` and `singleton_roles.json`. It reads `role_overrides.json` on every run; `--overrides FILE` names another file and `--no-overrides` ignores it. A plain `classify` reuses the taxonomy and overlays of the previous run.
- [select](../commands/select.md) with `--text` (a search over the finding text) and `--brief` (short entries) shows the findings behind a role.
- Then [check-pack](../commands/check-pack.md) and [pack](../commands/pack.md) for the `learning-clusters` report.

## What you get

- `clusters.json`: every finding's entities, tiers and relations.
- `unresolved_roles.json`: roles with no entity (F99) or no tier (T9).
- `singleton_roles.json`: roles that could point to one person, each with a general label to use instead.
- `role_overrides.json`: your corrections, kept for every later run.
- A report pack `learning-clusters.html` and `.md`: the cluster table, the tier table, the relation mix, the five largest clusters and the decisions on unplaced roles.

## Worked example (Hazira)

The first `classify` on Hazira placed 630 distinct role strings and reported 96 that need resolution. 27 findings had an unplaced entity (F99) and 98 touched an unplaced tier (T9). The largest clusters were F02 Mechanical Maintenance (194 findings) and F01 Operations & Control Room (170).

`singleton_roles.json` listed 15 roles. For example "Director Offshore (approval authority)" is the only role of its kind, so the general label "Corporate & Board (Corporate / board)" is used instead.

Adding one correction, `{"Area Supervisor": {"F": ["F01"], "T": "T2", "R": "actor"}}`, to `role_overrides.json` and re-running `classify` printed `Applied 1 override(s)` and brought the count to 95. Running with `--overlay india-process-site` then brought it to 86: F09b Emergency Planning & Command grew from 16 to 43 findings, and F99 fell from 27 to 13.

## Related skills

- [learnings-coach](learnings-coach.md): makes the workspace this skill reads.
- [cluster-learning-dossier](cluster-learning-dossier.md): opens one cluster in full.
- [organisation-learning-map](organisation-learning-map.md): shows all clusters on one page.
- Recipe: [Correct a role and keep the correction](../Workflows-and-recipes.md#correct-a-role-and-keep-the-correction).
