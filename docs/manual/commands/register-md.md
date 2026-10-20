# register-md

## What it does

Writes a Learnings Register JSON to **`learnings-register.md`**: a Summary (the same counts as the Excel Summary sheet), every priority-1 learning in full (lesson, context, recommendations table, evidence IDs, tiers) and a table of all learnings. The file starts with the register title and, until the register is approved, a DRAFT marker and the handling lines, and ends with the ProbeMatrix credit. Never write `learnings-register.md` by hand; run this command.

## When to use it

After [check-register](check-register.md) passes, whenever someone needs the register as readable text.

## Synopsis

```text
pmlc register-md ws register [--out OUT]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder (it decides the review status and the default output folder) |
| `register` | The Learnings Register JSON |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--out` | file | `<run>/outputs/learnings-register.md` | Where to write the Markdown |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E register-md $WS $OUT/learnings-register.json
```

## Common problems

- **"is a pack, not a register".** You gave a pack JSON; give the register JSON.
- **The file says DRAFT.** The register is not signed off in this workspace, or the investigation is unfinished; see [sign-off](sign-off.md).

## Related

- [check-register](check-register.md) checks the register first.
- [register-xlsx](register-xlsx.md) writes the same register to Excel.
- The register format: [register-schema.md](https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/skills/learnings-coach/references/register-schema.md).
