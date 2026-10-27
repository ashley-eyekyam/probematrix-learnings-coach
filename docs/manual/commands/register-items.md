# register-items

## What it does

Prints Learnings Register entries as a JSON list of **learning items** for a learning pack: the entries one tier must learn (`--tier`), the learnings you name (`--lr`), the transferable ones (`--transferable`: transferability `other sites` or `industry-wide`), or a combination, which keeps only the entries that meet every selector. Priority 1 comes first, then 2 and 3, ties by LR-ID; with `--lr` the items follow the order you give. With `--tier` each item's `id` is the tier and the LR-ID in lowercase (`t3-lr-08`), so a pack that pastes several tiers has no duplicate ids; without it the `id` is the LR-ID in lowercase (`lr-08`). Each item carries `learning` (the LR-ID), the lesson (the register's message for that tier when it has one, otherwise the lesson statement), an explanation, and the entry's Finding and Evidence IDs as `cites`.

It prints to the screen only; it writes no file.

## When to use it

While writing a pack for one tier, or a safety alert from the learnings [alert-grade](alert-grade.md) chose, so the pack repeats the register's wording instead of retyping it.

## Synopsis

```text
pmlc register-items ws [--tier {T1,T2,T3,T4,T5}] [--register REGISTER] [--lr LR-ID] [--transferable]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--tier` | `T1`, `T2`, `T3`, `T4` or `T5` | none | Which tier's learnings to list. Required unless `--lr` or `--transferable` is given |
| `--register` | file | `<run>/outputs/learnings-register.json` | The register to read |
| `--lr` | an LR-ID, repeatable | none | Keep only these learnings, in this order |
| `--transferable` | none | off | Keep only the learnings whose transferability is `other sites` or `industry-wide` |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E register-items $WS --tier T3 > t3-learnings.json
python3 $E register-items $WS --lr LR-01 --lr LR-02 --lr LR-03
python3 $E register-items $WS --transferable
```

## Common problems

- **"No Learnings Register at …".** Write the register first, or pass `--register`.
- **"register-items: give --tier, --lr or --transferable"**. Name at least one selector. Exit code 2.
- **"register-items: LR-09 is not in the register …"**. An `--lr` names a learning the register does not have. Exit code 2.
- **An empty list.** No entry meets the selectors (no entry lists that tier, for example).

## Related

- [table-item](table-item.md) prints table items.
- [alert-grade](alert-grade.md) chooses the learnings a safety alert carries.
- [check-pack](check-pack.md) checks the items once they are in a pack.
