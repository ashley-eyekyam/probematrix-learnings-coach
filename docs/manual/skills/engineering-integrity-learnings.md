# engineering-integrity-learnings

Learning for engineering, design, asset integrity, inspection, reliability, instrumentation and management-of-change functions. It covers specifications and documents, change control, inspection and corrosion programmes, testing after maintenance, alarm and safety-system design and ageing equipment, with technical recommendations rated on the hierarchy of controls and the route each one takes to be adopted.

## What it is for

- "What should engineers, the technical authority, integrity or reliability teams, change-control owners or instrument engineers learn?"
- A technical lessons pack from a ProbeMatrix export.

The barrier-by-barrier analysis across all functions is [barrier-learnings](barrier-learnings.md); when its pack exists, this skill takes its engineering barriers from it.

## How to start it

- "What should our engineering and integrity teams learn from this investigation?"
- "Give me the technical learnings on change control and testing after maintenance, with engineering fixes first."
- "Which engineering decisions does the technical authority now need to take?"

## What it needs

- `clusters.json`. The skill selects the functions tagged `engineering`: in the default list F03 Electrical Maintenance, F04 Instrumentation, Control & Calibration, F05 Asset Integrity, Corrosion & Inspection, and F07 Engineering, Design, Documents & MOC.
- Optional: the [barrier-learnings](barrier-learnings.md) pack (the source for barriers) and the Learnings Register (entries owned by an engineering function, with their `LR-nn` ids).

## Engine commands and flags

```bash
pmlc select <ws> --tag engineering --brief
pmlc select <ws> --tag engineering --level 3 4 --top-rated
pmlc select <ws> --text "specification|drawing|P&ID|MOC|change|inspection|thickness|corrosion|calibrat|interlock|test|design" --brief
pmlc select <ws> --prefix PTE --brief                       # technological environment: alarms, automation, displays
pmlc select <ws> --preset engineering-integrity-learnings   # the four calls above at once
pmlc timeline <ws> --before incident
pmlc check-pack <ws> <run>/outputs/engineering-integrity-learnings.json --strict
pmlc pack <ws> <run>/outputs/engineering-integrity-learnings.json
pmlc pack <ws> <run>/outputs/engineering-integrity-learnings.json --format docx   # for the technical review
pmlc pack <ws> <run>/outputs/engineering-integrity-learnings.json --format csv    # the actions CSV
```

- [select](../commands/select.md): `--tag engineering` every function tagged engineering; `--level 3 4` the Supervision and Organisational levels; `--top-rated` the strongest; `--text` a regular expression over the finding text (technical words); `--brief` short entries; `--prefix PTE` the findings coded to the technological environment (equipment, controls, automation, displays), for the alarms and automation section.
- [timeline](../commands/timeline.md) with `--before incident` gives dated technical history, such as inspection dates.
- [check-pack](../commands/check-pack.md) with `--strict` checks the pack against its profile, including one learning, one barrier and one recommendation per theme; [pack](../commands/pack.md) renders it.
- [pack](../commands/pack.md) `--format docx` writes `engineering-integrity-learnings.docx` for a technical review or MOC committee to mark up; `--format csv` writes `engineering-integrity-learnings.actions.csv`, every recommendation, decision and indicator for the MOC or CAPA system, with the owner, due, status, CAPA and effectiveness columns blank. It never overwrites an existing actions file, which may already hold the organisation's entries.

## What you get

`engineering-integrity-learnings.html` and `.md`:

1. **technical learnings by theme**, only for the themes the evidence supports. For each: a learning (the technical condition and how it persisted), the barrier it weakened, and a recommendation with engineering controls first where credible. Each recommendation starts with its route: "Route: MOC.", "Route: engineering standard revision.", "Route: inspection plan change." or "Route: technical query.";
2. optionally, **alarms and automation**: the same learning, barrier and recommendation triplets for alarm and detection design, automatic shutdown and other executive actions, and what operators could see on their displays (missing signals, no history, clocks that disagree). The pack mentions cyber security only when the export names it;
3. **engineering decisions pending**: questions for the technical authority, stated as decisions with options, not answers;
4. **data and records**: the minimum record at each point in the work.

**Numbers rule.** The pack never sets engineering values (pressures, thicknesses, intervals, percentages, durations) beyond what the cited records state. Those become decisions for the technical authority. The language check flags a percentage or duration that is not in the cited records (JC8, see [Language checks](../Language-checks.md)).

## Worked example (Hazira)

`select --tag engineering --brief` returned 203 findings, `--tag engineering --level 3 4 --top-rated` returned 49, and the technical-words search returned 334. `timeline --before incident` picks up the pipeline thickness measurements of 2011 and 2017. A decision for the technical authority could rest on the finding that the gasket was replaced and the line pressurised to operating pressure only, with no hydro test (FND-3AB996FC, EVD-2894): what test should follow pressure-boundary work is the authority's decision, not the pack's.

`select --prefix PTE` returned 48 findings. The sample pack's alarms and automation section holds two triplets: gas detection that only lit a panel, with no automatic shutdown or signal history (LR-10), and pressure transmitters at the leak point that sent no data to the control system, with control-room clocks 2 to 12 minutes apart (LR-15). The export does not mention cyber security, so the pack does not either.

These counts are from the base classification, before the resolution pass. After you place the remaining roles, or add an overlay, they change: on Hazira the india-process-site overlay alone moves F09b Emergency Planning & Command from 16 to 43 findings.

## Related skills

- [barrier-learnings](barrier-learnings.md): the barriers these learnings weaken.
- [supply-chain-contractor-learnings](supply-chain-contractor-learnings.md): who may approve a substitute part.
- [interface-learnings](interface-learnings.md): the seams between engineering, maintenance and stores.
