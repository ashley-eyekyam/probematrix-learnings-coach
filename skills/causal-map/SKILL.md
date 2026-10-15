---
name: causal-map
description: Extract and explain the causal map of a ProbeMatrix investigation - how organisational influences enabled supervisory failures, preconditions and unsafe acts - using the factor links the AI wrote into each finding's causal explanation, even when the export's Causal Chain sheet is empty. Produces a Mermaid diagram, a ranked list of causal pathways and a plain-language narrative. Use when someone asks how the factors connect, for a causal chain, causal tree, root-cause pathway, "how did the organisation set this up", or wants a diagram of the investigation.
---

# Causal Map

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py`.

## Build

```bash
PMLC causal <ws> --top 60                       # causal explanations only
PMLC causal <ws> --top 60 --include-justification   # wider net, more links
```

Outputs `<ws>/causal_graph.json` (nodes, edges with mention counts and supporting finding IDs) and `<ws>/causal_graph.mmd` (Mermaid flowchart grouped by level). Edge direction follows the four-level convention: the higher-level factor enables the lower-level one. Same-level links have no implied direction.

## Interpret

1. **Hubs.** Rank nodes by out-degree from L4 and L3. These are the organisational and supervisory conditions that fed many downstream factors: the most valuable learnings.
2. **Pathways.** Trace three to six chains from an L4 node to an L1 node through the strongest edges. For each, read the supporting findings (`PMLC select <ws> --code "<code>"`) and write the pathway as a story in four sentences, one per level, with evidence IDs.
3. **Breaks.** Where the narrative needs a link the graph lacks, say so as a gap. Do not invent the link.
4. **Event sequence.** If the export narrative or evidence gives times, align the pathways to the event sequence (latent conditions → trigger → escalation → response).

## Output

`<ws>/outputs/causal-map.md` with the Mermaid diagram (keep it to the top 30–40 edges for legibility), a hub table, the pathway stories, gaps, and the footer. If the user wants a picture, render the Mermaid in whatever the host supports or wrap it in a small HTML page.
