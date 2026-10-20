# dashboard

## What it does

Writes the **organisation learning map**: one self-contained HTML page (it works offline and can be emailed) that shows the whole investigation by part of the organisation, tier and HFACS level, the interfaces between teams and the causal links. With a Learnings Register it adds the learnings, a plan by tier and the strength of the proposed controls, with a detailed register tab.

The page is built from the workspace; it adds nothing that is not in the export or the register. It shows a **DRAFT** ribbon and a handling line until the register it shows is approved, and always while the investigation is unfinished.

`--embed` sets how much of the investigation's records the detailed register tab embeds, and `--share external` or `--share public` writes a masked copy for outside the organisation. A dashboard can be shared outside only with a register that is signed off for it: without `--register` there is nothing to approve, so the copy is refused.

## When to use it

For an overview meeting, a safety committee, or anyone who asks "where in the organisation does this investigation point?". Run [classify](classify.md) first. Add `--register` once a register has passed [check-register](check-register.md).

## Synopsis

```text
pmlc dashboard ws [--out OUT] [--register REGISTER] [--title TITLE] [--date DATE] [--location LOCATION]
               [--embed {cited,summary,full}] [--share {internal,external,public}] [--names NAMES] [--orgs ORGS]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--out` | file | `<run>/outputs/organisation-learning-map.html` (`organisation-learning-map.external.html` or `.public.html` when shared) | Where to write the page. A shared copy written with `--out` goes exactly where you say, so give it a name that cannot overwrite the internal page |
| `--register` | file | none | A Learnings Register JSON: adds the learnings, tier plan and control-strength sections |
| `--title` | text | the export's incident title | The incident title in the page header |
| `--date` | `YYYY-MM-DD` | the export's date | The incident date in the header. Use it when the summary sheet is wrong |
| `--location` | text | the export's location | The location in the header |
| `--embed` | `cited`, `summary` or `full` | `cited` (`summary` when sharing outside) | How much the register tab embeds. `cited`: full records for the findings and evidence the register cites; uncovered findings as ID, label and rating only. `summary`: as `cited`, without evidence descriptions, specific references (quotes), suggested interviews, key questions or reviewers' vote reasons. `full`: every relevant record in full |
| `--share` | `internal`, `external` or `public` | `internal` | Who the copy is for. `external` and `public` need `--register` with a register signed off as approved, a classification at that level or wider and `legal_review` cleared, and `--embed summary` (the default when sharing). Names, organisations, equipment tags, singleton roles, clock times and full dates are masked, and the register's source file name becomes "a ProbeMatrix investigation export" |
| `--names` | file | `$PMLC_NAMES` | A names file, one name per line. A shared copy masks these names; in every mode the page is refused if one of them still appears in it |
| `--orgs` | file | `$PMLC_ORGS` | An organisation names file, one per line. A shared copy masks these names |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

The learning map with the sample register, as published in the repository's sample folder:

```bash
python3 $E dashboard $WS --register $OUT/learnings-register.json
```

```text
note: embedded evidence includes witness statements; consider --embed summary
Dashboard written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/organisation-learning-map.html
```

The note is a reminder, not an error: the register cites witness statements, and the default `cited` mode carries their text. The same map without quotes or evidence descriptions is about 1.3 MB instead of 1.6 MB, and prints no note:

```bash
python3 $E dashboard $WS --register $OUT/learnings-register.json --embed summary --out $OUT/map-summary.html
```

```text
Dashboard written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/map-summary.html
```

The Hazira map cannot be shared outside, because the investigation is unfinished. Every unmet condition is listed and nothing is written:

```bash
python3 $E dashboard $WS --register $OUT/learnings-register.json --share external
```

```text
cannot share externally: review is draft (the investigation status is in progress, no finding is marked as edited by a person); classification is "internal" (needs "external" or "public"); legal_review is not "cleared"
```

On a synthetic, completed investigation where a person edited a finding (`SW` and `SO` are its workspace and outputs folders), the register is first approved for external readers, then the map is shared:

```bash
python3 $E sign-off $SW $SO/learnings-register.json --role "HSE manager" --status approved --classification external --legal-review cleared --date 2026-10-19
python3 $E dashboard $SW --register $SO/learnings-register.json --share external --orgs $SO/orgs.txt
```

```text
Signed off synth/pmlc-runs/2024-03-20-plant-pump-fire/outputs/learnings-register.json: approved by HSE manager on 2026-10-19
Dashboard written to synth/pmlc-runs/2024-03-20-plant-pump-fire/outputs/organisation-learning-map.external.html
Shared external: identifying details are masked
```

Without `--register` the same command is refused, because there is no signed-off register to share:

```text
cannot share externally: review is draft; classification is "internal" (needs "external" or "public"); legal_review is not "cleared"
```

A second copy with a clearer title than the export's "Hazira 2020":

```bash
python3 $E dashboard $WS --title "Hazira gas terminal release and fire" --out $OUT/map-retitled.html
```

```text
Dashboard written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/map-retitled.html
```

**Learnings by pack, reach, response and closure.**

The overview ends with a **Learnings × packs** table (how often each pack item names a learning, from the item's `learning` field in `outputs/*.json`) and a **Packs and reach** list. Reach comes from the rows of `distribution.csv` that have a `date`: deliveries, attendees, and deliveries that included contractors. With `--register`, the detailed register tab shows each learning's **response** from `adoption.csv` (accepted, modified, rejected) and its closure fields (`capa_ref`, `closure_evidence`, `effectiveness_result`) under "Response and closure". The toolbar has a **Needs legal / compliance review** chip that keeps the learnings with a `regulatory_touchpoint`.

An organisation file with an invalid value (for example a response other than accepted, modified or rejected) does not stop the dashboard: the page shows a warning line naming the file and row, the same line goes to stderr, and that file's data is left out.

## Common problems

- **"Needs clusters.json".** Run [classify](classify.md) first.
- **The header shows the wrong date or title.** The export's summary sheet is wrong. Override it with `--date`, `--title` or `--location`; better, correct it in ProbeMatrix and export again.
- **The register sections are missing.** Pass `--register`. Check the register first with [check-register](check-register.md).
- **"cannot share externally: …".** Each condition after the colon is unmet. Pass `--register` with a register signed off as approved for that audience (`sign-off --status approved --classification external --legal-review cleared`), and leave `--embed` out.
- **"refused: a listed name appears in the output".** A name from `--names` is still in the page (often in the export's own text). Redact it at ingest with `ingest --redact`, then re-run the analysis.
- **The page says draft.** Its status follows the investigation and the register's sign-off, as for a pack. See [Review and sharing](../Review-and-sharing.md).

## Related

- [check-register](check-register.md) and [register-xlsx](register-xlsx.md) for the register.
- [interfaces](interfaces.md) and [causal](causal.md) give the same data as tables.
- [Skills](../Skills.md): the `organisation-learning-map` skill explains the map to its readers.
