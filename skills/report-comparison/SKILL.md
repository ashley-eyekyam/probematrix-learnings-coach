---
name: report-comparison
description: Compares a ProbeMatrix investigation export with an official, regulatory, corporate or conventional investigation report on the same event, or with the organisation's own action plan - two-way coverage of learnings and recommendations, depth by HFACS level, ownership, actionability and control strength - fairly and without blame, with neutral client-safe and regulator-safe copies. Use when someone with a ProbeMatrix export has an enquiry committee report, regulator report, company RCA or CAPA plan and wants to know what each covers, what the second look adds, or wants a side-by-side comparison for a management or client discussion. Not for drafting new learnings (use `learnings-register`).
---

# Report Comparison

Engine: `PMLC` as in `learnings-coach/references/skill-common.md` §1; this skill needs the `learnings-coach` skill installed alongside it.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions; run `PMLC setup`
when only an .xlsx was given). Needs: `workspace`. Optional: the register, the comparator. **Read
`learnings-coach/references/comparison-method.md` first** (framing, reason classes, the name-bleed rule, file
shapes), and `learnings-coach/references/learning-principles.md`.

Ask which report is compared, and its kind: an official or regulator report (`official-report`), a company
report (`company-report`), or the organisation's **own action plan** (`own-action-plan`, L1-16 mode).

## Gather

1. **Extract the other report:** `pdftotext -layout report.pdf report.txt`. A scanned PDF gives an empty or
   garbled file: run OCR if available, otherwise transcribe the items by hand and say so on page 1.
2. **Sighted or blind.** Find findings that quote the other report's recommendation or lessons sections:

   ```bash
   PMLC select <ws> --text "recommendation|remedial" --brief
   PMLC select <ws> --text "<quoted phrase>" --in-evidence --brief   # findings whose evidence quotes it
   ```

   Count the findings that quote them and give the count on page 1. If any do, the comparison is **sighted**:
   report coverage, not independent discovery.
3. **Write `<ws>/comparator.json` first** (shape in `comparison-method.md` §7): `source` with `title`,
   `issuer_role`, `statutory_status` (as the report states it, e.g. "statutory enquiry under …" or
   "non-statutory") and `kind`, then one item per observation (`OBS-nn`), root cause (`RC-nn`), recommendation
   (`REC-nn`) or action (`ACT-nn`), with its section, group and `hoc_tier`. Never guess an item. Replace personal
   names with roles and company names with functions as you transcribe (the name-bleed rule).
4. **The ProbeMatrix side is learnings, not findings:** use the register if present; otherwise build a compact
   one first (`learnings-register`, its Gather and Write steps).
5. **Map both ways** in `<ws>/comparison-map.json` (`[{"lr_id", "ref", "match": "yes|partial|none"}]`), then:

   ```bash
   PMLC compare <ws> --register <run>/outputs/learnings-register.json          # check the inputs; read the tables
   PMLC compare <ws> --register <run>/outputs/learnings-register.json --json   # the same as ready pack items
   ```

   Paste the `--json` items unchanged (the basis sentence with the statutory status, the item counts, both
   directions, the control-tier profile and the group × owner cross-tab). Write the reason class for each
   "none" from `comparison-method.md` §4.
6. **Own-action-plan mode:** each learning is mapped to the organisation's actions (`ACT-nn`) with the action's
   `hoc_tier`. A learning with no matching action, or only a weaker one, is a candidate for the organisation's
   adoption review: offer `PMLC templates <ws> adoption` (the organisation fills it in; never you).

## Write

Write `<run>/outputs/report-comparison.json` in the shape in `learnings-coach/references/pack-schema.md`.

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | What each analysis covers, what the second look adds, and where the other report is stronger | `bottom_line` | up to 5 |
| 1 | `basis` | Basis of the comparison | The `compare` basis sentence (title, issuer role, statutory status); sighted or blind; "same evidence, different analytical architecture"; a conflict-of-interest line when the commissioning organisation is a compared party | `para` | up to 3 |
| 2 | `coverage` | Coverage both ways | The `compare` count tables and cross-tab, plus one mapping table per direction (Other report, ProbeMatrix learning, Match, Reason if none; `row_cites`) | `table` | up to 6 |
| 3 | `depth` | Depth and ownership | Dimension, Other report, ProbeMatrix: levels reached, ownership, actionability, evidence basis, interfaces | `table` | 1 |
| 4 | `control-tiers` | Control-tier profile | The `compare` control-tier table, both sides | `table` | 1 |
| 5 | `side-by-side` | Side by side | Topic, Other report says, ProbeMatrix says; three to five rows; `row_cites` | `table` | 1 |
| 6 | `stronger` | Where the other report is stronger | Specific engineering recommendations, site findings, primary evidence: credit them | `para` | up to 3 |
| 7 | `limits` | Limits of this comparison | What the desk analysis could not see; transcription or OCR caveats | `para` | up to 3 |

The other report's ids are plain text in tables; on an item, list them in `comparator_refs` (checked against
`comparator.json`). Carry `learning: "LR-nn"` where a row or item expresses one register learning.

**Variants: the same sections, only the content changes.** Each copy has exactly the sections above, in order
(its profile's rule `same-sections-as:report-comparison`):
- **Client-safe**, for the organisation that wrote the other report: `<run>/outputs/report-comparison-client-safe.json`,
  `"pack": "report-comparison-client-safe"`. Neutral wording, no product claims, roles for names, functions for
  companies, and no reason class that reads as a verdict.
- **Regulator-safe** (L7-12), for a regulator or other authority: `<run>/outputs/report-comparison-regulator-safe.json`,
  `"pack": "report-comparison-regulator-safe"`. Write "additional learning", never "missed" or "gap in the
  report"; make no product claims; put the comparator's `statutory_status` in the `basis` statement; add a
  `limits` line that the copy is not a statutory document and needs legal review before it leaves the
  organisation. It is rendered with `--embed summary` and shared only under `skill-common.md` §7.

## If the evidence is thin

Follow `skill-common.md` §6, and:
- **No numbered recommendations in the other report:** number its stated actions or conclusions as `OBS-nn`
  and say so in `basis`.
- **No register and too few findings for one:** compare at finding level, and say so in `basis` and `limits`.
- **A scanned report with no OCR:** transcribe only what you can read and list the pages not covered in `limits`.

## Not covered here

- Drafting the learnings themselves: `learnings-register`.
- What to ask next where the two reports differ: `investigator-coach`.
- Statutory notification or reporting duties: the organisation's own process (`learnings-coach/references/jurisdictions.md` lists regimes).

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/report-comparison.json --strict   # fix every problem it lists
PMLC pack <ws> <run>/outputs/report-comparison.json                  # -> report-comparison.html and .md
PMLC compare <ws> --client-safe <run>/outputs/report-comparison-regulator-safe.json --main <run>/outputs/report-comparison.json
PMLC check-pack <ws> <run>/outputs/report-comparison-regulator-safe.json --strict --share external
PMLC pack <ws> <run>/outputs/report-comparison-regulator-safe.json --embed summary
```

Run the variant lines only for the copies the user asked for (the same lines serve the client-safe copy). Check
quoted comparator text against the comparator's names (one per line in a file), with
`PMLC check-language <ws> <run>/outputs/report-comparison.json --names <names file>` or
`PMLC scan-names <names file> <run>/outputs`. Prompt for legal review
before any copy leaves the organisation; never run `sign-off` yourself.
