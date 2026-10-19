# top-management-brief

A brief for the CEO, the executive committee, corporate HSE and corporate function heads. It says which learnings transfer across sites and the enterprise, which corporate policies, standards and investments they touch, and what to decide at enterprise level. Four pages at most.

## What it is for

- An ExCo or CEO brief.
- An enterprise-wide lessons note, or cross-site learning.
- A review of corporate standards after an incident.
- "What does head office need to do?"

Top management (tier T5) sets policy, enterprise standards and investment, and decides whether a lesson from one site is applied at every site.

## How to start it

- "Prepare an ExCo brief on what this investigation means for the whole company."
- "Which learnings would apply at our other sites, and what should head office decide?"
- "Which corporate standards does this investigation touch?"

## What it needs

- `clusters.json` from [learning-clusters](learning-clusters.md).
- A Learnings Register if one exists; otherwise the skill finds the level 4 learnings directly.

## Engine commands and flags

```bash
pmlc select <ws> --tier T4 T5 --brief
pmlc select <ws> --level 4 --top-rated
pmlc select <ws> --tag people corporate assurance --level 4 --brief
pmlc select <ws> --preset top-management-brief   # the three calls above at once
pmlc check-pack <ws> <run>/outputs/top-management-brief.json
pmlc pack <ws> <run>/outputs/top-management-brief.json
```

- [select](../commands/select.md): `--tier T4 T5` keeps leadership and corporate findings; `--level 4` the Organisational Influences level; `--top-rated` the strongest; `--tag people corporate assurance` every function tagged as people, corporate or assurance (HR and training, corporate and board, HSE and audit in the default list); `--brief` short entries.
- [check-pack](../commands/check-pack.md) and [pack](../commands/pack.md) render the pack. The pack's scope is level 4 at the top rating.

## What you get

`top-management-brief.html` and `.md`:

1. an **executive summary**: what happened in two sentences, the three enterprise learnings and the decisions requested;
2. **transferability**: for each level 4 learning, site-specific, likely at similar sites, or enterprise-wide, with the reason;
3. **policies and standards implicated**, and what the evidence shows about how they were applied;
4. four to six **decisions**, each with options, a trade-off and an enterprise indicator;
5. **assurance** questions: how the organisation will know the learning is applied at every site.

The tone is neutral and factual, with roles only. Owners are named as functions.

## Worked example (Hazira)

`select --tier T4 T5 --brief` returned 54 findings: only one finding on Hazira touches tier T5, so nearly all of these are site leadership findings. `--level 4 --top-rated` returned 47, and the tag call returned 40. A transferability row could rest on the finding that locally bought O-rings had become the regular practice, with no specification or quality control (FND-B86F67F0, EVD-8645): a condition worth checking at any site with legacy equipment.

These counts are from the base classification, before the resolution pass. After you place the remaining roles they will be somewhat higher, most for T3 (in a trial resolution pass on Hazira: T1 222→231, T2 237→238, T3 211→257).

## Related skills

- [board-brief](board-brief.md): the same event for the board's oversight role.
- [auditor-assurance-pack](auditor-assurance-pack.md): the assurance behind section 5.
- [site-leadership-coach](site-leadership-coach.md): the site-level decisions.
