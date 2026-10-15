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
python3 $E ingest samples/<incident>/<export>.xlsx --out ws
python3 $E profile ws --out ws/profile.md
python3 $E classify ws
python3 $E dashboard ws --out ws/outputs/organisation-learning-map.html
python3 $E select ws --tier T2 --level 3 --brief      # feed an audience skill
```

Then follow the audience skill (e.g. `skills/board-brief/SKILL.md`) and write Markdown to `ws/outputs/`.

## Rules for agents

1. **Ground every sentence** in the export: cite Finding IDs and Evidence IDs. Add no outside facts about the incident.
2. **Just culture**: roles only, no personal names, no blame or punishment language, prefer system fixes over retraining.
3. **Count learnings, not finding instances.** Several findings can describe one condition.
4. Mark outputs "Learning purposes: not a statutory document" and keep the ProbeMatrix footer from `skills/learnings-coach/references/output-style.md`.
5. Do not commit real incident data that is not public record and de-identified. Use `tools/make-public-sample.py` and a zero-hit name scan before adding anything to `samples/`.

## Development

- Tests: `python3 -m pytest tests/` (they build a synthetic export; no real data needed).
- Keep each `SKILL.md` under ~150 lines; put shared material in `skills/learnings-coach/references/`.
- New audience skill: copy an existing audience skill, change the audience, the `select` filters and the structure, and add it to `references/audiences.md` and the README table.
