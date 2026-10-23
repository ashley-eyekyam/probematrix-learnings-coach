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
| [run-manifest](commands/run-manifest.md) | Sets a run's intended use, jurisdiction, retention review date and classification |
| [purge](commands/purge.md) | Deletes a run's workspace (and outputs) after retention, keeping `run-manifest.json` |
| [plan](commands/plan.md) | Turns a workflow preset, audiences or skills into an ordered plan, and prints the next step |

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
| [evidence-audit](commands/evidence-audit.md) | Counts how well the evidence holds up: strength per finding, single-source and document-only findings, concentration |
| [hfacs-profile](commands/hfacs-profile.md) | Counts findings by HFACS level and subcategory, recurring codes and causal feeds |
| [open-questions](commands/open-questions.md) | Lists what the export leaves open: empty columns, blank fields, absence and hedged findings |
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
| [pack](commands/pack.md) | Turns a learning pack JSON into HTML and Markdown, and on request into Word, slides, an email digest, print layouts, quiz files, graph files and more (see [Output formats](#output-formats)) |
| [dashboard](commands/dashboard.md) | Writes the self-contained organisation learning map (HTML) |
| [pack-xlsx](commands/pack-xlsx.md) | Writes a pack's test points or questions to an Excel sheet |
| [register-xlsx](commands/register-xlsx.md) | Writes a Learnings Register JSON to a formatted Excel workbook |
| [register-md](commands/register-md.md) | Writes a Learnings Register JSON to `learnings-register.md` |
| [register-render](commands/register-render.md) | Writes a Learnings Register JSON to a Word document and an email digest |
| [strings](commands/strings.md) | Extracts a pack's text for translation (XLIFF or CSV) and applies the translation as `<pack>-<lang>.json` |

### Run it all

| Command | What it does |
|---|---|
| [setup](commands/setup.md) | Runs ingest, classify, profile, causal, timeline and interfaces in one go |
| [check-all](commands/check-all.md) | Checks every pack and the register in the outputs folder |
| [render-all](commands/render-all.md) | Renders every pack that passed its check, and the register |
| [index](commands/index.md) | Writes the outputs front page, one row per pack |
| [dossier-index](commands/dossier-index.md) | Writes a pack listing the cluster dossiers |

### Files for the organisation to fill in

| Command | What it does |
|---|---|
| [templates](commands/templates.md) | Writes a blank adoption.csv, distribution.csv or verification.jsonl for your organisation to fill in |
| [export-actions](commands/export-actions.md) | Writes actions.csv and actions.json (owner, due date and status left blank) for your action-tracking system |

### 4a. Compare with another report

| Command | What it does |
|---|---|
| [compare](commands/compare.md) | Checks the comparator inventory and prints both-direction coverage tables as ready pack items |

### 5. Repository upkeep

| Command | What it does |
|---|---|
| [check-samples](commands/check-samples.md) | Checks that published sample folders follow the contribution layout |

## Output formats

[pack](commands/pack.md) writes `<pack>.html` and `<pack>.md` unless you ask for more. `--format` takes a comma-separated list of the formats below (no spaces: `--format html,docx,email`). `--format` replaces the default; list `html,md` too to keep them. A **document** format is for people to read: it carries the status phrase, the ProbeMatrix credit and, until sign-off, DRAFT. A **data** format is for another program to import: it carries the status in its own comment or metadata slot, or not at all where that would break the import. The full description of each, with what it holds, is in [pack](commands/pack.md#formats).

| Format | Kind | File | What it is for |
|---|---|---|---|
| `html` | document | `<pack>.html` | The offline page (default) |
| `md` | document | `<pack>.md` | The same content as Markdown (default) |
| `docx` | document | `<pack>.docx` | A Word document; with `--layout paper`, also the board paper `<pack>.paper.docx` |
| `pptx` | document | `<pack>.pptx` | A 16:9 slide deck you can edit, with the citations in the speaker notes |
| `email` | document | `<pack>.email.html`, `<pack>.email.txt` | An email-safe digest under 100 KB, to paste into a message |
| `scorm` | document | `<pack>.scorm.zip` | A SCORM 1.2 course for a learning management system (LMS), with a quiz graded in the browser |
| `normalised` | data | `<pack>.normalised.json` | The pack with every id filled in and the cited records, for other tools |
| `svg` | data | `<pack>.<item-id>.svg` | Each graph item as a picture with every label whole |
| `png` | data | `<pack>.<item-id>.png` | The same picture as a PNG, drawn by a local Chromium-family browser |
| `graphml` | data | `<pack>.<item-id>.graphml` | Each graph item for yEd and other graph tools |
| `bowtie-csv` | data | `<pack>.bowtie.csv` | The barriers, one row each, for a bow-tie tool |
| `ics` | data | `<pack>.ics` | Calendar reminders for the follow-ups, counted from `--start` |
| `gift` | data | `<pack>.gift.txt` | The questions for a Moodle import |
| `qti` | data | `<pack>.qti.zip` | The questions as an IMS QTI 2.1 package for other LMSs |
| `quiz-csv` | data | `<pack>.quiz.csv` | The questions as a spreadsheet, answer key included |
| `csv` | data | `<pack>.actions.csv` | The actions for an action-tracking system, owner and due date blank |
| `srt` | data | `<pack>.<item-id>.srt` | Subtitles from a video script |
| `narration` | data | `<pack>.<item-id>.narration.txt` | A script's narration only, for a voice-over or a PA reader |

Other `pack` flags that shape the output:

- `--layout` writes one print page beside the other files, `<pack>.<layout>.html`: `cards` (one card a page), `field` (cards with end-notes and a delivery record), `toolbox` (one toolbox talk a page), `checklist` (tick boxes and a "Checked by (role)" line), `poster` (one A3 page) or `paper` (a board paper).
- `--paper` sets `A4` or `A5` for the `cards` layout.
- `--base-url` is where the pack page is published; the print layouts then carry QR codes that open each item there.
- `--view` set to `learner` writes a learner copy of each document format, `<pack>.learner.<ext>`, without answers.
- `--brand` reads a `brand.json` with your organisation's name, accent colour and logo.
- `--start` is the day the `ics` reminders count from. The coach never picks a date by itself.

To translate a pack, use [strings](commands/strings.md); [register-render](commands/register-render.md) writes the register in Word and as an email digest.

## Typing flags

- **Write each flag in full.** The engine does not accept shortened flags: `--top-rat` is refused, not read as `--top-rated`. This stops a typo from silently meaning something else.

  ```bash
  python3 skills/learnings-coach/scripts/pmlc.py select $WS --top-rat
  ```

  ```text
  usage: pmlc [-h] [--version]
              {ingest,profile,classify,select,causal,timeline,interfaces,dashboard,check-register,check-language,register-xlsx,register-md,register-render,status,run-path,run-manifest,purge,check-samples,check-pack,pack,causal-item,sign-off,scan-names,setup,check-all,render-all,index,dossier-index,templates,export-actions,plan,compare,table-item,register-items,timeline-item,open-questions,facts,evidence-audit,hfacs-profile,pack-xlsx,strings} ...
  pmlc: error: unrecognized arguments: --top-rat
  ```

- A value can follow the flag after a space or an equals sign: `--tier T2` and `--tier=T2` mean the same, and both are checked the same way.
- Put quotes round a value with spaces: `--code "SVF 3.1"`.

## Exit codes

Scripts and agents read the exit code to know whether a step worked. These three codes are the same for every command, with or without `--json`.

| Code | Meaning |
|---|---|
| 0 | OK. Warnings may still be printed: read them |
| 1 | Problems found, or the plan cannot be resolved. For example `check-pack` found an unknown ID, the workspace is missing, or [plan](commands/plan.md) met an unknown skill, a cycle or a requirement nothing produces. A few contradictory flag pairs are also reported this way: `classify --overlay x --no-overlay` exits 1 with "--no-overlay and --overlay cannot be combined" |
| 2 | Usage error (the command line itself was wrong: an unknown or shortened flag, or a value outside the allowed list), or the plan is complete (`plan --next`) |

The `check-*` commands never use 2 for problems. One command outside that family, [scan-names](commands/scan-names.md), also exits 2 when a file could not be read, so a zero-hit result is not claimed for it.

## JSON output

These commands take `--json`: `profile`, `classify`, `causal`, `timeline`, `interfaces`, `status`, `facts`, `plan`, `compare`, `check-pack`, `check-register`, `check-language`, `check-all`, `check-samples` and `scan-names`. [select](commands/select.md) keeps `--format json` and accepts `--json` as an alias.

With `--json`, stdout holds exactly one JSON object and nothing else; messages, warnings and errors go to stderr. The exit code is the one the command gives without `--json`. `facts`, `plan`, `check-register` and `check-all` print their own documented shapes. `compare --json` keeps its existing output, the ready pack items. The other commands print `{"command", "ok", "exit_code", "output": [report lines]}` plus their data as structured fields (listed on each command page, for example `classify` gives `entities` and `tiers`). When a command fails, `ok` is false and `error` holds the reason, which is also written to stderr. A crash (an unexpected exception) prints a traceback and no JSON.

## Related

- [Workflows and recipes](Workflows-and-recipes.md): the commands in the order a real job uses them.
- [Troubleshooting](Troubleshooting.md): messages and what to do.
- [Developer tools](Developer-tools.md): the repository's own tools.
