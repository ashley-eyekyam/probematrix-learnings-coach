# run-manifest

## What it does

Updates `<run>/run-manifest.json`, the small record `ingest` writes beside the workspace. It holds the run's slug, the export's hash, the classification, the retention review date, the intended use and the jurisdictions. The export's own file name is never stored: `export_file` is always `<slug>.xlsx`.

When a retention review date is set, every pack, register and dashboard handling line gains `Retention review: <date>`. When a jurisdiction is set, it gains `Statutory report still required: <regimes>`, with the regimes taken from `skills/learnings-coach/references/jurisdictions.md`. This is a reminder, not legal advice: the organisation decides whether a report is owed.

## When to use it

After `ingest`, once you know who the learnings are for, which jurisdictions apply and when the run's data should be reviewed for deletion.

## Synopsis

```text
pmlc run-manifest ws [--intended-use TEXT] [--jurisdiction in,uk,us,eu] [--retention-review YYYY-MM-DD] [--classification internal|restricted|external|public]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder (the run manifest sits in its parent run folder) |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--intended-use` | text | unchanged | What the learnings are for |
| `--jurisdiction` | comma-separated `in`, `uk`, `us`, `eu` | unchanged | Jurisdictions whose statutory report may still be owed |
| `--retention-review` | `YYYY-MM-DD` | unchanged | The date to review whether to purge the run |
| `--classification` | `internal`, `restricted`, `external` or `public` | unchanged | The run's classification |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E run-manifest $WS --jurisdiction in --retention-review 2027-09-24
```

## Common problems

- **A legacy workspace.** A workspace made with `ingest --legacy-out` has no run folder, so no run manifest. Re-ingest into the standard layout.
- **Unknown jurisdiction.** Only `in`, `uk`, `us` and `eu` are accepted.

## Related

- [purge](purge.md) deletes the run's data and records it here.
- [status](status.md) shows the run manifest.
