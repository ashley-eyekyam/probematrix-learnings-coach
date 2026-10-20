# index

## What it does

Writes `outputs/index.html`, one page with a row for each pack (and the register): title, audience (from the skill's `skill.json`), coverage (from the last check record, or "not recorded"), formats present (`html`, `md`, `xlsx`), date (the file's modified date), status (the effective review status, `DRAFT` until signed off) and a relative link. The page carries the status phrase and the version footer, and has no JavaScript.

## When to use it

After [render-all](render-all.md), as the front page of the run's outputs.

## Synopsis

```text
pmlc index ws [--out OUT]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--out` | file | `<run>/outputs/index.html` | Where to write the page |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E index $WS
```

## Common problems

- **Status always DRAFT.** Correct until a person reviews the pack and [sign-off](sign-off.md) records it.

## Related

[render-all](render-all.md), [status](status.md)
