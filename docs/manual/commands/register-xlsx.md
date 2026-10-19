# register-xlsx

## What it does

Writes a Learnings Register JSON to a formatted **Excel workbook**: one row per learning and its recommendations, with the register's review status (draft until a reviewer signs it off, and always draft while the investigation is unfinished), ready to share with management, a safety committee or a regulator. The status phrase and the ProbeMatrix credit are added for you.

## When to use it

After [check-register](check-register.md) passes, whenever someone needs the register as a spreadsheet.

## Synopsis

```text
pmlc register-xlsx register [--out OUT] [--ws WS]
```

## Arguments

| Argument | What it is |
|---|---|
| `register` | The Learnings Register JSON |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--out` | file | `learnings-register.xlsx` next to the register JSON | Where to write the workbook |
| `--ws` | workspace folder | the run's workspace, when the register sits in `<run>/outputs/` | The workspace used to check whether the investigation is still unfinished (which forces draft). Give it when the register is not in a standard run folder |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E register-xlsx $OUT/learnings-register.json
```

```text
Register with 25 entries and 44 recommendations written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/learnings-register.xlsx
```

A copy elsewhere, naming the workspace:

```bash
python3 $E register-xlsx $OUT/learnings-register.json --ws $WS --out register-copy.xlsx
```

```text
Register with 25 entries and 44 recommendations written to register-copy.xlsx
```

## Common problems

- **The workbook is out of date.** It is a copy. Run register-xlsx again after every edit of the JSON.
- **A register outside its run folder.** Without the workspace the engine cannot see that the investigation is unfinished, so it cannot force the draft status. Pass `--ws`.
- **The file is open in Excel.** Close the workbook first, or write to a new name with `--out`.

## Related

- [check-register](check-register.md) checks the register first.
- [dashboard](dashboard.md) shows the same register in the learning map (`dashboard --register`).
- [Skills](../Skills.md): the `learnings-register` skill writes the JSON.
