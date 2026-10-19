# engineering-integrity-learnings

Learning for engineering, design, asset integrity, inspection, reliability, instrumentation and management-of-change functions. It covers specifications and documents, change control, inspection and corrosion programmes, testing after maintenance, alarm and safety-system design and ageing equipment, with technical recommendations rated on the hierarchy of controls.

## What it is for

- "What should engineers, the technical authority, integrity or reliability teams, change-control owners or instrument engineers learn?"
- A technical lessons pack from an incident.

## How to start it

- "What should our engineering and integrity teams learn from this investigation?"
- "Give me the technical learnings on change control and testing after maintenance, with engineering fixes first."
- "Which engineering decisions does the technical authority now need to take?"

## What it needs

- `clusters.json`. The skill selects the functions tagged `engineering`: in the default list F03 Electrical Maintenance, F04 Instrumentation, Control & Calibration, F05 Asset Integrity, Corrosion & Inspection, and F07 Engineering, Design, Documents & MOC.

## Engine commands and flags

```bash
pmlc select <ws> --tag engineering --brief
pmlc select <ws> --tag engineering --level 3 4 --top-rated
pmlc select <ws> --text "specification|drawing|P&ID|MOC|change|inspection|thickness|corrosion|calibrat|interlock|test|design" --brief
pmlc select <ws> --preset engineering-integrity-learnings   # the three calls above at once
pmlc timeline <ws> --before incident
pmlc check-pack <ws> <run>/outputs/engineering-integrity-learnings.json
pmlc pack <ws> <run>/outputs/engineering-integrity-learnings.json
```

- [select](../commands/select.md): `--tag engineering` every function tagged engineering; `--level 3 4` the Supervision and Organisational levels; `--top-rated` the strongest; `--text` a regular expression over the finding text (technical words); `--brief` short entries.
- [timeline](../commands/timeline.md) with `--before incident` gives dated technical history, such as inspection dates.
- [check-pack](../commands/check-pack.md) and [pack](../commands/pack.md) render the pack.

## What you get

`engineering-integrity-learnings.html` and `.md`:

1. **technical learnings by theme**, only for the themes the evidence supports. For each: a learning (the technical condition and how it persisted), the barrier it weakened, and a recommendation with engineering controls first where credible;
2. **engineering decisions pending**: questions for the technical authority, stated as decisions with options, not answers;
3. **data and records**: the minimum record at each point in the work.

**Numbers rule.** The pack never sets engineering values (pressures, thicknesses, intervals, percentages, durations) beyond what the cited records state. Those become decisions for the technical authority. The language check flags a percentage or duration that is not in the cited records (JC8, see [Language checks](../Language-checks.md)).

## Worked example (Hazira)

`select --tag engineering --brief` returned 203 findings, `--tag engineering --level 3 4 --top-rated` returned 49, and the technical-words search returned 334. `timeline --before incident` picks up the pipeline thickness measurements of 2011 and 2017. A decision for the technical authority could rest on the finding that the gasket was replaced and the line pressurised to operating pressure only, with no hydro test (FND-3AB996FC, EVD-2894): what test should follow pressure-boundary work is the authority's decision, not the pack's.

These counts are from the base classification, before the resolution pass. After you place the remaining roles, or add an overlay, they change: on Hazira the india-process-site overlay alone moves F09b Emergency Planning & Command from 16 to 43 findings.

## Related skills

- [barrier-learnings](barrier-learnings.md): the barriers these learnings weaken.
- [supply-chain-contractor-learnings](supply-chain-contractor-learnings.md): who may approve a substitute part.
- [interface-learnings](interface-learnings.md): the seams between engineering, maintenance and stores.
