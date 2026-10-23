# missed-opportunities

## What it does

Finds the chances to learn that the organisation had before the incident, and writes them to `<ws>/missed_opportunities.json`:

- `prior_recommendation`: the findings whose AI Justification cites an earlier recommendation (the word "recommend" at a word start, any case);
- `failure_to_correct`: the Failure-to-Correct findings (Nanocode prefix `SVF`);
- `dated`: the dated candidates from [timeline](timeline.md) before the incident date that cite one of those findings, each with its date, snippet and findings;
- `drift`: the findings whose justification uses drift wording ("normalised", "had become", "workaround" and so on), from the `drift` list in `references/open-questions.json`, matched as whole words in any case;
- `notes`: what was missing, for example no timeline candidates yet.

One engine serves two skills: `precursor-timeline` places the dated ones on its timeline as events that were knowable then, and `failure-to-learn-review` asks which step of the learning cycle broke. Re-running it gives the same file, byte for byte.

## When to use it

After [timeline](timeline.md), when a pack asks what was known before the event and why it did not lead to change.

## Synopsis

```text
pmlc missed-opportunities ws [--json] [--timeline-item]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--json` | none | off | Print `missed_opportunities.json` on the screen instead of the summary table |
| `--timeline-item` | none | off | Print the dated missed opportunities as a ready timeline item: one event per dated candidate, cut to whole words, with `knowable_then: true` |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E timeline $WS --before incident
python3 $E missed-opportunities $WS
python3 $E missed-opportunities $WS --timeline-item
```

On Hazira this finds 107 findings that cite an earlier recommendation and 40 Failure-to-Correct findings.

## Common problems

- **"No timeline_candidates.json: run `timeline <ws> --before incident` first".** The `dated` list stays empty until [timeline](timeline.md) has run; the other lists are filled.
- **The drift list is empty, with a note about the drift lexicon.** `references/open-questions.json` has no `drift` list in this copy of the coach.
- **The timeline item is empty.** No dated candidate before the incident cites these findings; the command says so and still exits 0.

## Related

- [timeline](timeline.md) finds the dated candidates.
- [timeline-item](timeline-item.md) prints the top dated candidates, or the incident-day sequence.
- [status](status.md) shows `missed_opportunities.json` as stale after a re-ingest.
