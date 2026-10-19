# site-leadership-coach

Learning for site and asset leadership: the plant manager, the head of operations and the site leadership team. It covers the decisions, trade-offs, resourcing, authority and culture signals that shaped the event, the decisions leadership must now take, and what leaders should visibly do.

## What it is for

- "What should plant or site leaders learn?"
- A leadership-team debrief or a site leadership workshop.
- A management review after an incident.
- "What does the plant manager need to decide?"

Site leaders (tier T4) set site priorities, allocate budgets and people, delegate authority and, by what they tolerate, set the norms.

## How to start it

- "What should the site leadership team learn from this investigation?"
- "List the decisions the plant leadership must now take, with their trade-offs."
- "Prepare a two-hour leadership workshop built on this event."

## What it needs

- `clusters.json` from [learning-clusters](learning-clusters.md).
- The causal graph and the precursor candidates, which the skill builds.

## Engine commands and flags

```bash
pmlc select <ws> --tier T4 --brief
pmlc select <ws> --level 4 --top-rated
pmlc select <ws> --relation norm_setter learner absent challenger
pmlc select <ws> --preset site-leadership-coach   # the three calls above at once
pmlc causal <ws> --top 40                         # organisational hubs
pmlc timeline <ws> --before incident
pmlc causal-item <ws> --top 20                    # the graph item for the pack
pmlc check-pack <ws> <run>/outputs/site-leadership-coach.json
pmlc pack <ws> <run>/outputs/site-leadership-coach.json
```

- [select](../commands/select.md): `--tier T4` keeps leadership-tier findings; `--level 4` the Organisational Influences level; `--top-rated` the strongest; `--relation norm_setter learner absent challenger` the findings about what leaders modelled, what people absorbed, absent functions and missing challenge; `--brief` short entries.
- [causal](../commands/causal.md) and [causal-item](../commands/causal-item.md) give the organisational hubs and the graph.
- [timeline](../commands/timeline.md) with `--before incident` gives the signals that reached leadership level.
- [check-pack](../commands/check-pack.md) and [pack](../commands/pack.md) render the pack.

## What you get

`site-leadership-coach.html` and `.md`:

1. five learnings, one sentence each;
2. **how the site set this up:** the graph, and two or three pathways from leadership conditions to the event;
3. **signals that reached leadership level**, and what happened to them;
4. **culture signals:** what had come to feel normal, what was modelled or tolerated, where challenge was absent. It describes norms, not people;
5. six to ten **decisions**, each a choice with its trade-off (cost, production, staffing, authority) and the indicator leadership will watch;
6. **what leaders will do visibly** in the next 30 days;
7. a two-hour **workshop** agenda.

Owners are written as functions ("Site operations function"), because at this level a post can be one person.

## Worked example (Hazira)

`select --tier T4 --brief` returned 54 findings; `--level 4 --top-rated` returned 47; and the relation filter returned 9. `causal-item --top 20` gave a graph of 17 factors and 20 links. A decision on Hazira could rest on the finding that the change-control procedure had not been used since 2018 (FND-F7FE8463, EVD-2986), framed as a choice for leadership, not a verdict on anyone.

These counts are from the base classification, before the resolution pass. After you place the remaining roles they will be somewhat higher, most for T3 (in a trial resolution pass on Hazira: T1 222→231, T2 237→238, T3 211→257). The india-process-site overlay, which places site ranks such as GM and CGM, raises the T4 count on Hazira from 54 to 78.

## Related skills

- [causal-map](causal-map.md): the full causal picture behind section 2.
- [precursor-timeline](precursor-timeline.md): the signals behind section 3.
- [top-management-brief](top-management-brief.md): the same learnings at enterprise level.
