---
name: latent-conditions-profile
description: Profiles the latent conditions in a ProbeMatrix investigation export for corporate HSE and top management, as an HFACS heat map of level by sub-category by rating, a ranking of the organisational factors that feed the most others, the factors that recur most often, the share of findings at levels 3 and 4, and up to six learnings about the conditions that run under many separate findings, with a plain "what this profile cannot tell you" note. Use when someone with a ProbeMatrix export asks for patterns, latent conditions, an HFACS profile or heat map, which factors recur, or "how much of this was supervision and organisation". Not for how the factors connect as pathways (use `causal-map`) or for grouping findings by department and tier (use `learning-clusters`).
---

# Latent Conditions Profile

Engine: `PMLC` as in `learnings-coach/references/skill-common.md` §1; this skill needs the `learnings-coach` skill installed alongside it.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions; run `PMLC setup`
when only an .xlsx was given). Needs: `workspace` and `hfacs-profile` (the first Gather line writes it; `setup`
writes the causal graph it counts links from). Optional: the register; when it exists, tie each learning to its
`LR-nn` (§2 "Start from the register"). Read `learnings-coach/references/learning-principles.md` (§3: respect the
level; §4: count honestly) and `learnings-coach/references/hfacs-levels.md` for the level names.

## Gather

```bash
PMLC hfacs-profile <ws>                              # writes <ws>/hfacs_profile.json and prints the heat map
PMLC hfacs-profile <ws> --table-item heatmap         # level x sub-category x rating, ready to paste
PMLC hfacs-profile <ws> --table-item feeds           # links out and in per code, from causal_graph.json
PMLC hfacs-profile <ws> --table-item recurrence      # codes carried by two or more findings
PMLC select <ws> --level 3 4 --top-rated --brief    # the top-rated level 3 and 4 findings (preset top-l34)
PMLC select <ws> --code "<code>" --brief             # the findings behind one hot code
```

The summary line gives the level 3 and 4 share (`share_l34` in `hfacs_profile.json`, as a percentage to one
decimal) and the counts per level. Paste the three table items unchanged: never retype a count, a code or a name.
**Feeds and recurrence:** keep the first 12 rows (the engine sorts them, most first), their `row_cites` in the
same order, and set the item's `cites` to the sorted IDs of the rows kept. Drop rows only from the end. The heat map
is pasted whole.

Then read the findings behind the top five feeds codes and the top five recurring codes (`select --code`), the
highest-rated first. Look for the condition that sits under many separate learnings: the same missing guidance, the
same accepted risk, the same problem left uncorrected. If the register exists, note which `LR-nn` entries each hot
code's findings belong to.

## Write

Write `<run>/outputs/latent-conditions-profile.json` in the shape in `learnings-coach/references/pack-schema.md`.

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/latent-conditions-profile.json (repository only).

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | The level 3 and 4 share, the factor that feeds the most others and the code that recurs most, each with its engine count; cite the findings behind them | `bottom_line` | 1–5 |
| 1 | `heatmap` | Where the findings sit | The `--table-item heatmap` table, whole | `table` | 1 |
| 2 | `feeds` | Factors that feed the most others | The `--table-item feeds` table, first 12 rows | `table` | 1 |
| 3 | `recurrence` | Factors that recur | The `--table-item recurrence` table, first 12 rows; leave the section out when no code recurs | `table` | 0–1 |
| 4 | `share` | Supervision and organisation | First the banner `para` (below), then one `para` giving the level 3 and 4 share and the counts per level, citing the top-rated findings of the largest level 3 and 4 rows | `para` | 1–2 |
| 5 | `learnings` | Latent conditions | One `learning` per condition that runs under several findings or register learnings: `lesson` names the condition, `explanation` gives its engine counts and where it shows; carry `learning: "LR-nn"` when one register learning holds most of its cites | `learning` | 1–6 |
| 6 | `cannot-tell` | What this profile cannot tell you | One `para`: counts measure how often the investigation coded a factor and named a link, not how much it contributed; no rates, no comparison with other sites; the ratings are the investigation's | `para` | 1 |

**The banner.** The pack needs one `para` whose `text` is exactly, character for character:
`For one incident these counts describe this investigation only. They are not rates, trends or a benchmark.`
Put it first in `share`. `check-pack` reports it missing (rule `banner:profile-limits`) when the text differs at all.

A learning describes a condition the organisation can change (`learning-principles.md` §3), never a person:
"written guidance for high-consequence work did not exist", not "supervisors did not provide guidance". Use the
engine's numbers as the evidence of spread, and the findings' own text for what the condition looked like.

```json
{"kind": "learning", "lesson": "Changes went ahead without the review the change procedure required.",
 "explanation": "The change procedure existed on paper but was not used … (OIC 2.7, 19 findings).",
 "learning": "LR-06", "cites": ["FND-0003", "FND-0002", "EVD-0001"], "evidence_strength": "corroborated"}
```

Every item but the banner cites. Leave `owner` out of every learning: this profile names conditions, and the
organisation decides who changes them. Two language-check hits are expected and right, so accept them with an item
`lint_ok` and its reason (`skill-common.md` §4): JC8 on the share percentage (it is `share_l34`, counted from the
export), and JC3 or JC5 on a pasted table whose HFACS code names say "Failed to" or "Deficient" (quoted verbatim).

## If the evidence is thin

Follow `skill-common.md` §6, and:
- **No causal graph, or no links in it** (`feeds` is empty and `notes` says why): keep the `feeds` table with the
  engine's rows as they are, say in `cannot-tell` that the export gave no links, and add a `gaps` entry.
- **Unresolved prefixes** (`unresolved` in `hfacs_profile.json`): those codes are not in `hfacs-codes.json`; name
  them in a `data_quality` note and do not place them at a level yourself.
- **Few level 3 or 4 findings:** write the share as it is. One learning is enough; never stretch a single finding
  into a pattern.

## Not covered here

- How the factors connect as pathways from level 4 to level 1: `causal-map`.
- Findings grouped by department, tier and relation: `learning-clusters`.
- Whether the evidence behind the findings is strong: `evidence-strength-scorecard`.
- Decisions for executives built on these conditions: `top-management-brief`.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/latent-conditions-profile.json --strict   # fix every problem it lists
PMLC pack <ws> <run>/outputs/latent-conditions-profile.json                  # -> latent-conditions-profile.html and .md
PMLC pack <ws> <run>/outputs/latent-conditions-profile.json --format docx    # -> latent-conditions-profile.docx, a paper
PMLC pack <ws> <run>/outputs/latent-conditions-profile.json --format pptx    # -> latent-conditions-profile.pptx, for a review
```

Offer the docx for a corporate HSE paper and the pptx for a management review. Tell the user the level 3 and 4
share, the factor that feeds the most others, the code that recurs most, and that for one incident these counts
describe this investigation only.
