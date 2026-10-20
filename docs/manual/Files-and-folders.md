# Files and folders

Every investigation gets one **run folder**. The engine writes all its working files and all its outputs there, and nowhere else. This page explains the layout, every file you will find, and the settings you can give through environment variables.

## The run folder

The run folder sits next to the export, inside a folder called `pmlc-runs`. Its name is the incident date followed by the site and event you gave as the slug:

```text
<folder of the export>/
  2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx
  pmlc-runs/
    2020-09-24-hazira-gas-release-fire/      <- the run folder (<run>)
      workspace/                             <- the workspace (<ws>): the engine's working files
      outputs/                               <- everything you read, print or share
```

- The date comes from the export's summary sheet, or from `ingest --date` when the sheet is wrong.
- If the export's folder is read-only (as for uploads in the Claude app), `ingest --root <folder>` makes `pmlc-runs/` inside a writable folder instead.
- `pmlc run-path <ws>` prints the run folder, the workspace, the outputs folder, the slug, the top rating and the incident date.
- `pmlc-runs/` is ignored by git in this repository, so real incident data is never committed by accident.

Everything in `workspace/` can be rebuilt from the export, except the decisions you made (`role_overrides.json`). Everything in `outputs/` comes from JSON files the skills write; the HTML, Markdown and Excel files are regenerated from that JSON.

## Workspace files

These are the files in a fresh Hazira workspace after `ingest`, `profile` and `classify`, then the files that later commands add.

| File | Written by | What it holds |
|---|---|---|
| `findings.json` | `ingest` | Every finding: ID, factor code and name, HFACS level and sub-category, rating, label, short description, AI justification, causal explanation, roles, linked evidence IDs, the four follow-up columns, and whether a person edited it. 436 on Hazira. |
| `evidence.json` | `ingest` | Every evidence item: ID, type, description, and for each linked factor the relevance and the quoted specific reference. 46 on Hazira. |
| `incident.json` | `ingest` | The summary-sheet fields (title, date, location, investigation status and so on), the narrative, the Causal Chain sheet rows, reviewer votes, the sheet names, the column check and the Analysis Statistics block. |
| `manifest.json` | every command | The bookkeeping: the export's file name and fingerprint, the engine version, a fingerprint of each derived file and of the inputs it was built from, the last check of each pack, sign-offs and the number of redactions. `status` reads it. |
| `profile.md` | `profile --out` | The readable summary: counts by level, rating and sub-category, the most frequent factors and roles, evidence types and data-quality flags. |
| `clusters.json` | `classify` | For every finding, its entities (F), tiers (T) and relations (R); the role map (how each role string was placed, and why); the taxonomy and overlays used; the overrides applied. |
| `unresolved_roles.json` | `classify` | Role strings with no entity (F99) or no tier (T9). 96 on Hazira before the resolution pass. |
| `singleton_roles.json` | `classify` | Roles that could point to one person (a post with a single holder, or a role with a number, date or place in it), each with a general label to use instead. 15 on Hazira. |
| `role_overrides.json` | you, or the agent with your agreement | Your decisions for roles the rules could not place or placed wrongly: `{"<role>": {"F": [...], "T": "...", "R": "..."}}`. Read on every `classify`. Never rebuilt: keep it. |
| `causal_graph.json`, `causal_graph.mmd` | `causal` | The factor-to-factor links, with mention counts and supporting finding IDs; the `.mmd` file is the same graph for tools that draw Mermaid diagrams. |
| `timeline_candidates.json` | `timeline` | Every dated mention in findings and evidence, with its precision and sources. 92 before the Hazira incident date. |
| `timeline_event_day.json` | `timeline --on` | Every clock time on one day, with its sources. 29 on the Hazira incident day. |
| `interfaces.json` | `interfaces` | Pairs of functions, with shared findings and cross-entity causal mentions. 125 pairs on Hazira. |
| `plan.json` | `plan` | The numbered plan of steps for a request, each with its state, commands and gate. It holds no dates or absolute paths. `status` shows it stale once the workspace changes; run `plan` again. |
| `sel-<F-id>.md`, `top.json` | `select --out` | Saved selections that some skills write while gathering. They are working notes, not outputs. |

`status` reports each derived file as `current`, `stale` (an input changed since it was built, with the reason) or `unknown` (built before the manifest existed). See the recipe [Re-run after the export changes, using status](Workflows-and-recipes.md#re-run-after-the-export-changes-using-status).

## Outputs

| File | Written by | What it is |
|---|---|---|
| `<skill>.json` | the skill (the agent) | The learning pack: the source of truth for that deliverable. Edit this, never the HTML. |
| `<skill>.html` | `pack` | The pack as a self-contained offline page. Open it first. |
| `<skill>.md` | `pack` | The same content in Markdown. `pack --no-md` skips it. |
| `dossier-<F-id>.json`, `.html`, `.md` | cluster-learning-dossier | One dossier per function, for example `dossier-F02`, plus `dossier-index`. |
| `follow-up.json` | `pack` on the investigator-coach pack | One entry per finding: evidence to collect, key questions, suggested interviews and a causal hypothesis, ready to paste back into ProbeMatrix. |
| `report-comparison-client-safe.json` and its page | report-comparison | A neutral version for the authors of the other report. |
| `learnings-register.json` | learnings-register | The register: the source of truth. |
| `learnings-register.xlsx` | `register-xlsx` | The workbook: Learnings Register, Recommendations, Learning Plan, Summary and About. |
| `learnings-register.md` | learnings-register | Summary tables and the learnings in Markdown. |
| `organisation-learning-map.html` | `dashboard` | The dashboard, with the Detailed register tab when built with `--register`. |
| `<pack>.external.html`, `<pack>.public.html` (and `.md`) | `pack --share external` or `--share public` | Masked copies of a pack for sharing outside the organisation. The internal copy is kept. |
| `organisation-learning-map.external.html`, `.public.html` | `dashboard --share external` or `--share public` | A masked copy of the learning map. It needs `--register` with a register approved for that audience. |
| `learnings-register.external.xlsx`, `.public.xlsx` | `register-xlsx --share external` or `--share public` | A masked copy of the workbook, with a "Sharing" row on its About sheet. |

A signed-off JSON file carries a `handling` block; the HTML and Markdown show it as the review line. The block counts only together with its sign-off record in this workspace's `manifest.json`, so a signed file copied to another folder or workspace is a draft there ("not signed off"). See [Review and sharing](Review-and-sharing.md).

Converted files (PDF, Word, PowerPoint) are made only when you ask, with the host's own tools. Their author fields are left blank so they carry no personal name. This repository's git settings ignore such files outside the published samples.

## Environment variables

| Variable | Used by | What it does |
|---|---|---|
| `PMLC_NAMES` | `check-language`, `check-pack`, `check-register`, `pack`, `dashboard` and `register-xlsx` | Path to a names file used when `--names` is not given. One name per line; blank lines and lines starting with `#` are skipped. |
| `PMLC_ORGS` | the same commands | Path to an organisation names file used when `--orgs` is not given. Same format. |
| `PMLC_UPDATE_GOLDEN` | the repository's test suite (contributors only; `tools/release.py` prints the reminder) | Set to `1` to regenerate the golden Markdown fixtures. Not used when you analyse an investigation. |

If a variable points to a file that does not exist, the command stops with, for example, `PMLC_NAMES: file not found: <path>`.

For the developer tools in `tools/`, see [Developer tools](Developer-tools.md).
