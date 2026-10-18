# Installing the ProbeMatrix Learnings Coach

All hosts need **Python 3.9+** and **openpyxl** (`pip install -r requirements.txt`, or `sudo apt install python3-openpyxl` on Debian/Ubuntu). The skills call `skills/learnings-coach/scripts/pmlc.py`. Full list of requirements and the local developer setup: [README, Requirements and local setup](../README.md#requirements-and-local-setup).

## Claude Code

```
/plugin marketplace add ashley-eyekyam/probematrix-learnings-coach
/plugin install probematrix-learnings-coach@probematrix
/reload-plugins
```

Or from a local clone: `/plugin marketplace add ./probematrix-learnings-coach`.

Check with `/plugin`; the skills appear as `probematrix-learnings-coach:<skill>`. Then attach or point to an export and ask, e.g. *"Use the learnings coach on samples/…xlsx and give me the supervisor coach."*

## Claude desktop / Cowork

Install the plugin from the same marketplace through the app's plugin settings, or upload the plugin folder if your workspace allows custom plugins. Attach the export to the conversation.

## Getting updates

Plugins do not update themselves unless you turn on auto-update. To get the latest version:

- **Claude Code:** `/plugin marketplace update probematrix`, then `/reload-plugins`.
- **Claude app:** open the plugin settings, find the `probematrix` marketplace and choose Update.

To check which version you have, ask the agent: *"Run the Learnings Coach engine with `--version` and tell me the result."* It prints, for example, `pmlc 2.0.0a1`.

## Pinning a version

The marketplace follows the `main` branch unless you name a tag with `#<tag>`:

```
/plugin marketplace add ashley-eyekyam/probematrix-learnings-coach#v0.3.5            # stable 0.3.5
/plugin marketplace add ashley-eyekyam/probematrix-learnings-coach#v2.0.0-alpha.1    # the v2.0 alpha
```

You can have only one marketplace named `probematrix` at a time. To change the pin, remove the marketplace first and then add it again:

```
/plugin marketplace remove probematrix
/plugin marketplace add ashley-eyekyam/probematrix-learnings-coach#v0.3.5
/plugin install probematrix-learnings-coach@probematrix
```

## Going back to stable

While v2.0 is in testing, `main` carries an alpha. To go back to the stable release, pin `v0.3.5` as in [Pinning a version](#pinning-a-version), then run `/reload-plugins` (or restart the app). To follow `main` again later, remove the marketplace and add it without a tag.

## OpenAI Codex (CLI, IDE, app)

Codex discovers skills in `.agents/skills` from the working directory up to the repository root, and in `~/.agents/skills` for all projects.

- **Per project**: clone the repo and run Codex inside it. `.agents/skills` is a link to `skills/`, and `AGENTS.md` gives Codex the working rules.
- **All projects**: `./tools/install-codex.sh` copies the skills to `~/.agents/skills`. Restart Codex if they do not appear.

Invoke a skill by name, e.g. *"Use $learnings-coach on ./export.xlsx"*, or just describe the task.

If `.agents/skills` shows as a plain file on Windows, copy `skills/` to `.agents/skills/` instead.

## ChatGPT

Where your ChatGPT plan supports skills (desktop app or plugins), add the skill folders from `skills/` and keep `learnings-coach` alongside the others, because they all use its engine and references. Code execution must be available for `pmlc.py`.

## Other agents

Any agent that reads the Agent Skills format (`SKILL.md` with `name` and `description`) can use the `skills/` folder directly. Agents that read `AGENTS.md` get the repo rules from it.

## Verify

```bash
python3 skills/learnings-coach/scripts/pmlc.py -h
.venv/bin/python -m pytest tests        # see README "Requirements and local setup"; plain python3 skips tests without openpyxl
```
