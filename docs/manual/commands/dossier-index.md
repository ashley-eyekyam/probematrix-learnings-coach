# dossier-index

## What it does

Writes `outputs/dossier-index.json`, a valid pack with one table listing each `dossier-F*.json` pack in the outputs folder: entity, title and item count, with each row citing the findings its dossier cites.

## When to use it

After the cluster dossiers are written, to give them a front page that [check-pack](check-pack.md) and [pack](pack.md) accept.

## Synopsis

```text
pmlc dossier-index ws [--out OUT]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--out` | file | `<run>/outputs/dossier-index.json` | Where to write the pack |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E dossier-index $WS
```

## Common problems

- **"no dossier-F*.json packs found".** Write the dossiers first.

## Related

[index](index.md), [check-pack](check-pack.md)
