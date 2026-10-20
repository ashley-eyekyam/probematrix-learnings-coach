# site-leadership-coach

Learning for the site leadership team: the plant manager, the head of operations and the site leadership team. It covers the decisions, trade-offs, resourcing, authority and culture signals that shaped the event, the decisions leadership can now take within site authority, what leaders should visibly model, and, on request, a management-review input.

## What it is for

- "What should our plant or site leaders learn?"
- A leadership-team debrief or a site leadership workshop.
- A site management review after an incident.
- "What does the plant manager need to decide?"

Site leaders (tier T4) set site priorities, allocate budgets and people, delegate authority and, by what they tolerate, set the norms. One function's own agenda belongs to [manager-coach](manager-coach.md).

## How to start it

- "What does the plant manager need to decide after this investigation?"
- "Prepare a two-hour workshop for the site leadership team."
- "Give the site management review its input from this investigation."

## What it needs

- `clusters.json` from [learning-clusters](learning-clusters.md).
- The causal graph and the precursor candidates, which `setup` writes.
- Optional: the Learnings Register; its T4 learnings are reused with their `LR-nn` ids.

## Engine commands and flags

```bash
pmlc select <ws> --tier T4 --brief
pmlc select <ws> --level 4 --top-rated
pmlc select <ws> --relation norm_setter learner absent challenger --brief
pmlc select <ws> --prefix OIC --level 4 --brief         # culture fallback: organisational climate findings
pmlc select <ws> --preset site-leadership-coach         # the four select calls above at once
pmlc causal-item <ws> --top 20                          # the causal map, ready to paste
pmlc table-item <ws> hubs --top 8                       # organisational hubs
pmlc timeline-item <ws> --before incident --top 12      # signals before the event
pmlc register-items <ws> --tier T4
pmlc check-pack <ws> <run>/outputs/site-leadership-coach.json --strict
pmlc pack <ws> <run>/outputs/site-leadership-coach.json
```

- [select](../commands/select.md): `--tier T4` keeps site leadership findings; `--level 4` the Organisational Influences level; `--top-rated` the strongest; `--relation norm_setter learner absent challenger` the roles that set or received norms, were absent, or were expected to challenge; `--prefix OIC` the level 4 organisational-climate codes (culture, norms, structure), so the culture section is not thin when the relation filter returns little; `--brief` short entries.
- [causal-item](../commands/causal-item.md), [table-item](../commands/table-item.md) `hubs` and [timeline-item](../commands/timeline-item.md) print ready items to paste.
- [check-pack](../commands/check-pack.md) with `--strict` and [pack](../commands/pack.md) render the pack. The pack's scope is tier T4.

## What you get

`site-leadership-coach.html` and `.md`:

1. a **bottom line** of up to five learnings for the leadership team;
2. **how the site set this up**: the causal map and up to three pathways from leadership conditions to the event;
3. **signals that reached leadership**, and what happened to them;
4. **culture signals**: what had become normal, what was modelled or tolerated, where challenge was absent. Norms, not people;
5. up to ten **decisions**, each a choice with its trade-off and the indicator leadership will watch. A decision that needs corporate authority is marked "Needs corporate decision" and feeds the [top-management-brief](top-management-brief.md);
6. **what leaders will do visibly** in the next 30 days;
7. optionally, the **management review input**: exactly six rows, each citing its findings or reading "not in this investigation";
8. a **two-hour workshop agenda**.

## Worked example (Hazira)

On the base classification, `select --tier T4 --brief` returned 39 findings, `--level 4 --top-rated` 47, and the relation filter only 9. The `--prefix OIC --level 4` fallback returned 51 organisational-climate findings, enough for the culture section. `causal-item --top 20` gave a graph of 17 factors and 20 links, and `table-item hubs` put OIC 2.1 (organisational culture allows for unsafe task) first, with 36 links out. A decision on Hazira could rest on the finding that the change-control procedure had not been used since 2018 (FND-F7FE8463, EVD-2986), framed as a choice for leadership, not a verdict on anyone.

These counts are from the base classification, before the resolution pass. The india-process-site overlay, which places site ranks such as GM and CGM, raises the T4 count on Hazira from 39 to 63.

## Related skills

- [causal-map](causal-map.md): the full causal picture behind section 2.
- [precursor-timeline](precursor-timeline.md): the signals behind section 3.
- [top-management-brief](top-management-brief.md): the decisions marked "Needs corporate decision".
- [manager-coach](manager-coach.md): each function's own agenda.
