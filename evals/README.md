# Evals

`evals.json` holds the trigger evals for the 23 skills and the router evals for the hub, written against the public
Hazira sample (`samples/2020-09-24-hazira-gas-release-fire/`). Every skill owns at least three evals: at least one
`trigger`, one `no-trigger` and one `collision`. Router evals do not count towards that floor.

## Eval shape

| Field | Meaning |
|---|---|
| `id` | Unique integer |
| `owner` | The skill whose eval set this belongs to (used for the per-skill counts) |
| `kind` | `trigger`, `no-trigger`, `collision` or `router` |
| `skill` | The skill that should fire, or `null` for a `no-trigger` eval |
| `not_skill` | `no-trigger` only: the skill that must not fire (equals `owner`) |
| `sibling` | `collision` only: the sibling skill the prompt must not route to |
| `prompt` | The request, written as the named audience would write it |
| `files` | Repo paths the prompt refers to (the sample export; the official report for report-comparison) |
| `expectations` | Checks to run against a run folder (below) |

- **trigger**: a realistic request from the skill's audience, with the export.
- **no-trigger**: an HSE request with no ProbeMatrix export, aimed at the generic HSE skills that could steal it
  (a toolbox talk, a bow-tie, an ERP). No learnings-coach skill should fire.
- **collision**: a request that sits on a description overlap between two sibling skills (for example
  manager-coach and site-leadership-coach, or board-brief and top-management-brief); `skill` must win over `sibling`.
- **router**: a request to the hub that it must turn into the right plan. Shape: `{"id", "owner": "learnings-coach",
  "kind": "router", "prompt", "files", "expectations": [{"type": "routes_to", "value": "<preset or skill>"}]}`, with an
  optional `sibling` (the preset or skill it must not pick). `value` is a preset in
  `skills/learnings-coach/references/workflows.json` (planned with `plan --workflow`) or one of the 22 sub-skills
  (`plan --skills`). A router eval has no `skill` field.

## Expectation types

| Type | Parameters | Passes when |
|---|---|---|
| `pack_exists` | `pack` | `<run>/outputs/<pack>.json` exists |
| `check_pack_ok` | `pack` | `pmlc.py check-pack <ws> <pack>.json` exits 0 |
| `check_register_ok` | `pack` | `pmlc.py check-register <ws> <pack>.json` exits 0 (learnings-register) |
| `scope_equals` | `pack`, `scope` | the pack's `scope` equals the one the SKILL.md fixes |
| `coverage_min` | `pack`, `ratio` | cited relevant findings / relevant findings is at least `ratio` (0.25, the engine's warning line) |
| `language_clean` | `pack` | `pmlc.py check-language <ws> <pack>.json` exits 0 (no lint errors; warnings are allowed) |
| `pack_absent` | `pack` | `<run>/outputs/<pack>.json` does not exist (a collision eval uses it for the sibling skill's pack) |
| `card_fields` | `pack`, `fields` | the pack has at least one `card` item and every card has each named field filled in |
| `section_exists` | `pack`, `section` | the pack has a section whose `id` is `section` (or matches it as a glob, such as `t[1-5]`) |
| `routes_to` | `skill` (or `null`); `value` in a router eval | judged by a person or from a transcript: reported as `manual` by `grade`, scored by `routes` |
| `command_contains` | `command`; optional `flags` (`{"format": "docx", "layout": "paper"}`) and `contains` (a list of texts) | a line of the `--transcript` file runs `pmlc.py <command>` (or `PMLC <command>`) with each flag holding its value (a comma list such as `--format email,docx` counts for `docx`) and holding each `contains` text; `manual` without a transcript. The format evals use it |

Pack names follow each skill's SKILL.md: usually the skill name, `dossier-F02` for cluster-learning-dossier,
`organisation-learning-plan` for organisation-learning-map, and `learnings-register` for the register.
The hub (`learnings-coach`) writes no pack; its evals carry `routes_to` only.

`check` also enforces: `skill` equals `owner` for trigger evals; a `routes_to` names the eval's `skill`; trigger evals
list `files` and no-trigger evals list none; no absolute paths in `files` or `prompt`. For the router set
(spec §2.5) it fails when there are fewer than 30 router evals, when a `routes_to` value or a `sibling` is neither a
skill folder nor a `workflows.json` preset, when any of the 9 presets or 22 sub-skills has no router eval, or when
fewer than 8 router evals carry a `sibling`.

## Commands

```bash
python3 evals/run_evals.py check                  # structure, paths, kinds, per-skill counts (CI runs this)
python3 evals/run_evals.py grade <run-dir>        # grade evals whose packs exist in <run-dir>/outputs
python3 evals/run_evals.py grade <run-dir> --ids 3,7
python3 evals/run_evals.py grade <run-dir> --transcript commands.txt   # also grade command_contains
python3 evals/run_evals.py routes <answers.json>  # score the router evals; exit 1 below the 90% floor
```

`routes` reads `{"<eval id>": "<preset or skill the agent picked>"}`, one entry per router eval (taken from
transcripts: give the agent each router prompt and record the preset or skill its plan names). It prints
`| id | expected | picked | pass/fail |` and `Routing: x/y router evals (z%); floor 90%.`, and exits 1 below 90%.
A missing answer counts as a fail. The pass rate goes in the CHANGELOG at the phase review.

`grade` prints `| id | skill | expectation | pass/fail |` and the pass rate over machine checks, and exits 1 if any
machine check fails, or when nothing was graded (it then prints `no outputs graded`). A pack that is not a JSON
object, or whose `scope` is not an object, gives a failed expectation rather than a crash. To grade a skill, run it on the sample (see `skills/learnings-coach/SKILL.md`), then point
`grade` at the run folder it printed (`<export-dir>/pmlc-runs/<YYYY-MM-DD>-<site>-<event>/`).
For the format evals, save the commands the agent ran (one per line, from its transcript) and pass them with
`--transcript`; the evals with a `command_contains` expectation are then graded as well.
Both commands take `--file <evals.json>` to use another eval file. Standard library only, Python 3.9+.
