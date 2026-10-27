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
| `singleton_roles.json` | `classify` | Roles that could point to one person, each with its reason (`qualifier` or `single-holder`) and a general label (its function and tier) to use instead. The rule is under [Singleton roles](#singleton-roles) below. 8 on Hazira. |
| `org-chart-ids.json` | `classify --org-chart` | The F-ids given to your own departments (`F20`, `F21` and so on), so they keep their ID on every re-run. |
| `role_overrides.json` | you, or the agent with your agreement | Your decisions for roles the rules could not place or placed wrongly: `{"<role>": {"F": [...], "T": "...", "R": "..."}}`. Read on every `classify`. Never rebuilt: keep it. |
| `causal_graph.json`, `causal_graph.mmd` | `causal` | The factor-to-factor links, with mention counts and supporting finding IDs; the `.mmd` file is the same graph for tools that draw Mermaid diagrams. |
| `timeline_candidates.json` | `timeline` | Every dated mention in findings and evidence, with its precision and sources. 92 before the Hazira incident date. |
| `timeline_event_day.json` | `timeline --on` | Every clock time on one day, with its sources. 29 on the Hazira incident day. |
| `evidence_audit.json` | `evidence-audit` | For every finding its evidence strength (`direct`, `corroborated` or `inferred`), sources and evidence types; per HFACS level the single-source, document-only and witness counts; the evidence items that support the most findings. Once it exists, `check-register` checks each learning's `evidence_strength` against it. 203 single-source and 195 document-only findings on Hazira. |
| `hfacs_profile.json` | `hfacs-profile` | Findings per HFACS level, the share at levels 3 and 4, the level by subcategory heat map, the codes that recur and the codes that feed the most others in the causal graph. 70.6% at levels 3 and 4 on Hazira; SVI 1.4 recurs 21 times. |
| `missed_opportunities.json` | `missed-opportunities` | The findings citing an earlier recommendation, the Failure-to-Correct (SVF) findings, the dated mentions before the incident that cite them, and the findings with drift wording. 107, 40, 34 and 41 on Hazira. |
| `open_questions.json` | `open-questions` | The empty follow-up columns, the blank Incident Summary fields, and the findings whose justification says something is absent or is hedged (240 and 193 on Hazira). |
| `wai_wad.json` | `wai-wad` | Work as imagined against work as done: for each code, its findings with document evidence, with work-as-done evidence (witness statements, log records, recordings) and with both; the codes with a gap; and the findings whose justification uses counterfactual wording (the list in `references/learning-team.json`). 68 of 94 codes with both, 92 findings with both, 210 with any work-as-done evidence and 337 counterfactual on Hazira. |
| `accimap.json` | `accimap` | Each finding placed on one of Rasmussen's six AcciMap levels (1 government to 6 equipment), with the rule that placed it and whether the placement is inferred; the levels with no placement as `gaps`. On Hazira levels 1 and 2 are gaps and level 3 holds 143 inferred placements. |
| `effect_plan.json` | `effect-plan` | The effectiveness checks for each register learning, counted from adoption (`30 days after adoption`), each with its Kirkpatrick level and the register's leading indicator, the lagging column blank; and each learning's Jacobsson spread, depth and duration. 97 checks for the 25 Hazira learnings. |
| `interfaces.json` | `interfaces` | Pairs of functions, with shared findings and cross-entity causal mentions. 125 pairs on Hazira. |
| `nine_m_seed.json` | `nine-m-seed` | Every finding scored against the nine Ms, the M profile and the unmapped findings. 436 findings, 0 unmapped on Hazira. |
| `nine_m_session.json` | `nine-m-suggest --record`, `nine-m-answer`, `nine-m-replay` | The 9M interview: each question with its M, step, subcategory and suggestions, and the answer as given (a suggestion's number or your own words). `mode` is `interview`, or `replay` for a scripted session (57 questions in the Hazira sample). |
| `plan.json` | `plan` | The numbered plan of steps for a request, each with its state, commands and gate. It holds no dates or absolute paths. `status` shows it stale once the workspace changes; run `plan` again. |
| `comparator.json` | the agent, in the report-comparison skill | The other report's numbered items (`OBS-`, `RC-`, `REC-`, `ACT-nn`), its issuer role and its statutory status. [compare](commands/compare.md) reads it. |
| `comparison-map.json` | the agent, in the report-comparison skill | Which learning matches which item of the other report: `[{"lr_id", "ref", "match": "yes" or "partial" or "none"}]`. |
| `sel-<F-id>.md`, `top.json` | `select --out` | Saved selections that some skills write while gathering. They are working notes, not outputs. |

### Singleton roles

`classify` lists a role in `singleton_roles.json` when it could point to one person, by this rule (from the engine's `privacy.py`):

1. **Group roles are never singletons.** Take the role up to its first bracket or spaced dash (" - "). If that part ends in *operators*, *crew*, *team*, *staff*, *workers* or *personnel*, the role is skipped, whatever follows. "Control Room Operators" and "Seal change crew (Shift B)" are not singletons.
2. **Dates are ignored.** Dates are removed from the role before the next test: "Dec-2019", "24 May 2020", "18-Sep-2020", "12/03/2020", "2020-03-12" and bare years such as "2019". A date alone never makes a role a singleton, so "Calibration supervisor (Dec-2019)" is not one.
3. **A qualifier makes a role a singleton** (reason `qualifier`) when what is left contains any of:
   - one of the words *post*, *gate*, *shift*, *grade*, *No.* (or *No*), *desk*, *cabin*, *CR* or *control room*, followed by a number or a single capital letter, with or without a space or hyphen: "Gate 3", "Shift A", "Grade-2", "No. 4", "CR2";
   - a `#` followed by a number: "Pump operator #2";
   - a spaced dash (" - ") followed by text with a number in it, at the end of the role: "Security Guard - Gate 3", "Fitter - bay 7";
   - a closing bracket with a number in it, at the end of the role: "Shift engineer (unit 2)".
4. **A sole post holder is a singleton** (reason `single-holder`) when the role maps to Plant & Asset Leadership (F13) or Corporate & Board (F14) and is the only role mapped to that entity at its tier. The list of such entities is `single_holder_entities` in `references/lint-terms.json`.

Anything else is not a singleton. On Hazira, 8 roles meet the rule. Until 2.0.0a5 a date counted as a qualifier, and the same export gave 15; the 7 roles dropped are all ones whose only qualifier was a date.

The language check (JC7) flags a singleton role in your own wording, and a shared copy (`--share external` or `public`) replaces it with its general label.

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
| `<pack>-tables.xlsx` | `pack-xlsx --kind table` | Each table item of a pack as its own sheet, named by the item's id, with a last `cites` column holding each row's cites. |
| `follow-up.json` | `pack` on the investigator-coach pack | One entry per finding: evidence to collect, key questions, suggested interviews and a causal hypothesis, ready to paste back into ProbeMatrix. |
| `follow-up.csv` | `pack` on the investigator-coach pack | The same follow-up table as a spreadsheet, in the export's own columns (`Finding ID,Evidence to Collect,Key Questions,Suggested Interviews,Causal Hypothesis`). A shared copy writes neither file.  |
| `open-questions-follow-up.csv` | `pack` on the `open-questions-register` pack | One row per Finding ID that a `question` item cites (Finding ID, the items' `good_evidence` under Evidence to Collect and their questions under Key Questions, each joined with `; ` when several questions cite the finding; the other two columns blank). Evidence IDs give no row. Written in any mode (a shared copy as `open-questions-follow-up.<mode>.csv`, masked); not written when no question cites a finding; an existing file is never overwritten, because the organisation fills it in. |
| `nine-m-map.json` | `pack` on the `nine-m-analysis` pack | Each cited finding with its M, subcategory and condition, and each condition with its M, subcategory, register learning and recommendations. The register copies `nine_m` and `nine_m_subcategory` from it, and `rec-review --nine-m` reads it. |
| `cihh-consolidated.json`, `cihh-events.jsonl` | [consolidate](commands/consolidate.md) | The sites' could-it-happen-here returns: how many returns assessed each learning, how many sites found each condition present or partly, and the learnings each site assessed (never a ranking of sites); and one `site_assessment` event per answered row, for the learnings library. Rewritten from all the returns given on each run. |
| `<pack>.actions-template.xlsx`, `<pack>.actions-template.csv` | [nine-m-actions-template](commands/nine-m-actions-template.md) | The blank actions sheet of a nine-m-analysis pack: Recommendation ID, M, Change, HoC tier, Corrective/Preventive, Indicator, Owner, Due date, Status and Notes. Owner, Due date, Status and Notes are blank, and an existing sheet is never overwritten. 9 rows for the Hazira pack. |
| `report-comparison-client-safe.json`, `report-comparison-regulator-safe.json` and their pages | report-comparison | Neutral versions for the authors of the other report and for a regulator. |
| `learnings-register.json` | learnings-register | The register: the source of truth. |
| `learnings-register.xlsx` | `register-xlsx` | The workbook: Learnings Register, Recommendations, Learning Plan, Summary and About. |
| `learnings-register.md` | `register-md` | Summary tables and the learnings in Markdown. Never written by hand. |
| `organisation-learning-map.html` | `dashboard` | The dashboard, with the Detailed register tab when built with `--register`. |
| `<pack>.external.html`, `<pack>.public.html` (and `.md`) | `pack --share external` or `--share public` | Masked copies of a pack for sharing outside the organisation. The internal copy is kept. |
| `organisation-learning-map.external.html`, `.public.html` | `dashboard --share external` or `--share public` | A masked copy of the learning map. It needs `--register` with a register approved for that audience. |
| `learnings-register.external.xlsx`, `.public.xlsx` | `register-xlsx --share external` or `--share public` | A masked copy of the workbook, with a "Sharing" row on its About sheet. |

### Other formats

`pack --format` writes these beside `<skill>.html` and `<skill>.md`, only when asked (see "Output formats" in [Commands](Commands.md)). A **document** file is for people and carries the status phrase, the ProbeMatrix credit and, until sign-off, DRAFT; a **data** file is for another program.

| File | Format or flag | What it is |
|---|---|---|
| `<pack>.docx` | `--format docx` | A Word document on A4, with the citations as endnotes |
| `<pack>.paper.docx` | `--format docx --layout paper` | The board paper in Word: cover, decisions requested, numbered paragraphs, annexes |
| `<pack>.pptx` | `--format pptx` | A 16:9 slide deck, with the citations and full text in the speaker notes |
| `<pack>.email.html`, `<pack>.email.txt` | `--format email` | An email-safe digest (inline styles, no images, under 100 KB) and its plain-text twin |
| `<pack>.<layout>.html` | `--layout cards`, `field`, `toolbox`, `checklist`, `poster` or `paper` | A page made for printing from the browser |
| `<pack>.learner.<ext>` | `--view learner` | A learner copy of each document format, without answers |
| `<pack>.scorm.zip` | `--format scorm` | A SCORM 1.2 course for an LMS: `imsmanifest.xml`, `index.html` and `scorm.js` |
| `<pack>.gift.txt` | `--format gift` | The questions for a Moodle import, answer key included |
| `<pack>.qti.zip` | `--format qti` | The questions as an IMS QTI 2.1 package |
| `<pack>.quiz.csv` | `--format quiz-csv` | The questions as a spreadsheet, one row each |
| `<pack>.<item-id>.svg`, `<pack>.<item-id>.png`, `<pack>.<item-id>.graphml` | `--format svg`, `png`, `graphml` | One file per graph item: a picture with every label whole, the same as a PNG, and the graph for yEd. On Hazira: `causal-map.causal-map.svg` |
| `<pack>.bowtie.csv` | `--format bowtie-csv` | One row per barrier, for a bow-tie tool |
| `<pack>.risk-changes.csv` | `--format risk-csv` | One row per risk change proposed, for a risk register; the last column is for the risk owner's decision. An existing file is never overwritten |
| `<pack>.ics` | `--format ics --start YYYY-MM-DD` | All-day calendar reminders for the follow-ups; no attendee, no organiser |
| `<pack>.<item-id>.srt`, `<pack>.<item-id>.narration.txt` | `--format srt`, `narration` | Subtitles and the narration only, from each video or radio script |
| `<pack>.normalised.json` | `--format normalised` | The pack for other tools, with every id filled in, the coverage counts and the cited records |
| `<pack>.actions.csv` | `--format csv` | The pack's actions for an action-tracking system; see the table below |
| `learnings-register.docx`, `learnings-register.email.html`, `learnings-register.email.txt` | [register-render](commands/register-render.md) | The register in Word and as an email digest |

A shared copy puts its mode before the last extension (`<pack>.external.docx`, `<pack>.email.external.html`), and a learner copy puts `learner` there (`<pack>.paper.learner.html`).

### Translations and the brand file

| File | Written by | What it is |
|---|---|---|
| `<pack>.strings.xlf`, `<pack>.strings.csv` | [strings extract](commands/strings.md) | The pack's text for a translator, as XLIFF 1.2 (the default) or CSV. Citations show as placeholders that must stay in place. Never overwritten, because it holds the translator's work. |
| `<pack>-<lang>.json` | [strings apply](commands/strings.md) | The translated pack, for example `frontline-learning-cards-hi.json`. It names its source in `translation_of`, carries "Translated with AI assistance: have a fluent speaker check it before use" under the status, and is rendered with `pack` like any pack. Never overwritten, because it may hold a reviewed translation. |
| `brand.json` | you | Your organisation's look for `pack --brand`: `organisation`, `accent` (a `#RRGGBB` colour with a contrast of at least 4.5:1 against white) and `logo` (a PNG or JPEG beside the file, at most 200 KB). Nothing else is accepted. |

### Files your organisation fills in

The engine writes these with the identifying columns filled in and every owner, date, response and assessed-by column blank. Your organisation fills them in; the agent never does. [templates](commands/templates.md) refuses to overwrite a file that already exists, because it may hold your entries. The files can be opened and saved in Excel: the engine reads them back with Excel's byte-order mark, extra or reordered columns and blank rows, and reports every bad value by file and row while still reading the good rows.

| File | Written by | Columns (engine-filled ones marked ✱) |
|---|---|---|
| `adoption.csv` | `templates adoption` | `lr_id`✱, `title`✱, `response` (accepted, modified or rejected), `reason`, `owning_role`, `target_window`. 25 rows for the Hazira register. |
| `distribution.csv` | `templates distribution` | `pack`✱, `audience`✱, `channel`, `date`, `delivered_by_role`, `attendees`, `contractors_included` (yes or no; `y` and `n` count too), `questions_raised`, `concerns_escalated` |
| `verification.jsonl` | `templates verification` | One line per learning: `lr_id`✱, `check_date`, `level` (communicated, understood, applied or effective), `evidence`, `assessed_by_role`. 25 lines for the Hazira register. |
| `actions.csv`, `actions.json` | [export-actions](commands/export-actions.md) | `id`✱, `lr_id`✱, `change`✱, `hoc_tier`✱, `barrier`✱, `indicator`✱, `owner`, `due`, `status`, `capa_ref`, `effectiveness_check`, `cites`✱, `evidence_strength`✱. 44 actions from the Hazira register. Never overwritten: a second run refuses while either file exists (move them or pass a new `--out-dir`). |
| `<pack>.actions.csv` | `pack --format csv` | The same columns as `actions.csv`, for one pack's recommendation, decision and indicator items. Never overwritten. |
| `<pack>.cihh-template.xlsx` | `templates cihh --pack <pack>` | One sheet, `Return`: Site (B1, blank), Pack (B2✱, the pack's content hash), then from row 4 `lr_id`✱, `condition`✱, `evidence_to_check`✱, `answer` (present, partly, absent or n/a), `site_response`, `assessed_by_role`; one row per `self_check` item. One copy goes to each site. Never overwritten; a shared copy is `<pack>.cihh-template.external.xlsx`. |
| `learning-team-notes.csv` | `templates learning-team` | Header only: `prompt_id`, `prompt`, `team_answer`, `source`. The learning team fills it in; the agent never writes `team_answer`. Never overwritten. |

The dashboard reads `adoption.csv` and `distribution.csv` back for its reach and response columns.

A signed-off JSON file carries a `handling` block; the HTML and Markdown show it as the review line. The block counts only together with its sign-off record in this workspace's `manifest.json`, so a signed file copied to another folder or workspace is a draft there ("not signed off"). See [Review and sharing](Review-and-sharing.md).

Converted files (PDF, Word, PowerPoint) are made only when you ask, with the host's own tools. Their author fields are left blank so they carry no personal name. This repository's git settings ignore such files outside the published samples.

## Shared contracts

These files in the skills folder (`skills/learnings-coach/references/` unless stated) tell the engine and the agent how the skills fit together. They ship with the skills; you change them only to adapt the coach.

| File | What it holds | Used by |
|---|---|---|
| `skills/<skill>/skill.json` | One per skill: its kind (hub, analysis, audience, register or dissemination today; interactive and multi-incident are reserved for later skills), audiences, scope, what it requires and produces, the default share level and the questions to ask | `plan`, `index`, the hub |
| `skill.schema.json` | The schema every `skill.json` must follow | the engine's contract check and the test suite |
| `pack.schema.json` | The published JSON Schema (draft 2020-12) for a learning pack: its shape, every item kind and every optional field. It checks structure only; `check-pack` also checks that cited IDs exist, the language rules, handling and coverage. Other tools can use it to validate a pack before it reaches the engine | the test suite; your own validators |
| `artefacts.json` | Every file a step can produce or need (workspace, clusters, register, gaps, adoption and so on), with its path in the run folder and what produces it | `plan` |
| `workflows.json` | The nine workflow presets and their steps, in order | `plan`, the hub |
| `audiences.json` | One entry per audience: who they are, what they control, what they need, their tier and levels, and the skill that serves them. `audiences.md` is generated from it | `plan --audiences`, the hub |
| `pack-profiles.json` | For each pack: its sections and the item kinds each allows, the minimum and maximum counts, the required scope, the bottom-line length, word limits and the coverage floor | `check-pack` (warnings, or problems under `--strict`) |
| `select-presets.json` | Each skill's recorded gather calls | `select --preset` |
| `actions-profiles.json` | Column mappings for EHS systems (generic, and unverified mappings for Enablon, Intelex, Cority and SAP EHS) | `export-actions --profile` |
| `standards-crosswalk.json` | Requirement IDs (such as `ISO45001-10.2`) for a pack item's `clauses` | `check-pack` |
| `hfacs-codes.json` | The HFACS levels, categories and sub-categories with their definitions | `profile`, the skills |
| `nine-m.json`, `nine-m.md` | The nine Ms (9M) and their 97 subcategories, each with a newly written definition and three probe questions; the page explains the order, the overlaps and the IP boundary | `nine-m-seed`, the 9M skill |
| `nine-m-map.json` | How a Nanocode prefix or code, keywords and Learning Cluster entities point to an M | `nine-m-seed` (`--map` for your own copy) |
| `open-questions.json` | The documented word lists: absence and hedging (for `open-questions`), drift (for `missed-opportunities`) | `open-questions`, `missed-opportunities` |
| `rec-review.json` | The strength bands for each hierarchy-of-controls tier, the weak administrative cues and the double-loop cues | `rec-review` |
| `learning-team.json` | Which evidence types count as work as imagined (documents) and work as done (witness statements, log records, recordings), the counterfactual word list (`did not`, `failure to`, `should have`, `lack of` and others, matched as whole words) and the columns of the learning-team notes sheet | `wai-wad`, `templates learning-team` |
| `accimap.json` | Rasmussen's six levels and the placement rules: entities first (regulators at level 2; corporate, board and contractors at level 3, inferred), then the HFACS level | `accimap` (`--map` for your own copy) |
| `effectiveness.json` | The check schedule by priority (offsets from adoption), the Kirkpatrick levels and the Jacobsson spread and depth rules | `effect-plan` |
| `industry/process/` | The process-industries reference pack: `overlay.json` (role words), `barriers.md`, `indicators.md` and `glossary.json`. Method reference, not evidence | `classify --industry process`, `setup --industry process` |
| `glossary.json` | The terms the packs and pages use, each with a definition and its `translations` (Hindi, `hi`, AI-drafted: check with a fluent speaker) | a shared word list for writers and translators; this manual's [Glossary](Glossary.md) explains the same terms |
| `taxonomy.json` | The Learning Cluster rules, with a `version` (2.0) that `classify` records with a fingerprint | `classify` |

The run-level contracts are on this page: `run-manifest.json` above, `plan.json` among the workspace files, and `gaps.json` and the files your organisation fills in among the outputs.

## The learnings library

A learnings library is a folder you choose, outside the run folders, that keeps learnings from many incidents. [library publish](commands/library.md) adds a run to it; nothing else writes there. Lines are only ever added.

```text
<library folder>/
  library.json             <- {"kind": "pmlc-library", "version": 1}
  learnings.jsonl          <- one snapshot of a learning a line, with its LL- ID
  events.jsonl             <- withdrawn and status events, site assessments, verification readings, adoption responses
  incidents.jsonl          <- one line for each published state of an incident
  private/
    sites.json             <- real site names and their codes (S01 ...). Never shared
    contexts.jsonl         <- each learning's context as written. Never shared
```

| File | What it holds |
|---|---|
| `library.json` | Marks the folder as a library |
| `learnings.jsonl` | Each learning's snapshots: `LL-` ID, `snapshot_id`, `supersedes`, incident key, LR-ID, content hash, review status and the de-identified learning |
| `events.jsonl` | What happened to a learning later, from the engine or the organisation, by month |
| `incidents.jsonl` | The incident key, site code, incident month, taxonomy version and fingerprint, export fingerprint, engine version, publish month and `LL-` IDs |
| `private/sites.json` | Each real site name and its code |
| `private/contexts.jsonl` | Each snapshot's original context |

Everything outside `private/` has passed the de-identification gate: no listed name, sites as codes, months instead of days. See [The learnings library](Library.md).

## Environment variables

| Variable | Used by | What it does |
|---|---|---|
| `PMLC_NAMES` | `check-language`, `check-pack`, `check-register`, `pack`, `dashboard` and `register-xlsx` | Path to a names file used when `--names` is not given. One name per line; blank lines and lines starting with `#` are skipped. |
| `PMLC_ORGS` | the same commands | Path to an organisation names file used when `--orgs` is not given. Same format. |
| `PMLC_LIBRARY` | `library publish` | The library folder used when `--library` is not given. With neither, the command stops with `no library folder: pass --library <dir> or set PMLC_LIBRARY`. |
| `PMLC_UPDATE_GOLDEN` | the repository's test suite (contributors only; `tools/release.py` prints the reminder) | Set to `1` to regenerate the golden Markdown fixtures and the HTML hashes in `tests/fixtures/packs/html-golden.json`. Not used when you analyse an investigation. |
| `SOURCE_DATE_EPOCH` | `pack` | A time in seconds since 1970. When set, its date is the generated date written into every output, and the time of every entry in a zipped output, so the same pack gives the same files on every run. |
| `PMLC_BROWSER` | `pack --format png` | The Chromium-family browser to draw PNG images with, tried before `chromium`, `chromium-browser`, `google-chrome`, `google-chrome-stable`, `microsoft-edge` and `msedge` on the PATH. |
| `PMLC_LABELS_DIR` | the repository's test suite (contributors only) | A folder searched before `references/labels/` for the label files (`<language>.json`). Not used when you analyse an investigation. |

If a variable points to a file that does not exist, the command stops with, for example, `PMLC_NAMES: file not found: <path>`.

For the developer tools in `tools/`, see [Developer tools](Developer-tools.md).
