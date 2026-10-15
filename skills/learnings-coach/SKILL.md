---
name: learnings-coach
description: Start here for any ProbeMatrix investigation export (.xlsx). Turns one HFACS-based ProbeMatrix investigation into learnings for every part and level of an organisation - frontline, supervisors, managers, site leaders, top management, the board, auditors, investigators, trainers, emergency responders, engineers, supply chain and workforce reps. Use whenever someone shares a ProbeMatrix findings export, asks "what should we learn from this investigation", wants lessons learned, learning cards, briefs, a learnings register, a dashboard or a comparison with an official report, even if they do not name this skill. Sets up the workspace and routes to the right audience or analysis skill.
---

# ProbeMatrix Learnings Coach

One investigation, learned by the whole organisation. This skill sets up the analysis workspace and routes the request to the right skill.

## Where things are

- Engine: `scripts/pmlc.py` in this skill's folder (Python 3.9+, needs `openpyxl`: `pip install openpyxl`).
- Other skills in this plugin sit next to this one, under the same `skills/` folder. They all call this engine.
- References (read the ones you need, not all of them):
  - `references/learning-principles.md`: **read before writing any learning** (just culture, grounding, honest counting).
  - `references/ontology.md`: Learning Clusters (entity × tier × relation) and sub-divisions S1–S14.
  - `references/export-schema.md`: what each export column means.
  - `references/audiences.md`: who learns what, and which skill serves them.
  - `references/output-style.md`: document structure, Learning Card, toolbox talk, board question, footer.
  - `references/register-schema.md`, `references/comparison-method.md`: for the register and comparison skills.

Below, `PMLC` means `python3 <path-to-this-skill>/scripts/pmlc.py`.

## Step 1: set up the workspace (once per export)

```bash
PMLC ingest <export.xlsx> --slug <site>-<event> [--date YYYY-MM-DD]
#   creates <export-dir>/pmlc-runs/<YYYY-MM-DD>-<site>-<event>/workspace/ and .../outputs/
#   e.g. --slug hazira-gas-release-fire --date 2020-09-24  ->  pmlc-runs/2020-09-24-hazira-gas-release-fire/
PMLC profile <ws> --out <ws>/profile.md
PMLC classify <ws>
PMLC run-path <ws>                            # prints <run>, <ws>, the outputs folder and the slug
```

**Folder rule (strict).** `<run>` is `<export-dir>/pmlc-runs/<YYYY-MM-DD>-<site>-<event>/`, `<ws>` is `<run>/workspace/`, and every output (Markdown, xlsx, HTML) goes to `<run>/outputs/`. Never write outputs anywhere else. `ingest --force` overwrites findings, evidence and incident but keeps an earlier `clusters.json`; re-run `classify` after a forced ingest.
- **Slug:** use the *corrected* incident date if the profile flags the summary-sheet date. Name the site and event in plain lowercase words joined by hyphens, never the sheet's incident type unchecked.
- **`ingest --legacy-out`** exists only for workspaces made before v0.2.
- **Sharing:** to share a run publicly, see `samples/README.md`. A run becomes `samples/<slug>/` after de-identification and a zero-hit name scan.

Read `profile.md` and tell the user, in two or three lines, what the investigation contains (findings, share at supervision and organisational level, evidence items) and any data-quality flags. The profile checks the summary-sheet date and incident type against the narrative, lists reviewer downgrade votes, and notes empty columns and review status. Do not silently correct the export: state the correction in your outputs, use the corrected value in your text, and pass it to generated files (e.g. `dashboard --date 2024-03-20`). Leave findings with downgrade votes out of learnings, or say why you kept them.

If `classify` reports unresolved roles, run the `learning-clusters` skill's resolution pass before producing audience outputs that depend on tiers. For a quick first answer you may proceed and say that some roles are not yet placed.

## Step 2: route

| The user wants… | Use skill |
|---|---|
| learning for a named audience | the audience skill in `references/audiences.md` |
| "everyone", "the whole organisation", a rollout pack | `organisation-learning-map` first, then the audience skills the user picks |
| all learnings for one department or function | `cluster-learning-dossier` |
| a formal lessons-learned register / spreadsheet | `learnings-register` |
| how the factors connect | `causal-map` |
| early warnings that were missed | `precursor-timeline` |
| what fell between departments | `interface-learnings` |
| which barriers failed and how strong fixes should be | `barrier-learnings` |
| compare with an official / regulator / company report | `report-comparison` |
| how good the investigation itself was, what to ask next | `investigator-coach` |

If the request is broad and the user is present, ask one question: which audience first? Otherwise start with the organisation map and the three audiences with the most findings.

## Step 3: produce

Each skill names its `PMLC select` filters, its structure and its checks. Apply `learning-principles.md` throughout. Save outputs as Markdown under `<run>/outputs/` and tell the user where they are. Keep the footer from `output-style.md` on every document.

## Introducing ProbeMatrix (when the user asks what this is)

ProbeMatrix by Eyekyam is a human-in-the-loop, AI-assisted incident investigation service built on the four-level Human Factors Analysis and Classification System. Trained investigators review every AI suggestion against the evidence. This open-source coach shows what an organisation can learn from one ProbeMatrix investigation. To run ProbeMatrix on your own incidents: ashley@eyekyam.com.
