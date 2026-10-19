---
name: causal-map
description: Extract and explain the causal map of a ProbeMatrix investigation - how organisational influences enabled supervisory failures, preconditions and unsafe acts - using the factor links the AI wrote into each finding's causal explanation, even when the export's Causal Chain sheet is empty. Produces a Mermaid diagram, a ranked list of causal pathways and a plain-language narrative. Use when someone asks how the factors connect, for a causal chain, causal tree, root-cause pathway, "how did the organisation set this up", or wants a diagram of the investigation.
---

# Causal Map

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py` (this skill needs the `learnings-coach` skill installed alongside it).

## Build

```bash
PMLC causal <ws> --top 60                       # causal explanations only
PMLC causal <ws> --top 60 --include-justification   # wider net, more links
```

Outputs `<ws>/causal_graph.json` (nodes, edges with mention counts and supporting finding IDs) and `<ws>/causal_graph.mmd` (Mermaid flowchart grouped by level). Edge direction follows the four-level convention: the higher-level factor enables the lower-level one. Same-level links have no implied direction.

## Interpret

1. **Hubs.** Rank nodes by out-degree from L4 and L3. These are the organisational and supervisory conditions that fed many downstream factors: the most valuable learnings.
2. **Pathways.** Trace three to six chains from an L4 node to an L1 node through the strongest edges. For each, read the supporting findings (`PMLC select <ws> --code "<code>"`) and write the pathway as a story in four sentences, one per level, with evidence IDs. **Read it top-down and end on a condition, never on a person:** start at the L4 condition, pass through supervision and preconditions, and finish on the sharp-end condition (for example "the replacement was returned to service without a design-pressure test"), not on someone's act or character.
3. **Breaks.** Where the narrative needs a link the graph lacks, say so as a gap. Do not invent the link.
4. **Event sequence.** If the export narrative or evidence gives times, align the pathways to the event sequence (latent conditions → trigger → escalation → response).

## Output

Write the pack `<run>/outputs/causal-map.json` (schema: `learnings-coach/references/pack-schema.md`), then:

```bash
PMLC causal-item <ws> --top 40                      # paste its output as the graph item; never retype links
PMLC check-pack <ws> <run>/outputs/causal-map.json   # fix every problem it lists
PMLC pack <ws> <run>/outputs/causal-map.json         # -> causal-map.html (primary, drawn graph) and causal-map.md
```

Sections and the kinds that fill them:
- **map:** the `graph` from `causal-item`, kept to the top 30–40 links for legibility.
- **hubs:** a `table` with columns Factor, Level and Out-links, plus `row_cites`.
- **pathways:** one `para` per pathway, with `group` set to the pathway's name. Write four sentences, one per level.
- **breaks:** `para`. Never invent a link.
- **sequence:** a `timeline` running from latent conditions to the trigger.

`causal_graph.mmd` is still written for hosts that draw Mermaid. Put data-quality corrections in `data_quality`, findings left out on purpose in `exclusions`, and same-condition findings in `supporting_cites`.

```json
{"kind": "table", "columns": ["Factor", "Level", "Out-links"], "rows": [["OR 2.2 …", "L4", 3]], "row_cites": [["FND-…"]]}
```
