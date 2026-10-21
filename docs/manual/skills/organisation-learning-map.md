# organisation-learning-map

The whole-organisation view of one investigation: an offline HTML dashboard and a short learning plan. It builds or reuses the Learnings Register, and shows which functions and which levels own which learnings, what each level must do, how strong the recommended fixes are, which pack reaches which learning, and a cascade plan for delivering the audience packs.

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
- A Learnings Register for the full map: the skill builds or reuses one. Without it, the dashboard shows where the findings sit, not what each level should learn. The skill offers to build the register first with [learnings-register](learnings-register.md).
- Optionally `distribution.csv`, filled in by the organisation as packs are delivered: the dashboard reads it for the reach of each pack.

## Engine commands and flags

```bash
pmlc dashboard <ws> --register <run>/outputs/learnings-register.json [--date <corrected date>] [--title "<plain title>"]
pmlc register-items <ws> --tier T2                                   # a tier's learnings as ready items
pmlc table-item <ws> hoc --register <run>/outputs/learnings-register.json
pmlc table-item <ws> interfaces --top 3
pmlc check-pack <ws> <run>/outputs/organisation-learning-plan.json --strict
pmlc pack <ws> <run>/outputs/organisation-learning-plan.json
pmlc pack <ws> <run>/outputs/organisation-learning-plan.json --format pptx    # the plan as slides
pmlc pack <ws> <run>/outputs/organisation-learning-plan.json --format email   # a digest to the deliverer roles
pmlc templates <ws> distribution                                     # next: the delivery record
```

- [dashboard](../commands/dashboard.md) writes `organisation-learning-map.html`. `--register` adds the learnings, the plan per level, the strength of fixes, the learnings × packs matrix (from the `learning` ids in the packs in `outputs/`) and the reach of each pack (from `distribution.csv`). `--date`, `--title` and `--location` correct the header when the summary sheet is wrong. `--out` writes the page elsewhere. `--embed` sets how much of the records the page carries, and `--share` makes a masked copy for outside the organisation (see [Review and sharing](../Review-and-sharing.md)).
- [register-items](../commands/register-items.md) with `--tier` prints one tier's learnings, with their `LR-nn` ids, as ready items for the plan.
- [table-item](../commands/table-item.md) `hoc` with `--register` counts the register's recommendations per control tier; `interfaces` with `--top` gives the strongest pairs.
- [check-pack](../commands/check-pack.md) with `--strict` and [pack](../commands/pack.md) check and render the learning plan.
- [templates](../commands/templates.md) `distribution` writes `distribution.csv` for the organisation to fill in as packs are delivered. It never overwrites a file that already exists.

This skill uses no `select` filters: the dashboard reads the whole workspace.

## What you get

- `organisation-learning-map.html`. With a register it has two tabs:
  - **Overview:** the learning-by-tier matrix (each cell holds its message for screen readers; the **Show the messages in the table** button shows them on screen), a plan per level, the control-tier profile of the recommendations, heat maps of findings by entity and tier, the most frequent factors, the learnings × packs matrix and the reach of each pack.
  - **Detailed register:** every register field, each cited finding and evidence item in full, and lenses for T1 to T5, investigators and auditors.
- `organisation-learning-plan.html` and `.md`: where the learning sits, what each level must learn (with each learning's `LR-nn`), the top learning owners, the strongest interfaces, the strength of fixes and the **cascade plan**.
- The cascade plan replaces the old rollout order. It is a table with the columns audience, pack, channel, deliverer role, window (relative weeks), feedback and completion measure. It names roles, never people, and relative weeks, never dates: the organisation sets those.
- The next step: `distribution.csv`, the delivery record the organisation fills in.

Do not edit the HTML by hand. Change the register or the plan JSON and run the command again.

**Formats.** The learning plan also renders as slides (`--format pptx`) for the leadership team and as an email digest (`--format email`) when the cascade starts by mail; see [pack](../commands/pack.md). The dashboard stays HTML.


## Worked example (Hazira)

With the sample register (25 learnings, 44 recommendations), `dashboard --register` printed `Dashboard written to …/outputs/organisation-learning-map.html`. `interfaces --top 10` put F01 Operations & Control Room and F02 Mechanical Maintenance at the top, with 71 shared findings and 391 cross-entity causal mentions, out of 126 pairs across 17 entities (with the india-process-site overlay). The plan would therefore name that seam among the strongest interfaces. Its cascade usually starts with site leadership and supervisors, then the largest clusters, then the board and auditors.

`templates distribution` printed `wrote …/outputs/distribution.csv (0 rows); the organisation fills in the blank columns`: no pack had been written yet, so the file holds only the header row (pack, audience, channel, date, delivered_by_role, attendees, contractors_included, questions_raised, concerns_escalated).

The committed sample page is [organisation-learning-map.html](https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/samples/2020-09-24-hazira-gas-release-fire/outputs/organisation-learning-map.html) (download it and open it in a browser).

These counts depend on the classification. After you place the remaining roles, or add an overlay, they change: on Hazira the india-process-site overlay alone moves F09b Emergency Planning & Command from 16 to 43 findings.

## Related skills

- [learnings-register](learnings-register.md): the register the map is built on.
- [interface-learnings](interface-learnings.md): what passes between the strongest pairs.
- [site-leadership-coach](site-leadership-coach.md) and [supervisor-coach](supervisor-coach.md): usually the first audience packs in the rollout.
- Recipe: [The organisation learning map dashboard](../Workflows-and-recipes.md#the-organisation-learning-map-dashboard).
