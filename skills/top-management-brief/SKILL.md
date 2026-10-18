---
name: top-management-brief
description: Produce a top-management brief from a ProbeMatrix investigation export for the CEO, executive committee, corporate HSE and corporate function heads - which learnings transfer across sites and the enterprise, which corporate policies, standards and investments they implicate, and what to decide at enterprise level. Use when someone asks for an ExCo or CEO brief, an enterprise-wide lessons note, cross-site learning, corporate standards review after an incident, or "what does head office need to do".
---

# Top Management Brief

Audience: T5 corporate leadership. They set policy, enterprise standards and investment, and they decide whether a lesson from one site is applied at every site.

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py` (this skill needs the `learnings-coach` skill installed alongside it). Read `learnings-coach/references/learning-principles.md`.

## Gather

```bash
PMLC select <ws> --tier T4 T5 --brief
PMLC select <ws> --level 4 --top-rated
PMLC select <ws> --tag people corporate assurance --level 4 --brief   # people, corporate, assurance
```

Use the Learnings Register if one exists; otherwise identify the L4 learnings directly.

## Write (four pages at most)

1. **Executive summary** (half a page): what happened, in two sentences; the three enterprise-level learnings; the decisions requested.
2. **Transferability**: for each L4 learning, would the same condition plausibly exist at other sites? Classify as site-specific / likely at similar sites / enterprise-wide, with the reason (shared standard, shared system, shared culture, shared vintage of equipment).
3. **Policies and standards implicated**: which corporate policies, standards or programmes (change management, spares and sourcing, maintenance strategy, emergency planning, competence, audit) the findings touch, and what the evidence shows about their implementation.
4. **Decisions for top management**: four to six, each with options, trade-off, and the enterprise indicator that would show progress (e.g. "% of sites with verified emergency-isolation authority").
5. **Assurance**: how the organisation will know the learning has been applied across sites (link to `auditor-assurance-pack`).

## Output

Write the pack `<run>/outputs/top-management-brief.json` (schema: `learnings-coach/references/pack-schema.md`), then:

```bash
PMLC check-pack <ws> <run>/outputs/top-management-brief.json   # fix every problem it lists
PMLC pack <ws> <run>/outputs/top-management-brief.json         # -> top-management-brief.html (primary) and .md
```

Sections → kinds:
1. `para`, with the four HFACS levels defined once. The three enterprise learnings go in `bottom_line`.
2. `table` with columns Learning, Transferability (site-specific, likely at similar sites, or enterprise-wide) and Reason, plus `row_cites`.
3. `para`, with `group` = the policy or standard.
4. `decision` ×4–6. Follow each one with its enterprise `indicator`, in the same `group`.
5. `question`, with `to` = the role asked.

Set `"scope": {"levels": [4], "min_rating": "top"}`. Put data-quality corrections in `data_quality`, findings left out on purpose in `exclusions`, and same-condition findings in `supporting_cites`. Use board-ready language.

```json
{"kind": "table", "columns": ["Learning", "Transferability", "Reason"],
 "rows": [["…", "Likely at similar sites", "…"]], "row_cites": [["FND-…"]]}
```
