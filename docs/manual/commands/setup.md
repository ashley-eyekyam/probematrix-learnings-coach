# setup

## What it does

Runs the first six steps of a run in one command: [ingest](ingest.md), [classify](classify.md), [profile](profile.md) (written to `profile.md` in the workspace, after classify so it carries the F99, T9 and tier flags), [causal](causal.md), [timeline](timeline.md) and [interfaces](interfaces.md). It stops at the first step that fails and prints one summary: the finding and evidence counts, the unresolved roles, the profile's data-quality flags, the workspace path and the next step.

## When to use it

At the start of every run, instead of typing the six commands. The individual commands stay available for re-running one step.

## Synopsis

```text
pmlc setup xlsx --slug SLUG [--date DATE] [--root ROOT] [--force] [--strict] [--redact MAP.json] [--overlay NAME_OR_PATH] [--industry NAME]
```

## Arguments

| Argument | What it is |
|---|---|
| `xlsx` | The ProbeMatrix findings export |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--slug` | `<site>-<event>` | required | The run folder name, as for ingest |
| `--date` | `YYYY-MM-DD` | the summary sheet's Date | Incident date |
| `--root` | folder | the export's folder | Folder that holds `pmlc-runs/` |
| `--force` | none | off | Overwrite an existing workspace |
| `--strict` | none | off | Exit 1 when a required column is missing |
| `--redact` | file | none | JSON `{name: role}` applied at ingest |
| `--overlay` | name or path | none | Role overlay for classify |
| `--industry` | name | none | Industry reference pack for classify, for example `process`. Setup prints `Industry reference: process (method reference, not evidence)`. See [classify](classify.md) |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E setup hazira/export.xlsx --slug hazira-gas-release-fire
```

The last line reads `Next: PMLC plan` followed by the workspace path and a workflow name; it is text only.

## Common problems

- **"setup stopped at ingest".** The export is not a findings export (for example a CAPA Planner workbook), or the run folder exists: add `--force`.

## Related

[ingest](ingest.md), [classify](classify.md), [check-all](check-all.md)
