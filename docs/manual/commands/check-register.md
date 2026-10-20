# check-register

## What it does

Checks a **Learnings Register**: the JSON file the learnings-register skill writes, with one entry per learning (its lesson, the findings and evidence behind it, its HFACS level, owner entity, audiences, priority and recommendations rated on the hierarchy of controls). It reports:

- **problems**, which fail the check: an entry with no `finding_ids` or `evidence_ids`; an ID that is not in the workspace; an Evidence ID not linked to any of the entry's findings; a cited finding with a reviewer downgrade vote; an `hfacs_level` that does not start with L1 to L4; a `priority` other than 1, 2 or 3; no `tier_messages`; no recommendations; a recommendation with no `hoc_tier` or no `leading_indicator`; a bad `urgency`, `recommendation_class` or `nine_m` value, or a `verification` that is not an object; language errors; and, under `--strict`, a priority-1 learning with no fix above the administrative tier;
- **coverage**: how many of the investigation's findings the register cites, and which are left out, highest rated first;
- **warnings**: a priority-1 learning with no fix above the administrative tier (silenced by a `why_not_stronger` on the entry); a `hoc_tier` text that is ambiguous; a recommendation `owner` that is not a role or looks like a personal name; a `due` date (owners and due dates are set by the organisation); an `owner_entity` that is not among the entry's main entities; an HFACS sub-category that matches nothing in the export, a missing handling block, and language warnings (rules JC1 to JC12, as in [check-language](check-language.md)).

## When to use it

Every time a register JSON is written or edited, before [register-xlsx](register-xlsx.md) or [dashboard](dashboard.md) with `dashboard --register`.

## Synopsis

```text
pmlc check-register ws register [--strict] [--json] [--share {internal,external,public}] [--names NAMES] [--orgs ORGS]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |
| `register` | The Learnings Register JSON |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--strict` | none | off | Makes the priority-1 rule a problem instead of a warning |
| `--json` | none | off | Prints `{"ok", "problems", "warnings", "stats"}` as JSON instead of the text report |
| `--share` | `internal`, `external` or `public` | the register's `handling.classification`, else `internal` | Which language rules apply |
| `--names` | file | `$PMLC_NAMES` | Personal names, one per line, that must not appear |
| `--orgs` | file | `$PMLC_ORGS` | Organisation names, one per line |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

The Hazira sample register (copied from the sample's `outputs/` folder into the run's outputs folder):

```bash
python3 $E check-register $WS $OUT/learnings-register.json
```

```text
25 learnings; 435 of 436 findings covered (100%); 0 problem(s).
Uncovered findings (1), highest rated first:
   FND-44219027 PPE 1.2 r3 Night-time darkness combined with dense white vapour cloud restricted visual assessment an
warning: LR-02: hfacs_level sub-category 'L4 Organisational Process: procedures (no return-to-service SOP)' matches no sub-category in the export
warning: LR-05: hfacs_level sub-category 'L4 Organisational Climate/Culture (inconsistent risk management of known problems)' matches no sub-category in the export
…
warning: no handling block: rendered as draft (internal)
warning: entries[7].recommendations: JC6 "administrative, training": the cited cause sits at level 3 or 4 and every control here is training or administrative: add a change at the cause's level (elimination, substitution or engineering), or, if the administrative change is itself the system fix, add lint_ok with the reason
warning: entries[11].recommendations: JC6 …
```

Read it as: the register is valid (0 problems) and cites all but one finding. FND-44219027 is left out on purpose; the sample README explains why. The sub-category warnings mean the register describes the level in its own words rather than with the export's exact sub-category name.

## Common problems

- **"… is not in this workspace".** An ID was mistyped, or the register belongs to another export. Check the workspace path.
- **Sub-category warnings.** The `hfacs_level` text does not match an export sub-category exactly. A warning only; use the export's wording if you want the dashboard to group by it.
- **A bare list of entries.** A register may be a list, but [sign-off](sign-off.md) needs it wrapped as `{"entries": [...]}`.
- **JC6 warnings.** Every recommendation for a level 3 or 4 cause is training or administrative. Add a change at the cause's level, or add `lint_ok` with the reason the administrative change is itself the system fix.

## Related

- [register-md](register-md.md) writes the checked register to Markdown.
- [register-xlsx](register-xlsx.md) writes the checked register to Excel.
- [dashboard](dashboard.md) adds it to the learning map.
- [check-language](check-language.md) explains the language rules.
- The register format: [register-schema.md](https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/skills/learnings-coach/references/register-schema.md).
