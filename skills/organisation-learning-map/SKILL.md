---
name: organisation-learning-map
description: Produces the whole-organisation view of one ProbeMatrix investigation export - an HTML dashboard and a learning plan showing which departments and levels (frontline, supervisors, managers, site leaders, corporate, board) own which learnings, what each level must do, how strong the fixes are, which pack reaches which learning, and a cascade plan for delivering the audience packs. It builds or reuses the Learnings Register. Use when someone with a ProbeMatrix export asks for an overview, a dashboard, a heatmap, "who needs to learn what", an organisation-wide learning or cascade plan, or a starting point before audience packs. Not for classifying findings or resolving roles (use `learning-clusters`), or for the register workbook alone (use `learnings-register`).
---

# Organisation Learning Map

Engine: `PMLC` as in `learnings-coach/references/skill-common.md` §1; this skill needs the `learnings-coach` skill installed alongside it.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions; run `PMLC setup`
when only an .xlsx was given). Needs: `workspace`, `clusters`, `register`. Optional: `interfaces`, `adoption`,
`distribution`. Read `learnings-coach/references/learning-principles.md`,
`learnings-coach/references/barriers-and-controls.md` (control tiers) and
`learnings-coach/references/audiences.md` (which skill serves which audience).

**The register comes first.** A map of findings alone shows where the evidence sits, not what each level should
learn. If `<run>/outputs/learnings-register.json` exists, reuse it; otherwise build it with `learnings-register`,
with `tier_messages` for every learning. If the user wants only a quick overview, say the dashboard will show
findings only, and offer the register as the next step.

## Gather

```bash
PMLC dashboard <ws> --register <run>/outputs/learnings-register.json   # -> <run>/outputs/organisation-learning-map.html
PMLC register-items <ws> --tier T2                       # a tier's learnings as ready items (repeat per tier)
PMLC table-item <ws> hoc --register <run>/outputs/learnings-register.json   # recommendations per control tier
PMLC table-item <ws> interfaces --top 3                  # the strongest interfaces
PMLC table-item <ws> nine-m --register <run>/outputs/learnings-register.json   # learnings per M, when the register has nine_m values
```

Add `--date <corrected date>` and `--title "<plain title>"` to `dashboard` when the profile flagged the
summary-sheet date. With `--register` the HTML has two tabs: **Overview** (the learning × tier matrix, a plan per
level, the control-tier profile, heatmaps, the most frequent factors, the **learnings × packs matrix** counted
from the `learning` ids in `<run>/outputs/*.json`, and the **reach** per pack from `distribution.csv`) and
**Detailed register**. Re-run `dashboard` after writing packs or after the organisation fills in
`distribution.csv`. Never hand-edit the HTML: change the register or packs and re-run.

## Write

Write `<run>/outputs/organisation-learning-plan.json` (the pack is named `organisation-learning-plan`) in the
shape in `learnings-coach/references/pack-schema.md`. Keep it to three or four pages; the dashboard carries the
detail.

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/organisation-learning-plan.json (repository only)

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | Which clusters and tiers own the priority-1 learnings, and the first packs to deliver | `bottom_line` | up to 7 |
| 1 | `where` | Where the learning sits | Which entities carry the most findings, how much sits at supervision and organisational level, which tiers are most involved | `para` | up to 3 |
| 2 | `t[1-5]` | What each level must learn | One section per tier (`t1` … `t5`) that must act: the `register-items` output for that tier (it carries the tier's message and `learning: "LR-nn"`), adding `owner` = the cluster; priority-1 first | `learning` | up to 8 |
| 3 | `owners` | Top learning owners | Cluster, Priority-1 learnings, Why; up to eight clusters; `row_cites` | `table` | 1 |
| 4 | `interfaces` | Strongest interfaces | Interface, What passes between them; the top three pairs | `table` | 1 |
| 5 | `fixes` | Strength of fixes | The share of recommendations above the administrative tier, and where stronger fixes are missing | `para` | up to 2 |
| 5 | `fixes` | Strength of fixes | The `table-item hoc` table | `table` | 1 |
| 6 | `nine-m` | Learnings by M (9M) | The `table-item nine-m` table, pasted unchanged; only when the register has `nine_m` values | `table` | optional, up to 1 |
| 7 | `cascade` | Cascade plan | A `table` with the columns Audience, Pack, Channel, Deliverer role, Window (relative weeks), Feedback, Completion measure; one row per audience pack, `row_cites` | `table` | 1 |

**The cascade** replaces the old rollout order. Each row names the audience, the pack name as `distribution.csv` will record it (with the skill that
writes it, from `audiences.md`), the channel (toolbox talk, briefing, committee, board paper), the deliverer role (a
role, never a person), the window (relative weeks), such as "weeks 1–2", how feedback comes back (questions raised,
concerns escalated) and the completion measure (for example "every crew has a `distribution.csv` row"). It has
no dates and no names: the organisation sets those. Usually site leadership and supervisors come first, then the
largest clusters, then board and auditors.

## If the evidence is thin

Follow `skill-common.md` §6, and:
- **No register and the user wants only an overview:** write `where`, `owners` and `interfaces` from the
  findings, leave out the tier sections, and add a `limits` line that the plan needs the register.
- **A tier with nothing to act on** (no `tier_messages` for it): leave its section out and say so in `where`.
- **No interfaces with shared findings:** keep the `interfaces` table to the pairs `interfaces` printed.

## Not covered here

- Classifying findings and resolving roles: `learning-clusters`.
- The register workbook and its checks: `learnings-register`.
- The audience packs themselves: the skills named in the cascade.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/organisation-learning-plan.json --strict   # fix every problem it lists
PMLC pack <ws> <run>/outputs/organisation-learning-plan.json                  # -> organisation-learning-plan.html and .md
PMLC pack <ws> <run>/outputs/organisation-learning-plan.json --format pptx     # the plan as slides for the leadership team
PMLC pack <ws> <run>/outputs/organisation-learning-plan.json --format email    # a digest to the deliverer roles
PMLC templates <ws> distribution                         # next: the delivery record the organisation fills in
```

Give the user the dashboard path and the plan path. Offer the slides when the plan is presented, and the email
digest (`.email.html` and `.email.txt`) when the cascade starts by mail; the format for each channel is in
`skill-common.md` §8. The next step is `PMLC templates <ws> distribution`: it writes
`<run>/outputs/distribution.csv`, which the organisation fills in as packs are delivered (never you), and which
the dashboard reads for reach. It refuses to overwrite a file that already holds entries.
