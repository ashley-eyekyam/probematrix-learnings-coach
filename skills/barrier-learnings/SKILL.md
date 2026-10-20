---
name: barrier-learnings
description: Analyses which safety barriers and controls failed in a ProbeMatrix investigation export - prevention barriers before the event and mitigation barriers after it - who owned each, its state on the day, how it degraded and how strong the fix should be on the hierarchy of controls, with leading indicators, critical controls to verify first and an optional mapping to the organisation's barrier register. Use when someone with a ProbeMatrix export asks about barriers, controls, defences, bow-tie style learning, critical controls, "why didn't our safeguards work", or wants recommendations stronger than retraining. Not for engineering and integrity recommendations by technical theme (use `engineering-integrity-learnings`), or for drawing a full bow-tie (hand the barrier items to a bow-tie tool).
---

# Barrier Learnings

Engine: `PMLC` as in `learnings-coach/references/skill-common.md` §1; this skill needs the `learnings-coach` skill installed alongside it.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions; run `PMLC setup`
when only an .xlsx was given). Needs: `workspace`. Optional: the register. Read
`learnings-coach/references/learning-principles.md`, `learnings-coach/references/barriers-and-controls.md` (the
one vocabulary: barrier names and sides, barrier types, the five states, critical controls, hierarchy of
controls) and `learnings-coach/references/indicators-and-effectiveness.md`.

Ask once whether the organisation has a **barrier or critical-control register** (a CSV with an id and a barrier
name, often a side and an owner). If it does, map each barrier you write to its row (below). If not, go on.

## Gather

```bash
PMLC select <ws> --top-rated --brief                     # the highest-rated findings, and the incident narrative in <ws>/incident.json
PMLC table-item <ws> hoc --pack <run>/outputs/barrier-learnings.json   # after writing: the control-tier counts of your fixes
```

List only the barriers the findings mention, under the headings of `barriers-and-controls.md` §5:
- **Prevention side** (before loss of control): design and specification, maintenance and testing, inspection
  and integrity, procedures and permits, competence and staffing, change management, materials and spares.
- **Mitigation side** (after loss of control): detection and alarm, isolation and shutdown, ignition control,
  communication and escalation, emergency command, fire-water and fire protection, escape, rescue and recovery.

**Organisation barrier register (optional).** Read its id and name columns. Give each pack barrier the matching
row's id as `barrier_id` (free text, as the register writes it). A barrier with no matching row stays unmapped;
list it in the `unmapped` table, with the register rows the findings touch but no barrier names.

## Write

Write `<run>/outputs/barrier-learnings.json` in the shape in `learnings-coach/references/pack-schema.md`, with
`"scope": {"min_rating": "top"}`.

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | Which barriers carried the most weight, which side the failures clustered on, and the share of fixes above the administrative tier | `bottom_line` | up to 7 |
| 1 | `barriers` | Barriers | One per barrier, `group` = "Prevention" or "Mitigation": `barrier` (the §5 name), `type` (active, passive, procedural, behavioural), `owner` (entity and tier), `state` (absent, degraded, defeated, worked partly, worked), `failure_mode` (the L2–L4 findings behind the state; "[GAP] …" where the export does not say), `fix` and `hoc_tier`, `indicator`, `barrier_id` (when mapped), `cites` | `barrier` | up to 12 |
| 2 | `summary` | Summary | Where the weight sat, whether failures clustered on one side, and how strong the fixes are | `para` | up to 3 |
| 3 | `verify-first` | Critical controls to verify first | Ranked; only controls the findings show were the main or last line (`barriers-and-controls.md` §4). Add `clauses` where the evidence touches the requirement: `ICMM-CCM-8` (verification and reporting), `ICMM-CCM-9` (responding to poor control performance), `SEVESO-AnnexIII(vi)` (Seveso III Annex III: monitoring performance and lessons learnt) | `check` | up to 8 |
| 4 | `unmapped` | Barriers not in the organisation's register | Only with a barrier register: Barrier, Side, Why unmapped; `row_cites` | `table` | optional, up to 1 |

Do not declare a barrier effective or ineffective beyond what the evidence states. Include barriers that worked:
they are learning too. Carry `learning: "LR-nn"` on a barrier that expresses a register learning.

```json
{"kind": "barrier", "group": "Prevention", "barrier": "maintenance and testing", "type": "procedural",
 "owner": "Mechanical Maintenance (F02, T2)", "state": "absent", "failure_mode": "No leak test before restart",
 "fix": "Interlock restart on a signed test record", "hoc_tier": "engineering",
 "indicator": "% of restarts with a test record", "barrier_id": "BR-07", "cites": ["FND-0001", "FND-0002"]}
```

## If the evidence is thin

Follow `skill-common.md` §6, and:
- **State not given:** write `failure_mode` as "[GAP] …" and add a `gaps` entry naming the record that would show
  the state (a test log, a calibration record). Never pick a state to fill the field.
- **Only one side in the evidence:** write that side and say in the summary that the other was not examined.
- **No fix above the administrative tier:** say so plainly in the summary rather than relabelling a procedure.

## Not covered here

- Technical recommendations by engineering theme (MOC, standards, inspection plans): `engineering-integrity-learnings`, which takes its barriers from this pack.
- The emergency-response phases in depth: `emergency-response-learnings`.
- An audit programme to test the controls across sites: `auditor-assurance-pack`.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/barrier-learnings.json --strict   # fix every problem it lists
PMLC pack <ws> <run>/outputs/barrier-learnings.json                  # -> barrier-learnings.html and .md
```

Tell the user the share of fixes above the administrative tier, the controls to verify first, and how many
barriers stayed unmapped. For a bow-tie, map the `barrier` items as in `barriers-and-controls.md` §2.
