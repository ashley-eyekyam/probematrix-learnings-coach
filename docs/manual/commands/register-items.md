# register-items

## What it does

Prints the Learnings Register entries that one tier must learn as a JSON list of **learning items** for a learning pack. Priority 1 comes first, then 2 and 3, ties by LR-ID. Each item's `id` is the tier and the LR-ID in lowercase (`t3-lr-08`), so a pack that pastes several tiers has no duplicate ids. Each item carries `learning` (the LR-ID), the lesson (the register's message for that tier when it has one, otherwise the lesson statement), an explanation, and the entry's Finding and Evidence IDs as `cites`.

It prints to the screen only; it writes no file.

## When to use it

While writing a pack for one tier, so the pack repeats the register's wording instead of retyping it.

## Synopsis

```text
pmlc register-items ws --tier {T1,T2,T3,T4,T5} [--register REGISTER]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--tier` | `T1`, `T2`, `T3`, `T4` or `T5` | required | Which tier's learnings to list |
| `--register` | file | `<run>/outputs/learnings-register.json` | The register to read |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E register-items $WS --tier T3 > t3-learnings.json
```

## Common problems

- **"No Learnings Register at …".** Write the register first, or pass `--register`.
- **An empty list.** No entry lists that tier.

## Related

- [table-item](table-item.md) prints table items.
- [check-pack](check-pack.md) checks the items once they are in a pack.
