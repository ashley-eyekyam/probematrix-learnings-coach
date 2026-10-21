# board-brief

A board paper for directors and the board's safety or risk committee. It says what the investigation reveals about governance, risk oversight and assurance, puts the ask of the board on the cover, gives the questions directors should ask management, and describes what good assurance evidence would look like. A cover page, two to three pages of body, and the questions as the annex.

## What it is for

- A board paper or a board safety committee briefing.
- Governance lessons and oversight questions.
- "What should the board ask?"

Directors do not manage the site. They oversee whether management's systems work and whether the assurance they receive is true, so this learning is about oversight and assurance, not operations. For the executive committee's decisions, use [top-management-brief](top-management-brief.md).

## How to start it

- "Prepare a board paper with the questions directors should ask."
- "What does this investigation say about our governance and assurance? Write it for the board safety committee."
- "Were the earlier audit recommendations acted on? Give the board the questions to ask."

## What it needs

- A workspace with `clusters.json` (`setup` makes both).
- Optional: the Learnings Register, whose board-level learnings the brief reuses with their `LR-nn` ids, and the organisation's `adoption.csv`, which gives the management response status.

## Engine commands and flags

```bash
pmlc select <ws> --level 4 --top-rated --brief
pmlc select <ws> --tag assurance --level 3 4 --brief    # audit and assurance findings
pmlc select <ws> --text "recommendation|alert|overdue|repeat|earlier|previous" --level 3 4 --top-rated --brief
pmlc select <ws> --preset board-brief                   # the three select calls above at once
pmlc register-items <ws> --tier T5                      # the register's board-level learnings
pmlc timeline-item <ws> --before incident --top 8       # signals that existed before the event
pmlc table-item <ws> adoption                           # management's response to each learning
pmlc check-pack <ws> <run>/outputs/board-brief.json --strict
pmlc pack <ws> <run>/outputs/board-brief.json
pmlc pack <ws> <run>/outputs/board-brief.json --format docx --layout paper   # the board paper
```

- [select](../commands/select.md): `--level 4` the Organisational Influences level; `--top-rated` the strongest findings; `--tag assurance` every function tagged assurance (HSE, process safety and audit in the default list); `--level 3 4` adds Supervision; `--text` finds earlier alerts, recommendations and overdue items; `--brief` short entries.
- [register-items](../commands/register-items.md) with `--tier T5` lists the register's learnings for corporate leadership and the board.
- [timeline-item](../commands/timeline-item.md) with `--before incident` gives the signals before the event as a ready timeline item.
- [table-item](../commands/table-item.md) `adoption` turns `adoption.csv` (from [templates](../commands/templates.md)) into the management response table.
- [check-pack](../commands/check-pack.md) with `--strict` and [pack](../commands/pack.md) render the pack. The pack's scope is levels 3 and 4 at the top rating.

## What you get

`board-brief.html` and `.md`:

1. the **ask of the board** on the cover: to note, to request assurance, or to approve;
2. what happened, and why it matters to the board;
3. up to five governance learnings: assurance that did not detect, signals that did not escalate, risk accepted without authority, resources;
4. the **management response status**, when the organisation has filled in `adoption.csv`;
5. up to twelve **questions for directors to ask**, each with why it matters and what good evidence looks like, including whether earlier alerts and recommendations were acted on;
6. **assurance the board should request**, with a requested reporting date for the board to set;
7. up to five **indicators** for the board dashboard;
8. optionally, the **governance duties touched**: the board-reporting frameworks the learnings bear on (such as UK Corporate Governance Code Provision 29 or Companies Act 2013 s.134), with no legal conclusions;
9. a reminder that minuted questions need tracked answers.

The tone is neutral and factual: no blame of management or staff, and roles only. The skill's default sharing class is external: a copy for anyone outside the organisation follows [Review and sharing](../Review-and-sharing.md).

**Formats.** `--format docx --layout paper` (see [pack](../commands/pack.md)) also writes the **board paper**: `board-brief.docx`, `board-brief.paper.docx` and `board-brief.paper.html`. The paper has a cover with the status and reading time, "Decisions requested" with the bottom line, numbered paragraphs, Annex A for the questions and Annex B for the assurance table and indicators. Section order in the JSON stays as above; the layout moves the questions to the annex.

## Worked example (Hazira)

On the base classification, `select --level 4 --top-rated --brief` returned 47 findings, `--tag assurance --level 3 4 --brief` returned 69, and the earlier-warnings `--text` call returned 40. With the sample register in the outputs folder, `register-items --tier T5` gave 12 learnings, and `timeline-item --before incident --top 8` gave 8 dated signals. With no `adoption.csv`, `table-item adoption` prints one row, "No adoption record yet", so the brief leaves the management response section out and says so in its limits.

These counts are from the base classification, before the resolution pass. After you place the remaining roles, or add an overlay, the tag and level counts can change.

## Related skills

- [top-management-brief](top-management-brief.md): the executive committee's decisions.
- [auditor-assurance-pack](auditor-assurance-pack.md): the independent checks behind the assurance request.
- [precursor-timeline](precursor-timeline.md): the signals that existed before the event.
- Recipe: [Brief the board](../Workflows-and-recipes.md#brief-the-board).
