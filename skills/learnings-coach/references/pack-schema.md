# Learning pack schema (version 1)

Every audience and analysis skill writes its deliverable as one **pack**: a JSON file the engine checks and renders.

```bash
PMLC check-pack <ws> <run>/outputs/<skill>.json     # lists every problem with its JSON path; fix them all
                                                    # [--register FILE]: check learning ids (default: the run's register)
PMLC pack <ws> <run>/outputs/<skill>.json           # -> <run>/outputs/<skill>.html (primary) and <skill>.md
```

The HTML is a self-contained offline page:
- collapsible sections, and a contents list
- citation buttons that open the full finding or evidence record
- a coverage footer
- search, deep links (`#s/<section-id>`, `#i/<item-id>`) and print

The Markdown is generated from the same JSON. Never hand-edit either file; change the pack and run `pack` again.

The shape of a pack is also published as a JSON Schema, [`pack.schema.json`](pack.schema.json) (draft 2020-12). It covers the fields and kinds below and checks structure only; `check-pack` remains the full check (cited IDs exist, language rules, handling, coverage).

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

- **`pack`:** the skill name, which is also the file name. It is lowercase words joined by hyphens, or `dossier-F<nn>` for `cluster-learning-dossier` (a lettered entity keeps its letter: `dossier-F09b`). The exceptions, where the pack name is not the skill name:
  - `organisation-learning-plan` (from `organisation-learning-map`);
  - `dossier-F<nn>`, one per cluster, and `dossier-index` (from `cluster-learning-dossier`);
  - `report-comparison-client-safe`, the neutral copy beside `report-comparison`, for the organisation that wrote
    the other report;
  - `report-comparison-regulator-safe`, the copy for a regulator or other authority ("additional learning"
    wording, the comparator's statutory status, `--embed summary`, legal review first).

  Both copies have exactly the sections of `report-comparison` (profile rule `same-sections-as:report-comparison`).
- **`skill` (optional):** the skill that wrote the pack, a folder in `skills/` with a `skill.json`. With it, `pack` must be that skill's `produces.pack`, or `<produces.pack>-<variant>` (lowercase words joined by hyphens, as `report-comparison-client-safe`), or for `cluster-learning-dossier` `dossier-F<nn>` or `dossier-index`; otherwise `check-pack` reports `pack <p> is not a pack or variant of skill <s>`. Give it on every pack whose name is not its skill's name.
- **`lang` and `dir` (optional):**
  - `lang` is a language tag such as `en` (the default), `hi` or `pt-BR`. The page's own words (headings, buttons, field labels, the citation pop-up) then come from `references/labels/<lang>.json`, and any word that file lacks stays in English. The pack's own text is never translated by the engine.
  - `dir` is `ltr` or `rtl`; by default it is the label file's `_dir`. A page in another language than English carries `lang` and `dir` on its `<html>` element.
  - The fixed copy (the status line, the DRAFT label, the coverage lines and the ProbeMatrix footer) always stays in English, word for word.
  - `hi.json` (Hindi) is AI-drafted: have a fluent speaker check it before use.
- **`translation_of` (optional):** the name of the English pack this one translates, written by `PMLC strings apply` together with `lang` and the name `<translation_of>-<lang>`. Never write it by hand. Its items may carry `source_text` (each field's English) and `back_translation`. `check-pack` warns `item <id> is safety-critical: add back_translation` (a problem under `--strict`), and when `<translation_of>.json` is beside it or in the run's outputs it requires the same cites, ids, kinds and section ids. Every page shows `Translated with AI assistance: have a fluent speaker check it before use` under the status line.
- **`lens` (optional):** who the assurance is for, in `auditor-assurance-pack` only: `regulator`, `insurer`, `jv-partner` or `client`; leave it out for internal audit. The page shows "Assurance for: <reader>" under the audience. With a lens the pack needs a `lens` section with one `para` on what that reader needs (`check-pack` warns, a problem under `--strict`); any other value is a problem. It is never offered for translation.
- **`status`:** must contain `Learning purposes: not a statutory document`.
- **`bottom_line`:** 1 to 7 takeaways, each citing at least one Finding or Evidence ID.
- **`scope` (optional):**
  - It says which findings the pack should cover, using the same filters as `PMLC select`. `tags` (e.g. `["emergency"]`) expand to every entity with that tag and are unioned with `entities`; prefer tags, so the pack survives a custom taxonomy. Tiers, entities and tags need `clusters.json`.
  - `min_rating` is a whole number or `"top"` (the workspace's top rating, which `run-path` prints). `relations` is a list of relation IDs (e.g. `["owner"]`). `entity_mode` is `"any"` (default) or `"all"`: with `all` a finding must carry every entity in `entities` and at least one entity of each tag, as with `select --entity-mode all`.
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
| `question` | question*, why*, answer (an answer key), good_evidence, to (role the question is put to), type (`single`, `multi`, `truefalse` or `short`), options (a list of `{"text", "correct"}` objects; with `short`, the accepted answers, all `correct`). `single` and `truefalse` need exactly one correct option, `multi` at least one, `truefalse` exactly two options. Without a `type` the question is a discussion question and `options` are ignored (a warning) | board questions, questions to raise, interview questions |
| `recommendation` | change*, indicator*, hoc_tier*, barrier, barrier_id, owner, by_when, why_not_stronger; **must cite** | what should change, with its leading indicator and hierarchy-of-controls tier |
| `decision` | decision*, options[], trade_offs, owner, by_when | decisions for leaders, pending engineering decisions |
| `indicator` | name*, measure*, deterioration, owner | leading indicators, readiness indicators |
| `card` | title*, what_happened*, why_made_sense, organisation_changing (what the organisation is changing; `check-pack` warns when a pack for tier T1 omits it), warning_signs[]*, good_looks_like*, did_you_know[] (shown as "Did you know?": a fact from the evidence that surprises), what_you_can_do[] (shown as "What can you do?": actions in the reader's own control), discussion[]; **must cite** | Learning Cards (`output-style.md`) |
| `scenario` | situation*, prompts[]*, injects[]: {offset* (`+HH:MM` after the exercise starts, e.g. `+00:15`), text*, decision (shown as a "Decision point")} | coaching conversations, drills, exercises; injects render as a timed, ordered list |
| `table` | columns[]*, rows[][]*, row_cites[][], row_supporting_cites[][] | anything tabular; each row has as many cells as there are columns |
| `test_point` | requirement*, sample*, conformity_evidence*, red_flags[], clause (free text naming the requirement source, e.g. "ISO 45001 8.1.3; OSHA 1910.119(l)", shown as a badge); **must cite** | audit test points |
| `module` | title*, objective*, audience, duration, content[]*, assessment[] | training modules |
| `barrier` | barrier*, failure_mode*, hoc_tier*, type, fix, owner, state (absent, degraded, defeated, worked partly, worked), indicator, barrier_id; **must cite** | barrier analysis |
| `timeline` | events[]*: {date* (YYYY-MM-DD, YYYY-MM or YYYY), time (HH:MM), text*, signal (true/false), knowable_then (true, false or text: what could be known at that moment), received_by, response, cites[]} | precursors, response timelines; events sort by date then time, and same-date events without a time keep your order |
| `graph` | nodes[]*: {id*, label*}; edges[]*: {from*, to*, label} | causal maps, interfaces; drawn as SVG with a text list of links. `PMLC causal-item <ws> --top 40` prints a ready graph item from `causal_graph.json` (run `PMLC causal` first) |
| `learning` | lesson* (one sentence), explanation (two to four sentences), owner (who must learn it); **must cite** | a learning: the lesson, why, and its evidence (dossiers, manager and leadership coaches, signal and interface learnings) |
| `toolbox` | opening_question*, story* (the story in 90 seconds), warning_signs[]* (two; `check-pack` warns `toolbox <id>: a toolbox talk has two warning signs` otherwise), one_change* (one thing to do differently tomorrow), crew_question* (one question to the crew), duration; **must cite** | a five-minute toolbox talk (`output-style.md`), shown as its five parts in order |
| `script` | title*, segments[]*: {visual*, narration*, seconds* (a whole number, 1 to 600), on_screen, cites[]}, purpose, channel (`video`, `radio`, `pa` or `screen`); **must cite** | a shooting script for a short video, radio or PA message: a two-column Visual and Narration table with each segment's time and the total duration. `pack --format srt,narration` writes `<pack>.<item-id>.srt` (subtitles: one cue per segment, timed cumulatively, 42 characters a line, 2 lines a cue) and `<pack>.<item-id>.narration.txt` (the narration only). Neither file carries the status line, because it would be shown on screen or spoken; inline citations are left out of both |
| `risk_change` | risk* (the risk, as the title), change_type* (`missing-threat`, `control-rating`, `accepted-without-authority`, `kri` or `other`), current_assumption*, evidence_says*, proposed_change*; **must cite** | a proposal for the risk owner to assess: what the register assumes today, what the evidence says and the change proposed. It carries no owner, date, rating or loss estimate; the risk owner decides. `pack --format risk-csv` writes `<pack>.risk-changes.csv` with the last column, `risk_owner_decision`, left blank |

Each kind also lists its fields in display order, each with a role (`title`, `body`, `list`, `badge`, `indicator`, `table`, `events`, `graph`, `choices`, `segments` or `injects`), in `KINDS[kind]["fields"]` of `pack/schema.py`; the labels are the `f.<field>` keys of `references/labels/en.json`. Formats without a layout of their own for a kind use them, and a kind the HTML and Markdown renderers do not know is shown as a labelled list of its fields, where its `body` and `list` fields carry citations.

## Optional on every pack and item

| Field | Where | What it does |
|---|---|---|
| `incident` | top level: `{"title": "…", "date": "YYYY-MM-DD"}` | Overrides the export's summary-sheet title and date in the page header and in the Markdown's `**Incident:**` line (use it when the profile flags them as wrong). |
| `data_quality` | top level: list of `{"text": "…", "cites": [...]}` | Data-quality corrections and limits (wrong dates, wrong incident type, draft status). Shown in a box under the status line. |
| `exclusions` | top level: list of `{"id": "FND-…", "reason": "…"}` | Findings left out on purpose (e.g. a reviewer downgrade vote). They leave the coverage total and are listed with their reason. A finding is either cited or excluded, never both. |
| `supporting_cites` | any item or bottom-line entry | Further Finding/Evidence IDs for the same condition. They count for coverage and are shown collapsed ("+N supporting"); keep `cites` to the key evidence. |
| `evidence_strength` | any item or bottom-line entry | `direct`, `corroborated` or `inferred` (`learning-principles.md`), shown as a badge. On a recommendation (or any item) it rates the evidence for the condition the item describes, not how well a proposed fix will work. |
| `group` | any item | A label such as a supervisor habit, a question mix or an interviewee role; a subheading is shown whenever it changes. |
| `learning` | any item or bottom-line entry | The Learnings Register entry the item carries, as `LR-` and two or more digits (`LR-01`). Shown as a chip that searches the pack for that id. `check-pack` checks it against the register given with `--register FILE`, or found at `<run>/outputs/learnings-register.json`: an unknown id is a warning (a problem with `strict`). With no register it warns once: `learning ids not verified: no register`. |
| `clauses` | any item or bottom-line entry | Requirement ids from `standards-crosswalk.json` (e.g. `["ISO45001-10.2", "PSM-(m)(4)"]`), shown as a badge. An id the crosswalk does not hold warns `unknown clause <id>` (a problem with `strict`). For free-text clause wording on a test point use `clause`. |
| `comparator_refs` | any item | Ids of the comparator report's items (`OBS-`, `RC-`, `REC-` or `ACT-` and two or more digits) that the item corresponds to, for `report-comparison`. |
| `gaps` | top level: list of `{"text": "…", "cites": [...], "evidence_needed": "…"}` | What the evidence could not show (the `[GAP]` convention, `learning-principles.md`). `text` and `evidence_needed` are required; `cites` is optional and every ID must exist. Shown in a box titled "Gaps in the evidence". `pack` also writes them to `<run>/outputs/gaps.json` (below). |
| `limits` | top level: list of text | What this pack's analysis could not see or does not cover. Listed under "Limits of this pack". |

**`why_not_stronger`.** A `recommendation` whose `hoc_tier` is `administrative` or `training` should say why no stronger control (elimination, substitution, engineering) is proposed; without it `check-pack` warns `recommendation <id> is administrative or training only: say why_not_stronger`. **`barrier_id`** (free text, on `barrier` and `recommendation`) names the organisation's own barrier or critical-control register entry.

**`gaps.json`.** `{"gaps": [{"pack": "…", "text": "…", "cites": [...], "evidence_needed": "…"}]}`, collected across packs for `investigator-coach`. Each `pack` run replaces that pack's entries and keeps every other pack's; a pack that no longer has `gaps` has its entries removed. It is always written to the run's outputs folder, whatever `--out` says.

A table's `row_cites` appear as an extra last column labelled **Cites**; `row_supporting_cites` (one list per row, may be empty) add a collapsed "+N supporting" to that cell and count for coverage. `check-pack` warns when a pack cites fewer than a quarter of the top-rated findings within its scope (the profile's `coverage_floor`); the page always shows both counts (relevant and top-rated relevant) and lists the rest. Each skill's pack also has a profile in `pack-profiles.json` (sections, kinds, counts, bottom-line count, required scope keys, word limits, rules); `check-pack` warns on a profile violation, on padding (3 or more items in one section with the same `cites`; items in one `group` count once) and on scope drift from the audience default, and `check-pack --strict` makes them problems.

Profile rules (`rules` in `pack-profiles.json`): `triplets`, `assessment-answer`, `follow-up-per-top` and `same-sections-as:<pack>` as above, plus three from v2.0 Phase 5. `no-owner-due`: an item with a non-empty `owner` or `by_when` is a problem even without `--strict` ("owner and due dates are set by the organisation, not in this pack"), because the organisation sets owners and dates. `banner:<key>`: the pack needs a `para` whose `text` is exactly the fixed banner `<key>` (`crosswalk`, `people`, `risk`, `evidence`, `profile-limits`, `nine-m-demo`); a near match does not count. `knowable-then`: every event of every `timeline` item carries `knowable_then`. A profile may also list `lint_errors`, such as `["JC5"]`: `check-pack` and `check-language` then report those language rules as errors for that pack; a `lint_ok` with its reason still clears a hit.

`hoc_tier` must name one of: elimination, substitution, engineering, administrative, training, ppe. Free wording such as "Engineering control: interlock" is fine.

## What check-pack does not check

An `OK` from `check-pack` means the pack is well formed and grounded in IDs that exist. It does not mean the content is right. It does not check that a cited finding or evidence item actually says what the sentence claims, that a quote is exact, that every name has been removed (the language lint catches common patterns and `--names` lists, not every name), that the wording is fair to the people involved beyond the JC rules, that a recommendation would work, or that a `barrier_id` or free-text `clause` exists in the organisation's registers. A person must still review the pack before `sign-off`.

## Handling and sign-off

Every pack and register may carry a top-level `handling` object. It is optional: without one the document is treated as `draft` / `internal` and `check-pack` (or `check-register`) passes with the warning `no handling block: rendered as draft (internal)`.

| Key | Values | Default |
|---|---|---|
| `status` | `draft`, `reviewed`, `approved` | `draft` |
| `reviewer_role` | the reviewer's role, never a name | none |
| `reviewed_on` | `YYYY-MM-DD` | none |
| `classification` | `internal`, `restricted`, `external`, `public` | `internal` |
| `legal_review` | `not-required`, `requested`, `cleared` | `not-required` |
| `distribution` | list of audience names | `[]` |
| `version` | text | `1.0` |
| `retention_review` | `YYYY-MM-DD` | none |
| `content_hash` | `sha256:` and 64 hex digits | none |

Unknown keys, bad values and `reviewed` or `approved` without `reviewer_role`, `reviewed_on` and `content_hash` are problems.

**Forced draft.** Nothing may be reviewed or approved unless the export's Investigation Status is `completed` (compared in lower case, with spaces and hyphens read as underscores): `in_progress` gives "the investigation status is in progress", and anything else, including `draft` or a blank, gives "the investigation status is not completed". Nor while no finding is marked as edited by a person ("no finding is marked as edited by a person"): only `yes`, `y`, `true` or `1` in User Edited counts. There is no override: finish the investigation in ProbeMatrix first.

**Sign-off.** After a person has reviewed the document and given their role, run `pmlc sign-off <ws> <file> --role "<role>" [--status reviewed|approved] [--classification ...] [--legal-review ...] [--distribution AUDIENCE ...] [--retention-review YYYY-MM-DD] [--version V] [--date YYYY-MM-DD]`. It refuses on forced-draft reasons and on any check problem, writes the `handling` block into the file with a `content_hash` of everything except `handling`, and records the whole block and the file's resolved path in the manifest (`status` lists it). The block is written by `sign-off` only: never write or edit it by hand. A `reviewed` or `approved` status holds only when this workspace's manifest records that sign-off for this file (same block, same path); a hand-written, hand-edited or copied block is `draft` ("not signed off", with the check warning `not signed off in this workspace: status is draft until sign-off records it`). Any later edit, even one character, changes the hash: the effective status falls back to `draft` and the check warns `edited since sign-off: status is draft until signed off again`. A bare-list register cannot be signed off; wrap it as `{"entries": [...]}`.

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

Its follow-up table contract (the `table` with `"id": "follow-up"`, `finding_notes` and `follow-up.json`) is in `skills/investigator-coach/references/follow-up.md`, linked from `skills/investigator-coach/SKILL.md`.
