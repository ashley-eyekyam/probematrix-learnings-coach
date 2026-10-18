---
name: report-comparison
description: Compare a ProbeMatrix investigation with an official, regulatory, corporate or conventional investigation report on the same event - two-way coverage of learnings and recommendations, depth by HFACS level, ownership, actionability and control strength - fairly and without blame. Use when someone has an enquiry committee report, regulator report, company RCA or root-cause report and wants to know what each analysis covers, what the second look adds, or wants a side-by-side comparison for a management or client discussion.
---

# Report Comparison

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py` (this skill needs the `learnings-coach` skill installed alongside it). **Read `learnings-coach/references/comparison-method.md` before starting**, and `learning-principles.md`.

## Inputs

- the ProbeMatrix workspace (ingested and classified)
- the other report (PDF, Word or text). Extract its text with whatever tools the host provides.

## Steps

1. **Establish sighted or blind.** Search the findings for quotations of the other report's recommendation or lessons sections, e.g. `PMLC select <ws> --text "recommendation|remedial" --brief`, and look for page references that fall inside those sections. Report how many findings cite them. If any do, the comparison is sighted; say so on page 1.
2. **Inventory the other report**: observations (`OBS-nn`), root causes (`RC-nn`), recommendations (`REC-nn`), each with its section or discipline group. Count them.
3. **Learnings on the ProbeMatrix side**: use an existing Learnings Register if present; otherwise build a compact one (see `learnings-register`, steps 1–2) so both sides are compared at the level of learnings, not finding instances.
4. **Map both ways** (yes / partial / none) with reason classes for "none".
5. **Compare dimensions**: level reached, ownership (entity and tier named?), actionability, control tier of recommendations, evidence basis, interfaces.
6. **Cross-tabulate** the other report's discipline groups against Learning Clusters to show where each concentrates.
7. **Say where the other report is stronger.** Specific engineering recommendations, site findings, primary evidence: credit them.

## Output

Write the pack `<run>/outputs/report-comparison.json` (schema: `learnings-coach/references/pack-schema.md`), then:

```bash
PMLC check-pack <ws> <run>/outputs/report-comparison.json   # fix every problem it lists
PMLC pack <ws> <run>/outputs/report-comparison.json         # -> report-comparison.html (primary) and .md
```

The pack supplies the status line and the footer. Sections and the kinds that fill them:
1. **Basis:** a `para` with the sighted or blind statement and the "same evidence, different analytical architecture" framing.
2. **Bottom line:** five entries.
3. **Coverage:** one `table` per direction (Other report, ProbeMatrix learning, Match = yes, partial or none, Reason if none; `row_cites`), plus a counts `table`.
4. **Depth and ownership:** a `table` (Dimension, Other report, ProbeMatrix).
5. **Control-tier profile:** a `table`.
6. **Side by side:** a `table` (Topic, Other report says, ProbeMatrix says; `row_cites`) with three to five rows.
7. **Where the other report is stronger:** `para`.
8. **Limits:** `para`.

Use the cross-tab of discipline groups × Learning Clusters as a further `table`. The other report's IDs (`OBS-nn`, `RC-nn`, `REC-nn`) are plain text, not citations. Put data-quality corrections in `data_quality`, findings left out on purpose in `exclusions`, and same-condition findings in `supporting_cites`.

If the user will share the comparison with the organisation that wrote the other report, also write `<run>/outputs/report-comparison-client-safe.json` with `"pack": "report-comparison-client-safe"`. Keep the same content, use neutral wording and make no product claims.

```json
{"kind": "table", "columns": ["Other report", "ProbeMatrix learning", "Match", "Reason if none"],
 "rows": [["REC-01 …", "…", "partial", ""]], "row_cites": [["FND-…"]]}
```
