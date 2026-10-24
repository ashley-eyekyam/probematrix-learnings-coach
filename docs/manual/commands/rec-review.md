# rec-review

## What it does

Reads a Learnings Register and reviews the strength of its recommendations. It prints:

- **Strength bands.** Each recommendation is `stronger` (elimination, substitution, engineering), `intermediate` (administrative), `weaker` (training, PPE, or an administrative change whose text is a procedure, policy, reminder, memo, warning, sign, poster, double-check or re-brief) or `unrated`. The cues are in `references/rec-review.json`.
- **Level match.** A learning whose cited findings include HFACS level 3 or 4 (its own level when none of its findings can be looked up) and whose recommendations include nothing `stronger` or `intermediate` is flagged `weak fix for a deep cause`.
- **Loops.** A change whose text names an assumption, norm, design basis, the standard itself, a target, an incentive or a budget counts as double-loop; the rest are single-loop.
- **SMART gaps.** A recommendation is missing "specific" when its change has fewer than 6 words, "measurable" when it has no leading indicator, and "relevant" when it cites no evidence or finding. Time-bound is never checked: dates are the organisation's to set (D7).
- **Recipients.** How many recommendations each role receives.
- **9M spread.** With `--nine-m`, how many recommendations sit under each of M1 to M9.

It writes no file and no owner or date. A re-run gives identical output.

## When to use it

Run it once the register passes [check-register](check-register.md).

## Synopsis

```text
pmlc rec-review ws register [--nine-m] [--json] [--table-item {strength,spread,smart}]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |
| `register` | The Learnings Register JSON |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--nine-m` | none | off | Also read `<run>/outputs/nine-m-map.json` and count recommendations per M. Exits 2 if the file is missing |
| `--json` | none | off | Print the whole review as JSON |
| `--table-item` | strength, spread or smart | none | Print a ready table item (with `row_cites`) for a pack. `spread` needs `--nine-m` |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E rec-review $WS $OUT/learnings-register.json
python3 $E rec-review $WS $OUT/learnings-register.json --table-item strength
```

On the Hazira register the bands are 24 stronger, 15 intermediate and 5 weaker, and no learning is flagged.

## Common problems

- **"rec-review reads a learnings register (check-register passes on it), not a pack"**. You passed a pack or another JSON file. Pass the register, and run [check-register](check-register.md) on it first.
- **"rec-review --nine-m reads ... nine-m-map.json, which does not exist yet"**. Run the nine-m-analysis skill first, or leave `--nine-m` off.

## Related

- [check-register](check-register.md) checks the register this command reads.
- [table-item](table-item.md) prints other ready table items.
- [recommendation-strength-review](../skills/recommendation-strength-review.md) is the skill that pastes these tables into a review pack.
