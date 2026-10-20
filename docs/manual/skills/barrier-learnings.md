# barrier-learnings

Which safety barriers and controls failed: prevention barriers before the loss of control, and mitigation barriers after it. For each barrier it gives the owner, its state on the day, how it degraded, and how strong the fix should be on the hierarchy of controls, with a leading indicator.

## What it is for

- Barriers, controls and defences, and bow-tie style learning.
- Critical controls, and "why didn't our safeguards work?"
- Recommendations stronger than retraining.

## How to start it

- "Which barriers failed in this event, and how strong should the fixes be?"
- "Give me the critical controls to verify first, with leading indicators."
- "List the prevention and mitigation barriers so we can draw a bow-tie."

## What it needs

- A workspace with `clusters.json` (owners come from the clusters).
- The incident narrative in `incident.json`, which `ingest` writes.

## Engine commands and flags

```bash
pmlc select <ws> --top-rated --brief
pmlc select <ws> --preset barrier-learnings     # the same call, as the skill's preset
pmlc table-item <ws> hoc --pack <run>/outputs/barrier-learnings.json   # control-tier counts of the fixes
pmlc check-pack <ws> <run>/outputs/barrier-learnings.json --strict
pmlc pack <ws> <run>/outputs/barrier-learnings.json
```

- [select](../commands/select.md): `--top-rated` keeps the findings at the workspace's top rating, and `--brief` keeps entries short.
- [table-item](../commands/table-item.md) `hoc` with `--pack` counts the pack's fixes per control tier, so the share above the administrative tier is computed, not estimated.
- [check-pack](../commands/check-pack.md) with `--strict` and [pack](../commands/pack.md) check and render the pack. The pack's scope is `{"min_rating": "top"}`, so its coverage is measured against the top-rated findings. `check-pack` also checks the `clauses` on the critical controls (`ICMM-CCM-8`, `ICMM-CCM-9`, `SEVESO-AnnexIII(vi)`) against the standards crosswalk.

Barrier names, types, states and control tiers come from one shared vocabulary, `barriers-and-controls.md`, so a barrier means the same thing in every pack. If the organisation has a barrier or critical-control register (a CSV with an id and a name), the agent gives each barrier the matching `barrier_id` and lists the barriers it could not map.

## What you get

`barrier-learnings.html` and `.md`:

- **Barriers:** up to twelve, grouped as Prevention or Mitigation. Each gives the barrier, its type (active, passive, procedural or behavioural), its owner, its state (absent, degraded, defeated, worked partly or worked), how it degraded (or "[GAP]" where the export does not say), the fix with its control tier, a leading indicator, the organisation's `barrier_id` when mapped, and the evidence.
- **Summary:** which barriers carried the most weight, whether failures clustered on one side, and the share of fixes above the administrative tier.
- **Critical controls to verify first:** a ranked list for the owners, with ICMM critical-control and Seveso III clauses where the evidence touches them.
- **Barriers not in the organisation's register:** only when a barrier register was supplied.

The `barrier` items can be handed to a bow-tie tool.

## Worked example (Hazira)

`select --top-rated --brief` returned 150 findings at rating 4. Among them are barriers on both sides:

- Prevention: return to service after a gasket replacement without a design-pressure test (FND-3AB996FC, evidence EVD-2894).
- Mitigation: emergency isolation valves that could be worked only locally, with no remote operation from the control room (FND-7D28BE30, EVD-3932); and a gas detection system not linked to automatic shutdown or suppression (FND-119E6CF7, EVD-3452).

## Related skills

- [engineering-integrity-learnings](engineering-integrity-learnings.md): the technical side of each barrier.
- [emergency-response-learnings](emergency-response-learnings.md): the mitigation barriers in response order.
- [auditor-assurance-pack](auditor-assurance-pack.md): how to test the critical controls at other sites.
