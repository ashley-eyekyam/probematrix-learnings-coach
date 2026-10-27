# systemic-accimap

A systemic AcciMap of one investigation, for corporate HSE, site leaders and the investigation team. It lays every finding out on Rasmussen's six levels of the wider system, from government policy and the regulator down to the work and the equipment, draws the causal links between the codes cited most at each level, and names the levels the export does not reach. Placements at levels 1 to 3 are inferred from codes and departments, so the pack opens with a fixed banner and ends with questions that ask a person to confirm each inferred level before the map is shared. The method follows Rasmussen's AcciMap as Salmon, Cornelissen and Trotter (2012) compare it with HFACS; `hfacs-levels.md` §7 has the placement rules.

## What it is for

- "Where in the wider system did this come from?"
- An AcciMap or a Rasmussen-style map of the findings.
- What the regulator, the company and its operational management each contributed, and which of those levels the investigation never looked at.
- A wall chart of the system levels for a review, with the gaps marked.

## How to start it

- "Draw an AcciMap from this ProbeMatrix export."
- "Lay the causes out by level of the system, from the regulator down to the equipment."
- "Which levels above the company does this investigation reach?"

## What it needs

- A workspace from [learnings-coach](learnings-coach.md). `setup` writes the entity tags and the causal graph the placement and the links come from.
- The `accimap.json` artefact, which the first command below writes.
- Optional: the Learnings Register. With it, each learning carries the register learning (`LR-nn`) that holds most of its findings.

## Engine commands and flags

```bash
pmlc accimap <ws>                                        # writes accimap.json; prints the levels and the gaps
pmlc accimap <ws> --graph-item                           # the map as a ready graph item
pmlc accimap <ws> --table-item levels                    # findings per level, with row_cites
pmlc accimap <ws> --json                                 # every placement, the gaps and the notes
pmlc check-pack <ws> <run>/outputs/systemic-accimap.json --strict
pmlc pack <ws> <run>/outputs/systemic-accimap.json
pmlc pack <ws> <run>/outputs/systemic-accimap.json --format svg,graphml   # the map as a picture and for yEd or Gephi
pmlc pack <ws> <run>/outputs/systemic-accimap.json --format docx,pptx     # a Word paper and slides
```

- [accimap](../commands/accimap.md) places each finding by the rules in `references/accimap.json`: entities first (regulators at level 2; corporate, vendors and contractors at level 3), then the HFACS level. `--graph-item` prints one node per level, up to four code nodes under each and the causal links between them; `--table-item levels` prints the levels table; `--map FILE` adds keywords or replaces rules.
- [check-pack](../commands/check-pack.md) with `--strict` checks the pack against its profile, including the fixed banner (rule `inferred-banner`, a problem even without `--strict` whenever a node is inferred), then [pack](../commands/pack.md) renders it.

The skill pastes the graph item and the levels table whole and never retypes a count or a label. When a pasted code name says "Failed to", the graph item carries a `lint_ok` for rule JC3: the name is quoted from the export.

## What you get

`systemic-accimap.html` and `systemic-accimap.md`, with these sections:

- **banner:** the fixed text "Placements above the company level are inferred from codes and departments. A person confirms them before this map is shared.";
- **map:** the AcciMap, one band per level with its most-cited codes and the links between them;
- **levels:** the findings at each level and how they were placed (inferred, or from the HFACS level);
- **gaps:** every level with no placement, government included, as a question for the organisation;
- **learnings:** up to five conditions that a higher level set up for a lower one, each with the levels, the link's mention count and, where the register has it, its `LR-nn`;
- **confirm:** one question per inferred level, and one per gap, for a person to answer before the map is shared.

No owners or dates are written. `--format svg` and `graphml` write the map alone (`systemic-accimap.accimap.svg` and `.graphml`); `docx` and `pptx` give the whole pack as a Word paper and slides.

## Worked example (Hazira)

`accimap` printed:

```text
Wrote accimap.json: 436 findings placed, 2 empty level(s) (1, 2).
```

Level 3 (company management) holds 143 findings: 134 HFACS level 4 findings and 9 tagged to the corporate centre or a vendor. Level 4 (technical and operational management) is the busiest, with 166; level 5 holds 76 and level 6 holds 51. Levels 1 (government) and 2 (regulators) are gaps: no finding is tagged to a regulator.

The strongest links across levels run from SVI 1.4 (missing policy and guidance, level 4) to checklists not followed at level 5 and to unclear technical guidance at level 6, 6 mentions each. The golden pack names five conditions: the management-of-change procedure not in use (LR-06), no return-to-service procedure for the meters (LR-02), generic audit checklists (LR-20), repeat seal failures handled as routine repairs (LR-05) and the emergency plan with no isolation criteria (LR-07). Its four confirm questions cover level 3, the seven vendor placements, the regulator and government. It is `samples/2020-09-24-hazira-gas-release-fire/outputs/systemic-accimap.json` in the repository.

## Related skills

- [causal-map](causal-map.md): the causal pathways from level 4 to level 1, story by story.
- [latent-conditions-profile](latent-conditions-profile.md): counts of the factors that recur and feed the most others.
- [organisation-learning-map](organisation-learning-map.md): which departments, tiers and roles should learn what.
- [interface-learnings](interface-learnings.md): what fell between two departments.
