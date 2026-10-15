# Sample ProbeMatrix exports

Download an export from a sub-folder, install the plugin, and ask your agent to run the Learnings Coach on it.

| Sample | Event | Source of evidence | Findings |
|---|---|---|---|
| *(to be added)* | | | |

## What a sample contains

Only the sheets the coach reads: `Incident Summary`, `Identified Findings`, `Evidence Links`, `Causal Chain`, `Analysis Statistics`. See [`export-schema.md`](../skills/learnings-coach/references/export-schema.md).

## Folder layout (required)

```
samples/
  <YYYY-MM-DD>-<site>-<event>/                 e.g. 2020-09-24-hazira-gas-release-fire
    README.md
    <slug>_probematrix-findings.xlsx           from tools/make-public-sample.py --slug <slug>
    outputs/                                   copied from your pmlc-runs/<slug>/outputs/ (optional)
      learnings-register.json / .xlsx / .md
      organisation-learning-map.html
      <audience packs>.md
```

The slug is the same one `pmlc.py ingest --slug` used for your run, so a contributed folder mirrors the run folder. Do not contribute `workspace/`; anyone can rebuild it from the export. `python3 skills/learnings-coach/scripts/pmlc.py check-samples` checks the layout, and the test suite runs it. Run with no argument, `check-samples` also reports untracked local folders you keep in `samples/` for testing; only tracked folders must pass before a pull request.

## Rules for adding a sample

1. The incident is **public record** (for example a published regulator or enquiry report), and you have the right to publish an analysis of it.
2. The export is **de-identified to roles**: no personal names, staff numbers or contact details.
3. Prepare it with `tools/make-public-sample.py --slug <slug>`. The name scan must return **zero hits**. Run `pmlc.py scan-names <names-file> samples/<slug>/outputs` too, and get zero hits, before adding outputs.
4. Add a `README.md` in the sample folder stating:
   - the public source;
   - what the ProbeMatrix analysis had access to (desk analysis of the published report, no site access or interviews);
   - whether the source report's own recommendations were part of the evidence pack (a *sighted* analysis);
   - any corrections made to the summary sheet;
   - whether the learnings are draft (investigation still in progress) or reviewed.
