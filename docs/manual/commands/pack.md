# pack

## What it does

Turns a learning pack JSON into the files people read:

- `<pack>.html`: a self-contained page that works offline and prints well. Each cited ID opens the finding or evidence it refers to, the findings in scope that the pack does not cite are listed, and the footer carries the status phrase and the ProbeMatrix credit;
- `<pack>.md`: the same content as Markdown, for email, a wiki or a document.
- `follow-up.json` and `follow-up.csv`, for an internal `investigator-coach` pack only: the follow-up table by Finding ID. The CSV header is the export's own: `Finding ID,Evidence to Collect,Key Questions,Suggested Interviews,Causal Hypothesis`. A shared copy never writes either file, because interview plans stay inside the team;
- `gaps.json`, when the pack has `gaps`: the run's outputs folder collects every pack's evidence gaps there for the investigator. Each run replaces this pack's entries and keeps the other packs'. It is always written to the run's outputs folder, even with `--out`.

`--format` chooses which of these files to write (the default, `html,md`, writes exactly the two above). The formats are listed under [Formats](#formats).

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
          [--format FORMATS] [--view {full,learner}]
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
| `-h`, `--help` | none | | Show the flags and stop |

### Formats

| Format | Kind | File | What it is |
|---|---|---|---|
| `html` | document | `<pack>.html` | The offline page (default) |
| `md` | document | `<pack>.md` | The same content as Markdown (default) |
| `normalised` | data | `<pack>.normalised.json` | The pack for other tools: every item id filled in, the status line, the brand, the effective status, the word count and reading time, the coverage counts and the cited findings (label, level, rating) and evidence (type). A shared copy carries no run slug |
| `csv` | data | `<pack>.actions.csv` | Every recommendation, decision and indicator item, in the same columns and order as [export-actions](export-actions.md); owner, due, status, CAPA reference and effectiveness check are blank for your organisation. The file is never replaced: if `<pack>.actions.csv` exists, the command exits 1 with `<file> already exists and may hold your organisation's entries; move it or pass a new --out` and writes nothing |

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

A learner copy of a training pack, without the answer keys:

```bash
python3 $E pack $WS $OUT/training-designer.json --view learner
```

```text
…
HTML written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/training-designer.learner.html
Markdown written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/training-designer.learner.md
```

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
- **Where did the files go?** Without `--out`, into the run's outputs folder; [run-path](run-path.md) prints it.

## Related

- [check-pack](check-pack.md) runs first.
- [causal-item](causal-item.md) makes a graph item for a pack.
- [dashboard](dashboard.md) is the whole-organisation view.
- [Skills](../Skills.md): every audience skill ends with check-pack and pack.
