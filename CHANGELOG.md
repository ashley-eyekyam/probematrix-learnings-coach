# Changelog

## [Unreleased] (v2.0.0)

- Workflow: every change starts with an issue and a branch; v2.0 work happens on `feature/v2.0-features-edition` under epic issue #1. AGENTS.md and CONTRIBUTING.md describe the workflow, and `.github/` adds pull request, feature and bug templates.

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
