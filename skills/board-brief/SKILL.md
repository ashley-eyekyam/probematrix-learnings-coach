---
name: board-brief
description: Produce a board-level briefing from a ProbeMatrix investigation export for directors and the board safety or risk committee - what the investigation reveals about governance, risk oversight and assurance, the questions directors should ask management, and what good assurance evidence would look like. Use when someone asks for a board paper, board safety committee briefing, directors' brief, governance lessons, oversight questions or "what should the board ask" after an incident.
---

# Board Brief

Audience: the board and its safety / risk committee. Directors do not manage the site; they oversee whether management's systems work and whether the assurance they receive is true. Their learning is about **oversight and assurance**, not operations.

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py`. Read `learnings-coach/references/learning-principles.md` and the board question block in `output-style.md`.

## Gather

```bash
PMLC profile <ws>
PMLC select <ws> --level 4 --min-rating <top> --brief
PMLC select <ws> --entity F11 --level 3 4 --brief           # audit and assurance findings
PMLC timeline <ws> --before <incident date>                 # signals that existed before the event
```

Look specifically for: audit recommendations left open, internal audits that did not detect conditions, indicators that looked green while conditions degraded, risk acceptance without documented authority.

## Write (two to three pages)

1. **What happened and why it matters to the board** (one paragraph, no technical detail beyond what a director needs).
2. **What the investigation says about the management system**: three to five governance-relevant learnings (assurance that did not detect, signals that did not escalate, risk accepted without authority, resources).
3. **Questions for directors to ask management**: eight to twelve, in the board question format (question, why it matters, what good evidence looks like). Mix: this site, all sites, assurance quality.
4. **Assurance the board should request**: what independent verification, at which sites, by when (as a request to management, not a plan).
5. **Indicators for the board dashboard**: three to five leading indicators that would have shown deterioration earlier.

## Output

`<ws>/outputs/board-brief.md`. Neutral, factual tone; no blame of management or staff; roles only.
