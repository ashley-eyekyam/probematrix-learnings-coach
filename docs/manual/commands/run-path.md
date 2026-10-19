# run-path

## What it does

Prints where a run lives and two facts the skills need: the run folder, the workspace, the outputs folder, the run's slug, the top rating in the export and the incident date. Skills use it so they never have to guess a path or a rating scale.

## When to use it

When you know the workspace and need the outputs folder (to save a pack JSON), or when a skill needs the top rating for `select --top-rated`.

## Synopsis

```text
pmlc run-path ws
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `-h`, `--help` | none | | Show the flags and stop |

run-path has no other flags.

## Examples

```bash
python3 $E run-path $WS
```

```text
run:       hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire
workspace: hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/workspace
outputs:   hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs
slug:      2020-09-24-hazira-gas-release-fire
top_rating: 4
incident_date: 2020-09-24
```

## Common problems

- **The paths are relative.** run-path prints paths the way you gave the workspace. Give an absolute workspace path to get absolute paths.
- **A legacy workspace.** A workspace made with `ingest --legacy-out` is outside the standard layout, so its outputs folder is not where the other commands look. Re-ingest with `ingest --slug`.

## Related

- [ingest](ingest.md) creates the run folder.
- [Files and folders](../Files-and-folders.md) explains the layout.
