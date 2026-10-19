# cluster-learning-dossier

The complete learning dossier for one function (one Learning Cluster): its practices, the conditions it created or tolerated, its supervisory and organisational learnings, its interfaces, barriers, warning signs, messages for each level, recommendations, training needs and how far the learning transfers.

## What it is for

- "What does maintenance (or operations, engineering, fire services, HSE, procurement) need to learn from this?"
- A department-level lessons pack, with every learning for one function in one place.
- A set of dossiers, one per function, largest first, with an index.

## How to start it

- "Build the learning dossier for mechanical maintenance."
- "What does the emergency planning function need to learn from this investigation? Give me its dossier."
- "Make a dossier for every cluster, largest first."

## What it needs

- `clusters.json` from [learning-clusters](learning-clusters.md).
- The entity ID of the function, for example `F02` or `F09b`. The agent finds it from the name you give.
- For the interface and precursor parts, the outputs of `interfaces` and `timeline` (the skill runs them).

## Engine commands and flags

```bash
pmlc select <ws> --entity <F-id> --out <ws>/sel-<F-id>.md   # full text of the cluster
pmlc select <ws> --entity <F-id> --level 1 --brief          # one level at a time when the cluster is large
pmlc interfaces <ws>                                         # for S6, interfaces
pmlc timeline <ws> --before incident                         # for S8, precursors
pmlc check-pack <ws> <run>/outputs/dossier-<F-id>.json
pmlc pack <ws> <run>/outputs/dossier-<F-id>.json
```

- [select](../commands/select.md): `--entity` picks the function, `--level` one HFACS level, `--brief` short entries and `--out` writes the bundle to a file. There is no preset for this skill, because the entity changes each time.
- [interfaces](../commands/interfaces.md) and [timeline](../commands/timeline.md) feed sub-divisions S6 and S8.
- [check-pack](../commands/check-pack.md) and [pack](../commands/pack.md) render `dossier-<F-id>`.

For a cluster of more than about 60 findings, the skill works level by level so each pass stays grounded in the text.

## What you get

`dossier-<F-id>.html` and `.md`, one section per sub-division:

- S1 profile (counts by level, top-rated count, tiers and relations);
- S2 practice (L1), S3 conditions (L2), S4 supervision (L3) and S5 system (L4), three to eight learnings each;
- S6 interfaces, S7 barriers and S8 precursors;
- S9 one message for each tier, S10 recommendations, S11 competence, S12 transferability, S13 comparison (only with a comparator report) and S14 formats.

For all clusters you also get `dossier-index`, a table of every dossier.

## Worked example (Hazira)

On Hazira, `select --entity F02` returned 194 findings for Mechanical Maintenance, split 22, 36, 86 and 50 across levels 1 to 4. That is well over 60, so the skill works level by level: `select --entity F02 --level 1 --brief` returned the 22 Unsafe Acts findings. `timeline --before incident` wrote 92 dated precursor candidates for S8, and `interfaces` showed F02's strongest seam, with F01 Operations & Control Room (71 shared findings).

## Related skills

- [learning-clusters](learning-clusters.md): makes the clusters this skill opens.
- [interface-learnings](interface-learnings.md): the seams between this function and others, in depth.
- [barrier-learnings](barrier-learnings.md) and [precursor-timeline](precursor-timeline.md): S7 and S8 across all functions.
- [report-comparison](report-comparison.md): fills S13 when you have an official report.
