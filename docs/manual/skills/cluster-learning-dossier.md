# cluster-learning-dossier

The complete learning dossier for one department or function (a Learning Cluster). A two-page front sheet comes first: the top five learnings, three decisions and three indicators. Behind it, the dossier opens the cluster along sub-divisions S1 to S14 and writes one learning piece for each one the evidence supports: practice, conditions, supervision, system, interfaces, barriers, precursors, tier messages, recommendations, competence, transferability, comparison and formats.

## What it is for

- "What does maintenance (or operations, engineering, fire services, HSE, procurement) need to learn from this investigation?"
- A department-level lessons pack.
- Every learning for one function in one place.

The dossier is the function's reference file across every tier. The T3 managers' own action agenda across functions belongs to [manager-coach](manager-coach.md).

## How to start it

- "What does mechanical maintenance need to learn from this investigation?"
- "Give me the complete lessons pack for our fire services, with a front sheet for the department head."
- "Write one dossier for each department, largest first, with an index."

## What it needs

- `clusters.json` from [learning-clusters](learning-clusters.md).
- The interface matrix and the precursor candidates, which `setup` writes.
- At least 3 findings for the entity: below that, the skill skips the dossier and says so.

## Engine commands and flags

```bash
pmlc select <ws> --entity <F-id> --count-by level                                # size and S1 counts
pmlc select <ws> --entity <F-id> --budget-chars 60000 --out <ws>/sel-<F-id>.md   # full text, highest-rated first
pmlc select <ws> --entity <F-id> --fields short,code,level,rating --budget-chars 60000   # index: every finding, one line each
pmlc select <ws> --entity <F-id> --level 1 --fields label,short,justification,code,rating --budget-chars 60000   # then levels 2, 3, 4
pmlc table-item <ws> entity-tier --entity <F-id>                                 # S1 table, ready to paste
pmlc interfaces <ws>                                                             # S6
pmlc timeline-item <ws> --before incident --top 12                               # S8
pmlc check-pack <ws> <run>/outputs/dossier-<F-id>.json --strict
pmlc pack <ws> <run>/outputs/dossier-<F-id>.json
pmlc pack <ws> <run>/outputs/dossier-<F-id>.json --format docx   # the reference file in Word
pmlc dossier-index <ws>                                                          # the index of every dossier
```

- [select](../commands/select.md): `--entity` limits the bundle to one cluster; `--count-by level` prints only the counts; `--budget-chars` keeps findings in rating order within a character budget and says how many it dropped; `--out` saves the bundle; `--fields` keeps only the named parts of each finding (`short,code,level,rating` for the index; adding `label` and `justification` for the level passes), so each 60,000-character pass holds more findings; `--level` reads one level at a time.
- [table-item](../commands/table-item.md) `entity-tier`, [interfaces](../commands/interfaces.md) and [timeline-item](../commands/timeline-item.md) give S1, S6 and S8.
- [check-pack](../commands/check-pack.md) with `--strict` and [pack](../commands/pack.md) render each dossier. The pack is named `dossier-<F-id>` (for example `dossier-F02` or `dossier-F09b`), and its scope is that one entity.
- [dossier-index](../commands/dossier-index.md) writes `dossier-index.json` from the dossier packs; render it with `pack`.

## What you get

`dossier-<F-id>.html` and `.md`:

- the **front sheet**: the top five learnings as the bottom line, then three decisions and three indicators, two pages with S1;
- **S1 Profile**: counts by level and tier, and a note naming any sub-division left out because no learning could be grounded;
- **S2 to S5**: up to eight learnings each for practice, conditions, supervision and the system;
- **S6 Interfaces**, **S7 Barriers** and **S8 Precursors**;
- **S9 Tier messages**: one short message per tier, from the register's tier messages when it exists;
- **S10 Recommendations**, **S11 Competence** and **S12 Transferability**;
- **S13 Comparison**, only when an official report is supplied;
- **S14 Formats**: which learnings become Learning Cards, brief paragraphs or toolbox talks.

For all clusters, one dossier per cluster with at least 3 findings, largest first, and a `dossier-index` pack.

With `--format docx`, `dossier-<F-id>.docx` is the function's reference file in Word. The S14 Formats table names, for each learning, the skill and layout that carries it, such as `frontline-learning-cards --layout toolbox`.


## Worked example (Hazira)

On Hazira, `select --entity F02 --count-by level` showed 194 findings for Mechanical Maintenance, split 22, 36, 86 and 50 across levels 1 to 4. `--budget-chars 60000` kept the 19 highest-rated in full and reported `Dropped for budget: 175 findings (lowest kept rating 4)`, so the skill reads an index of all 194 (`--fields short,code,level,rating`, about 43,000 characters) and then each level with its justifications: the four passes kept 22 of 22, 36 of 36, 38 of 86 and 41 of 50 findings in full, 137 of 194 in all. `interfaces` showed F02's strongest seam, with F01 Operations & Control Room (71 shared findings).

These counts are from the base classification, before the resolution pass. After you place the remaining roles, or add an overlay, they change: on Hazira the india-process-site overlay alone moves F09b Emergency Planning & Command from 16 to 43 findings.

## Related skills

- [learning-clusters](learning-clusters.md): makes the clusters this skill opens.
- [manager-coach](manager-coach.md): the T3 action agenda, which can reuse dossier items.
- [interface-learnings](interface-learnings.md): the seams between this function and others, in depth.
- [barrier-learnings](barrier-learnings.md) and [precursor-timeline](precursor-timeline.md): S7 and S8 across all functions.
- [report-comparison](report-comparison.md): fills S13 when you have an official report.
