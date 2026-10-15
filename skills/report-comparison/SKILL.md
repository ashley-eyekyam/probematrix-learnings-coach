---
name: report-comparison
description: Compare a ProbeMatrix investigation with an official, regulatory, corporate or conventional investigation report on the same event - two-way coverage of learnings and recommendations, depth by HFACS level, ownership, actionability and control strength - fairly and without blame. Use when someone has an enquiry committee report, regulator report, company RCA or root-cause report and wants to know what each analysis covers, what the second look adds, or wants a side-by-side comparison for a management or client discussion.
---

# Report Comparison

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py`. **Read `learnings-coach/references/comparison-method.md` before starting**, and `learning-principles.md`.

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

`<run>/outputs/report-comparison.md`:
1. Status line, sighted/blind statement, "same evidence, different analytical architecture" framing.
2. Bottom line (five bullets).
3. Coverage tables (both directions) and counts.
4. Depth and ownership comparison.
5. Recommendations: control-tier profile of each side.
6. Side-by-side examples (three to five).
7. Limits of this comparison.
8. Footer.

Offer a client-safe edition if the user will share it with the organisation that wrote the other report: same content, neutral wording, no product claims.
