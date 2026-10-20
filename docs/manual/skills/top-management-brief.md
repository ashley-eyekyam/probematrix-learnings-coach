# top-management-brief

A brief for the CEO, the executive committee, corporate HSE and corporate function heads. It says which learnings transfer across sites and the enterprise, which policies, standards and legal requirements they touch, what to decide at enterprise level, and, on request, a management-review input. Four pages at most.

## What it is for

- An ExCo or CEO brief.
- An enterprise-wide lessons note, or cross-site learning.
- A review of corporate standards and the legal register after an incident.
- "What does head office need to do?"

Top management (tier T5) sets policy, enterprise standards and investment, and decides whether a lesson from one site is applied at every site. The executive committee decides and resources; the board oversees and asks ([board-brief](board-brief.md)).

## How to start it

- "Prepare an ExCo brief on what this investigation means for the whole company."
- "Which learnings would apply at our other sites, and what should head office decide?"
- "Give me the management-review input from this investigation for the corporate management review."

## What it needs

- `clusters.json` from [learning-clusters](learning-clusters.md).
- Optional: the Learnings Register; the brief then takes the enterprise learnings from it and carries their `LR-nn` ids.

## Engine commands and flags

```bash
pmlc select <ws> --tier T4 T5 --brief
pmlc select <ws> --level 4 --top-rated
pmlc select <ws> --tag people corporate assurance --level 4 --brief
pmlc select <ws> --tag leadership corporate --level 4 --brief
pmlc select <ws> --preset top-management-brief   # the four calls above at once
pmlc register-items <ws> --tier T5               # the register's T5 learnings
pmlc facts <ws>                                  # headline numbers and priority-1 learnings by tier
pmlc check-pack <ws> <run>/outputs/top-management-brief.json --strict
pmlc pack <ws> <run>/outputs/top-management-brief.json
```

- [select](../commands/select.md): `--tier T4 T5` keeps leadership and corporate findings; `--level 4` the Organisational Influences level; `--top-rated` the strongest; `--tag people corporate assurance` and `--tag leadership corporate` select by function tag (HR and training, corporate and board, HSE and audit, plant leadership in the default list), so the brief survives an organisation's own taxonomy; `--brief` short entries.
- [register-items](../commands/register-items.md) and [facts](../commands/facts.md) give the register's learnings and the headline numbers.
- [check-pack](../commands/check-pack.md) with `--strict` and [pack](../commands/pack.md) render the pack. The pack's scope is level 4 at the top rating.

## What you get

`top-management-brief.html` and `.md`:

1. an **executive summary**: what happened in two sentences and the decisions requested, with the three enterprise learnings as the bottom line;
2. **transferability**: for each learning, site-specific, likely at similar sites, or enterprise-wide, with the reason;
3. **policies, standards and legal requirements implicated**, with requirement ids from the standards crosswalk where they apply, and what the evidence shows about how they were applied (never that a requirement was breached);
4. up to six **decisions**, each marked "For decision" or "For noting", with options, a trade-off and an enterprise indicator with its deterioration trigger;
5. optionally, the **management review input**: exactly six rows (incidents and corrective actions, monitoring results, audit results, risks and opportunities, adequacy of resources, consultation outcomes), each citing its findings or reading "not in this investigation";
6. **assurance** questions: how the organisation will know the learning is applied at every site.

The tone is neutral and factual, with roles only. Owners are named as functions.

## Worked example (Hazira)

On the base classification, `select --tier T4 T5 --brief` returned 39 findings: only one finding on Hazira touches tier T5, so the brief falls back to tier T4 and level 4 and says so. `--level 4 --top-rated` returned 47, `--tag people corporate assurance --level 4` 40 and `--tag leadership corporate --level 4` 14. With the sample register, `register-items --tier T5` gave 12 learnings. A transferability row could rest on the finding that locally bought O-rings had become the regular practice, with no specification or quality control (FND-B86F67F0, EVD-8645): a condition worth checking at any site with legacy equipment.

These counts are from the base classification, before the resolution pass. After you place the remaining roles they will change.

## Related skills

- [board-brief](board-brief.md): the same event for the board's oversight role.
- [auditor-assurance-pack](auditor-assurance-pack.md): the assurance behind the last section.
- [site-leadership-coach](site-leadership-coach.md): the site-level decisions, and the ones marked "Needs corporate decision".
