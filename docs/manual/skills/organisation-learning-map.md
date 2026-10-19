# organisation-learning-map

The whole-organisation view of one investigation: an offline HTML dashboard and a short learning plan. It shows which functions and which levels own which learnings, what each level must do, how strong the recommended fixes are, and in which order to roll out the audience packs.

## What it is for

- An overview, a heat map or "who needs to learn what".
- An organisation-wide learning plan, or a starting point before choosing audience packs.
- A page leaders can open in a meeting without any software beyond a web browser.

## How to start it

- "Give me the organisation learning map for this investigation."
- "Who in the organisation needs to learn what, and in what order should we brief them?"
- "Build the dashboard with the register so I can see every learning by level."

## What it needs

- `clusters.json` from [learning-clusters](learning-clusters.md). Resolve unplaced roles first if there is time.
- A Learnings Register for the full map. Without one, the dashboard shows where the findings sit, not what each level should learn. The skill offers to build the register first with [learnings-register](learnings-register.md).

## Engine commands and flags

```bash
pmlc dashboard <ws> --register <run>/outputs/learnings-register.json [--date <corrected date>] [--title "<plain title>"]
pmlc interfaces <ws> --top 10
pmlc check-pack <ws> <run>/outputs/organisation-learning-plan.json
pmlc pack <ws> <run>/outputs/organisation-learning-plan.json
```

- [dashboard](../commands/dashboard.md) writes `organisation-learning-map.html`. `--register` adds the learnings, the plan per level and the strength of fixes. `--date`, `--title` and `--location` correct the header when the summary sheet is wrong. `--out` writes the page elsewhere. `--embed` sets how much of the records the page carries, and `--share` makes a masked copy for outside the organisation (see [Review and sharing](../Review-and-sharing.md)).
- [interfaces](../commands/interfaces.md) gives the strongest pairs of functions for the plan.
- [check-pack](../commands/check-pack.md) and [pack](../commands/pack.md) for the learning plan.

This skill uses no `select` filters: the dashboard reads the whole workspace.

## What you get

- `organisation-learning-map.html`. With a register it has two tabs:
  - **Overview:** the learning-by-tier matrix (hover a cell for the message), a plan per level, the control-tier profile of the recommendations, heat maps of findings by entity and tier, and the most frequent factors.
  - **Detailed register:** every register field, each cited finding and evidence item in full, and lenses for T1 to T5, investigators and auditors.
- `organisation-learning-plan.html` and `.md`: where the learning sits, what each level must learn, the top learning owners, the strongest interfaces, the strength of fixes and the rollout order (an order, not dates).

Do not edit the HTML by hand. Change the register or the plan JSON and run the command again.

## Worked example (Hazira)

With the sample register (25 learnings, 44 recommendations), `dashboard --register` printed `Dashboard written to …/outputs/organisation-learning-map.html`. `interfaces --top 10` put F01 Operations & Control Room and F02 Mechanical Maintenance at the top, with 71 shared findings and 391 cross-entity causal mentions, out of 125 pairs across 17 entities. The plan would therefore name that seam among the strongest interfaces. Its rollout order usually starts with site leadership and supervisors, then the largest clusters, then the board and auditors.

The committed sample page is [organisation-learning-map.html](https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/samples/2020-09-24-hazira-gas-release-fire/outputs/organisation-learning-map.html) (download it and open it in a browser).

These counts are from the base classification, before the resolution pass. After you place the remaining roles, or add an overlay, they change: on Hazira the india-process-site overlay alone moves F09b Emergency Planning & Command from 16 to 43 findings.

## Related skills

- [learnings-register](learnings-register.md): the register the map is built on.
- [interface-learnings](interface-learnings.md): what passes between the strongest pairs.
- [site-leadership-coach](site-leadership-coach.md) and [supervisor-coach](supervisor-coach.md): usually the first audience packs in the rollout.
- Recipe: [The organisation learning map dashboard](../Workflows-and-recipes.md#the-organisation-learning-map-dashboard).
