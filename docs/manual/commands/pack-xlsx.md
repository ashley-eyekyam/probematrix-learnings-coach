# pack-xlsx

## What it does

Writes the `test_point` or `question` items of a learning pack to one Excel sheet: a column for each item field, then a `cites` column with the Finding and Evidence IDs. The sheet carries the "Learning purposes: not a statutory document" header (with DRAFT while the pack is not approved) and the version footer when printed. The pack must pass the same checks as [pack](pack.md).

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
| `--share` | `internal`, `external` or `public` | the pack's classification | Lint the pack for this audience |
| `--names` | file | `$PMLC_NAMES` | Names file for the language check |
| `--orgs` | file | `$PMLC_ORGS` | Organisation names file for the language check |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E pack-xlsx $WS $RUN/outputs/auditor-assurance-pack.json --kind test_point
```

## Common problems

- **"… has no test_point items".** The pack holds no items of that kind.
- **Problems listed and nothing written.** Fix what [check-pack](check-pack.md) lists.

## Related

- [pack](pack.md) writes the HTML and Markdown.
- [register-xlsx](register-xlsx.md) does the same for the register.
