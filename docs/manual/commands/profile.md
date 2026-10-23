# profile

## What it does

Writes a one-page Markdown summary of the investigation: the incident fields, how many findings sit at each HFACS level and rating, an **HFACS levels** table (level, name, definition, findings), the sub-categories, the most frequent factors, the roles named most often, the kinds of evidence, and a list of **data-quality flags** (including how many Incident Summary fields are blank): things to know before you write any learning (for example, that no finding has been reviewed by a person yet).

## When to use it

Right after [ingest](ingest.md), and before choosing which audiences to write for. Read the data-quality flags first: they decide whether outputs must stay drafts.

## Synopsis

```text
pmlc profile ws [--top TOP] [--out OUT]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--top` | number | 15 | How many rows to show in the "most frequent factors" and "most-named roles" tables |
| `--out` | file | print to the screen | Write the profile to this file instead. The usual place is `$WS/profile.md` |
| `--json` | none | off | Print one JSON object on stdout instead of the report: `{command, ok, exit_code, output}` plus, for this command, `incident`, `findings`, `evidence_items`, `distinct_factor_codes`, `distinct_roles`, `supervision_and_organisational`, `levels`, `ratings`, `sub_categories`, `top_factors`, `top_roles`, `evidence_types`, `empty_columns`, `blank_summary_fields`, `summary_fields`, `investigation_status`, `any_user_edited` and `flags` (the data-quality flags). On failure `ok` is false and `error` holds the reason. Messages go to stderr. The exit code is the same as without `--json` |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E profile $WS --out $WS/profile.md
```

```text
Profile written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/workspace/profile.md
```

The start of the file:

```text
# Investigation profile: Hazira 2020

| Field | Value |
|---|---|
| Incident Number | INC-2026-031 |
| Incident Title | Hazira 2020 |
| Incident Type | fire |
| Date | 2020-09-24 |
| Location | ONGC Hazira |
| Severity | major |
| Investigation Status | in_progress |

**Findings:** 436 across 94 distinct factor codes. **Evidence items:** 46. **Distinct role strings:** 630.
**Share at Supervision + Organisational levels:** 308 of 436 (71%).

## By level

| Level | Name | Findings |
|---|---|---:|
| 1 | Unsafe Acts | 36 |
| 2 | Preconditions | 92 |
| 3 | Supervision | 167 |
| 4 | Organisational Influences | 141 |
…
```

A shorter top list, printed to the screen:

```bash
python3 $E profile $WS --top 3
```

```text
…
## Most frequent factors (top 3)

| Factor | Instances |
|---|---:|
| SVI 1.4 Failed to Provide Appropriate Policy/ Guidance | 21 |
| OIC 2.7 Inconsistent Risk Management Practices | 19 |
| SVF 3.2 Operations Management | 18 |
…
## Data-quality flags

- Column 'Evidence to Collect' is empty on every finding (the investigator-coach skill can draft it).
…
- No finding is marked 'User Edited'. Confirm the human review status before publishing learnings.
- Investigation Status is 'in_progress'; label outputs as draft learnings.
- Regulator involvement is mentioned but "Reportable to Regulator" is "No": confirm reporting status
```

**Thin-export flags.**

The data-quality flags also warn when an export is too thin to support every audience. Each line is one of:

- `No Evidence Links sheet: learnings rest on findings only; use evidence_strength "inferred"`
- `No narrative text`
- `No dated text: timelines will show order only`
- `High F99 share: {x} of {n} findings unmapped (over 10%)`
- `High T9 share: {x} of {n} findings touch unresolved roles (over 25%)`
- `Run classify to check the F99 and T9 shares` (the two share checks and the tier checks need `clusters.json`)
- `Empty tiers: T2, T3` (tiers with no findings)
- `Thin tiers: T5 (1)` (tiers with 1 to 4 findings)

On the Hazira sample only `Thin tiers: T5 (1)` fires.

## Common problems

- **"No findings.json in …".** The path is not a workspace. Use the `workspace` path that [ingest](ingest.md) printed, or ask [run-path](run-path.md).
- **"Most-named roles" shows full role strings.** That table counts the raw text of the Individuals Involved column, before [classify](classify.md) groups the roles into clusters. It is expected.
- **The flags say the investigation is in progress.** Then every pack and register stays a draft, and [sign-off](sign-off.md) refuses. Finish the review in ProbeMatrix and export again.

## Related

- [classify](classify.md) groups the roles.
- [select](select.md) gathers findings once you know the shape of the investigation.
- [Glossary](../Glossary.md) explains HFACS levels and ratings.
