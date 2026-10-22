# supply-chain-contractor-learnings

Learning for procurement, stores, materials management, vendors, original equipment manufacturers (OEMs) and contractors. It covers part specifications and substitutions, local sourcing without quality control, OEM support for ageing equipment, vendor documents, contractor work control, agency or outsourced roles, and a briefing for the contractor workforce.

## What it is for

- "What should procurement, stores, the supply chain, vendors, OEMs or contractors learn?"
- A supplier or contractor briefing.
- Input to a spares policy.
- Contractor-management lessons after an incident, and what contractor crews should be told.

The pack is often shared outside the organisation, so the skill defaults to the external sharing class (`share_default: external`); see [Review and sharing](../Review-and-sharing.md).

## How to start it

- "What should procurement and stores learn from this investigation?"
- "Trace how the substitute part reached the job, with each decision point."
- "Prepare a contractor briefing from this event, without blaming the contractor."

## What it needs

- `clusters.json`. The skill selects the functions tagged `supply` or `contractor`: in the default list F06 Materials Management, F16 Vendors, OEMs & Suppliers, and F17 Contractors.
- Optional: the Learnings Register (entries owned by a supply or contractor function, with their `LR-nn` ids).

## Engine commands and flags

```bash
pmlc select <ws> --tag supply contractor --brief
pmlc select <ws> --text "procure|stores|spare|OEM|vendor|supplier|local|substitut|contract|agency|outsourc" --brief
pmlc select <ws> --preset supply-chain-contractor-learnings   # the two calls above at once
pmlc check-pack <ws> <run>/outputs/supply-chain-contractor-learnings.json --strict
pmlc check-pack <ws> <run>/outputs/supply-chain-contractor-learnings.json --share external   # before a copy leaves
pmlc pack <ws> <run>/outputs/supply-chain-contractor-learnings.json
pmlc pack <ws> <run>/outputs/supply-chain-contractor-learnings.json --format email   # .email.html and .email.txt
pmlc strings extract <ws> <run>/outputs/supply-chain-contractor-learnings.json --to csv --lang hi   # translation, when asked
```

- [select](../commands/select.md): `--tag supply contractor` every function with either tag; `--text` a regular expression over the finding text (supply words); `--brief` short entries.
- [check-pack](../commands/check-pack.md) with `--strict` checks the pack against its profile; with `--share external` it applies the external language rules. [pack](../commands/pack.md) renders the pack.
- [pack](../commands/pack.md) `--format email` writes a self-contained digest (`.email.html`, and `.email.txt` for plain-text mail) for the contract owner to send to a vendor or contractor. After a person's sign-off for external sharing, `--share external --embed summary` writes the masked `.external.` copies of the page and the email.
- [strings](../commands/strings.md) carries the briefing into the contractor workforce's language; a fluent speaker checks it, and the translation is signed off on its own.
- When the pack will leave the organisation, run [check-language](../commands/check-language.md) with `--share external` and `--orgs FILE`: company names become errors (JC9).

## What you get

`supply-chain-contractor-learnings.html` and `.md`:

1. **how the part (or service) reached the job**: a timeline of decision points, each with the role that took it, and "No record" where there is none;
2. learnings for **procurement and stores**, **engineering at the supply interface**, **vendors and OEMs**, and **contractors and outsourced roles**, only where the evidence supports them;
3. a **briefing for contractor crews**, when the findings involve contractor or agency workers: what the host's supervisor or permit issuer covers with the crew before and during the work;
4. **recommendations** with control tier and indicator, such as "% of critical spares with an approved specification".

When the pack is shared, it uses functions ("the maintenance contractor"), never company names.

**Contractor just-culture rule.** The host organisation's system owns contractor and vendor learnings: how it selects, briefs, supervises and works with them. The pack writes "the contractor's task was not covered by the host's permit briefing", not "the contractor failed". If the export has few supply-chain findings, the pack says so and stays short.

## Worked example (Hazira)

`select --tag supply contractor --brief` returned 35 findings: F06 Materials Management has 29, F16 Vendors has 7 and F17 Contractors has 2, and some findings carry more than one. The supply-words search returned 178. With only two F17 findings, the contractor-crew briefing is short. The timeline of the part would start from the evidence that "there is no record of date or authority of the decision to switch over from OEM supplied gasket to locally purchased gasket" (FND-B86F67F0, EVD-8645).

These counts are from the base classification, before the resolution pass. After you place the remaining roles, or add an overlay, they change: on Hazira the india-process-site overlay alone moves F09b Emergency Planning & Command from 16 to 43 findings.

## Related skills

- [interface-learnings](interface-learnings.md): the maintenance and stores seam (27 shared findings on Hazira).
- [engineering-integrity-learnings](engineering-integrity-learnings.md): technical approval of substitutes.
- [frontline-learning-cards](frontline-learning-cards.md): the cards contractor crews keep (its contractor-workforce option).
- [Review and sharing](../Review-and-sharing.md): before a briefing goes to a vendor or contractor.
