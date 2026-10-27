# effect-plan

## What it does

Reads a Learnings Register and sets out, for each learning, what to check and when to check that it worked. It writes `workspace/effect_plan.json`, and with a flag prints a ready item for a pack. It holds:

- **A schedule.** A priority-1 learning gets five checks: 30 days (communicated), 60 days (understood), 90 days (applied), 6 months (applied) and 12 months (effective). Any other learning gets three: 3 months (communicated and understood), 6 months (applied) and 12 months (effective). A learning with no priority, as in a v0.3 register, uses the second schedule and the plan notes it. The cues are in `references/effectiveness.json`.
- **Kirkpatrick levels.** Communicated is L1, understood is L2, applied is L3 and effective is L4. The 3-month check is L1-L2.
- **Jacobsson spread, depth and duration.** Spread follows `transferability` (same site is `site`, other sites is `organisation`, industry-wide is `industry`). Depth follows the strongest recommendation's control tier (elimination, substitution or engineering is `system`; administrative is `procedure`; training or PPE is `individual`; none is `unknown`). Duration is the longest check, `12 months`.
- **The leading indicator.** From the register's `verification.indicator`, else the first recommendation's indicator. The lagging indicator is left blank for the pack to fill in.

Every check is an offset counted from adoption, such as "90 days after adoption". The command writes no calendar date, owner or status: those belong to the organisation (D7). A re-run gives identical output.

## When to use it

Run it once the register passes [check-register](check-register.md), before you write a learning-effectiveness-plan pack.

## Synopsis

```text
pmlc effect-plan ws --register REGISTER [--json] [--table-item {schedule,levels,indicators}] [--items {audit}]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--register` | file | required | The Learnings Register JSON |
| `--json` | none | off | Print the whole plan as JSON |
| `--table-item` | schedule, levels or indicators | none | Print a ready table item (with `row_cites`). `indicators` has the columns `LR`, `Leading` and `Lagging`, and `Lagging` is blank |
| `--items` | audit | none | Print one question item per learning: "What would an auditor see that shows LR-nn is applied?" |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E effect-plan $WS --register $OUT/learnings-register.json
python3 $E effect-plan $WS --register $OUT/learnings-register.json --table-item schedule
```

On the Hazira register the plan has 97 checks: 11 priority-1 learnings with five checks each, and 14 others with three.

## Common problems

- **"effect-plan reads a learnings register (check-register passes on it), not a pack"**. You passed a pack or another JSON file. Pass the register.
- **"the register has no entries"**. The register is empty, so there is nothing to plan.
- **A note that a learning has no priority.** The register comes from an older version. The plan uses the 3-month schedule; add a priority to use the longer one.

## Related

- [check-register](check-register.md) checks the register this command reads.
- [rec-review](rec-review.md) reviews the strength of the same recommendations.
- [table-item](table-item.md) prints other ready table items.
