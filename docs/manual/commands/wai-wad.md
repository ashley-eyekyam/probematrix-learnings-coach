# wai-wad

## What it does

Sets work as imagined against work as done, and writes `wai_wad.json` in the workspace. Work as imagined is what the documents say; work as done is what witnesses, logs and recordings show. For each HFACS code, the command lists the findings backed by documents, the findings backed by witness statements, log records or recordings, and those backed by both. A code that has both kinds of evidence is a gap to explore: the paper and the practice can be set side by side. It also marks the findings whose justification uses counterfactual wording ("failed to", "did not", "lack of" and the like), and turns them into questions of the form "What made sense at the time about …?". The evidence types and the word list are data in `references/learning-team.json`. The engine counts; it says nothing about the people involved.

## When to use it

Before a learning team session, or when a pack (such as a facilitator guide) needs the gap table or the prompts. Also when you want to know how much of the export rests on documents alone.

## Synopsis

```text
pmlc wai-wad ws [--json] [--table-item gaps|codes] [--items prompts] [--top N]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--json` | none | off | Print the comparison as one JSON object (`command`, `ok`, `exit_code`, `wai_wad`) |
| `--table-item` | `gaps` or `codes` | none | Print a ready `table` item for a pack, with `row_cites`, instead of the summary |
| `--items` | `prompts` | none | Print ready `question` items, highest-rated finding first |
| `--top` | number | 30 | With `--items`: at most this many questions |
| `-h`, `--help` | none | | Show the flags and stop |

The command always writes `wai_wad.json`, with sorted keys, so a re-run gives identical bytes. After a re-ingest, `status` shows it as stale.

How the counts work:
- A finding has document evidence when any linked evidence item is a `document`, and work-as-done evidence when any is a `witness_statement`, `log_record` or `recording`.
- A code has both when, across its findings, at least one linked item is a document and at least one is work-as-done evidence.
- A finding is counterfactual when its justification matches a whole word or phrase in the list, ignoring case. "Failed tolerance" does not match "failed to".

Each question item cites its finding. The export's counterfactual words appear only in the `why` line, in quotes, so the question itself stays free of them. Because the `why` line quotes them, `check-language` reports a JC3 warning there: a pack that quotes them adds `lint_ok` with the reason.

The learning team's own answers go in `learning-team-notes.csv`, a blank file that `pmlc templates ws learning-team` writes (see [templates](templates.md)).

## Examples

```bash
python3 $E wai-wad $WS
python3 $E wai-wad $WS --table-item gaps
python3 $E wai-wad $WS --items prompts --top 5
```

On Hazira, 68 of the 94 codes have both document and work-as-done evidence. 92 findings have both, and 210 have some work-as-done evidence. 337 findings use counterfactual wording; the earlier planning figure of 353 was never reproducible, because its word list was not recorded.

## Common problems

- **"no witness statement, log record or recording".** The export has no work-as-done evidence linked to a finding. The `gaps` list is empty and the command still exits 0; collect that evidence first.
- **A question reads awkwardly.** It quotes the finding's short description. Edit the wording in your pack, keeping the finding cite.
- **A word is missing from the list.** Add it to `counterfactual` in `references/learning-team.json`; the numbers will move, so re-pin any calibration that depends on them.

## Related

- [templates](templates.md) writes the blank learning-team notes file.
- [open-questions](open-questions.md) lists what the export leaves open.
- [evidence-audit](evidence-audit.md) counts evidence strength.
