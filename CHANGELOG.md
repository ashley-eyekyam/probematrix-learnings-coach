# Changelog

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
