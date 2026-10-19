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
pmlc check-pack <ws> <run>/outputs/barrier-learnings.json
pmlc pack <ws> <run>/outputs/barrier-learnings.json
```

- [select](../commands/select.md): `--top-rated` keeps the findings at the workspace's top rating, and `--brief` keeps entries short.
- [check-pack](../commands/check-pack.md) and [pack](../commands/pack.md) render the pack. The pack's scope is `{"min_rating": "top"}`, so its coverage is measured against the top-rated findings.

## What you get

`barrier-learnings.html` and `.md`:

- **Barriers:** one entry per barrier, grouped as Prevention or Mitigation. Each gives the barrier, its owner, its state (absent, degraded, defeated, worked partly or worked), how it degraded (or "[GAP]" where the export does not say), the fix with its control tier, a leading indicator and the evidence.
- **Summary:** which barriers carried the most weight, whether failures clustered on one side, and the share of fixes above the administrative tier.
- **Critical controls to verify first:** a ranked list for the owners.

The `barrier` items can be handed to a bow-tie tool.

## Worked example (Hazira)

`select --top-rated --brief` returned 150 findings at rating 4. Among them are barriers on both sides:

- Prevention: return to service after a gasket replacement without a design-pressure test (FND-3AB996FC, evidence EVD-2894).
- Mitigation: emergency isolation valves that could be worked only locally, with no remote operation from the control room (FND-7D28BE30, EVD-3932); and a gas detection system not linked to automatic shutdown or suppression (FND-119E6CF7, EVD-3452).

## Related skills

- [engineering-integrity-learnings](engineering-integrity-learnings.md): the technical side of each barrier.
- [emergency-response-learnings](emergency-response-learnings.md): the mitigation barriers in response order.
- [auditor-assurance-pack](auditor-assurance-pack.md): how to test the critical controls at other sites.
