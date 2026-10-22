# check-samples

## What it does

Checks that the published sample folders follow the repository's contribution layout. Each folder under `samples/` must:

- be named `YYYY-MM-DD-<site>-<event>` in lowercase words joined by hyphens;
- hold a `README.md`;
- hold the export as `<folder name>_probematrix-findings.xlsx`;
- keep each pack JSON in its `outputs/` folder beside the pack's `.html` and `.md`, as `pack` writes them. The Learnings Register is exempt: its Markdown is `learnings-register.md` and its HTML page is the dashboard, `organisation-learning-map.html`.

It prints each problem and the total, and exits with code 1 if there is any problem.

## When to use it

Before you propose a new public sample, and in the repository's automatic checks. It is for contributors; you do not need it for your own runs.

## Synopsis

```text
pmlc check-samples [dir]
```

## Arguments

| Argument | What it is |
|---|---|
| `dir` | The folder of samples. Optional: by default, the `samples/` folder of the repository the engine is in |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--json` | none | off | Print one JSON object on stdout instead of the report: `{command, ok, exit_code, output}` plus, for this command, `problems`. On failure `ok` is false and `error` holds the reason. Messages go to stderr. The exit code is the same as without `--json` |
| `-h`, `--help` | none | | Show the flags and stop |

check-samples has no other flags.

## Examples

From the repository root:

```bash
python3 $E check-samples samples
```

```text
0 problem(s) in samples
```

## Common problems

- **"folder name must be YYYY-MM-DD-<site>-<event>".** Rename the folder. `tools/make-public-sample.py --slug` creates it with the right name.
- **"missing README.md".** Every sample needs a README with its public source, what the analysis had access to, and how it was prepared. Copy the Hazira sample's README as a model.
- **"missing <slug>_probematrix-findings.xlsx".** The export must sit in the folder under exactly that name.
- **"outputs/<pack>.json has no <pack>.html" (or `.md`).** Render the pack with [pack](pack.md) and copy its `.html` and `.md` into the sample's `outputs/` folder, or remove the JSON.
- **"No such folder: …".** The path is wrong.

## Related

- [Developer tools](../Developer-tools.md) describes `tools/make-public-sample.py`.
- The Hazira sample: [samples/2020-09-24-hazira-gas-release-fire](https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/samples/2020-09-24-hazira-gas-release-fire/README.md).
- [scan-names](scan-names.md) for organisations' own de-identification checks.
