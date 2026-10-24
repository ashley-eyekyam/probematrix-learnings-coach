# open-questions-register

A register of what the investigation could not answer. It lists the follow-up columns the export leaves empty on every finding, the blank Incident Summary fields, the findings whose AI justification says a record or fact is absent or is hedged, and the gaps that other packs in the run recorded. Each question names the finding it would firm up and the kind of source that would settle it, and `pack` writes a follow-up CSV that pastes back into the ProbeMatrix export.

## What it is for

- "What could this investigation not answer?"
- "Which records are missing, and where should we look?"
- A follow-up sheet for the investigation team before the learnings are adopted.

This skill *lists* the open questions. Coaching the method, an interview plan and causal hypotheses are [investigator-coach](investigator-coach.md), which can take this list as its starting point.

## How to start it

- "What does this ProbeMatrix investigation leave unanswered? List the open questions and what would settle each."
- "Give the investigation team a follow-up sheet of missing records that pastes back into the export."
- "Which findings say a record is missing, and which are hedged?"

## What it needs

- A workspace from [learnings-coach](learnings-coach.md).
- `open_questions.json`, which [open-questions](../commands/open-questions.md) writes into the workspace. The `investigation-quality` preset runs it as an engine step.
- Optional: `gaps.json`, the gaps other packs recorded, which [pack](../commands/pack.md) collects in the run's outputs folder. Run this skill after the other packs to include their gaps.
- Optional: `evidence_audit.json` from [evidence-audit](../commands/evidence-audit.md), to say which findings rest on a single source.

## Engine commands and flags

```bash
pmlc open-questions <ws>                  # the counts; writes open_questions.json
pmlc open-questions <ws> --json           # the lists, with the packs' gaps
pmlc open-questions <ws> --items          # up to 30 ready question items
pmlc evidence-audit <ws>                  # optional: single-source findings
pmlc check-pack <ws> <run>/outputs/open-questions-register.json --strict
pmlc pack <ws> <run>/outputs/open-questions-register.json
```

- [open-questions](../commands/open-questions.md): `--json` prints the empty columns, blank fields, absence and hedged finding lists and the merged gaps; `--items` prints the questions in the engine's order (empty columns, then top-rated absence findings, then the other absence findings, then hedged ones), which the skill pastes unchanged.
- The skill uses no `select` filters: the engine's word lists choose the findings, matched at word boundaries on the AI justification.
- [check-pack](../commands/check-pack.md) checks the five sections against the pack profile. [pack](../commands/pack.md) writes `open-questions-follow-up.csv` beside the page and never overwrites it, because the investigation team fills it in.

## What you get

`open-questions-register.html`, `.md` and `open-questions-follow-up.csv`:

1. a **summary** of what the export leaves open, in counts the engine gives;
2. the **follow-up columns** table: each empty column, "0 of n" findings with an entry, and a suggested source;
3. the **blank Incident Summary fields**, grouped (when and where, consequence, risk, regulatory, people and team, record dates);
4. up to 30 **questions to settle**, each with the finding it would firm up and the kind of source to look for (document, witness statement, inspection record, data log or photograph);
5. up to 20 **questions other packs raised**, one per recorded gap, grouped by the pack that raised it.

The CSV has one row per cited finding in the export's own follow-up columns: the questions under Key Questions and their sources under Evidence to Collect, with Suggested Interviews and Causal Hypothesis left blank for the team. A shared copy (`--share external`) writes only the masked `open-questions-follow-up.external.csv`.

## Worked example (Hazira)

`open-questions` on Hazira gave 4 empty follow-up columns, 21 of 30 blank Incident Summary fields, 240 of 436 findings whose justification says something is absent and 193 hedged ones. After the other sample packs were rendered, it merged their 15 gaps. The register pastes the 30 `--items` questions unchanged: the four empty columns, then 26 top-rated absence findings, led by the emergency isolation valves, the flameproof lamp and the seal change and return to service on meter 310FT01. The 15 other-pack questions include the ignition source, still named only as probable, and the date the investigation began. The bottom line ties the seal-change trail to register learning LR-01 and the emergency plan's isolation criteria to LR-07. The follow-up CSV has 44 rows, one per cited finding.

## Related skills

- [investigator-coach](investigator-coach.md): coaches the method, plans interviews and drafts the follow-up for each top-rated finding.
- [report-comparison](report-comparison.md): where an official report sees further, and what to ask next.
- The `evidence-strength-scorecard` skill (v2.0 Phase 5): how strong the evidence behind each finding is.
