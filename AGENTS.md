# AGENTS.md: ProbeMatrix Learnings Coach

Instructions for coding and analysis agents (OpenAI Codex, Claude Code, and any agent that reads AGENTS.md) working with this repository.

## What this repo is

A set of agent skills that turn one **ProbeMatrix investigation export** (`.xlsx`) into learnings for every part and level of an organisation. ProbeMatrix by Eyekyam is a human-in-the-loop, AI-assisted incident investigation service built on the four-level Human Factors Analysis and Classification System (HFACS). Contact: ashley@eyekyam.com.

## Where to start

- Skills live in `skills/<name>/SKILL.md` (Agent Skills format: YAML front matter with `name` and `description`, then instructions). `.agents/skills` points to the same folder for Codex.
- **Always start with `skills/learnings-coach/SKILL.md`.** It sets up the workspace and routes to the other 22 skills.
- The engine is `skills/learnings-coach/scripts/pmlc.py` (Python 3.9+, `pip install openpyxl`). Run `python3 skills/learnings-coach/scripts/pmlc.py -h`.
- Read `skills/learnings-coach/references/learning-principles.md` before writing any learning.

## Typical run

```bash
pip install openpyxl
E=skills/learnings-coach/scripts/pmlc.py
python3 $E setup path/to/<export>.xlsx --slug <site>-<event> [--date YYYY-MM-DD] [--overlay india-process-site] [--industry process]   # ingest, classify, profile, causal, timeline, interfaces
WS=path/to/pmlc-runs/<YYYY-MM-DD>-<site>-<event>/workspace      # printed by setup
python3 $E run-manifest $WS --intended-use "internal learning" --jurisdiction in --retention-review YYYY-MM-DD   # run-manifest.json: adds the Retention review and Statutory report lines
python3 $E open-questions $WS                   # what the export leaves open -> open_questions.json (--items: ready question items)
python3 $E facts $WS                           # headline numbers (tiers, levels, top-rated) to suggest a workflow
python3 $E evidence-audit $WS                  # -> <ws>/evidence_audit.json: engine-computed evidence strength, single-source and document-only counts; copy its strength into the register
python3 $E plan $WS --workflow leadership      # numbered plan -> <ws>/plan.json; show it and wait for the user's OK
python3 $E plan $WS --next                     # the next step to do, with its commands and gate (exit 2: the plan is complete)
python3 $E select $WS --preset board-brief     # a step's gather calls, as the plan prints them
python3 $E check-pack $WS <run>/outputs/board-brief.json --strict   # a pack step's gate (runs the language check too)
python3 $E pack $WS <run>/outputs/board-brief.json  # -> board-brief.html + .md (DRAFT until signed off)
python3 $E pack $WS <run>/outputs/board-brief.json --format html,md,docx,email --layout paper   # the page and Markdown, plus Word, an email digest and the board paper (--format replaces the default; formats: pack -h)
python3 $E strings extract $WS <run>/outputs/frontline-learning-cards.json --lang hi   # -> <pack>.strings.xlf for a translator
python3 $E strings apply $WS <run>/outputs/frontline-learning-cards.json <run>/outputs/frontline-learning-cards.strings.xlf --lang hi   # -> frontline-learning-cards-hi.json; a fluent speaker checks it
python3 $E check-all $WS --strict              # every pack and the register in outputs/
python3 $E render-all $WS                      # render every pack that passed its check, and the register
python3 $E index $WS                           # -> <run>/outputs/index.html, the front page: give the user this path first
python3 $E status $WS                          # which derived files are stale after a re-ingest
python3 $E sign-off $WS <run>/outputs/board-brief.json --role "<reviewer's role>" --status approved   # only after a person says they reviewed it
python3 $E purge <run> --keep outputs --yes   # delete the workspace after retention; run-manifest.json stays (no --yes: lists only)
```

`pack --format` takes a comma-separated list (default `html,md`): `docx`, `pptx`, `email`, `scorm`, `gift`, `qti`, `quiz-csv`, `csv`, `svg`, `png`, `graphml`, `bowtie-csv`, `ics` (needs `--start`), `srt`, `narration` and `normalised`; `--layout cards|field|toolbox|checklist|poster|paper` adds a print page, `--view learner` a copy without answers, `--brand brand.json` the organisation's name, colour and logo. Offer the formats the skill's `skill.json` lists; never pass `--start` with a date the user did not give. A translation from `strings apply` is AI-assisted until a fluent speaker checks it; never overwrite `<pack>.strings.*`, `<pack>-<lang>.json` or `<pack>.actions.csv` (the engine refuses). The individual commands stay: `setup` is `ingest`, `profile --out`, `classify`, `causal`, `timeline` and `interfaces` run in one go. The nine workflow presets are in `skills/learnings-coach/references/workflows.json`; `plan --audiences board,supervisors` or `--skills causal-map,interface-learnings` plans without a preset. A step marked "planned for v2.0, Phase N" is skipped. `dossier-index` writes the pack that lists the `dossier-F*.json` packs. `templates $WS adoption|distribution|verification` and `export-actions $WS --register <register.json>` write the files the organisation fills in, with owner, due-date and response columns blank; never fill them in.

The user manual, `docs/manual/Home.md` (repository only; also on the project wiki), documents every skill, command and flag with Hazira examples, including sharing a masked copy outside the organisation (`--share external|public`).

Then follow the audience skill (e.g. `skills/board-brief/SKILL.md`) and write its pack JSON to `<run>/outputs/<skill>.json`, then run `python3 $E check-pack $WS <pack>` and `python3 $E pack $WS <pack>` (`python3 $E run-path $WS` prints the folder). `learnings-register` writes a register JSON instead: check it with `python3 $E check-register $WS <register.json>`, then `python3 $E register-xlsx <register.json>` writes the workbook and `python3 $E register-md $WS <register.json>` writes `learnings-register.md` (never hand-write it; `check-register --strict` makes the priority-1 rule a problem); `python3 $E register-render $WS <register.json> --format docx,email` writes the register as a Word document and an email digest. `python3 $E compare $WS --register <register.json> --json` prints the comparator coverage tables (from `comparator.json` and `comparison-map.json`) as ready pack items. `python3 $E rec-review $WS <register.json> [--nine-m] [--table-item strength|spread|smart]` bands each recommendation (stronger, intermediate, weaker), flags weak fixes for deep causes and lists loops, SMART gaps and recipients (it reads a register, never a pack). `python3 $E causal-item $WS` prints the top causal links as a ready graph item for a pack; likewise `table-item $WS <clusters|tiers|relations|hubs|interfaces|evidence-types|entity-tier|hoc|adoption|nine-m>`, `register-items $WS --tier T3`, `timeline-item $WS --before incident` (or `--event-day` for the incident day) and `missed-opportunities $WS --timeline-item` (earlier recommendations and Failure-to-Correct findings, dated before the incident; writes `missed_opportunities.json`) print ready table, learning and timeline items, `facts $WS --json` prints the headline numbers, `crosswalk $WS --framework iso45001|psm|rmp|seveso|rbps|icmm|india [--register R] [--table-item]` maps the register to a standard's clauses (a table item for a pack; never a claim of compliance), `hfacs-profile $WS [--table-item heatmap|feeds|recurrence]` writes `hfacs_profile.json` (level x subcategory heat map, recurring codes, causal feeds), `nine-m-seed $WS` scores every finding against the nine Ms (9M) and prints the M profile (`nine_m_seed.json`; a CAPA Planner workbook is refused; `select $WS --m M8 [--m-secondary]` then selects through the 9M lens), the 9M interview runs one question at a time with `nine-m-suggest $WS --m M8 --step relevance --record` and `nine-m-answer $WS --q Q02 --choice 1` (`nine_m_session.json`; `nine-m-replay $WS --accept-recommended` scripts a demonstration session), `nine-m-actions-template $WS <pack>` writes the blank actions sheet of a nine-m-analysis pack (Owner, Due date and Status blank, never overwritten), and `pack-xlsx $WS <pack> --kind test_point|question|table` writes those items to Excel. Both checks also run the just-culture language lint (rules JC1 to JC12); `python3 $E check-language $WS <json>` runs it alone. After a person has reviewed a pack or register, `python3 $E sign-off $WS <file> --role "<their role>"` records it (`handling` block with a content hash; refused until the investigation status is completed, and while no finding is marked as edited by a person; any later edit reverts it to draft).

## Rules for agents

1. **Ground every sentence** in the export: cite Finding IDs and Evidence IDs. Add no outside facts about the incident.
2. **Just culture**: roles only, no personal names, no blame or punishment language, prefer system fixes over retraining.
3. **Count learnings, not finding instances.** Several findings can describe one condition.
4. Mark outputs "Learning purposes: not a statutory document" and keep the ProbeMatrix footer from `skills/learnings-coach/references/output-style.md`.
5. **Run folders are strict:** `<export-dir>/pmlc-runs/<YYYY-MM-DD>-<site>-<event>/{workspace,outputs}/`. `pmlc-runs/` is git-ignored. Do not commit real incident data that is not public record. For a public-record incident, committed samples may include the official public report and ProbeMatrix material (export, report, outputs) unmodified; no name scan is required. Generated learnings still follow just culture (roles only, no blame). De-identification tooling (`scan-names`, `--names`) remains available for organisations' own runs. To publish a run, create `samples/<slug>/` with `tools/make-public-sample.py --slug <slug>`, copy the outputs into `samples/<slug>/outputs/`, and add a README; `python3 $E check-samples` must pass.

## Development

- Setup: `python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt`. Tests: `.venv/bin/python -m pytest tests` (they build a synthetic export; no real data needed; the JS tests need Node and are skipped without it; with Node, run `npm ci --prefix tests/js` once for the accessibility tests, which fail without those packages).
- Keep each `SKILL.md` under ~150 lines; put shared material in `skills/learnings-coach/references/`.
- New audience skill: copy an existing audience skill, change the audience, the `select` filters and the structure, and add it to `references/audiences.md` and the README table.

### Workflow: issue, branch, pull request

- Every change starts with a GitHub issue and a branch; nothing is committed to `main` directly. Branch names: `feature/`, `fix/` or `docs/` plus `<issue#>-<slug>`.
- **v2.0 Features Edition:** all v2.0 work goes only on `feature/v2.0-features-edition`, tracked by epic issue #1. Check the current branch before the first commit of a session.
- Commit messages read `<type>(<area>): <what> (#N)`, for example `fix(engine): keep role overrides in classify (#1)`. Push after every task.
- Each v2.0 phase ends with an annotated tag `v2.0.0-alpha.N` (version `2.0.0aN`), a CHANGELOG entry, the phase ticked in the issue and a summary comment. Merge `main` into the branch when it moves; never rebase.
- The branch reaches `main` through one pull request ("Closes #1"), merged with a merge commit (not squash or rebase).

Files the organisation fills in: `python3 $E templates $WS (adoption|distribution|verification)` writes a blank `adoption.csv`, `distribution.csv` or `verification.jsonl` (never overwrites). `python3 $E export-actions $WS [--profile generic|enablon|intelex|cority|sap-ehs] [--names FILE]` writes `actions.csv` and `actions.json` with the owner, due, status, CAPA and effectiveness columns left blank.

Translation: `python3 $E strings extract $WS <pack.json> [--to xliff|csv] [--lang hi]` writes the text for a translator (never overwrites); `python3 $E strings apply $WS <pack.json> <strings-file> --lang hi` writes `<pack>-hi.json` (`translation_of`, `lang`), which `check-pack` compares with the source pack. Never write the translation yourself as if a person had checked it: every translated page says it needs a fluent speaker's check.
