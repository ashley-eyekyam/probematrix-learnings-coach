# nine-m-actions-template

## What it does

Writes a blank actions sheet from a nine-m-analysis pack: one row per recommendation in the pack's M sections (m1 to m9), with the columns Recommendation ID, M, Change, HoC tier, Corrective/Preventive, Indicator, Owner, Due date, Status and Notes. Owner, Due date, Status and Notes are left blank for the organisation to fill in (D7). Corrective/Preventive is filled when the change says which it is.

The file is `<run>/outputs/<pack>.actions-template.xlsx` (or `.csv`), and it is never overwritten, because your organisation may have filled it in. A pack whose recommendations carry an owner or a due date is refused. The pack is checked first, as `check-pack` does.

For someone outside the organisation, `--share external` or `--share public` writes a masked copy named `<pack>.actions-template.external.xlsx` (or `.public.`). It needs the pack signed off as approved with that classification and `legal_review` cleared. In any mode, a name from `--names` in the output stops the command before anything is written.

## When to use it

After the nine-m-analysis pack passes `check-pack` and is rendered with `pack`, when the organisation is ready to assign the changes in its own action-tracking system.

## Synopsis

```text
pmlc nine-m-actions-template ws pack [--format {xlsx,csv}] [--out OUT]
                             [--share {internal,external,public}] [--names NAMES] [--orgs ORGS]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |
| `pack` | The nine-m-analysis pack JSON |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--format` | `xlsx` or `csv` | `xlsx` | The file type. The CSV has Windows line endings, and a cell that starts with = + - or @ gets a leading quote |
| `--out` | file | `<run>/outputs/<pack>.actions-template.<format>` | Where to write the sheet. An existing file is never overwritten |
| `--share` | `internal`, `external` or `public` | `internal` | Who the copy is for; see above |
| `--names` | file | `$PMLC_NAMES` | A names file, one name per line. A shared copy masks these names, and in any mode one in the output stops the command |
| `--orgs` | file | `$PMLC_ORGS` | An organisation names file, one per line. A shared copy masks these names |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E check-pack $WS $RUN/outputs/nine-m-analysis.json --strict
python3 $E pack $WS $RUN/outputs/nine-m-analysis.json
python3 $E nine-m-actions-template $WS $RUN/outputs/nine-m-analysis.json
python3 $E nine-m-actions-template $WS $RUN/outputs/nine-m-analysis.json --format csv
```

## Common problems

- **"… already exists and may hold your organisation's entries".** The template was written before. Move it, or pass a new `--out` (exit code 1).
- **"…: owner and due dates are set by the organisation, not in this pack".** Remove `owner` and `by_when` from the recommendations, then run again.
- **"… has no recommendation in a section m1 to m9".** The pack holds no change to assign yet.
- **"refused: a listed name appears in the output".** A name from `--names` is in a recommendation. Use the role instead.

## Related

- [pack](pack.md) writes the pack's pages and `nine-m-map.json`.
- [export-actions](export-actions.md) writes the actions of every pack and the register.
- [nine-m-suggest](nine-m-suggest.md) runs the interview the pack is written from.
