# Commands

The engine is one Python program, `skills/learnings-coach/scripts/pmlc.py`. It does the counting and checking so that the AI agent can spend its effort on judgement. Each job is a **command** (for example `select` or `check-pack`), and each command takes **flags** that start with two hyphens (for example `--tier`).

Most people never type these commands: the agent runs them. Read this reference when you want to know exactly what a step did, to repeat it yourself, or to put it in a script.

## Before you start

You need Python 3.9 or later and the `openpyxl` package (`pip install openpyxl`). The examples set three short names first, so the commands stay readable:

```bash
E=skills/learnings-coach/scripts/pmlc.py
WS=hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/workspace
OUT=hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs
```

- `$E` is the engine.
- `$WS` is the **workspace**: the folder of JSON files that [ingest](commands/ingest.md) makes from the export. Almost every command takes it first.
- `$OUT` is the run's **outputs** folder, where packs, registers and dashboards go.

The examples ran from a folder holding `hazira/`, a copy of the Hazira sample export. See [Files and folders](Files-and-folders.md) for the layout.

## Global options

| Flag | What it does |
|---|---|
| `--version` | Print the engine version, for example `pmlc 2.0.0a4`, and stop |
| `-h`, `--help` | Print the list of commands. After a command name (`$E select -h`) it prints that command's flags |

```bash
python3 $E --version
```

```text
pmlc 2.0.0a4
```

## Every command

### 1. Read the export

| Command | What it does |
|---|---|
| [ingest](commands/ingest.md) | Reads the `.xlsx` export into a workspace in a strict run folder |
| [profile](commands/profile.md) | Writes a one-page profile: counts by level, rating, sub-category and data-quality flags |
| [classify](commands/classify.md) | Maps the roles named in each finding to Learning Clusters (who: entity, tier, relation) |
| [status](commands/status.md) | Shows which workspace files are current or stale, and the last check of each pack |
| [run-path](commands/run-path.md) | Prints the run folder, workspace, outputs folder, slug, top rating and incident date |

### 2. Gather and analyse

| Command | What it does |
|---|---|
| [select](commands/select.md) | Picks the findings for one audience or question, as Markdown or JSON |
| [causal](commands/causal.md) | Builds the causal graph from the findings' causal explanations |
| [causal-item](commands/causal-item.md) | Prints the top causal links as a ready graph item for a pack |
| [table-item](commands/table-item.md) | Prints a ready table item (clusters, tiers, hubs, hoc, adoption and more) for a pack |
| [register-items](commands/register-items.md) | Prints one tier's register learnings as learning items for a pack |
| [timeline-item](commands/timeline-item.md) | Prints the dated candidates as a timeline item for a pack |
| [facts](commands/facts.md) | Prints the headline numbers of a workspace |
| [timeline](commands/timeline.md) | Finds dated precursor candidates and the clock times of the event day |
| [interfaces](commands/interfaces.md) | Finds where two parts of the organisation share findings or causal links |

### 3. Check what was written

| Command | What it does |
|---|---|
| [check-pack](commands/check-pack.md) | Checks a learning pack JSON against the workspace: IDs, structure, coverage and language |
| [check-register](commands/check-register.md) | Checks a Learnings Register JSON against the workspace |
| [check-language](commands/check-language.md) | Runs only the just-culture and grounding language checks (JC1 to JC12) |
| [scan-names](commands/scan-names.md) | Searches files for a list of personal names (a de-identification check) |
| [sign-off](commands/sign-off.md) | Records that a person reviewed a pack or register, with their role |

### 4. Produce outputs

| Command | What it does |
|---|---|
| [pack](commands/pack.md) | Turns a learning pack JSON into HTML and Markdown |
| [dashboard](commands/dashboard.md) | Writes the self-contained organisation learning map (HTML) |
| [pack-xlsx](commands/pack-xlsx.md) | Writes a pack's test points or questions to an Excel sheet |
| [register-xlsx](commands/register-xlsx.md) | Writes a Learnings Register JSON to a formatted Excel workbook |

### Files for the organisation to fill in

| Command | What it does |
|---|---|
| [templates](commands/templates.md) | Writes a blank adoption.csv, distribution.csv or verification.jsonl for your organisation to fill in |
| [export-actions](commands/export-actions.md) | Writes actions.csv and actions.json (owner, due date and status left blank) for your action-tracking system |

### 5. Repository upkeep

| Command | What it does |
|---|---|
| [check-samples](commands/check-samples.md) | Checks that published sample folders follow the contribution layout |

## Typing flags

- **Write each flag in full.** The engine does not accept shortened flags: `--top-rat` is refused, not read as `--top-rated`. This stops a typo from silently meaning something else.

  ```bash
  python3 skills/learnings-coach/scripts/pmlc.py select $WS --top-rat
  ```

  ```text
  usage: pmlc [-h] [--version]
              {ingest,profile,classify,select,causal,timeline,interfaces,dashboard,check-register,check-language,register-xlsx,status,run-path,check-samples,check-pack,pack,causal-item,sign-off,scan-names} ...
  pmlc: error: unrecognized arguments: --top-rat
  ```

- A value can follow the flag after a space or an equals sign: `--tier T2` and `--tier=T2` mean the same, and both are checked the same way.
- Put quotes round a value with spaces: `--code "SVF 3.1"`.

## Exit codes

Scripts and agents read the exit code to know whether a step worked.

| Code | Meaning |
|---|---|
| 0 | Success. Warnings may still be printed: read them |
| 1 | The command ran but found a problem, for example `check-pack` found an unknown ID, or the workspace is missing. A few contradictory flag pairs are also reported this way: `classify --overlay x --no-overlay` exits 1 with "--no-overlay and --overlay cannot be combined" |
| 2 | The command line itself was wrong: an unknown or shortened flag, a value outside the allowed list, or (for `scan-names`) a file that could not be read |

## Related

- [Workflows and recipes](Workflows-and-recipes.md): the commands in the order a real job uses them.
- [Troubleshooting](Troubleshooting.md): messages and what to do.
- [Developer tools](Developer-tools.md): the repository's own tools.
