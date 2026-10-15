# ProbeMatrix findings export: what the Learnings Coach reads

A ProbeMatrix investigation can be exported to Excel. The Learnings Coach reads the sheets below and ignores the rest. Column names are matched exactly; missing optional columns are tolerated.

## Sheet: Identified Findings (required)

One row per finding instance.

| Column | Meaning | Used for |
|---|---|---|
| Finding ID | Unique ID (e.g. `FND-98A4D631`) | Every citation |
| Nanocode | Factor code in the four-level HFACS-based taxonomy (e.g. `OIR 1.1`) | Grouping, causal graph |
| Name | Factor name | Display |
| Level / Level Name | 1 Unsafe Acts · 2 Preconditions · 3 Supervision · 4 Organisational Influences | Depth analysis |
| Category / Subcategory | Taxonomy sub-category | Sub-division routing |
| Classification | e.g. `substantiated` | Status |
| Rating | Strength of causal contribution; higher is stronger (the app shows its highest rating as "Primary") | Prioritisation |
| Instance ID / Instance Label | Which occurrence of the factor, in words | Headline of the learning |
| Short Description | One-sentence finding | Summaries |
| AI Justification | Why the evidence supports the factor, quoting evidence IDs | Grounding |
| Causal Explanation | How the factor contributed, often naming other factor codes | Causal graph, interfaces |
| Individuals Involved | Comma-separated roles and entities, sometimes with qualifiers in parentheses | Learning Clusters |
| Linked Evidence | Comma-separated evidence IDs (`EVD-nnnn`) | Citations |
| Evidence to Collect, Key Questions, Suggested Interviews, Causal Hypothesis | Investigative follow-up; often empty in exports | investigator-coach can draft them |
| User Edited | Whether a human edited the AI's finding | Review status |

## Sheet: Evidence Links

One row per (factor code, evidence item) link: `Finding Code`, `Finding Name`, `Evidence ID`, `Evidence Type` (document, log_record, witness_statement, recording, physical_item, photograph…), `Relevance` (why this evidence supports the factor), `Specific Reference` (verbatim quote), `Evidence Description`.

Links are keyed by factor **code**, not finding ID. The engine joins them to findings on (code, evidence ID).

## Sheet: Incident Summary

Field/value pairs (incident number, title, type, date, location, severity, status…) and an `INCIDENT NARRATIVE` block. Check these fields for obvious errors before quoting them.

## Sheet: Causal Chain (optional)

`From Code`, `To Code`, `Relationship`, `Confidence`… when the investigator has built a causal map. Often empty; `pmlc.py causal` extracts links from the causal explanations instead.

## Other sheets

`Analysis Statistics`, `Personnel & Equipment` and any reference or collaboration sheets are not needed. Public sample files in this repo contain only the sheets above.
