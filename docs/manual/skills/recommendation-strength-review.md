# recommendation-strength-review

How strong the recommendations are, reviewed as a set and banded by the engine rather than judged. The review covers the Learnings Register's recommendations, and the 9M analysis's when there is one. It shows the strongest change for each learning on the hierarchy of controls, flags any deep cause that gets only a weak fix, counts the changes that question an assumption or norm (double loop), shows how the fixes spread across the nine Ms, and lists the recommendations that miss a SMART element. It ends with up to ten directions for stronger change. It never sets an owner, a due date or a decision.

## What it is for

- "How strong are these corrective actions?"
- "Which recommendations are only training or a procedure, and does any deep cause get nothing better?"
- A CAPA critique before the meeting that agrees the actions.
- Checking whether the fixes question the assumptions behind a cause, or only patch the condition.

## How to start it

- "Before we agree the actions, review how strong the register's recommendations are."
- "Is any organisational cause in this register fixed only by training or a reminder?"
- "We have done the 9M analysis: review its actions and the register's together, and show the spread by M."

## What it needs

- A workspace from [learnings-coach](learnings-coach.md) and the Learnings Register from [learnings-register](learnings-register.md), checked with [check-register](../commands/check-register.md).
- Optional: `outputs/nine-m-map.json`, which [nine-m-analysis](nine-m-analysis.md) writes. With it, the review covers the register and the 9M analysis together and shows the spread across the nine Ms. Without it, the review covers the register only, and the page says so.
- Never the CAPA Planner workbook. A pack, or any other file in the register's place, is refused with one sentence naming the file it expects.

## Engine commands and flags

```bash
pmlc rec-review <ws> <run>/outputs/learnings-register.json --nine-m                        # the summary
pmlc rec-review <ws> <run>/outputs/learnings-register.json --nine-m --table-item strength  # per learning
pmlc rec-review <ws> <run>/outputs/learnings-register.json --nine-m --table-item spread    # recommendations per M
pmlc rec-review <ws> <run>/outputs/learnings-register.json --nine-m --table-item smart     # SMART gaps
pmlc rec-review <ws> <run>/outputs/learnings-register.json --nine-m --json                 # causes, loops, recipients
pmlc check-pack <ws> <run>/outputs/recommendation-strength-review.json --strict
pmlc pack <ws> <run>/outputs/recommendation-strength-review.json
pmlc pack <ws> <run>/outputs/recommendation-strength-review.json --format docx     # a Word copy
pmlc pack-xlsx <ws> <run>/outputs/recommendation-strength-review.json --kind table   # the tables in Excel
```

- [rec-review](../commands/rec-review.md) bands each recommendation: `stronger` (elimination, substitution, engineering), `intermediate` (administrative), `weaker` (training, PPE, or an administrative change that is a procedure, policy, reminder, memo, warning, sign, poster, double-check or re-brief) or `unrated`. A learning whose findings reach HFACS level 3 or 4 with nothing `stronger` or `intermediate` is flagged `weak fix for a deep cause`. `--table-item` prints the `strength`, `spread` or `smart` table, with `row_cites`, ready to paste unchanged. Leave `--nine-m` off without a 9M map.
- [check-pack](../commands/check-pack.md) fails the pack on any `owner` or `by_when`, even without `--strict` (the `no-owner-due` rule). [pack](../commands/pack.md) renders it, and [pack-xlsx](../commands/pack-xlsx.md) with `--kind table` writes the tables to Excel.

## What you get

`recommendation-strength-review.html` and `recommendation-strength-review.md`, with these sections:

- **reviewed-set:** which set was reviewed, "the learnings register" or "the learnings register and the 9M analysis", with the number of recommendations in each. When the 9M answers came from a scripted replay, it says they were chosen for demonstration, not by the organisation;
- **strength:** for each learning, its HFACS levels, its strongest change, whether that matches the depth of the cause, and the flag, pasted from the engine;
- **spread:** recommendations under each of M1 to M9 (only with a 9M map);
- **loops:** the double-loop and single-loop counts, and the learnings the register marks double-loop whose changes question nothing;
- **directions:** up to ten `recommendation` items, each a direction of change for one learning with its tier, a leading indicator and its cites;
- **smart:** the recommendations missing "specific", "measurable" or "relevant" (left out when there are none). Time-bound is never checked: dates are the organisation's to set.

The Word copy suits the meeting that agrees the actions. The pack is a review of the recommendations, not of the people who wrote them.

## Worked example (Hazira)

`rec-review` on the Hazira register and the 9M map printed:

```text
rec-review (register+9M): stronger 24; intermediate 15; weaker 5; unrated 0
0 learning(s) flagged 'weak fix for a deep cause'
double-loop 0, single-loop 44; 0 recommendation(s) missing a SMART element
9M spread: M1 1, M2 1, M3 1, M4 1, M5 1, M6 1, M7 1, M8 1, M9 1
```

The worked pack, `samples/2020-09-24-hazira-gas-release-fire/outputs/recommendation-strength-review.json` in the repository, reviews the register and the 9M analysis, and says the 9M answers were chosen for demonstration. Each of the five weaker changes sits beside a stronger one in the same learning. Six learnings have nothing stronger than an intermediate change; two of them already say why. The register marks 12 learnings double-loop, but none of its 44 changes questions an assumption or norm. The seven directions suggest engineered changes for the thickness cycle (LR-18), the drawings used for isolation (LR-19) and the drill record (LR-24). They also question the norms behind the repeat seal repairs (LR-05), display-only gas detection (LR-10), painted wall loss (LR-17) and checklist assurance (LR-20). No SMART gap is found, so the `smart` section is left out.

## Related skills

- [nine-m-analysis](nine-m-analysis.md): designs the corrective and preventive actions by M with the user; this skill reviews them.
- [learnings-register](learnings-register.md): writes the learnings and the recommendations this skill reviews.
- [barrier-learnings](barrier-learnings.md): which barriers failed and how strong their fixes should be.
