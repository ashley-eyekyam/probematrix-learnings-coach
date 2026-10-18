# Sample ProbeMatrix exports

Download an export from a sub-folder, install the plugin, and ask your agent to run the Learnings Coach on it.

| Sample | Event | Source of evidence | Findings |
|---|---|---|---|
| [`2020-09-24-hazira-gas-release-fire`](2020-09-24-hazira-gas-release-fire/) | Gas terminal release and fire, ONGC Hazira, 24 Sep 2020 | PNGRB Enquiry Committee report (desk analysis, sighted) | 436 (draft) |

## What a sample contains

Only the sheets the coach reads: `Incident Summary`, `Identified Findings`, `Evidence Links`, `Causal Chain`, `Analysis Statistics`. See [`export-schema.md`](../skills/learnings-coach/references/export-schema.md).

## Folder layout (required)

```
samples/
  <YYYY-MM-DD>-<site>-<event>/                 e.g. 2020-09-24-hazira-gas-release-fire
    README.md
    <slug>_probematrix-findings.xlsx           from tools/make-public-sample.py --slug <slug>
    <slug>_probematrix-report.pdf              the ProbeMatrix investigation report (optional)
    <slug>_official-report.pdf                 the official public report, unmodified (optional)
    outputs/                                   copied from your pmlc-runs/<slug>/outputs/ (optional)
      learnings-register.json / .xlsx / .md
      organisation-learning-map.html
      <audience packs>.md
```

The slug is the same one `pmlc.py ingest --slug` used for your run, so a contributed folder mirrors the run folder. Do not contribute `workspace/`; anyone can rebuild it from the export. `python3 skills/learnings-coach/scripts/pmlc.py check-samples` checks the layout, and the test suite runs it. Run with no argument, `check-samples` also reports untracked local folders you keep in `samples/` for testing; only tracked folders must pass before a pull request.

## Rules for adding a sample

1. The incident is **public record** (for example a published regulator or enquiry report), and you have the right to publish an analysis of it.
2. **Material may be included unmodified.** The official public report and ProbeMatrix material (export, report, outputs) go in as they are; no name scan is required. Generated learnings still follow just culture (roles only, no blame). De-identification tooling (`pmlc.py scan-names`, and `--names` on `tools/make-public-sample.py`) remains available for an organisation's own runs.
3. Prepare the export with `tools/make-public-sample.py --slug <slug>`. It keeps the sheets the coach reads and applies any `--set` overrides. Without `--names` it skips the name scan and says so.
4. Add a `README.md` in the sample folder stating:
   - the public source;
   - what the ProbeMatrix analysis had access to (desk analysis of the published report, no site access or interviews);
   - whether the source report's own recommendations were part of the evidence pack (a *sighted* analysis);
   - any corrections made to the summary sheet;
   - whether the learnings are draft (investigation still in progress) or reviewed.
