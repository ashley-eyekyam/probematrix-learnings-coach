# Contributing

Contributions are welcome: new audience skills, taxonomies for other sectors (healthcare, mining, aviation, construction), engine improvements and public-record samples.

- Set up once: `python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt` (see the README section "Requirements and local setup"). Run `.venv/bin/python -m pytest tests` before opening a pull request.
- Skills follow the Agent Skills format: `skills/<name>/SKILL.md` with `name` and `description` front matter. Keep shared material in `skills/learnings-coach/references/`.
- New pack item kind: add it to `KINDS` in `skills/learnings-coach/scripts/pmlc_lib/pack/schema.py`, its Markdown in `_md_item` (`pack/markdown.py`) and HTML in `_html_item` (`pack/html.py`), a row in `references/pack-schema.md`, a minimal item in `MIN` in `tests/test_pack.py` and an example in `tests/fixtures/packs/all-kinds.json`.
- Every skill must respect `learning-principles.md`: grounded, blame-free, roles only.
- Samples and published runs go in `samples/<YYYY-MM-DD>-<site>-<event>/` (layout and rules in `samples/README.md`; `pmlc.py check-samples` must pass). Never add non-public incident data. For a public-record incident, the official report and ProbeMatrix material (export, report, outputs) may be included unmodified, with no name scan required; generated learnings still follow just culture (roles only, no blame).

## Skill skeleton

Every skill except the hub (`learnings-coach`) uses the same `##` headings, in this order; other headings may sit between them. `tests/test_skills.py` checks them.

1. **Before you start**: link `learnings-coach/references/skill-common.md` §1–§2 and list what the skill needs (the same names as `requires` in its `skill.json`).
2. **Gather**: the `PMLC select` commands and item generators (`causal-item`, `table-item`, `timeline-item`, `register-items`), one comment per command.
3. **Write**: one section-spec table, `| § | id | Heading | Content rule | Kind | Count |`, one row per section id and kind. An optional `bottom_line` row gives the bottom-line count. The ids, kinds and counts must equal the skill's entry in `references/pack-profiles.json`. Counts read `N`, `up to N` (min 1), `N–M`, `at least N`, or `optional` / `optional, up to N` (min 0); text in parentheses is a note. Prefer `up to N` to an open `at least N`. Add one line `Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/<pack>.json (repository only)`.
4. **If the evidence is thin**: the skill's own thin case (`skill-common.md` §6 covers the rest).
5. **Not covered here**: what the skill does not do, and which skill does.
6. **Check and hand over**: "Run `skill-common.md` §4, then tick §5", the literal `PMLC check-pack … --strict` and `PMLC pack …` lines, then one `PMLC pack … --format <names>` or `--layout <name>` line for each format the skill offers, plus any skill-specific check. The offered names go in `formats` in its `skill.json` (registered formats and layouts only; `skill-common.md` §8).

Also:

- The description names ProbeMatrix and the export, opens in the third person ("Produces…"), says "Use when…", stays at 1024 characters or fewer, and adds "Not for … (use `<sibling>`)" for each overlapping sibling listed in `OVERLAPS` in `tests/test_skills.py`.
- Cite `learnings-coach/references/learning-principles.md` by that full path, and name references as `learnings-coach/references/<file>`. Every reference a SKILL.md names must exist.
- Do not repeat what `skill-common.md` says: no `PMLC = python3 …` definition and no `data_quality` / `exclusions` sentence.
- Keep the SKILL.md at 150 lines or fewer, and mark any path under `samples/`, `tools/`, `docs/`, `tests/` or `evals/` "(repository only)".

## Workflow

1. **Issue.** Open an issue first (use the Feature or Bug template), or comment on an existing one.
2. **Branch.** Branch from `main`: `feature/`, `fix/` or `docs/` plus `<issue#>-<slug>`, such as `fix/12-classify-overrides`. Work for v2.0 goes on `feature/v2.0-features-edition` under issue #1.
3. **Commits.** Small and focused, with messages of the form `<type>(<area>): <what> (#N)`.
4. **Tests.** Run `.venv/bin/python -m pytest tests` and, if you changed samples, `python3 skills/learnings-coach/scripts/pmlc.py check-samples`.
5. **Pull request.** Open it against `main` using the template, with "Closes #N" in the body. Pull requests are merged with a merge commit.

The de-identification tools (`scan-names`, `--names`) stay available for organisations' own runs.

Questions: ashley@eyekyam.com
