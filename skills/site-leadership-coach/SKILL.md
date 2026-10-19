---
name: site-leadership-coach
description: Produce learning for site and asset leadership from a ProbeMatrix investigation export - plant manager, head of operations, site leadership team - on the decisions, trade-offs, resourcing, authority and culture signals that shaped the event, with the decisions leadership must now take and what leaders should visibly model. Use when someone asks what plant or site leaders should learn, for a leadership-team debrief, a site leadership workshop, a management review after an incident, or "what does the plant manager need to decide".
---

# Site Leadership Coach

Audience: T4 plant / asset leadership. They set site priorities, allocate budgets and people, delegate authority and, by what they tolerate, set the norms.

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py` (this skill needs the `learnings-coach` skill installed alongside it). Read `learnings-coach/references/learning-principles.md`.

## Gather

```bash
PMLC select <ws> --tier T4 --brief
PMLC select <ws> --level 4 --top-rated
PMLC select <ws> --relation norm_setter learner absent challenger
PMLC causal <ws> --top 40          # organisational hubs
PMLC timeline <ws> --before incident
```

## Write

1. **Bottom line for the leadership team**: five learnings, each one sentence.
2. **How the site set this up**: the organisational hubs from the causal map (L4 factors with the most downstream links), told as two or three pathways from leadership conditions to the event. Evidence trail on each step.
3. **Signals that reached leadership level** (from the timeline) and what happened to them.
4. **Culture signals**: what the organisation had come to treat as normal, what leaders modelled or tolerated, where challenge was absent. Describe norms, not people.
5. **Decisions for the leadership team**: six to ten decisions, each framed as a choice with its trade-off (cost, production, staffing, authority), the learning it answers, and the leading indicator leadership will watch. Include delegation-of-authority questions if the findings show escalation delays.
6. **What leaders will do visibly** in the next 30 days: walk-throughs, questions to ask in reviews, things to stop accepting.

## Output

Write the pack `<run>/outputs/site-leadership-coach.json` (schema: `learnings-coach/references/pack-schema.md`), then:

```bash
PMLC check-pack <ws> <run>/outputs/site-leadership-coach.json   # fix every problem it lists
PMLC pack <ws> <run>/outputs/site-leadership-coach.json         # -> site-leadership-coach.html (primary) and .md
```

Sections → kinds:
1. The pack's `bottom_line`: five entries.
2. A `graph` from `PMLC causal-item <ws> --top 20`. Paste it unchanged; drop nodes only if you need to. Follow it with one `para` per pathway, with `group` = the pathway's name.
3. A `timeline`, with `signal`, `received_by` and `response` on each event.
4. `para`.
5. `decision` ×6–10 (options, trade_offs, owner). Follow each one with the `indicator` leadership will watch, in the same `group`.
6. `check` items, with `when` = "next 30 days".

Close with a `workshop` section: one `table` with columns Time, Activity and Built on, for a two-hour agenda built on sections 2, 4 and 5.

Set `"scope": {"tiers": ["T4"]}`. Put data-quality corrections in `data_quality`, findings left out on purpose in `exclusions`, and same-condition findings in `supporting_cites`. Owner wording: `owner` is the function that **owns the change**, not who "was involved" (`learning-principles.md`).

```json
{"kind": "decision", "group": "Spares specification", "decision": "Require a specification for every critical-spares order",
 "options": ["…", "…"], "trade_offs": "…", "owner": "Site operations function", "cites": ["FND-…"]}
```
