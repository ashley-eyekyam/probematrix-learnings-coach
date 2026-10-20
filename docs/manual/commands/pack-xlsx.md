# pack-xlsx

## What it does

Writes the `test_point` or `question` items of a learning pack to one Excel sheet: a column for each item field, then a `cites` column with the Finding and Evidence IDs. The sheet carries the "Learning purposes: not a statutory document" header (with DRAFT while the pack is not approved) and the version footer when printed. The pack must pass the same checks as [pack](pack.md). With `--share external` or `public` the same share gate as [pack](pack.md) applies: the pack must be approved, its classification must be at the mode's level or higher, and `legal_review` must be cleared; otherwise nothing is written and no check is recorded. A shared sheet has names, organisations, tags, singleton roles, times and full dates masked, carries no author or timestamps, and is written as `<pack>-<kind>.<mode>.xlsx`; the command refuses an `--out` that is the internal copy.

## When to use it

When auditors or investigators want to work through a pack's test points or questions in a spreadsheet.

## Synopsis

```text
pmlc pack-xlsx ws pack --kind {test_point,question} [--out OUT] [--share {internal,external,public}] [--names NAMES] [--orgs ORGS]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |
| `pack` | The pack JSON |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--kind` | `test_point` or `question` | required | Which items to write |
| `--out` | file | `<run>/outputs/<pack>-test-points.xlsx` or `-questions.xlsx` | Where to write |
| `--share` | `internal`, `external` or `public` | `internal` | A masked copy for outside the organisation; needs an approved sign-off, the right classification and `legal_review` cleared. Written as `<name>.<mode>.xlsx`, never over the internal copy |
| `--names` | file | `$PMLC_NAMES` | Names file for the language check |
| `--orgs` | file | `$PMLC_ORGS` | Organisation names file for the language check |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E pack-xlsx $WS $RUN/outputs/auditor-assurance-pack.json --kind test_point
```

## Common problems

- **"… has no test_point items".** The pack holds no items of that kind.
- **"cannot share …".** The pack is not approved, its classification is too low or `legal_review` is not cleared. Sign it off first.
- **Problems listed and nothing written.** Fix what [check-pack](check-pack.md) lists.

## Related

- [pack](pack.md) writes the HTML and Markdown.
- [register-xlsx](register-xlsx.md) does the same for the register.
