# The follow-up table contract (investigator-coach)

The `investigator-coach` pack carries one table that goes back into the investigation: the follow-up table. `check-pack` enforces this contract and `pack` writes `follow-up.json` from it. Only this skill uses it; `pack-schema.md` points here.

## The table

- One `table` item with `"id": "follow-up"`, in the `follow-up-per-finding` section.
- Its columns are exactly `Finding`, `Evidence to collect`, `Key questions`, `Suggested interviews`, `Causal hypothesis`, in that order. `check-pack` reports `investigator-coach: needs a table item with id follow-up and columns [...]` otherwise.
- **One row per condition.** The first cell holds that condition's high-rated Finding IDs, comma-separated (`FND-0002, FND-0005`). Nothing else goes in the first cell: `check-pack` reports `follow-up.rows[n][0]: must be one or more Finding IDs`.
- **A finding appears in one row only** (`FND-… already has a row` otherwise).
- **Every top-rated finding in the pack's coverage has a row.** Under `--strict`, `check-pack` reports `follow-up: no row for top-rated finding(s) …` for any that is missing (the `follow-up-per-top` rule in `pack-profiles.json`). An excluded finding (`exclusions`, with its reason) needs no row.
- Give the table `row_cites`, one list per row, holding at least that row's Finding IDs.
- Keep each cell specific to the finding's evidence: the record to pull, the question to ask, the role to interview, the hypothesis to test. Roles only in Suggested interviews, never a person's name.

## Notes for one finding in a shared row

When one finding in a shared row needs its own note, add `finding_notes` to the table: `{"FND-…": "note"}`. Every key must be a Finding ID in the table's first column, and every note is non-empty text. `finding_notes` is allowed only on the follow-up table.

## follow-up.json

`PMLC pack <ws> <run>/outputs/investigator-coach.json` writes `<run>/outputs/follow-up.json` beside the HTML and Markdown. It maps each Finding ID in the first column to:

```json
{"FND-0003": {"evidence_to_collect": "…", "key_questions": "…", "suggested_interviews": "…",
              "causal_hypothesis": "…", "note": "… (only when finding_notes gives one)"}}
```

The four fields fill the export's Evidence to Collect, Key Questions, Suggested Interviews and Causal Hypothesis columns, ready to paste back into the investigation in ProbeMatrix. They are working papers: when litigation or a regulator's inquiry is in prospect, paste them back only at the direction of the organisation's legal adviser (see the privilege question in `investigator-coach/SKILL.md`).

## Example

```json
{"kind": "table", "id": "follow-up",
 "columns": ["Finding", "Evidence to collect", "Key questions", "Suggested interviews", "Causal hypothesis"],
 "rows": [["FND-0002", "Procedure index history", "Was a checklist ever drafted?", "Maintenance manager",
           "The checklist was dropped in a procedure rewrite"]],
 "row_cites": [["FND-0002"]]}
```
