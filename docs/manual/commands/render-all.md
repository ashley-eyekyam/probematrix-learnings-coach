# render-all

## What it does

Renders what passed its check: [pack](pack.md) for each pack whose last check passed and whose file has not changed since, then for the register [register-xlsx](register-xlsx.md), `register-md`, and [dashboard](dashboard.md) with the register. A pack or register never checked, failing, or changed since its check is skipped with `skipped <file>: run check-all first`. "Changed" is judged on the content without its `handling` block, so signing a file off after its check does not make the check stale; any other edit does.

## When to use it

After [check-all](check-all.md) is clean.

## Synopsis

```text
pmlc render-all ws [--embed {cited,summary,full}] [--format FORMATS] [--share {internal,external,public}] [--names NAMES] [--orgs ORGS]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--embed` | `cited`, `summary` or `full` | `cited` | Records each page embeds, as for pack |
| `--format` | comma-separated format names | `html,md` | Passed to [pack](pack.md) for every pack, for example `--format html,md,docx`. The register is not affected. A `csv` format refuses to replace an existing `<pack>.actions.csv`, which makes that pack count as failed |
| `--share` | `internal`, `external` or `public` | `internal` | A masked copy for outside the organisation; needs a sign-off |
| `--names` | file | `$PMLC_NAMES` | Personal names, one per line |
| `--orgs` | file | `$PMLC_ORGS` | Organisation names, one per line |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E render-all $WS
```

## Common problems

- **"skipped … run check-all first".** Run [check-all](check-all.md); a pack edited after its check is skipped too.

## Related

[check-all](check-all.md), [index](index.md), [pack](pack.md)
