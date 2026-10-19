# ingest

## What it does

Reads a ProbeMatrix findings export (`.xlsx`) and writes a **workspace**: a folder of JSON files that every other command reads. It keeps the findings, the evidence, the incident summary and a manifest that records where each file came from.

The workspace always goes in a strict run folder next to the export:

```text
<export folder>/pmlc-runs/<YYYY-MM-DD>-<site>-<event>/workspace/
<export folder>/pmlc-runs/<YYYY-MM-DD>-<site>-<event>/outputs/
```

The date is the incident date from the export's summary sheet (or `--date`). The site and event part is the `--slug` you give. While reading, it also:

- checks the columns against the expected export layout and prints a short fingerprint of what it found;
- cross-checks the number of findings against the export's Analysis Statistics sheet;
- refuses a CAPA Planner export, which is a different kind of file.

## When to use it

First, once per export. Run it again with `--force` when you get a newer export of the same investigation; then run [status](status.md) to see which derived files need to be rebuilt.

## Synopsis

```text
pmlc ingest xlsx [--slug SLUG | --out OUT | --legacy-out LEGACY_OUT] [--date DATE] [--root ROOT]
                 [--force] [--strict] [--redact MAP.json]
```

`--slug`, `--out` and `--legacy-out` are alternatives: give one of them.

## Arguments

| Argument | What it is |
|---|---|
| `xlsx` | The ProbeMatrix findings export, an `.xlsx` file |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--slug` | `<site>-<event>` | none | The run name after the date: lowercase words joined by hyphens, for example `hazira-gas-release-fire`. The usual choice |
| `--date` | `YYYY-MM-DD` | the summary sheet's Date | The incident date used in the run folder name. Use it when the export's date is missing or wrong |
| `--root` | folder | the export's folder | The folder that holds `pmlc-runs/` |
| `--out` | path | none | An explicit workspace path. It must still end in `pmlc-runs/<YYYY-MM-DD>-<site>-<event>/workspace` |
| `--legacy-out` | folder | none | Write the workspace to any folder (the layout before version 0.2). Not for new runs: other commands then cannot find the outputs folder on their own |
| `--force` | none | off | Overwrite a workspace that already exists in the run folder |
| `--strict` | none | off | Stop with exit code 1 when a required column is missing, instead of carrying on with a warning |
| `--redact` | `MAP.json` | none | A JSON object `{"name": "role"}`. Each name, and its usual variants (surname, initial and surname, honorific and surname), is replaced by the role everywhere in the workspace |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

Ingest the Hazira sample:

```bash
python3 $E ingest hazira/2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx --slug hazira-gas-release-fire
```

```text
Ingested 436 findings, 46 evidence items, 0 causal-chain rows -> hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/workspace
schema: fingerprint b2ea9b9179b3; missing: none; unknown: none
cross-check: Analysis Statistics agrees (436)
Run folder: hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire
  workspace: hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/workspace
  outputs:   hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs
```

Replace names with roles while reading. The map below names a person from a fictional list; the Hazira export names roles only, so nothing is replaced:

```bash
echo '{"R. K. Sharma": "the maintenance supervisor"}' > redact.json
python3 $E ingest hazira/2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx --slug hazira-gas-release-fire --force --redact redact.json
```

```text
Ingested 436 findings, 46 evidence items, 0 causal-chain rows -> hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/workspace
…
redacted 0 name occurrence(s) from the workspace
…
```

## Common problems

- **The workspace already exists.** Running the same ingest twice stops, to protect your work:

  ```text
  hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/workspace already holds a workspace. Pass --force to overwrite it.
  ```

  Add `--force` only when you mean to replace it. Your outputs folder is not touched.
- **The slug is not in the right form.** Use lowercase words and hyphens only:

  ```text
  slug must be lowercase words joined by hyphens, e.g. hazira-gas-release-fire (got 'Hazira Fire')
  ```

- **The date is not `YYYY-MM-DD`.** `--date 24-09-2020` gives `No valid incident date from --date: '24-09-2020'. Pass --date YYYY-MM-DD.`
- **`--out` is outside the standard layout.** It gives `--out must be <dir>/pmlc-runs/<YYYY-MM-DD>-<site>-<event>/workspace (got elsewhere/workspace). Use --slug instead, or --legacy-out for a non-standard folder.`
- **A CAPA Planner export.** The coach needs the investigation's findings export, not the corrective-action planner. Export "Identified Findings" from the investigation instead.
- **"missing: …" in the schema line.** The export is from a different ProbeMatrix version or was edited. The run carries on; check the [profile](profile.md) data-quality flags, or use `--strict` to stop instead.

## Related

- [profile](profile.md) and [classify](classify.md) come next.
- [status](status.md) shows what a re-ingest made stale.
- [Files and folders](../Files-and-folders.md) explains the run folder.
- [scan-names](scan-names.md) checks outputs for names after `--redact`.
