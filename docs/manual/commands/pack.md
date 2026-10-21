# pack

## What it does

Turns a learning pack JSON into the files people read:

- `<pack>.html`: a self-contained page that works offline and prints well. Each cited ID opens the finding or evidence it refers to, the findings in scope that the pack does not cite are listed, and the footer carries the status phrase and the ProbeMatrix credit;
- `<pack>.md`: the same content as Markdown, for email, a wiki or a document.
- `follow-up.json` and `follow-up.csv`, for an internal `investigator-coach` pack only: the follow-up table by Finding ID. The CSV header is the export's own: `Finding ID,Evidence to Collect,Key Questions,Suggested Interviews,Causal Hypothesis`. A shared copy never writes either file, because interview plans stay inside the team;
- `gaps.json`, when the pack has `gaps`: the run's outputs folder collects every pack's evidence gaps there for the investigator. Each run replaces this pack's entries and keeps the other packs'. It is always written to the run's outputs folder, even with `--out`.

`--format` chooses which of these files to write (the default, `html,md`, writes exactly the two above). The formats are listed under [Formats](#formats).

Each page and Markdown file shows "About *n* min read" under the header (200 words a minute, at least 1), counted from the bottom line and the items.

It first runs the full [check-pack](check-pack.md). If the check finds a problem, nothing is written. A pack that has not been signed off renders with a **DRAFT** label.

Two flags decide what the page carries and who it is for:

- `--embed` sets how much of the investigation's records the page embeds. The default, `cited`, embeds the full records only for the findings and evidence the pack cites.
- `--share external` or `--share public` writes a separate, masked copy for people outside the organisation. It works only for an approved pack; see [Review and sharing](../Review-and-sharing.md#sharing-outside-the-organisation---share).

## When to use it

After [check-pack](check-pack.md) passes. Run it again after every edit of the JSON; the HTML is rebuilt each time.

## Synopsis

```text
pmlc pack ws pack [--out OUT] [--no-md] [--embed {cited,summary,full}]
          [--share {internal,external,public}] [--names NAMES] [--orgs ORGS]
          [--format FORMATS] [--view {full,learner}] [--start YYYY-MM-DD]
          [--brand FILE]
          [--layout {cards,toolbox,poster,checklist,paper,field}] [--paper {A4,A5}] [--base-url URL]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |
| `pack` | The learning pack JSON |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--out` | folder | the run's outputs folder | Where to write the HTML and Markdown |
| `--no-md` | none | off | Write only the HTML |
| `--embed` | `cited`, `summary` or `full` | `cited` (`summary` when sharing outside) | How much of the investigation's records the page embeds. `cited`: full records for the cited findings and evidence; the findings the pack does not cite travel as ID, label and rating only. `summary`: as `cited`, without evidence descriptions, specific references (quotes), suggested interviews, key questions or reviewers' vote reasons. `full`: every relevant record in full, as in v0.3 |
| `--share` | `internal`, `external` or `public` | `internal` | Who the copy is for. `external` (named people outside, such as a regulator) and `public` write a masked copy named `<pack>.external.html` or `<pack>.public.html` (and `.md`), and need an approved sign-off with that classification or wider, `legal_review` cleared and `--embed summary` |
| `--names` | file | `$PMLC_NAMES` | A names file, one name per line (blank lines and lines starting with `#` are skipped). A shared copy masks these names. In every mode the page is refused if one of them still appears in it |
| `--orgs` | file | `$PMLC_ORGS` | An organisation names file, one per line. A shared copy masks these names |
| `--format` | comma-separated format names | `html,md` | Which files to write; see [Formats](#formats). An unknown name stops the command (exit 2) and lists the formats. `--no-md` still removes `md`. A format with nothing to write in this pack says `<format>: nothing to write (<why>)` and writes nothing |
| `--view` | `full` or `learner` | `full` | `learner` writes a learner copy of each document format, named `<pack>.learner.<ext>`: answers, good-evidence notes and the correct-option flags are left out, and the line "Learner view: answers are hidden" sits under the status. Data formats ignore it |
| `--start` | date, `YYYY-MM-DD` | none | The day that the follow-up offsets of `--format ics` count from. Without it, `ics` says `ics: needs --start YYYY-MM-DD; nothing written (the coach never sets dates by itself)` and writes nothing |
| `--brand` | file | none | A `brand.json` that sets your organisation's look: `organisation` (a name), `accent` (a `#RRGGBB` colour) and `logo` (a PNG or JPEG next to the file, at most 200 KB). Any other key is refused, because the footer and the status line are fixed. The accent must reach a contrast of 4.5:1 against white (WCAG AA), or the command stops with the ratio it found. The page shows the logo (embedded in the file) and the name in its header |
| `--layout` | `cards`, `toolbox`, `poster`, `checklist`, `paper` or `field` | none | Also write a print layout, `<pack>.<layout>.html`, beside the other files; see [Print layouts](#print-layouts). It never changes `<pack>.html` |
| `--paper` | `A4` or `A5` | `A4` | The page size of `--layout cards`. The other layouts have a fixed size; with any other layout, or none, the command says `--paper applies to --layout cards only; ignored` |
| `--base-url` | an `http://` or `https://` URL | none | Where the pack page is published. The print layouts put a QR code on each printed item that links to `<URL>#i/<item id>`, and the poster one that links to the URL itself |
| `-h`, `--help` | none | | Show the flags and stop |

### Formats

| Format | Kind | File | What it is |
|---|---|---|---|
| `html` | document | `<pack>.html` | The offline page (default) |
| `md` | document | `<pack>.md` | The same content as Markdown (default) |
| `normalised` | data | `<pack>.normalised.json` | The pack for other tools: every item id filled in, the status line, the brand, the effective status, the word count and reading time, the coverage counts and the cited findings (label, level, rating) and evidence (type). A shared copy carries no run slug |
| `svg` | data | `<pack>.<item-id>.svg` | One stand-alone SVG for each graph item, with every label whole (the page clips them at 28 characters). The status phrase and the ProbeMatrix credit sit in its `<desc>` |
| `png` | data | `<pack>.<item-id>.png` | The same drawing as a picture, made by a Chromium-family browser: `$PMLC_BROWSER`, else `chromium`, `chromium-browser`, `google-chrome`, `google-chrome-stable`, `microsoft-edge` or `msedge` on the PATH. With none, the command says `png: no Chromium-family browser found; open the .svg in a browser and export it, or set PMLC_BROWSER`, writes no PNG and still exits 0. If the browser fails, it says `png: the browser did not produce an image (<reason>)` |
| `graphml` | data | `<pack>.<item-id>.graphml` | The graph for yEd and other graph tools: one node for each node (with a `label`), one edge for each link, and a `<desc>` with the status and credit. One file for each graph item |
| `bowtie-csv` | data | `<pack>.bowtie.csv` | One row for each barrier item, for a bow-tie tool or a spreadsheet. Columns: `side,barrier,barrier_id,state,type,hoc_tier,failure_mode,fix,owner_role,indicator,cites`. `side` is `threat` for a group that starts with "prevent", `consequence` for "mitigat" or "recover", and blank otherwise. `owner_role` is the pack's role text and `cites` are joined with `;`. It is an import file, so it carries no status line |
| `ics` | data | `<pack>.ics` | One all-day event for each check (`when`), decision (`by_when`) or recommendation (`by_when`) whose time is `<n> days`, `Day <n>` or `<n> weeks`, counted from `--start`. The summary is the item text cut to 70 characters; the description has the cites and the status phrase. No attendee and no organiser are written, and no date is ever invented. In a shared copy the event UID leaves out the run slug (`<pack>-<item-id>@pmlc` instead of `<run>-<pack>-<item-id>@pmlc`)
| `gift` | data | `<pack>.gift.txt` | The questions as GIFT (UTF-8), for a Moodle import. `//` comment lines carry the status, the DRAFT label, the handling line and the ProbeMatrix line. One question each: `single` as one `=` and the rest `~`, `multi` weighted so the correct options add up to 100, `truefalse` as `T` or `F`, `short` as the accepted answers, a question without a type as an essay. The `why` is the feedback. The characters `~ = # { } :` and the backslash are escaped. It keeps the answer key whatever `--view` says |
| `qti` | data | `<pack>.qti.zip` | The same questions as an IMS QTI 2.1 package: `imsmanifest.xml` and one `assessmentItem` file per question (`choiceInteraction`, `textEntryInteraction`, or an ungraded `extendedTextInteraction` for a question without a type). It keeps the answer key |
| `quiz-csv` | data | `<pack>.quiz.csv` | One row per question: `id,type,question,option_1,...,option_6,correct,why,cites`. `correct` holds the 1-based option numbers joined by `;`. A question without a type has the type `discussion` and no options. Cells that start with `=`, `+`, `-` or `@` get a leading `'` so a spreadsheet never runs them. Options beyond the sixth are left out, and the command says so |
| `email` | document | `<pack>.email.html` and `<pack>.email.txt` | An email-safe digest: the title, status, DRAFT label and reading time, the bottom line in full, each section's items in order, the cited finding and evidence IDs, the coverage line and the brand. The HTML uses inline styles only (no script, style sheet, link or image) and stays under 100 KB; when a long pack does not fit, each section ends with "N more items are in the full pack". The `.txt` twin has the same content, wrapped at 78 columns. When a base web address is given, it holds one link to that address and no other |
| `csv` | data | `<pack>.actions.csv` | Every recommendation, decision and indicator item, in the same columns and order as [export-actions](export-actions.md); owner, due, status, CAPA reference and effectiveness check are blank for your organisation. The file is never replaced: if `<pack>.actions.csv` exists, the command exits 1 with `<file> already exists and may hold your organisation's entries; move it or pass a new --out` and writes nothing |
| `docx` | document | `<pack>.docx` (`<pack>.paper.docx` with the `paper` layout) | A Word document on A4: the title with the status line under it, the DRAFT line, the handling lines and the reading time, then the bottom line, one heading per section, coverage, gaps and limits. Tables are real Word tables whose header row repeats on each page. Each item's citations are one endnote, listing every cited finding as `ID: label · L<level> · rating <r>` and every cited evidence item as `ID: type`. The footer of every page carries the status phrase, the ProbeMatrix credit and the page number; a draft has DRAFT in its header. The file has no author. With the `paper` layout a board paper is written as well: a cover page, "Decisions requested" (decision items, then the bottom line), numbered paragraphs (`1.`, `1.1`), Annex A for questions and Annex B for tables and indicators |
| `srt` | data | `<pack>.<item-id>.srt` | Subtitles from each `script` item: one cue per segment, timed cumulatively from 00:00:00,000, the narration wrapped at 42 characters and 2 lines a cue (a longer narration splits into cues that share the segment's time). No status line: it would show on screen. Prints "nothing to write" when the pack has no script item |
| `narration` | data | `<pack>.<item-id>.narration.txt` | Each `script` item's narration only, one paragraph per segment, for a voice-over or a PA reader. No status line and no citations: the text is spoken. The shooting script in the html and md carries the status |

A typed question has a `type` (`single`, `multi`, `truefalse` or `short`) and `options`, a list of `{"text": ..., "correct": true or false}`. `check-pack` stops a `single` or `truefalse` question without exactly one correct option, a `multi` with none, a `truefalse` without exactly two options, and a `short` whose accepted answers are not all marked correct. With the learner view the correct-option flags are left out, and a `short` question's options (its answers) are left out altogether. A pack with no questions has nothing to write for these three formats.

### Print layouts

`--layout` writes one more page, made to be printed from the browser (Ctrl+P). Every printed page carries the status phrase, the short footer ("ProbeMatrix Learnings Coach v… · ProbeMatrix by Eyekyam") and, until the pack is approved, the DRAFT label.

| Layout | Page | What it prints |
|---|---|---|
| `cards` | A4, or A5 with `--paper A5` | One page per card, toolbox talk, test point and scenario inject. A last page gives the bottom line and "<n> more items are in the full pack" for the rest |
| `field` | A4 | As `cards`, with the citations as numbered end-notes on a page of their own, then a printable delivery record |
| `toolbox` | A4 | One page per toolbox talk (its opening question, story, warning signs, one change and crew question, in that order), then the delivery record. A pack without toolbox talks writes nothing: `toolbox: nothing to write (no toolbox items)` |
| `checklist` | A4 | The checks and test points, grouped by section, each with a ☐ box; hold points are marked "Hold point", and each section ends with "Checked by (role): ________   Date: ________   Shift: ________". A pack without checks writes nothing |
| `poster` | A3 landscape | One page: the title, the bottom line, up to 6 card or learning titles, the pack's timeline events in one line, and the QR code when `--base-url` is given |
| `paper` | A4 | A board paper: a cover (title, incident, status, handling, reading time), "Decisions requested" with the bottom line, numbered paragraphs (`1.`, `1.1`) for the other items, Annex A for questions and Annex B for tables and indicators |

The delivery record has the columns of `distribution.csv` after `pack` and `audience` (`channel`, `date`, `delivered_by_role`, `attendees`, `contractors_included`, `questions_raised`, `concerns_escalated`) and blank rows to fill in by hand. Write roles, never personal names, then copy the rows into `distribution.csv` (see [templates](templates.md)).

With `--view learner` the layout is written as `<pack>.<layout>.learner.html`, and a shared copy as `<pack>.<layout>.external.html` or `.public.html`.

A shared copy (`--share external` or `public`) of any format is built from the masked pack, and the mode goes just before the last extension of its file name: `<pack>.normalised.external.json`, `<pack>.learner.external.html`. Every format's text goes through the name check.

## Examples

The Hazira board brief from the [check-pack](check-pack.md) example:

```bash
python3 $E pack $WS $OUT/board-brief.json
```

```text
warning: coverage: cites 3 of 308 relevant findings; under a quarter of the top-rated relevant findings are cited (3 of 101)
…
warning: no handling block: rendered as draft (internal)
HTML written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/board-brief.html
Markdown written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/board-brief.md
```

Only the HTML, into another folder:

```bash
python3 $E pack $WS $OUT/board-brief.json --no-md --out print
```

```text
warning: coverage: cites 3 of 308 relevant findings; under a quarter of the top-rated relevant findings are cited (3 of 101)
…
warning: no handling block: rendered as draft (internal)
HTML written to print/board-brief.html
```

The normalised pack only, for another tool, with the build date fixed (`SOURCE_DATE_EPOCH`, seconds since 1970) so the file is the same on every run:

```bash
SOURCE_DATE_EPOCH=1600905600 python3 $E pack $WS $OUT/board-brief.json --format normalised
```

```text
warning: coverage: cites 3 of 308 relevant findings; under a quarter of the top-rated relevant findings are cited (3 of 101)
…
warning: no handling block: rendered as draft (internal)
normalised written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/board-brief.normalised.json
```

The follow-up dates of the Hazira safety-committee guide, counted from the day the committee first meets. Five of the guide's checks say "30 days", "60 days" or "90 days", so the calendar gets five all-day events: two on 2 December 2026, two on 1 January 2027 and one on 31 January 2027. None has an attendee or an organiser:

```bash
python3 $E pack $WS $OUT/safety-committee-guide.json --format ics --start 2026-11-02
```

```text
…
ics written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/safety-committee-guide.ics
```

Without `--start` the command writes nothing and says `ics: needs --start YYYY-MM-DD; nothing written (the coach never sets dates by itself)`.

The HTML page and a Word copy of the board brief:

```bash
python3 $E pack $WS $OUT/board-brief.json --format html,docx
```

```text
…
HTML written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/board-brief.html
docx written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/board-brief.docx
```

A learner copy of a training pack, without the answer keys:

```bash
python3 $E pack $WS $OUT/training-designer.json --view learner
```

```text
…
HTML written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/training-designer.learner.html
Markdown written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/training-designer.learner.md
```

Field cards for a crew briefing, with a QR code on each card that opens it in the published pack:

```bash
python3 $E pack $WS $OUT/frontline-learning-cards.json --layout field --base-url https://intranet.example.org/learning/frontline-learning-cards.html
```

```text
…
HTML written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/frontline-learning-cards.html
Markdown written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/frontline-learning-cards.md
field layout written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/frontline-learning-cards.field.html
```

Open `frontline-learning-cards.field.html` and print it. The A5 cards for a pocket book: `--layout cards --paper A5`.

A smaller page for an internal working group, without quotes or evidence descriptions. On this pack the page drops from about 205 KB (`cited`) to about 168 KB; with `--embed full` it is about 1.2 MB:

```bash
python3 $E pack $WS $OUT/board-brief.json --embed summary --no-md --out e-summary
```

```text
warning: coverage: cites 3 of 308 relevant findings; under a quarter of the top-rated relevant findings are cited (3 of 101)
…
warning: no handling block: rendered as draft (internal)
HTML written to e-summary/board-brief.html
```

A copy for a regulator cannot be made from Hazira. The investigation is still in progress and no finding was edited by a person, so the pack stays a draft, and the command lists every condition it does not meet. Nothing is written:

```bash
python3 $E pack $WS $OUT/board-brief.json --share external
```

```text
warning: coverage: cites 3 of 308 relevant findings; under a quarter of the top-rated relevant findings are cited (3 of 101)
…
warning: no handling block: rendered as draft (internal)
cannot share externally: review is draft (the investigation status is in progress, no finding is marked as edited by a person); classification is "internal" (needs "external" or "public"); legal_review is not "cleared"
```

The same pack asked for a public copy with `--embed cited` also gets the embed condition:

```text
cannot share publicly: review is draft (the investigation status is in progress, no finding is marked as edited by a person); classification is "internal" (needs "public"); legal_review is not "cleared"; --embed cited is refused (use --embed summary)
```

A shared copy that works, on a synthetic, completed investigation where a person edited a finding (`SW` and `SO` are its workspace and outputs folders; `orgs.txt` lists the fictional organisation "Acme"). First a reviewer approves the brief for external readers, with legal review cleared:

```bash
python3 $E sign-off $SW $SO/board-brief.json --role "HSE manager" --status approved --classification external --legal-review cleared --date 2026-10-19
python3 $E pack $SW $SO/board-brief.json --share external --orgs $SO/orgs.txt
```

```text
Signed off synth/pmlc-runs/2024-03-20-plant-pump-fire/outputs/board-brief.json: approved by HSE manager on 2026-10-19
HTML written to synth/pmlc-runs/2024-03-20-plant-pump-fire/outputs/board-brief.external.html
Markdown written to synth/pmlc-runs/2024-03-20-plant-pump-fire/outputs/board-brief.external.md
Shared external: identifying details are masked
```

In that copy the export's "Pump P-101 restarted at 14:05 hrs on 2024-03-12 after the Acme Pumps Ltd seal change." reads "Pump [equipment tag] restarted on March 2024 after the [organisation] seal change.", the role "Security Guard - Gate 3" reads "Security & Surveillance (Unresolved)", and the handling line reads "Review: approved by HSE manager on October 2026 · Classification: external · Version 1.0". The shared copy has its own name, so it never overwrites the internal `board-brief.html`.

Before the sign-off, the same command lists all three unmet conditions:

```text
cannot share externally: review is draft; classification is "internal" (needs "external" or "public"); legal_review is not "cleared"
```

A pack with a problem is not rendered:

```bash
python3 $E pack $WS bad.json
```

```text
sections[1].items[0].cites[1]: FND-00000000 is not in this workspace
warning: no handling block: rendered as draft (internal)
1 problem(s) in bad.json. Nothing written.
```

## Common problems

- **"Nothing written."** The pack failed its check. Fix the problems listed above that line, then run pack again.
- **The page says DRAFT.** It will until a reviewer signs it off with [sign-off](sign-off.md), and always while the investigation is not completed or no finding has been edited by a person in ProbeMatrix.
- **Old HTML after an edit.** pack does not watch the file. Run it again after each change.
- **"cannot share externally: …" or "cannot share publicly: …".** Each condition after the colon is one that is not met. Sign the pack off with the right classification and legal review (`sign-off --classification external --legal-review cleared`), and leave `--embed` out (or give `summary`). Edit nothing after the sign-off: any change turns the pack back into a draft.
- **A shared copy is refused by the language check.** At the external level the check is stricter: an organisation's name or a singleton role in the pack's own text is an error. Masking covers the embedded export records, not your wording; rewrite the text with roles and functions.
- **"refused: a listed name appears in the output".** A name from `--names` (or `PMLC_NAMES`) is still on the page. Fix the pack text, or redact the name when you ingest (`ingest --redact`).
- **"argument --format: unknown format …".** The name is not a format; the message lists the ones there are. Separate several with commas and no spaces: `--format html,normalised`.
- **"already exists and may hold your organisation's entries".** `--format csv` never overwrites `<pack>.actions.csv`. Move the old file, or pass a new `--out`.
- **Word shows the citations as small numbers.** They are endnotes: the cited findings and evidence are listed at the end of the document, one note per item.
- **"toolbox: nothing to write (no toolbox items)" or "checklist: nothing to write (no check or test_point items)".** The pack has nothing that layout prints; the other files are still written. Pick another layout.
- **"QR codes left out: the link is too long for a QR code".** The `--base-url` is too long to encode; the pages print without the codes. Use a shorter address.
- **"argument --base-url: needs an http:// or https:// URL".** Give the full address of the published pack page.
- **Where did the files go?** Without `--out`, into the run's outputs folder; [run-path](run-path.md) prints it.

## Related

- [check-pack](check-pack.md) runs first.
- [causal-item](causal-item.md) makes a graph item for a pack.
- [dashboard](dashboard.md) is the whole-organisation view.
- [Skills](../Skills.md): every audience skill ends with check-pack and pack.
