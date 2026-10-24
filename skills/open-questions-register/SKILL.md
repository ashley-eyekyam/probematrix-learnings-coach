---
name: open-questions-register
description: Lists what a ProbeMatrix investigation export leaves unanswered, as a register of open questions - the follow-up columns left empty on every finding, the blank Incident Summary fields, the findings whose justification says a record is absent or is hedged, and the gaps other packs recorded - each question with the finding it would firm up and the kind of source to look for, plus a follow-up CSV that pastes back into the export. Use when someone with a ProbeMatrix export asks what the investigation could not answer, what is still open or unknown, which records are missing, or wants an open-questions list or follow-up sheet for the investigation team. Not for coaching the investigation method, interview plans or causal hypotheses (use `investigator-coach`), and not for rating how strong the evidence is (use `evidence-strength-scorecard`).
---

# Open Questions Register

Engine: `PMLC` as in `learnings-coach/references/skill-common.md` §1; this skill needs the `learnings-coach` skill installed alongside it.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions; run `PMLC setup`
when only an .xlsx was given). Needs: `workspace` and `open-questions` (`PMLC open-questions <ws>` writes it).
Optional: `gaps` (`<run>/outputs/gaps.json`, which `pack` collects from the packs already rendered in this run) and
`evidence-audit` (`PMLC evidence-audit <ws>`, to say which questions would turn a single-source finding into a
corroborated one). Read `learnings-coach/references/learning-principles.md` (§2: the AI justification is
reasoning, not evidence; name the evidence that would settle a gap). A hedged justification marks where more
evidence would raise confidence; it is not a mistake by the analyst.

This skill *lists* the questions. It does not coach the method, plan interviews or propose causal hypotheses: that
is `investigator-coach`, which takes this register's questions as its starting list.

## Gather

```bash
PMLC open-questions <ws>             # the counts; writes <ws>/open_questions.json (merges gaps.json when present)
PMLC open-questions <ws> --json      # the lists: empty columns, blank fields, absence, hedged, and the packs' gaps
PMLC open-questions <ws> --items     # up to 30 question items, ready to paste
PMLC evidence-audit <ws>             # optional: which findings rest on a single source
```

The engine finds absence ("no record", "missing", "lack of") and hedging ("may", "likely", "suggests") in the AI
justification by fixed word lists, at word boundaries; the lists live in `learnings-coach/references/open-questions.json`.
A match is a pointer, not a verdict: read the finding before you rely on it. Paste the `--items` output unchanged;
never retype a count, a question or a finding ID. The order is the engine's: empty columns first, then the
top-rated absence findings, then the other absence findings, then the hedged ones.

## Write

Write `<run>/outputs/open-questions-register.json` in the shape in `learnings-coach/references/pack-schema.md`.

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/open-questions-register.json (repository only).

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | What is most open and what would settle it first; cite the findings behind each point | `bottom_line` | up to 5 |
| 1 | `summary` | What the export leaves open | The counts from `open-questions`, in words: the empty columns, the blank fields "x of y", the absence and hedged findings "x of the n", and the gaps from other packs; cite the findings the questions start from | `para` | up to 2 |
| 2 | `follow-up-columns` | Follow-up columns | Columns Follow-up column, Findings with an entry, Suggested source: one row per empty column from `--json`, "0 of n", and the `good_evidence` of that column's question in `--items` | `table` | 1 |
| 3 | `summary-fields` | Blank Incident Summary fields | Columns Group, Blank fields: every blank field from `--json`, each once, grouped (when and where, consequence, risk, regulatory, people and team, record dates); leave out when none is blank | `table` | optional, up to 1 |
| 4 | `questions` | Questions to settle | The `--items` output, pasted unchanged | `question` | up to 30 |
| 5 | `from-other-packs` | Questions other packs raised | One question per gap in `--json` `gaps`: the gap turned into a question; `why` names the pack (`Recorded as a gap by the <pack> pack.`); `good_evidence` is the gap's `evidence_needed`, verbatim; `cites` the gap's cites; `group` the pack | `question` | optional, up to 20 |

- Roles only. A question about who decided something asks for the record of the decision, never for a person.
- No `answer`, `to` or `type` on a question: this is a list to settle, not an interview plan or a quiz.
- Add `limits` naming how many absence and hedged findings the 30 questions leave out, and that
  `open_questions.json` lists them all. Put no `gaps` of your own: the gaps are already questions here.
- Carry `learning: "LR-nn"` on a bottom-line point that a register learning would change (`skill-common.md` §3),
  with that learning's other `finding_ids` in `supporting_cites`.
- The language check reads two-word field names such as Persons Affected as personal names (JC1). On the two
  tables only, add `"lint_ok": {"rule": "JC1", "reason": "export column and Incident Summary field names, not people"}`;
  in prose, write the fields in lower case ("the due and completion dates").

```json
{"kind": "question", "question": "What record shows who approved the substitute seal?", "group": "supply-chain-contractor-learnings",
 "why": "Recorded as a gap by the supply-chain-contractor-learnings pack.", "good_evidence": "Purchase orders and stores issue records",
 "cites": ["FND-0003"]}
```

## If the evidence is thin

Follow `skill-common.md` §6, and:
- **No justification text, or nothing matches the word lists:** `open-questions` says so in a note. Keep the
  columns and fields sections, write the summary from them, and say in `limits` that absence and hedging could not
  be checked. Never add questions the engine did not find.
- **No Incident Summary fields** ("0 of 0"): leave out `summary-fields` and say so in the summary.
- **An older workspace** (the note "ingested before blank summary fields were recorded"): re-run `PMLC setup` or
  `PMLC ingest`, then `open-questions` again.
- **No other pack rendered yet:** there is no `gaps.json`; leave out `from-other-packs`. Re-run this skill after
  the other packs to add their gaps.

## Not covered here

- Coaching the method, the interview plan and causal hypotheses to test: `investigator-coach`.
- How strong the evidence behind each finding is, and where it rests on one source: `evidence-strength-scorecard`.
- Comparing this investigation with an official report: `report-comparison`.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/open-questions-register.json --strict   # fix every problem it lists
PMLC pack <ws> <run>/outputs/open-questions-register.json                  # -> .html, .md and open-questions-follow-up.csv
```

`pack` also writes `<run>/outputs/open-questions-follow-up.csv`: one row per cited finding, in the export's own
follow-up columns (Finding ID, Evidence to Collect, Key Questions, Suggested Interviews, Causal Hypothesis), with
the questions under Key Questions and their sources under Evidence to Collect. The investigation team pastes it
back into the ProbeMatrix export. Suggested Interviews and Causal Hypothesis stay blank for the team. The
organisation may fill the file in, so `pack` never overwrites it; move the old one aside to write it again. A shared
copy (`--share external`) writes only the masked `open-questions-follow-up.external.csv`.

Tell the user the HTML path first, then the CSV: how many questions, which kinds of record would settle the most,
and that `investigator-coach` can turn the list into an interview plan.
