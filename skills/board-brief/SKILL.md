---
name: board-brief
description: Produces a board paper from a ProbeMatrix investigation export for directors and the board's safety or risk committee - what the investigation shows about governance, oversight and assurance, the questions directors should put to management, and the assurance to request. Use when someone asks for a board paper, a board safety committee briefing, a directors' brief, oversight questions or "what should the board ask" after an incident with a ProbeMatrix export. Not for executive decisions on enterprise standards and investment (use `top-management-brief`).
---

# Board Brief

Audience: the board and its safety or risk committee. Directors do not manage the site; they oversee whether management's systems work and whether the assurance they receive is true. Their learning is about **oversight and assurance**, not operations. Read `learnings-coach/references/learning-principles.md` and the board question block in `learnings-coach/references/output-style.md`.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 and §2.

Engine: `PMLC`, as `skill-common.md` §1 defines it (this skill needs the `learnings-coach` skill installed alongside it).

This skill needs the **workspace** and **clusters** (`setup` makes both). It uses, when present: the register (`<run>/outputs/learnings-register.json`), the causal graph, the timeline and the organisation's adoption record (`<run>/outputs/adoption.csv`).

Start from the register if present: take the board-level learnings from it and carry `learning: "LR-nn"` on every item that expresses a register learning.

## Gather

```bash
PMLC select <ws> --level 4 --top-rated --brief
PMLC select <ws> --tag assurance --level 3 4 --brief        # audit and assurance findings
PMLC select <ws> --text "recommendation|alert|overdue|repeat|earlier|previous" --level 3 4 --top-rated --brief   # earlier warnings
PMLC register-items <ws> --tier T5                          # the register's board-level learnings: reuse wording and LR ids
PMLC timeline-item <ws> --before incident --top 8           # signals that existed before the event
PMLC table-item <ws> adoption                               # management's response to each learning (needs adoption.csv)
```

`select --preset board-brief` runs the three select calls at once. Look specifically for audit recommendations left open, earlier alerts or recommendations that were not acted on, internal audits that did not detect conditions, indicators that looked green while conditions degraded, and risk accepted without documented authority.

## Write

A board paper: the cover (bottom line and the ask of the board) on page one, then the body in two to three pages. Write the sections in the order below; the paper layout (`--layout paper`, under Check and hand over) moves the questions to Annex A and the tables and indicators to Annex B by itself. Write the pack `<run>/outputs/board-brief.json` in the shape in `learnings-coach/references/pack-schema.md`. Set `"scope": {"levels": [3, 4], "min_rating": "top"}`.

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/board-brief.json (repository only)

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | The cover summary: the governance learnings, one sentence each, each citing its findings | `bottom_line` | up to 7 |
| 1 | `ask` | Ask of the board | On the cover. One `para` per ask, opening "To note:", "To request assurance:" or "To approve:"; approve only what management has put to the board | `para` | up to 3 |
| 2 | `what-happened` | What happened and why it matters to the board | One paragraph, no technical detail beyond what a director needs | `para` | up to 2 |
| 3 | `management-system` | What the investigation says about the management system | One `para` per governance learning: assurance that did not detect, signals that did not escalate, risk accepted without authority, resources | `para` | up to 5 |
| 4 | `management-response` | Management response status | The `table-item adoption` output pasted unchanged; only when `adoption.csv` holds responses | `table` | optional, up to 1 |
| 5 | `questions` | Questions for directors to ask management | Board question format (question, why, good_evidence, `to` = the role asked). Mix this site, all sites and assurance quality, and ask whether earlier alerts and recommendations were acted on | `question` (with `to`) | up to 12 |
| 6 | `assurance` | Assurance the board should request | Columns Verification, Sites, Requested reporting date; `row_cites`. A request to management, not a plan | `table` | 1 |
| 7 | `indicators` | Indicators for the board dashboard | Leading indicators that would have shown deterioration earlier, each with `deterioration` | `indicator` | up to 5 |
| 8 | `governance` | Governance duties touched | Names the frameworks the learnings touch, with no legal conclusions (below) | `para` | optional, up to 1 |
| 9 | `follow-up` | Tracking the board's questions | One `check`: minuted questions need tracked answers (below), citing the findings behind the questions it tracks | `check` | 1 |

Rules for the content:

- **Ask of the board.** Board secretaries need it on the cover. "To note" is the default; "to request assurance" points to section 6; "to approve" only for a proposal management has made (the export rarely holds one).
- **Requested reporting date.** The Requested reporting date cell reads "for the board to set" unless the user gives a date. Never invent one (`learning-principles.md` §6).
- **Management response.** Paste the `table-item adoption` item unchanged when `<run>/outputs/adoption.csv` holds responses. With no adoption record, leave section 4 out and add a `limits` line: "Management's response to each learning is not yet recorded (`PMLC templates <ws> adoption`)."
- **Earlier alerts.** Ask at least one question on whether earlier alerts, audit recommendations or the register's priority-1 learnings were acted on, when the evidence shows any.
- **Governance duties touched.** Write it when the user names a jurisdiction or the run has one (`PMLC run-manifest`). Name the board-reporting frameworks the learnings touch: the statutory ones from the "Board reporting" lines of `learnings-coach/references/jurisdictions.md` (such as UK Corporate Governance Code Provision 29, Companies Act 2013 s.134, SEBI BRSR Principle 3) and, when the organisation reports under the GRI Standards, the voluntary disclosure GRI 403-2 (hazard identification, risk assessment and incident investigation), which `jurisdictions.md` does not list. Say which learnings bear on which framework and stop there: no statement that a duty applies, was met or was breached. Whether and how to disclose is for the board's own advisers.
- **Tracking.** The `follow-up` check reads, in substance: "Record each question the board minutes, the answer management gives and when; a minuted question with no tracked answer stays open." Give it the `cites` of the questions in section 5, like every other item. Board minutes can be disclosed later, so a question asked and never answered is worse than one never asked.
- **Indicators.** Specify each as in `learnings-coach/references/indicators-and-effectiveness.md` §1; thresholds are for the owner to set.
- Neutral, factual tone; no blame of management or staff; roles only. Any `owner` is the function that **owns the change**, not who "was involved".

```json
{"kind": "question", "question": "Were the earlier audit recommendations on critical spares closed with evidence?",
 "why": "…", "good_evidence": "…", "to": "Chief Executive", "learning": "LR-02", "cites": ["FND-…"]}
```

## If the evidence is thin

- **Few L3–L4 findings at the top rating:** write fewer questions and indicators rather than padding (`skill-common.md` §6). Two grounded questions are better than twelve thin ones.
- **No T5 findings and no register:** the board brief still stands on L3–L4 findings; say in `limits` that no finding names the board or corporate leadership directly, and do not invent board-level conditions.
- **No dated signals** (`timeline-item` returns none): leave signals out of section 3 and add a `gaps` entry for the records that would date them.

## Not covered here

- Executive decisions, enterprise standards and investment: `top-management-brief`.
- Site decisions and the leadership workshop: `site-leadership-coach`.
- The independent audit test points behind section 6: `auditor-assurance-pack`.
- Legal advice, disclosure decisions and statutory reports: the organisation's advisers; the pack is "Learning purposes: not a statutory document".

## Check and hand over

Run `learnings-coach/references/skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/board-brief.json --strict   # fix every problem it lists
PMLC pack <ws> <run>/outputs/board-brief.json                  # -> board-brief.html (open first) and board-brief.md
PMLC pack <ws> <run>/outputs/board-brief.json --format docx --layout paper   # the board paper: .docx, .paper.docx, .paper.html
```

The board paper (L4-20) is what a board secretary files: `board-brief.paper.docx` has a cover with the status and reading time, "Decisions requested" (the bottom line), numbered paragraphs, Annex A (the questions) and Annex B (the assurance table and indicators); `board-brief.paper.html` prints the same from a browser. Offer it whenever the brief goes to a board pack. Formats and channels: `skill-common.md` §8.

Also confirm: the ask of the board is on the cover, every Requested reporting date is "for the board to set" or the user's date, and the governance paragraph draws no legal conclusion. This skill's `share_default` is `external`: a copy for anyone outside the organisation follows `skill-common.md` §7. Next: `top-management-brief` for the executive decisions the questions point to.
