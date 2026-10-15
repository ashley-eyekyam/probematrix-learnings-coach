---
name: investigator-coach
description: Coach incident investigators and HSE professionals using a ProbeMatrix investigation export - evidence gaps and conflicts, key questions and suggested interviews still to pursue, causal hypotheses to test, and method lessons on reaching supervisory and organisational causes. Fills the export's Evidence to Collect, Key Questions, Suggested Interviews and Causal Hypothesis columns when they are empty. Use when someone asks how to deepen or strengthen an investigation, what evidence is missing, who else to interview, how good the investigation is, or wants investigator training material from a real case.
---

# Investigator Coach

Audience: investigators, HSE advisers and process-safety engineers who run or review investigations.

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py`. Read `learnings-coach/references/learning-principles.md` and `export-schema.md`.

## Gather

```bash
PMLC profile <ws>                           # shows whether follow-up columns are empty
PMLC select <ws> --min-rating <top> --format json --out <ws>/top.json
```

Read the incident narrative in `<ws>/incident.json` and the evidence descriptions in `<ws>/evidence.json`.

## Write

1. **Evidence base audit**: evidence items by type; which kinds of evidence are absent (e.g. no maintenance-fitter statement, no procurement records, no calibration master data); conflicts between sources (dates, times, identifiers) and how they were resolved or not.
2. **Follow-up per high-rated finding** (one table row each): evidence to collect · key questions · suggested interviews (by role) · causal hypothesis to test. Keep it specific to the finding's evidence.
3. **Interview plan**: roles to interview that the evidence never heard from, ordered by how much they could change the analysis, each with five questions.
4. **Method lessons**: where the analysis reached L3–L4 and how; where findings may be coded at too low a level (an organisational condition recorded as an individual act); where a finding rests on a single source.
5. **Training use**: three exercises from this case for investigator training (e.g. "move this L1 finding to the level where it belongs").

## Output

`<ws>/outputs/investigator-coach.md`, plus `<ws>/outputs/follow-up.json` (finding ID → the four follow-up fields) if the user wants to paste them back into their investigation.
