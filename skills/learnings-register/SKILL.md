---
name: learnings-register
description: Builds a formal Learnings Register (lessons-learned register) from a ProbeMatrix investigation export - one row per learning with evidence, HFACS level, barrier, organisational system, audiences, priority, urgency and recommendations rated on the hierarchy of controls with leading indicators - and writes it to Markdown, a formatted Excel workbook and the two-tab dashboard. Use when someone with a ProbeMatrix export asks for a lessons-learned register, a learnings log, an Excel of learnings, a register to take to management, or "turn these findings into lessons and recommendations". Not for the organisation-wide cascade plan (use `organisation-learning-map`).
---

# Learnings Register

Engine: `PMLC` as in `learnings-coach/references/skill-common.md` §1; this skill needs the `learnings-coach` skill installed alongside it.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions; run `PMLC setup`
when only an .xlsx was given). Needs: `workspace`, `clusters` (resolve unresolved roles with `learning-clusters`
first if many findings sit in F99). Optional: the comparator. Read
`learnings-coach/references/learning-principles.md`, `learnings-coach/references/register-schema.md` (fields and
controlled values), `learnings-coach/references/barriers-and-controls.md` (barrier names and control tiers) and
`learnings-coach/references/indicators-and-effectiveness.md` (indicators; single- and double-loop criteria).

## Gather

```bash
PMLC select <ws> --top-rated --brief                     # start from the highest-rated findings
PMLC facts <ws>                                          # counts, levels and the L3-L4 share, to quote exactly
```

1. **Find the learnings, not the findings.** Group findings that describe the same condition. Scale to the
   export: roughly **one learning per 5–10 distinct conditions** (a few hundred findings typically give 15–40
   learnings; a small export may give 3–6). Then sweep lower ratings for conditions not yet covered, especially
   at L3–L4.
2. **Owner and tiers** come from `clusters.json` for the learning's findings (the owner rule in
   `register-schema.md`).
3. **Prioritise.** Priority 1 = a credible major consequence, likely to recur or transfer; 3 = local and minor.

## Write

Write `<run>/outputs/learnings-register.json` in the shape in `register-schema.md` (it is a register, not a
pack). One entry per learning, classified against every section A–K of `register-schema.md`.

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/learnings-register.json (repository only)

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| A | `lr_id` | Identity | `LR-01`, `LR-02` … with a short `title` | text | 1 |
| A | `ml_id` | Identity | `ML-01` … only for a learning with no counterpart in a supplied comparator report (`report-comparison`); otherwise `""` | text | optional |
| B | `lesson` | Lesson | A generalisable sentence ("If X, then Y, because Z") that makes sense at another site, not a restatement of the event; `owner_entity`, `tiers` | text | 1 |
| B | `context` | Lesson | Two or three de-identified sentences, roles only, on where the lesson comes from; also why the owner departs from the owner rule, or that the evidence is inferred | text | 1 |
| C | `finding_ids` | Evidence | Finding IDs and Evidence IDs (`evidence_ids`), `evidence_strength`, `confidence` | ID list | at least 1 |
| D | `hfacs_level` | Causal classification | Level plus sub-category as the export writes it; `barrier` and `org_system` in the shared vocabulary | text | 1 |
| D | `causal_role` | Causal classification | `initiating`, `contributory`, `escalating` or `failed mitigation`, with `hazard`, `activity` and `performance_mode` (skill / rule / knowledge; slip / lapse / mistake / violation) | value | 1 |
| E | `pattern` | Pattern | Recurrence or cross-incident pattern, and `precursors` (dated weak signals, from `precursor-timeline` when it ran) | text | optional |
| F | `comparison` | Comparison | `not compared` unless a comparator is supplied; then `yes` / `partial` / `none` with `reason_class` | value | 1 |
| H | `audiences` | Dissemination | Who must learn, `learning_level` (individual / team / organisational; single- or double-loop, by the criteria in `indicators-and-effectiveness.md`) and `formats` (brief, card, toolbox talk, module) | list | 1 |
| G | `priority` | Significance | 1, 2 or 3, with `worst_case` and `transferability` | value | 1 |
| I | `recommendations` | Recommendations | Each with `what`, `level_barrier` (the HFACS level and barrier it strengthens, such as "L4 / emergency isolation"), `evidence_basis` (the EVD IDs, else the Finding IDs, it rests on), `hoc_tier`, `leading_indicator`; at least one above the administrative tier for a priority-1 learning, or say why in `why_not_stronger` | list | 1–3 |
| J | `tier_messages` | Tier messages | One short, concrete message per tier that must act (T1 … T5), omitting tiers with nothing to do | object | up to 5 |
| K | `urgency` | Urgency | `alert` (act now, a live risk elsewhere), `notice` (act within the normal cycle), `information` (awareness only) | value | optional |
| K | `recommendation_class` | Class | `recommendation` (a change still to make), `observation` (worth knowing, no change asked), `action_taken` (already done; say so, with evidence) | value | optional |
| K | `recipient_role` | Recipient | The role that must receive and answer the learning, never a name; use it when one role is clearly the addressee | text | optional |
| K | `regulatory_touchpoint` | Regulatory touchpoint | Free text naming a regime the learning touches (e.g. a permit or PSM duty), as a flag for legal or compliance review, never a legal conclusion | text | optional |
| K | `verification` | Verification | `{"method", "indicator"}`: how the organisation will check the change worked; use it for priority-1 and alert learnings | object | optional |
| K | `why_not_stronger` | Why not stronger | Only for a priority-1 learning with no fix above the administrative tier: why elimination, substitution or engineering is not possible | text | optional |

Use the controlled values in `register-schema.md` for `hfacs_level`, `hoc_tier`, `priority`, `urgency`,
`recommendation_class`, `learning_level` and `comparison`; put nuance in free text. For a comparison, use
`report-comparison`. Owners and due dates stay
blank unless the user asks (`learning-principles.md` §6).

## If the evidence is thin

Follow `skill-common.md` §6, and:
- **No Evidence Links sheet:** cite Finding IDs only, set `evidence_strength: "inferred"`, and say so in each
  learning's `context` and to the user. `check-register` cannot then find evidence IDs; do not invent them.
- **A small export:** write fewer learnings (the scaling rule above); never split one condition into several.
- **No fix above the administrative tier is possible for a priority-1 learning:** fill `why_not_stronger`
  honestly rather than relabelling a procedure as engineering.

## Not covered here

- The whole-organisation dashboard narrative and cascade plan: `organisation-learning-map`.
- Comparison with an official report or the organisation's own action plan: `report-comparison`.
- Audience packs built from the register: the audience skills (`learnings-coach/references/audiences.md`).

## Sharing outside the organisation

A register is for the organisation's own learning. Do not offer to send it outside. Sharing a copy needs legal
review, an approved sign-off and `register-xlsx --share external`; follow `skill-common.md` §7.

## Check and hand over

Run `skill-common.md` §4 (the register's own loop), then tick §5 with `check-register` in place of `check-pack`:

```bash
PMLC check-register <ws> <run>/outputs/learnings-register.json --strict   # fix every problem; read the warnings
PMLC register-md <ws> <run>/outputs/learnings-register.json               # -> learnings-register.md
PMLC register-xlsx <run>/outputs/learnings-register.json                  # -> learnings-register.xlsx
PMLC dashboard <ws> --register <run>/outputs/learnings-register.json      # -> organisation-learning-map.html
PMLC register-render <ws> <run>/outputs/learnings-register.json --format docx,email   # Word copy and email digest
```

Offer `register-render` when the register goes to people who read Word or email rather than Excel:
`learnings-register.docx` holds every learning, with its IDs as endnotes; `learnings-register.email.html` and
`.email.txt` hold the summary and as many learnings as fit in 100 KB, and say how many are left out. Both carry
the status line and, until a person approves the register, DRAFT (`skill-common.md` §8).

Add `--date <corrected date>` and `--title "<plain title>"` to `dashboard` when the profile flagged the
summary-sheet date. The dashboard has two tabs: Overview (the learning × tier matrix, a plan per level, fix
strength, heatmaps) and Detailed register (every field, each cited finding and evidence item in full, and
stakeholder lenses).

`check-register --strict` validates IDs, evidence links, controlled values, tier messages and indicators, makes
the priority-1 rule a problem, flags findings with reviewer downgrade votes, and lists high-rated findings no
learning covers. Run `register-md`; never hand-write the Markdown: it holds the summary counts (by entity, level,
organisational system and control tier) the engine computes. The workbook (Learnings Register, Recommendations,
Learning Plan, Summary, About) and the dashboard (Overview and Detailed register tabs) are rebuilt from the JSON:
change the JSON and re-run, never edit the outputs. Every register entry and every audience pack that uses it
carries the same `LR-nn`.
