# Getting started

This page takes you from nothing to your first learning pack, using the public Hazira sample. It assumes no programming knowledge: your AI agent runs every command for you. You read, decide and review.

## What you need

- An AI agent that can use skills: the **Claude app** (desktop or Cowork), **Claude Code**, or **OpenAI Codex**.
- **Python 3.9 or newer** with the **openpyxl** package on the computer where the agent runs. The agent uses them to run the engine. If openpyxl is missing, the engine stops with `openpyxl is required: pip install openpyxl` and the agent can install it for you.
- A **ProbeMatrix findings export**: the `.xlsx` file you export from an investigation in ProbeMatrix. To practise, use the public Hazira sample: [2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx](https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/samples/2020-09-24-hazira-gas-release-fire/2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx).
- A web browser, to open the HTML pages. They work offline.

## Install

The full instructions, including pinning a version and going back to the stable release, are in [INSTALL.md](https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/docs/INSTALL.md). In short:

### Claude app (desktop or Cowork)

1. Open the app's plugin settings.
2. Add the marketplace `ashley-eyekyam/probematrix-learnings-coach` and install the plugin `probematrix-learnings-coach`.
3. Start a new conversation and attach the export.

### Claude Code

Type these three lines in Claude Code:

```text
/plugin marketplace add ashley-eyekyam/probematrix-learnings-coach
/plugin install probematrix-learnings-coach@probematrix
/reload-plugins
```

Check with `/plugin`: the skills appear as `probematrix-learnings-coach:<skill>`.

### OpenAI Codex

Clone the repository and run Codex inside it: Codex reads `AGENTS.md` and the skills folder. To make the skills available in every project, run `./tools/install-codex.sh` once from the clone.

### Check the version

Ask the agent: *"Run the Learnings Coach engine with `--version` and tell me the result."* It prints, for example, `pmlc 2.0.0a3`. This manual describes v2.0.0-alpha.4.

## Your first run, step by step (Hazira)

Each step gives the prompt to paste, what the agent does, and what you should see. The numbers are the real ones from the Hazira sample.

### Step 1: set up the workspace

Attach the Hazira export (or point the agent to it) and paste:

> Use the learnings coach on this ProbeMatrix export. The site and event are hazira-gas-release-fire. Tell me what the investigation contains.

The agent runs `ingest`, `profile` and `classify`. It should report:

- 436 findings and 46 evidence items;
- 308 of the 436 findings (71%) at the Supervision and Organisational Influences levels;
- data-quality flags, including that the investigation status is `in_progress` and that no finding is marked as edited by a person, so every output will be a **draft**;
- 630 role strings placed, with 96 that still need resolution.

It creates the run folder `pmlc-runs/2020-09-24-hazira-gas-release-fire/` next to the export (see [Files and folders](Files-and-folders.md)). In the Claude app, where the upload folder is read-only, it makes the folder in a writable working folder instead.

### Step 2: place the remaining roles

Paste:

> Resolve the unplaced roles, show me your decisions, then re-run the classification.

The agent reads `unresolved_roles.json`, proposes a function, a tier and a relation for each role, and writes them to `role_overrides.json`. Correct any decision you disagree with: the file is kept, and every later run uses it. For an Indian process site you can also ask: *"Apply the india-process-site overlay."* On Hazira the overlay alone brings the unplaced roles from 96 to 87 (see [Add an industry overlay](Workflows-and-recipes.md#add-an-industry-overlay)).

### Step 3: make your first pack

Paste:

> Make the supervisor coach for this investigation.

The agent gathers the supervision findings (237 findings at tier T2 on Hazira, before the resolution pass), writes `supervisor-coach.json`, checks it with `check-pack`, fixes any problem it reports, and renders it with `pack`. It then tells you where the files are.

### Step 4: open it and read it

Open `outputs/supervisor-coach.html` in your browser. Read it as the person who will receive it would. Every sentence should trace to a Finding or Evidence ID: click an ID to see the full record.

### Step 5: build the register and the dashboard

Paste:

> Build the learnings register and the organisation learning dashboard.

You get `learnings-register.xlsx` and `organisation-learning-map.html`. The committed Hazira register has 25 learnings and 44 recommendations, covering 435 of the 436 findings.

## What each output looks like

| Output | What you see | Open it with |
|---|---|---|
| `<skill>.html` (a pack) | A title, a **DRAFT** ribbon until approved, the handling line, the status line "Learning purposes: not a statutory document", the bottom line, then collapsible sections. Every Finding and Evidence ID is a button that opens the full record. A coverage note says how many of the relevant findings the pack cites. Search and print buttons sit in the toolbar. | a web browser |
| `<skill>.md` | The same content as plain Markdown, for pasting into other documents. | any text editor |
| `learnings-register.xlsx` | Five sheets: Learnings Register, Recommendations, Learning Plan, Summary and About. The status phrase is in every sheet header. | Excel or LibreOffice |
| `organisation-learning-map.html` | Two tabs with a register: **Overview** (the learning-by-tier matrix, the plan per level, heat maps) and **Detailed register** (every learning with its evidence, and lenses per audience). | a web browser |

A pack page on Hazira opens like this (from `board-brief.md`, the Markdown twin of the page):

```text
# Board Brief: Hazira gas terminal release and fire, 2020

**DRAFT**

Review: draft · Classification: internal · Version 1.0

Draft because: the investigation status is in progress; no finding is marked as edited by a person

*Learning purposes: not a statutory document · Learnings drafted by an AI agent from AI-assisted findings*
```

## What to do next

- Pick the audiences you need from [Skills](Skills.md).
- Follow a ready-made sequence in [Workflows and recipes](Workflows-and-recipes.md).
- Before anything leaves the investigating team, read [Review and sharing](Review-and-sharing.md) and [Language checks](Language-checks.md).
- If a command stops with a message, look it up in [Troubleshooting](Troubleshooting.md).
- Words you do not know are in the [Glossary](Glossary.md).

**Commands in this manual.** Pages write the engine as `pmlc <command>`. That is short for `python3 skills/learnings-coach/scripts/pmlc.py <command>` (your agent fills in the real path). `<ws>` means the workspace folder and `<run>` the run folder. Every command has its own page under [Commands](Commands.md).
