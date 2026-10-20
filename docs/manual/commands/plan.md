# plan

## What it does

Turns a request into a numbered plan of steps, in the order they must run, and writes it to `plan.json` in the workspace. The request is one of:

- a **workflow preset** from `references/workflows.json`, such as `leadership` or `full-cascade`;
- a list of **audiences** from `references/audiences.json`, such as `board,supervisors`;
- a list of **skills**, such as `board-brief,supervisor-coach`.

plan reads each skill's `skill.json` and adds what the skill needs first. Every skill needs the workspace, so ingest is always step 1; a skill that filters by tier needs `clusters.json`, so classify comes before it. The steps are sorted so that nothing runs before what it needs, keeping the preset's own order wherever it can.

Each step gives:

- the skill to follow, or the engine command (`engine:classify`);
- its state: **done**, **todo** or **planned**;
- the engine commands to run, with your real paths filled in;
- any question to ask the user first (for example which report a comparison is against);
- the **gate** to pass before moving on: check-pack in strict mode for a pack, check-register in strict mode for the register, and an approved review as well when the skill's output is meant for outside the organisation (the board brief and the supply-chain pack).

A step is **done** only when its output is current:

- an engine step, when its file exists and [status](status.md) says it is current. After a re-ingest of a changed export, classify shows as todo again;
- a pack step, when `<run>/outputs/<pack>.json` exists and its last [check-pack](check-pack.md) passed on the file as it is now. Editing the pack after the check makes the step todo again;
- the register step, when the register passed check-register on its current content.

A preset step whose skill has not been released yet is listed as **planned for v2.0, Phase N** and skipped. It is not an error.

`plan.json` holds no dates and no absolute paths: commands use the placeholders `PMLC`, `<ws>` and `<run>`, so the same request on the same workspace always writes the same file. Only the printed plan fills in the paths.

## When to use it

After [ingest](ingest.md) and [classify](classify.md), to agree the work with the person who asked before any pack is written. The agent shows the numbered plan and waits for an OK. Then, after each step, `--next` tells the agent what comes next.

## Synopsis

```text
pmlc plan ws (--workflow NAME | --audiences A,B | --skills S,T | --next) [--json]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--workflow` | a preset name | | Plan a preset from `workflows.json`: first-48-hours, full-cascade, leadership, assurance, investigation-quality, action-design, sister-sites, training or follow-up |
| `--audiences` | ids, comma-separated | | Plan the skill for each audience, through `audiences.json` (for example `board` is the board brief) |
| `--skills` | names, comma-separated | | Plan these skills |
| `--next` | none | | Rebuild the saved plan from the workspace's current state and print only the next step to do. Exits 2 when every step is done or planned |
| `--json` | none | | Print the plan as one JSON object instead of the numbered list |
| `-h`, `--help` | none | | Show the flags and stop |

Give exactly one of `--workflow`, `--audiences`, `--skills` and `--next`.

## Examples

Plan the leadership preset on the Hazira sample, after ingest and classify (paths shortened):

```bash
python3 $E plan $WS --workflow leadership
```

```text
Plan: leadership (Leadership: register, site leadership, top management and board)
 1. engine:ingest [done]
 2. engine:classify [done]
 3. learnings-register [todo]
      python3 skills/learnings-coach/scripts/pmlc.py select hazira/…/workspace --preset learnings-register:top
      python3 skills/learnings-coach/scripts/pmlc.py check-register hazira/…/workspace hazira/…/outputs/learnings-register.json --strict
      python3 skills/learnings-coach/scripts/pmlc.py register-xlsx hazira/…/outputs/learnings-register.json
      python3 skills/learnings-coach/scripts/pmlc.py register-md hazira/…/workspace hazira/…/outputs/learnings-register.json
      gate: check-register --strict
 4. site-leadership-coach [todo]
      …
 6. board-brief [todo]
      …
      gate: check-pack --strict, approved review
Next: step 3
```

A preset with a skill that has not been released yet:

```bash
python3 $E plan $WS --workflow first-48-hours
```

```text
…
 3. learnings-register [todo] (mode draft)
      …
 4. safety-alert [planned for v2.0, Phase 6]
 5. supervisor-coach [todo]
      …
Next: step 3
```

Plan by audience, then ask for the next step after each one is checked:

```bash
python3 $E plan $WS --audiences board,supervisors
python3 $E plan $WS --next
```

When everything is done, `--next` prints "The plan is complete: every step is done or planned for a later phase." and exits 2.

## Common problems

- **"unknown skill: …".** The name is not a skill folder, and the preset does not mark it as planned. The message lists the skills.
- **"unknown workflow: …" or "unknown audience: …".** The message lists the presets or the audience ids.
- **"cycle: a -> b -> a".** Two skills' manifests each need what the other makes. Fix the `requires` lists in their `skill.json`.
- **"nothing produces '…', which … requires".** A `requires` entry names something no engine command or released skill makes. Check the name against `references/artefacts.json`.
- **"no plan in …".** `--next` needs a plan made first with `--workflow`, `--audiences` or `--skills`.
- **A step stays todo after you wrote its pack.** Run [check-pack](check-pack.md) on it: a step is done only after a passing check of the file as it is now.
- **[status](status.md) shows plan.json as stale.** Something in the workspace changed since the plan was made. Run plan again, or `--next`.

## Related

- [status](status.md) shows the state the plan reads.
- [check-pack](check-pack.md) and [check-register](check-register.md) are the gates.
- [Workflows and recipes](../Workflows-and-recipes.md) shows the commands in the order a real job uses them.
