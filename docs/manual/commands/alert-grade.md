# alert-grade

## What it does

Reads a Learnings Register and says which learnings a safety alert carries by default and what grade the alert has. The grades are `alert`, `notice` and `information`, highest first.

- **The learnings.** By default, the priority-1 learnings, ordered by transferability (industry-wide, then other sites, then same site), then by evidence strength (corroborated, then direct, then inferred), then by LR-ID; the top 3. `--lr` chooses them instead.
- **The grade from the register.** When any chosen learning has an `urgency`, the grade is the highest of them, and the source is `register urgency`. A chosen learning without one is named in a note.
- **A suggested grade.** When none of them has an `urgency`, the command suggests one and says it is a suggestion: priority 1 with transferability `other sites` or `industry-wide` gives `alert`; priority 1 at the same site, or priority 2, gives `notice`; anything else gives `information`. The highest suggestion wins. The coach then asks you which grade the alert has, and the pack records `grade_source: "chosen by the user"`. The word `suggested` never goes into a pack.

It reads the register only and writes no file. It never writes an owner, a date or a grade into a pack. A re-run gives identical output.

## When to use it

Before writing a safety alert, so the alert carries the learnings that travel furthest and a grade you have confirmed.

## Synopsis

```text
pmlc alert-grade ws [--register REGISTER] [--lr LR-ID] [--json]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--register` | file | `<run>/outputs/learnings-register.json` | The register to read |
| `--lr` | an LR-ID, repeatable | the top 3 priority-1 learnings | The learnings the alert carries |
| `--json` | none | off | Print `{grade, grade_source, suggested, learnings, notes}` as JSON. `grade_source` is `register urgency` or `suggested`; `suggested` holds the suggestion per learning and the rule |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E alert-grade $WS
python3 $E alert-grade $WS --lr LR-01 --lr LR-04 --json
python3 $E register-items $WS --lr LR-01 --lr LR-02 --lr LR-03
```

On the Hazira register the default learnings are LR-01, LR-02 and LR-03. Over all 25 learnings the rule suggests 11 alerts, 12 notices and 2 information, so while those three have no `urgency` the suggested grade is `alert`; once the register records an urgency for them, that urgency gives the grade.

## Common problems

- **"alert-grade reads a learnings register, and … is not one"**. You passed a pack or another JSON file. Pass the register. Exit code 2.
- **"alert-grade: LR-09 is not in the register …"**. An `--lr` names a learning the register does not have. Exit code 2.
- **"note: LR-01 has urgency 'High', not one of alert, notice or information: it is ignored"**. The register's `urgency` for that learning is not one of the three grades, so it does not count. Correct it in the register. Exit code 0.
- **"note: LR-05 is priority 2; the safety-alert check needs priority 1"**. An `--lr` names a learning that is not priority 1; `check-pack` refuses a safety alert that carries it. Exit code 0.
- **"no priority-1 learning: choose with --lr"**. The register has no priority-1 learning, so there is no default. Choose the learnings with `--lr`. Exit code 0.

## Related

- [register-items](register-items.md) prints the chosen learnings as learning items for the pack.
- [check-pack](check-pack.md) warns when a pack has no `grade` or `grade_source`.
- [pack](pack.md) writes a sister-site or industry alert as a review copy until it is approved and shared.
