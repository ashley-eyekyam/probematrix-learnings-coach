---
name: engineering-integrity-learnings
description: Produces learning for engineering, design, asset integrity, inspection, reliability, instrumentation and management-of-change functions from a ProbeMatrix investigation export - specifications and documents, change control, inspection and corrosion programmes, testing after maintenance, alarm and safety-system design, ageing equipment - with technical recommendations rated on the hierarchy of controls and the route each one takes (MOC, standard revision, inspection plan change, technical query). Use when someone has a ProbeMatrix export and asks what engineers, the technical authority, integrity or reliability teams, MOC owners or instrument engineers should learn, or wants a technical lessons pack. Not for the barrier-by-barrier analysis across all functions (use `barrier-learnings`).
---

# Engineering & Integrity Learnings

Audience: the Learning Clusters tagged `engineering` (in the default taxonomy F03 electrical, for
hazardous-area equipment, F04 instrumentation, control and calibration, F05 asset integrity, corrosion and
inspection, and F07 engineering, design, documents and MOC).

## Before you start

Engine: `PMLC` as defined in `skill-common.md` §1 (needs the `learnings-coach` skill installed alongside it).

- Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions).
- Needs: **workspace** and **clusters**.
- Read `learnings-coach/references/learning-principles.md`; barrier and tier words from
  `learnings-coach/references/barriers-and-controls.md`.
- **Barriers come from `barrier-learnings`.** If `<run>/outputs/barrier-learnings.json` exists, take each
  engineering barrier from it (same wording, `state`, `hoc_tier` and `barrier_id`) rather than re-deriving it.
  If it does not, write the barriers here and suggest `barrier-learnings` as the next step.
- **Start from the register if present.** In `<run>/outputs/learnings-register.json`, take the entries whose
  `owner_entity` is an `engineering` entity: keep their wording and carry `learning: "LR-nn"` on the items.

## Gather

```bash
PMLC select <ws> --tag engineering --brief                        # the engineering functions' findings
PMLC select <ws> --tag engineering --level 3 4 --top-rated        # how the conditions persisted
PMLC select <ws> --text "specification|drawing|P&ID|MOC|change|inspection|thickness|corrosion|calibrat|interlock|test|design" --brief
PMLC timeline <ws> --before incident                              # the build-up, for "how it persisted"
```

## Write

Pack `<run>/outputs/engineering-integrity-learnings.json` (shape: `learnings-coach/references/pack-schema.md`),
`"scope": {"tags": ["engineering"]}`.

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | The technical learnings, one line each | `bottom_line` | up to 5 |
| 1 | `themes` | Technical learnings by theme | The technical condition and how it persisted (L3–L4); `group` = the theme | `learning` | up to 8 |
| 1 | `themes` | Technical learnings by theme | The barrier it weakened (type, owner, state, failure_mode, hoc_tier, fix, indicator), same `group` | `barrier` | up to 8 |
| 1 | `themes` | Technical learnings by theme | The fix, engineering controls first where credible, with its route (below) and a technical leading indicator, same `group` | `recommendation` | up to 8 |
| 2 | `decisions` | Engineering decisions pending | Questions the technical authority must settle (e.g. test pressure after pressure-boundary work, acceptance of substitute components), as options without answers; `owner` = the technical authority | `decision` | up to 6 |
| 3 | `records` | Data and records | Which technical records were missing or unreliable, and the minimum record, `when` = the point in the work | `check` | up to 8 |

- **Themes.** Specification and substitution of parts; testing after maintenance; change management; inspection
  and corrosion programmes; documents and as-built records; detection, alarm and shutdown design; hazardous-area
  equipment integrity; ageing equipment. Only the themes the evidence supports. Each theme has one learning, one
  barrier and one recommendation with the same `group`.
- **Route.** Each recommendation's `change` starts with the route it takes to be adopted: "Route: MOC.",
  "Route: engineering standard revision.", "Route: inspection plan change." or "Route: technical query." Pick
  the route the change needs, not the quickest one.
- **Numbers rule.** Do not specify engineering values (pressures, thicknesses, intervals, percentages,
  durations) beyond what the cited records state; never add a figure from outside the export; make them
  `decision` items for the technical authority.

```json
{"kind": "recommendation", "group": "Specification and substitution",
 "change": "Route: MOC. Put every substitute critical part through change control before it is bought.",
 "hoc_tier": "administrative", "why_not_stronger": "…", "indicator": "…", "cites": ["FND-…"]}
```

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/engineering-integrity-learnings.json (repository only)

## If the evidence is thin

- **Few engineering findings:** write only the themes the evidence supports; one theme is a valid pack.
- **No barrier in the evidence for a theme:** keep the learning and recommendation, and write the barrier with
  `state` only where a record states it; otherwise add a `gaps` entry for the record that would show it.
- `skill-common.md` §6 covers the rest.

## Not covered here

- The barrier-by-barrier analysis across all functions, prevention and mitigation: `barrier-learnings` (the
  source for barriers here).
- The interfaces between engineering and other functions: `interface-learnings`.
- Procurement and vendor learning about parts: `supply-chain-contractor-learnings`.
- Engineering values and standards themselves: decisions for the technical authority, not this pack.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/engineering-integrity-learnings.json --strict
PMLC pack <ws> <run>/outputs/engineering-integrity-learnings.json
PMLC pack <ws> <run>/outputs/engineering-integrity-learnings.json --format docx   # for the technical review
PMLC pack <ws> <run>/outputs/engineering-integrity-learnings.json --format csv    # the actions CSV
```

- **Word.** `engineering-integrity-learnings.docx` is the document a technical review or MOC committee can
  mark up: real tables, and each item's citations as one endnote.
- **Actions CSV.** `engineering-integrity-learnings.actions.csv` lists every recommendation, decision and
  indicator, with its route in `change`, for the MOC or CAPA system. The owner, due, status, CAPA reference and
  effectiveness columns stay blank for the organisation; never fill them. It never overwrites an existing file
  (exit 1): the organisation may already have filled it in, so move it or pass a new `--out`.
- Check that every recommendation names its route and that no engineering value lacks a cited record.
- Next step: `barrier-learnings`, if its pack does not exist yet.
