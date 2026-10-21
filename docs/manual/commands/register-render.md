# register-render

## What it does

Writes a Learnings Register JSON in two document formats: **`learnings-register.docx`** (a Word document) and **`learnings-register.email.html`** with its plain-text twin **`learnings-register.email.txt`** (an email digest under 100 KB). The sections are those of [register-md](register-md.md): the Summary, every priority-1 learning in full, and a table of all learnings. Each learning's finding and evidence IDs become an endnote in the Word file. Every file carries the status line, the handling lines and the ProbeMatrix credit, and, until the register is approved, the DRAFT marker. The email shows as many learnings as fit and says how many are left out; the Word file always holds them all.

## When to use it

After [check-register](check-register.md) passes, when the register has to go to people who read Word or email rather than Excel. The Markdown and Excel copies stay with [register-md](register-md.md) and [register-xlsx](register-xlsx.md); asking for them here prints `use register-md / register-xlsx` and stops with exit code 2.

## Synopsis

```text
pmlc register-render ws register [--format FORMAT] [--out OUT] [--share {internal,external,public}] [--names NAMES] [--orgs ORGS]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder (it decides the review status and the default output folder) |
| `register` | The Learnings Register JSON |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--format` | `docx`, `email` or `docx,email` | `docx,email` | Which files to write |
| `--out` | folder | `<run>/outputs` | Where to write the files |
| `--share` | `internal`, `external` or `public` | `internal` | Writes a copy for outside the organisation, masked as [register-xlsx](register-xlsx.md) masks it, under names like `learnings-register.external.docx`; see [Review and sharing](../Review-and-sharing.md) |
| `--names` | file | `$PMLC_NAMES` | Names to mask when shared; in any mode the command stops if one appears in an output |
| `--orgs` | file | `$PMLC_ORGS` | Organisation names to mask when shared |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E register-render $WS $OUT/learnings-register.json
python3 $E register-render $WS $OUT/learnings-register.json --format docx
```

## Common problems

- **"use register-md / register-xlsx".** You asked for `md` or `xlsx`; run those commands instead.
- **The files say DRAFT.** The register is not signed off in this workspace, or the investigation is unfinished; see [sign-off](sign-off.md).
- **"cannot share externally".** A shared copy needs an approved sign-off, the right classification and legal review cleared; the message lists what is missing.
- **The email ends with "n more items are in the full pack".** The digest keeps to 100 KB; the Word file holds every learning.

## Related

- [check-register](check-register.md) checks the register first.
- [register-md](register-md.md) and [register-xlsx](register-xlsx.md) write the Markdown and Excel copies.
- [pack](pack.md) writes the same docx and email formats for a learning pack.
