# ProbeMatrix findings export: what the Learnings Coach reads

A ProbeMatrix investigation can be exported to Excel. The Learnings Coach reads the sheets below and ignores the rest. Column names are matched exactly; missing optional columns are tolerated.

`pmlc.py ingest` prints a `schema:` line with a fingerprint (12 hex characters over the sheet names and the three column headers) and lists missing and unknown columns. `--strict` exits 1 when one of `Finding ID`, `Level`, `Rating`, `Individuals Involved` or `Linked Evidence` is missing. A workbook with the CAPA Planner sheets (`Chapter Headers`, `Corrective Actions`, `Preventive Actions`, `Residual Risks`) is refused: it is not a findings export.

## Sheet: Identified Findings (required)

One row per finding instance.

| Column | Meaning | Used for |
|---|---|---|
| Finding ID | Unique ID (e.g. `FND-98A4D631`) | Every citation |
| Nanocode | Factor code in the four-level HFACS-based taxonomy (e.g. `OIR 1.1`) | Grouping, causal graph |
| Name | Factor name | Display |
| Level / Level Name | 1 Unsafe Acts · 2 Preconditions · 3 Supervision · 4 Organisational Influences | Depth analysis |
| Category / Subcategory | `Category` repeats the level name in the sample (all 436 rows); `Subcategory` is the taxonomy sub-category | Sub-division routing |
| Classification | e.g. `substantiated` | Status |
| Rating | Strength of causal contribution; higher is stronger (the app shows its highest rating as "Primary"). The scale is 1 to 5 in Analysis Statistics; the sample uses 2 to 4 | Prioritisation |
| Instance ID / Instance Label | Which occurrence of the factor, in words | Headline of the learning |
| Short Description | One-sentence finding | Summaries |
| AI Justification | Why the evidence supports the factor, quoting evidence IDs | Grounding |
| Causal Explanation | How the factor contributed, often naming other factor codes | Causal graph, interfaces |
| Individuals Involved | Comma-separated roles and entities, sometimes with qualifiers in parentheses | Learning Clusters |
| Linked Evidence | Comma-separated evidence IDs (`EVD-nnnn`) | Citations |
| Evidence to Collect, Key Questions, Suggested Interviews, Causal Hypothesis | Investigative follow-up; often empty in exports | investigator-coach can draft them |
| User Edited | Whether a human edited the AI's finding | Review status |
| Created At / Updated At | ISO timestamps (e.g. `2026-05-25T04:59:32.868Z`) of when the finding was created and last changed | Audit trail; not used in the learnings |

## Sheet: Evidence Links

One row per (factor code, evidence item) link: `Finding Code`, `Finding Name`, `Evidence ID`, `Evidence Type` (document, log_record, witness_statement, recording, physical_item, photograph…), `Relevance` (why this evidence supports the factor), `Specific Reference` (verbatim quote), `Evidence Description`.

Links are keyed by factor **code**, not finding ID. The engine joins them to findings on (code, evidence ID).

## Sheet: Incident Summary

A `Field | Value` table under section headers, then an `INCIDENT NARRATIVE` block. Check these fields for obvious errors before quoting them. Many are empty in an export.

- Core: `Incident Number`, `Incident Title`, `Incident Type`, `Date`, `Time`, `Location`, `Severity`, `Outcome`, `Investigation Status`, `Investigating Officer`
- CONSEQUENCE CLASSIFICATION: `Consequence Type`, `Persons Affected`, `Fatalities`, `Injuries`
- RISK ASSESSMENT: `Risk Rating`, `Potential Severity`, `Likelihood of Recurrence`
- REGULATORY REPORTING: `Reportable to Regulator`, `Regulatory Bodies`, `Regulatory Reference`
- LOCATION & CONTEXT: `Department`, `Area/Zone`, `Shift`, `Weather Conditions`, `Lighting Conditions`, `Supervisor at Time`, `Investigation Team`
- INVESTIGATION TIMELINE: `Due Date`, `Completed Date`, `Verification Required`

## Sheet: Causal Chain (optional)

Eleven columns: `Link ID`, `From Code`, `From Level`, `To Code`, `To Level`, `Relationship`, `Confidence`, `Basis`, `Evidence Support`, `User Confirmed`, `Notes`. Filled when the investigator has built a causal map. Often holds a single row, `No causal links found`; `pmlc.py causal` then extracts links from the causal explanations instead.

## Sheet: Analysis Statistics

Not a plain table. After the title rows comes a `Level | Level Name | Total Findings | Rating 1 … Rating 5` block with one row per level, then a `Total` row, then a `Category Distribution` block. `ingest` reads the level counts and the total and cross-checks the total against the findings it ingested (`cross-check: Analysis Statistics agrees (436)`, or a `warning:`). When the block is absent it prints a note and skips the check.

## Sheet: Collaboration Data (optional)

Present only when reviewers voted or commented. It has a `VOTES` block and a `COMMENTS` block; the votes are rows of `Finding ID | Vote | Reason`. `ingest` reads the votes into `incident.json` as `review_votes`, and they drive reviewer downgrades. The Hazira sample has no such sheet.

## Other sheets

`Personnel & Equipment` and any other reference sheets are not needed. The Hazira sample contains five sheets: Incident Summary, Identified Findings, Evidence Links, Causal Chain and Analysis Statistics.
