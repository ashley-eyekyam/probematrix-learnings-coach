# consolidate

## What it does

Reads the could-it-happen-here returns your sites filled in, and writes the corporate view of them. Each return is a copy of the template that [templates](templates.md) `cihh` wrote from a could-it-happen-here pack: the site's name in B1, and for each self-check an answer (`present`, `partly`, `absent` or `n/a`), the site's response and the assessor's role.

It writes two files in `<run>/outputs/`:

- `cihh-consolidated.json`, the view:
  - `returns`: how many returns were read;
  - `coverage`: for each learning, how many returns assessed it (`assessed`) and how many left it blank (`not_assessed`);
  - `conditions`: for each self-check, how many sites found the condition `present` and how many `partly`;
  - `sites`: for each site, the learnings it assessed (a list of `LR-` ids, nothing more).
- `cihh-events.jsonl`, one line per answered row, for the learnings library: `{"type": "site_assessment", "lr_id", "site", "answer", "site_response", "source": "organisation", "event_hash"}`. The site is its real name here; publishing to a library codes it.

The view shows coverage and conditions only. It never ranks or scores a site: there are no per-site counts of conditions found and no totals per site, because a league table would punish the sites that look hardest.

Answers are read without regard to case or spaces, and `N/A`, `na` and `n.a.` all count as `n/a`. Every return is checked first. A return is refused, with one line naming the file and row, when:

- it is not a return at all (not an Excel workbook, or the Site and Pack cells or the column headings are missing);
- its Site cell (B1) is blank;
- a second return names a site that already has one (names are compared without regard to case or spaces);
- an answer is not one of `present`, `partly`, `absent` or `n/a`;
- it was made from another pack's template: its Pack cell (B2) holds the content hash of the pack the template was written from, and it must match `--pack`;
- a row's `lr_id` is not one of the pack's self-checks.

Without `--keep-going`, any problem stops the command and nothing is written (exit code 1). With `--keep-going`, the problems are still listed, and the good returns and rows are consolidated.

For someone outside the organisation, `--share external` or `--share public` writes masked copies named `cihh-consolidated.external.json` and `cihh-events.external.jsonl` (or `.public.`). Each site becomes a code (`S01`, `S02`… in name order), and names, organisations, tags, times and full dates in the text are masked. It needs the pack signed off as approved with that classification and `legal_review` cleared. In any mode, a name from `--names` in the output stops the command before anything is written.

## When to use it

After the sites have sent back the templates written by `templates <ws> cihh --pack <pack>`. Run it again whenever more returns arrive: it rewrites the view from all the returns you pass.

## Synopsis

```text
pmlc consolidate ws RETURN [RETURN ...] --pack PACK [--keep-going]
                 [--share {internal,external,public}] [--names NAMES] [--orgs ORGS]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |
| `RETURN` | The filled return workbooks (`.xlsx`), one per site |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--pack` | file | required | The could-it-happen-here pack the templates were written from |
| `--keep-going` | none | off | List each bad return or row, then consolidate the good ones (exit code 0) |
| `--share` | `internal`, `external` or `public` | `internal` | Who the copy is for; see above |
| `--names` | file | `$PMLC_NAMES` | A names file, one name per line. A shared copy masks these names, and in any mode one in the output stops the command |
| `--orgs` | file | `$PMLC_ORGS` | An organisation names file, one per line. A shared copy masks these names |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

For example, after three sites (North Works, South Terminal and East Depot, invented for the example) returned the template of a could-it-happen-here pack with six self-checks:

```bash
python3 $E templates $WS cihh --pack $RUN/outputs/could-it-happen-here.json
python3 $E consolidate $WS returns/north.xlsx returns/south.xlsx returns/east.xlsx --pack $RUN/outputs/could-it-happen-here.json
```

```text
A self-assessment for each site. Results show coverage and conditions, never a ranking of sites.
consolidated 3 return(s) over 6 self-check(s): coverage and conditions in .../outputs/cihh-consolidated.json; 14 site assessment event(s) in .../outputs/cihh-events.jsonl
```

With a return that has a bad answer:

```text
returns/east.xlsx row 6: answer 'maybe' must be one of present, partly, absent, n/a (or blank)
1 problem(s) in the returns; nothing written (fix them, or pass --keep-going to use the good rows)
```

## Common problems

- **"not a could-it-happen-here return".** The file is not the template, or its first rows or headings were changed. Ask the site to fill in a fresh copy of the template.
- **"Site is blank".** The site did not write its name in B1. Add it and run again.
- **"made from another pack's template".** The pack changed after the template was sent, or the return belongs to another pack. Pass the pack the template was written from, or send the site the new template.
- **"already has a return".** Two returns name the same site. Keep the later one only.
- **"the pack has no self_check items".** `--pack` is not a could-it-happen-here pack.
- **"refused: a listed name appears in the output".** A site response names a person. Use the role instead.

## Related

- [templates](templates.md) writes the return template (`cihh`).
- [pack](pack.md) renders the could-it-happen-here pack the sites read.
- [scan-names](scan-names.md) checks files for listed names before you share them.
