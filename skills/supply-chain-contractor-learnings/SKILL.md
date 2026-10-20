---
name: supply-chain-contractor-learnings
description: Produces learning for procurement, stores, materials management, vendors, OEMs, contractors and contractor crews from a ProbeMatrix investigation export - part specifications and substitutions, local sourcing without quality control, OEM support for ageing equipment, vendor documents, contractor work control, agency or outsourced roles, and a briefing for the contractor workforce. Use when someone has a ProbeMatrix export and asks what procurement, stores, the supply chain, vendors, OEMs or contractors should learn, or wants a supplier or contractor briefing, spares policy input, or contractor-management lessons after an incident.
---

# Supply Chain & Contractor Learnings

Audience: the Learning Clusters tagged `supply` or `contractor` (in the default taxonomy F06 materials
management, F16 vendors, OEMs and suppliers, F17 contractors), plus any agency roles named in the findings.
This pack is often shared outside the organisation (`share_default: external`).

## Before you start

Engine: `PMLC` as defined in `skill-common.md` §1 (needs the `learnings-coach` skill installed alongside it).

- Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions).
- Needs: **workspace** and **clusters**.
- Read `learnings-coach/references/learning-principles.md`.
- **Start from the register if present.** In `<run>/outputs/learnings-register.json`, take the entries whose
  `owner_entity` is a `supply` or `contractor` entity: keep their wording and carry `learning: "LR-nn"`.

## Gather

```bash
PMLC select <ws> --tag supply contractor --brief         # the supply and contractor functions' findings
PMLC select <ws> --text "procure|stores|spare|OEM|vendor|supplier|local|substitut|contract|agency|outsourc" --brief
```

## Write

Pack `<run>/outputs/supply-chain-contractor-learnings.json` (shape: `learnings-coach/references/pack-schema.md`),
`"scope": {"tags": ["supply", "contractor"]}`.

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | The supply-chain and contractor learnings, one line each | `bottom_line` | up to 5 |
| 1 | `path` | How the part (or service) reached the job | One event per decision point from need to installed item: `received_by` = the role that decided, `response` = "No record" where there is none | `timeline` | 1 |
| 2 | `learnings` | Learnings | `group` = Procurement and stores / Engineering at the supply interface / Vendors and OEMs / Contractors and outsourced roles (only the groups the evidence supports) | `learning` | up to 10 |
| 3 | `contractor-briefing` | Briefing for contractor crews | What the contractor workforce should be told or asked before and during the work (permit briefing, hold points, who to stop and ask), `when` = the point in the contract | `check` | optional, up to 6 |
| 4 | `recommendations` | Recommendations and indicators | change, `hoc_tier`, indicator (e.g. "% of critical spares with an approved specification", "substitutions approved through change control") | `recommendation` | up to 8 |

- **Procurement and stores:** specification, technical approval of substitutes, quality checks at receipt,
  storage and shelf-life, traceability. **Engineering at the supply interface:** who may approve a substitute,
  and how it is recorded (see `interface-learnings`). **Vendors and OEMs:** documents and support for legacy
  equipment; what to ask vendors for. **Contractors and outsourced roles:** the reporting lines, competence and
  supervision the findings question for contractor or agency staff (security, fire, inspection agencies).
- **Briefing for contractor crews.** Write it when the findings involve contractor or agency workers. It is what
  the host's supervisor or permit issuer covers with the crew, so it is the host's system that owns it.
- **Contractor just-culture rule.** The host organisation's system owns contractor and vendor learnings: its
  selection, briefing, supervision and interfaces. Write "the contractor's task was not covered by the host's
  permit briefing", not "the contractor failed".
- **No company names when shared.** When the pack goes outside the organisation, use the function ("the
  maintenance contractor", "the seal supplier"), never a company name; `check-language --share external` flags
  organisation names (JC9). See `skill-common.md` §7 before any external copy.

```json
{"kind": "timeline", "events": [{"date": "YYYY-MM", "text": "…", "received_by": "Stores/procurement officer",
 "response": "No technical approval recorded", "cites": ["FND-…"]}]}
```

## If the evidence is thin

- **Few supply-chain findings:** say so in a `limits` line and keep the pack short: one decision point and one
  learning are a valid pack.
- **No contractor or agency workers in the findings:** leave the contractor-briefing section out.
- `skill-common.md` §6 covers the rest.

## Not covered here

- Cards for the contractor crews to keep: `frontline-learning-cards` with its contractor-workforce option.
- The engineering side of specifications and substitution: `engineering-integrity-learnings`.
- Supplier pre-qualification questionnaires or contract terms: outside this skill.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/supply-chain-contractor-learnings.json --strict
PMLC pack <ws> <run>/outputs/supply-chain-contractor-learnings.json
```

- Before a copy leaves the organisation, also run `PMLC check-pack <ws> <run>/outputs/supply-chain-contractor-learnings.json --share external`
  and fix every error; sharing follows `skill-common.md` §7.
- Next step: `frontline-learning-cards` with the contractor-workforce option, for the contractor crews.
