# check-all

## What it does

Checks every pack in the outputs folder with [check-pack](check-pack.md) and the register with [check-register](check-register.md). A pack is a JSON object with a `sections` list; `learnings-register.json` is the register; other files (`gaps.json`, `plan.json`, `actions.json`, `*.jsonl`) are ignored. It prints one line per file, `ok` or `<n> problem(s)`, lists the problems on stderr, and exits 1 if any file has a problem.

## When to use it

After writing or editing packs, before [render-all](render-all.md).

## Synopsis

```text
pmlc check-all ws [--strict] [--json]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--strict` | none | off | Pass `--strict` to check-pack when this engine's check-pack has it |
| `--json` | none | off | Print one JSON object on stdout; the per-file lines go to stderr |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E check-all $WS
```

```text
board-brief.json: ok
bad-l3-01.json: 2 problem(s)
```

## Common problems

- **Exit 1.** At least one file has problems; the lines under it say which.

## Related

[check-pack](check-pack.md), [check-register](check-register.md), [render-all](render-all.md)
