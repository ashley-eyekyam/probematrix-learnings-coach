# facts

## What it does

Prints the headline numbers of a workspace so a pack quotes the same figures every time: findings, evidence items, findings per HFACS level, the share at levels 3 and 4, findings per cluster and per tier, the top rating and how many findings have it, the incident date, and (with a register) the priority-1 learnings for each tier. Without clusters the cluster and tier counts are empty, and without a register the priority-1 list is `null`.

## When to use it

Before writing any sentence that contains a number.

## Synopsis

```text
pmlc facts ws [--register REGISTER] [--json]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--register` | file | `<run>/outputs/learnings-register.json` when present | The register for the priority-1 list |
| `--json` | none | off | Print one JSON object instead of a Markdown table |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E facts $WS --json
```

On Hazira this gives 436 findings, 46 evidence items, 36, 92, 167 and 141 findings at levels 1 to 4, and 0.706 at levels 3 and 4.

## Common problems

- **"No Learnings Register at …".** The file you passed with `--register` does not exist.

## Related

- [profile](profile.md) is the longer profile.
- [run-path](run-path.md) also prints the top rating and incident date.
