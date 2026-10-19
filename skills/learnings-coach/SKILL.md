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
  - `references/pack-schema.md`: the learning-pack JSON that skills render to HTML.

Below, `PMLC` means `python3 <path-to-this-skill>/scripts/pmlc.py`.

## Step 1: set up the workspace (once per export)

```bash
PMLC ingest <export.xlsx> --slug <site>-<event> [--date YYYY-MM-DD]
#   creates <export-dir>/pmlc-runs/<YYYY-MM-DD>-<site>-<event>/workspace/ and .../outputs/
#   e.g. --slug hazira-gas-release-fire --date 2020-09-24  ->  pmlc-runs/2020-09-24-hazira-gas-release-fire/
PMLC profile <ws> --out <ws>/profile.md
PMLC classify <ws>                            # add --overlay india-process-site for Indian process-site role words (remembered on re-run; --no-overlay clears)
PMLC run-path <ws>                            # prints <run>, <ws>, the outputs folder, the slug, top_rating and incident_date
PMLC status <ws>                              # which workspace files are out of date; re-run classify/ingest as it says
```

**Folder rule (strict).** `<run>` is `<export-dir>/pmlc-runs/<YYYY-MM-DD>-<site>-<event>/`, `<ws>` is `<run>/workspace/`, and every output (Markdown, xlsx, HTML) goes to `<run>/outputs/`. Never write outputs anywhere else. `ingest --force` overwrites findings, evidence and incident but keeps an earlier `clusters.json`; re-run `classify` after a forced ingest.
- **Slug:** use the *corrected* incident date if the profile flags the summary-sheet date. Name the site and event in plain lowercase words joined by hyphens, never the sheet's incident type unchecked.
- **Read-only upload folder** (as in the Claude app): if the export's folder is not writable, add `--root <a writable working folder>` to `ingest`; the run folder is then made under that folder's `pmlc-runs/`.
- **`ingest --legacy-out`** exists only for workspaces made before v0.2.
- **Sharing:** to share a run publicly, see `samples/README.md` (repository only). A public-record run becomes `samples/<slug>/`; the official report and ProbeMatrix material may be included unmodified, with no name scan required (learnings still follow just culture: roles only, no blame). `scan-names` remains available for your own organisation's runs.

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

Select by entity tag (`PMLC select --tag <tag>`) instead of hard-coding entity IDs where a tag exists.

Each skill names its `PMLC select` filters, its structure and its checks. Apply `learning-principles.md` throughout. Skills that produce a pack write `<run>/outputs/<skill>.json` (`references/pack-schema.md`), run `PMLC check-pack`, then `PMLC pack`, which writes `<skill>.html` (open this first) and `<skill>.md`. `learnings-register` writes its register (JSON, .xlsx, .md) there instead. Tell the user where the files are. Keep the footer from `output-style.md` on every document.

## Step 4: language check, review and sharing

- **Language check.** `check-pack` and `check-register` now run the same language check (rules JC1-JC12: names, blame wording, hindsight, outside facts, status). Errors fail the check. Run it alone with `PMLC check-language <ws> <pack.json> [--share internal|external|public] [--names FILE] [--orgs FILE]`. To fix a hit, rewrite the sentence with the hint it prints (roles for names, a system statement for blame or "failed to X"; see `learning-principles.md` §1a). Only if the wording is right, accept a hit with an item-level `"lint_ok": {"rule": "JCn", "reason": "..."}`.
- **Sign-off.** `PMLC sign-off <ws> <json> --role ROLE [--status reviewed|approved] [--classification ...] [--legal-review not-required|requested|cleared]` records a human review. **The model must never run sign-off unless the user says they reviewed it and gives their role.** Never write owners, due dates or a reviewer name yourself, and never write or edit the `handling` block yourself; only sign-off writes it. Sign-off is refused while the investigation status is in progress or no finding is marked as edited by a person; tell the user to finish the investigation in ProbeMatrix first.
- **What a page embeds.** `pack` and `dashboard` embed only the cited records (`--embed cited`, the default); findings left uncited carry their label and rating only, and printing lists only what is cited. `--embed summary` also drops evidence descriptions, quotes, suggested interviews, key questions and vote reasons; use it when `pack` notes that witness statements are embedded. `--embed full` embeds every relevant record, as v0.3 did.
- **Sharing outside the organisation.** `pack`, `dashboard` and `register-xlsx` accept `--share external|public`. For `pack` and `dashboard`, outside sharing embeds `summary` by default, and an explicit `--embed cited|full` is refused. They refuse unless the file is approved, its classification matches, and `legal_review` is cleared. Do not offer this unprompted; follow "Sharing outside the organisation" in `learning-principles.md` (§7).

## Introducing ProbeMatrix (when the user asks what this is)

ProbeMatrix by Eyekyam is a human-in-the-loop, AI-assisted incident investigation service built on the four-level Human Factors Analysis and Classification System. Trained investigators review every AI suggestion against the evidence. This open-source coach shows what an organisation can learn from one ProbeMatrix investigation. To run ProbeMatrix on your own incidents: ashley@eyekyam.com.
