# Files and folders

Every investigation gets one **run folder**. The engine writes all its working files and all its outputs there, and nowhere else. This page explains the layout, every file you will find, and the settings you can give through environment variables.

## The run folder

The run folder sits next to the export, inside a folder called `pmlc-runs`. Its name is the incident date followed by the site and event you gave as the slug:

```text
<folder of the export>/
  2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx
  pmlc-runs/
    2020-09-24-hazira-gas-release-fire/      <- the run folder (<run>)
      run-manifest.json                      <- what this run is for, and its retention record
      workspace/                             <- the workspace (<ws>): the engine's working files
      outputs/                               <- everything you read, print or share
```

- The date comes from the export's summary sheet, or from `ingest --date` when the sheet is wrong.
- If the export's folder is read-only (as for uploads in the Claude app), `ingest --root <folder>` makes `pmlc-runs/` inside a writable folder instead.
- `pmlc run-path <ws>` prints the run folder, the workspace, the outputs folder, the slug, the top rating and the incident date.
- `pmlc-runs/` is ignored by git in this repository, so real incident data is never committed by accident.

Everything in `workspace/` can be rebuilt from the export, except the decisions you made (`role_overrides.json`) and the comparison files the agent wrote with you (`comparator.json`, `comparison-map.json`). Everything in `outputs/` comes from JSON files the skills write; the HTML, Markdown and Excel files are regenerated from that JSON.

## The run manifest

`run-manifest.json` sits in the run folder, beside `workspace/` and `outputs/`. `ingest` (and so `setup`) writes it; [run-manifest](commands/run-manifest.md) sets its fields; [purge](commands/purge.md) records what it deleted and never deletes the manifest itself.

| Field | What it holds |
|---|---|
| `run` | The run folder's name, for example `2020-09-24-hazira-gas-release-fire` |
| `export_sha256`, `export_file` | A fingerprint of the export and its file name, so you can show later which file the run was made from |
| `ingested_on` | The date of the ingest |
| `classification` | `internal` until you set another level |
| `retention_review` | The date to review whether the run is still needed, or `null` |
| `intended_use` | What the learnings are for, in your words, or `null` |
| `jurisdiction` | The regimes that apply, from `in`, `uk`, `us` and `eu` |
| `purged_on`, `purged` | When `purge` ran and what it removed; `null` and empty until then |

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
| `singleton_roles.json` | `classify` | Roles that could point to one person (a post with a single holder, or a role with a number, date or place in it), each with a general label to use instead. 8 on Hazira. |
| `org-chart-ids.json` | `classify --org-chart` | The F-ids given to your own departments (`F20`, `F21` and so on), so they keep their ID on every re-run. |
| `role_overrides.json` | you, or the agent with your agreement | Your decisions for roles the rules could not place or placed wrongly: `{"<role>": {"F": [...], "T": "...", "R": "..."}}`. Read on every `classify`. Never rebuilt: keep it. |
| `causal_graph.json`, `causal_graph.mmd` | `causal` | The factor-to-factor links, with mention counts and supporting finding IDs; the `.mmd` file is the same graph for tools that draw Mermaid diagrams. |
| `timeline_candidates.json` | `timeline` | Every dated mention in findings and evidence, with its precision and sources. 92 before the Hazira incident date. |
| `timeline_event_day.json` | `timeline --on` | Every clock time on one day, with its sources. 29 on the Hazira incident day. |
| `interfaces.json` | `interfaces` | Pairs of functions, with shared findings and cross-entity causal mentions. 125 pairs on Hazira. |
| `plan.json` | `plan` | The numbered plan of steps for a request, each with its state, commands and gate. It holds no dates or absolute paths. `status` shows it stale once the workspace changes; run `plan` again. |
| `comparator.json` | the agent, in the report-comparison skill | The other report's numbered items (`OBS-`, `RC-`, `REC-`, `ACT-nn`), its issuer role and its statutory status. [compare](commands/compare.md) reads it. |
| `comparison-map.json` | the agent, in the report-comparison skill | Which learning matches which item of the other report: `[{"lr_id", "ref", "match": "yes" or "partial" or "none"}]`. |
| `sel-<F-id>.md`, `top.json` | `select --out` | Saved selections that some skills write while gathering. They are working notes, not outputs. |

`status` reports each derived file as `current`, `stale` (an input changed since it was built, with the reason) or `unknown` (built before the manifest existed). See the recipe [Re-run after the export changes, using status](Workflows-and-recipes.md#re-run-after-the-export-changes-using-status).

## Outputs

| File | Written by | What it is |
|---|---|---|
| `<skill>.json` | the skill (the agent) | The learning pack: the source of truth for that deliverable. Edit this, never the HTML. |
| `<skill>.html` | `pack` | The pack as a self-contained offline page. Open it first. |
| `<skill>.md` | `pack` | The same content in Markdown. `pack --no-md` skips it. |
| `index.html` | [index](commands/index.md) | The front page of the outputs: one row per pack and the register, with audience, coverage, formats, date, review status and a link. Open it first. |
| `dossier-<F-id>.json`, `.html`, `.md` | cluster-learning-dossier | One dossier per function, for example `dossier-F02`. |
| `dossier-index.json` | [dossier-index](commands/dossier-index.md) | A pack listing the dossiers, rendered by `pack` like any other. |
| `gaps.json` | `pack` | What the evidence could not show, collected from every pack that has `gaps`, for the investigator: `{"gaps": [{"pack", "text", "cites", "evidence_needed"}]}`. Each `pack` run replaces that pack's entries and keeps the others. |
| `<pack>-test-points.xlsx`, `<pack>-questions.xlsx` | [pack-xlsx](commands/pack-xlsx.md) | A pack's test points or questions as one Excel sheet. |
| `follow-up.json` | `pack` on the investigator-coach pack | One entry per finding: evidence to collect, key questions, suggested interviews and a causal hypothesis, ready to paste back into ProbeMatrix. |
| `report-comparison-client-safe.json`, `report-comparison-regulator-safe.json` and their pages | report-comparison | Neutral versions for the authors of the other report and for a regulator. |
| `learnings-register.json` | learnings-register | The register: the source of truth. |
| `learnings-register.xlsx` | `register-xlsx` | The workbook: Learnings Register, Recommendations, Learning Plan, Summary and About. |
| `learnings-register.md` | `register-md` | Summary tables and the learnings in Markdown. Never written by hand. |
| `organisation-learning-map.html` | `dashboard` | The dashboard, with the Detailed register tab when built with `--register`. |
| `<pack>.external.html`, `<pack>.public.html` (and `.md`) | `pack --share external` or `--share public` | Masked copies of a pack for sharing outside the organisation. The internal copy is kept. |
| `organisation-learning-map.external.html`, `.public.html` | `dashboard --share external` or `--share public` | A masked copy of the learning map. It needs `--register` with a register approved for that audience. |
| `learnings-register.external.xlsx`, `.public.xlsx` | `register-xlsx --share external` or `--share public` | A masked copy of the workbook, with a "Sharing" row on its About sheet. |

### Files your organisation fills in

The engine writes these with the identifying columns filled in and every owner, date, response and assessed-by column blank. Your organisation fills them in; the agent never does. [templates](commands/templates.md) refuses to overwrite a file that already exists, because it may hold your entries. The files can be opened and saved in Excel: the engine reads them back with Excel's byte-order mark, extra or reordered columns and blank rows, and reports a bad value by file and row.

| File | Written by | Columns (engine-filled ones marked ✱) |
|---|---|---|
| `adoption.csv` | `templates adoption` | `lr_id`✱, `title`✱, `response` (accepted, modified or rejected), `reason`, `owning_role`, `target_window`. 25 rows for the Hazira register. |
| `distribution.csv` | `templates distribution` | `pack`✱, `audience`✱, `channel`, `date`, `delivered_by_role`, `attendees`, `contractors_included` (yes or no), `questions_raised`, `concerns_escalated` |
| `verification.jsonl` | `templates verification` | One line per learning: `lr_id`✱, `check_date`, `level` (communicated, understood, applied or effective), `evidence`, `assessed_by_role`. 25 lines for the Hazira register. |
| `actions.csv`, `actions.json` | [export-actions](commands/export-actions.md) | `id`✱, `lr_id`✱, `change`✱, `hoc_tier`✱, `barrier`✱, `indicator`✱, `owner`, `due`, `status`, `capa_ref`, `effectiveness_check`, `cites`✱, `evidence_strength`✱. 44 actions from the Hazira register. Rewritten on every run, since it holds nothing you entered. |

The dashboard reads `adoption.csv` and `distribution.csv` back for its reach and response columns.

A signed-off JSON file carries a `handling` block; the HTML and Markdown show it as the review line. The block counts only together with its sign-off record in this workspace's `manifest.json`, so a signed file copied to another folder or workspace is a draft there ("not signed off"). See [Review and sharing](Review-and-sharing.md).

Converted files (PDF, Word, PowerPoint) are made only when you ask, with the host's own tools. Their author fields are left blank so they carry no personal name. This repository's git settings ignore such files outside the published samples.

## Shared contracts

These files in the skills folder (`skills/learnings-coach/references/` unless stated) tell the engine and the agent how the skills fit together. They ship with the skills; you change them only to adapt the coach.

| File | What it holds | Used by |
|---|---|---|
| `skills/<skill>/skill.json` | One per skill: its kind (hub, analysis, audience, register, dissemination), audiences, scope, what it requires and produces, the default share level and the questions to ask | `plan`, `index`, the hub |
| `skill.schema.json` | The schema every `skill.json` must follow | the engine's contract check and the test suite |
| `artefacts.json` | Every file a step can produce or need (workspace, clusters, register, gaps, adoption and so on), with its path in the run folder and what produces it | `plan` |
| `workflows.json` | The nine workflow presets and their steps, in order | `plan`, the hub |
| `audiences.json` | One entry per audience: who they are, what they control, what they need, their tier and levels, and the skill that serves them. `audiences.md` is generated from it | `plan --audiences`, the hub |
| `pack-profiles.json` | For each pack: its sections and the item kinds each allows, the minimum and maximum counts, the required scope, the bottom-line length, word limits and the coverage floor | `check-pack` (warnings, or problems under `--strict`) |
| `select-presets.json` | Each skill's recorded gather calls | `select --preset` |
| `actions-profiles.json` | Column mappings for EHS systems (generic, and unverified mappings for Enablon, Intelex, Cority and SAP EHS) | `export-actions --profile` |
| `standards-crosswalk.json` | Requirement IDs (such as `ISO45001-10.2`) for a pack item's `clauses` | `check-pack` |
| `hfacs-codes.json` | The HFACS levels, categories and sub-categories with their definitions | `profile`, the skills |
| `glossary.json` | The terms the packs and pages use, each with a definition and an empty `translations` slot (English only for now) | a shared word list for writers and translators; this manual's [Glossary](Glossary.md) explains the same terms |
| `taxonomy.json` | The Learning Cluster rules, with a `version` (2.0) that `classify` records with a fingerprint | `classify` |

The run-level contracts are on this page: `run-manifest.json` above, `plan.json` among the workspace files, and `gaps.json` and the files your organisation fills in among the outputs.

## Environment variables

| Variable | Used by | What it does |
|---|---|---|
| `PMLC_NAMES` | `check-language`, `check-pack`, `check-register`, `pack`, `dashboard` and `register-xlsx` | Path to a names file used when `--names` is not given. One name per line; blank lines and lines starting with `#` are skipped. |
| `PMLC_ORGS` | the same commands | Path to an organisation names file used when `--orgs` is not given. Same format. |
| `PMLC_UPDATE_GOLDEN` | the repository's test suite (contributors only; `tools/release.py` prints the reminder) | Set to `1` to regenerate the golden Markdown fixtures. Not used when you analyse an investigation. |

If a variable points to a file that does not exist, the command stops with, for example, `PMLC_NAMES: file not found: <path>`.

For the developer tools in `tools/`, see [Developer tools](Developer-tools.md).
