# compliance-crosswalk

Which requirements of a management-system framework the learnings of an investigation speak to, and what the organisation must still show. The skill maps the Learnings Register onto ISO 45001, OSHA PSM, the 20 CCPS Risk Based Process Safety elements, Seveso III, ICMM critical control management, the Indian regimes or the organisation's own elements. The engine sets each requirement's status from the register; the skill then explains, requirement by requirement, what the most relevant learnings show. It is an aid to assurance, not a compliance opinion: it never says a site conformed or did not.

## What it is for

- "Which ISO 45001 clauses does this investigation give us evidence for?"
- "Map the learnings onto the RBPS elements."
- Preparing for a certification visit, a surveillance audit or an internal audit of the management system.
- Seeing which requirements the organisation must evidence from its own records, because the learnings do not reach them.

## How to start it

- "Our ISO 45001 audit is next month: which clauses do these learnings speak to?"
- "Give me a crosswalk of the learnings against the 20 RBPS elements."
- "Map this register onto our own management-system elements" (with a CSV of the elements).

The skill asks one question, "Which framework?": `iso45001`, `psm`, `rbps`, `seveso`, `icmm`, `india`, or a company system CSV.

## What it needs

- A workspace from [learnings-coach](learnings-coach.md), and the Learnings Register from [learnings-register](learnings-register.md). The crosswalk maps learnings, not findings, so the register comes first.
- Optional: the organisation's `adoption.csv` and `distribution.csv` (from [templates](../commands/templates.md)). When either has rows, ISO 45001 7.3 and 7.4 and PSM (m)(6) move up one step and name the file.
- Optional: a CSV of the organisation's own elements, with the columns `id,title` and an optional `topics` pattern.

## Engine commands and flags

```bash
pmlc crosswalk <ws> --framework iso45001                    # the summary: status and learnings per requirement
pmlc crosswalk <ws> --framework iso45001 --table-item       # the table item to paste, one per framework
pmlc crosswalk <ws> --framework rbps --table-item
pmlc crosswalk <ws> --system-csv <org-elements.csv> --table-item   # the organisation's own elements
pmlc crosswalk <ws> --framework rbps --json                 # rows with the learnings and cites behind each
pmlc check-pack <ws> <run>/outputs/compliance-crosswalk.json --strict
pmlc pack <ws> <run>/outputs/compliance-crosswalk.json
pmlc pack <ws> <run>/outputs/compliance-crosswalk.json --format docx        # a Word copy
pmlc pack-xlsx <ws> <run>/outputs/compliance-crosswalk.json --kind table    # the crosswalk tables in Excel
```

- [crosswalk](../commands/crosswalk.md) gives each requirement one status: `evidenced here` when a register learning's `clauses` names it, `partly` when only the requirement's topic words match a learning's text, and `needs organisation evidence` otherwise. It never sets `not applicable`; that is the organisation's call. `--table-item` prints the table (id `crosswalk-<framework>-table`) with `row_cites`, ready to paste unchanged.
- [check-pack](../commands/check-pack.md) with `--strict` checks the pack against its profile, including the fixed banner. In this pack the legal-judgment words of rule JC5 ("breach", "liable", "failed to comply") are errors, not warnings: the pack describes the gap against a requirement and leaves legal conclusions to the competent authority.
- [pack](../commands/pack.md) renders it, and [pack-xlsx](../commands/pack-xlsx.md) with `--kind table` writes the tables to Excel.

## What you get

`compliance-crosswalk.html` and `compliance-crosswalk.md`, with these sections:

- **banner:** the fixed sentence "Aid to assurance, not a compliance opinion.";
- **crosswalk-&lt;framework&gt;:** one table per chosen framework, up to three, pasted from the engine: Requirement, Status, Evidence here (the `LR-nn` ids), Organisation must show, and the cited findings;
- **by-element:** up to twelve learnings, each naming the requirement it speaks to (`clauses`), the register learning (`LR-nn`) and what the organisation must still show from its own records;
- **unverified:** which rows carry "(unverified)", because their ids and titles were not checked against the primary text (left out when every row is verified).

The pack carries no owners or due dates. The Word copy suits the audit file; the Excel copy suits working through the rows.

## Worked example (Hazira)

On the Hazira sample register, `crosswalk --framework iso45001` printed 23 clauses: 17 `partly` and 6 `needs organisation evidence` (among them 5.4 worker consultation, 7.3 awareness and 9.3 management review). `--framework rbps` printed the 20 elements: 16 `partly` and 4 `needs organisation evidence` (process safety culture, workforce involvement, stakeholder outreach, management review). No requirement is `evidenced here`, because no learning in the sample register carries `clauses` yet.

The worked pack, `samples/2020-09-24-hazira-gas-release-fire/outputs/compliance-crosswalk.json` in the repository, pastes both tables and writes ten `by-element` learnings, among them RBPS management of change (LR-06: the procedure had not been used since 2018), emergency management and ISO 45001 8.2 (LR-07: no isolation criteria or delegated authority) and ISO 45001 10.2 (LR-17: measured wall loss with no corrective plan). Its `unverified` paragraph notes that 15 of the 23 ISO rows and 16 of the 20 RBPS rows are unverified.

## Related skills

- [auditor-assurance-pack](auditor-assurance-pack.md): audit test points, sampling and evidence requests, grouped by the same framework.
- [learnings-register](learnings-register.md): the learnings themselves, and the `clauses` column that makes a row `evidenced here`.
