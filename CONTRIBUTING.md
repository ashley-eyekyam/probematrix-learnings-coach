# Contributing

Contributions are welcome: new audience skills, taxonomies for other sectors (healthcare, mining, aviation, construction), engine improvements and public-record samples.

- Set up once: `python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt` (see the README section "Requirements and local setup"). Run `.venv/bin/python -m pytest tests` before opening a pull request.
- Skills follow the Agent Skills format: `skills/<name>/SKILL.md` with `name` and `description` front matter. Keep shared material in `skills/learnings-coach/references/`.
- Every skill must respect `learning-principles.md`: grounded, blame-free, roles only.
- Samples and published runs go in `samples/<YYYY-MM-DD>-<site>-<event>/` (layout and rules in `samples/README.md`; `pmlc.py check-samples` must pass). Never add non-public or identifiable incident data.

Questions: ashley@eyekyam.com
