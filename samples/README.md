# Sample ProbeMatrix exports

Download an export from a sub-folder, install the plugin, and ask your agent to run the Learnings Coach on it.

| Sample | Event | Source of evidence | Findings |
|---|---|---|---|
| *(to be added)* | | | |

## What a sample contains

Only the sheets the coach reads: `Incident Summary`, `Identified Findings`, `Evidence Links`, `Causal Chain`, `Analysis Statistics`. See [`export-schema.md`](../skills/learnings-coach/references/export-schema.md).

## Rules for adding a sample

1. The incident is **public record** (for example a published regulator or enquiry report), and you have the right to publish an analysis of it.
2. The export is **de-identified to roles**: no personal names, staff numbers or contact details.
3. Prepare it with `tools/make-public-sample.py`. The name scan must return **zero hits**.
4. Add a `README.md` in the sample folder stating: the public source, what the ProbeMatrix analysis had access to (desk analysis of the published report, no site access or interviews), whether the source report's own recommendations were part of the evidence pack (a *sighted* analysis), and any corrections made to the summary sheet.
