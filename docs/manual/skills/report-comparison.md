# report-comparison

A fair comparison between the ProbeMatrix investigation and another report on the same event: an official enquiry, a regulator's report, a company root-cause analysis. It maps both ways, compares depth by HFACS level, ownership, actionability and control strength, and says where the other report is stronger.

## What it is for

- "What does each analysis cover, and what does the second look add?"
- A side-by-side comparison for a management or client discussion.
- Checking how many of an enquiry's recommendations the learnings already reach.

## How to start it

- "Compare this investigation with the official enquiry report (attached)."
- "Which of the committee's recommendations do our learnings cover, and what do we add?"
- "Prepare a neutral comparison we can share with the organisation that wrote the other report."

## What it needs

- The workspace, ingested and classified.
- The other report as a PDF, Word or text file. The agent extracts its text with the host's tools.
- A Learnings Register, ideally. Without one the skill builds a compact one first, so both sides are compared as learnings, not as finding counts.

## Engine commands and flags

```bash
pmlc select <ws> --text "recommendation|remedial" --brief   # sighted or blind?
pmlc select <ws> --preset report-comparison                # the same call, as the skill's preset
pmlc check-language <ws> <run>/outputs/report-comparison.json --names <comparator names file>
pmlc scan-names <names file> <run>/outputs
pmlc check-pack <ws> <run>/outputs/report-comparison.json
pmlc pack <ws> <run>/outputs/report-comparison.json
```

- [select](../commands/select.md) with `--text` (a regular expression over the finding text) and `--brief` finds findings that quote the other report's recommendation sections. If any do, the comparison is **sighted**, and the first page says so.
- [check-language](../commands/check-language.md) with `--names`, or [scan-names](../commands/scan-names.md), confirms that no personal name from the other report has crept into the tables.
- [check-pack](../commands/check-pack.md) and [pack](../commands/pack.md) render the pack.

## What you get

`report-comparison.html` and `.md`:

- the basis (sighted or blind), the bottom line, two-way coverage tables (yes, partial or none, with a reason for "none"), depth and ownership, the control-tier profile, a side-by-side of three to five topics, where the other report is stronger, and the limits of the comparison;
- if you will share it with the other report's authors, `report-comparison-client-safe.json` and its page: the same content in neutral wording, with no product claims.

The other report's IDs (`OBS-nn`, `RC-nn`, `REC-nn`) are plain text, not citations.

## Worked example (Hazira)

`select --text "recommendation|remedial" --brief` returned 106 findings. The sample's README records that the enquiry committee's remedial measures (report pages 33 to 36) were in the evidence pack, so this comparison is **sighted**: read any match with the committee's recommendations as coverage, not as independent discovery. The official report is committed with the sample as [the PNGRB enquiry report](https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/samples/2020-09-24-hazira-gas-release-fire/2020-09-24-hazira-gas-release-fire_official-report.pdf).

## Related skills

- [learnings-register](learnings-register.md): the ProbeMatrix side of the comparison.
- [investigator-coach](investigator-coach.md): what to ask next where the two reports differ.
- Recipe: [Compare with the official report](../Workflows-and-recipes.md#compare-with-the-official-report).
