# Troubleshooting

Each problem below starts with the message the engine prints, word for word, so you can search this page for the text you see. `<ws>`, `<n>` and similar words in angle brackets stand for the parts that change. Most messages also say what to do; this page explains why it happened.

Your agent usually reads these messages and fixes the cause itself. Look here when it asks you to decide, or when you want to understand what happened.

**Exit codes.** Every command ends with code 0 when it worked (warnings may still be printed), 1 when it found problems or a plan cannot be resolved, and 2 for a usage error, such as an unknown or shortened flag. `plan --next` also ends with 2 when the plan is complete. The `check-*` commands never use 2 for problems. The full table is under "Exit codes" in [Commands](Commands.md).

**Strict mode.** `check-pack --strict` and `check-register --strict` turn some warnings into problems. Plans use strict mode as the gate, so a pack or register that passes the default check can still stop a plan. The sections below on strict mode say which messages change.

## The engine says openpyxl is missing

```text
openpyxl is required: pip install openpyxl
```

**Why.** The engine reads the Excel export with the `openpyxl` package, and the Python the agent is using does not have it.

**What to do.** Ask the agent to install it. On macOS or Windows: `python3 -m pip install --user openpyxl`. On Debian or Ubuntu, where the system Python refuses `pip install`: `sudo apt install python3-openpyxl`. Or point the agent at a virtual environment that has it.

## A command cannot find the workspace

```text
No findings.json in <ws>. Run: pmlc.py ingest <export.xlsx> --slug <site>-<event>
```

**Why.** The folder given as `<ws>` is not a workspace: the export has not been ingested yet, or the path points to the run folder or the outputs folder instead of `workspace/`.

**What to do.** Run `ingest` first, or use the workspace path that `ingest` printed. `pmlc run-path <ws>` prints the right paths for an existing workspace.

## Ingest asks for a slug

```text
Give --slug <site>-<event>, e.g. --slug hazira-gas-release-fire (the date comes from --date or the summary sheet's Date).
```

**Why.** Every run folder is named by date, site and event, and the engine will not guess the site and event.

**What to do.** Give `--slug` with the site and event in plain words, for example `--slug hazira-gas-release-fire`. Do not copy the export's incident type unchecked.

## The slug is refused

```text
slug must be lowercase words joined by hyphens, e.g. hazira-gas-release-fire (got <your slug>)
```

For example, `--slug "Hazira Fire"` ends with `(got 'Hazira Fire')`.

**Why.** The slug becomes part of a folder name, so it may hold only lowercase letters, digits and single hyphens.

**What to do.** Write it as `hazira-fire`: lowercase, no spaces.

## Ingest finds no valid incident date

```text
No valid incident date from <source>: <value>. Pass --date YYYY-MM-DD.
```

**Why.** The summary sheet's Date field is empty or not a date, so the run folder cannot be named.

**What to do.** Pass `--date` with the correct date. Also use `--date` when the profile flags the summary-sheet date as wrong: on the Hazira sample the sheet once said 2020-08-24 for a fire on 2020-09-24.

## The workspace already exists

```text
<ws> already holds a workspace. Pass --force to overwrite it.
```

**Why.** The run folder for this date and slug already holds an analysis, and the engine will not overwrite it by accident.

**What to do.** If you are loading a new export of the same investigation, run it again as `ingest --force`. It replaces the findings, evidence and incident files and keeps `clusters.json` and `role_overrides.json`. Then run `classify` again and check `pmlc status <ws>`. If it is a different investigation, use a different slug.

## The file is a CAPA Planner export

```text
This is a CAPA Planner export, not a findings export. Export "Identified Findings" from the investigation instead.
```

**Why.** ProbeMatrix can export corrective and preventive actions (the CAPA Planner) as well as findings. The coach needs the findings.

**What to do.** In ProbeMatrix, export the investigation's Identified Findings and use that file.

## A required column is missing

```text
--strict: Identified Findings is missing required column(s): <columns>
```

For example, an export whose `Rating` header was renamed `Score` ends with `required column(s): Rating`.

**Why.** With `--strict`, ingest stops when one of `Finding ID`, `Level`, `Rating`, `Individuals Involved` or `Linked Evidence` is missing. Without `--strict` it carries on and reports the gap on its `schema:` line, for example `missing: Identified Findings: Rating; unknown: Identified Findings: Score`. A renamed column header is the usual cause.

**What to do.** Export again from ProbeMatrix without editing the headers, or restore the header's original name.

## The export's statistics disagree with its findings

```text
warning: Analysis Statistics says <n> findings, ingested <m>
```

**Why.** The export's Analysis Statistics sheet counts a different number of findings from the rows in Identified Findings. Rows may have been deleted or filtered in Excel, or the export is incomplete. On a clean export, ingest prints `cross-check: Analysis Statistics agrees (436)` instead.

**What to do.** Export again from ProbeMatrix and do not edit the workbook. If the difference is expected, say so in the outputs' data-quality notes.

## A tier or function filter needs the clusters

```text
Needs clusters.json. Run: pmlc.py classify <ws>
```

**Why.** Tiers, entities, tags and relations come from `classify`. This command needs them, and the workspace has not been classified yet.

**What to do.** Run `pmlc classify <ws>`, then the command again.

## Many roles are not placed

```text
Classified 630 distinct roles; 96 need resolution …
```

**Why.** The rules place most role strings by their words, but some are site titles, abbreviations or names of committees the rules do not know. Those findings have no function (F99) or no level (T9), so tier-based packs miss them.

**What to do.** Ask the agent for the resolution pass of [learning-clusters](skills/learning-clusters.md). It writes your decisions to `role_overrides.json`. For Indian process sites, also try `--overlay india-process-site`, which on Hazira places 9 more roles.

## An overlay is not found

```text
Overlay <name> not found at <path>. Pass a name from references/overlays/ or a path to a .json file.
```

**Why.** `--overlay` takes either the name of a file in the skill's `references/overlays/` folder (such as `india-process-site`) or the path to your own JSON file, and neither matched.

**What to do.** Check the spelling, or give the full path to your overlay file.

## Classify warns that the taxonomy changed

```text
warning: previous classify used <taxonomy and overlays before>; this run uses <taxonomy and overlays now>
```

For example, the first `--overlay india-process-site` on Hazira printed `warning: previous classify used taxonomy.json; this run uses taxonomy.json + india-process-site`.

**Why.** The function list or overlays differ from the previous run. Counts by function and tier will change, and packs built on the old counts may be out of date. The first time you add an overlay, this is expected.

**What to do.** Nothing, if the change is intended. Re-check the packs that depend on tiers, and see `pmlc status <ws>`.

## An override matches no role

```text
warning: <n> override(s) match no role: <role>
```

**Why.** A role string in `role_overrides.json` does not appear in the export exactly as written. Role strings are matched exactly, including capitals, spaces and brackets.

**What to do.** Copy the string exactly from `unresolved_roles.json` or from the profile. If the export changed and the role is gone, remove that entry.

## A workspace file is out of date

```text
warning: stale input <file> (<reason>); re-run pmlc <command> <ws>
```

For example: `warning: stale input clusters.json (overrides changed since this was built); re-run pmlc classify …`.

**Why.** A file the command reads was built before one of its own inputs changed: here, the role overrides were edited after the last `classify`. Files built from it, such as `interfaces.json`, are stale too.

**What to do.** Run the command the warning names, then the one you were running. `pmlc status <ws>` lists every stale file and the reason.

## A preset is combined with filters

```text
--preset cannot be combined with filters; edit the preset or drop --preset.
```

**Why.** A preset is a fixed set of filters recorded for a skill. Adding `--tier` or `--level` on top would make it something else.

**What to do.** Use the preset alone (with output options such as `--format`, `--brief` or `--budget-chars`), or drop it and give the filters yourself. Run `pmlc select <ws> --preset foo` to see the list of skills with presets.

## An unknown field name

```text
Unknown --fields value(s): <value>. Allowed: <field names>
```

**Why.** `select --fields` takes only the names in that list, separated by commas.

**What to do.** Use names from the list: label, short, justification, causal, roles, clusters, evidence, code, name, level, subcategory and rating. For example `--fields label,evidence,level`.

## The causal graph is missing

```text
Needs <file>. Run: pmlc.py causal <ws>
```

Here `<file>` is `causal_graph.json`.

**Why.** `causal-item` builds its graph from the file that `causal` writes.

**What to do.** Run `pmlc causal <ws>` first. If it then says `causal_graph.json has no links`, the findings' causal explanations name no other factors: tell the causal story in plain paragraphs instead.

## The timeline day is not understood

```text
--on takes a YYYY-MM-DD date or the word incident.
```

**Why.** `timeline --on` needs a full date, or `incident` for the workspace's incident date.

**What to do.** Use `--on incident` or a date such as `--on 2020-09-24`.

## A pack cites IDs that are not in the workspace

```text
bottom_line[0].cites[0]: FND-0003 is not in this workspace
```

**Why.** A Finding or Evidence ID in the pack does not exist in this export: it was mistyped, it comes from another investigation, or the export changed. The check then ends with `<n> problem(s) in <pack>. Nothing written.`

**What to do.** Correct or remove the ID. Never invent one: if no record supports a sentence, the sentence goes.

## The language check finds errors

```text
ERROR JC2 $.sections[0].items[0].text: "careless": describe what the organisation will change so the work is safer (a check, a design change, a resourced task), not a sanction
```

**Why.** The pack has wording that names a person, blames, or judges with hindsight. Errors stop `check-pack`, and `check-language` exits with 1.

**What to do.** Rewrite the sentence with the hint it prints. Each rule, with examples and rewrites, is on [Language checks](Language-checks.md).

## The check warns about coverage

```text
warning: coverage: cites 3 of 308 relevant findings; under a quarter of the top-rated relevant findings are cited (3 of 101)
```

**Why.** The pack cites less than a quarter of the top-rated findings within its scope (here 101 of the 308 relevant findings have the top rating). It may be fine for a short brief, but it can also mean whole conditions were missed.

**What to do.** Read the list of uncovered findings on the page. Cite the conditions that matter, add same-condition findings as `supporting_cites`, and list deliberate omissions as `exclusions` with a reason.

## The check warns that there is no handling block

```text
warning: no handling block: rendered as draft (internal)
```

**Why.** The file has not been signed off, so it has no review record. This is normal for every new pack.

**What to do.** Nothing until a person has reviewed it. See [Review and sharing](Review-and-sharing.md).

## Sign-off is refused on an unfinished investigation

```text
cannot sign off: the investigation status is in progress; no finding is marked as edited by a person
```

**Why.** The export says the investigation is still in progress, or no person has edited any finding in ProbeMatrix. Nothing from such an export may be reviewed or approved. The Hazira sample is in this state. Any status other than completed refuses too: a `draft` or blank status gives "the investigation status is not completed". Only `Yes` (or `y`, `true`, `1`) in User Edited counts as edited.

**What to do.** Finish the investigation in ProbeMatrix, export again, re-run the analysis, then sign off. There is no override.

## The check says the file is not signed off

```text
warning: not signed off in this workspace: status is draft until sign-off records it
```

**Why.** The file's handling block says `reviewed` or `approved`, but this workspace has no sign-off of it. The block was typed or changed by hand, or the file was copied from another folder or workspace. It counts as a draft, and the page says "Draft because: not signed off".

**What to do.** Have a person review the file, then run `sign-off` on it in this workspace. Never write the handling block by hand.

## Sign-off is refused because the role looks like a name

```text
--role: looks like a personal name ("Mr John Smith"); give a role
```

**Why.** The reviewer and the audiences are recorded as roles, never as people. The value has an honorific, two capitalised words that are not role words, or a name from the names file. The same message starts `--distribution:` for an audience.

**What to do.** Give the role, such as "HSE manager" or "Site HSE lead". If a real role is caught, word it with a role noun ("Plant Manager", "Head of Safety").

## Sign-off is refused for a register saved as a list

```text
wrap the entries as {"entries": [...]} before signing off
```

**Why.** The sign-off record is written into the file itself, so the register must be a JSON object, not a bare list.

**What to do.** Ask the agent to wrap the register as `{"title": "…", "entries": [ … ]}`, check it again, then sign off.

## A signed-off file was changed

```text
edited since sign-off: status is draft until signed off again
```

**Why.** The file's fingerprint no longer matches the one recorded at sign-off: someone changed it, even by one character. Its status is back to draft and the DRAFT ribbon returns.

**What to do.** Have the change reviewed and sign off again.

## The names file is not found

```text
--names: file not found: <path>
```

**Why.** The path given with `--names` points to no file. If the message starts `PMLC_NAMES:`, the path came from that environment variable. The same message appears for `--orgs` and `PMLC_ORGS`.

**What to do.** Check the path. The file is plain text, one name per line.

## The redaction map is not in the right shape

```text
--redact: expected a JSON object of "name": "role"
```

**Why.** `ingest --redact` needs a JSON object whose keys are names and whose values are the roles to use instead, such as `{"Jane Placeholder": "the shift supervisor"}` (a fictional name). A list, or a value that is not text, is refused.

**What to do.** Rewrite the file in that shape.

## A surname was replaced on its own

```text
warning: surname-only match "<word>" replaced <n> times: check the text reads correctly
```

**Why.** Redaction also replaces each name's surname on its own. A surname can also be an ordinary word, so a sentence may now read oddly.

**What to do.** Read the sentences that contain the replacement role. If one is wrong, adjust the map and ingest again with `--force`.

## The register's sub-category does not match the export

```text
warning: <LR-ID>: hfacs_level sub-category <value> matches no sub-category in the export
```

On the Hazira sample register, for example: `warning: LR-02: hfacs_level sub-category 'L4 Organisational Process: procedures (no return-to-service SOP)' matches no sub-category in the export`.

**Why.** A register's `hfacs_level` should start with the level and the export's own sub-category name, so summaries count cleanly. Extra detail in the same field breaks the match. In v2.0 this is a warning only.

**What to do.** Put the export's sub-category name in `hfacs_level`, and the detail in another field such as `context`.

## The name scan finds hits

```text
<n> hit(s).
```

Above the total, each hit has its own line starting `HIT`, with the file, the line number, the name found and the text around it. For example, scanning the Hazira findings for the word "Kribhico" (the name of a gas header, used here only to show the format) found 16 hits, each reported on a line like `HIT …/workspace/findings.json:772: 'Kribhico' … ' while carrying out change of Low-Pressure Gas to Kribhico from Medium Pressure Gas headers in LPG Plant…`, then `16 hit(s).`

**Why.** `scan-names` found a listed name in a file. It exits with 1 on hits, and with 2 if a file could not be read (it then prints `warning: <file> could not be read`).

**What to do.** Remove the name from the source (the pack JSON, or the export with `ingest --redact`), regenerate the outputs, and scan again until it prints `0 hit(s).`

## The names file for the scan is empty

```text
Names file is empty.
```

**Why.** `scan-names` needs at least one name to look for. Blank lines and lines starting with `#` do not count.

**What to do.** Add the names, one per line, and run the scan again.

## A check passes, but fails in strict mode

```text
section <id>: missing (<kinds> items, expected <n>-<m>)
```

**Why.** The pack departs from its pack profile in `references/pack-profiles.json`: a required section is missing (here, for example, the board brief's `ask` section with 1 to 3 paragraphs), a section has too many items or the wrong kind, or the scope drifted from the one the skill fixes. Without `--strict` the same line is printed as a warning and the check passes; with `--strict` it is a problem and the check exits 1.

**What to do.** Add or trim the section as the skill's Write table says, then run the check again with `--strict`. If the evidence is thin, write the section as the skill's "If the evidence is thin" part describes rather than dropping it.

## A priority-1 learning has no stronger fix

```text
priority-1 learning <LR-id> has no fix above the administrative tier
```

**Why.** Every recommendation on a priority-1 learning is administrative or training. `check-register` prints this as a warning ending "(give why_not_stronger, or add a stronger fix)"; `check-register --strict` counts it as a problem, so a plan's register step stops here.

**What to do.** Add a recommendation at the elimination, substitution or engineering tier if the evidence supports one. If the learning is about a decision or a competence that only an administrative change can address, add a `why_not_stronger` to the entry, grounded in its own cited findings. The Hazira sample register does this for LR-08 and LR-12.

## Learning IDs are not verified

```text
warning: learning ids not verified: no register
```

**Why.** The pack's items carry `learning: "LR-nn"`, but `check-pack` found no register to check them against: none was given with `--register`, and there is no `learnings-register.json` in the run's outputs folder. When a register is found, an ID it does not hold gives `unknown learning LR-nn`, a warning by default and a problem under `--strict`.

**What to do.** Write the register first, or pass `--register <file>`. Then correct any unknown ID to the register's own `lr_id`.

## The plan names an unknown skill

```text
unknown skill: <skill> (skills: <list>)
```

**Why.** `plan --skills` was given a name that is not a skill folder, often a typo. The plan cannot be resolved, so `plan` exits 1. The same exit code comes with "cycle: …" (two skills that each need the other first) and "nothing produces '<artefact>', which <skill> requires" (a requirement no engine command or skill writes). A preset step whose skill arrives in a later v2.0 phase is not an error: it is listed as "planned" and skipped.

**What to do.** Use a name from the list the message prints, or a workflow preset with `--workflow`. A cycle or a missing producer means a `skill.json` or `artefacts.json` was edited by hand: undo that edit.

## The plan says it is complete

```text
The plan is complete: every step is done or planned for a later phase.
```

**Why.** `plan --next` found no step left to do. It ends with exit code 2 on purpose, so a script or an agent looping over `--next` knows to stop. It is not an error.

**What to do.** Nothing more for this plan. Open `outputs/index.html` (run `index` if it is not there yet), and plan another workflow if you need one.

## A template file already exists

```text
<file> already exists and may hold your organisation's entries; move it or pass a new --out
```

**Why.** `templates` never overwrites `adoption.csv`, `distribution.csv` or `verification.jsonl`, because your organisation may have filled them in. It exits 1 and writes nothing.

**What to do.** If the file holds entries, keep it: the dashboard and later reviews read it back. To start a fresh copy, move the old file away first, or write the new one elsewhere with `--out`.

## No PNG because there is no browser

```text
png: no Chromium-family browser found; open the .svg in a browser and export it, or set PMLC_BROWSER
```

**Why.** `pack --format png` draws the graph with a Chromium-family browser on this computer (Chromium, Google Chrome or Microsoft Edge), and it found none. The engine has no picture library of its own. It wrote no PNG, the other formats were still written, and the command ended with code 0. If the browser was found but failed, even after one retry with its sandbox switched off, the message is `png: the browser did not produce an image (<reason>)` instead; the reason holds the browser's exit code and the last line it printed.

**What to do.** Use `--format svg`: the SVG is the same drawing, opens in any browser and goes into most slide programs as it is. To get a PNG, install Chromium or Chrome, or set `PMLC_BROWSER` to the browser's full path. If `PMLC_BROWSER` names something that cannot run, the engine says `warning: PMLC_BROWSER=<value> is not an executable; looking for a browser on PATH` and tries the usual names.

## The accessibility tests fail with "npm ci"

```text
run: npm ci --prefix tests/js
```

**Why.** This is for contributors running the repository's tests, not for users of the coach. The accessibility checks (`tests/test_a11y_js.py`) run axe-core in Node.js against the pack page, every print layout, the email, `index.html`, the dashboard and the SCORM page. Node.js is installed but the test packages (axe-core and jsdom, pinned in `tests/js/package.json`) are not. The tests fail on purpose rather than skip, so a CI run cannot pass without checking accessibility. Without Node.js at all, they skip.

**What to do.** From the repository folder run `npm ci --prefix tests/js` once, then run the tests again. `npm ci` installs exactly the versions in `tests/js/package-lock.json`.

## Word says the document needs repair

```text
<format> written to <path>
```

**Why.** The engine wrote the `.docx` or `.pptx`, but Word or PowerPoint reports "found unreadable content" or offers to repair it. The engine checks every package it writes (each part parses, every part has a content type, every link has a target, no two tables touch), so this usually means the file was changed after it was written: opened and saved by another program, cut short in an email or a download, or synced while it was still being written.

**What to do.** Write the file again with `pack --format docx` (or `pptx`) and open the new copy directly from the outputs folder. If the fresh file still asks for repair, open it in LibreOffice to read it, and report the pack and the message (no incident data needed: the synthetic test export reproduces most problems) to the maintainers. Do not accept the repair and send that copy on: the repaired file can lose the footer with the status line.

## The email digest leaves items out

```text
<n> more items are in the full pack
```

**Why.** `--format email` keeps `<pack>.email.html` under 100 KB so that it passes mail servers and pastes into a message without being cut. It adds each section's items in order until the next one would pass that size, then ends the section with this line. The bottom line, the cited IDs, the coverage line and the status are always kept. The full pack page is much larger (on Hazira the board brief page is about 470 KB), so attach or link that, not paste it.

**What to do.** Nothing, if the digest is a summary: send it with a link to the full page (`pack --base-url` adds the link). If a section must go in full, write a smaller pack for the email, or send the Word copy (`--format docx`) as an attachment.
