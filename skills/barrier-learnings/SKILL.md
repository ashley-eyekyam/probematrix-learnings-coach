---
name: barrier-learnings
description: Analyse which safety barriers and controls failed in a ProbeMatrix investigation - prevention barriers before the event and mitigation barriers after it - who owned each, how it degraded, and how strong the fix should be on the hierarchy of controls, with leading indicators. Use when someone asks about barriers, controls, defences, bow-tie style learning, critical controls, "why didn't our safeguards work", or wants recommendations stronger than retraining.
---

# Barrier Learnings

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py`. Read `learnings-coach/references/output-style.md` (hierarchy of controls, leading indicators).

## Identify barriers

From the incident narrative (`<ws>/incident.json`) and the highest-rated findings (`PMLC select <ws> --top-rated --brief`), list the barriers that were supposed to stand between the hazard and the outcome:
- **Prevention side** (before loss of control): design and specification, maintenance and testing, inspection, procedures and permits, competence, change management.
- **Mitigation side** (after loss of control): detection, alarm, isolation, ignition control, emergency response, fire protection, escape and recovery.

## For each barrier

| Field | Content |
|---|---|
| Barrier | name and side |
| Owner | entity and tier (from the findings' clusters) |
| State on the day | absent / degraded / defeated / worked partly / worked |
| How it degraded | the L2–L4 findings behind its state, with dates if known |
| Fix | proposed control and its HoC tier |
| Leading indicator | how the owner will know the barrier is healthy |
| Evidence | finding and evidence IDs |

Do not declare a barrier effective or ineffective beyond what the evidence states. Use "[GAP]" where the export does not tell you.

## Learn

Summarise: which barriers carried the most weight, whether failures clustered on one side, and what share of proposed fixes are above the administrative tier. Give a short ranked list of "critical controls to verify first" for the owners.

## Output

Write the pack `<run>/outputs/barrier-learnings.json` (schema: `learnings-coach/references/pack-schema.md`), then:

```bash
PMLC check-pack <ws> <run>/outputs/barrier-learnings.json   # fix every problem it lists
PMLC pack <ws> <run>/outputs/barrier-learnings.json         # -> barrier-learnings.html (primary) and .md
```

Sections and the kinds that fill them:
- **Barriers:** one `barrier` per row of the table above, with `group` = "Prevention" or "Mitigation". The table's fields map like this:
  - Barrier → `barrier`, plus `type`
  - Owner → `owner`
  - State on the day → `state`
  - How it degraded → `failure_mode` (write "[GAP] …" where the export does not say)
  - Fix → `fix` and `hoc_tier`
  - Leading indicator → `indicator`
  - Evidence → `cites`
- **Summary:** `para`.
- **Critical controls to verify first:** `check` items, in ranked order.

Set `"scope": {"min_rating": "top"}`. Put data-quality corrections in `data_quality`, findings left out on purpose in `exclusions`, and same-condition findings in `supporting_cites`. For a bow-tie, hand the `barrier` items to a bow-tie tool.

```json
{"kind": "barrier", "group": "Prevention", "barrier": "…", "type": "prevention", "owner": "…", "state": "absent",
 "failure_mode": "…", "hoc_tier": "engineering", "fix": "…", "indicator": "…", "cites": ["FND-…"]}
```
