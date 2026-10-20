# check-language

## What it does

Reads a learning pack or a Learnings Register and checks its **wording** against twelve rules (JC1 to JC12) for just culture and grounding. For each hit it prints the rule, where in the file it is, the words that triggered it and a hint for rewriting the sentence.

| Rule | Looks for | Severity |
|---|---|---|
| JC1 | A person's name: an honorific with a name (fictional examples: "Shri A. B. Example", "Ms Jane Placeholder"), a name from `--names`, or two capitalised words that are not role or place words | error |
| JC2 | Blame or sanction words ("careless", "disciplined") | error |
| JC3 | Counterfactual framing: "failed to", "should have", "would have", "could have prevented" | warning |
| JC4 | Hindsight: "obviously", "clearly should", "simply needed to" | warning |
| JC5 | Legal conclusions: "breach", "negligent", "liable", "failed to comply", "illegal" | warning |
| JC6 | A cause at level 3 or 4 whose every fix is training or an administrative control | warning (error for a pack only for frontline readers) |
| JC7 | A role that only one person holds, which points to that person | warning, error when shared outside |
| JC8 | A percentage or duration that the cited records do not give | warning |
| JC9 | An organisation's name: one from `--orgs`, or a company name ending in Ltd, Pvt, Inc, GmbH, LLC or Limited | warning, error when shared outside |
| JC10 | An equipment tag or similar identifier (letters then digits), checked only when shared outside | warning |
| JC11 | The phrase "Learning purposes: not a statutory document" is missing | error for a pack, warning for a register |
| JC12 | An appeal such as "be more careful" or "stay vigilant" | warning (error for a pack only for frontline readers) |

Errors make the command exit with code 1. [check-pack](check-pack.md) and [check-register](check-register.md) run the same checks as part of their own; check-language runs only these.

A hit can be accepted, when the wording is right, by adding to that item `"lint_ok": {"rule": "JCn", "reason": "..."}`. The reason must not be empty. `lint_ok` belongs on an item, a bottom-line entry or a register entry; on a section or at the top of the file it is an error, and it accepts nothing. [Language checks](../Language-checks.md) explains every rule with examples.

## When to use it

On any pack or register before it goes to a reviewer, and again before sharing it outside the organisation with `--share external` or `--share public`.

## Synopsis

```text
pmlc check-language ws json [--share {internal,external,public}] [--names NAMES] [--orgs ORGS]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder. Some rules (JC6, JC8) read the findings the file cites |
| `json` | A learning pack JSON or a Learnings Register JSON |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--share` | `internal`, `external` or `public` | the file's `handling.classification`, else `internal` | Who the file is for. `external` and `public` turn on the stricter outside rules (JC7, JC9 and JC10) |
| `--names` | file | `$PMLC_NAMES` | A text file of personal names, one per line, that must not appear. Lines starting with `#` and blank lines are skipped |
| `--orgs` | file | `$PMLC_ORGS` | A text file of organisation names, one per line, for JC9 |
| `--json` | none | off | Print one JSON object on stdout instead of the report: `{command, ok, exit_code, output, ...}`, where `output` holds the report's lines and this command adds `hits`. Messages go to stderr. The exit code is the same as without `--json` |
| `-h`, `--help` | none | | Show the flags and stop |

Keep the names and organisations files outside the repository: they hold the very names you are keeping out.

## Examples

The Hazira sample register, for readers inside the organisation:

```bash
python3 $E check-language $WS $OUT/learnings-register.json
```

```text
WARNING JC6 $.entries[7].recommendations: "administrative, training": the cited cause sits at level 3 or 4 and every control here is training or administrative: add a change at the cause's level (elimination, substitution or engineering), or, if the administrative change is itself the system fix, add lint_ok with the reason
WARNING JC6 $.entries[11].recommendations: "administrative, training": …
check-language: 0 errors, 2 warnings
```

The same register checked for sharing outside, where equipment tags and identifiers matter:

```bash
python3 $E check-language $WS $OUT/learnings-register.json --share external
```

```text
WARNING JC10 $.source: "INC-2026": describe the equipment generically, e.g. "the condensate meter", before sharing outside
…
check-language: 0 errors, 74 warnings
```

A test copy of the pack with one added paragraph that uses two fictional names and blame words. The sentence is invented for this example; it says nothing about anyone in the Hazira enquiry:

```bash
python3 $E check-language $WS lint-demo.json
```

```text
ERROR JC1 $.sections[0].items[1].text: "Shri A. B. Example": use the role, not the person, e.g. "the fitter" or "the shift supervisor"; if this is not a person, add lint_ok with the reason
ERROR JC1 $.sections[0].items[1].text: "Ms Jane Placeholder": use the role, not the person, e.g. "the fitter" or "the shift supervisor"; if this is not a person, add lint_ok with the reason
ERROR JC2 $.sections[0].items[1].text: "disciplined": describe what the organisation will change so the work is safer (a check, a design change, a resourced task), not a sanction
ERROR JC2 $.sections[0].items[1].text: "careless": describe what the organisation will change so the work is safer (a check, a design change, a resourced task), not a sanction
check-language: 4 errors, 0 warnings
```

With a names file of the same fictional names, the bare names are caught too:

```bash
printf '# fictional names for this example\nA. B. Example\nJane Placeholder\n' > names.txt
python3 $E check-language $WS lint-demo.json --names names.txt
```

```text
ERROR JC1 $.sections[0].items[1].text: "Shri A. B. Example": …
ERROR JC1 $.sections[0].items[1].text: "Ms Jane Placeholder": …
ERROR JC1 $.sections[0].items[1].text: "A. B. Example": use the role, not the person, …
ERROR JC1 $.sections[0].items[1].text: "Jane Placeholder": use the role, not the person, …
…
check-language: 6 errors, 0 warnings
```

Setting `PMLC_NAMES=names.txt` in the environment gives the same result without the flag.

## Common problems

- **"(json): invalid JSON at line … column …".** The file is not valid JSON. Fix it at the line and column given.
- **A false hit on a proper noun that is not a person** (a place, a piece of equipment). Rewrite if you can; otherwise add `lint_ok` to that item with the reason.
- **"name one rule, JC1 to JC12" or "give the reason the rule does not apply here".** A `lint_ok` entry names an unknown rule or has an empty reason. It then suppresses nothing.
- **"--names: file not found: …".** The names file path is wrong. If the message names `PMLC_NAMES` or `PMLC_ORGS` instead, the environment variable points to a missing file.
- **Many JC10 warnings with `--share external`.** Identifiers and tags are fine inside the organisation but can identify the site outside it. Describe the equipment generically in a copy meant for outside.

## Related

- [check-pack](check-pack.md) and [check-register](check-register.md) include these checks.
- [scan-names](scan-names.md) searches any file, including HTML and Excel, for names.
- [Language checks](../Language-checks.md) and [Review and sharing](../Review-and-sharing.md).
