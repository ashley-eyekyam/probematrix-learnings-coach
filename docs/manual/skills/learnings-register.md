# learnings-register

A formal Learnings Register (a lessons-learned register): one row per **learning**, not per finding. Each row carries its evidence, HFACS level, barrier, organisational system, audiences, priority, recommendations rated on the hierarchy of controls, leading indicators and a message for each tier. It is written to JSON, Markdown and a formatted Excel workbook, and it feeds the dashboard.

## What it is for

- A lessons-learned register, a learnings log or "an Excel of learnings".
- A register to take to management.
- "Turn these findings into lessons and recommendations."
- The spine for the organisation learning map and the report comparison.

## How to start it

- "Build a learnings register from this export, with recommendations, and give me the Excel."
- "Turn these 436 findings into a lessons-learned register for the management review."
- "Make the register and the organisation dashboard."

## What it needs

- `clusters.json` from [learning-clusters](learning-clusters.md). Owner entities and tiers come from it.
- Time for judgement: the agent groups findings that describe the same condition. Roughly one learning per 5 to 10 distinct conditions: a few hundred findings typically become 15 to 40 learnings, and a small export only a handful.

## Engine commands and flags

```bash
pmlc select <ws> --top-rated --brief          # start from the strongest findings
pmlc select <ws> --preset learnings-register  # the same call, recorded as the skill's preset
pmlc facts <ws>                               # counts and shares to quote exactly
pmlc check-register <ws> <run>/outputs/learnings-register.json --strict
pmlc register-md <ws> <run>/outputs/learnings-register.json
pmlc register-xlsx <run>/outputs/learnings-register.json
pmlc dashboard <ws> --register <run>/outputs/learnings-register.json [--date <corrected date>] [--title "<plain title>"]
```

- [select](../commands/select.md): `--top-rated` keeps findings at the workspace's top rating, and `--brief` drops the long text. Then the agent sweeps the lower ratings for conditions not yet covered, especially at levels 3 and 4.
- [facts](../commands/facts.md) prints the counts, levels and the share of findings at levels 3 and 4.
- [check-register](../commands/check-register.md) checks IDs, evidence links, controlled values (including the new optional fields), tier messages and indicators. It flags findings with reviewer downgrade votes, lists high-rated findings no learning covers, and runs the language check. With `--strict`, a priority-1 learning with no fix above the administrative tier is a problem, not a warning, unless the entry says `why_not_stronger`. `--json`, `--share`, `--names` and `--orgs` work as on [check-language](../commands/check-language.md).
- [register-md](../commands/register-md.md) writes `learnings-register.md`. Never write it by hand: it holds the summary counts the engine computes. `--out` names another file.
- [register-xlsx](../commands/register-xlsx.md) writes the workbook. `--out` names it, and `--ws` points to the workspace when the register is not in the standard run folder. It also takes `--share`, `--names` and `--orgs` for a masked copy (see [Review and sharing](../Review-and-sharing.md)).
- [dashboard](../commands/dashboard.md) with `--register` is required for this skill.

The optional spine fields, each used only when it applies: `urgency` (alert, notice or information), `recommendation_class` (recommendation, observation or action already taken), `recipient_role` (the role that must answer), `regulatory_touchpoint` (a regime the learning touches, as a flag for legal or compliance review), `verification` (how the organisation will check the change worked) and `why_not_stronger` (for a priority-1 learning with only administrative or training fixes).

## What you get

- `learnings-register.json`, the source of truth. Fix problems here and re-run, never in the workbook.
- `learnings-register.xlsx`, with the sheets Learnings Register, Recommendations, Learning Plan, Summary and About.
- `learnings-register.md` from `register-md`: summary tables, the priority-1 learnings in full, then the rest in a compact table.
- `organisation-learning-map.html` with the **Detailed register** tab.

Each learning has an ID such as `LR-01` (see [LR-ID](../Glossary.md#lr-id)). Audience packs that express a register learning carry the same ID.

## Worked example (Hazira)

`select --top-rated --brief` returned 150 findings at rating 4. The committed sample register groups the whole export into 25 learnings. `check-register` on it printed:

```text
25 learnings; 435 of 436 findings covered (100%); 0 problem(s).
Uncovered findings (1), highest rated first:
   FND-44219027 PPE 1.2 r3 Night-time darkness combined with dense white vapour cloud restricted visual assessment an
```

It then listed 14 `hfacs_level` wording warnings, the warning `no handling block: rendered as draft (internal)`, and two JC6 warnings (entries 8 and 12 rely only on administrative and training controls for a level 3 or 4 cause). Warnings do not fail the check. `register-xlsx` printed `Register with 25 entries and 44 recommendations written to …/learnings-register.xlsx`.

`check-register --strict` on the same register printed `25 learnings; 435 of 436 findings covered (100%); 2 problem(s).` and named them: `priority-1 learning LR-08 has no fix above the administrative tier` and the same for LR-12. Adding a `why_not_stronger` to each entry, or a stronger fix, clears them. `register-md` printed `Register markdown written to …/outputs/learnings-register.md`.

## Related skills

- [organisation-learning-map](organisation-learning-map.md): the dashboard built on the register.
- [report-comparison](report-comparison.md): compares the register with an official report.
- [barrier-learnings](barrier-learnings.md): stronger fixes for the barriers behind each learning.
- Recipe: [A learnings register to Excel](../Workflows-and-recipes.md#a-learnings-register-to-excel).
