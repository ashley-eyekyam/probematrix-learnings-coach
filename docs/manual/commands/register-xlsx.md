# register-xlsx

## What it does

Writes a Learnings Register JSON to a formatted **Excel workbook**: one row per learning and its recommendations, with the register's review status (draft until a reviewer signs it off, and always draft while the investigation is unfinished), ready to share with management or a safety committee. The status phrase and the ProbeMatrix credit are added for you: every sheet carries the status phrase in its page header (followed by "· DRAFT" until the register is approved), and the About sheet lists the review status, classification, legal review, distribution, version and retention review.

For a regulator or anyone else outside the organisation, `--share external` or `--share public` writes a separate, masked workbook. It works only for an approved register; see [Review and sharing](../Review-and-sharing.md#sharing-outside-the-organisation---share).

## When to use it

After [check-register](check-register.md) passes, whenever someone needs the register as a spreadsheet.

## Synopsis

```text
pmlc register-xlsx register [--out OUT] [--ws WS] [--share {internal,external,public}]
                  [--names NAMES] [--orgs ORGS]
```

## Arguments

| Argument | What it is |
|---|---|
| `register` | The Learnings Register JSON |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--out` | file | `learnings-register.xlsx` next to the register JSON (`learnings-register.external.xlsx` or `.public.xlsx` when shared) | Where to write the workbook. A shared copy written with `--out` goes exactly where you say |
| `--ws` | workspace folder | the run's workspace, when the register sits in `<run>/outputs/` | The workspace used to check whether the investigation is still unfinished (which forces draft) and whether the register was signed off there. Give it when the register is not in a standard run folder: without a workspace the workbook is a draft ("no workspace to check"), and `--share external` is refused |
| `--share` | `internal`, `external` or `public` | `internal` | Who the copy is for. `external` and `public` need the register signed off as approved, with a classification at that level or wider and `legal_review` cleared. Names, organisations, equipment tags, singleton roles, clock times and full dates are masked; the source file name becomes "a ProbeMatrix investigation export", and the About sheet gains a "Sharing" row. A workbook embeds no records, so there is no embed flag here |
| `--names` | file | `$PMLC_NAMES` | A names file, one name per line. A shared copy masks these names |
| `--orgs` | file | `$PMLC_ORGS` | An organisation names file, one per line. A shared copy masks these names |
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

The Hazira register cannot be shared outside, because the investigation is unfinished. Nothing is written:

```bash
python3 $E register-xlsx $OUT/learnings-register.json --share external
```

```text
cannot share externally: review is draft (the investigation status is in progress, no finding is marked as edited by a person); classification is "internal" (needs "external" or "public"); legal_review is not "cleared"
```

On a synthetic, completed investigation (`SO` is its outputs folder), once the register is signed off as approved for external readers with legal review cleared (see [dashboard](dashboard.md#examples)):

```bash
python3 $E register-xlsx $SO/learnings-register.json --share external --orgs $SO/orgs.txt
```

```text
Register with 1 entries and 1 recommendations written to synth/pmlc-runs/2024-03-20-plant-pump-fire/outputs/learnings-register.external.xlsx
```

A copy of that register outside its run folder, without `--ws`:

```bash
python3 $E register-xlsx reg-elsewhere.json --share external
```

```text
cannot share externally: no workspace (pass --ws); review is draft (no workspace to check)
```

Without `--share`, the same copy is written, but as a draft: its sign-off is recorded in a workspace the engine cannot see. The About sheet reads `Review status: draft. Draft because: no workspace to check`, and every sheet's page header ends in "· DRAFT".

## Common problems

- **The workbook is out of date.** It is a copy. Run register-xlsx again after every edit of the JSON.
- **A register outside its run folder.** Without the workspace the engine cannot check the investigation status or the sign-off, so the workbook is a draft with the reason "no workspace to check". Pass `--ws`.
- **"cannot share externally: …".** Each condition after the colon is unmet. Sign the register off for that audience (`sign-off --status approved --classification external --legal-review cleared`), and pass `--ws` when it is not in its run folder.
- **The file is open in Excel.** Close the workbook first, or write to a new name with `--out`.

## Related

- [check-register](check-register.md) checks the register first.
- [dashboard](dashboard.md) shows the same register in the learning map (`dashboard --register`).
- [Skills](../Skills.md): the `learnings-register` skill writes the JSON.
