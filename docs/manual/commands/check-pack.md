# check-pack

## What it does

Checks a **learning pack**: the JSON file an audience skill writes (a board brief, learning cards, a supervisor guide and so on) before it becomes HTML. It finds anything that would make the pack wrong or impossible to render:

- the required fields (`pack`, `schema`, `title`, `audience`, `status`, `bottom_line`, `sections`) and the shape of every section and item;
- every Finding ID and Evidence ID it cites exists in this workspace;
- every bottom-line entry cites at least one ID;
- a cited finding that a reviewer voted to downgrade has a data-quality note;
- the `scope` (levels, tiers, entities) is valid;
- the `handling` block, when present, is valid;
- the language rules JC1 to JC12, the same as [check-language](check-language.md);
- the optional v2.0 fields: a `learning` id has the shape `LR-01` and is in the Learnings Register; every id in `clauses` is in `standards-crosswalk.json`; `gaps` and `limits` are well formed;
- the optional `skill` names a skill in `skills/`, and the pack is that skill's pack or one of its variants (`pack <p> is not a pack or variant of skill <s>` otherwise).

Two profile settings make problems even without `--strict`. A profile with the rule `no-owner-due` refuses any item with a non-empty `owner` or `by_when`: `<id>: owner and due dates are set by the organisation, not in this pack`. A profile's `lint_errors` (for example `["JC5"]`) turns those language rules into errors for that pack, here and in [check-language](check-language.md); a `lint_ok` with its reason still clears a hit.

It also gives **warnings**, which do not fail the check: low coverage of the top-rated relevant findings, an Evidence ID not linked to the findings its item cites, an ID written in the text but not in `cites`, a missing handling block, `learning ids not verified: no register` when the pack uses `learning` and no register is found, an administrative or training recommendation without `why_not_stronger`, and language warnings. Seven more warnings become **problems under `--strict`**:

- **Pack profile.** Each skill's pack has a profile in `skills/learnings-coach/references/pack-profiles.json`, written from the skill's "Sections → kinds" text: its sections, the kinds that fill each one, how many items of each kind (for example up to 12 board questions), how many bottom-line entries, the `scope` keys it must set, word limits (a learning card has at most 250 words) and a few named rules (an engineering learning, barrier and recommendation share a `group`; a training assessment question has an `answer` and `cites`; the investigator follow-up table has a row for every top-rated finding). Every count a skill names is read as a maximum with a floor of one: "`question` ×8–12" means up to 12 and at least 1, and "`scenario` ×3" means up to 3 and at least 1, so a thin export never forces padding. The section ids come from the committed example packs; until each SKILL.md's Write table names them, a pack that uses other ids gets "not a section of the … profile" warnings.
- **Profile rules from Phase 5.** `banner:<key>`: the pack has no `para` whose text is exactly that fixed banner (for example `banner:crosswalk` needs "Aid to assurance, not a compliance opinion."). `knowable-then`: an event of a `timeline` item has no `knowable_then`.
- **Length.** A pack whose profile sets `max_words` and that has more words than that: `pack has <n> words; the <pack> profile allows <m>`. The count is the words a reader sees in the bottom line and the items (ids, citations and kind names are not words). The limits are 1500 for `board-brief`, 2000 for `top-management-brief` and 9000 for each `dossier-F*` pack. [pack](pack.md) shows the same count as "About *n* min read" (200 words a minute, at least 1) in the page header.
- **Padding.** Three or more items in one section with the same `cites` list may be one condition written several times. Items in different sections are not compared, and items that share one `group` count once, so an engineering learning, barrier and recommendation on the same finding, or a decision and its indicator, are not padding.
- **Scope drift.** An audience skill's pack whose `scope` leaves out its audience's default tiers, levels or tags (from `references/audiences.json`), for example a supervisor pack without `T2`. Only the dimensions the pack sets are compared, and a wider scope is fine; a pack that sets none of its audience's default dimensions (no tiers, levels or tags that the default uses) counts as drift, because it is no longer aimed at that audience.
- **Unknown learning id.** A `learning` id that the Learnings Register has no entry for.
- **Unknown clause.** An id in `clauses` that `standards-crosswalk.json` does not have.

**Coverage** is measured against the top-rated findings within the pack's scope (those with the highest rating any relevant finding has), so a short pack on a broad scope need not pad its citations. The rendered pack prints both numbers: "*x* of *y* relevant findings cited" and "*x* of *y* top-rated relevant findings cited".

An `OK` does not mean the content is right: see "What check-pack does not check" in pack-schema.md.

The result is recorded in the workspace manifest, and [status](status.md) shows it.

## When to use it

Every time a pack JSON is written or edited, before [pack](pack.md). [pack](pack.md) runs the same check and writes nothing if it fails.

## Synopsis

```text
pmlc check-pack ws pack [--share {internal,external,public}] [--names NAMES] [--orgs ORGS] [--strict] [--register REGISTER]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |
| `pack` | The learning pack JSON, usually `$OUT/<skill>.json` |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--share` | `internal`, `external` or `public` | the pack's `handling.classification`, else `internal` | Which language rules apply. `external` and `public` turn on the stricter outside rules |
| `--names` | file | `$PMLC_NAMES` | Personal names, one per line, that must not appear |
| `--orgs` | file | `$PMLC_ORGS` | Organisation names, one per line |
| `--strict` | none | off | Pack-profile violations, padding, scope drift, unknown learning ids and unknown clauses are problems (exit code 1), not warnings. Run it before handing a pack over |
| `--register` | file | `<run>/outputs/learnings-register.json` when it exists | The Learnings Register JSON that `learning` ids are checked against. A given file that cannot be read is a problem; an auto-detected one that cannot be read is warned about and ignored |
| `--json` | none | off | Print one JSON object on stdout instead of the report: `{command, ok, exit_code, output}` plus, for this command, `problems`, `warnings` and `stats`. On failure `ok` is false and `error` holds the reason. Messages go to stderr. The exit code is the same as without `--json` |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

A short board brief for Hazira, written by hand from three real findings. Its start:

```json
{"pack": "board-brief", "schema": 1, "title": "Board Brief: Hazira gas terminal release and fire, 2020",
 "audience": "Board and its safety committee", "status": "Learning purposes: not a statutory document",
 "bottom_line": [
  {"text": "Locally bought O-rings replaced the original meter gasket as a regular practice, with no specification or quality check.", "cites": ["FND-B86F67F0", "EVD-8645"]},
  …
```

```bash
python3 $E check-pack $WS $OUT/board-brief.json
```

```text
warning: coverage: cites 3 of 308 relevant findings; under a quarter of the top-rated relevant findings are cited (3 of 101)
warning: section what-happened: missing (para items, expected at least 1)
warning: section assurance: missing (table items, expected at least 1)
warning: section indicators: missing (indicator items, expected 1-5)
warning: scope.min_rating: required by the board-brief profile
warning: no handling block: rendered as draft (internal)
OK: 2 sections, 2 items, 5 cited IDs
```

The pack passes. The warnings say it covers little of the investigation's levels 3 and 4 (its scope): 101 of the 308 relevant findings have the top rating, and it cites 3 of them. It does not yet have the board-brief structure (the missing sections and `"min_rating": "top"` in its scope), and it has not been signed off, so it renders as a draft.

The same pack under `--strict`, as a skill runs it before hand-over:

```bash
python3 $E check-pack $WS $OUT/board-brief.json --strict
```

```text
section what-happened: missing (para items, expected at least 1)
section assurance: missing (table items, expected at least 1)
section indicators: missing (indicator items, expected 1-5)
scope.min_rating: required by the board-brief profile
warning: coverage: cites 3 of 308 relevant findings; under a quarter of the top-rated relevant findings are cited (3 of 101)
warning: no handling block: rendered as draft (internal)
4 problem(s) in hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/board-brief.json.
```

The profile lines are now problems, so the exit code is 1.

The same pack with an ID that does not exist:

```bash
python3 $E check-pack $WS bad.json
```

```text
sections[1].items[0].cites[1]: FND-00000000 is not in this workspace
warning: no handling block: rendered as draft (internal)
1 problem(s) in bad.json.
```

The exit code is 1, so a script or agent stops here.

## Common problems

- **"… is not in this workspace".** A typing error in an ID, or an ID from a different investigation. Copy IDs from [select](select.md) output.
- **"every bottom-line entry needs at least one Finding or Evidence ID".** Each headline must be grounded.
- **"cites …, which has a reviewer downgrade vote".** Add a `data_quality` note that cites it, or leave the finding out.
- **"… is shown as plain text, not a citation; put it in cites".** An ID in the text is not in the item's `cites` list, so the reader cannot follow it.
- **"coverage: … under a quarter of the top-rated relevant findings are cited".** A warning only. Cite more of the top-rated findings in scope, narrow the pack's `scope`, or list deliberate omissions under `exclusions` with a reason. The threshold is the profile's `coverage_floor` (0.25 unless a profile says otherwise).
- **"section …: N … items, expected …", "section …: missing", "scope.…: required by the … profile".** The pack does not have its skill's structure: a section is missing, holds a kind it should not, or has more items than the skill allows. Compare it with the skill's SKILL.md and `pack-profiles.json`; under `--strict` these are problems.
- **"N items share the same cites (…): possible padding".** Merge items that describe one condition, or give each item the findings that are its own. Only items in one section are compared, and items in one `group` count once.
- **"scope differs from the … audience default (…)".** Put the audience's default tiers, levels or tags back in `scope`; a wider scope is fine.
- **"no handling block: rendered as draft (internal)".** Expected until a reviewer runs [sign-off](sign-off.md).
- **"not signed off in this workspace: status is draft until sign-off records it".** The file claims `reviewed` or `approved`, but this workspace has no sign-off of it: the block was written or changed by hand, or the file was copied. Have it reviewed and run [sign-off](sign-off.md) here.
- **"unknown learning LR-nn".** The register has no entry with that `lr_id`: a typing error, or the register was rebuilt with new numbers. Fix the pack, or pass the right register with `--register`.
- **"learning ids not verified: no register".** The pack uses `learning` but no register was found. Write the register first, or pass `--register`.
- **"unknown clause …".** The id is not in `standards-crosswalk.json`. Use an id from it, or put free wording in a test point's `clause`.
- **"recommendation … is administrative or training only: say why_not_stronger".** Add `why_not_stronger`: why no elimination, substitution or engineering control is proposed.
- **Language errors (JC1, JC2, JC11 …).** See [check-language](check-language.md) for each rule and how to fix it.

## Related

- [pack](pack.md) renders a pack that passes.
- [check-register](check-register.md) is the same for a Learnings Register.
- [sign-off](sign-off.md) records a person's review.
- [Review and sharing](../Review-and-sharing.md) and [Skills](../Skills.md).
- The pack format: [pack-schema.md](https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/skills/learnings-coach/references/pack-schema.md).
