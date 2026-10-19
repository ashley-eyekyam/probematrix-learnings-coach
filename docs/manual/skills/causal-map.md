# causal-map

The causal map of an investigation: how organisational influences enabled supervisory gaps, preconditions and unsafe acts. It uses the factor links the AI wrote into each finding's causal explanation, so it works even when the export's Causal Chain sheet is empty. You get a drawn graph, the hub factors, the main pathways told as short stories, and the gaps where a link is missing.

## What it is for

- "How do the factors connect?"
- A causal chain, causal tree or root-cause pathway.
- "How did the organisation set this up?"
- A diagram of the investigation for a briefing.

## How to start it

- "Show me how the factors in this investigation connect, from the organisation down to the event."
- "Draw the causal map and tell the three strongest pathways."
- "Which organisational conditions fed the most downstream factors?"

## What it needs

- A workspace from [learnings-coach](learnings-coach.md). Clusters are not needed for the graph itself.
- Findings whose causal explanations name other factor codes. The engine says how many do.

## Engine commands and flags

```bash
pmlc causal <ws> --top 60                             # causal explanations only
pmlc causal <ws> --top 60 --include-justification     # a wider net: the justification text too
pmlc select <ws> --code "<code>"                      # read the findings behind a link
pmlc causal-item <ws> --top 40                        # the graph item to paste into the pack
pmlc check-pack <ws> <run>/outputs/causal-map.json
pmlc pack <ws> <run>/outputs/causal-map.json
```

- [causal](../commands/causal.md) writes `causal_graph.json` and `causal_graph.mmd`. `--top` sets how many links it prints. `--include-justification` also reads the AI justification text.
- [select](../commands/select.md) with `--code` shows the findings for one factor code, such as `OIR 1.6`.
- [causal-item](../commands/causal-item.md) prints a ready `graph` item from `causal_graph.json`, so links are never retyped. `--top` keeps that many links (default 40).
- [check-pack](../commands/check-pack.md) and [pack](../commands/pack.md) render the pack.

The direction of each link follows the four levels: the higher-level factor enables the lower-level one. Links between factors on the same level have no direction.

## What you get

`causal-map.html` (with the drawn graph) and `causal-map.md`, with these sections:

- **map:** the graph, kept to the top 30 to 40 links so it stays readable;
- **hubs:** the factors with the most outgoing links;
- **pathways:** three to six stories, each in four sentences, one per level, read from the organisation down and ending on a condition, never on a person;
- **breaks:** links the story needs but the graph lacks, stated as gaps;
- **sequence:** the order from latent conditions to the trigger.

## Worked example (Hazira)

`causal --top 60` printed:

```text
287 of 436 findings name other factors in their causal explanation. 555 distinct links. Wrote causal_graph.json and causal_graph.mmd (top 60).
```

With `causal --include-justification` the count rose to 675 distinct links. The strongest link was OIR 1.6 (Failure in Maintenance/ Spares/ Support Programme, level 4) to SVF 3.4 (level 3), with 7 mentions. `causal-item --top 40` gave a graph of 26 factors and 40 links.

## Related skills

- [site-leadership-coach](site-leadership-coach.md): uses the organisational hubs.
- [precursor-timeline](precursor-timeline.md): the same story in time order.
- [barrier-learnings](barrier-learnings.md): which defences the pathways passed through.
- [investigator-coach](investigator-coach.md): tests causal hypotheses where the graph has gaps.
