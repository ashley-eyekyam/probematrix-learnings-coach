---
name: learnings-register
description: Build a formal Learnings Register (lessons-learned register) from a ProbeMatrix investigation export - one row per learning with evidence, HFACS level, barrier, organisational system, audiences, priority and recommendations rated on the hierarchy of controls with leading indicators - and write it to Markdown and a formatted Excel workbook. Use when someone asks for a lessons-learned register, a learnings log, an Excel of learnings, a register to share with management or a regulator, or "turn these findings into lessons and recommendations".
---

# Learnings Register

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py` (this skill needs the `learnings-coach` skill installed alongside it). Needs `clusters.json` (see `learning-clusters`). Read `learnings-coach/references/learning-principles.md` and `learnings-coach/references/register-schema.md`.

## Method

1. **Find the learnings, not the findings.** Start from the highest-rated findings: `PMLC select <ws> --top-rated --brief`. Group findings that describe the same condition. A typical investigation of a few hundred findings yields 15–40 learnings. Then sweep lower ratings for conditions not yet covered, especially at L3–L4.
2. **One learning per row.** Write the lesson as a generalisable sentence that would make sense to another site ("If X, then Y, because Z"), not a restatement of the event.
3. **Classify** each learning against register sections B–H. Owner entity and tiers come from `clusters.json` for its findings.
4. **Recommend.** One to three recommendations per learning, each with HoC tier and a leading indicator. At least one recommendation per priority-1 learning should be above the administrative tier, or say why none is possible.
5. **Tier messages.** For each learning, write `tier_messages`: one short, concrete message per tier that must act (T1 frontline … T5 corporate/board), omitting tiers with nothing to do. This is what turns the register into a learning plan for the whole organisation.
6. **Use the controlled values** in `register-schema.md` for `hfacs_level`, `hoc_tier`, `priority` and `comparison`, so the Summary sheet and dashboard count cleanly. Put nuance in the free-text fields.
7. **Prioritise.** Priority 1 = credible major consequence and likely to recur or transfer; 3 = local and minor.
8. **Comparison.** Leave `comparison` as `not compared` unless a comparator report is supplied (then use `report-comparison`).

## Output

All files go to `<run>/outputs/` (see the folder rule in `learnings-coach/SKILL.md`; `PMLC run-path <ws>` prints it).

- `<run>/outputs/learnings-register.json` in the schema shape.
- `PMLC check-register <ws> <run>/outputs/learnings-register.json`: validates IDs, evidence links, controlled values, tier messages and leading indicators, flags findings with reviewer downgrade votes, and lists high-rated findings no learning covers. Fix everything it reports, then:
- `PMLC register-xlsx <run>/outputs/learnings-register.json` writes `learnings-register.xlsx` beside it (sheets: Learnings Register, Recommendations, Learning Plan, Summary, About). Do not rebuild these sheets by hand; if something is missing, add it to the JSON and re-run.
- `PMLC dashboard <ws> --register <run>/outputs/learnings-register.json [--date <corrected date>] [--title "<plain title>"]` writes `<run>/outputs/organisation-learning-map.html` with two tabs:
  - **Overview:** the organisation map plus the learning × tier matrix, whose rows link to tab 2.
  - **Detailed register:** every field of every learning, its recommendations, tier messages, and the full text of each cited finding and evidence item. It has stakeholder lenses (T1–T5, Investigator, Auditor), filters, search, expand/collapse, print, and a panel of findings no learning covers. Unknown register keys are shown, never dropped.
  - It is required for this skill.
  - Do not hand-edit the HTML: change the JSON and re-run.
- `<run>/outputs/learnings-register.md`: summary tables (counts by entity, level, organisational system, HoC tier), the priority-1 learnings in full, then the rest in a compact table.

## Checks before handing over

- Every row has finding IDs and at least one evidence ID.
- No names, no blame wording, no owners or due dates (unless the user asked).
- The share of recommendations at administrative or training tier is reported honestly.
