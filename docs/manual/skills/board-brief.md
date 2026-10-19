# board-brief

A board-level briefing for directors and the board's safety or risk committee. It says what the investigation reveals about governance, risk oversight and assurance, gives the questions directors should ask management, and describes what good assurance evidence would look like. Two to three pages.

## What it is for

- A board paper or a board safety committee briefing.
- Governance lessons and oversight questions.
- "What should the board ask?"

Directors do not manage the site. They oversee whether management's systems work and whether the assurance they receive is true, so this learning is about oversight and assurance, not operations.

## How to start it

- "Prepare a board briefing with the questions directors should ask."
- "What does this investigation say about our governance and assurance? Write it for the board safety committee."
- "Give me eight to twelve board questions, with what good evidence would look like."

## What it needs

- A workspace with `clusters.json`.
- The profile, the precursor candidates and the assurance findings, which the skill gathers.

## Engine commands and flags

```bash
pmlc profile <ws>
pmlc select <ws> --level 4 --top-rated --brief
pmlc select <ws> --tag assurance --level 3 4 --brief   # audit and assurance findings
pmlc select <ws> --preset board-brief                  # the two select calls above at once
pmlc timeline <ws> --before incident                   # signals that existed before the event
pmlc check-pack <ws> <run>/outputs/board-brief.json
pmlc pack <ws> <run>/outputs/board-brief.json
```

- [profile](../commands/profile.md) gives the shape of the investigation.
- [select](../commands/select.md): `--level 4` the Organisational Influences level; `--top-rated` the strongest findings; `--tag assurance` every function tagged assurance (HSE, process safety and audit in the default list); `--level 3 4` adds Supervision; `--brief` short entries.
- [timeline](../commands/timeline.md) with `--before incident` gives the signals before the event.
- [check-pack](../commands/check-pack.md) and [pack](../commands/pack.md) render the pack. The pack's scope is levels 3 and 4 at the top rating.

## What you get

`board-brief.html` and `.md`:

1. what happened, and why it matters to the board (one paragraph);
2. three to five governance learnings: assurance that did not detect, signals that did not escalate, risk accepted without authority, resources;
3. eight to twelve **questions for directors to ask**, each with why it matters and what good evidence looks like, mixing this site, all sites and the quality of assurance;
4. **assurance the board should request**, as a request to management, not a plan;
5. three to five **indicators** for the board dashboard.

The tone is neutral and factual: no blame of management or staff, and roles only.

## Worked example (Hazira)

`profile` showed 308 of 436 findings (71%) at the Supervision and Organisational levels. `select --level 4 --top-rated --brief` returned 47 findings and `--tag assurance --level 3 4 --brief` returned 69. With `--preset board-brief:top-l4 --budget-chars 20000`, `select` kept 34 findings and reported `Dropped for budget: 13 findings (lowest kept rating 4)`.

A short Hazira board pack written for this manual passed `check-pack` with the line `OK: 3 sections, 3 items, 6 cited IDs` and two warnings: the coverage warning (`cites 3 of 101 relevant findings (under a quarter)`) and `no handling block: rendered as draft (internal)`. Its page carries the DRAFT ribbon and the line "Draft because: the investigation status is in progress; no finding is marked as edited by a person".

These counts are from the base classification, before the resolution pass. After you place the remaining roles, or add an overlay, the tag and level counts can change: on Hazira the india-process-site overlay alone moves F09b Emergency Planning & Command from 16 to 43 findings.

## Related skills

- [top-management-brief](top-management-brief.md): the executive committee's version.
- [auditor-assurance-pack](auditor-assurance-pack.md): the independent checks behind section 4.
- [precursor-timeline](precursor-timeline.md): the signals that existed before the event.
- Recipe: [Brief the board](../Workflows-and-recipes.md#brief-the-board).
