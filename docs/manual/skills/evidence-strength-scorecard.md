# evidence-strength-scorecard

How well the evidence behind an investigation holds up, counted by the engine rather than judged. The scorecard shows the findings that rest on one source or on documents alone, the evidence mix at each HFACS level, the documents that support many findings, the findings that rest on their justification alone and the codes the causal text names that no finding carries. It ends with up to twelve requests for the evidence that would most strengthen confidence. It shows where more evidence would help; it does not grade the investigation team.

## What it is for

- "How well-evidenced are these findings?"
- "Where is the evidence thin, and how much rests on one document?"
- An evidence check before an audit, a register sign-off or a review of the investigation.
- Choosing which records or accounts to collect next, starting with the top-rated findings.

## How to start it

- "Before we sign off the register, how solid is the evidence behind these findings?"
- "Which documents carry the most findings, and what would corroborate them?"
- "Give me an evidence scorecard for this investigation, by HFACS level."

## What it needs

- A workspace from [learnings-coach](learnings-coach.md). The skill runs [evidence-audit](../commands/evidence-audit.md) itself, which writes `evidence_audit.json`.
- Optional: the Learnings Register. With it, each request that would firm up a learning names its `LR-nn`, and learnings rated `direct` (one evidence type) come first.

## Engine commands and flags

```bash
pmlc evidence-audit <ws>                                    # writes evidence_audit.json and prints the summary
pmlc evidence-audit <ws> --table-item scorecard             # every measure, as a table item to paste
pmlc evidence-audit <ws> --table-item levels                # the evidence mix per HFACS level
pmlc evidence-audit <ws> --table-item concentration         # items that support ten or more findings
pmlc select <ws> --level 3 4 --top-rated --fields label,evidence,level,rating   # the findings the requests firm up
pmlc check-pack <ws> <run>/outputs/evidence-strength-scorecard.json --strict
pmlc pack <ws> <run>/outputs/evidence-strength-scorecard.json
pmlc pack <ws> <run>/outputs/evidence-strength-scorecard.json --format docx       # a Word copy
pmlc pack-xlsx <ws> <run>/outputs/evidence-strength-scorecard.json --kind question   # the requests in Excel
pmlc pack-xlsx <ws> <run>/outputs/evidence-strength-scorecard.json --kind table      # the three tables in Excel
```

- [evidence-audit](../commands/evidence-audit.md) counts the strength of every finding (`corroborated`: two or more items of two or more types; `direct`: at least one item; `inferred`: none). `--table-item` prints the `scorecard`, `levels` or `concentration` table, with `row_cites`, ready to paste unchanged.
- [select](../commands/select.md) with `--level 3 4` and `--top-rated` lists the high-rated findings at the supervisory and organisational levels; `--fields label,evidence,level,rating` keeps each one to its label and its evidence. `select --preset evidence-strength-scorecard` runs the same call.
- [check-pack](../commands/check-pack.md) with `--strict` checks the pack against its profile, including the fixed banner, then [pack](../commands/pack.md) renders it. [pack-xlsx](../commands/pack-xlsx.md) with `--kind question` or `--kind table` writes the requests or the tables to Excel.

## What you get

`evidence-strength-scorecard.html` and `evidence-strength-scorecard.md`, with these sections:

- **banner:** the fixed sentence "This scorecard shows where more evidence would strengthen confidence. It does not grade the investigation team.";
- **scorecard:** the findings rated `direct`, `corroborated` and `inferred`, then the single-source, document-only and justification-only findings and the unknown codes, pasted from the engine;
- **levels:** findings, single-source, document-only and witness-backed findings at each HFACS level;
- **concentration:** the evidence items that support ten or more findings, with their share (left out when there are none);
- **requests:** up to twelve questions, each naming the evidence to look for, the finding or learning it would firm up, a source of another type that would corroborate it, and the role that holds it;
- **limits:** what counting links cannot show, such as how reliable a document or a statement is.

The pack carries no owners or due dates: the investigation lead decides what to collect. The Word copy suits the investigation file; the Excel copies suit tracking the requests. `--format csv` writes nothing for this pack, because it exports recommendations and the scorecard has none.

## Worked example (Hazira)

`evidence-audit` printed:

```text
| Measure | Count |
|---|---:|
| direct | 284 |
| corroborated | 152 |
| inferred | 0 |
| single-source | 203 |
| document-only | 195 |
| justification only | 0 |
| codes named in causal text that no finding carries: PSE 5.6, PTE 1.5 | 2 |
```

These are the same rows as `--table-item scorecard`. The summary goes on to the largest concentration: EVD-8645 supports 67 of 436 findings (15%). The `levels` table shows that 11 of the 167 level 3 findings cite a witness statement.

The worked pack, `samples/2020-09-24-hazira-gas-release-fire/outputs/evidence-strength-scorecard.json` in the repository, writes eleven requests. They start with the seal practice behind LR-01, which rests largely on EVD-8645, and go on to the nine register learnings rated `direct`, such as the calibration record behind all 26 findings of LR-16.

## Related skills

- [investigator-coach](investigator-coach.md): how to run the investigation, interview plans and method lessons.
- [auditor-assurance-pack](auditor-assurance-pack.md): test points for checking that the lessons were applied.
- [learnings-register](learnings-register.md): `check-register` holds each learning's `evidence_strength` to `evidence-audit`.
