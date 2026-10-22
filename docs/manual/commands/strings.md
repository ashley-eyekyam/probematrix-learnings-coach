# strings

## What it does

Moves a learning pack through translation and back. `strings extract` writes the pack's translatable text to a file a translator can work in: XLIFF 1.2 (the default, for translation tools) or CSV (for Excel). `strings apply` reads the translated file and writes a new pack, `<pack>-<lang>.json`, that `check-pack` and `pack` treat like any other pack.

The engine never translates anything itself. A person (or a translation tool they run) fills in the targets, and a fluent speaker checks the result before it is used.

What the file holds:

- **The status line and the ProbeMatrix footer** sit in two file-level `<note>` elements in the XLIFF `<header>`. They are not units: nothing there is translated.
- **One unit per piece of text**, named by its place in the pack (for example `sections[1].items[0].what_happened`).
- **Locked fields are never offered**: the pack name, schema, skill, status line and scope; every `kind`, `id` and cite field; `evidence_strength`, `hoc_tier`, `group`, `learning`, `clauses`, `comparator_refs`, `state`, `type`, `hold_point`, `seconds`, `offset`, `correct`; timeline dates and times; graph node ids. They are copied unchanged.
- **Citations become placeholders.** An inline `[FND-0002; EVD-007]` (or a bare ID) becomes `{c1}` in CSV, or `<x id="c1" ctype="x-pmlc-cite"/>` in XLIFF. Keep every placeholder exactly once; `apply` puts the IDs back.
- **A glossary note on each unit** lists the terms from `references/glossary.json` found in its text, as `term = translation` or `term (keep as written)` (ProbeMatrix, HFACS, Finding ID and the other names and codes). The Hindi glossary is AI-drafted: check it with a fluent speaker.
- **A back-translation unit for each safety-critical item**, named `<item>#back_translation`. An item is safety-critical when it is a `check` with `hold_point: true`, or when its English says stop, halt, or do not start, proceed, restart or enter. The translator writes their translation back into English there, so a reviewer can compare it with the source.

What `apply` writes into `<pack>-<lang>.json`:

- `pack` = `<pack>-<lang>`, `skill` = the source pack's skill, `translation_of` = the source pack's name, and `lang`;
- the translated text, with the IDs restored;
- on each safety-critical item, `source_text` (each field's English) and `back_translation`;
- no `handling` block: a sign-off of the English is not a sign-off of the translation. Sign the translation off on its own after review.

The status line, the DRAFT label and the ProbeMatrix footer stay in English, word for word, and every page of a translated pack shows `Translated with AI assistance: have a fluent speaker check it before use` under its status line.

## When to use it

After the English pack has passed `check-pack` and been reviewed, when a pack needs to reach readers in another language (for example a Hindi version of the frontline learning cards). Extract, send the file to the translator, apply what comes back, then check and render the translated pack.

## Synopsis

```text
pmlc strings extract ws pack [--to {xliff,csv}] [--lang LANG] [--out FILE]
pmlc strings apply ws pack file --lang LANG [--to {xliff,csv}] [--allow-partial] [--out FILE]
```

## Arguments

| Argument | What it is |
|---|---|
| `action` | `extract` (write the strings file) or `apply` (read a translated strings file) |
| `ws` | The workspace folder |
| `pack` | The English pack JSON (for `apply`, the same pack the strings were extracted from) |
| `file` | `apply` only: the translated `.xlf` or `.csv` file |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--to` | `xliff` or `csv` | `xliff` for `extract`; for `apply`, read from the file's extension | The strings file format |
| `--lang` | language tag | `hi` for `extract`; required for `apply` | The translation's language, such as `hi` or `pt-BR`. It goes in the XLIFF `target-language`, or the CSV's `note` column |
| `--allow-partial` | none | off | `apply` only: keep the English of any untranslated unit instead of refusing |
| `--out` | file | `<run>/outputs/<pack>.strings.xlf` or `.strings.csv` (`extract`); `<run>/outputs/<pack>-<lang>.json` (`apply`) | Where to write. An existing file is never overwritten |
| `-h`, `--help` | none | | Show the flags and stop |

`action` is `extract` or `apply`.

The CSV has the columns `id`, `source`, `target` and `note`, and starts with a byte-order mark so Excel opens it as UTF-8. Fill in `target` only. In Excel, save it with **Save As > CSV UTF-8**; a plain "CSV (Comma delimited)" file is in a legacy code page, loses the Devanagari and is refused. Saved as CSV UTF-8, a byte-order mark, Windows line ends, extra or reordered columns and blank rows are all accepted. A cell that starts with `=`, `+`, `-` or `@` is written with a leading `'` so Excel does not run it as a formula; `apply` removes it again.

`apply` refuses (exit 1, nothing written) when:

- a placeholder is missing or added: `<unit>: placeholders differ from the source ({c1} missing or added); keep every {cN} exactly once`;
- a unit is untranslated, unless `--allow-partial` is given;
- the English pack has changed since the strings were extracted, or the file names a unit the pack does not have (extract again);
- the file is for another language than `--lang` (the XLIFF `target-language`, or the CSV note's `target-language:`);
- the file contains a DOCTYPE or an entity declaration: `strings file must not contain a DOCTYPE or entity declarations`.
- the file is not UTF-8 text (for example UTF-16, or a legacy Excel CSV): `strings file must be UTF-8 text`;
- a target adds a Finding or Evidence ID of its own: citations travel only as the `{cN}` placeholders.

`check-pack` on a translated pack also:

- warns `item <id> is safety-critical: add back_translation` (a problem with `check-pack --strict`);
- when the source pack `<translation_of>.json` sits beside it or in `<run>/outputs/`, requires the same cites, ids, kinds and section ids. A difference is always a problem: `<path>: differs from the source pack <name>`.

## Examples

```bash
python3 $E strings extract $WS $WS/../outputs/frontline-learning-cards.json --lang hi
```

```text
strings written to .../outputs/frontline-learning-cards.strings.xlf (211 units, xliff, en -> hi); translate the targets, then run strings apply
```

```bash
python3 $E strings extract $WS $WS/../outputs/frontline-learning-cards.json --to csv
python3 $E strings apply $WS $WS/../outputs/frontline-learning-cards.json $WS/../outputs/frontline-learning-cards.strings.csv --lang hi
python3 $E check-pack $WS $WS/../outputs/frontline-learning-cards-hi.json --strict
python3 $E pack $WS $WS/../outputs/frontline-learning-cards-hi.json
```

```text
translation written to .../outputs/frontline-learning-cards-hi.json; check it with check-pack, and have a fluent speaker review it before use
```

## Common problems

- **"already exists and may hold your translator's work" or "may hold a reviewed translation".** The command never overwrites a strings file or a translated pack. Move the old file, or pass a new `--out`.
- **"placeholders differ from the source".** The translator dropped, doubled or invented a `{cN}`. Put each placeholder back once, anywhere in the sentence that reads naturally.
- **"units are untranslated".** Finish the translation, or pass `--allow-partial` to keep the English for now. A safety-critical item without a back-translation is then flagged by `check-pack`.
- **"the English has changed since extract".** The English pack was edited after the strings were extracted. Extract again and carry the translations across.
- **The translated page shows English words.** The status line, DRAFT label and footer are always English. Page labels come from `references/labels/<lang>.json`; a language without a labels file shows English labels.
- **Have it checked.** Every translation is marked as AI-assisted until a fluent speaker has reviewed it. Use roles, not names, in any translator's comments.

## Related

- [check-pack](check-pack.md) checks the translated pack, including the source comparison and the back-translations.
- [pack](pack.md) renders the translated pack.
- [sign-off](sign-off.md) records the fluent speaker's review.
