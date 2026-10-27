# templates

## What it does

Writes one of the files your organisation fills in: `adoption.csv` (did you accept each learning), `distribution.csv` (who each pack reached), `verification.jsonl` (did each learning stick) or, with `cihh`, a could-it-happen-here return template for each site. The engine fills in only the ids, titles, pack names and the conditions to look for. Every column that records a decision, an answer, an owner or a date is left blank, because those belong to your organisation.

`cihh` reads the pack named by `--pack` (it is checked first, as `check-pack` does) and writes `<run>/outputs/<pack>.cihh-template.xlsx`, one sheet called `Return`:

- A1 `Site`, with B1 blank for the site to fill in;
- A2 `Pack`, with B2 the pack's content hash, so that [consolidate](consolidate.md) can refuse a return made from another pack's template;
- A3 the reminder "A self-assessment for each site. Results show coverage and conditions, never a ranking of sites.";
- from row 4, the columns `lr_id`, `condition`, `evidence_to_check`, `answer`, `site_response` and `assessed_by_role`, one row per `self_check` item of the pack. The last three are blank, and `answer` offers `present`, `partly`, `absent` and `n/a`.

A `self_check` with no `lr_id` is listed under its item id. A pack with no `self_check` item gives a template with its headings only, and the note "the pack has no self_check items". Send one copy to each site.

For a site outside the organisation, `--share external` (or `public`) writes a masked copy named `<pack>.cihh-template.external.xlsx`: names, organisations, tags, times and full dates in the conditions are masked. It needs the pack signed off as approved with that classification and `legal_review` cleared. B2 still holds the hash of the pack you have, so the returns consolidate against it.

## When to use it

After the register exists (adoption, verification), after the packs exist (distribution), or after a could-it-happen-here pack passes its check (`cihh`), when you want a file to record what happened next. Other commands read the files back; a blank row simply counts as "not yet recorded".

## Synopsis

```text
pmlc templates ws mode [--register FILE] [--out PATH] [--pack PACK]
                       [--share {internal,external,public}] [--names NAMES] [--orgs ORGS]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |
| `mode` | Which file to write: `adoption`, `distribution`, `verification` or `cihh` |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--register` | file | `<run>/outputs/learnings-register.json` | The Learnings Register to list (adoption and verification) |
| `--out` | file | `<run>/outputs/<file>` | Where to write the file |
| `--pack` | file | none | `cihh` only, and required there: the could-it-happen-here pack whose `self_check` items become the rows |
| `--share` | `internal`, `external` or `public` | `internal` | `cihh` only: who the copy is for; see above |
| `--names` | file | `$PMLC_NAMES` | `cihh`: a names file, one name per line. A shared copy masks these names, and in any mode one in the template stops the command |
| `--orgs` | file | `$PMLC_ORGS` | `cihh`: an organisation names file, one per line. A shared copy masks these names |
| `-h`, `--help` | none | | Show the flags and stop |

### The files

| File | Columns |
|---|---|
| `adoption.csv` | `lr_id`, `title` (filled), then `response` (accepted, modified or rejected), `reason`, `owning_role`, `target_window` |
| `distribution.csv` | `pack`, `audience` (filled, one row per pack in outputs), then `channel`, `date`, `delivered_by_role`, `attendees`, `contractors_included` (yes or no; `y` and `n` count too), `questions_raised`, `concerns_escalated` |
| `verification.jsonl` | One JSON line per learning: `lr_id`, then `check_date`, `level` (communicated, understood, applied or effective), `evidence`, `assessed_by_role`, all `null` |
| `<pack>.cihh-template.xlsx` | Site (B1, blank) and Pack (B2, the content hash); from row 4 `lr_id`, `condition`, `evidence_to_check` (filled), then `answer` (present, partly, absent or n/a), `site_response`, `assessed_by_role` |

Open the CSV files in Excel and save them as CSV again; the engine reads the saved file (extra or reordered columns, blank rows and Excel's byte-order mark are fine). A value outside the allowed ones is reported with its file and row, for example `adoption.csv row 3: response 'maybe' must be one of accepted, modified, rejected`. Every bad row is reported, not only the first, and the good rows are still read.

## Examples

```bash
python3 $E templates $WS adoption
```

```text
wrote .../outputs/adoption.csv (12 rows); the organisation fills in the blank columns
```

```bash
python3 $E templates $WS cihh --pack $RUN/outputs/could-it-happen-here.json
```

```text
could-it-happen-here return template with 6 self-check(s) written to .../outputs/could-it-happen-here.cihh-template.xlsx; each site fills in Site (B1), answer (present, partly, absent, n/a), site_response and assessed_by_role
```

## Common problems

- **"already exists and may hold your organisation's entries".** The command never overwrites a file. Move the old file, or pass a new `--out`.
- **"No Learnings Register".** Write the register first, or pass `--register FILE`.
- **"templates cihh needs --pack".** Name the could-it-happen-here pack. `--pack` and `--share` belong to `cihh` only.
- **Use roles, not names.** Fill the `*_role` and `owning_role` columns with roles. Run `scan-names` over the folder before sharing.

## Related

- [export-actions](export-actions.md) writes the action list for your tracking system.
- [check-register](check-register.md) checks the register these files list.
- [consolidate](consolidate.md) reads the sites' could-it-happen-here returns back.
