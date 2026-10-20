# interface-learnings

The learnings that fall between departments: handovers, shared ownership, unclear authority, and assumptions one function made about another. For each seam it says what passes across it, what went wrong there, why neither side saw it alone, and a joint fix with an indicator both sides can see.

## What it is for

- "What fell through the cracks?"
- Silos, handovers and cross-functional failures.
- "Who should have been talking to whom?"
- Designing a cross-department review after an incident.

## How to start it

- "What fell between departments in this investigation?"
- "Look at the seam between maintenance and stores: what went wrong there and what should both sides change?"
- "Which functions should meet after this incident, and about what?"

## What it needs

- `clusters.json` from [learning-clusters](learning-clusters.md). Interfaces are pairs of entities, so unplaced roles weaken them.

## Engine commands and flags

```bash
pmlc interfaces <ws> --top 25
pmlc table-item <ws> interfaces --top 12                       # the matrix table to paste into the pack
pmlc select <ws> --entity <A> <B> --entity-mode all --brief     # the findings both functions share
pmlc select <ws> --entity <A> --tag emergency --entity-mode all --brief   # A with any emergency-response function
pmlc check-pack <ws> <run>/outputs/interface-learnings.json --strict
pmlc pack <ws> <run>/outputs/interface-learnings.json
```

- [interfaces](../commands/interfaces.md) ranks pairs of functions by **shared findings** (both named on the same finding) and **cross-entity causal mentions** (a finding of one names a factor of the other). `--top` sets how many pairs it prints. It writes `interfaces.json`.
- [table-item](../commands/table-item.md) `interfaces` prints the top pairs as a ready `table` item, with their example findings as row citations; `--top` keeps that many pairs.
- [select](../commands/select.md) with two `--entity` IDs and `--entity-mode all` returns only the findings that carry both. With the default `--entity-mode any` you would get every finding of either function, which is far too many. `--tag emergency` with one `--entity` finds a mitigation-side seam: the findings that name that function and any emergency-response function. `--brief` keeps entries short.
- [check-pack](../commands/check-pack.md) with `--strict` and [pack](../commands/pack.md) check and render the pack.

## What you get

`interface-learnings.html` and `.md`:

- a matrix of the top pairs, with their shared findings and causal mentions;
- one section per interface, named by the pair with the lower ID first (for example `f02-f06`): the seam, what went wrong, why neither side saw it, a learning for each side, and a joint fix as a recommendation with its control tier, an indicator both sides can see, an owner on one side and a co-owner on the other;
- at least one interface on the mitigation side (detection, isolation, emergency command) when the evidence supports one;
- **Joint-review agenda:** a table for the meeting the two sides hold (interface, roles who meet, agenda item, evidence to bring, decision sought);
- **Who must meet whom:** a closing list.

## Worked example (Hazira)

`interfaces` found 125 pairs across 17 entities. The top pair was F01 Operations & Control Room with F02 Mechanical Maintenance (71 shared findings, 391 cross-entity causal mentions).

For the seam between maintenance and stores, `select --entity F02 F06 --entity-mode all --brief` returned 27 findings: the ones that name both Mechanical Maintenance and Materials Management. That small, focused set is what the skill reads to write the seam, for example how the locally bought O-rings reached the job.

These counts are from the base classification, before the resolution pass. After you place the remaining roles, or add an overlay, they change: on Hazira the india-process-site overlay alone moves F09b Emergency Planning & Command from 16 to 43 findings.

## Related skills

- [cluster-learning-dossier](cluster-learning-dossier.md): S6 is this analysis for one function.
- [supply-chain-contractor-learnings](supply-chain-contractor-learnings.md): the supply interface in depth.
- [manager-coach](manager-coach.md): agrees the interfaces with the managers who own them.
