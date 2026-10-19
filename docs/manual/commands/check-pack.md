# check-pack

## What it does

Checks a **learning pack**: the JSON file an audience skill writes (a board brief, learning cards, a supervisor guide and so on) before it becomes HTML. It finds anything that would make the pack wrong or impossible to render:

- the required fields (`pack`, `schema`, `title`, `audience`, `status`, `bottom_line`, `sections`) and the shape of every section and item;
- every Finding ID and Evidence ID it cites exists in this workspace;
- every bottom-line entry cites at least one ID;
- a cited finding that a reviewer voted to downgrade has a data-quality note;
- the `scope` (levels, tiers, entities) is valid;
- the `handling` block, when present, is valid;
- the language rules JC1 to JC12, the same as [check-language](check-language.md).

It also gives **warnings**, which do not fail the check: low coverage of the relevant findings, an Evidence ID not linked to the findings its item cites, an ID written in the text but not in `cites`, a missing handling block, and language warnings.

The result is recorded in the workspace manifest, and [status](status.md) shows it.

## When to use it

Every time a pack JSON is written or edited, before [pack](pack.md). [pack](pack.md) runs the same check and writes nothing if it fails.

## Synopsis

```text
pmlc check-pack ws pack [--share {internal,external,public}] [--names NAMES] [--orgs ORGS]
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
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

A short board brief for Hazira, written by hand from four real findings. Its start:

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
warning: coverage: cites 3 of 308 relevant findings (under a quarter)
warning: no handling block: rendered as draft (internal)
OK: 2 sections, 2 items, 6 cited IDs
```

The pack passes. The warnings say it covers little of the investigation's levels 3 and 4 (its scope), and that it has not been signed off, so it renders as a draft.

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
- **"coverage: cites X of Y relevant findings (under a quarter)".** A warning only. Either cite more of the relevant findings, narrow the pack's `scope`, or list deliberate omissions under `exclusions` with a reason.
- **"no handling block: rendered as draft (internal)".** Expected until a reviewer runs [sign-off](sign-off.md).
- **Language errors (JC1, JC2, JC11 …).** See [check-language](check-language.md) for each rule and how to fix it.

## Related

- [pack](pack.md) renders a pack that passes.
- [check-register](check-register.md) is the same for a Learnings Register.
- [sign-off](sign-off.md) records a person's review.
- [Review and sharing](../Review-and-sharing.md) and [Skills](../Skills.md).
- The pack format: [pack-schema.md](https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/skills/learnings-coach/references/pack-schema.md).
