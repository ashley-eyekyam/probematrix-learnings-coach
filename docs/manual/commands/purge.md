# purge

## What it does

Deletes a run's `workspace/` and, unless you keep it, its `outputs/`. It never deletes `run-manifest.json`: it records `purged_on` and what was removed there.

It deletes nothing unless you pass `--yes`; without it, it lists what it would delete and exits 1. It refuses anything that is not a real run folder: the folder must be named `<YYYY-MM-DD>-<site>-<event>`, sit directly in a folder named `pmlc-runs`, and hold `workspace/manifest.json`. It refuses a run folder, workspace or outputs folder that is a symlink, and never follows a link out of the run folder.

## When to use it

When the retention review date has passed and the organisation has decided to remove the working data.

## Synopsis

```text
pmlc purge run [--keep outputs] [--yes]
```

## Arguments

| Argument | What it is |
|---|---|
| `run` | The run folder, `<dir>/pmlc-runs/<YYYY-MM-DD>-<site>-<event>` (not the workspace) |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--keep` | `outputs` | none | Keep the outputs folder |
| `--yes` | none | off | Really delete; without it nothing is deleted |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E purge hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire --keep outputs --yes
```

## Common problems

- **"refused: ... is not a run folder".** Give the run folder, not the workspace or a parent folder.
- **"refused: ... is a symlink".** Remove the link by hand, then run purge again.
- **Nothing happens.** Without `--yes` purge only lists what it would delete.

## Related

- [run-manifest](run-manifest.md) sets the retention review date.
- [Files and folders](../Files-and-folders.md) explains the layout.
