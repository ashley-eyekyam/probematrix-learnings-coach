---
name: systemic-accimap
description: Draws a systemic AcciMap from a ProbeMatrix investigation export, placing every finding on Rasmussen's six levels from government and regulators down to equipment and surroundings, with the causal links between the most-cited codes, a levels table, the empty levels named as questions, up to five learnings about the wider system and a question asking a person to confirm each inferred level before the map is shared. Use when someone with a ProbeMatrix export asks for an AcciMap, a systemic or Rasmussen-style map, "where in the wider system did this come from", or what the regulator, the company and its management each contributed. Not for the causal pathways from level 4 to level 1 (use `causal-map`), counts of the factors that recur (use `latent-conditions-profile`) or which departments and roles should learn what (use `organisation-learning-map`).
---

# Systemic AcciMap

Engine: `PMLC` as in `learnings-coach/references/skill-common.md` §1; this skill needs the `learnings-coach` skill installed alongside it.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions; run `PMLC setup`
when only an .xlsx was given). Needs: `workspace` and `accimap` (the first Gather line writes it; `setup` writes the
entity tags and the causal graph it reads). Optional: the register; when it exists, tie each learning to its `LR-nn`
(§2 "Start from the register"). Read `learnings-coach/references/learning-principles.md` (§3: respect the level;
§4: count honestly) and `learnings-coach/references/hfacs-levels.md` §7 for the six AcciMap levels, the placement
rules and the method (Rasmussen's AcciMap, compared with HFACS by Salmon, Cornelissen and Trotter, 2012).

## Gather

```bash
PMLC accimap <ws>                                    # writes <ws>/accimap.json; prints the levels and the gaps
PMLC accimap <ws> --graph-item                       # the map: one node per level, its top codes, causal links
PMLC accimap <ws> --table-item levels                # findings per level, how each was placed, with row_cites
PMLC accimap <ws> --json                             # placements per finding, the gaps and the notes
```

Paste the graph item and the levels table unchanged: never retype a count, a code, a label or the `inferred` flag.
The summary line names the empty levels (`gaps` in `accimap.json`). A level is `inferred` when its placements come
from entity tags and codes, not from what the export says; levels 1 to 3 always are.

Then read the findings behind the links that cross levels (the graph edges labelled "mentions"), the most mentions
first, with `PMLC accimap <ws> --json` for the placement of each finding and the register's `finding_ids`. Look for
what a higher level did that made the lower level's conditions likely: the company practice under a supervision gap,
the supervision gap under a work-site condition. If the register exists, note which `LR-nn` holds the findings of
each link.

## Write

Write `<run>/outputs/systemic-accimap.json` in the shape in `learnings-coach/references/pack-schema.md`.

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/systemic-accimap.json (repository only).

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | How far up the system the findings reach, the busiest level, and the strongest link that crosses levels; cite the findings behind each | `bottom_line` | 1–3 |
| 1 | `banner` | Before this map is shared | The banner `para` (below), with no cites | `para` | 1 |
| 2 | `map` | The AcciMap | The `--graph-item` graph, whole | `graph` | 1 |
| 3 | `levels` | Findings at each level | The `--table-item levels` table, whole | `table` | 1 |
| 4 | `gaps` | Levels the export does not reach | Name every gap level by number and name, government (level 1) included, and say an empty level is a question for the organisation, not a finding that nobody there contributed; cite the findings of the nearest placed level | `para` | 1–2 |
| 5 | `learnings` | What the wider system shows | One `learning` per condition that a higher level set up for a lower one: `lesson` names the condition, `explanation` names the levels and the link's mention count; carry `learning: "LR-nn"` when one register learning holds most of its cites | `learning` | 1–5 |
| 6 | `confirm` | For a person to confirm | One `question` per inferred level, naming it as "level N": is the placement right, and what would show it; `why` says the level is inferred; one more per gap level is allowed | `question` | 1–6 |

**The banner.** The pack needs one `para` whose `text` is exactly, character for character:
`Placements above the company level are inferred from codes and departments. A person confirms them before this map is shared.`
Put it alone in `banner`. `check-pack` reports it missing (rule `inferred-banner`, a problem even without
`--strict`) whenever a graph node carries `"inferred": true`.

A learning names a condition in the system the organisation can change (`learning-principles.md` §3), never a
person or a regulator's fault: "company practice let risk assessments go unchecked down to the work site", not
"managers ignored the risks". Use the engine's counts as the evidence of spread, and the findings' own text for
what the condition looked like.

```json
{"kind": "question", "question": "Is level 3 (company management) right for the 143 findings placed there?",
 "why": "Level 3 is inferred from HFACS level 4 codes and entity tags, not from what the export says.",
 "good_evidence": "Board or corporate HSE minutes, group standards", "cites": ["FND-0003"]}
```

Every item but the banner cites. Leave `owner` out of every learning and question: a person confirms the map, and
the organisation decides who changes each condition. When a pasted code name says "Failed to" or "Inadequate",
accept the language-check hit with an item `lint_ok` and its reason (`skill-common.md` §4): it is quoted verbatim.

## If the evidence is thin

Follow `skill-common.md` §6, and:
- **No F14 or F15 finding** (`notes` says levels 2 and 3 come from the codes only): keep the map, say so in `gaps`,
  and ask in `confirm` whether the regulator or the corporate centre played a part.
- **No causal graph, or no links between the codes shown:** the map has only the "holds" edges; say in `gaps` that
  the export gave no links across levels, write one learning at most, and add an entry to the pack's top-level
  `gaps` list (`pack-schema.md`).
- **Unplaced findings** (a note lists findings with no HFACS level): name them in a `data_quality` note; never place
  them yourself.

## Not covered here

- The causal pathways from level 4 to level 1, story by story: `causal-map`.
- Counts of the factors that recur and feed the most others: `latent-conditions-profile`.
- Which departments, tiers and roles should learn what: `organisation-learning-map`.
- What fell between two departments: `interface-learnings`.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/systemic-accimap.json --strict   # fix every problem it lists
PMLC pack <ws> <run>/outputs/systemic-accimap.json                  # -> systemic-accimap.html and .md
PMLC pack <ws> <run>/outputs/systemic-accimap.json --format svg,graphml   # the map as a picture and for yEd or Gephi
PMLC pack <ws> <run>/outputs/systemic-accimap.json --format docx,pptx     # a Word paper and slides for a review
```

Offer the svg for a wall chart, the graphml to edit the layout, and the docx or pptx for a review. Tell the user how
far up the system the findings reach, which levels are empty, and that levels 1 to 3 are inferred: a person confirms
them before the map is shared.
