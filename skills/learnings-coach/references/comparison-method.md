# Comparing a ProbeMatrix analysis with another investigation report

Use this when an organisation has an official or conventional report on the same event and wants to see what each analysis covers.

## 1. Frame it fairly, on page 1

- **Same evidence, different analytical architecture.** If the ProbeMatrix analysis was built from the other report's evidence, say so: this compares analysis depth, not investigation quality. The original team may have had site access, interviews and physical evidence that the desk analysis did not.
- **Sighted or blind.** If the ProbeMatrix evidence pack included the other report's own recommendations or lessons, the comparison is **sighted**: report coverage, not independent discovery. Check by searching findings for quotations of the other report's recommendation sections. If they were withheld, it is **blind**.
- **Method, not verdict.** No blame. Never use the word "deficiency". The original team worked under its own terms of reference.

- **Names do not bleed in.** Official reports often name people and companies. Replace every personal name in quoted or paraphrased comparator text with the role, and company names with their function ("the contractor"), before it reaches a table or an example. Run `scan-names` or `check-language --names` with the comparator's names as the check. Put a conflict-of-interest line on page 1 if the compared parties include the commissioning organisation.

## 2. Build the comparator inventory

Number every item in the other report: observations (`OBS-nn`), root causes (`RC-nn`), recommendations (`REC-nn`). Keep its own grouping (usually by discipline) as a column.

## 3. Map both ways

For each **learning** (not finding): does the other report have a counterpart?

| Value | Meaning |
|---|---|
| yes | the same learning is stated, at the same level |
| partial | the topic is present but at a lower level, narrower scope, or without the "why" |
| none | absent |

For each **comparator item**: which learnings or findings cover it? An item with no ProbeMatrix counterpart is reported as plainly as the reverse.

## 4. Reason classes for "none" (neutral wording)

- analysis stopped at the individual level
- organisational layer not examined
- evidence present but not interpreted
- pattern visible only across functions or incidents
- outside the original terms of reference

## 5. Dimensions to compare side by side

1. **Depth**: which levels each reaches (L1–L4).
2. **Ownership**: whether the learning names who must learn (entity and tier).
3. **Actionability**: whether it says what should change.
4. **Control strength**: hierarchy-of-controls tier of the recommendations.
5. **Evidence basis**: how directly each item is tied to evidence.
6. **Interfaces**: whether learnings between functions are visible.

## 6. Report

A coverage matrix, counts by value and reason class, and short side-by-side examples. Where the other report is stronger (for example, specific engineering recommendations), say so explicitly.

## 7. File shapes and the engine

The inventory in section 2 is kept in the workspace as two files that `pmlc compare` reads and checks.

`comparator.json`:

```json
{"source": {"title": "...", "issuer_role": "...", "statutory_status": "...",
            "kind": "official-report|own-action-plan|company-report"},
 "items": [{"id": "REC-01", "type": "observation|root_cause|recommendation|action",
            "section": "...", "text": "...", "group": "...", "hoc_tier": "..."}]}
```

Ids are `OBS-nn`, `RC-nn`, `REC-nn` and `ACT-nn` (observation, root cause, recommendation, action), unique, with at least two digits.

`comparison-map.json`: `[{"lr_id": "LR-01", "ref": "REC-03", "match": "yes|partial|none"}]`. An item or learning with no row counts as `none`.

- **Extracting the text.** Use `pdftotext -layout report.pdf report.txt` as the default extractor. If the PDF is scanned (the text file is empty or garbled), run OCR if available; otherwise transcribe the items by hand and say so on page 1. Never guess an item.
- **Action-plan mode.** Set `source.kind` to `own-action-plan` to compare the learnings with the organisation's own action plan (items are mostly `ACT-nn`); the output then reads "against the organisation's action plan".
- **Client-safe and regulator-safe variants** (`report-comparison-client-safe`, `report-comparison-regulator-safe`). Keep the same section ids as the main pack and change only the content: roles for names, functions for companies, no `none` reason classes that read as a verdict. The regulator-safe copy also says "additional learning" (never "missed"), makes no product claims, states the comparator's `statutory_status` in its basis, and is rendered with `--embed summary` after legal review. `pmlc compare --client-safe VARIANT --main PACK` checks the section ids match, for either variant.
- **In a pack.** An item may carry `comparator_refs` (a list of item ids); `check-pack` checks them against `comparator.json`. `pmlc select --text "<quoted phrase>" --in-evidence` finds the findings whose linked evidence quotes it.
- Run `pmlc compare <ws> --register <register.json> --json` for the ready tables.
