# Contributing

Contributions are welcome: new audience skills, taxonomies for other sectors (healthcare, mining, aviation, construction), engine improvements and public-record samples.

- Set up once: `python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt` (see the README section "Requirements and local setup"). Run `.venv/bin/python -m pytest tests` before opening a pull request.
- Skills follow the Agent Skills format: `skills/<name>/SKILL.md` with `name` and `description` front matter. Keep shared material in `skills/learnings-coach/references/`.
- New pack item kind: add it to `KINDS` in `skills/learnings-coach/scripts/pmlc_lib/pack/schema.py`, its Markdown in `_md_item` (`pack/markdown.py`) and HTML in `_html_item` (`pack/html.py`), a row in `references/pack-schema.md`, a minimal item in `MIN` in `tests/test_pack.py` and an example in `tests/fixtures/packs/all-kinds.json`.
- Every skill must respect `learning-principles.md`: grounded, blame-free, roles only.
- Samples and published runs go in `samples/<YYYY-MM-DD>-<site>-<event>/` (layout and rules in `samples/README.md`; `pmlc.py check-samples` must pass). Never add non-public incident data. For a public-record incident, the official report and ProbeMatrix material (export, report, outputs) may be included unmodified, with no name scan required; generated learnings still follow just culture (roles only, no blame).

## Workflow

1. **Issue.** Open an issue first (use the Feature or Bug template), or comment on an existing one.
2. **Branch.** Branch from `main`: `feature/`, `fix/` or `docs/` plus `<issue#>-<slug>`, such as `fix/12-classify-overrides`. Work for v2.0 goes on `feature/v2.0-features-edition` under issue #1.
3. **Commits.** Small and focused, with messages of the form `<type>(<area>): <what> (#N)`.
4. **Tests.** Run `.venv/bin/python -m pytest tests` and, if you changed samples, `python3 skills/learnings-coach/scripts/pmlc.py check-samples`.
5. **Pull request.** Open it against `main` using the template, with "Closes #N" in the body. Pull requests are merged with a merge commit.

The de-identification tools (`scan-names`, `--names`) stay available for organisations' own runs.

Questions: ashley@eyekyam.com
