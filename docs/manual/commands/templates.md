# templates

## What it does

Writes one of three files your organisation fills in: `adoption.csv` (did you accept each learning), `distribution.csv` (who each pack reached) or `verification.jsonl` (did each learning stick). The engine fills in only the ids, titles and pack names. Every column that records a decision, an owner or a date is left blank, because those belong to your organisation.

## When to use it

After the register exists (adoption, verification) or after the packs exist (distribution), when you want a file to record what happened next. Other commands read the files back; a blank row simply counts as "not yet recorded".

## Synopsis

```text
pmlc templates ws mode [--register FILE] [--out PATH]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |
| `mode` | Which file to write: `adoption`, `distribution` or `verification` |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--register` | file | `<run>/outputs/learnings-register.json` | The Learnings Register to list (adoption and verification) |
| `--out` | file | `<run>/outputs/<file>` | Where to write the file |
| `-h`, `--help` | none | | Show the flags and stop |

### The files

| File | Columns |
|---|---|
| `adoption.csv` | `lr_id`, `title` (filled), then `response` (accepted, modified or rejected), `reason`, `owning_role`, `target_window` |
| `distribution.csv` | `pack`, `audience` (filled, one row per pack in outputs), then `channel`, `date`, `delivered_by_role`, `attendees`, `contractors_included` (yes or no; `y` and `n` count too), `questions_raised`, `concerns_escalated` |
| `verification.jsonl` | One JSON line per learning: `lr_id`, then `check_date`, `level` (communicated, understood, applied or effective), `evidence`, `assessed_by_role`, all `null` |

Open the CSV files in Excel and save them as CSV again; the engine reads the saved file (extra or reordered columns, blank rows and Excel's byte-order mark are fine). A value outside the allowed ones is reported with its file and row, for example `adoption.csv row 3: response 'maybe' must be one of accepted, modified, rejected`. Every bad row is reported, not only the first, and the good rows are still read.

## Examples

```bash
python3 $E templates $WS adoption
```

```text
wrote .../outputs/adoption.csv (12 rows); the organisation fills in the blank columns
```

## Common problems

- **"already exists and may hold your organisation's entries".** The command never overwrites a file. Move the old file, or pass a new `--out`.
- **"No Learnings Register".** Write the register first, or pass `--register FILE`.
- **Use roles, not names.** Fill the `*_role` and `owning_role` columns with roles. Run `scan-names` over the folder before sharing.

## Related

- [export-actions](export-actions.md) writes the action list for your tracking system.
- [check-register](check-register.md) checks the register these files list.
