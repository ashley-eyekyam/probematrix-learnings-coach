# Workflows and recipes

Each recipe is one job you are likely to want. It gives the goal, the prompt to give your agent, the engine commands the agent runs, and what to check before you use the result. The numbers come from the public Hazira sample.

Commands are written `pmlc <command>`; your agent fills in the real path (see [Getting started](Getting-started.md)). `<ws>` is the workspace folder and `<run>` the run folder. All recipes assume the workspace exists: if not, the agent runs Step 1 of [Getting started](Getting-started.md) first.

## Let the coach plan the work

**Goal.** Start from a fresh export and let the hub ([learnings-coach](skills/learnings-coach.md)) choose and order the skills, with a plan you approve before anything runs.

**Prompt.**

> Here is our ProbeMatrix export. What should we learn from it? Show me the plan before you start.

**Engine commands.**

```bash
pmlc setup <export.xlsx> --slug <site>-<event> [--date YYYY-MM-DD]
pmlc run-manifest <ws> --intended-use "internal learning" --jurisdiction in
pmlc facts <ws>
pmlc plan <ws> --workflow full-cascade
pmlc plan <ws> --next                     # after your OK, once per step
pmlc check-all <ws> --strict
pmlc index <ws>
```

The nine presets are `first-48-hours`, `full-cascade`, `leadership`, `assurance`, `investigation-quality`, `action-design`, `sister-sites`, `training` and `follow-up` (in `references/workflows.json`). Instead of a preset, the agent can plan `--audiences board,supervisors` or `--skills causal-map,interface-learnings`.

**What to check.**

- The agent asks one question at a time (what the learnings are for, then the jurisdiction, then what you want if it is unclear) and offers two to four suggestions each time.
- It shows the numbered plan and does nothing until you say OK. Steps marked `planned for v2.0, Phase N` are skipped: their skill has not shipped yet.
- Each step passes its gate (`check-pack --strict` or `check-register --strict`) before the next starts. `plan --next` ends with exit code 2 when the plan is complete.
- It ends with the path of `outputs/index.html` first, then each pack's HTML. It never runs `sign-off` for you, and it leaves owners and due dates blank.
- On Hazira, `facts` before any register ranks the tiers by finding counts (`T1: 227; T2: 219; T3: 247; T4: 63; T5: 1`); with the sample register, priority-1 learnings sit at every tier from T1 to T4, so the suggestion is `full-cascade`.

## Pick a workflow preset

**Goal.** Choose the preset that fits the job, and know before you start how many steps it has and which of them are not available yet.

**Prompt.**

> Which of your workflows fits a leadership review of this investigation? Show me the steps first.

**Engine commands.**

```bash
pmlc plan <ws> --workflow leadership
pmlc plan <ws> --workflow leadership --json      # the same plan as one JSON object (plan.json)
pmlc plan <ws> --next                            # the next step to do; exit code 2 when the plan is complete
```

The table shows what `plan --workflow <preset>` printed for each preset on a fresh Hazira workspace (after `setup` with the `india-process-site` overlay, before any pack or register was written). "Engine" steps are `ingest`, `classify`, `templates` and `export-actions`; "planned" steps belong to skills that arrive in a later v2.0 phase and are skipped.

| Preset | What it is for | Steps on Hazira | Planned (skipped) |
|---|---|---|---|
| `first-48-hours` | A draft register, an alert and the supervisor briefing within two days | 5: ingest and classify (done), learnings-register (draft), supervisor-coach | `safety-alert` (Phase 6) |
| `full-cascade` | Every level, frontline to board | 12: ingest and classify (done), learning-clusters, learnings-register, organisation-learning-map, frontline-learning-cards, supervisor-coach, manager-coach, site-leadership-coach, top-management-brief, board-brief, then `templates` | none |
| `leadership` | Register, site leadership, top management and board | 6: ingest and classify (done), learnings-register, site-leadership-coach, top-management-brief, board-brief | none |
| `assurance` | Register, evidence strength, standards crosswalk and the auditor pack | 6: ingest and classify (done), learnings-register, auditor-assurance-pack | `evidence-strength-scorecard`, `compliance-crosswalk` (Phase 5) |
| `investigation-quality` | Evidence strength, open questions and investigator coaching | 5: ingest (done), investigator-coach, report-comparison (only when an official report is supplied) | `evidence-strength-scorecard`, `open-questions-register` (Phase 5) |
| `action-design` | 9M analysis, recommendation strength and an action export | 6: ingest and classify (done), learnings-register, then `export-actions` | `nine-m-analysis`, `recommendation-strength-review` (Phase 5) |
| `sister-sites` | An alert and "could it happen here" for other sites | 5: ingest and classify (done), learnings-register | `safety-alert`, `could-it-happen-here` (Phase 6) |
| `training` | Register, training design, frontline cards and a safety-moment deck | 6: ingest and classify (done), learnings-register, training-designer, frontline-learning-cards | `safety-moment-deck` (Phase 6) |
| `follow-up` | Effectiveness plan and the verification log | 2: `templates` (the verification log) | `learning-effectiveness-plan` (Phase 6) |

All nine exit with code 0 on Hazira. Once the sample register is copied into `outputs/` and passes `check-register --strict`, the register step shows `done` in every preset that has one, so `plan --next` moves on to the first pack.

**What to check.**

- The plan names each step's gate: `check-pack --strict` for a pack, `check-register --strict` for the register, and an approved review as well for the board brief and the supply-chain pack, which are meant for outside the organisation.
- A step is `done` only when its output is current. After you edit a pack, its step is `todo` again until the next check passes.
- A plan that cannot be resolved (an unknown skill, a cycle, or a requirement that nothing produces) exits 1 with a sentence naming it. See [plan](commands/plan.md).
- If no preset fits, ask for audiences (`--audiences board,supervisors`) or named skills (`--skills causal-map,interface-learnings`) instead.

## The first 48 hours

**Goal.** Something useful within two days of the export: a draft register and the supervisor briefing, with the full cascade later.

**Prompt.**

> We need to brief the shifts by Monday from this investigation. What can we put out now?

**Engine commands.**

```bash
pmlc plan <ws> --workflow first-48-hours
pmlc plan <ws> --next
pmlc check-register <ws> <run>/outputs/learnings-register.json --strict
pmlc check-pack <ws> <run>/outputs/supervisor-coach.json --strict
pmlc pack <ws> <run>/outputs/supervisor-coach.json
```

**What to check.**

- On Hazira the plan has five steps: ingest and classify (done), the draft register, `safety-alert` (planned for Phase 6, skipped) and the supervisor coach.
- The register is a draft: say so when it is shared. The full register, the organisation map and the other audiences follow with `full-cascade`.
- After the packs are reviewed, `pmlc templates <ws> distribution` gives the record of who received each one.

## Brief the board

**Goal.** A two-to-three page paper for the board or its safety committee: what the investigation says about governance and assurance, and the questions directors should ask.

**Prompt.**

> Prepare a board briefing from this investigation, with eight to twelve questions directors should ask management and what good evidence would look like.

**Engine commands.**

```bash
pmlc profile <ws>
pmlc select <ws> --preset board-brief          # level 4 top-rated, and assurance findings at levels 3 and 4
pmlc timeline <ws> --before incident
pmlc check-pack <ws> <run>/outputs/board-brief.json --strict
pmlc pack <ws> <run>/outputs/board-brief.json
```

**What to check.**

- Each question has "why it matters" and "what good evidence looks like".
- The tone is neutral: no blame of management or staff, roles only.
- The page carries the DRAFT ribbon until it is signed off. On Hazira it always will (see [Review and sharing](Review-and-sharing.md)).
- Skill page: [board-brief](skills/board-brief.md).

## A frontline toolbox talk, and printing it

**Goal.** Learning Cards and five-minute toolbox talks for a crew, printed for a shift briefing.

**Prompt.**

> Make toolbox-talk learning cards for the maintenance crews, with a stop-and-ask list. I will print them.

**Engine commands.**

```bash
pmlc select <ws> --preset frontline-learning-cards     # T1 brief, T1 levels 1 and 2, T1 top-rated
pmlc check-pack <ws> <run>/outputs/frontline-learning-cards.json --strict
pmlc pack <ws> <run>/outputs/frontline-learning-cards.json --layout field
```

Then open `frontline-learning-cards.field.html` and print it from the browser: one A4 page per card, the citations as numbered end-notes, and a delivery record to fill in at the briefing. `--layout cards --paper A5` prints pocket-size cards instead; `--layout checklist` prints the stop-and-ask list with a box per check and a "Checked by (role)" line; `--layout toolbox` prints one page per toolbox talk when the pack has them. With `--base-url <published page>`, each card carries a QR code that opens it in the full pack. The page itself (`frontline-learning-cards.html`) still has its own **Print** button.

**What to check.**

- Each card says what the organisation is changing. Not one ends with "be careful" or "stay vigilant": in a frontline pack the language check treats that as an error.
- No card singles out "the" operator of a small crew.
- In print, each card stays on one page and carries the status line. The printed evidence trail lists only the cited records and follows on the same page, and the uncovered findings print as one line, "x of y relevant findings cited", with the pack's own numbers.
- Every printed page carries the status line, the footer and, until sign-off, DRAFT.
- The delivery record holds roles only. After the briefing, copy its rows into `distribution.csv`.
- Consult the people involved before wide release.

## A learnings register to Excel

**Goal.** A formal lessons-learned register, one row per learning, with recommendations, as an Excel workbook.

**Prompt.**

> Build a learnings register from this export with recommendations and leading indicators, and give me the Excel file.

**Engine commands.**

```bash
pmlc select <ws> --preset learnings-register
pmlc check-register <ws> <run>/outputs/learnings-register.json --strict
pmlc register-xlsx <run>/outputs/learnings-register.json
pmlc register-md <ws> <run>/outputs/learnings-register.json
pmlc export-actions <ws> --register <run>/outputs/learnings-register.json
```

**What to check.**

- `check-register --strict` ends with `0 problem(s)`. On the Hazira sample register it printed `25 learnings; 435 of 436 findings covered (100%); 0 problem(s).`
- Under `--strict`, a priority-1 learning needs at least one fix above the administrative tier, or a `why_not_stronger` that says why not. On the sample, LR-08 and LR-12 (decision-making and competence) carry one each, pointing to the engineering fixes in LR-09 and LR-10.
- Read the warnings too. They do not fail the check, but each JC6 warning means a learning relies only on training or administrative fixes for a level 3 or 4 cause.
- The workbook has five sheets: Learnings Register, Recommendations, Learning Plan, Summary and About, each an Excel table with filters and drop-down lists.
- `learnings-register.md` comes from `register-md`; never write it by hand. `export-actions` wrote 44 actions for the sample's 44 recommendations, with owner, due date and status blank for your organisation.
- Change the JSON and re-run; never edit the workbook by hand.

## The organisation learning map dashboard

**Goal.** One offline page that shows who must learn what across the organisation.

**Prompt.**

> Build the organisation learning map with the register, so I can see every learning by level.

**Engine commands.**

```bash
pmlc dashboard <ws> --register <run>/outputs/learnings-register.json
pmlc interfaces <ws> --top 10
```

If the profile flagged a wrong summary-sheet date or title, the agent adds `--date` or `--title`.

**What to check.**

- The page has two tabs, **Overview** and **Detailed register**. Without a register there is only the overview of findings.
- The header shows the right incident title, date and location.
- The DRAFT ribbon shows until the register is approved.

## Correct a role and keep the correction

**Goal.** Put a role the rules placed wrongly (or not at all) with the right function and tier, and keep that decision for every later run.

**Prompt.**

> "Area Supervisor" belongs to operations at supervisor level. Correct it and keep the correction.

**Engine commands.**

```bash
# the agent adds the decision to <ws>/role_overrides.json:
#   {"Area Supervisor": {"F": ["F01"], "T": "T2", "R": "actor"}}
pmlc classify <ws>
```

**What to check.**

- `classify` prints `Applied 1 override(s) from …/role_overrides.json`. On Hazira the unplaced count fell from 96 to 95.
- A warning `override(s) match no role` means a role string in the file is spelt differently from the export. Copy the string exactly from `unresolved_roles.json`.
- Re-run the packs that depend on tiers. `pmlc status <ws>` shows what is now out of date.

## Add an industry overlay

**Goal.** Teach the classifier the role words of a type of site, such as the titles used on Indian public-sector oil and gas sites, without editing the base list of functions.

**Prompt.**

> This is an Indian process site. Apply the india-process-site overlay and show me what changed.

**Engine commands.**

```bash
pmlc classify <ws> --overlay india-process-site
pmlc classify <ws>              # later runs reuse the overlay automatically
pmlc classify <ws> --no-overlay # to drop it again
```

**What to check.**

- The run prints `warning: previous classify used taxonomy.json; this run uses taxonomy.json + india-process-site`. That is expected the first time.
- On Hazira the overlay brought the unplaced roles from 96 to 87, and F09b Emergency Planning & Command from 16 to 43 findings.
- For a different kind of organisation (a hospital, a mine, an airline), ask the agent to copy the taxonomy and adapt it; it is then used with `--taxonomy`.

## Re-run after the export changes, using status

**Goal.** Bring the analysis up to date after the investigation team edits findings in ProbeMatrix and exports again.

**Prompt.**

> I have a new export of the same investigation. Update the workspace and tell me which outputs are out of date.

**Engine commands.**

```bash
pmlc ingest <new export.xlsx> --slug hazira-gas-release-fire --force
pmlc status <ws>
pmlc classify <ws>              # and any other command status names
pmlc check-pack <ws> <run>/outputs/<pack>.json
```

**What to check.**

- Without `--force`, `ingest` refuses: `… already holds a workspace. Pass --force to overwrite it.` A forced ingest keeps `clusters.json` and `role_overrides.json`.
- `status` lists each workspace file as `current` or `stale`, with the reason, for example `clusters.json | stale | overrides changed since this was built`. Re-run the command it names.
- The second table shows each pack's last check and whether the pack file changed since. Re-check every pack whose findings may have moved.
- `pack` and `dashboard` warn `stale input …; re-run pmlc classify …` if you forget.

## Check a pack for blame and hindsight wording, and fix the hits

**Goal.** Make sure a pack reads as learning, not blame, before anyone sees it.

**Prompt.**

> Run the language check on the board brief and fix every hit.

**Engine commands.**

```bash
pmlc check-language <ws> <run>/outputs/board-brief.json
pmlc check-pack <ws> <run>/outputs/board-brief.json      # runs the same check
```

**What to check.**

- An invented draft paragraph read "The maintenance crew failed to carry out a hydro test, which was obviously careless, and the team should have been held accountable." The check printed `check-language: 2 errors, 3 warnings`: JC2 for "careless" and "held accountable", JC3 for "failed to" and "should have", JC4 for "obviously".
- The rewrite, "No hydro test was done after the gasket was replaced; the system was pressurised to operating pressure only. No return-to-service procedure required a design-pressure test.", gave `check-language: 0 errors, 0 warnings`.
- Fix the wording first. Use `lint_ok` only when the wording is right and the rule does not apply, and always give the reason. See [Language checks](Language-checks.md).

## Review and sign off

**Goal.** Record that a competent person has reviewed a pack or register, so it stops being a draft.

**Prompt.**

> I have reviewed the supervisor coach and approve it. My role is HSE manager.

**Engine commands.**

```bash
pmlc check-pack <ws> <run>/outputs/supervisor-coach.json
pmlc sign-off <ws> <run>/outputs/supervisor-coach.json --role "HSE manager" --status approved
pmlc pack <ws> <run>/outputs/supervisor-coach.json
pmlc status <ws>
```

**What to check.**

- The agent runs `sign-off` only after you say you reviewed the file and give your role. It never writes a name, an owner or a due date.
- On Hazira, sign-off is refused: `cannot sign off: the investigation status is in progress; no finding is marked as edited by a person`. There is no override. Finish the investigation in ProbeMatrix and export again.
- After an approval, the DRAFT ribbon goes. Any later edit to the file, even one character, brings it back.
- `status` lists the sign-off with its role and date, and whether the file changed since.

## Make a version safe to share outside

**Goal.** A copy of an approved pack, dashboard or register for a regulator, a client or the public, with identifying details masked.

**Prompt.**

> Legal review is cleared and the pack is approved for external sharing. Make the external version of the board brief.

**Engine commands.**

```bash
pmlc sign-off <ws> <run>/outputs/board-brief.json --role "HSE manager" --status approved \
     --classification external --legal-review cleared
pmlc pack <ws> <run>/outputs/board-brief.json --share external --names names.txt --orgs orgs.txt
```

**What to check.**

- The pack must be approved, classified `external` or `public`, and have `legal_review` set to `cleared`. Otherwise the command refuses, lists every unmet condition and writes nothing, for example `cannot share externally: classification is "internal" (needs "external" or "public"); legal_review is not "cleared"`. A Hazira pack is always refused, because the investigation is unfinished.
- Sharing outside uses `--embed summary`. An explicit `--embed cited` or `--embed full` is refused.
- The output is a separate file, `board-brief.external.html` (and `.md`), so the internal copy is kept. The command ends with `Shared external: identifying details are masked`.
- The language check runs at the external level first, so a name, an organisation or a singleton role in the pack's own wording stops the copy. Rewrite it with roles and functions.
- Read the masked copy: names, organisations, equipment tags, singleton roles, clock times and full dates should all be gone or generalised. Details in [Review and sharing](Review-and-sharing.md).

## Redact names at ingest

**Goal.** Keep personal names out of the workspace from the start, so no later step can quote them.

**Prompt.**

> This export contains staff names. Here is a list of each name and the role to use instead. Redact them when you set up the workspace.

**Engine commands.**

```bash
# names-map.json (fictional names):  {"A. B. Example": "shift engineer", "Jane Placeholder": "control room operator"}
pmlc ingest <export.xlsx> --slug <site>-<event> --redact names-map.json
pmlc scan-names names.txt <run>/outputs --variants
```

**What to check.**

- `ingest` prints `redacted <n> name occurrence(s) from the workspace`. The Hazira export names roles only, so a test map gave `redacted 0 name occurrence(s)`.
- Each name also matches its common variants: surname only, initials and surname, honorific and surname.
- A `warning: surname-only match "…" replaced <n> times` asks you to read those sentences, because a surname can also be an ordinary word.
- Before sharing, run `scan-names` with a plain list of the names (one per line). It must print `0 hit(s).`

## Compare with the official report

**Goal.** A fair, two-way comparison with an official enquiry or company report on the same event.

**Prompt.**

> Compare this investigation with the official enquiry report (attached). Say where each is stronger.

**Engine commands.**

```bash
pmlc select <ws> --text "recommendation|remedial" --brief
pmlc check-language <ws> <run>/outputs/report-comparison.json --names comparator-names.txt
pmlc check-pack <ws> <run>/outputs/report-comparison.json --strict
pmlc pack <ws> <run>/outputs/report-comparison.json
```

**What to check.**

- The first page says whether the comparison is **sighted** (the findings quote the other report's recommendations) or **blind**. On Hazira it is sighted: 106 findings match the search, and the committee's remedial measures were in the evidence pack.
- Both sides are compared as learnings, not finding counts.
- No personal name from the other report appears in the tables.
- There is a section on where the other report is stronger.

## Give every level its own pack

**Goal.** A learning pack for each tier of the organisation, in a sensible order.

**Prompt.**

> We want the whole organisation to learn from this. Start with the map, then make the packs for each level in the order you recommend.

**Engine commands.**

```bash
pmlc dashboard <ws> --register <run>/outputs/learnings-register.json
pmlc select <ws> --preset site-leadership-coach
pmlc select <ws> --preset supervisor-coach
pmlc select <ws> --preset manager-coach
pmlc select <ws> --preset frontline-learning-cards
pmlc select <ws> --preset board-brief
```

Each pack is then checked with `check-pack` and rendered with `pack`.

**What to check.**

- The learning plan gives the order and the reason. A usual order is site leadership and supervisors first, then the largest clusters, then the board and auditors.
- The messages for each tier agree with each other: the frontline is not asked to fix what only managers can change.

## Deepen the investigation

**Goal.** Find what evidence is missing and who else to hear from, before the learnings are adopted.

**Prompt.**

> What evidence is missing from this investigation, and who should we interview next? Fill in the follow-up columns.

**Engine commands.**

```bash
pmlc profile <ws>
pmlc select <ws> --top-rated --format json --out <ws>/top.json
pmlc check-pack <ws> <run>/outputs/investigator-coach.json --strict
pmlc pack <ws> <run>/outputs/investigator-coach.json
```

**What to check.**

- `pack` writes `follow-up.json`, one entry per finding, ready to paste back into ProbeMatrix.
- Suggested interviews name roles only. Interviews are for learning, with a representative offered.
- On Hazira, the profile shows all four follow-up columns empty, so the agent drafts them for the 150 top-rated findings.
