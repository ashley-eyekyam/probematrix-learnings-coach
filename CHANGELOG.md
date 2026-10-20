# Changelog

## [Unreleased] (v2.0.0)

- Workflow: every change starts with an issue and a branch; v2.0 work happens on `feature/v2.0-features-edition` under epic issue #1. AGENTS.md and CONTRIBUTING.md describe the workflow, and `.github/` adds pull request, feature and bug templates.

### 2.0.0a5

Phase 3: the shared spine and the planner.

- **The planner.** New `plan <ws> --workflow <preset>` (or `--audiences`, `--skills`) turns a request into a numbered plan of steps, with each step's commands and gate, and writes `plan.json`. `plan --next` prints the next step to do. Nine workflow presets ship: `first-48-hours`, `full-cascade`, `leadership`, `assurance`, `investigation-quality`, `action-design`, `sister-sites`, `training` and `follow-up`. A step is done only when its output is current and passed its gate's check with `--strict` (the manifest's check record now says whether a pass was strict, and `check-all --strict` also runs `check-register --strict`); a step whose skill arrives in a later phase is shown as "planned for v2.0, Phase N" and skipped. The hub skill now asks what the learnings are for, one question at a time, shows the plan and waits for your OK.
- **Run it all.** New `setup` (ingest, classify, profile, causal, timeline and interfaces in one go), `check-all`, `render-all`, `index` (the outputs front page, `index.html`) and `dossier-index`.
- **The register as the spine.** Packs can name the register learning they express (`learning: "LR-nn"`), and `check-pack` checks it against the register (`--register`, or the run's `learnings-register.json`). New `register-md` writes `learnings-register.md`; it is never hand-written again. The register workbook has an Excel table per sheet, filters, drop-down lists, print setup and links between sheets. `check-register` splits its report into problems and warnings, and adds the rule that a priority-1 learning needs a fix above the administrative tier, or a `why_not_stronger`.
- **Files your organisation fills in.** New `templates <ws> adoption|distribution|verification` writes `adoption.csv`, `distribution.csv` and `verification.jsonl`, and new `export-actions` writes `actions.csv` and `actions.json` for an action-tracking system (`--profile generic`, with unverified column mappings for Enablon, Intelex, Cority and SAP EHS). Owner, due-date, response and assessed-by columns are always blank, `templates` never overwrites an existing file, and files saved from Excel are read back. The dashboard shows learnings by pack, the reach of each pack, each learning's response, and a filter for learnings that need legal or compliance review.
- **Ready-made items.** New `table-item`, `register-items`, `timeline-item` and `facts`, and `causal --hubs`, print ready pack items and the headline numbers, so the agent pastes numbers rather than retyping them. New `pack-xlsx` writes a pack's test points or questions to Excel.
- **Comparisons.** New `compare` checks the other report's inventory (`comparator.json`) and the mapping (`comparison-map.json`) and prints both-direction coverage tables as pack items. The report-comparison skill can also write a regulator-safe copy. `select --text … --in-evidence` also searches the linked evidence (its specific reference and description).
- **Retention.** Every run gets a `run-manifest.json` (export fingerprint, intended use, jurisdiction, classification, retention review). New `run-manifest` sets its fields; new `purge` deletes a run's workspace (and outputs) after retention and keeps the manifest. With a jurisdiction set, pages carry "Statutory report still required: …".
- **Pack checks.** `check-pack` reads each pack's profile (`pack-profiles.json`: sections, item kinds and counts, scope, word limits) and warns on departures, on 3 or more items in one section with the same citations (possible padding), and on scope drift. The coverage line is joined by a second one: "x of y top-rated relevant findings cited".
- **Skills.** All 22 sub-skills follow one skeleton: Before you start, Gather, Write, If the evidence is thin, Not covered here, Check and hand over. Shared rules sit once in `references/skill-common.md`. Each skill has a `skill.json` manifest, and the shared contracts (`artefacts.json`, `workflows.json`, `audiences.json`, `glossary.json`, `hfacs-codes.json`, `standards-crosswalk.json`) are new.
- **Profile.** `profile` flags thin exports (no Evidence Links sheet, no narrative, no dated text, a high share of unmapped functions or unresolved tiers, empty and thin tiers) and adds an HFACS levels table with definitions. `setup` runs `classify` before `profile`, so its summary and `profile.md` carry these flags. On Hazira it reports one thin tier, `T5 (1)`.
- **`--json`.** `profile`, `classify`, `causal`, `timeline`, `interfaces`, `status`, `facts`, `plan`, `compare`, `check-pack`, `check-register`, `check-language`, `check-all`, `check-samples` and `scan-names` take `--json`: one JSON object on stdout, messages on stderr, the same exit code. `select` keeps `--format json` and accepts `--json` too. The exit codes are documented once in the manual: 0 OK, 1 problems (or a plan that cannot be resolved), 2 a usage error (or `plan --next` with nothing left).
- **Classify.** `classify --org-chart FILE.csv` maps roles to your own departments, and `clusters.json` records the taxonomy version, a fingerprint of the rules used, and roles that name a statutory post (such as the Occupier or a COMAH operator) as prompts to check the duty.
- **evals.** Router evals for the hub (34) and a new `section_exists` expectation. The frontline eval prompt says "the people on the floor"; new evals cover the regulator-safe comparison copy, frontline cards for a contractor crew against the supply-chain skill (both directions), and supervisors briefing their crews on the cards. 109 evals in all.
- **Fixes.**
  - Tied counts in `causal` and `interfaces` are now listed in ID order, so the same workspace always gives the same output.
  - Shared copies keep standards clauses and LR, OBS, RC, REC and ACT ids, and keep ratios after a colon ("1:10").
  - The Hazira sample register gives LR-08 and LR-12 a `why_not_stronger`, so it passes `check-register --strict`, and its `learnings-register.md` is regenerated with `register-md`.
- **Migration notes.**
  - **Taxonomy 2.0.** `taxonomy.json` now carries `"version": "2.0"`, and `classify` records it with a fingerprint. Re-run `classify` on an existing workspace; tier counts move:
    - Deputy and Assistant General Managers ("DGM", "Dy. GM", "Deputy General Manager", "Asst. GM", "Assistant General Manager") are T3, and Additional General Managers ("Addl. GM", "Additional General Manager") are T4, in the `india-process-site` overlay. A bare "AGM" is left unresolved (T9), because it can mean either: resolve it in `role_overrides.json`.
    - Without the India overlay, "Dy./Asst. General Manager" moves from T4 to T3, and "DGM" from T2 to T9 (unresolved), because the base rule for `dgm` is removed.
    - A function's own leadership ("Maintenance leadership", "HSE leadership") is T3 (function management); plant, site, asset and senior leadership stay T4. "Leader" as a word still means T2.
    - Signing roles ("signing authority", "signatories", "countersigned by") count as approvers, and a document custodian or owner maps to Engineering, Design, Documents & MOC (F07).
    - On Hazira with the India overlay, findings touching each tier move from T2 234, T3 211, T4 78 to **T2 219, T3 247, T4 63** (T1 227, T5 1, T9 87 unchanged). With the base taxonomy, T3 moves from 211 to 219 and T4 from 54 to 39.
  - **A date alone no longer makes a role a singleton.** A role whose only qualifier is a date, such as "Maintenance Fitter (18-Sep-2020 gasket replacement)" or "Calibration supervisor (Dec-2019)", is no longer listed in `singleton_roles.json`. In `--share external` and `--share public` copies such a role keeps its wording, with its date treated like any other date (a full date becomes the month and year), instead of being replaced by its function and tier; the language check (JC7) no longer flags it. Roles with an instance number or letter (a gate, post, shift, desk or control room number) and sole post holders are unchanged. On Hazira `singleton_roles.json` falls from 15 roles to 8: the 7 dropped roles are all date-only.
  - **`lint_ok` placement.** A `lint_ok` at the top level of a pack or on a section is now a language error ("lint_ok must sit on an item, a bottom-line entry or a register entry"), because it never suppressed anything there. Move it onto the item it explains.
  - **`--strict`.** `check-pack --strict` and `check-register --strict` are new. Without `--strict`, nothing that passed before fails because of the new pack-profile and register rules: pack-profile departures, padding, scope drift, unknown `LR-nn` and unknown clauses are warnings, and the priority-1 rule is a warning in `check-register`. Under `--strict` they are problems. The planner's gates use `--strict`.
  - **The coverage warning** now looks at the top-rated relevant findings: it fires when fewer than a quarter of them are cited (the profile's `coverage_floor`).
  - **Manifest records by path.** The workspace manifest now keys pack checks and sign-offs by the file's resolved path, not its bare name, so two files with the same name in different folders no longer share a record. Records written by alpha.4 or v0.3 under the bare name are still read and honoured; the next check or sign-off rewrites them under the path.
  - **Checks survive a sign-off.** A check record stores the content hash without the `handling` block, so signing off a file does not make its last check out of date (`render-all` and `plan` still count it as checked).
  - **New optional fields.** Every new field is optional: alpha.4 and v0.3 packs and registers still pass, at worst with warnings.
    - Register entries: `urgency`, `recommendation_class`, `recipient_role`, `regulatory_touchpoint`, `nine_m`, `nine_m_subcategory`, `verification` (`method`, `indicator`), `why_not_stronger`, `capa_ref`, `closure_evidence` and `effectiveness_result`.
    - Pack items: `learning`, `clauses` and `comparator_refs` on any item; `why_not_stronger`, `barrier_id` and `co_owner` on a recommendation; `barrier_id` on a barrier; `clause` on a test point. Top level: `gaps` (collected into `outputs/gaps.json`) and `limits`.
  - **Personal names next to a month.** A month word is now exempt from the name rule JC1 only when a day number or a year sits next to it ("24 May", "May 2020"). A capitalised month before a surname ("May Patel") is a JC1 error, where alpha.4 let it pass.
  - The engine is now the `pmlc_lib` package; `pmlc.py`, `pmlc_pack.py`, `pmlc_lint.py` and `pmlc_privacy.py` stay as entry points with the same commands and flags.

### 2.0.0a4

Phase 2: trust gates and the user manual.

- **Language checks.** New `check-language <ws> <json>` runs the just-culture rules JC1 to JC12 (names, punitive wording, counterfactuals, hindsight, legal conclusions, retraining as the only fix, roles that point to one person, numbers not in the cited findings, organisation names, equipment tags, the status phrase, appeals to "be more careful") and exits 1 on an error. `check-pack` and `check-register` run it too. `--share` checks at the sharing level; `--names` and `--orgs` (or `PMLC_NAMES` and `PMLC_ORGS`) add your own lists. An accepted exception is a `lint_ok` with a reason, and the page shows the reason.
- **Review and sign-off.** New `sign-off <ws> <file> --role <role>` writes a `handling` block (status, reviewer role, date, classification, legal review, distribution, version, retention review) with a content hash, and `status` lists the sign-offs. An edit after sign-off turns the file back into a draft. Nothing can be reviewed or approved until the investigation status is completed, and while no finding is marked as edited by a person.
- **Draft ribbon and provenance.** Packs, the learning map and the register workbook show DRAFT until approved, with a handling line and the reasons. The export's wording is labelled "AI justification (ProbeMatrix)", and a finding no person edited carries "AI-drafted, not human-edited". Every printed page and every workbook sheet carries the status phrase.
- **`--embed cited|summary|full`** on `pack` and `dashboard`. `summary` also leaves out evidence descriptions, quotes, suggested interviews, key questions and vote reasons. A note suggests `summary` when witness statements would be embedded.
- **Print.** The printed evidence trail lists only the cited findings and evidence, and it no longer starts on a new page. The uncovered findings print as one line, "x of y relevant findings cited".
- **`--share internal|external|public`** on `pack`, `dashboard` and `register-xlsx`, with `--names` and `--orgs`. An external or public copy needs an approved sign-off, a classification at that level, `legal_review` cleared and `--embed summary`; otherwise the command lists every unmet condition and writes nothing. The copy masks names, organisations, equipment tags, one-person roles, clock times and full dates, and is written as `<name>.external.<ext>` or `<name>.public.<ext>`. In every mode, `pack` and `dashboard` refuse a page that still contains a listed name.
- **`register-xlsx --ws`** names the workspace when the register is not in its run folder, so the workbook can show the forced-draft status (and a shared copy can be checked).
- **Privacy at ingest and in samples.** `ingest --redact MAP.json` replaces listed names with roles as the export is read. `classify` writes `singleton_roles.json`. `profile` flags personal fields and a missing regulator mention. `scan-names --variants --patterns` also reads Office and PDF metadata. `tools/make-public-sample.py` strips document metadata and blanks personal fields.
- **Packs.** Learning cards take an optional `organisation_changing` (a warning when a T1 pack's card has none) and timeline events an optional `knowable_then`.
- **User manual.** `docs/manual/`: every skill, command, flag and developer tool, with Hazira examples, recipes, troubleshooting and a glossary. `tools/sync-wiki.py` mirrors it to the GitHub wiki.
- **evals and CI.** New eval expectations `language_clean`, `pack_absent` and `card_fields`; `grade` exits 1 when nothing was graded. CI caches pip, fails a piped step on any error, and checks that the pack renderer is covered. The Hazira smoke run also runs `check-language` on the sample register.
- **Fixes.**
  - `select --preset` combined with a filter now exits 2 with "--preset cannot be combined with filters; edit the preset or drop --preset."
  - A role counts as one that points to one person only when it carries an instance id, such as "Gate 3" or "Shift A". Group roles such as "Control Room Operators" are never counted.
  - Equipment-tag matching skips Learning Cluster entity IDs (`F02`) and tier IDs (`T4`).
  - The phone-number pattern ignores dates such as `2020-09-24` and `24-09-2020`.
  - The Hazira sample's register workbook and learning map are rebuilt with this engine.
  - A reviewed or approved status now counts only when `sign-off` recorded it in this workspace, for this file. A handling block typed or changed by hand, or a signed file copied to another folder or workspace, is a draft ("not signed off"), and the checks warn "not signed off in this workspace: status is draft until sign-off records it".
  - `register-xlsx` on a register outside its run folder, with no `--ws`, writes a draft workbook ("no workspace to check").
  - Forced draft now covers every unfinished investigation: any status other than "completed" (such as "draft", "In Progress" or a blank) is a draft, with the reason "the investigation status is not completed" (or "… is in progress"). Only Yes, Y, True or 1 in User Edited counts as edited by a person.
  - `sign-off` refuses a personal name as `--role` or in `--distribution` ('--role: looks like a personal name ("…"); give a role'), and takes `--names`. It now checks the file at the classification it will have, so an external sign-off meets the external language rules.
  - Shared copies keep finding and evidence IDs such as `FND-AE629313` whole (they were masked as equipment tags), and keep `lint_ok` rule IDs such as `JC10`.
  - Shared copies also remove "At 0216"-style times after a preposition and dotted times such as "9.15 am" or "21.30 hrs". Years ("from 2017", "by 2020") and quantities ("at 1500 rpm") are kept.
  - In shared copies and `scan-names --variants`, a surname that is also a role word ("Officer") is not matched on its own, so a role such as "Procurement Officer" is no longer masked.
  - The register workbook stores text that starts with `=`, `+`, `-` or `@` as text, never as a formula.
  - `dashboard --register` and `register-xlsx` given a pack JSON say "<file> is a pack, not a register" instead of failing with a traceback.
  - The README says how to stay on the tested alpha.3.
- **Migration notes.**
  - `--embed cited` is the new default for `pack` and `dashboard`. Pass `--embed full` for the v0.3 behaviour, where the page embeds every relevant record.
  - The `handling` block is optional. A pack or register without one still passes, with the warning "no handling block: rendered as draft (internal)", and renders as a draft. Do not write the block by hand; run `sign-off`.
  - `check-pack` (and `check-register`) now fail on language errors. Rewrite the wording, or add a `lint_ok` with a reason when the hit is not what it looks like.
  - Abbreviated flags are refused: write `--top-rated`, not `--top-rat`.

### 2.0.0a3

- Dashboard "Highest-rated findings" shows 0 when no finding has a rating; UAT book restructured; revert procedure corrected. The UAT book is now `docs/uat/v2.0-phase-1-uat.md` (version-neutral name). The hub skill says to ingest with `--root` when the upload folder is read-only.
- CI also runs on pushes to `main`.

### 2.0.0a2

- Dashboard no longer crashes when no finding has a rating.
- Alpha notice at the top of the README, INSTALL sections on getting updates, pinning a version and going back to stable, and a UAT book for testing in the Claude app (`docs/uat/`, inputs from `tools/make-uat-inputs.py`).

### Phase 1: Correct and tested (2.0.0a1)

- Fix: role overrides now persist. `classify` keeps `role_overrides.json` when you re-run it, and it reuses the previous taxonomy and overlays (`--no-overlay` opts out; `--no-overrides` ignores the overrides file). A malformed overrides file is reported, not ignored.
- Fix: interface selection uses shared findings. `select --entity F02 --entity F06 --entity-mode all` returns the findings both functions share (27 on the Hazira sample, not 196). `--entity-mode any` is the old behaviour.
- `pmlc.py status <ws>` lists the workspace files, what each was built from and which are out of date, and when each pack was last checked. `pack` and `dashboard` also print a stale-input warning on stderr.
- `pmlc.py --version`; `run-path` also prints `top_rating` and `incident_date`.
- `select`: `--tag` (select by entity tag, not hard-coded IDs), `--top-rated`, `--exclude-downgraded`, `--subcategory`, `--prefix`, `--budget-chars` (never splits a finding), `--fields`, `--group-by`, `--count-by`, and `--preset <skill>` (reproduces that skill's gather calls). Presets share one budget.
- `timeline`: clock times and an event-day sequence (one entry per minute), `--on <day|incident>`, `--entity`, `--min-precision`, and `--before incident` (months or years before the incident, with year-only dates shown as such).
- `ingest --strict` fails on missing required columns. `ingest` records a schema fingerprint, cross-checks the Analysis Statistics sheet against the findings, and refuses a CAPA Planner export with a clear message.
- Checks: `check-pack` evidence linkage counts justification IDs, a citation to a downgraded finding needs a `data_quality` note, and `check-register` reports controlled-vocabulary drift as warnings (not errors).
- Taxonomy: F14 is now Corporate & Board, and F15 Regulators, F16 Vendors/OEMs and F17 Contractors are new. Entities carry tags. Site-specific role words moved to the `india-process-site` overlay. Governance is a weak T5 signal and a general manager is plant leadership (T4). Migration: re-run `classify` on existing workspaces; add `--overlay india-process-site` for Hazira-style vocabulary (it is remembered afterwards).
- Samples: official and ProbeMatrix material may be included unmodified; the name scan is optional. Just culture in outputs is unchanged.
- CI: GitHub Actions on Linux (ubuntu) only, with Python 3.9 and the latest 3.x, with and without Node; ruff, subprocess coverage (90% floor), a Hazira smoke test and a skills drift test (subcommands and SKILL.md command lines).
- evals: 71 defined; structure check passing; graded runs: none yet (golden packs arrive in Phase 4).

## 0.3.5

- `scan-names` lists any file it cannot read (such as a PDF) and exits 2, so a zero-hit result never silently skips a file.
- Samples: the de-identification rule covers ProbeMatrix material; an official public report may be included unmodified. New sample `2020-09-24-hazira-gas-release-fire` replaces the old `Hazira-2020` folder.

## 0.3.4

- `question` items take an optional `answer` (an answer key); `training-designer` puts its answer keys there instead of in `why`. The role a question goes to is labelled "Put to" (was "Ask").
- Causal and other graphs: a link that skips a layer (such as L4 to L1) arcs above the nodes instead of lying on the chain through the layers between.
- The Markdown renders consecutive checks as one tight list.

## 0.3.3

- Learning packs for the eight analysis skills: `causal-map` (drawn graph from `pmlc.py causal-item`), `precursor-timeline`, `interface-learnings`, `barrier-learnings`, `learning-clusters`, `cluster-learning-dossier` (`dossier-<F-id>`), `report-comparison` and the organisation learning plan (`organisation-learning-plan`). Every skill except the router and `learnings-register` now writes a pack; all keep writing `<skill>.md` at the same path.

## 0.3.2

- Learning packs for the ten audience skills: `frontline-learning-cards`, `manager-coach`, `site-leadership-coach`, `top-management-brief`, `auditor-assurance-pack`, `training-designer`, `emergency-response-learnings`, `engineering-integrity-learnings`, `supply-chain-contractor-learnings` and `safety-committee-guide` now write a pack JSON and render `<skill>.html` plus `<skill>.md` with `pmlc.py pack`.
- Pack schema v1 additions (all optional): a `learning` item kind; `owner`, `state` and `indicator` on `barrier`; `time`, `received_by` and `response` on timeline events; `row_supporting_cites` on tables; `finding_notes` on the investigator follow-up table (copied to `follow-up.json`).
- `pmlc.py causal-item` prints a ready graph item from `causal_graph.json`.
- Fixes: the Markdown shows the incident title and date; `dossier-F09b`-style names are accepted; an unknown scope entity is a problem; the bottom-line and data-quality boxes fit their text on wide screens.

## 0.3.1 (2026-10-16)

- Pack schema v1 additions from the pilot run (all optional): `incident` override, `data_quality`, `exclusions`, `supporting_cites`, `evidence_strength`, `group`; investigator follow-up rows per condition; the `row_cites` column is labelled Cites; the coverage warning fires under a quarter; card grids and table columns fixed on wide and narrow screens.

## 0.3.0 (2026-10-16)

- Learning packs: `board-brief`, `supervisor-coach` and `investigator-coach` now write a pack JSON (`references/pack-schema.md`). `pmlc.py check-pack` validates it against the workspace, and `pmlc.py pack` renders a self-contained offline HTML page (collapsible sections, citations that open the full finding and evidence, coverage, search, deep links, print) plus generated Markdown. `investigator-coach` also writes `follow-up.json`. The other skills follow in 0.3.1 and 0.3.2.
- `organisation-learning-map.html` uses the extra width on screens 1400px and wider.

## 0.2.0 (2026-10-15)

- `learnings-register`: `organisation-learning-map.html` now has a second tab, **Detailed register**. It shows every learning field, recommendation, tier message, finding and evidence quote, with stakeholder lenses (T1–T5, Investigator, Auditor), filters, search, deep links, print and a coverage panel. It is self-contained and works offline.
- **Breaking:** `ingest --out <any folder>` is now refused unless it is `<dir>/pmlc-runs/<YYYY-MM-DD>-<site>-<event>/workspace`; use `--slug`, or `--legacy-out` for the old behaviour.
- Strict run folders: `pmlc.py ingest --slug <site>-<event>` writes `<export-dir>/pmlc-runs/<YYYY-MM-DD>-<site>-<event>/{workspace,outputs}/`; `dashboard` and `register-xlsx` default to `outputs/`; new `run-path`. Old free-form workspaces: `ingest --legacy-out`.
- Contribution layout `samples/<slug>/` with `pmlc.py check-samples` and `tools/make-public-sample.py --slug`.
- Local setup: `requirements.txt`, `requirements-dev.txt`, and a README 'Requirements and local setup' section.

## 0.1.0 (2026-10-15)

- First public release: 23 skills (core analysis and stakeholder coaches), the `pmlc.py` engine, the Learning Cluster ontology (15 entities × 5 tiers × 7 relations, sub-divisions S1–S14), Learnings Register schema, comparison method, Claude Code plugin and marketplace manifests, `AGENTS.md` and `.agents/skills` for Codex, sample-preparation tool, tests.
