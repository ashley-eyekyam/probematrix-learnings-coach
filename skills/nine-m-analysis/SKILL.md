---
name: nine-m-analysis
description: Works through the nine Ms (9M) of a ProbeMatrix investigation export with the user, one question at a time, to find which part of the work system each condition belongs to (people readiness, environment, method, mission, measurement, management and money, machine, material, maintenance), then writes one learning, barrier and direction of change per relevant M with no owners or dates, a blank actions sheet, and the 9M map the learnings register and the recommendation review read. Use when someone with a ProbeMatrix export asks for a 9M or "nine Ms" analysis, to "work through the 9Ms with me", for CAPA design by M, or which Ms the findings point to. Not for reviewing how strong the recommendations already written are (use `recommendation-strength-review`) or for which barriers failed (use `barrier-learnings`).
---

# 9M Analysis

Engine: `PMLC` as in `learnings-coach/references/skill-common.md` §1; this skill needs the `learnings-coach` skill installed alongside it.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions; run `PMLC setup`
when only an .xlsx was given). Needs: `workspace` and `nine-m-seed` (the first Gather line writes it). Optional: the
register; when it exists, tie each learning to its `LR-nn` (§2 "Start from the register"). Read
`learnings-coach/references/learning-principles.md` (§3: respect the level; §4: count honestly) and
`learnings-coach/references/nine-m.md`: the nine Ms, where they overlap, and why M1 is not the people M.

**A CAPA Planner workbook is the wrong file.** `nine-m-seed` refuses it; ask for the findings export instead.

## Gather

This skill is an interview. **Ask one question per turn**, through the host's question tool where there is one,
otherwise as a numbered list. Every question comes from the engine, and every answer goes back to it:

```bash
PMLC nine-m-seed <ws>                                    # scores every finding per M; prints the M profile
PMLC nine-m-suggest <ws> --step scope --record           # 2. which Ms to work through (asks Q01)
PMLC nine-m-suggest <ws> --m M1 --step relevance --record   # 3a for one M; then subcategory, condition, ...
PMLC nine-m-suggest <ws> --m M1 --step condition --subcategory M1.08 --record   # later steps take the subcategory
PMLC nine-m-answer <ws> --q Q02 --choice 1               # the user picked suggestion 1
PMLC nine-m-answer <ws> --q Q03 --text "the user's own words"   # free text is always allowed
PMLC select <ws> --code "<code>" --brief                 # the findings behind a code a suggestion names
```

Show the suggestions exactly as printed: 2 to 4, the recommended one first, each with its cites, and always the
last one, `None / unknown (record as a gap)`. Never add an option of your own. The session lives in
`<ws>/nine_m_session.json`, so a run can be resumed and audited.

**The flow** (spec §7.4; the detail is in `nine-m.md`):
1. **Seed.** Run `nine-m-seed` and show the M profile table.
2. **Scope** (`--step scope`): every M with seed weight, M1 to M9 (recommended); the top four; a list; unknown runs all.
3. **Per M in scope, in order M1 to M9**, at most 6 questions, and "skip the rest of this M" is always allowed:
   a. `relevance`: "Not relevant" stops the M; keep its reason and cites for the `not-relevant` table.
   b. `subcategory`: when a suggestion says it overlaps another M, settle which M owns it in this same answer
      (`--text` naming the owning M, `nine-m.md` §2), not with a seventh question.
   c. `condition`: merge conditions that are one learning; count learnings, not instances.
   d. `driver`: why it made sense at the time, from causal links into level 3 and 4 codes.
   e. `barrier`: its state in the shared vocabulary (absent, degraded, defeated, worked partly).
   f. `change`: the strongest feasible tier first; the user says whether it is corrective or preventive.
   g. A leading indicator: there is no engine step for it and a to f use the M's 6, so do not ask it. Derive
      the indicator, and corrective or preventive when 3f leaves it open, and say in `data_quality` they are yours.
   **For M1, get the 3d answer before you write any M1 learning**, or record the driver as unknown.
4. **Cross-M** (`--step cross-m`): keep Ms that a causal link joins as one learning, or separate them.
5. **Gaps** (`--step gaps`): an evidence request for every "None / unknown".

**Budget:** 6 questions per M plus 4 global, 58 at most; the engine refuses one more. Typical runs are far shorter.

**Never offered**, whatever the export says: discipline, "accountability", "consequences" as a sanction, or any
option about a person's character. Suggestions describe conditions.

**Facts the user supplies** that the export does not hold (a shift pattern, a budget rule) go into
`organisation-context` paras and a `data_quality` note, never with an FND citation.

## Write

Write `<run>/outputs/nine-m-analysis.json` from the session, in the shape in `learnings-coach/references/pack-schema.md`.

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/nine-m-analysis.json (repository only).

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | The relevant Ms, the M with the most level 3–4 findings, and the conditions that cross Ms; each cites | `bottom_line` | 3–7 |
| 1 | `nine-m-overview` | The nine Ms | One table, exactly 9 rows, M1 to M9 in order: M (code and name), Relevance, Conditions, Top subcategory (id and name), Findings in the seed; `row_cites` from the relevance answer | `table` | 1 |
| 2 | `m*` | `M<n> <name>` (ids `m1` to `m9`) | One section per relevant M: per condition one `learning`, one `barrier` and one `recommendation`, sharing a `group` (`c-m<n>-1`, …); a `question` for an evidence request | `learning`, `barrier`, `recommendation`, `question` | 0–12 |
| 3 | `not-relevant` | Not relevant | One table, columns M and Why not relevant, a non-empty reason per row; leave it out when every M is relevant | `table` | 0–1 |
| 4 | `cross-m` | Conditions that cross Ms | A `graph`: one node per M, an edge per cross-M answer labelled with the causal link | `graph` | 0–1 |
| 5 | `organisation-context` | Context supplied by the organisation | Facts the user gave, uncited; on a replay, first the banner `para` | `para` | 0–5 |

**Each M section, from its answers:**
- `learning`: `lesson` names the condition (3c), `explanation` gives the subcategory (3b), the system driver with its
  code (3d) and the barrier state (3e); `cites` the condition's findings. Carry `learning: "LR-nn"` for the register
  learning that holds the condition's first finding, unless another M already carries it.
- `barrier`: `barrier`, `failure_mode` and `state` from 3e, citing the finding and the `EVD-` quote it showed.
- `recommendation`: `change` at the tier chosen in 3f, saying corrective or preventive; `hoc_tier` that tier;
  `indicator` from 3g, or one you derive and say so. **Never `owner` or `by_when`**: `check-pack` refuses them.
- Cite in `cites` only findings the seed links to that M (rule `nine-m-cites`); a driver finding from another M goes
  in `supporting_cites`. A not-relevant M has no section, only its row with the reason.

```json
{"kind": "recommendation", "group": "c-m9-1", "hoc_tier": "elimination", "learning": "LR-05",
 "change": "Preventive: remove the repeat reseal task by replacing the legacy joint …",
 "indicator": "Repeat seal jobs on the same joint in 12 months", "cites": ["FND-0003"]}
```

**The replay banner.** When the session's `mode` is `replay` (`nine-m-replay --accept-recommended`), the pack needs
one `para` in `organisation-context` whose `text` is exactly, character for character:
`Answers chosen for demonstration, not by the organisation.` `check-pack` reports it missing (rule
`banner:nine-m-demo`) on a replay only; never put it on a real interview. The replay exists for demonstrations and
tests (`BANNERS` in `pack/profiles.py`); the organisation's own answers come from the interview.

## If the evidence is thin

Follow `skill-common.md` §6, and:
- **An M with no seeded finding:** its relevance question offers "Not relevant"; take the user's answer and keep the
  reason. Never stretch a wording-only signal into a condition without the user's yes.
- **"None / unknown" answers:** each becomes a `gaps` entry with the evidence that would settle it (step 5).
- **No causal graph:** the driver step falls back to the M's own level 3 and 4 findings; say so in the explanation.

## Not covered here

- How strong the recommendations already in the register are: `recommendation-strength-review`.
- Which barriers failed and how strong fixes should be: `barrier-learnings`.
- The formal register row per learning: `learnings-register` (it reads `nine-m-map.json`).
- Assigning owners and dates: the organisation does it in the blank actions sheet.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/nine-m-analysis.json --strict   # fix every problem it lists
PMLC pack <ws> <run>/outputs/nine-m-analysis.json                  # -> .html, .md and outputs/nine-m-map.json
PMLC pack <ws> <run>/outputs/nine-m-analysis.json --format docx    # -> nine-m-analysis.docx, a Word paper
PMLC pack <ws> <run>/outputs/nine-m-analysis.json --format csv     # -> the recommendations as a CSV
PMLC nine-m-actions-template <ws> <run>/outputs/nine-m-analysis.json   # blank Owner, Due date and Status
```

Tell the user which Ms were relevant, the conditions that cross Ms, the gaps, and that the actions sheet's Owner,
Due date and Status columns are for the organisation to fill in. It never overwrites an existing sheet.
