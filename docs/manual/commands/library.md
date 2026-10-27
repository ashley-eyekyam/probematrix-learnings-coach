# library

## What it does

`library publish` adds a finished run's learnings to a library: a folder you choose that keeps learnings from many incidents, so later work can find repeats and trends. The library is opt-in. Run folders do not change.

The folder holds JSON Lines files, one JSON object a line. Lines are only ever added, never edited or deleted.

| File | What it holds |
|---|---|
| `library.json` | `{"kind": "pmlc-library", "version": 1}`. Written when the folder is new or empty |
| `learnings.jsonl` | One snapshot of a learning a line: its `LL-` ID, `snapshot_id` (`LL-000001#1`), `supersedes`, `incident_key`, `lr_id`, `content_hash`, `review_status` and the `learning` itself |
| `events.jsonl` | Things that happen to a learning: `withdrawn`, and `status` (a learning back in the register, or a new review status). Each of these names the event it follows in `data.after`, so every change is kept |
| `incidents.jsonl` | One line for each published state of an incident: `incident_key`, the site's code (`site_code`), the incident month, the taxonomy version and fingerprint, the export fingerprint, the engine version, the month it was published and its `LL-` IDs |
| `private/contexts.jsonl` | Each snapshot's original `context`. Nothing under `private/` is shared |
| `private/sites.json` | Each real site name and its code (`S01`, `S02` …). Never shared |

- **Stable IDs.** The incident's key is `INC-` and 10 hex characters, made from the export's Incident Number (or the run slug when that field is blank), so a re-export of the same incident gets the same key. Each learning gets an `LL-` ID once, for its incident and LR-ID, and keeps it when it is reworded.
- **References carry their incident.** Findings and evidence are written as `INC-…/FND-…` and `INC-…/EVD-…`, and recommendations as `LL-000001/R1`.
- **Publishing again.** An unchanged run adds nothing. A changed learning adds a new snapshot with the same `LL-` ID that supersedes the old one. A learning that has left the register gets a `withdrawn` event; if it comes back it gets a `status` event, `reinstated`, and keeps its ID. A change of review status alone gets a `status` event.
- **Absent fields are left out.** A register from v0.3, with no spine fields, publishes; the missing fields are omitted, never written as null.
- **All or nothing.** The command builds every line first and checks the files already there. If anything is wrong it writes nothing at all.
- **Taxonomy.** Each incident records the fingerprint of the taxonomy that classified it, from `clusters.json`.
- **De-identified before it is written.** Every line of `learnings.jsonl`, `events.jsonl` and `incidents.jsonl` passes a gate first:
  1. **Zero hits for listed names.** The names in `--names` or `PMLC_NAMES` are searched for in every line, as [scan-names](scan-names.md) does. One hit refuses the whole publish: change the register's wording to a role, then publish again. A listed name is never masked quietly.
  2. **Sites become codes.** The site (`--site`, else the export's Site or Location field) gets a code, `S01`, `S02` …, kept in `private/sites.json`. The same site keeps its code on every publish (case and spacing do not matter), and every site the library knows is replaced by its code wherever it appears in the text.
  3. **The text is masked as an external shared copy is** (`pack --share external`). Name variants and honorific forms become `[name]`; organisation names (`--orgs`, `PMLC_ORGS`, and any name ending in Ltd, Pvt, Inc, GmbH, LLC or Limited) become `[organisation]`; equipment tags become `[equipment tag]`; singleton roles become their function and tier; clock times are removed; and dates are rounded to the month ("24 March 2026 at 14:05" becomes "March 2026"). See [What the shared copy masks](../Review-and-sharing.md#what-the-shared-copy-masks).
  4. **A last scan.** The masked lines are searched again for the listed names, organisations and site names. Any hit refuses the publish.

  Each learning's `context` is kept twice: masked, as `public_context` in `learnings.jsonl`, and as written, in `private/contexts.jsonl`. IDs, references, hashes and the `YYYY-MM` months are never masked. The content hash is of the masked learning, so a new names or organisations file can add a superseding snapshot.

It never writes an owner, a due date or a sign-off. Publishing does not need an approved register: each snapshot records the register's review status.

## When to use it

When an investigation's register is finished and your organisation keeps a library of learnings across incidents. Use synthetic data to try it out.

## Synopsis

```text
pmlc library publish ws [--register REGISTER] [--library LIBRARY] [--site SITE] [--names NAMES] [--orgs ORGS] [--dry-run]
```

## Arguments

| Argument | What it is |
|---|---|
| `action` | `publish`, the only action |
| `ws` | The workspace folder of the run (it needs `clusters.json`: run `setup` first) |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--register` | file | `<run>/outputs/learnings-register.json` | The register to publish |
| `--library` | folder | `$PMLC_LIBRARY` | The library folder. A new or empty folder becomes a library on the first publish |
| `--site` | text | the export's Site or Location field | The site's real name. It is kept in `private/sites.json` and coded `S01`… in the library. With neither this flag nor a Site or Location field, no site is coded and `site_code` is null |
| `--names` | file | `$PMLC_NAMES` | Names, one a line, for the zero-hit name check before anything is written. A listed name in any public line refuses the publish |
| `--orgs` | file | `$PMLC_ORGS` | Organisation names, one a line, masked as `[organisation]` in the public lines |
| `--dry-run` | none | off | Print what would be added and write nothing |
| `-h`, `--help` | none | | Show the flags and stop |

Every flag belongs to the `publish` action.

## Examples

```bash
export PMLC_LIBRARY=~/learnings-library
python3 $E library publish $WS --dry-run
python3 $E library publish $WS
python3 $E library publish $WS --register $RUN/outputs/learnings-register.json --library ~/learnings-library
python3 $E library publish $WS --site "Kestrel Works" --names names.txt --orgs orgs.txt
```

The first publish of a synthetic run with three learnings prints:

```text
library publish: /home/user/learnings-library (new library)
incident INC-2649855c22: 3 new, 0 superseded, 0 unchanged, 0 withdrawn, 0 reinstated, 0 status changes
site coded S01 (the real name stays in private/sites.json, which is never shared)
  + LL-000001#1 LR-01 (new)
  + LL-000002#1 LR-02 (new)
  + LL-000003#1 LR-03 (new)
  + incident INC-2649855c22 (3 learnings)
appended: learnings.jsonl: 3, events.jsonl: 0, incidents.jsonl: 1, private/contexts.jsonl: 2
```

Publishing it again prints "nothing to append: the library already holds this run as it stands".

## Common problems

- **"no library folder: pass --library <dir> or set PMLC_LIBRARY"**. No folder was given. Exit code 2.
- **"… is not a library: it holds other files and no library.json; choose a new or empty folder"**. The folder holds other files. Choose a new or empty folder, or the library's own folder. Exit code 2.
- **"learnings.jsonl: the last line is cut short (it has no line end)"**, then **"library publish refused: the library at … is damaged, so nothing was written"**. A file was cut off, for example by a full disk or a copy that stopped. Restore it from a backup. Exit code 1.
- **"learnings.jsonl: LL-000001 is used for two learnings …"**. Someone edited the file by hand. Restore it from a backup. Exit code 1.
- **"learnings.jsonl: the learning INC-…/LR-01 has two LL- IDs …"**. Someone edited the file by hand. Restore it from a backup. Exit code 1.
- **Two publishes at once.** Nothing locks the library, and each file gets its own append. Publish one run at a time, and keep a backup of the folder.
- **"library publish refused: 1 listed name in the public lines (from --names or PMLC_NAMES), so nothing was written …"**. The register names a person from your names file. Name the role instead, then publish again. Exit code 1.
- **"library publish refused: … identifying detail … left in the public lines after masking"**. Masking missed a listed name, organisation or site, for example one written inside another word. Reword the register, then publish again. Exit code 1.
- **"private/sites.json: the code S01 is given to two sites"** (or "is not valid JSON", or "is not a site code"), then **"library publish refused: the library at … is damaged"**. Someone edited the site map by hand. Restore it from a backup. Exit code 1.
- **"library publish reads a learnings register, and … is not one"**. You passed a pack or another JSON file. Exit code 2.
- **"library publish: LR-01 appears twice in the register …"**. Give each learning its own LR-ID. Exit code 2.
- **"library publish: … has no clusters.json: run classify (or setup) first"**. Exit code 2.

## Related

- [scan-names](scan-names.md) is the same name check, for finished files.
- [Review and sharing](../Review-and-sharing.md#publishing-to-a-library) describes the masking the library shares with `pack --share external`.
- [templates](templates.md) writes the files your organisation fills in, such as `verification.jsonl` and `adoption.csv`.
- [consolidate](consolidate.md) writes the sites' could-it-happen-here returns, which a later alpha publishes as site-assessment events.
- [sign-off](sign-off.md) records a person's review of the register; the library records the review status it gives.
