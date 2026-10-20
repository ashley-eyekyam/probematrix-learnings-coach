# report-comparison

A fair comparison between the ProbeMatrix investigation and another report on the same event: an official enquiry, a regulator's report, a company root-cause analysis. It maps both ways, compares depth by HFACS level, ownership, actionability and control strength, and says where the other report is stronger.

## What it is for

- "What does each analysis cover, and what does the second look add?"
- A side-by-side comparison for a management or client discussion.
- Checking how many of an enquiry's recommendations the learnings already reach.

## How to start it

- "Compare this investigation with the official enquiry report (attached)."
- "Which of our own action plan's actions cover the learnings, and which learnings have no action?"
- "Prepare a regulator-safe copy of the comparison for the authority that wrote the report."

## What it needs

- The workspace, ingested and classified.
- The other report as a PDF, Word or text file, or the organisation's own action plan. The agent extracts the text with `pdftotext -layout`; a scanned PDF needs OCR or a hand transcription, which the comparison says on page 1.
- A Learnings Register, ideally. Without one the skill builds a compact one first, so both sides are compared as learnings, not as finding counts.
- `comparator.json` (the other report's numbered items and its statutory status) and `comparison-map.json` (which learning matches which item), both written by the agent in the workspace before `compare` runs.

## Engine commands and flags

```bash
pmlc select <ws> --text "recommendation|remedial" --brief   # sighted or blind?
pmlc select <ws> --preset report-comparison                # the same call, as the skill's preset
pmlc select <ws> --text "<quoted phrase>" --in-evidence --brief
pmlc compare <ws> --register <run>/outputs/learnings-register.json          # check the inputs, read the tables
pmlc compare <ws> --register <run>/outputs/learnings-register.json --json   # the same as ready pack items
pmlc check-language <ws> <run>/outputs/report-comparison.json --names <comparator names file>
pmlc check-pack <ws> <run>/outputs/report-comparison.json --strict
pmlc pack <ws> <run>/outputs/report-comparison.json
pmlc compare <ws> --client-safe <run>/outputs/report-comparison-regulator-safe.json --main <run>/outputs/report-comparison.json
pmlc check-pack <ws> <run>/outputs/report-comparison-regulator-safe.json --strict --share external
pmlc pack <ws> <run>/outputs/report-comparison-regulator-safe.json --embed summary
```

- [select](../commands/select.md) with `--text` (a regular expression over the finding text) and `--brief` finds findings that quote the other report's recommendation sections. If any do, the comparison is **sighted**, and the first page says so. `--in-evidence` also searches the findings' linked evidence for a quoted phrase.
- [compare](../commands/compare.md) reads `comparator.json` and `comparison-map.json` from the workspace (`--comparator` and `--mapping` name other files), checks them, and prints the basis sentence with the comparator's statutory status, the item counts, coverage both ways, the control-tier profile and the group × owner cross-tab. `--register` adds the learnings with no match; `--json` prints the same as ready pack items. `--client-safe` with `--main` checks that a variant copy has the main pack's sections.
- [check-language](../commands/check-language.md) with `--names`, or [scan-names](../commands/scan-names.md), confirms that no personal name from the other report has crept into the tables.
- [check-pack](../commands/check-pack.md) with `--strict` and [pack](../commands/pack.md) check and render the pack; for the regulator-safe copy, `--share external` lints it for an outside reader and `--embed summary` leaves out evidence descriptions and quotes.

## What you get

`report-comparison.html` and `.md`:

- the basis (the comparator's title, issuer and statutory status; sighted or blind), the bottom line, two-way coverage tables (yes, partial or none, with a reason for "none"), depth and ownership, the control-tier profile, a side-by-side of three to five topics, where the other report is stronger, and the limits of the comparison.
- In **own-action-plan mode** (`source.kind` is `own-action-plan`), the same tables read "against the organisation's action plan": each learning is matched to the actions (`ACT-nn`) and their control tier, and learnings with no matching action are candidates for the organisation's adoption review (`templates adoption`).
- Two neutral copies with exactly the same sections, written only when asked:
  - `report-comparison-client-safe.json`, for the organisation that wrote the other report: neutral wording, no product claims;
  - `report-comparison-regulator-safe.json`, for a regulator or other authority: "additional learning" wording (never "missed"), no product claims, the comparator's statutory status in the basis, a reminder that it needs legal review, rendered with `--embed summary`. It leaves the organisation only after legal review and an approved sign-off (see [Review and sharing](../Review-and-sharing.md)).

The other report's IDs (`OBS-nn`, `RC-nn`, `REC-nn`, `ACT-nn`) are plain text in tables; an item can list them in `comparator_refs`, which `check-pack` checks against `comparator.json`.

## Worked example (Hazira)

`select --text "recommendation|remedial" --brief` returned 106 findings. The sample's README records that the enquiry committee's remedial measures (report pages 33 to 36) were in the evidence pack, so this comparison is **sighted**: read any match with the committee's recommendations as coverage, not as independent discovery. The official report is committed with the sample as [the PNGRB enquiry report](https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/samples/2020-09-24-hazira-gas-release-fire/2020-09-24-hazira-gas-release-fire_official-report.pdf).

## Related skills

- [learnings-register](learnings-register.md): the ProbeMatrix side of the comparison.
- [investigator-coach](investigator-coach.md): what to ask next where the two reports differ.
- Recipe: [Compare with the official report](../Workflows-and-recipes.md#compare-with-the-official-report).
