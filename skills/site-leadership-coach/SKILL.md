---
name: site-leadership-coach
description: Produces learning for site and asset leadership from a ProbeMatrix investigation export - plant manager, head of operations, site leadership team - on the decisions, trade-offs, resourcing, authority and culture signals that shaped the event, the decisions within site authority, what leaders should visibly model, and a management-review input. Use when someone asks what plant or site leaders should learn, for a leadership-team debrief or workshop, a site management review, or "what does the plant manager need to decide" after an incident with a ProbeMatrix export. Not for one function's own action agenda (use `manager-coach`).
---

# Site Leadership Coach

Audience: T4 plant and asset leadership. They set site priorities, allocate budgets and people, delegate authority and, by what they tolerate, set the norms. Read `learnings-coach/references/learning-principles.md`.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 and §2.

Engine: `PMLC`, as `skill-common.md` §1 defines it (this skill needs the `learnings-coach` skill installed alongside it).

This skill needs the **workspace** and **clusters**. It uses, when present: the register (`<run>/outputs/learnings-register.json`), the causal graph, the timeline and the adoption record.

Start from the register if present: `PMLC register-items <ws> --tier T4` gives the site learnings with their wording; carry `learning: "LR-nn"` on every item that expresses a register learning.

## Gather

```bash
PMLC select <ws> --tier T4 --brief
PMLC select <ws> --level 4 --top-rated
PMLC select <ws> --relation norm_setter learner absent challenger --brief   # who set, received or did not challenge norms
PMLC select <ws> --prefix OIC --level 4 --brief                             # culture fallback: organisational climate findings
PMLC causal-item <ws> --top 20                                              # the causal map, ready to paste
PMLC table-item <ws> hubs --top 8                                           # organisational hubs: most downstream links
PMLC timeline-item <ws> --before incident --top 12                          # signals before the event
PMLC register-items <ws> --tier T4                                          # the register's site learnings (needs the register)
```

`select --preset site-leadership-coach` runs the four select calls at once. The relation filter often returns few findings; the `--prefix OIC` call reads the L4 organisational-climate findings (culture, norms, structure) so the culture section is not thin.

## Write

Write the pack `<run>/outputs/site-leadership-coach.json` in the shape in `learnings-coach/references/pack-schema.md`. Set `"scope": {"tiers": ["T4"]}`.

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/site-leadership-coach.json (repository only)

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | The learnings for the leadership team, one sentence each | `bottom_line` | up to 5 |
| 1 | `set-up` | How the site set this up | The `causal-item` graph pasted unchanged; drop nodes only if you must | `graph` | 1 |
| 1 | `set-up` | (same section) | One `para` per pathway from the hubs to the event, `group` = the pathway's name, read top-down and ending on a condition | `para` | up to 3 |
| 2 | `signals` | Signals that reached leadership | The `timeline-item` output with `signal`, `received_by` and `response` on each event you keep | `timeline` | 1 |
| 3 | `culture` | Culture signals | What had become normal, what leaders modelled or tolerated, where challenge was absent. Norms, not people | `para` | up to 4 |
| 4 | `decisions` | Decisions for the leadership team | A choice with options, trade-off (cost, production, staffing, authority) and `owner` = a function; mark escalations (below) | `decision` | up to 10 |
| 4 | `decisions` | (same section) | The leading indicator leadership will watch, after its decision in the same `group`, with `deterioration` | `indicator` | up to 10 |
| 5 | `visible` | What leaders will do visibly | Walk-throughs, questions to ask in reviews, things to stop accepting; `when` = "next 30 days" | `check` | up to 6 |
| 6 | `management-review` | Management review input | The six-row table (below) | `table` | optional, up to 1 |
| 7 | `workshop` | Leadership workshop agenda (two hours) | Columns Time, Activity, Built on; built on sections 1, 3 and 4 | `table` | 1 |

Rules for the content:

- **Site authority.** Keep decisions to what the site can decide. A decision that needs corporate authority (an enterprise standard, a capital budget above site limits, a corporate policy) opens its `decision` text with "Needs corporate decision:" and is an input to `top-management-brief`. Include delegation-of-authority decisions when the findings show escalation delays.
- **Culture.** Describe norms, not people. This is the most sensitive content in the pack: keep it to what the findings record.
- **Management review input** (ISO 45001 9.3). Write it when the user asks for a management review or the debrief feeds one. One `table`, columns Input, What this investigation shows, Indicator, Deterioration trigger, with **exactly six rows** in this order: Incidents and corrective actions; Monitoring results; Audit results; Risks and opportunities; Adequacy of resources; Consultation outcomes. Each row cites its findings in `row_cites`, or reads "not in this investigation" in the second cell with an empty cites list; every row with cites names an indicator and its deterioration trigger (`learnings-coach/references/indicators-and-effectiveness.md` §1).
- **Owner wording.** `owner` is the function that **owns the change**, not who "was involved".

```json
{"kind": "decision", "group": "Spares specification", "decision": "Require a specification for every critical-spares order",
 "options": ["…", "…"], "trade_offs": "…", "owner": "Site operations function", "learning": "LR-01", "cites": ["FND-…"]}
```

## If the evidence is thin

- **Few L4 findings for T4:** write the decisions the evidence supports (one per supported theme), not six to ten; say so in `limits`.
- **The relation and OIC selections both return little:** write one culture `para` that states what the findings do not show, and a `gaps` entry for the interviews that would show it.
- **No causal links** (`causal-item` prints an empty graph): run `PMLC causal <ws>` first; if it is still empty, say so and tell the pathways from the cited findings only.

## Not covered here

- One function's system learnings, indicators and 90-day agenda: `manager-coach`.
- Enterprise standards, investment and decisions marked "Needs corporate decision": `top-management-brief`.
- The board's oversight questions: `board-brief`.
- The full causal map and precursor timeline: `causal-map`, `precursor-timeline`.

## Check and hand over

Run `learnings-coach/references/skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/site-leadership-coach.json --strict   # fix every problem it lists
PMLC pack <ws> <run>/outputs/site-leadership-coach.json                  # -> site-leadership-coach.html (open first) and .md
PMLC pack <ws> <run>/outputs/site-leadership-coach.json --format pptx    # the workshop deck: site-leadership-coach.pptx
PMLC pack <ws> <run>/outputs/site-leadership-coach.json --format docx    # the debrief as a Word paper
```

**The workshop deck** (L4-04). Offer the `.pptx` for the two-hour workshop in section 7: one slide per bottom-line point and per decision, the causal map as boxes and arrows the facilitator can move, the citations and full text in the speaker notes, and the status line on every slide. Run the workshop from the deck and keep the HTML open for the evidence (`skill-common.md` §8).

Also confirm: every decision is within site authority or marked "Needs corporate decision", and the management-review table, if present, has exactly the six rows. Next: `top-management-brief` for the escalated decisions, or `manager-coach` for the function agendas.
