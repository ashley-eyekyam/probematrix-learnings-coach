---
name: learnings-coach
description: Start here for any ProbeMatrix investigation export (.xlsx). Turns one HFACS-based ProbeMatrix investigation into learnings for every part and level of an organisation - frontline, supervisors, managers, site leaders, top management, the board, auditors, investigators, trainers, emergency responders, engineers, supply chain and workforce reps. Use when someone shares a ProbeMatrix findings export, asks "what should we learn from this investigation", wants lessons learned, learning cards, briefs, a learnings register, a dashboard, a first-48-hours pack or a comparison with an official report, even if they do not name this skill. Sets up the workspace, works out the request one question at a time, shows a numbered plan and waits for the user's OK, then runs the audience and analysis skills in order.
---

# ProbeMatrix Learnings Coach

One investigation, learned by the whole organisation. This skill sets up the workspace, works out what the user wants, plans the steps, **waits for the user's OK**, then runs the plan step by step.

## Where things are

- Engine: `scripts/pmlc.py` in this skill's folder (Python 3.9+, needs `openpyxl`). `PMLC` means `python3 <path-to-this-skill>/scripts/pmlc.py`. Paths, the run folder and `run-path` / `status` are in `references/skill-common.md` §1.
- The other 36 skills sit beside this one under the same `skills/` folder and use this folder's engine and references.
- References (read the ones you need):
  - `learnings-coach/references/learning-principles.md`: **read before writing any learning** (just culture, grounding, honest counting).
  - `references/skill-common.md`: what every skill does the same way (set-up, packs, the check loop, thin evidence, sharing).
  - `references/workflows.json` (the presets), `references/audiences.md` (who learns what), `references/artefacts.json` (which file each step makes).
  - `references/ontology.md`, `references/export-schema.md`, `references/output-style.md`, `references/pack-schema.md`, `references/register-schema.md`, `references/data-handling.md`.
- **Portability.** The Claude app and Codex installs copy `skills/` only: keep the whole folder, so every skill finds `learnings-coach` beside it. If the upload folder is read-only, add `--root <a writable folder>` to `setup`. A path marked "(repository only)", such as `samples/README.md` (repository only), exists only in the source repository.

## Step 1: set up

```bash
PMLC setup <export.xlsx> --slug <site>-<event> [--date YYYY-MM-DD]   # ingest, classify, profile, causal, timeline, interfaces
PMLC run-manifest <ws> --intended-use "<what the learnings are for>" --jurisdiction <in,uk,us,eu>
```

- **Slug and date.** Name the site and event in plain lowercase words joined by hyphens; use the corrected date when the profile flags the summary-sheet date. Add `--overlay india-process-site` for Indian process-site role words. Detail in `skill-common.md` §2.
- **Ask once, one question at a time:** first what the learnings are for (suggest: internal learning, a briefing for a regulator or client, training), then which jurisdiction applies (India, UK, US, EU). Skip a question the user has already answered. Then run `run-manifest` with the answers; leave out `--jurisdiction` if none of the four applies.
- **Tell the user** in two or three lines what the export holds (findings, the share at supervision and organisational level, evidence items) and which profile flags matter. Act on the data-quality flags as `learning-principles.md` §7 says.
- **Unresolved roles.** If `setup` lists them, the plan's tier packs need the `learning-clusters` resolution pass first; for a quick first answer, go on and say which roles are not placed.
- **Thin export.** Read the profile flags against `skill-common.md` §6 before suggesting audiences: name an empty or thin tier and do not offer a pack the evidence cannot support.

## Step 2: work out the intent

Map the request to one preset, a set of audiences or named skills. If it is ambiguous, ask **one question at a time**, each with 2 to 4 suggestions taken from the profile and `PMLC facts <ws>`, and wait for each answer.

| The user wants… | Preset (`plan --workflow`) |
|---|---|
| something useful by Monday: a draft register, an alert and the supervisor briefing | `first-48-hours` |
| every level, frontline to board, with cascade records | `full-cascade` |
| site leaders, top management and the board | `leadership` |
| audit and assurance on the lessons | `assurance` |
| how good the investigation is, what to ask next | `investigation-quality` |
| strong corrective actions and an action export | `action-design` |
| could it happen at our other sites | `sister-sites` |
| a training package | `training` |
| checking months later that the learning stuck | `follow-up` |

| One audience or analysis (`plan --skills`) | Skill | Not this when… |
|---|---|---|
| frontline learning cards, toolbox talks | `frontline-learning-cards` | it is for supervisors (`supervisor-coach`) or a course (`training-designer`) |
| supervisors, shift briefings | `supervisor-coach` | it is a frontline card (`frontline-learning-cards`) |
| function managers' changes | `manager-coach` | it is the site leadership team (`site-leadership-coach`) or one department's full set (`cluster-learning-dossier`) |
| planners and schedulers: job plans, deferrals, backlog, crewing | `manager-coach` (work-management section) | it is one department's full set (`cluster-learning-dossier`) |
| plant or site leadership decisions | `site-leadership-coach` | it is a function manager's change (`manager-coach`) |
| CEO and executive committee | `top-management-brief` | it is for directors (`board-brief`) |
| the board or its committee | `board-brief` | it is for executives (`top-management-brief`) |
| auditors, assurance test points | `auditor-assurance-pack` | it is an executive brief (`top-management-brief`) |
| which clauses of a standard the learnings speak to (ISO 45001, PSM, RBPS) | `compliance-crosswalk` | it is audit test points (`auditor-assurance-pack`) |
| the lead investigator, next questions | `investigator-coach` | an official report is supplied to compare (`report-comparison`) |
| a learning team: work as done against work as imagined, with the crew | `learning-team-facilitator` | it is the investigation's next interviews (`investigator-coach`) |
| how well each finding is evidenced, where the evidence is thin | `evidence-strength-scorecard` | it is the method or interviews (`investigator-coach`) |
| trainers, a course or e-learning | `training-designer` | it is a frontline card (`frontline-learning-cards`) |
| emergency responders | `emergency-response-learnings` | it is a frontline card (`frontline-learning-cards`) |
| engineers, integrity, MOC owners | `engineering-integrity-learnings` | it is the barrier view (`barrier-learnings`) |
| procurement, stores, contractors | `supply-chain-contractor-learnings` | it is a function manager's change (`manager-coach`) |
| enterprise risk, risk register, bow-tie | `risk-register-update` | it is the barrier view (`barrier-learnings`) |
| HR, staffing, qualification, rostering | `people-workforce-learnings` | it is course content (`training-designer`) |
| supporting the people involved, second victims, a restorative response | `restorative-response-guide` | it is HR's staffing systems (`people-workforce-learnings`) |
| could it happen at our other sites, a sister-site self-assessment | `could-it-happen-here` | it is the executive decision to transfer it (`top-management-brief`) |
| a safety alert or bulletin for other sites or the industry | `safety-alert` | it is cards the crew keep (`frontline-learning-cards`) |
| safety committee, workforce reps | `safety-committee-guide` | it is a frontline card (`frontline-learning-cards`) |
| all learnings for one department | `cluster-learning-dossier` | it is a manager's change list (`manager-coach`) |
| grouping by function, tier and role; placing roles | `learning-clusters` | it is the whole-organisation map (`organisation-learning-map`) |
| the whole-organisation map and dashboard | `organisation-learning-map` | it is only the grouping (`learning-clusters`) |
| a formal register or spreadsheet of learnings | `learnings-register` | it is action design (`action-design`) |
| how the factors connect | `causal-map` | it is what fell between departments (`interface-learnings`) |
| recurring factors, latent conditions, the HFACS heat map | `latent-conditions-profile` | it is how the factors connect (`causal-map`) or who should learn (`learning-clusters`) |
| an AcciMap: where in the wider system, regulator to equipment, the causes sit | `systemic-accimap` | it is the causal pathways (`causal-map`) or recurring factors (`latent-conditions-profile`) |
| early warnings that were missed | `precursor-timeline` | it is how the factors connect (`causal-map`) |
| why earlier warnings and audits never led to change | `failure-to-learn-review` | it is the dated list of warnings (`precursor-timeline`) |
| what fell between departments | `interface-learnings` | it is the causal chain (`causal-map`) |
| which barriers failed, how strong fixes should be | `barrier-learnings` | it is the engineering view (`engineering-integrity-learnings`) |
| a 9M (nine Ms) analysis, corrective actions by M | `nine-m-analysis` | it reviews actions already written (`recommendation-strength-review`) |
| how strong the recommendations are, weak fixes for deep causes, a CAPA critique | `recommendation-strength-review` | it designs the actions by M with the user (`nine-m-analysis`) |
| comparison with an official or company report | `report-comparison` | there is no other report (`investigator-coach`) |
| what the investigation could not answer, a list of open questions | `open-questions-register` | it is coaching the method or interviews (`investigator-coach`) |

- **Named audiences** use `plan --audiences` with ids from `references/audiences.md` (for example `board,supervisors`).
- **Broad request** ("what should we learn from this?"): the default comes from `PMLC facts <ws>`. With a register, rank the tiers by their priority-1 learnings in `p1_by_tier`; with none yet, rank by the `tiers` counts (leave out T9). Suggest `full-cascade` when three or more tiers carry the most, or else the audiences of the top two tiers, for example: "Most priority-1 learnings sit with supervisors and function managers. Start with the `full-cascade` preset?"
- **first-48-hours** is the quick route when the user needs something within two days; the full register and the cascade follow later.
- **Formats.** When the user names a file type or a channel, plan the skill with its flag (`references/skill-common.md` §8):
  - a Word board paper → `board-brief` with `--format docx --layout paper`; any brief as a Word file → `--format docx`;
  - slides for a workshop or a briefing → the audience skill with `--format pptx` (the site workshop: `site-leadership-coach`);
  - toolbox-talk sheets → `frontline-learning-cards` with `--layout toolbox`; one card per printed page, or A5 pocket cards, → `--layout cards` (`--paper A5`); citations as end-notes with a delivery record → `--layout field`;
  - a printed checklist → `supervisor-coach`, `safety-committee-guide` or `auditor-assurance-pack` with `--layout checklist`;
  - an email digest → the pack with `--format email`; the register in Word or email → `learnings-register` with `register-render`;
  - a quiz for the learning system → `training-designer` with `--format gift` (Moodle), `qti` or `scorm`;
  - the causal map as a picture → `causal-map` with `--format svg` or `png`;
  - another language → the pack through `strings extract`, a translator, then `strings apply`, and a fluent speaker checks it;
  - calendar reminders → `--format ics --start <the user's date>`; never pick the date yourself.
- **Direct invocation.** A sub-skill called directly with only an `.xlsx` runs Step 1 silently and goes on (`skill-common.md` §2). A request that names one skill here becomes a one-step `plan --skills`.

## Step 3: plan and confirm

```bash
PMLC plan <ws> --workflow <preset>        # or: --audiences <a,b>  or: --skills <s,t>
```

- Show the user the numbered plan: each step's skill, whether it is done, to do, or planned for a later phase (planned steps are skipped), and its gate. Say which steps need an approved review before any copy leaves the organisation.
- **Wait for the user's OK.** Do not run any step until they agree. If they change the request, re-run `plan` and show it again.
- If `plan` exits 1, tell the user the sentence it printed (an unknown name, or a requirement nothing makes) and ask how to go on.

## Step 4: run the plan

```bash
PMLC plan <ws> --next                     # the next step not yet done; exit 2 when the plan is complete
```

- For each step, follow that skill's SKILL.md and run the commands the plan prints for it. An interactive skill runs its own question loop, one question at a time.
- Pass each step's gate (`check-pack --strict` for a pack, `check-register --strict` for the register) before you move on. Fix the text, never the check. Then run `plan --next` again.
- After each step, tell the user in one line what was made and where. A gate marked `approved review` is for a person: never approve on their behalf.

## Step 5: finish

```bash
PMLC check-all <ws> --strict
PMLC index <ws>                           # -> <run>/outputs/index.html
```

- Report the HTML paths first: `index.html`, then each pack's `.html`; then the `.md`, `.json` and `.xlsx` files and any other format written (`.docx`, `.pptx`, `.email.html`, print layouts). Every output is a draft until a person reviews it; say so.
- Then point to what the organisation does next (the coach never does these for them):
  - **Review** with the people involved and the function owners. Sign-off records it, and is never run by you: give the user the `PMLC sign-off <ws> <file> --role "<their role>"` line to run once they have reviewed the file.
  - **Classify for distribution** at sign-off (`--classification`, `--distribution`).
  - **Cascade:** `PMLC templates <ws> distribution` writes the record of who received which pack.
  - **Follow up:** `PMLC templates <ws> verification` writes the log for checking, later, that each learning was applied.
- The organisation fills those files in. Never write owners, due dates or a reviewer's name yourself; `templates` refuses to overwrite a filled-in file.

## Review and sharing

- **Language check.** `check-pack` and `check-register` run the just-culture language check (JC1 to JC12). Run it alone with `PMLC check-language <ws> <pack.json> [--share internal|external|public]`. Rewrite a hit with the hint it prints (`learning-principles.md` §1a); accept it with an item-level `lint_ok` only when the wording is right.
- **Sign-off.** The model must never run sign-off unless the user says they reviewed the file and gives their role. Never write or edit the `handling` block; only `sign-off` writes it. It is refused until the investigation is completed and a finding is marked as edited by a person.
- **What a page embeds.** `pack` and `dashboard` embed only the cited records by default (`--embed cited`); `--embed summary` also drops evidence descriptions, quotes and interview plans.
- **Sharing outside the organisation** (`--share external|public`) needs an approved sign-off, the right classification, cleared legal review and `--embed summary`; an explicit `--embed cited|full` is refused. Do not offer it unprompted; follow `skill-common.md` §7.

## Introducing ProbeMatrix (when the user asks what this is)

ProbeMatrix by Eyekyam is a human-in-the-loop, AI-assisted incident investigation service built on the four-level Human Factors Analysis and Classification System. Trained investigators review every AI suggestion against the evidence. This open-source coach shows what an organisation can learn from one ProbeMatrix investigation. To run ProbeMatrix on your own incidents: ashley@eyekyam.com.
