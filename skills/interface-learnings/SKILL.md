---
name: interface-learnings
description: Finds the learnings that fall between departments in a ProbeMatrix investigation export - handovers, shared ownership, unclear authority and assumptions one function made about another (operations and maintenance, maintenance and procurement, engineering and integrity, control room and emergency command) - with a learning for each side, a joint fix with a co-owner and a joint-review agenda. Use when someone with a ProbeMatrix export asks what fell through the cracks, about silos, handovers, cross-functional or interface failures, who should have been talking to whom, or how to run a cross-department review after an incident. Not for one department's whole learning (use `cluster-learning-dossier`).
---

# Interface Learnings

Engine: `PMLC` as in `learnings-coach/references/skill-common.md` §1; this skill needs the `learnings-coach` skill installed alongside it.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions; run `PMLC setup`
when only an .xlsx was given). Needs: `workspace`, `interfaces` (`setup` writes `interfaces.json`; the pairs need
`clusters.json`, so resolve unresolved roles first if many findings sit in F99). Optional: the register. Read
`learnings-coach/references/learning-principles.md` and `learnings-coach/references/barriers-and-controls.md`
(the barrier names, prevention and mitigation sides, and control tiers).

## Gather

```bash
PMLC interfaces <ws> --top 25                            # pairs: shared findings and cross-entity causal mentions
PMLC table-item <ws> interfaces --top 12                 # the matrix table, ready to paste
PMLC select <ws> --entity <A> <B> --entity-mode all --brief            # the findings both entities share
PMLC select <ws> --entity <A> --tag emergency --entity-mode all --brief  # A with any emergency-response entity
```

Each pair has **shared findings** (both entities named on one finding) and **cross-entity causal mentions** (a
finding owned by one entity names a factor owned by the other). Rank by the two together; break ties by the
higher-rated findings. Take up to 12 pairs, then read the full text of the highest-rated shared findings.
**Include at least one mitigation-side interface** (detection and alarm, isolation, communication and escalation,
emergency command) when the evidence supports one: the second `select` line finds them.

## Write

Write `<run>/outputs/interface-learnings.json` in the shape in `learnings-coach/references/pack-schema.md`.

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/interface-learnings.json (repository only).

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | The seams that carried the most risk, and which side of the event each sits on | `bottom_line` | up to 7 |
| 1 | `matrix` | Interface matrix | The `table-item interfaces` table (Interface, Shared findings, Cross-entity causal mentions; `row_cites`) | `table` | 1 |
| 2 | `*` | One section per interface | Section `id` = the entity pair, **lower id first** (`f02-f06`, never `f06-f02`). `para` items with `group` = "The seam" (what passes between them: a work order, a part, a test, an alarm, a decision), "What went wrong at the seam" (assumption, ownership gap, missing hand-back, authority with neither), "Why neither side saw it" | `para` | up to 3 |
| 2 | `*` | One section per interface | The learning for each side in one sentence, `owner` = that side | `learning` | up to 2 |
| 2 | `*` | One section per interface | The joint fix (a hold point, a shared check, a single owner, a handover record): `hoc_tier`, an `indicator` both sides can see, `owner` = one side and `co_owner` = the other | `recommendation` | 1 |
| 3 | `agenda` | Joint-review agenda | A `table` for the meeting the two sides hold: Interface, Roles who meet, Agenda item, Evidence to bring, Decision sought; `row_cites` | `table` | 1 |
| 4 | `who-meets` | Who must meet whom | One line per pair: the roles, and the record they review together | `check` | up to 12 |

Name barriers and sides in the words of `barriers-and-controls.md`. Carry `learning: "LR-nn"` on a learning or
fix that expresses a register learning (`skill-common.md` §3).

```json
{"kind": "recommendation", "group": "Joint fix", "change": "Add a specification check at the stores issue counter",
 "hoc_tier": "administrative", "owner": "Materials Management (F06)", "co_owner": "Mechanical Maintenance (F02)",
 "indicator": "% of critical spares issued with a specification reference", "cites": ["FND-0003"]}
```

## If the evidence is thin

Follow `skill-common.md` §6, and:
- **No pairs, or a single-entity export:** say so, write the matrix with what `interfaces` printed, and stop
  before writing per-interface sections. Suggest the `learning-clusters` resolution pass if F99 is large.
- **A pair with causal mentions but no shared findings:** keep it only if its findings name what passes between
  the two; otherwise list it in the matrix only.
- **No mitigation-side pair in the evidence:** say so in the bottom line rather than forcing one.

## Not covered here

- One department's whole learning across every tier: `cluster-learning-dossier`.
- The causal chain behind the seam: `causal-map`.
- Barrier states and the strength of each fix: `barrier-learnings`.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/interface-learnings.json --strict   # fix every problem it lists
PMLC pack <ws> <run>/outputs/interface-learnings.json                  # -> interface-learnings.html and .md
PMLC pack <ws> <run>/outputs/interface-learnings.json --format docx    # -> interface-learnings.docx, for the joint review
```

Tell the user which seams matter most, and hand them the joint-review agenda as the next step: the docx carries
it as a Word table both sides can annotate.
