---
name: organisation-learning-map
description: Produce the whole-organisation view of one ProbeMatrix investigation - an HTML dashboard and a learning plan showing which departments and which levels (frontline, supervisors, managers, site leaders, corporate, board) own which learnings, what each level must do, how strong the recommended fixes are, and the order to roll out audience packs. Use when someone asks for an overview, a dashboard, a heatmap, "who needs to learn what", an organisation-wide learning plan, a safety transformation view, or a starting point before producing audience-specific packs.
---

# Organisation Learning Map

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py` (this skill needs the `learnings-coach` skill installed alongside it). Needs `clusters.json` (resolve unresolved roles first if time allows; see `learning-clusters`).

## 1. Build the learnings (unless a register already exists)

A map of findings alone shows where the evidence sits, not what each level should learn. Build the Learnings Register first by following the `learnings-register` skill, including `tier_messages` for every learning. If the user only wants a quick overview, say that the map will show findings only and offer the register as the next step.

## 2. Build the dashboard

```bash
PMLC dashboard <ws> --register <run>/outputs/learnings-register.json \
     [--date <corrected date>] [--title "<plain title>"]      # if the profile flagged summary-sheet errors
#   -> <run>/outputs/organisation-learning-map.html
PMLC interfaces <ws> --top 10
```

With `--register`, the HTML has two tabs.
- **Overview:** the learning × tier matrix (hover a cell for the message; a row links to its detail), a learning plan per level, the control-tier profile of the recommendations, the findings heatmaps (entity × tier, entity × level), and the most frequent factors.
- **Detailed register:** every register field, each cited finding and evidence item in full, and stakeholder lenses (T1–T5, Investigator, Auditor).

Without `--register`, it is the single-page Overview. The page is self-contained (offline, light and dark mode) and carries the ProbeMatrix footer. Do not hand-edit the generated HTML; change the register JSON and re-run.

## 3. Write the learning plan

Write the pack `<run>/outputs/organisation-learning-plan.json` (schema: `learnings-coach/references/pack-schema.md`) with these sections:
1. **Where the learning sits**: three sentences on the shape of the map (which entities carry the most findings, how much sits at supervision and organisational level, which tiers are most involved).
2. **What each level must learn**: one short section per tier (frontline → board), listing the learnings with that tier's message, priority-1 first.
3. **Top learning owners**: six to eight clusters with the most priority-1 learnings or highest-rated findings, one sentence each.
4. **Strongest interfaces**: the top three pairs and what passes between them.
5. **Strength of fixes**: share of recommendations above the administrative tier, and where stronger fixes are missing.
6. **Rollout plan**: which audience packs to produce, in which order, and why (usually site leadership and supervisors first, then the largest clusters, then board and auditors). Name the skill for each.

The kinds that fill each numbered section:
1. `para`.
2. One section per tier, holding `learning` items: `lesson` = that tier's message and `owner` = the cluster, priority-1 first.
3. A `table` (Cluster, Priority-1 learnings, Why; `row_cites`).
4. A `table` (Interface, What passes between them).
5. A `para`, plus a `table` of recommendations per control tier.
6. A `table` (Order, Skill, Audience, Why). A rollout has an order, not dates.

Then:

```bash
PMLC check-pack <ws> <run>/outputs/organisation-learning-plan.json   # fix every problem it lists
PMLC pack <ws> <run>/outputs/organisation-learning-plan.json         # -> organisation-learning-plan.html (primary) and .md
```

Put data-quality corrections in `data_quality`, findings left out on purpose in `exclusions`, and same-condition findings in `supporting_cites`. Keep the plan to three or four pages. The dashboard and register carry the detail.
