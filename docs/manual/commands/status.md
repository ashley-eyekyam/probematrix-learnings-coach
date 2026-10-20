# status

## What it does

Shows whether the files in a workspace are still up to date. Each derived file (clusters, causal graph, timeline, interfaces and so on) records which source files it was built from. When a source changes, for example after a re-ingest of a newer export, status marks the files built from the old version as **stale**, with the reason.

It also lists every pack in the outputs folder with the result and time of its last [check-pack](check-pack.md), and whether the pack has changed since.

## When to use it

After a re-ingest, before re-using older outputs, and before sharing a pack: a pack that changed since its last check needs checking again.

## Synopsis

```text
pmlc status ws
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--json` | none | off | Print one JSON object on stdout instead of the report: `{command, ok, exit_code, output, ...}`, where `output` holds the report's lines and some commands add fields (`problems`, `warnings`, `stats`, `hits`). Messages go to stderr. The exit code is the same as without `--json` |
| `-h`, `--help` | none | | Show the flags and stop |

status has no other flags than `--json`.

## Examples

Straight after [classify](classify.md):

```bash
python3 $E status $WS
```

```text
| File | State | Reason |
|---|---|---|
| findings.json | current |  |
| evidence.json | current |  |
| incident.json | current |  |
| clusters.json | current |  |
| singleton_roles.json | current |  |

| Pack | Last check | Changed since |
|---|---|---|
```

Later in the run, after the analysis commands and a [check-pack](check-pack.md) of a board brief:

```bash
python3 $E status $WS
```

```text
| File | State | Reason |
|---|---|---|
| findings.json | current |  |
…
| causal_graph.json | current |  |
| causal_graph.mmd | current |  |
| timeline_candidates.json | current |  |
| timeline_event_day.json | current |  |
| interfaces.json | current |  |

| Pack | Last check | Changed since |
|---|---|---|
| board-brief | ok (2026-10-19T16:23:26) | no |
```

Re-ingesting the same export with `ingest --force` leaves everything current, because the content did not change. A newer export with different findings would mark the derived files stale.

## Common problems

- **"… is not a folder."** The path is wrong. [run-path](run-path.md) prints the workspace path of a run.
- **"unknown (built before manifest)".** The file was made by an engine version older than the manifest. Rebuild it with its command to get a state.
- **A file is "stale".** Run the command that builds it again: [classify](classify.md) for `clusters.json`, [causal](causal.md) for the causal graph, [timeline](timeline.md), [interfaces](interfaces.md). Then check your packs again.
- **A pack shows "Changed since: yes".** Someone edited it after its last check. Run [check-pack](check-pack.md) again.

## Related

- [ingest](ingest.md) (`ingest --force`) replaces the source files.
- [Files and folders](../Files-and-folders.md) lists every workspace file.
