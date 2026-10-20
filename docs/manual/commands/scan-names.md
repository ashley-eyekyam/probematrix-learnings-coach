# scan-names

## What it does

Searches files for a list of **personal names**, as a de-identification check before anything leaves the team. It reads text files, JSON, Markdown and HTML, and inside Word, Excel and PowerPoint files (including comments and author fields), and PDF metadata when `pdfinfo` is installed. Every hit is printed with the file, the line and the words around it.

The goal is **zero hits**. The exit code says how it went:

| Code | Meaning |
|---|---|
| 0 | No hits, and every file could be read |
| 1 | At least one hit |
| 2 | No hits, but some files could not be read, so zero hits does not cover them |

## When to use it

Before sharing any output outside the people who already know the names, and before publishing a sample. Use it on the outputs folder and on any PDF text you have extracted.

## Synopsis

```text
pmlc scan-names names paths [paths ...] [--show SHOW] [--variants] [--patterns]
```

## Arguments

| Argument | What it is |
|---|---|
| `names` | A text file with one name per line. Blank lines and lines starting with `#` are skipped, so you can add comments. Keep it outside the repository |
| `paths` | One or more files or folders to scan. Folders are scanned with everything inside them |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--show` | number | 50 | Print at most this many hits. The count at the end is always the full number |
| `--variants` | none | off | Also match each name's surname, initial and surname, and honorific and surname (for the fictional "Jane Placeholder": "Placeholder", "J. Placeholder", "Ms Placeholder"). A one-word variant that is a role noun or a vocabulary word (the surname of "Fictional Officer") is skipped, so roles such as "Procurement Officer" are not hits |
| `--patterns` | none | off | Also flag e-mail addresses, phone-like numbers and staff-number patterns. An aid only: it gives false hits (dates and long record numbers look like phone numbers) and is not proof of de-identification |
| `--json` | none | off | Print one JSON object on stdout instead of the report: `{command, ok, exit_code, output}` plus, for this command, `hit_count` (a number) and `unread` (the files that could not be read). On failure `ok` is false and `error` holds the reason. Messages go to stderr. The exit code is the same as without `--json` |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

A names file. Both names are fictional:

```text
# fictional names for this example
A. B. Example
Jane Placeholder
```

The Hazira outputs, which name roles only:

```bash
python3 $E scan-names names.txt $OUT
```

```text

0 hit(s).
```

With `--variants`, a scan of the Hazira register and learning map gives 1 hit, on the ordinary word "placeholder" in the page's code: the fictional surname is a common word. "Example" alone is not matched, because a one-word variant that is a role noun or a language-check vocabulary word is skipped. Real surnames can still match ordinary words, so read the context of each hit.

The test copy of a pack from [check-language](check-language.md), with one invented paragraph that uses the two fictional names:

```bash
python3 $E scan-names names.txt lint-demo.json --variants
```

```text
HIT lint-demo.json:40: 'A. B. Example' … '     "text": "Shri A. B. Example was careless and should be disciplined; Ms Jane P'
HIT lint-demo.json:40: 'Jane Placeholder' … 'xample was careless and should be disciplined; Ms Jane Placeholder agreed."'

2 hit(s).
```

With `--patterns`, the Hazira outputs give many false hits, which shows why it is only an aid:

```bash
python3 $E scan-names names.txt $OUT --patterns
```

```text
HIT [pattern:phone] hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/board-brief.html:118: '2020-09-24' … 'm">Board and its safety committee · Hazira 2020 · 2020-09-24 · run 2020-09-24-hazira-gas-release-fire · genera'
…
HIT [pattern:phone] hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/board-brief.html:127: '3800419840' … 'E93</button> SAP notification closure oversight - 3800419840 left open · rating 3 · L3 · not cited in this pac'
…
HIT [pattern:email] hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/board-brief.html:128: 'ashley@eyekyam.com' … 'an-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com</footer>'
…
225 hit(s).
```

The dates, the maintenance notification number and the ProbeMatrix contact address are not personal data. Read each pattern hit; do not treat the count as a score.

## Common problems

- **"Names file is empty."** The file has only comments or blank lines.
- **"… file(s) not scanned (this type cannot be read)".** Exit code 2. The list names them. Extract their text (for a PDF: `pdftotext -layout report.pdf report.txt`) and scan the text file.
- **"note: pdfinfo not found: PDF metadata not checked".** Install poppler-utils to check PDF metadata, or extract the text as above.
- **A hit inside a longer word.** Names are matched as whole words, but a common surname can still match an ordinary word or place. Read the context printed with each hit.
- **Zero hits is not the whole check.** A person can be identified by a role only one person holds, a date and a shift. [check-language](check-language.md) (`check-language --share external`) warns about some of these.

## Related

- [ingest](ingest.md) with `ingest --redact` replaces names while reading the export.
- [check-language](check-language.md) catches names and honorifics in packs and registers.
- [Review and sharing](../Review-and-sharing.md) and [Developer tools](../Developer-tools.md) (`tools/make-public-sample.py`).
