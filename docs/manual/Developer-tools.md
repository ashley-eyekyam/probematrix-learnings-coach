# Developer tools

This page is for people who maintain the coach or contribute to it: the tools in the repository's `tools/` folder, the eval runner, the tests and the environment variables. None of these are installed with the skills; they live only in the repository. Run them from the repository root.

## Set up

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest tests -q        # the whole test suite; it builds a synthetic export, no real data needed
.venv/bin/ruff check .                     # style checks (Python 3.9, lines up to 120 characters)
```

The JavaScript tests need Node.js and are skipped without it.

## `tools/make-public-sample.py`

Prepares a ProbeMatrix export for publication as a public sample. It:

1. keeps only the five sheets the coach reads (Incident Summary, Identified Findings, Evidence Links, Causal Chain, Analysis Statistics);
2. applies any summary-sheet corrections you give with `--set`;
3. strips the workbook's metadata (author, company, comments, headers and footers, defined names), unhides hidden rows, columns and sheets, blanks the Investigating Officer, Supervisor at Time and Investigation Team fields, and drops narrative lines that start with To:, From: or Cc:;
4. with `--names`, runs a name scan and writes nothing if any name is found.

```text
python3 tools/make-public-sample.py src [dst] [--slug SLUG] [--samples-root DIR] [--names FILE]
                                    [--keep-field NAME] [--set "Field=Value"]
```

| Flag | Value | Default | What it does |
|---|---|---|---|
| `src` | file | required | The export to prepare |
| `dst` | file | none | The output `.xlsx`. Leave it out when you give `--slug` |
| `--slug` | `YYYY-MM-DD-<site>-<event>` | none | Write `<samples-root>/<slug>/<slug>_probematrix-findings.xlsx`, the layout [check-samples](commands/check-samples.md) expects |
| `--samples-root` | folder | the repository's `samples/` | Where the sample folder goes |
| `--names` | file | none | Names and identifiers that must not appear, one per line. Keep this file outside the repository. Without it the scan is skipped |
| `--keep-field` | field name | none | Keep this personal summary field instead of blanking it. Repeatable |
| `--set` | `"Field=Value"` | none | Override a summary-sheet field, for example `--set "Date=2020-09-24"`. Repeatable |

Example, writing into a scratch folder:

```bash
python3 tools/make-public-sample.py samples/2020-09-24-hazira-gas-release-fire/2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx --slug 2020-09-24-hazira-gas-release-fire --samples-root pubsamples --names names.txt
```

```text
Name scan passed (1 names). Kept sheets: ['Incident Summary', 'Identified Findings', 'Evidence Links', 'Causal Chain', 'Analysis Statistics']. Wrote pubsamples/2020-09-24-hazira-gas-release-fire/2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx
```

Only publish exports of incidents that are public record and that you have the right to publish.

## `tools/release.py`

Bumps the version everywhere it lives: `__version__` in the engine (the Python form, `2.0.0a4`) and `version` in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` (the semantic-version form, `2.0.0-alpha.4`). It prints the git tag command but never runs git. The version only ever changes through this tool.

```text
python3 tools/release.py version [--root DIR]
```

| Flag | Value | Default | What it does |
|---|---|---|---|
| `version` | `2.0.0`, `2.0.0a1` or `2.0.0rc1` | required | The new version |
| `--root` | folder | the repository root | The repository to update |

Example, on a scratch copy of the three files:

```bash
python3 tools/release.py 2.0.0a4 --root relroot
```

```text
updated relroot/skills/learnings-coach/scripts/pmlc.py
updated relroot/.claude-plugin/plugin.json
updated relroot/.claude-plugin/marketplace.json

git tag -a v2.0.0-alpha.4 -m "ProbeMatrix Learnings Coach 2.0.0-alpha.4"
Regenerate golden fixtures: PMLC_UPDATE_GOLDEN=1 .venv/bin/python -m pytest tests/test_pack.py -k golden
```

A malformed version changes nothing: `Version must look like 2.0.0, 2.0.0a1 or 2.0.0rc1, not '2.0'.`

## `tools/make-uat-inputs.py`

Writes the user-acceptance-test input files: three small synthetic exports (a reviewer downgrade vote, a renamed column, a CAPA Planner export) and two packs to check against them. Fictional event, no real data.

```text
python3 tools/make-uat-inputs.py [--out DIR]
```

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--out` | folder | `docs/uat/inputs` | Where to write the files |

```bash
python3 tools/make-uat-inputs.py --out uat
```

```text
wrote uat/uat-votes.xlsx
wrote uat/uat-renamed-header.xlsx
wrote uat/uat-capa-planner.xlsx
wrote uat/uat-votes-pack.json
wrote uat/uat-unlinked-pack.json
```

## `tools/smoke_sample.py`

A quick end-to-end check: ingests the Hazira sample into a temporary folder and checks the baseline numbers. It takes no flags and exits non-zero naming the failing check.

```bash
python3 tools/smoke_sample.py
```

```text
smoke OK: 436 findings, 46 evidence, register 0 problems
```

## `tools/sync-wiki.py`

Mirrors this manual (`docs/manual/`) into a local clone of the project's GitHub Wiki. The manual in the repository is the source; the wiki is a copy, replaced on every release.

- Page names: `Home.md` becomes `Home`, `X.md` becomes `X`, `commands/<n>.md` becomes `Command-<n>`, `skills/<n>.md` becomes `Skill-<n>`.
- Links between manual pages are rewritten to wiki links. A link to a page that does not exist, or one that leaves `docs/manual/`, stops the sync with an error, so link to other repository files with full GitHub addresses.
- Every page gets a header naming the version it documents, and `_Sidebar` and `_Footer` pages are generated.
- The pages the tool wrote are recorded in `<wiki-dir>/.pmlc-sync.json`. Only those are ever updated or deleted; a page someone wrote by hand is never overwritten unless you name it with `--adopt`.
- It never runs git. Commit and push the wiki clone yourself.

```text
python3 tools/sync-wiki.py --wiki-dir DIR [--manual-dir docs/manual] [--version V] [--check] [--adopt NAME ...]
```

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--wiki-dir` | folder | required | The local wiki clone (`git clone https://github.com/ashley-eyekyam/probematrix-learnings-coach.wiki.git`) |
| `--manual-dir` | folder | `docs/manual` | The manual to mirror |
| `--version` | text | the engine's version | The version named in each page header |
| `--check` | none | off | Write nothing; exit 1 if anything would change. Use it in a release check |
| `--adopt` | page names | none | Take over existing wiki pages this tool does not own, for example `--adopt Home` |

The first sync into an empty wiki clone. Without `--version`, the pages name the engine's own version, the one `pmlc --version` prints (here `pmlc 2.0.0a3`), so every page starts `> Documents ProbeMatrix Learnings Coach v2.0.0a3.`:

```bash
python3 tools/sync-wiki.py --wiki-dir wiki
```

```text
write Command-causal
write Command-causal-item
write Command-check-language
write Command-check-pack
…
```

Checking again with nothing changed exits 0:

```bash
python3 tools/sync-wiki.py --wiki-dir wiki --check
```

```text
unchanged Command-causal
unchanged Command-causal-item
unchanged Command-check-language
…
```

A wiki that already has a hand-written Home page is not overwritten:

```bash
python3 tools/sync-wiki.py --wiki-dir wiki2
```

```text
Refusing to overwrite wiki pages this tool does not own: Home
Re-run with --adopt NAME to take them over.
```

Taking it over:

```bash
python3 tools/sync-wiki.py --wiki-dir wiki2 --adopt Home
```

```text
write Command-causal
write Command-causal-item
write Command-check-language
…
```

A broken link stops the sync before anything is written, for example `error: commands/causal.md: link to missing manual page Skills.md` (exit code 1).

## `tools/install-codex.sh`

Installs the skills for OpenAI Codex at user level, by copying every folder under `skills/` into the Codex skills folder. It needs Python 3.9 or later.

```bash
tools/install-codex.sh
```

The target folder is `$CODEX_SKILLS_DIR` when set, otherwise `~/.agents/skills`.

## `evals/run_evals.py`

Checks and grades the eval set in `evals/evals.json`: prompts that should (or should not) trigger each skill, with machine-checkable expectations for the outputs.

| Command | What it does |
|---|---|
| `run_evals.py check [--file F]` | Checks the structure of the eval file, its paths, kinds and per-skill counts. The automatic checks run this |
| `run_evals.py grade <run-dir> [--ids 3,7] [--file F]` | Grades the machine expectations against a run folder's `outputs/` and `workspace/`. Expectations that need a person, such as which skill the agent chose, are reported as `manual` |

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--file` | file | `evals/evals.json` | The eval file |
| `--ids` | comma list | the evals whose outputs exist in the run | Grade only these evals (`grade` only) |

```bash
python3 evals/run_evals.py check
```

```text
71 evals over 23 skills: 25 trigger, 23 no-trigger, 23 collision
OK
```

Grading the Hazira run used in this manual, which holds a short hand-written board brief and the sample register:

```bash
python3 evals/run_evals.py grade hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire
```

```text
| id | skill | expectation | pass/fail |
|---|---|---|---|
| 7 | board-brief | pack_exists board-brief | pass |
| 7 | board-brief | check_pack_ok board-brief | pass |
| 7 | board-brief | language_clean board-brief | pass |
| 7 | board-brief | scope_equals board-brief | fail: scope is {"levels": [3, 4]} |
| 7 | board-brief | coverage_min board-brief >= 0.25 | fail: 0.01 |
| 7 | board-brief | routes_to board-brief | manual |
…
| 39 | learnings-register | check_register_ok learnings-register | pass |
…
```

It exits with code 1 when any machine check fails, as here: the short example brief covers too little of the investigation.

## Environment variables

| Variable | Read by | What it does |
|---|---|---|
| `PMLC_NAMES` | `check-pack`, `check-register`, `check-language` | A names file used when `--names` is not given. See [check-language](commands/check-language.md) |
| `PMLC_ORGS` | `check-pack`, `check-register`, `check-language` | An organisation names file used when `--orgs` is not given |
| `PMLC_UPDATE_GOLDEN` | `tests/test_pack.py` | Set to `1` to rewrite the golden Markdown fixtures: `PMLC_UPDATE_GOLDEN=1 .venv/bin/python -m pytest tests/test_pack.py -k golden`. Read the diff before committing |
| `CODEX_SKILLS_DIR` | `tools/install-codex.sh` | Where to install the skills for Codex (default `~/.agents/skills`) |

## Related

- [Commands](Commands.md): the engine's own commands.
- [CONTRIBUTING.md](https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/CONTRIBUTING.md) and [AGENTS.md](https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/AGENTS.md).
