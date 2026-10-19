# ProbeMatrix Learnings Coach

> **v2.0 alpha in testing.** The stable release is 0.3.5, and `main` now carries the alpha. To stay on 0.3.5:
> - **Claude app:** in the app's plugin settings, leave auto-update off and do not choose Update for the `probematrix` marketplace. If you have already updated, remove that marketplace there, add `ashley-eyekyam/probematrix-learnings-coach#v0.3.5` and install the plugin again.
> - **Claude Code:** pin the tag as in [Pinning a version](docs/INSTALL.md#pinning-a-version). Once you have installed the plugin the `probematrix` marketplace name is already taken, so pinning means removing the marketplace, adding it again with `#v0.3.5` and reinstalling the plugin; a single `marketplace add` is not enough.
> - **To stay on the tested alpha.3** instead, pin that tag the same way: `/plugin marketplace add ashley-eyekyam/probematrix-learnings-coach#v2.0.0-alpha.3`.

[![Licence: MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE) ![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)

**One investigation. Every level of the organisation learns.**

An open-source plugin of 23 agent skills that turns a single [ProbeMatrix](mailto:ashley@eyekyam.com) investigation export into learning for frontline crews, supervisors, managers, site leaders, top management, the board, auditors, investigators, trainers, emergency responders, engineers, the supply chain and workforce representatives.

Works with **Claude Code**, **Claude (Cowork / desktop)** and **OpenAI Codex**, and any agent that reads the Agent Skills format or `AGENTS.md`.

**User manual:** [`docs/manual/Home.md`](docs/manual/Home.md), also on the [project wiki](https://github.com/ashley-eyekyam/probematrix-learnings-coach/wiki). It covers every skill, command and flag, with worked examples from the Hazira sample.

---

## Why

A conventional investigation report is organised by discipline and ends with a flat list of root causes and recommendations. It tells the organisation *what went wrong*. It rarely tells each part of the organisation, at each level, *what it should now learn*.

ProbeMatrix analyses the evidence at four human-factors levels (Unsafe Acts → Preconditions → Supervision → Organisational Influences) and, for every finding, names the **roles and organisational entities involved**. The Learnings Coach uses that field to place every finding with the people who own its learning, then writes the learning in the form each audience can use.

```
ProbeMatrix export (.xlsx)
        │  pmlc ingest / classify
        ▼
Learning Clusters  =  entity (17 functions)  ×  tier (frontline → board)  ×  relation (actor, approver, owner, absent…)
        │  one focused pass per cluster × sub-division (practice, conditions, supervision, system,
        │  interfaces, barriers, precursors, tier messages, recommendations, competence, transferability)
        ▼
Learning Cards · Supervisor checklists · Manager agendas · Leadership decisions · ExCo & Board briefs
Audit test points · Investigator follow-up · Training modules · ER drills · Learnings Register (.xlsx) · Dashboard
```

## What's new in v2.0 so far

v2.0 is in testing (current build: 2.0.0-alpha.4, Phase 2: trust gates and the user manual). This guide still describes 0.3.5 in places; it is rewritten in full before v2.0.0.

**Phase 2 (2.0.0-alpha.4):**

- **Language checks.** `check-language` reads a pack or register the way a just-culture reviewer would: personal names, punitive wording, counterfactuals and hindsight, legal conclusions, retraining as the only fix, numbers that are not in the cited findings, organisation names, equipment tags, roles that point to one person and appeals to "be more careful". `check-pack` and `check-register` run it too, and stop on an error.
- **Review and sign-off.** A person who has reviewed an output tells the agent their role, and `sign-off` records it in the file with a fingerprint of the text. Any later edit turns the file back into a draft. Nothing can be approved while the investigation is still in progress in ProbeMatrix or no finding has been edited by a person.
- **The draft ribbon.** Every page shows DRAFT until it is approved, says why, and labels the AI-drafted wording from the export as such.
- **Safer sharing.** `--share external` or `--share public` writes a separate copy for a regulator, a client or the public, with names, organisations, equipment tags, one-person roles, clock times and full dates masked. It needs an approval, a matching classification and a cleared legal review.
- **Smaller pages.** Packs and the learning map now carry full records only for what they cite (`--embed cited`), and print only the cited evidence trail. A small Hazira board brief fell from about 1.2 MB to about 205 KB.
- **The user manual.** [`docs/manual/`](docs/manual/Home.md) explains every skill, engine command and flag with real examples from the Hazira sample, plus recipes, troubleshooting and a glossary. The full command list is in [Commands](docs/manual/Commands.md).

**Phase 1 (2.0.0-alpha.1 to alpha.3):**

- The coach no longer forgets your role corrections when you re-run the analysis.
- Questions about where two departments meet now use only the findings both share, so the numbers are small and meaningful (27 on the Hazira sample, not 196).
- It tells you when an analysis file is out of date (`pmlc.py status`).
- It refuses exports it cannot read properly, such as a CAPA Planner file, and warns when an export's own statistics disagree with its findings.
- Regulators, vendors and contractors now have their own functions, and site-specific role words (for Indian process sites) are an optional overlay you switch on.
- Timelines show clock times and how long before the incident each signal appeared.
- Automatic tests run on every change, so fixes stay fixed.

## The skills

| Skill | For | Produces |
|---|---|---|
| `learnings-coach` | everyone, **start here** | workspace setup, profile, routing |
| `learning-clusters` | analysts | findings classified by entity × tier × relation |
| `organisation-learning-map` | leadership, HSE | HTML dashboard + rollout plan |
| `cluster-learning-dossier` | any department | complete learning dossier for one function |
| `learnings-register` | HSE, management | Learnings Register (.md + .xlsx) with recommendations |
| `causal-map` | investigators, leaders | causal graph and pathway stories |
| `precursor-timeline` | leaders, auditors | dated weak signals and how they were handled |
| `interface-learnings` | managers | what fell between departments |
| `barrier-learnings` | engineers, HSE | barriers, failure modes, control-tier fixes |
| `report-comparison` | HSE, consultants | fair two-way comparison with an official report |
| `frontline-learning-cards` | operators, technicians, crews | Learning Cards, toolbox talks, "stop and ask" list |
| `supervisor-coach` | supervisors, shift in-charges, permit issuers | checklists, hold points, what to refuse |
| `manager-coach` | department managers | system learnings, indicators, 90-day agenda |
| `site-leadership-coach` | plant / site leadership | decisions, trade-offs, culture signals, workshop |
| `top-management-brief` | CEO, ExCo, corporate | transferability, policy, enterprise decisions |
| `board-brief` | board, safety committee of the board | governance learnings, questions to ask, assurance |
| `auditor-assurance-pack` | auditors, inspectors, insurers | audit test points, sampling, evidence requests |
| `investigator-coach` | investigators, HSE professionals | evidence gaps, key questions, interviews, method |
| `training-designer` | L&D, instructors | training-needs map, modules, assessments |
| `emergency-response-learnings` | fire services, ERT, incident command | response timeline, plan gaps, drills |
| `engineering-integrity-learnings` | engineering, integrity, MOC, I&C | technical learnings and decisions |
| `supply-chain-contractor-learnings` | procurement, stores, vendors, contractors | sourcing and contractor learnings |
| `safety-committee-guide` | safety committees, workforce reps | discussion guide and questions |

All skills share one engine, `skills/learnings-coach/scripts/pmlc.py`, which does the counting, filtering, causal extraction and file writing deterministically, so the model spends its effort on judgement.

## Install

Full instructions: [`docs/INSTALL.md`](docs/INSTALL.md).

**Claude Code**
```
/plugin marketplace add ashley-eyekyam/probematrix-learnings-coach
/plugin install probematrix-learnings-coach@probematrix
```

**OpenAI Codex**: clone the repo and work inside it (Codex reads `AGENTS.md` and `.agents/skills`), or install the skills for all projects:
```bash
git clone https://github.com/ashley-eyekyam/probematrix-learnings-coach
cd probematrix-learnings-coach && ./tools/install-codex.sh
```

On Windows, `.agents/skills` is a symlink to `../skills`. Clone with `git config core.symlinks true` (symlinks need Developer Mode or an elevated shell), or run `tools/install-codex.sh` (Git Bash or WSL), or copy the `skills/` folders yourself.

All hosts need Python 3.9+ with `openpyxl` (see below).

## Requirements and local setup

| Need | Version | Why | Required? |
|---|---|---|---|
| Python | 3.9 or newer (tested on 3.14) | runs the engine `skills/learnings-coach/scripts/pmlc.py` | yes |
| openpyxl | 3.1 or newer (`requirements.txt`) | reads the ProbeMatrix export and writes the register workbook | yes |
| pytest | 8 or newer (`requirements-dev.txt`) | runs the test suite | contributors |
| Node.js | 18 or newer | runs the JavaScript tests of the dashboard's Detailed register tab (skipped if absent) | contributors, optional |
| git, and the GitHub CLI `gh` | any recent | cloning, pull requests | contributors |
| A web browser | any current | opens `organisation-learning-map.html` (works offline) | yes |

**Set up a local clone** (a virtual environment keeps the packages out of your system Python):

```bash
git clone https://github.com/ashley-eyekyam/probematrix-learnings-coach
cd probematrix-learnings-coach
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt        # Windows: .venv\Scripts\pip install -r requirements-dev.txt
.venv/bin/python -m pytest tests                      # Windows: .venv\Scripts\python -m pytest tests
```

`requirements.txt` holds what the engine needs at run time; `requirements-dev.txt` adds the test tools.

**When an agent runs the engine with your system `python3`** (Claude Code, Claude desktop, Codex), that Python also needs openpyxl:
- macOS or Windows: `python3 -m pip install --user openpyxl`
- Debian or Ubuntu, where the system Python refuses `pip install`: `sudo apt install python3-openpyxl`
- Or point the agent at the virtual environment: `.venv/bin/python skills/learnings-coach/scripts/pmlc.py ...`

## Try it

1. Download an export from [`samples/`](samples/) or export your own investigation from ProbeMatrix.
2. Ask your agent, for example:
   - "Here's a ProbeMatrix export. What should our supervisors learn from it?"
   - "Make toolbox-talk learning cards for the maintenance crews."
   - "Prepare a board briefing with the questions directors should ask."
   - "Build a learnings register and the organisation learning dashboard."
   - "Compare this with the official enquiry report (attached)."

## Where outputs go

Every run gets one folder next to the export, named by incident date, site and event:

```
<export-dir>/pmlc-runs/2020-09-24-hazira-gas-release-fire/
  workspace/   findings, evidence, clusters (rebuildable from the export)
  outputs/     learnings register (.json, .xlsx, .md), organisation-learning-map.html, audience packs (<skill>.html + .md)
```

`organisation-learning-map.html` opens offline. With a Learnings Register it has two tabs: **Overview** (who must learn what) and **Detailed register** (every learning, recommendation, finding and evidence quote, with views for frontline, supervisors, managers, site leaders, board, investigators and auditors).

Every audience and analysis skill writes a learning pack, a self-contained HTML page too: collapsible sections, every Finding and Evidence ID expandable to the full record, a coverage note, search and print. The same content is in `<skill>.md`.

To share a run with others, publish it under [`samples/<slug>/`](samples/) (see the rules there).

## Principles

Learning, not blame. Roles, never names. Every sentence traces to Finding and Evidence IDs. Learnings, not finding counts. Every output is marked *Learning purposes: not a statutory document*. See [`learning-principles.md`](skills/learnings-coach/references/learning-principles.md).

## About ProbeMatrix

ProbeMatrix by Eyekyam is a human-in-the-loop, AI-assisted incident investigation service built on the four-level Human Factors Analysis and Classification System. AI widens the search; trained investigators test every suggestion against the evidence; the organisation decides what it adopts. This coach is free and open source; the investigations it reads come from ProbeMatrix.

**Want a ProbeMatrix investigation of your own incident, or a second look at a closed one?** ashley@eyekyam.com

## Licence

MIT. See [`LICENSE`](LICENSE). Sample exports are derived from public-record reports; see each sample's README.
