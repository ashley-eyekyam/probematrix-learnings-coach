# The learnings library

A **learnings library** is a folder your organisation keeps that holds the learnings of many investigations, so that later work can find repeats and trends across incidents. It is optional. `pmlc library publish` adds one finished run to it; nothing else in the coach needs a library, and the run folder is not changed.

This page explains what the library holds, the de-identification gate every line passes before it is written, and what is coming in v2.1. The full command, flag by flag, is on the [library](commands/library.md) page.

The example on this page is invented: a synthetic export of a pump seal change at a site called "Kestrel Works", built by the repository's tests, with a three-learning register. No real incident is ever published into a library in this repository's tests, samples or documents, and nothing in the repository's `samples/` folder is a library.

## What the library holds

A library is a folder of JSON Lines files: one JSON object a line. Lines are only ever added. Nothing is edited or deleted, so the library keeps every version of every learning.

```text
<library folder>/
  library.json             <- {"kind": "pmlc-library", "version": 1}
  learnings.jsonl          <- one snapshot of a learning a line
  events.jsonl             <- what happened to a learning later: withdrawn, a new status, a site's assessment, a verification reading
  incidents.jsonl          <- one line for each published state of an incident
  private/
    sites.json             <- each real site name and its code (S01, S02 ...). Never shared
    contexts.jsonl         <- each learning's context as written. Never shared
```

| File | What it holds |
|---|---|
| `library.json` | Marks the folder as a library. Written on the first publish into a new or empty folder |
| `learnings.jsonl` | One snapshot of a learning a line: its `LL-` ID, `snapshot_id` (`LL-000001#1`), `supersedes`, `incident_key`, `lr_id`, `content_hash`, `review_status` and the learning itself (title, lesson, masked context, HFACS level, organisational system, barrier, priority, transferability, evidence strength, urgency, references and recommendations) |
| `events.jsonl` | `withdrawn` and `status` events from the engine, and the organisation's own events: site assessments from [consolidate](commands/consolidate.md), verification readings from `verification.jsonl`, and adoption responses from `adoption.csv` |
| `incidents.jsonl` | The incident's key, its site code, the incident month (`YYYY-MM`), the taxonomy version and fingerprint, the export fingerprint, the engine version, the month it was published and its `LL-` IDs |
| `private/sites.json` | The real site names and their codes |
| `private/contexts.jsonl` | Each snapshot's `context` as the register wrote it |

**Stable IDs.**

- Each incident gets a key, `INC-` and 10 hex characters, made from the export's Incident Number (or the run slug when that field is blank). A re-export of the same incident gets the same key.
- Each learning gets an **`LL-` ID** once, for its incident and LR-ID, and keeps it for ever, even when it is reworded. `LR-01` is a learning's number in one register; `LL-000001` is its number in the library.
- Findings and evidence are written with their incident, as `INC-2649855c22/FND-0001`, and recommendations as `LL-000001/R1`, so references from different incidents never collide.

**Publishing again.**

- An unchanged run adds nothing.
- A changed learning adds a new snapshot with the same `LL-` ID that supersedes the old one (`LL-000002#2` supersedes `LL-000002#1`).
- A learning that has left the register gets a `withdrawn` event; if it comes back it gets a `status` event, `reinstated`, and keeps its ID.
- A change of review status alone gets a `status` event.
- Publishing does not need an approved register. Each snapshot records the register's review status, so later views can tell a draft from an approved learning.

**All or nothing.** The command builds every line first and checks the files already there. If anything is wrong (a damaged file, a listed name, a bad row in a file your organisation filled in), it writes nothing at all.

### The invented example

```bash
pmlc library publish <ws> --register register.json --library ~/learnings-library --site "Kestrel Works" --names names.txt --dry-run
pmlc library publish <ws> --register register.json --library ~/learnings-library --site "Kestrel Works" --names names.txt
```

The first publish of the invented run printed:

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

`--dry-run` prints the same with "would append" and writes nothing. Publishing the same register again printed `incident INC-2649855c22: 0 new, 0 superseded, 3 unchanged, …` and "nothing to append: the library already holds this run as it stands". After LR-02's lesson was reworded, the next publish printed:

```text
incident INC-2649855c22: 0 new, 1 superseded, 2 unchanged, 0 withdrawn, 0 reinstated, 0 status changes
  + LL-000002#2 LR-02 (supersedes LL-000002#1)
appended: learnings.jsonl: 1, events.jsonl: 0, incidents.jsonl: 0, private/contexts.jsonl: 1
```

The incident line it wrote holds no site name and no day:

```json
{"engine_version": "2.0.0a7", "incident_key": "INC-2649855c22", "learnings": ["LL-000001", "LL-000002", "LL-000003"], "month": "2024-03", "published": "2026-10", "site_code": "S01", "taxonomy_version": "2.0", …}
```

## The de-identification gate

A library is meant to be read across the organisation, so every line of `learnings.jsonl`, `events.jsonl` and `incidents.jsonl` passes a gate before anything is written. Only the two files under `private/` keep the original wording, and nothing under `private/` is shared.

1. **Zero hits for listed names.** The names in `--names` or `PMLC_NAMES` are searched for in every public line. One hit refuses the whole publish. A listed name is never masked quietly: change the register's wording to a role, then publish again. With neither `--names` nor `PMLC_NAMES` the check cannot run, and the command prints a note saying so.
2. **Sites become codes.** The site (`--site`, else the export's Site or Location field) gets a code, `S01`, `S02` …, kept in `private/sites.json`. The same site keeps its code on every publish, and every site the library knows is replaced by its code wherever it appears in the text.
3. **The text is masked as an external shared copy is** (`pack --share external`): name variants and honorifics, organisation names, equipment tags and singleton roles are masked, clock times are removed and dates are rounded to the month. See [What the shared copy masks](Review-and-sharing.md#what-the-shared-copy-masks).
4. **A last scan.** The masked lines are searched again for the listed names, organisations and site names. Any hit refuses the publish.

The name search in steps 1 and 4 is the one [scan-names](commands/scan-names.md) runs on finished files.

In the invented example, LR-01's context read "The pump at Kestrel Works went back to service on 14 March 2024 at 09:40 after a seal change, with no leak test on the work order." The library keeps it twice:

- in `learnings.jsonl`, as `public_context`: "The pump at S01 went back to service on March 2024 after a seal change, with no leak test on the work order.";
- in `private/contexts.jsonl`, as written.

When the register named a person from `names.txt` (an invented name, "Jane Placeholder"), the publish stopped and wrote nothing:

```text
library publish: library publish refused: 1 listed name (1 hit) in the public lines (from --names or PMLC_NAMES), so nothing was written. Name a role instead in the register, then publish again
```

Months, not days, are kept throughout: the incident month, the publish month and the month of each verification reading. IDs, references and hashes are never masked. The content hash is of the masked learning, so a new names or organisations file can add a superseding snapshot.

The gate never writes an owner, a due date or a sign-off, and it does not need an approved register. Sharing the library folder itself, or anything read from it, is still your organisation's decision.

## Coming in v2.1

v2.0 builds the library's storage and `publish` only. These come in v2.1, together with the skills that read across incidents:

- **The multi-incident skills:** `learning-verification`, `repeat-learnings`, `portfolio-trends`, `change-and-task-lessons` and `lfi-health-check`.
- **Reading the library:** `library export`, `library match` and `library search`, and the portfolio views.
- **A search index** (`sqlite3`) beside the JSON Lines files, rebuilt from them.
- **Small-cell suppression,** so a count small enough to point to one site or one person is not shown.
- **Refusing to mix taxonomies,** so learnings classified under different taxonomy versions are not counted together. The library already records each incident's taxonomy version and fingerprint for this.

Until then, keep a backup of the library folder, publish one run at a time (nothing locks the folder), and treat the files as append-only: an edit by hand makes the next publish refuse with "the library at … is damaged". See [Troubleshooting](Troubleshooting.md#library-publish-found-a-listed-name).
