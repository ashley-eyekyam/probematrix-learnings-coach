# classify

## What it does

Reads the roles named in each finding's "Individuals Involved" column (for example "Maintenance fitters (meter 310FT01)") and maps each one to a **Learning Cluster**, which says three things about who the learning is for:

- the **entity**: which part of the organisation (F01 Operations & Control Room, F02 Mechanical Maintenance, … F17 Contractors, F99 Unmapped);
- the **tier**: how senior (T1 frontline, T2 first-line supervision, T3 function management, T4 plant leadership, T5 corporate and board, T9 unresolved);
- the **relation**: how the role relates to the finding (actor, approver, owner, absent, norm-setter, learner, challenger).

It writes `clusters.json` and `singleton_roles.json` to the workspace, and lists the roles it could not place in `unresolved_roles.json`. The words it matches come from the taxonomy in `skills/learnings-coach/references/taxonomy.json`; an **overlay** adds site-specific role words on top.

### Taxonomy version, fingerprint and statutory roles

`clusters.json` records `taxonomy_version` (taxonomy 2.0 and later), `taxonomy_fingerprint` (a sha256 of the merged taxonomy, the overlays and the org chart, so two runs can show they used the same rules) and `statutory_roles`: the roles that name a statutory post such as the Occupier or Factory Manager (India), the COMAH operator (UK), a PSM contract employee (US) or a DGMS mine manager (India), each as `{role, label, regime, findings}`. Each is a prompt to check the statutory duty, not a finding.

An org-chart row error names the row, counting the header as row 1, for example `org chart row 3: match is required`.

## When to use it

After [ingest](ingest.md), and before any [select](select.md) by entity, tag, tier or relation. Run it again after you resolve unresolved roles, or when you add an overlay.

## Synopsis

```text
pmlc classify ws [--taxonomy TAXONOMY] [--overlay NAME_OR_PATH] [--no-overlay]
                 [--overrides OVERRIDES] [--no-overrides]
                 [--org-chart FILE.csv] [--no-org-chart]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--taxonomy` | file | the built-in `taxonomy.json` | Use a different taxonomy file |
| `--overlay` | name or file | none | Extra site role words added to the taxonomy. Repeat it for several overlays. A bare name means `references/overlays/<name>.json`, for example `india-process-site` |
| `--no-overlay` | none | off | Use no overlay. Without `--taxonomy`, `--overlay` or `--no-overlay`, classify reuses the taxonomy and overlays the previous run used, and says so |
| `--overrides` | file | `$WS/role_overrides.json` when it exists | A JSON object `{role: {"F": [...], "T": ..., "R": ...}}` that fixes the cluster of named roles, usually written by the agent's resolution pass |
| `--no-overrides` | none | off | Ignore any overrides file |
| `--org-chart` | CSV file | none | Your own departments, as a CSV with the columns `department` (required), `entity` (an F-id to extend, optional), `match` (keywords separated by `;`, or a regex; required) and `tier` (`T1` to `T5`, optional). Rows without an `entity` become new entities `F20`, `F21` and so on, in CSV order, and keep their ID across re-runs through `org-chart-ids.json` in the workspace. Remembered like `--overlay`. Classify prints `<n> of <m> findings mapped to your departments` |
| `--no-org-chart` | none | off | Forget the remembered org chart |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

The first classify of the Hazira workspace:

```bash
python3 $E classify $WS
```

```text
Classified 630 distinct roles; 96 need resolution (no entity or no tier). Wrote hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/workspace/clusters.json

| Cluster | Name | Findings | L1/L2/L3/L4 |
|---|---|---:|---|
| F01 | Operations & Control Room | 170 | 13/46/49/62 |
| F02 | Mechanical Maintenance | 194 | 22/36/86/50 |
…
| F99 | Unmapped | 27 | 2/12/2/11 |

| Tier | Findings touching |
|---|---:|
| T1 Frontline / sharp end | 222 |
| T2 First-line supervision / shift in-charge | 237 |
| T3 Function / department management | 211 |
| T4 Plant / asset leadership | 54 |
| T5 Corporate / policy owner / board | 1 |
| T9 Unresolved | 98 |

Unresolved roles listed in hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/workspace/unresolved_roles.json. Resolve them into an overrides JSON ({role: {F: [...], T: ..., R: ...}}) in hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/workspace/role_overrides.json and re-run classify; that file is picked up automatically.
```

With the Indian process-site overlay, which knows site words such as CISF security posts, ERDMP / DMP emergency plans and GM / CGM ranks, fewer roles are left unresolved:

```bash
python3 $E classify $WS --overlay india-process-site
```

```text
warning: previous classify used taxonomy.json; this run uses taxonomy.json + india-process-site
Classified 630 distinct roles; 87 need resolution (no entity or no tier). Wrote hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/workspace/clusters.json
…
| F09b | Emergency Planning & Command | 43 | 5/11/14/13 |
…
| F99 | Unmapped | 14 | 2/6/2/4 |
…
```

Running classify again with no flags keeps that overlay:

```bash
python3 $E classify $WS
```

```text
Reusing taxonomy taxonomy.json and overlays india-process-site from the previous classify (pass --taxonomy/--overlay to change, --no-overlay for none).
Classified 630 distinct roles; 87 need resolution (no entity or no tier). …
```

Going back to the base taxonomy:

```bash
python3 $E classify $WS --no-overlay
```

```text
warning: previous classify used taxonomy.json + india-process-site; this run uses taxonomy.json
Classified 630 distinct roles; 96 need resolution (no entity or no tier). …
```

## Common problems

- **Many roles need resolution.** This is normal on a first run. The agent reads `unresolved_roles.json`, proposes a cluster for each role in `role_overrides.json`, and classify picks that file up next time. Check its choices: a role placed in the wrong tier sends a learning to the wrong people.
- **"--no-overlay and --overlay cannot be combined; pass one or the other."** They contradict each other; give one.
- **An override names an unknown entity, tier or relation.** Classify stops and lists the IDs it knows, for example `ov.json: the override for role 'Area Supervisor' has unknown F ID(s) F55; taxonomy taxonomy.json has F01, F02, … F17, F99.` Use IDs from the taxonomy (or F99 and T9).
- **The counts moved after a re-run.** Classify reuses the previous overlay unless told otherwise; the first line says so. Pass `--no-overlay` for the base taxonomy.

## Related

- [select](select.md) filters by the clusters this writes.
- [interfaces](interfaces.md) uses the entities to find shared findings.
- [Glossary](../Glossary.md) defines entity, tier and relation.
- [Skills](../Skills.md): the `learning-clusters` skill explains the clusters to readers.
