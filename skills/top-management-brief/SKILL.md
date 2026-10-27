---
name: top-management-brief
description: Produces an executive brief from a ProbeMatrix investigation export for the CEO, executive committee, corporate HSE and corporate function heads - which learnings transfer across sites, which policies, standards and legal requirements they implicate, the enterprise decisions to take and a management-review input. Use when someone asks for an ExCo or CEO brief, an enterprise-wide lessons note, cross-site learning, a corporate standards review or "what does head office need to do" after an incident with a ProbeMatrix export. Not for directors' oversight questions (use `board-brief`) or audit test points (use `auditor-assurance-pack`).
---

# Top Management Brief

Audience: T5 corporate leadership. They set policy, enterprise standards and investment, and they decide whether a lesson from one site is applied at every site. The executive committee decides and resources; the board oversees and asks. Read `learnings-coach/references/learning-principles.md`.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 and §2.

Engine: `PMLC`, as `skill-common.md` §1 defines it (this skill needs the `learnings-coach` skill installed alongside it).

This skill needs the **workspace** and **clusters**. It uses, when present: the register (`<run>/outputs/learnings-register.json`), the causal graph, the adoption record and the could-it-happen-here pack (`<run>/outputs/could-it-happen-here.json`).

Start from the register if present: take the enterprise learnings from it (`register-items --tier T5`, then `--tier T4`) and carry `learning: "LR-nn"` on every item that expresses a register learning.

## Gather

```bash
PMLC select <ws> --tier T4 T5 --brief
PMLC select <ws> --level 4 --top-rated
PMLC select <ws> --tag people corporate assurance --level 4 --brief   # people, corporate, assurance functions
PMLC select <ws> --tag leadership corporate --level 4 --brief         # plant and corporate leadership functions
PMLC register-items <ws> --tier T5                                    # the register's T5 learnings (needs the register)
PMLC facts <ws>                                                       # headline numbers and priority-1 learnings by tier
```

`select --preset top-management-brief` runs the four select calls at once. Select by tag, not by F-id, so the brief survives an organisation's own taxonomy.

## Write

Four pages at most. Write the pack `<run>/outputs/top-management-brief.json` in the shape in `learnings-coach/references/pack-schema.md`. Set `"scope": {"levels": [4], "min_rating": "top"}`.

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/top-management-brief.json (repository only)

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | The three enterprise-level learnings | `bottom_line` | up to 3 |
| 1 | `summary` | Executive summary | Half a page: what happened in two sentences, the decisions requested; define the four HFACS levels once | `para` | up to 3 |
| 2 | `transferability` | Transferability | Columns Learning, Transferability (site-specific, likely at similar sites, enterprise-wide), Reason (shared standard, system, culture or vintage of equipment); `row_cites` | `table` | 1 |
| 3 | `sister-sites` | Sister sites | Only when `<run>/outputs/could-it-happen-here.json` exists: one `para` naming that pack as the self-assessment the other sites run, and the learnings it covers; leave the section out otherwise | `para` | optional, up to 1 |
| 4 | `policies` | Policies, standards and legal requirements implicated | One `para` per policy, standard or legal requirement (`group` = its name): what the evidence shows about its implementation; `clauses` where a crosswalk requirement applies | `para` | up to 8 |
| 5 | `decisions` | Decisions for top management | Each with options and trade-off; `group` opens "For decision:" or "For noting:" | `decision` | up to 6 |
| 5 | `decisions` | (same section) | The enterprise indicator that would show progress, after its decision in the same `group`, with `deterioration` | `indicator` | up to 6 |
| 6 | `management-review` | Management review input | The six-row table (below) | `table` | optional, up to 1 |
| 7 | `assurance` | Assurance | How the organisation will know the learning is applied across sites; `to` = the role asked | `question` | up to 6 |

Rules for the content:

- **Decisions.** Mark each decision "For decision:" (the committee must choose) or "For noting:" (already decided, or within a function's authority) in its `group`, such as `"group": "For decision: critical spares"`. A site decision marked "Needs corporate decision" in `site-leadership-coach` comes here as "For decision".
- **Policies, standards and legal requirements.** Cover corporate policies and standards (change management, spares and sourcing, maintenance strategy, emergency planning, competence, audit) and the external requirements the learnings touch, for the legal-register review. Take requirement ids from `learnings-coach/references/standards-crosswalk.json` (`clauses`, such as `ISO45001-10.2`) and the regimes from `learnings-coach/references/jurisdictions.md`. Say what the evidence shows; never that a requirement was breached.
- **Management review input** (ISO 45001 9.3, RBPS management review). Write it when the user asks for a management-review input or the brief goes to a management review. One `table`, columns Input, What this investigation shows, Indicator, Deterioration trigger, with **exactly six rows** in this order: Incidents and corrective actions; Monitoring results; Audit results; Risks and opportunities; Adequacy of resources; Consultation outcomes. Each row cites its findings in `row_cites`, or reads "not in this investigation" in the second cell with an empty cites list. Every row with cites names an indicator and its deterioration trigger (`learnings-coach/references/indicators-and-effectiveness.md` §1).
- **Sister sites** (L1-06). When the `could-it-happen-here` pack exists, say that the other sites assess these learnings with it, cite the findings behind them, and never rank or compare sites. Without it, leave the section out; never describe a self-assessment that was not written.
- **Assurance** questions point to `auditor-assurance-pack` for the test points.
- Board-ready language. Neutral, factual tone; no blame of management or staff; roles only. Name the function that owns the change, not the post.

```json
{"kind": "decision", "group": "For decision: critical spares", "decision": "Set one enterprise rule for critical-spares specifications",
 "options": ["Mandatory standard", "Guidance with audit"], "trade_offs": "…", "learning": "LR-02", "cites": ["FND-…"]}
```

## If the evidence is thin

- **T5 is empty** (common in plant-level exports): fall back to T4 and L4 findings, reason about transferability from them, and say in `limits` that no finding names corporate leadership directly.
- **A management-review input with no evidence:** write the row as "not in this investigation"; never fill it from outside the export.
- **Few L4 findings at the top rating:** fewer decisions, not padded ones (`skill-common.md` §6).

## Not covered here

- Directors' oversight questions and the ask of the board: `board-brief`.
- Audit test points and the cross-site verification protocol: `auditor-assurance-pack`.
- Site decisions and the leadership workshop: `site-leadership-coach`.
- The function-by-function action agenda: `manager-coach`.
- The sister sites' self-assessment itself: `could-it-happen-here`.

## Check and hand over

Run `learnings-coach/references/skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/top-management-brief.json --strict   # fix every problem it lists
PMLC pack <ws> <run>/outputs/top-management-brief.json                  # -> top-management-brief.html (open first) and .md
PMLC pack <ws> <run>/outputs/top-management-brief.json --format docx,pptx   # the ExCo paper (.docx) and its slides (.pptx)
PMLC pack <ws> <run>/outputs/top-management-brief.json --format email       # a digest for the executives' inboxes
```

Offer the Word paper when the brief goes into an executive-committee pack, the slides when someone presents it, and the email digest (`.email.html` and `.email.txt`) for a pre-read; each carries the status line and, until a person approves it, DRAFT (`skill-common.md` §8).

Also confirm: every decision is marked "For decision" or "For noting", and the management-review table, if present, has exactly the six rows. Next: `board-brief` for the board's oversight questions, or `auditor-assurance-pack` for cross-site verification.
