# evidence-audit

## What it does

Counts how well the evidence behind the findings holds up, and writes `evidence_audit.json` in the workspace. For every finding it gives the evidence strength (`corroborated`: at least two distinct evidence items of at least two types; `direct`: at least one item; `inferred`: none, the finding rests on its justification alone), the number of sources and the evidence types. It also lists the single-source findings, the document-only findings, the findings per level (single-source, document-only, with a witness statement), the evidence items that support ten or more findings (the concentration), the codes the causal explanations name that no finding carries, and notes for a thin export. The strength is counted by the engine; the model never judges it. It shows where more evidence would strengthen confidence, and says nothing about the investigation team.

## When to use it

Before writing a register: run this command, so `evidence_audit.json` exists. The engine pools the findings a learning cites and works out its `evidence_strength` by the same rule. `check-register` then reports a learning whose `evidence_strength` differs, and its message names the value to use; this command itself prints per-finding strengths only. Also when a pack needs a scorecard, a concentration table or a level table.

## Synopsis

```text
pmlc evidence-audit ws [--json] [--table-item scorecard|concentration|levels]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--json` | none | off | Print the audit as one JSON object (`command`, `ok`, `exit_code`, `audit`) |
| `--table-item` | `scorecard`, `concentration` or `levels` | none | Print a ready `table` item for a pack, with `row_cites`, instead of the summary |
| `-h`, `--help` | none | | Show the flags and stop |

The command always writes `evidence_audit.json`, with sorted keys, so a re-run gives identical bytes. After a re-ingest, `status` shows it as stale.

## Examples

```bash
python3 $E evidence-audit $WS
python3 $E evidence-audit $WS --table-item levels
```

On Hazira this gives 284 direct and 152 corroborated findings, none inferred; 205 single-source findings, 195 whose evidence is all documents, and 11 level-3 findings with a witness statement. EVD-8645 supports 67 findings, the largest concentration.

## Common problems

- **Every finding is `inferred`.** The export has no Evidence Links rows, or no finding names an evidence item. The `notes` entry says so; the command still exits 0.
- **A register learning is a problem: "evidence_strength is computed by the engine".** Run `evidence-audit` and copy the value it names, or remove the field.
- **The concentration table is empty.** No evidence item supports ten findings; small exports often have none.

## Related

- [table-item](table-item.md) prints other ready tables, including `evidence-types`.
- [check-register](check-register.md) enforces the strength.
- [facts](facts.md) prints the headline numbers.
