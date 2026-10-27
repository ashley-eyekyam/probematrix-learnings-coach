# learnings-coach (start here)

The hub skill. It sets up the analysis folder for one ProbeMatrix export, works out with you what you want from it, shows you a numbered plan and **waits for your OK**, then runs the other skills in order. Every other skill relies on it.

## What it is for

- Turning a ProbeMatrix findings export (an `.xlsx` file) into a workspace the other skills can read, in one step.
- Telling you, in two or three lines, what the investigation holds and where its data has problems.
- Working out your request. When it is not clear, the hub asks **one question at a time**, each with two to four suggestions taken from the export.
- Planning the work: a named preset (such as `leadership` or `first-48-hours`), a set of audiences or named skills. You see the plan before anything runs.
- Running the plan step by step, passing each skill's check, and finishing with one index page of everything made.
- Pointing you to what the organisation does next: review and sign-off, distribution, the cascade record and the follow-up log. The hub never signs off for you and never writes owners or due dates.

You do not need to name this skill. Your agent starts it whenever you share a ProbeMatrix export.

## How to start it

- "Here is a ProbeMatrix export. What should our organisation learn from it?"
- "Use the learnings coach on this export. I need something for the supervisors by Monday."
- "Plan the leadership packs from samples/2020-09-24-hazira-gas-release-fire, and show me the plan first."

## What it needs

- A ProbeMatrix **findings** export (`.xlsx`). A CAPA Planner export is refused, because it holds actions, not findings.
- Python 3.9 or newer with `openpyxl`, which your agent uses to run the engine. See [Getting started](../Getting-started.md).
- A short name for the run: the site and the event in lowercase words joined by hyphens, for example `hazira-gas-release-fire`. Your agent proposes one.
- Two answers, asked once and one at a time: what the learnings are for, and which jurisdiction applies (India, the UK, the US or the EU).
- The whole `skills/` folder installed. Every skill uses the engine and references inside `learnings-coach`, so a single skill copied on its own cannot run.

## Engine commands and flags

The hub works in five steps:

```bash
pmlc setup <export.xlsx> --slug <site>-<event> [--date YYYY-MM-DD] [--root <writable folder>] [--overlay india-process-site]
pmlc run-manifest <ws> --intended-use "internal learning" --jurisdiction in
pmlc facts <ws>
pmlc plan <ws> --workflow <preset>        # or --audiences board,supervisors  or --skills causal-map
pmlc plan <ws> --next
pmlc check-all <ws> --strict
pmlc index <ws>
```

1. **Set up.** [setup](../commands/setup.md) runs ingest, classify, profile, causal, timeline and interfaces, and prints one summary: the unresolved roles, the profile flags and the workspace path. `--date` corrects a wrong summary-sheet date, `--root` puts the run folder somewhere writable when the upload folder is read-only (as in the Claude app), and `--overlay` adds an industry's role words. [run-manifest](../commands/run-manifest.md) records `--intended-use` and `--jurisdiction`.
2. **Work out the intent.** The hub maps your request to one of the nine presets in `workflows.json`, a set of audiences, or one or more of the 33 skills. For a broad request ("what should we learn from this?") it ranks the tiers with [facts](../commands/facts.md): by priority-1 learnings per tier (`p1_by_tier`) when a register exists, or by finding counts per tier before there is one. It then suggests a preset, for example `full-cascade`. When you name a file type or a channel (a Word board paper, slides for a workshop, toolbox-talk sheets, a printed checklist, an email digest, a quiz for your learning system, the causal map as a picture, another language, calendar reminders), the plan names the skill and its [pack](../commands/pack.md) flag, such as `frontline-learning-cards` with `--layout toolbox`.
3. **Plan and confirm.** [plan](../commands/plan.md) resolves the steps and what each needs, marks the ones already done, and lists steps whose skill arrives in a later phase as planned (they are skipped). The hub shows you the numbered plan and waits for your OK.
4. **Run the plan.** `plan --next` names the next step not yet done. The hub follows that skill, runs its commands and passes its gate: [check-pack](../commands/check-pack.md) `--strict` for a pack, [check-register](../commands/check-register.md) `--strict` for the register. `plan --next` exits 2 when the plan is complete.
5. **Finish.** [check-all](../commands/check-all.md) `--strict` checks every pack once more and [index](../commands/index.md) writes `outputs/index.html`. The hub gives you the HTML paths first.

After that, the hub points you to the organisation's own steps: [sign-off](../commands/sign-off.md) once you have reviewed a file (it runs only when you say you reviewed it and give your role), `--classification` and `--distribution` at sign-off, and [templates](../commands/templates.md) `distribution` (who received which pack) and `verification` (whether each learning was applied). It can also run [check-language](../commands/check-language.md) on its own, with `--share`.

## What you get

- The run folder `<export folder>/pmlc-runs/<date>-<site>-<event>/`, with `workspace/` and `outputs/`, and `run-manifest.json` beside them (see [Files and folders](../Files-and-folders.md)).
- A short summary of the export and its data-quality flags.
- A numbered plan (`workspace/plan.json`), shown to you before any step runs.
- The packs, the register or both, each checked, and `outputs/index.html` listing every output.
- A list of the next steps for the organisation, with the commands to run when it is ready.

## Worked example (Hazira)

On the public Hazira sample, `setup` printed `Ingested 436 findings and 46 evidence items`, 87 unresolved roles (with the `india-process-site` overlay) and nine profile flags, among them:

- the four investigative follow-up columns are empty on every finding;
- no finding is marked "User Edited";
- the investigation status is `in_progress`, so outputs are draft learnings.

`facts` without a register gave the tier counts `T1: 227; T2: 219; T3: 247; T4: 63; T5: 1; T9: 87` and `p1_by_tier: not available (no register)`. With the sample register it listed eleven priority-1 learnings for each of T1 to T4 and seven for T5, so the hub would suggest `full-cascade`.

`plan --workflow first-48-hours` printed:

```text
Plan: first-48-hours (First 48 hours: a draft register, an alert and the supervisor briefing)
 1. engine:ingest [done]
 2. engine:classify [done]
 3. learnings-register [todo] (mode draft)
      gate: check-register --strict
 4. safety-alert [planned for v2.0, Phase 6]
 5. supervisor-coach [todo]
      gate: check-pack --strict
Next: step 3
```

(The plan also prints each step's commands; they are left out here.) The hub would show this plan and wait. Sign-off is refused on Hazira because the investigation is still in progress, so every output stays a draft.

## Related skills

- [learning-clusters](learning-clusters.md): resolves the roles the rules could not place.
- [organisation-learning-map](organisation-learning-map.md): the whole-organisation map and dashboard.
- [learnings-register](learnings-register.md): the formal register of learnings, the first step of most presets.
- The full list, grouped by audience: [Skills](../Skills.md). The presets: [Workflows and recipes](../Workflows-and-recipes.md).
