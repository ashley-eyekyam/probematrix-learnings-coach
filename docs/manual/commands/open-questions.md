# open-questions

## What it does

Lists what the export leaves open, so a person can decide what to chase. It collects four things, all by fixed rules: the follow-up columns (Evidence to Collect, Key Questions, Suggested Interviews, Causal Hypothesis) that are empty on every finding; the Incident Summary fields left blank; the findings whose AI justification says something is absent (words such as "no record", "missing", "lack of"); and the findings whose justification is hedged (words such as "may", "likely", "suggests"). It also merges in the gaps that earlier packs recorded in `<run>/outputs/gaps.json`.

The word lists live in `references/open-questions.json` (repository only) and are matched without regard to case, at word boundaries, on the justification only: "mayor" does not match "may". The command writes `open_questions.json` to the workspace. With `--items` it prints up to 30 ready `question` items instead: the empty columns first, then the top-rated absence findings, then the other absence findings, then the hedged ones. Each item says in `why` which finding it would firm up, and `good_evidence` names the kind of source to look for: document, witness statement, inspection record, data log or photograph.

The counts describe this one investigation. They are not rates, and a hedged justification is not a mistake: it marks where more evidence would raise confidence.

## When to use it

After [setup](setup.md), before the `open-questions-register` skill, or any time you want to know how much of the export is still open.

## Synopsis

```text
pmlc open-questions ws [--json] [--items]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--json` | none | off | Print `open_questions.json` on stdout instead of the summary |
| `--items` | none | off | Print up to 30 `question` items as JSON, ready to paste into a pack |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E open-questions $WS
```

```text
- empty follow-up columns: 4 (Evidence to Collect, Key Questions, Suggested Interviews, Causal Hypothesis)
- blank Incident Summary fields: 21 of 30
- findings whose justification says something is absent: 240 of 436
- findings whose justification is hedged: 193 of 436
- gaps recorded by packs: 0
```

Running it again gives byte-identical files. [status](status.md) reports `open_questions.json` as stale after a re-ingest.

## Common problems

- **"This workspace was ingested before blank summary fields were recorded".** The workspace was built by an older engine. Re-run [ingest](ingest.md) (or [setup](setup.md)) to count the blank fields.
- **The blank-field count is 0 of 0 on a thin export.** The export has no Incident Summary fields at all.
- **A pack's `open-questions-follow-up.csv` is not written.** [pack](pack.md) never overwrites the file for an `open-questions-register` pack, because the organisation fills it in; it also writes nothing when no question item cites a finding. Move the old one aside and render again.

## Related

- [profile](profile.md) flags the blank summary fields too.
- [facts](facts.md) gives the headline numbers.
- [pack](pack.md) writes `open-questions-follow-up.csv` for the `open-questions-register` pack.
