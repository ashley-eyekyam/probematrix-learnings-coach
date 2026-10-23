# latent-conditions-profile

A profile of the latent conditions in one investigation, for corporate HSE and top management. It shows where the findings sit on the four HFACS levels, which factors the investigation found again and again, which organisational factors the causal explanations name as enabling the most others, and what share of the findings sit at supervision and organisation (levels 3 and 4). It then names up to six conditions that run under many separate findings. A fixed note says what the counts cannot tell you: for one incident they describe this investigation only.

## What it is for

- "Which conditions keep coming up in this investigation?"
- An HFACS profile or heat map of the findings.
- "How much of this was supervision and organisation, not the people at the sharp end?"
- The organisational factors that sit behind the most others.

## How to start it

- "Profile the latent conditions in this ProbeMatrix export for our corporate HSE team."
- "Which HFACS factors recur most, and which organisational ones feed the most others?"
- "What share of the findings sit at levels 3 and 4?"

## What it needs

- A workspace from [learnings-coach](learnings-coach.md). `setup` writes the causal graph the feed counts come from.
- The `hfacs_profile.json` artefact, which the first command below writes.
- Optional: the Learnings Register. With it, each condition is tied to the register learning (`LR-nn`) that holds most of its findings.

## Engine commands and flags

```bash
pmlc hfacs-profile <ws>                                  # writes hfacs_profile.json and prints the heat map
pmlc hfacs-profile <ws> --table-item heatmap             # the heat map as a ready table item
pmlc hfacs-profile <ws> --table-item feeds               # links out and in per code
pmlc hfacs-profile <ws> --table-item recurrence          # codes carried by two or more findings
pmlc select <ws> --preset latent-conditions-profile:top-l34   # the top-rated level 3 and 4 findings
pmlc select <ws> --code "<code>" --brief                 # the findings behind one code
pmlc check-pack <ws> <run>/outputs/latent-conditions-profile.json --strict
pmlc pack <ws> <run>/outputs/latent-conditions-profile.json
pmlc pack <ws> <run>/outputs/latent-conditions-profile.json --format docx   # a Word paper
pmlc pack <ws> <run>/outputs/latent-conditions-profile.json --format pptx   # slides for a management review
```

- [hfacs-profile](../commands/hfacs-profile.md) counts the findings per level and sub-category, the codes that recur, and the links in and out of each code in `causal_graph.json`. `--table-item heatmap|feeds|recurrence` prints one ready `table` item, every row with its citations; `--json` prints the whole profile.
- [select](../commands/select.md) with `--preset latent-conditions-profile` runs the preset `top-l34` (`--level 3 4 --top-rated --brief`). With `--code` it shows the findings for one code, such as `SVI 1.4`, and `--brief` keeps them short.
- [check-pack](../commands/check-pack.md) with `--strict` checks the pack against its profile, including the fixed banner (rule `banner:profile-limits`), then [pack](../commands/pack.md) renders it.

The skill pastes the heat map whole. It keeps the first 12 rows of the feeds and recurrence tables (the engine sorts them, most first) and never retypes a count.

## What you get

`latent-conditions-profile.html` and `latent-conditions-profile.md`, with these sections:

- **heatmap:** level by sub-category, with the top-rated and other findings in each row;
- **feeds:** the factors with the most links out, the ones the causal explanations name as enabling others;
- **recurrence:** the codes carried by the most findings (left out when none recurs);
- **share:** the fixed banner "For one incident these counts describe this investigation only. They are not rates, trends or a benchmark.", then the level 3 and 4 share and the counts per level;
- **learnings:** up to six latent conditions, each with its engine counts, its evidence and, where the register has it, its `LR-nn`;
- **cannot-tell:** "What this profile cannot tell you": counts measure how often a factor was coded or a link named, not how much it contributed.

No owners or dates are written: the organisation decides who changes each condition. `--format docx` and `--format pptx` give the same content as a Word paper and a slide deck.

## Worked example (Hazira)

`hfacs-profile` printed:

```text
Wrote hfacs_profile.json: 436 findings, 70.6% at levels 3 and 4, 17 heat-map rows, 68 recurring codes, 89 codes in the causal graph.
```

followed by the heat map. 167 findings sit at level 3 and 141 at level 4, so 308 of 436 (70.6%) are supervision or organisational findings. Supervision Inadequate is the largest row (25 top-rated, 51 other), and the Failure to Correct Known Problem row holds 40.

The feeds table puts OIC 2.1 (Organizational Culture Allows for Unsafe Task/Mission) first, with 36 links out and none in, then OIC 2.5 and OIR 1.6 with 26 each. The recurrence table puts SVI 1.4 (Failed to Provide Appropriate Policy/ Guidance) first, with 21 findings, then OIC 2.7 with 19.

The golden pack names five conditions: written guidance missing for high-consequence work (SVI 1.4, under 12 register learnings), known risks accepted as normal working (OIC 2.1, under 14 of the 25), repeat seal failures handled as routine repairs (LR-05), a change procedure on paper but not in use (LR-06), and integrity findings left without a corrective plan (LR-17). It is `samples/2020-09-24-hazira-gas-release-fire/outputs/latent-conditions-profile.json` in the repository.

## Related skills

- [causal-map](causal-map.md): how the same factors connect as pathways from level 4 to level 1.
- [learning-clusters](learning-clusters.md): the findings grouped by department, tier and relation.
- [top-management-brief](top-management-brief.md): executive decisions built on these conditions.
- [learnings-register](learnings-register.md): the register learnings each condition runs under.
