# select

## What it does

Picks the findings that matter for one audience or one question, and prints them as a compact **bundle** in Markdown (the default) or JSON. Each finding comes with its ID, code, level, rating, label, short description, roles, clusters and, unless you ask for less, its justification, causal text and evidence quotes. The bundle is what an audience skill reads before writing a pack.

Filters combine: a finding must pass every filter you give. Inside one filter, several values mean "any of these" (`--tier T2 T3` keeps findings that touch T2 or T3).

A line such as `select: 27 findings, 112 chars` is printed to the error stream (so it does not end up in a saved bundle) to tell you how big the bundle is.

## When to use it

Whenever you, or a skill, need "the findings for …": the supervisors, one department, the top-rated findings, everything about one factor code, or a count to see the shape of the data. Each skill's SKILL.md lists its gather calls; `--preset` runs them for you.

## Synopsis

```text
pmlc select ws [--entity [ENTITY ...]] [--tag TAG [TAG ...]] [--tier [TIER ...]]
               [--relation [RELATION ...]] [--level [LEVEL ...]] [--min-rating MIN_RATING] [--top-rated]
               [--entity-mode {any,all}] [--exclude-downgraded]
               [--subcategory SUBCATEGORY [SUBCATEGORY ...]] [--prefix PREFIX [PREFIX ...]]
               [--code [CODE ...]] [--text TEXT] [--in-evidence] [--max MAX]
               [--m {M1,M2,M3,M4,M5,M6,M7,M8,M9} [{M1,M2,M3,M4,M5,M6,M7,M8,M9} ...]] [--m-secondary]
               [--brief] [--budget-chars BUDGET_CHARS]
               [--fields FIELDS] [--group-by {level,subcategory,code,entity}]
               [--count-by {entity,tier,relation,level,subcategory,code}] [--format {md,json}]
               [--out OUT] [--preset SKILL[:NAME]]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

**Who the learning is for** (these need [classify](classify.md) first):

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--entity` | entity IDs, e.g. `F02 F09b` | all | Keep findings that touch these parts of the organisation |
| `--tag` | tags, e.g. `emergency` or `supply contractor` | all | Keep findings that touch any entity with this tag (operations, engineering, supply, emergency, assurance, people, leadership, corporate, external, contractor). Added to `--entity` |
| `--tier` | tier IDs, e.g. `T2 T3` | all | Keep findings that touch these tiers (T1 to T5, or T9 for unresolved roles) |
| `--relation` | relations | all | Keep findings where a role has this relation: `actor`, `approver`, `owner`, `absent`, `norm_setter`, `learner`, `challenger` |
| `--entity-mode` | `any` or `all` | `any` | `any`: a finding matches if it has any requested entity. `all`: it must have every `--entity` and, for each `--tag`, at least one of that tag's entities. Use `all` for the findings two departments share |

**What the finding is about:**

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--level` | `1` to `4` | all | HFACS levels: 1 Unsafe Acts, 2 Preconditions, 3 Supervision, 4 Organisational Influences |
| `--min-rating` | number | none | Keep findings rated at least this (higher means a stronger causal contribution) |
| `--top-rated` | none | off | Keep only findings at the workspace's top rating ([run-path](run-path.md) prints it; 4 for Hazira) |
| `--subcategory` | names | all | HFACS sub-category, matched exactly but ignoring case. Quote names with spaces |
| `--prefix` | prefixes, e.g. `SV OR` | all | The part of the factor code before the space |
| `--code` | codes, e.g. `"SVF 3.1"` | all | Exact factor codes |
| `--text` | pattern | none | A regular expression searched in the label, short description, justification and causal text, for example `"O-ring\|MOC"` |
| `--in-evidence` | none | off | Search `--text` also in the Specific Reference and description of the evidence linked to each finding. Needs `--text` |
| `--exclude-downgraded` | none | off | Drop findings a reviewer voted to downgrade, reject or remove, and print which were dropped |

**How much to print:**

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--max` | number | no limit | Keep at most this many findings, highest rated first |
| `--m` | one or more of `M1`, `M2`, `M3`, `M4`, `M5`, `M6`, `M7`, `M8` or `M9` | none | The 9M lens: keep findings whose primary M in `<ws>/nine_m_seed.json` is one of these. Run [nine-m-seed](nine-m-seed.md) first; without the seed the command stops with "run nine-m-seed first" (exit code 2) |
| `--m-secondary` | none | off | With `--m`: also keep findings that carry the M as a secondary M |
| `--brief` | none | off | Leave out the justification, causal text and evidence quotes |
| `--budget-chars` | number | no limit | Keep findings in rating order while the output stays within this many characters, and list what was dropped. The header and footer are always printed |
| `--fields` | comma list | all | Only these fields: `label`, `short`, `justification`, `causal`, `roles`, `clusters`, `evidence`, `code`, `name`, `level`, `subcategory`, `rating`. The ID is always kept |
| `--group-by` | `level`, `subcategory`, `code` or `entity` | none | Group the findings under one heading (Markdown) or key (JSON) per value |
| `--count-by` | `entity`, `tier`, `relation`, `level`, `subcategory` or `code` | none | Print only a count table (Markdown) or object (JSON), no findings |
| `--format` | `md` or `json` | `md` | Markdown for reading, JSON for tools |
| `--out` | file | print to the screen | Write the bundle to this file |

**Recorded gather calls:**

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--preset` | `SKILL` or `SKILL:NAME` | none | Run a skill's recorded gather calls (from `references/select-presets.json`). It takes only the output flags `--format`, `--fields`, `--group-by`, `--count-by`, `--brief`, `--budget-chars` and `--out`, never filters. Each call keeps its own format unless you pass `--format`, which then applies to all. With several calls you get one bundle per call under a `# Preset <skill>: <name>` heading, so JSON output is several JSON values one after another. `--budget-chars` caps the whole output: each call gets what the earlier calls left |
| `--json` | none | off | An alias for `--format json` |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

The findings Mechanical Maintenance (F02) and Materials Management (F06) share, counted by level:

```bash
python3 $E select $WS --entity F02 F06 --entity-mode all --count-by level
```

```text
select: 27 findings, 112 chars
# Findings by level (27 selected)

| level | findings |
|---|---:|
| L3 | 14 |
| L4 | 8 |
| L2 | 4 |
| L1 | 1 |
```

Two supervision-level findings that touch first-line supervisors, without the long text:

```bash
python3 $E select $WS --tier T2 --level 3 --brief --max 2
```

```text
select: 2 findings, 1273 chars
# Selected findings (2)

Filters: entity=None tag=None tier=['T2'] relation=None level=[3] min_rating=None top_rated=False entity_mode=any code=None prefix=None subcategory=None text=None

## FND-45363DCA · SVF 3.1 Personnel Management · L3 Failure to Correct Known Problem · rating 4
**Instance:** Maintenance fitters — routine O-ring substitution without authority or qualification

**Short:** Maintenance fitters repeatedly substituted locally purchased O-rings for the lost OEM rectangular-slot gasket spec; supervisors never identified or remediated the unsafe tendency across three replacements in 22 months.

**Roles:** Maintenance fitters (meter 310FT01); Maintenance supervisor (metering skid)  
**Clusters:** F=F02,F04 T=T1,T2 R=actor
…
```

Which parts of the organisation the top-rated findings touch, as JSON:

```bash
python3 $E select $WS --top-rated --count-by entity --format json
```

```text
select: 150 findings, 169 chars
{
 "F02": 91,
 "F01": 72,
 "F07": 30,
 "F06": 27,
…
```

One factor code, only the label and rating:

```bash
python3 $E select $WS --code "SVF 3.1" --fields label,rating --format json
```

```text
select: 4 findings, 580 chars
[
 {
  "id": "FND-45363DCA",
  "rating": 4,
  "label": "Maintenance fitters — routine O-ring substitution without authority or qualification"
 },
…
```

A text search, grouped by level:

```bash
python3 $E select $WS --text "O-ring" --group-by level --brief --max 3
```

```text
select: 3 findings, 1894 chars
# Selected findings (3)
…
## L4

### FND-B86F67F0 · OIC 2.1 Organizational Culture Allows for Unsafe Task/Mission · L4 Organisational Climate/ Culture Influences · rating 4
**Instance:** Regular use of locally procured O-rings for the 1986 rectangular-slot meter gasket
…
```

The emergency-response findings, kept within a character budget:

```bash
python3 $E select $WS --tag emergency --brief --budget-chars 1500
```

```text
Dropped for budget: 47 findings (lowest kept rating 4): FND-730D0DCA, FND-E009D26B, …
select: 1 finding, 1072 chars
# Selected findings (1)
…
## FND-DF1144C3 · OIC 2.1 Organizational Culture Allows for Unsafe Task/Mission · L4 Organisational Climate/ Culture Influences · rating 4
**Instance:** DMP/ERDMP omitted isolation/stoppage decision criteria and authority
…
```

Leaving out findings a reviewer voted to downgrade. The public Hazira export keeps no reviewer votes, so nothing is excluded here:

```bash
python3 $E select $WS --exclude-downgraded --top-rated --count-by level
```

```text
select: 150 findings, 152 chars
# Findings by level (150 selected)
…
Excluded (reviewer downgrade): none
```

The supervisor-coach skill's gather calls, as counts:

```bash
python3 $E select $WS --preset supervisor-coach --count-by level
```

```text
select: 237 findings, 117 chars
select: 54 findings, 79 chars
select: 28 findings, 112 chars
# Preset supervisor-coach: tier-t2

# Findings by level (237 selected)
…
# Preset supervisor-coach: top-l3

# Findings by level (54 selected)

| level | findings |
|---|---:|
| L3 | 54 |

# Preset supervisor-coach: tier-t2-relation
…
```

## Common problems

- **"Filtering or grouping by entity/tag/tier/relation needs clusters.json. Run: pmlc.py classify <ws>".** Run [classify](classify.md) first.
- **A preset with a filter.** `--preset supervisor-coach --tier T1` (or `--tier=T1`) stops with exit code 2: `--preset cannot be combined with filters; edit the preset or drop --preset.`
- **A shortened flag** is refused with `unrecognized arguments: …` and exit code 2. Write every flag in full; see [Typing flags](../Commands.md#typing-flags).
- **An unknown field.** `--fields label,colour` gives `Unknown --fields value(s): colour. Allowed: label, short, justification, causal, roles, clusters, evidence, code, name, level, subcategory, rating`.
- **"budget N is below the minimum output".** The budget is smaller than the header and footer alone, so no findings fit. Raise `--budget-chars`.
- **No findings at all.** The filters are too narrow together. Try `--count-by` with fewer filters to see where the findings are.
- **`--text` finds too much or too little.** It is a regular expression, matched without regard to case. Use `|` for "or" and quote the pattern.

## Related

- [classify](classify.md) makes the clusters the first group of filters needs.
- [check-pack](check-pack.md) checks that a pack cites the findings it should.
- [Skills](../Skills.md): each audience skill lists its select calls.
- [Workflows and recipes](../Workflows-and-recipes.md) shows select inside complete jobs.
