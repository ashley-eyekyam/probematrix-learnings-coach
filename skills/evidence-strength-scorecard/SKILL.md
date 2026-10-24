---
name: evidence-strength-scorecard
description: Scores how well the evidence behind a ProbeMatrix investigation export holds up - findings resting on one source, document-only findings, the evidence-type mix at each HFACS level (how few supervision findings cite a witness), single documents behind many findings, justification-only findings and codes the causal text names that no finding carries - all counted by the engine, never judged, plus up to twelve requests for the evidence that would most strengthen confidence. Use when someone with a ProbeMatrix export asks how well-evidenced the findings or learnings are, where the evidence is thin, how much rests on one document, or wants an evidence scorecard before an audit or a register sign-off. Not for coaching the investigation method or an interview plan (use `investigator-coach`), the full list of unanswered questions (use `open-questions-register`) or audit test points (use `auditor-assurance-pack`).
---

# Evidence Strength Scorecard

Engine: `PMLC` as in `learnings-coach/references/skill-common.md` §1; this skill needs the `learnings-coach` skill installed alongside it.

Audience: investigators, auditors and HSE leads. The scorecard shows where more evidence would strengthen
confidence. It never grades, ranks or scores the investigation team or any person.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions; run `PMLC setup`
when only an .xlsx was given). Needs: `workspace`, `evidence-audit` (the first Gather line writes it). Optional:
the register. Read `learnings-coach/references/learning-principles.md` (§2: independent sources, not the same
source counted twice).

- Start from the register if present: carry `learning: "LR-nn"` on a request that would firm up a register
  learning. A learning whose `evidence_strength` is `direct` rests on one evidence type; it gains most from a source
  of another type.

## Gather

```bash
PMLC evidence-audit <ws>                                     # writes <ws>/evidence_audit.json; prints the summary
PMLC evidence-audit <ws> --table-item scorecard              # every measure, ready to paste
PMLC evidence-audit <ws> --table-item levels                 # the evidence mix per HFACS level, ready to paste
PMLC evidence-audit <ws> --table-item concentration          # items behind ten or more findings, ready to paste
PMLC select <ws> --level 3 4 --top-rated --fields label,evidence,level,rating   # the findings the requests firm up
```

`select --preset evidence-strength-scorecard` runs the select call. Paste the three table items unchanged; never
retype a count, recompute a share or reorder a row. Then read `<ws>/evidence_audit.json`:
- `findings` gives each finding's `strength`, `sources` and evidence `types`;
- `single_source`, `document_only` and `justification_only` list the finding ids behind those rows;
- `unknown_codes` lists codes the causal text names that no finding carries;
- `notes` says when the export is thin.

Pick the requests from what the tables show, in this order: the top-rated level 3 and 4 findings that rest on one
source or on documents only; register learnings rated `direct`; the items with the largest concentration; then the
unknown codes. Read each finding's evidence description before you write its request.

## Write

Write `<run>/outputs/evidence-strength-scorecard.json` in the shape in `learnings-coach/references/pack-schema.md`.
Set `"scope": {"levels": [1, 2, 3, 4], "min_rating": "top"}`, and write the title in sentence case ("Evidence
strength scorecard: <incident>"): two capitalised words in a row read as a person's name to the language check.

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/evidence-strength-scorecard.json (repository only).

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | Where more evidence would most strengthen confidence, each point with its count from the tables; no grade and no score | `bottom_line` | 1–5 |
| 1 | `banner` | About this scorecard | The fixed banner, word for word (below) | `para` | 1 |
| 2 | `scorecard` | Evidence scorecard | The `--table-item scorecard` output, unchanged | `table` | 1 |
| 3 | `levels` | Evidence by HFACS level | The `--table-item levels` output, unchanged | `table` | 1 |
| 4 | `concentration` | Evidence items behind many findings | The `--table-item concentration` output, unchanged; leave the section out when it has no rows | `table` | optional, up to 1 |
| 5 | `requests` | Evidence that would strengthen confidence | One `question` per request (below) | `question` | 1–12 |
| 6 | `limits` | What this scorecard cannot tell you | What counting links cannot show (below) | `para` | 1–2 |

The `banner` is one `para` whose `text` is exactly: "This scorecard shows where more evidence would strengthen
confidence. It does not grade the investigation team." (`check-pack` checks it word for word.)

Each request is a `question` item:
- `question`: the evidence to look for, phrased as a question about a record, a place or a role's account;
- `why`: the finding or learning it would firm up, and which measure flagged it (single-source, document-only, no
  witness at level 3, a concentration, an unknown code);
- `good_evidence`: an independent source of another type, such as a log record, a witness statement, a site
  inspection or a photograph;
- `to`: a role that holds that source, never a name; `cites` the findings and the Evidence IDs it rests on.

```json
{"kind": "question", "question": "Do the stores issue records show when local O-rings were first fitted to this meter?",
 "why": "Three level 4 findings on the substitute part rest on one investigation document (EVD-0001).",
 "good_evidence": "Stores issue and purchase records for the meter's seals", "to": "Stores officer",
 "learning": "LR-01", "cites": ["FND-0003", "EVD-0001"]}
```

In `limits`, say that the scorecard counts the evidence links the export records: it cannot judge how reliable a
document or a statement is, and a single strong source can outweigh several weak ones.

Write about the evidence, never about the people who gathered it: "this finding rests on one document", not "the
team relied on one document". No owners and no due dates: the investigation lead decides what to collect.

## If the evidence is thin

Follow `skill-common.md` §6, and:
- **No Evidence Links rows** (the audit `notes` say every strength is `inferred`): keep the three tables, write one
  request per top-rated theme for the source that would anchor it, and say in `limits` that the export carries no
  evidence links.
- **The concentration table has no rows:** leave the `concentration` section out.
- **No register:** write the requests against findings only.

## Not covered here

- How to run the investigation, interview plans and method lessons: `investigator-coach`.
- Every unanswered question in the export, with the follow-up columns: `open-questions-register`.
- Test points for auditors on whether the lessons were applied: `auditor-assurance-pack`.
- The register's `evidence_strength` values: `check-register` holds them to `evidence-audit`.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/evidence-strength-scorecard.json --strict   # fix every problem it lists
PMLC pack <ws> <run>/outputs/evidence-strength-scorecard.json                  # -> evidence-strength-scorecard.html and .md
PMLC pack <ws> <run>/outputs/evidence-strength-scorecard.json --format docx    # -> a Word copy for the investigation file
PMLC pack-xlsx <ws> <run>/outputs/evidence-strength-scorecard.json --kind question   # -> the requests in Excel
PMLC pack-xlsx <ws> <run>/outputs/evidence-strength-scorecard.json --kind table      # -> the three tables in Excel
```

Offer the docx for the investigation file, and the Excel files for tracking the requests or sorting the tables
(`--format csv` writes nothing here: it exports recommendations, and this pack has none). Tell the user the
single-source and document-only counts, the largest concentration, and the first three requests.
