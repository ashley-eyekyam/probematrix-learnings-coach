# Changelog

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
