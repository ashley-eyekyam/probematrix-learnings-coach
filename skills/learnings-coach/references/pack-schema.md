# Learning pack schema (version 1)

Every audience and analysis skill writes its deliverable as one **pack**: a JSON file the engine checks and renders.

```bash
PMLC check-pack <ws> <run>/outputs/<skill>.json     # lists every problem with its JSON path; fix them all
PMLC pack <ws> <run>/outputs/<skill>.json           # -> <run>/outputs/<skill>.html (primary) and <skill>.md
```

The HTML is a self-contained offline page:
- collapsible sections, and a contents list
- citation buttons that open the full finding or evidence record
- a coverage footer
- search, deep links (`#s/<section-id>`, `#i/<item-id>`) and print

The Markdown is generated from the same JSON. Never hand-edit either file; change the pack and run `pack` again.

## Top level

```json
{
  "pack": "supervisor-coach",
  "schema": 1,
  "title": "Supervisor Coach: Gas terminal fire, 2020",
  "audience": "T2 first-line supervision",
  "status": "Learning purposes: not a statutory document",
  "bottom_line": [{"text": "…", "cites": ["FND-…", "EVD-…"]}],
  "scope": {"tiers": ["T2"], "levels": [3], "entities": ["F02"], "min_rating": 4},
  "sections": [{"id": "before-work", "heading": "Before work starts", "intro": "optional", "items": [ … ]}]
}
```

- **`pack`:** the skill name, which is also the file name. It is lowercase words joined by hyphens, or `dossier-F<nn>` for `cluster-learning-dossier` (a lettered entity keeps its letter: `dossier-F09b`).
- **`status`:** must contain `Learning purposes: not a statutory document`.
- **`bottom_line`:** 1 to 7 takeaways, each citing at least one Finding or Evidence ID.
- **`scope` (optional):**
  - It says which findings the pack should cover, using the same filters as `PMLC select`. Tiers and entities need `clusters.json`.
  - Without a scope, coverage is measured against the top-rated findings.
  - The page shows "This pack cites *x* of *y* relevant findings" and lists the rest.
- **IDs:**
  - Section `id`s, and item `id`s when given, are lowercase words joined by hyphens and unique within the pack.
  - Items without an `id` get `<section-id>-<n>`.
- **Citations:** go in `cites` (a list of IDs) or inline in body text as `[FND-…; EVD-…]`. Every cited ID must exist in the workspace. Inline IDs count only in fields that render as text: not in headings, titles, badges (`to`, `owner`, `when`, `barrier`, `type`, `audience`, `duration`), table column headers or graph labels. There they show as plain text, and `check-pack` warns.
- **Text:** plain text only. No HTML or Markdown markup; a blank line starts a new paragraph.

## Item kinds

`*` marks a required field. List fields hold non-empty text. `cites` is optional except where marked **must cite**.

| Kind | Fields | Typical use |
|---|---|---|
| `para` | text* | narrative, explanation |
| `check` | text*, hold_point (true/false), when | checklists, hold points, what to refuse; readers can tick them on screen |
| `question` | question*, why*, good_evidence, to (role asked) | board questions, questions to raise, interview questions |
| `recommendation` | change*, indicator*, hoc_tier*, barrier, owner, by_when; **must cite** | what should change, with its leading indicator and hierarchy-of-controls tier |
| `decision` | decision*, options[], trade_offs, owner, by_when | decisions for leaders, pending engineering decisions |
| `indicator` | name*, measure*, deterioration, owner | leading indicators, readiness indicators |
| `card` | title*, what_happened*, why_made_sense, warning_signs[]*, good_looks_like*, discussion[]; **must cite** | Learning Cards (`output-style.md`) |
| `scenario` | situation*, prompts[]* | coaching conversations, drills, exercises |
| `table` | columns[]*, rows[][]*, row_cites[][], row_supporting_cites[][] | anything tabular; each row has as many cells as there are columns |
| `test_point` | requirement*, sample*, conformity_evidence*, red_flags[]; **must cite** | audit test points |
| `module` | title*, objective*, audience, duration, content[]*, assessment[] | training modules |
| `barrier` | barrier*, failure_mode*, hoc_tier*, type, fix, owner, state (absent, degraded, defeated, worked partly, worked), indicator; **must cite** | barrier analysis |
| `timeline` | events[]*: {date* (YYYY-MM-DD, YYYY-MM or YYYY), time (HH:MM), text*, signal (true/false), received_by, response, cites[]} | precursors, response timelines; events sort by date then time, and same-date events without a time keep your order |
| `graph` | nodes[]*: {id*, label*}; edges[]*: {from*, to*, label} | causal maps, interfaces; drawn as SVG with a text list of links |
| `learning` | lesson* (one sentence), explanation (two to four sentences), owner (who must learn it); **must cite** | a learning: the lesson, why, and its evidence (dossiers, manager and leadership coaches, signal and interface learnings) |

## Optional on every pack and item

| Field | Where | What it does |
|---|---|---|
| `incident` | top level: `{"title": "…", "date": "YYYY-MM-DD"}` | Overrides the export's summary-sheet title and date in the page header and in the Markdown's `**Incident:**` line (use it when the profile flags them as wrong). |
| `data_quality` | top level: list of `{"text": "…", "cites": [...]}` | Data-quality corrections and limits (wrong dates, wrong incident type, draft status). Shown in a box under the status line. |
| `exclusions` | top level: list of `{"id": "FND-…", "reason": "…"}` | Findings left out on purpose (e.g. a reviewer downgrade vote). They leave the coverage total and are listed with their reason. A finding is either cited or excluded, never both. |
| `supporting_cites` | any item or bottom-line entry | Further Finding/Evidence IDs for the same condition. They count for coverage and are shown collapsed ("+N supporting"); keep `cites` to the key evidence. |
| `evidence_strength` | any item or bottom-line entry | `direct`, `corroborated` or `inferred` (`learning-principles.md`), shown as a badge. On a recommendation (or any item) it rates the evidence for the condition the item describes, not how well a proposed fix will work. |
| `group` | any item | A label such as a supervisor habit, a question mix or an interviewee role; a subheading is shown whenever it changes. |

A table's `row_cites` appear as an extra last column labelled **Cites**; `row_supporting_cites` (one list per row, may be empty) add a collapsed "+N supporting" to that cell and count for coverage. `check-pack` warns when a pack cites fewer than a quarter of its relevant findings; the page always shows the count and lists the rest.

`hoc_tier` must name one of: elimination, substitution, engineering, administrative, training, ppe. Free wording such as "Engineering control: interlock" is fine.

## Examples

```json
{"kind": "check", "text": "Leak-test record attached and signed.", "hold_point": true,
 "when": "before return to service", "cites": ["FND-…", "EVD-…"]}
{"kind": "recommendation", "change": "Interlock pump start on a signed leak-test record", "hoc_tier": "engineering",
 "barrier": "Return-to-service test", "owner": "Maintenance supervisor",
 "indicator": "% of pump restarts with a leak-test record on the shift log", "cites": ["FND-…"]}
{"kind": "question", "question": "How do we know critical spares meet specification at every site?",
 "why": "Local purchasing bypassed the specification.", "good_evidence": "A sampled audit against specifications.",
 "to": "Chief Executive", "cites": ["FND-…"]}
```

## investigator-coach

Its pack must contain a `table` with `"id": "follow-up"` and columns `Finding`, `Evidence to collect`, `Key questions`, `Suggested interviews`, `Causal hypothesis`, with Finding IDs in the first cell of each row. A row may list several Finding IDs (one row per condition, comma-separated); `follow-up.json` gets one entry per finding, and a finding may appear in only one row. `pack` also writes `<run>/outputs/follow-up.json` from it (finding ID → `evidence_to_collect`, `key_questions`, `suggested_interviews`, `causal_hypothesis`). An optional `finding_notes` object on that table (`{"FND-…": "note"}`) gives one finding in a shared row its own note: it is shown under the table and copied to that finding's `note` in `follow-up.json`. Every key must appear in the table's first column.
