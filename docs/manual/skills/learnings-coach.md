# learnings-coach (start here)

The hub skill. It sets up the analysis folder for one ProbeMatrix export, tells you what the investigation contains, and sends your request to the right skill. Every other skill relies on it.

## What it is for

- Turning a ProbeMatrix findings export (an `.xlsx` file) into a workspace the other skills can read.
- Telling you, in two or three lines, what the investigation holds and where its data has problems.
- Choosing the right skill for your request: an audience skill (for example supervisors or the board) or an analysis skill (for example the causal map or the register).
- Running the language check, and, only when you say you have reviewed a file, the sign-off step.

You do not need to name this skill. Your agent starts it whenever you share a ProbeMatrix export.

## How to start it

- "Here is a ProbeMatrix export. What should our organisation learn from it?"
- "Set up the learnings coach on this export and tell me what the investigation contains."
- "Use the learnings coach on samples/2020-09-24-hazira-gas-release-fire and give me the supervisor coach."

## What it needs

- A ProbeMatrix **findings** export (`.xlsx`). A CAPA Planner export is refused, because it holds actions, not findings.
- Python 3.9 or newer with `openpyxl`, which your agent uses to run the engine. See [Getting started](../Getting-started.md).
- A short name for the run: the site and the event in lowercase words joined by hyphens, for example `hazira-gas-release-fire`. Your agent asks for it, or proposes one.

## Engine commands and flags

The hub runs the set-up steps once per export:

```bash
pmlc ingest <export.xlsx> --slug <site>-<event> [--date YYYY-MM-DD] [--root <writable folder>]
pmlc profile <ws> --out <ws>/profile.md
pmlc classify <ws> [--overlay india-process-site]
pmlc run-path <ws>
pmlc status <ws>
```

- [ingest](../commands/ingest.md) reads the export into the workspace. `--date` corrects a wrong summary-sheet date. `--root` puts the run folder somewhere writable when the upload folder is read-only (as in the Claude app). `--force` rebuilds an existing workspace. `--redact` replaces listed names with roles as the export is read (see [Review and sharing](../Review-and-sharing.md)).
- [profile](../commands/profile.md) writes `profile.md`, the summary the hub reads back to you.
- [classify](../commands/classify.md) places every finding with the functions and levels that own its learning.
- [run-path](../commands/run-path.md) prints the run folder, the outputs folder, the top rating and the incident date.
- [status](../commands/status.md) says which workspace files are out of date.

When routing, the hub selects by entity tag rather than entity number, for example `pmlc select <ws> --tag emergency` ([select](../commands/select.md)). After a skill writes a pack it runs [check-pack](../commands/check-pack.md) and [pack](../commands/pack.md). It can also run [check-language](../commands/check-language.md) on its own, with `--share`, `--names` and `--orgs`. It runs [sign-off](../commands/sign-off.md) only when you say you reviewed the file and give your role.

## What you get

- The run folder `<export folder>/pmlc-runs/<date>-<site>-<event>/`, with `workspace/` and `outputs/` (see [Files and folders](../Files-and-folders.md)).
- A short summary: the number of findings and evidence items, the share at supervision and organisational level, and any data-quality flags.
- A recommendation of which skill to run next, or one question: which audience first?

## Worked example (Hazira)

On the public Hazira sample, `ingest` printed:

```text
Ingested 436 findings, 46 evidence items, 0 causal-chain rows -> …/pmlc-runs/2020-09-24-hazira-gas-release-fire/workspace
schema: fingerprint b2ea9b9179b3; missing: none; unknown: none
cross-check: Analysis Statistics agrees (436)
```

The profile reported that 308 of the 436 findings (71%) sit at the Supervision and Organisational Influences levels. It listed eight data-quality flags, among them:

- the four investigative follow-up columns are empty on every finding;
- no finding is marked "User Edited";
- the investigation status is `in_progress`, so outputs are draft learnings.

`classify` placed 630 distinct role strings and reported that 96 still need resolution. `run-path` printed `top_rating: 4` and `incident_date: 2020-09-24`. The hub would then say what the export contains and suggest the [learning-clusters](learning-clusters.md) resolution pass before tier-based packs.

The `classify` numbers are from the base classification; the resolution pass and an overlay lower the unresolved count (see [learning-clusters](learning-clusters.md)).

## Related skills

- [learning-clusters](learning-clusters.md): resolves the roles the rules could not place.
- [organisation-learning-map](organisation-learning-map.md): the usual first output for "everyone".
- [learnings-register](learnings-register.md): the formal register of learnings.
- The full list, grouped by audience: [Skills](../Skills.md).
