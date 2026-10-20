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
python3 $E ingest path/to/<export>.xlsx --slug <site>-<event> [--date YYYY-MM-DD]
WS=path/to/pmlc-runs/<YYYY-MM-DD>-<site>-<event>/workspace      # printed by ingest
python3 $E profile $WS --out $WS/profile.md
python3 $E classify $WS
python3 $E status $WS                          # which derived files are stale after a re-ingest
python3 $E dashboard $WS                       # -> <run>/outputs/organisation-learning-map.html
python3 $E select $WS --tier T2 --level 3 --brief      # feed an audience skill
python3 $E check-language $WS <run>/outputs/board-brief.json   # just-culture language check (check-pack runs it too)
python3 $E pack $WS <run>/outputs/board-brief.json  # -> board-brief.html + .md (DRAFT until signed off)
python3 $E sign-off $WS <run>/outputs/board-brief.json --role "<reviewer's role>" --status approved   # only after a person says they reviewed it
```

The user manual, `docs/manual/Home.md` (repository only; also on the project wiki), documents every skill, command and flag with Hazira examples, including sharing a masked copy outside the organisation (`--share external|public`).

Then follow the audience skill (e.g. `skills/board-brief/SKILL.md`) and write its pack JSON to `<run>/outputs/<skill>.json`, then run `python3 $E check-pack $WS <pack>` and `python3 $E pack $WS <pack>` (`python3 $E run-path $WS` prints the folder). `learnings-register` writes a register JSON instead: check it with `python3 $E check-register $WS <register.json>`, then `python3 $E register-xlsx <register.json>` writes the workbook and `python3 $E register-md $WS <register.json>` writes `learnings-register.md` (never hand-write it; `check-register --strict` makes the priority-1 rule a problem). `python3 $E causal-item $WS` prints the top causal links as a ready graph item for a pack. Both checks also run the just-culture language lint (rules JC1 to JC12); `python3 $E check-language $WS <json>` runs it alone. After a person has reviewed a pack or register, `python3 $E sign-off $WS <file> --role "<their role>"` records it (`handling` block with a content hash; refused until the investigation status is completed, and while no finding is marked as edited by a person; any later edit reverts it to draft).

## Rules for agents

1. **Ground every sentence** in the export: cite Finding IDs and Evidence IDs. Add no outside facts about the incident.
2. **Just culture**: roles only, no personal names, no blame or punishment language, prefer system fixes over retraining.
3. **Count learnings, not finding instances.** Several findings can describe one condition.
4. Mark outputs "Learning purposes: not a statutory document" and keep the ProbeMatrix footer from `skills/learnings-coach/references/output-style.md`.
5. **Run folders are strict:** `<export-dir>/pmlc-runs/<YYYY-MM-DD>-<site>-<event>/{workspace,outputs}/`. `pmlc-runs/` is git-ignored. Do not commit real incident data that is not public record. For a public-record incident, committed samples may include the official public report and ProbeMatrix material (export, report, outputs) unmodified; no name scan is required. Generated learnings still follow just culture (roles only, no blame). De-identification tooling (`scan-names`, `--names`) remains available for organisations' own runs. To publish a run, create `samples/<slug>/` with `tools/make-public-sample.py --slug <slug>`, copy the outputs into `samples/<slug>/outputs/`, and add a README; `python3 $E check-samples` must pass.

## Development

- Setup: `python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt`. Tests: `.venv/bin/python -m pytest tests` (they build a synthetic export; no real data needed; the JS tests need Node and are skipped without it).
- Keep each `SKILL.md` under ~150 lines; put shared material in `skills/learnings-coach/references/`.
- New audience skill: copy an existing audience skill, change the audience, the `select` filters and the structure, and add it to `references/audiences.md` and the README table.

### Workflow: issue, branch, pull request

- Every change starts with a GitHub issue and a branch; nothing is committed to `main` directly. Branch names: `feature/`, `fix/` or `docs/` plus `<issue#>-<slug>`.
- **v2.0 Features Edition:** all v2.0 work goes only on `feature/v2.0-features-edition`, tracked by epic issue #1. Check the current branch before the first commit of a session.
- Commit messages read `<type>(<area>): <what> (#N)`, for example `fix(engine): keep role overrides in classify (#1)`. Push after every task.
- Each v2.0 phase ends with an annotated tag `v2.0.0-alpha.N` (version `2.0.0aN`), a CHANGELOG entry, the phase ticked in the issue and a summary comment. Merge `main` into the branch when it moves; never rebase.
- The branch reaches `main` through one pull request ("Closes #1"), merged with a merge commit (not squash or rebase).
