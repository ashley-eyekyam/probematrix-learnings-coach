# investigator-coach

Coaching for investigators and HSE professionals from a real case. It audits the evidence base, drafts the follow-up for each high-rated finding (evidence to collect, key questions, interviews by role, a causal hypothesis to test), plans interviews, draws method lessons and turns the case into training exercises. It fills the export's four follow-up columns when they are empty.

## What it is for

- "How do we deepen or strengthen this investigation?"
- "What evidence is missing, and who else should we interview?"
- "How good is this investigation?"
- Investigator training material from a real case.

## How to start it

- "What evidence is missing from this investigation, and who should we interview next?"
- "Fill in the evidence-to-collect, key questions and interview columns for the high-rated findings."
- "Give me three training exercises for investigators from this case."

## What it needs

- A workspace from [learnings-coach](learnings-coach.md).
- The incident narrative (`incident.json`) and the evidence descriptions (`evidence.json`), which `ingest` writes.

## Engine commands and flags

```bash
pmlc profile <ws>                                              # shows whether follow-up columns are empty
pmlc select <ws> --top-rated --format json --out <ws>/top.json
pmlc select <ws> --preset investigator-coach                   # the same call, as the skill's preset
pmlc check-pack <ws> <run>/outputs/investigator-coach.json
pmlc pack <ws> <run>/outputs/investigator-coach.json
```

- [profile](../commands/profile.md) lists empty columns among its data-quality flags.
- [select](../commands/select.md): `--top-rated` keeps the strongest findings, `--format json` writes structured output and `--out` saves it to a file.
- [check-pack](../commands/check-pack.md) checks the follow-up table. [pack](../commands/pack.md) also writes `follow-up.json`, one entry per finding, ready to paste back into the investigation.

## What you get

`investigator-coach.html`, `.md` and `follow-up.json`:

1. an **evidence audit**: evidence by type, kinds of evidence that are absent, and conflicts between sources;
2. a **follow-up table**, one row per condition: evidence to collect, key questions, suggested interviews (by role) and a causal hypothesis;
3. an **interview plan**: roles the evidence never heard from, each with five questions. Interviews are for learning, not discipline, with a representative offered and no leading questions;
4. **method lessons**: where the analysis reached levels 3 and 4, where a finding may be coded too low, and where a finding rests on one source;
5. three **training exercises** for investigators.

Suggested interviews name roles only, and pass through the language check like any other text. Sharing a pack outside the organisation drops the key questions, suggested interviews, causal hypotheses and evidence to collect, and writes no `follow-up.json` (see [Review and sharing](../Review-and-sharing.md)).

## Worked example (Hazira)

The profile flagged that `Evidence to Collect`, `Key Questions`, `Suggested Interviews` and `Causal Hypothesis` are empty on every finding, so this skill drafts them. `select --top-rated --format json --out <ws>/top.json` wrote the 150 top-rated findings. The 46 evidence items are 18 documents, 9 log records, 7 witness statements, 6 recordings, 3 physical items and 3 photographs. The sample was a desk analysis of a published report, with no site access or interviews, so the interview plan is a list of what a site team would still need to hear.

## Related skills

- [report-comparison](report-comparison.md): where the two reports differ, and what to ask next.
- [causal-map](causal-map.md): the hypotheses to test where links are missing.
- [training-designer](training-designer.md): turns the exercises into a module.
