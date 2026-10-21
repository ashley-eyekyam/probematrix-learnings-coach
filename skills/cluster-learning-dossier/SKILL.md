---
name: cluster-learning-dossier
description: Produces the complete learning dossier for one department or function (a Learning Cluster) from a ProbeMatrix investigation export - a two-page front sheet, then every learning for that function at every tier, from frontline practice to organisational influences, with its interfaces, barriers, warning signs and recommendations. Use when someone asks "what does maintenance (or operations, engineering, fire services, HSE, procurement) need to learn from this investigation", wants a department-level lessons pack, or wants every learning for one function in one place from a ProbeMatrix export. Not for the T3 managers' own action agenda across functions (use `manager-coach`).
---

# Cluster Learning Dossier

Steps 2 and 3 of the method for one Learning Cluster: open it along sub-divisions S1–S14 (`learnings-coach/references/ontology.md` §4) and write one learning piece per sub-division that the evidence supports. The dossier is the function's reference file across all tiers; a department head reads the two-page front sheet first. Read `learnings-coach/references/learning-principles.md` first.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 and §2.

Engine: `PMLC`, as `skill-common.md` §1 defines it (this skill needs the `learnings-coach` skill installed alongside it).

This skill needs the **workspace** and **clusters** (see `learning-clusters`). It uses, when present: the register (`<run>/outputs/learnings-register.json`), the interfaces and the timeline.

- **Which cluster.** When the user names a department in words ("maintenance"), map it to its F-id with `learnings-coach/references/ontology.md` §3.1 or the `classify` output, and confirm it in one line.
- **Size floor.** `PMLC select <ws> --entity <F-id> --count-by level` gives the cluster's size. Skip the dossier for an entity with fewer than 3 findings: say so, and point to the register or `manager-coach` instead.
- Start from the register if present: carry `learning: "LR-nn"` on items that express a register learning, and take S9 from its `tier_messages`.

## Gather

```bash
PMLC select <ws> --entity <F-id> --count-by level                                       # size floor and S1 counts
PMLC select <ws> --entity <F-id> --budget-chars 60000 --out <ws>/sel-<F-id>.md          # full text, highest-rated first
PMLC select <ws> --entity <F-id> --level 1 --brief                                      # level by level for large clusters
PMLC table-item <ws> entity-tier --entity <F-id>                                        # S1: findings by tier, ready to paste
PMLC interfaces <ws>                                                                    # S6: pairs involving this entity
PMLC timeline-item <ws> --before incident --top 12                                      # S8: dated warnings (keep this entity's)
```

The `--budget-chars` call keeps findings in rating order and says how many it dropped. For a cluster with more than about 60 findings, read the dropped ones level by level (`--level 1` to `--level 4`) so each pass stays grounded.

## Write

Write the pack `<run>/outputs/dossier-<F-id>.json` in the shape in `learnings-coach/references/pack-schema.md` (`pack` = `dossier-<F-id>`, such as `dossier-F02` or `dossier-F09b`). Set `"scope": {"entities": ["<F-id>"]}`. Give each sub-division its own section, `id` = `s<n>-<name>`. **Omit a sub-division with no grounded learning** and name it in the S1 note.

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/dossier-F02.json (repository only).

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | Front sheet: the top five learnings for this entity | `bottom_line` | up to 5 |
| 0 | `front-sheet` | Front sheet: decisions and indicators | The three decisions the function's leadership should take | `decision` | up to 3 |
| 0 | `front-sheet` | (same section) | The three indicators that would show the learning has been applied, with `deterioration` | `indicator` | up to 3 |
| S1 | `s1-*` | S1 Profile | Counts by level and tier, top-rated count (the `entity-tier` table) | `table` | 1 |
| S1 | `s1-*` | (same section) | The note naming each omitted sub-division and why | `para` | optional, up to 1 |
| S2 | `s2-*` | S2 Practice (L1) | The practices that contributed, why each made sense at the time | `learning` | optional, up to 8 |
| S3 | `s3-*` | S3 Conditions (L2) | The conditions this entity created or tolerated | `learning` | optional, up to 8 |
| S4 | `s4-*` | S4 Supervision (L3) | What supervisors should see, check, correct and refuse | `learning` | optional, up to 8 |
| S5 | `s5-*` | S5 System (L4) | Systems, resources, policies and norms that must change | `learning` | optional, up to 8 |
| S6 | `s6-*` | S6 Interfaces | What fell between this entity and others; who must talk to whom | `para` | optional, up to 2 |
| S6 | `s6-*` | (same section) | The interface learnings | `learning` | optional, up to 8 |
| S7 | `s7-*` | S7 Barriers | Barriers this entity owns: type, state, failure_mode, hoc_tier, fix | `barrier` | optional, up to 8 |
| S8 | `s8-*` | S8 Precursors | Dated warnings and what was done with them (`signal`, `received_by`, `response`) | `timeline` | optional, up to 1 |
| S9 | `s9-*` | S9 Tier messages | One short message per tier, `group` = the tier | `para` | optional, up to 5 |
| S10 | `s10-*` | S10 Recommendations | What should change, barrier, evidence, control tier, leading indicator | `recommendation` | optional, up to 8 |
| S11 | `s11-*` | S11 Competence | Columns Tier, Competence | `table` | optional, up to 1 |
| S12 | `s12-*` | S12 Transferability | Columns Learning, Reach, Reason | `table` | optional, up to 1 |
| S13 | `s13-*` | S13 Comparison | Only when a comparator report is supplied (`report-comparison`) | `para` | optional, up to 3 |
| S14 | `s14-*` | S14 Formats | Columns Learning, Format: the skill and engine layout or format that carries it, such as `frontline-learning-cards --layout cards`, `frontline-learning-cards --layout toolbox`, `board-brief --layout paper` or `--format docx` | `table` | optional, up to 1 |

Rules for the content:

- **Learnings.** One sentence of lesson plus two to four sentences of explanation, with the evidence trail. Merge findings that describe the same condition into one learning; the engine adds the evidence trail.
- **Front sheet.** The bottom line, the `front-sheet` section and S1 together fit on two pages. Decisions and indicators there are the function's own; site-wide ones go to `site-leadership-coach`.
- **All clusters.** Write one dossier per cluster with at least 3 findings, largest first, then build the index: `PMLC dossier-index <ws>` writes `<run>/outputs/dossier-index.json` from the dossier packs, and `PMLC pack <ws> <run>/outputs/dossier-index.json` renders it. Never hand-write the index.

```json
{"kind": "learning", "lesson": "Supervisors had no checklist to refuse a restart against.", "explanation": "…", "learning": "LR-01", "cites": ["FND-…"]}
```

## If the evidence is thin

- **Fewer than 3 findings for the entity:** no dossier (size floor above).
- **A sub-division with no grounded learning:** leave its section out and name it in the S1 note; never write a learning to fill it.
- **The budget call dropped findings:** say in `limits` how many were read level by level and how many not at all.

## Not covered here

- The T3 managers' action agenda across functions: `manager-coach` (it may reuse this dossier's items).
- Grouping the whole organisation into clusters: `learning-clusters`.
- The full barrier analysis and interface review: `barrier-learnings`, `interface-learnings`.

## Check and hand over

Run `learnings-coach/references/skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/dossier-<F-id>.json --strict   # fix every problem it lists
PMLC pack <ws> <run>/outputs/dossier-<F-id>.json                  # -> dossier-<F-id>.html (open first) and .md
PMLC pack <ws> <run>/outputs/dossier-<F-id>.json --format docx    # -> dossier-<F-id>.docx, the function's reference file in Word
```

Several dossiers: `PMLC check-all <ws> --strict`, then `PMLC dossier-index <ws>` and `PMLC render-all <ws>`. Also confirm: the front sheet fits two pages and every omitted sub-division is named in S1. Next: `manager-coach` for the function's 90-day agenda.
