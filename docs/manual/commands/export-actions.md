# export-actions

## What it does

Collects every `recommendation`, `decision` and `indicator` item from the packs, plus each recommendation in the Learnings Register, and writes them as `actions.csv` and `actions.json`. The owner, due date, status, CAPA reference and effectiveness check columns are always written blank: your organisation assigns them in its own system.

## When to use it

When the packs and register are signed off and you want to load the proposed changes into an action-tracking or EHS system.

## Synopsis

```text
pmlc export-actions ws [--packs PACK ...] [--register FILE] [--profile {generic,enablon,intelex,cority,sap-ehs}] [--names FILE] [--out-dir DIR]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--packs` | pack names or JSON paths | every pack in `<run>/outputs` | Which packs to export |
| `--register` | file | `<run>/outputs/learnings-register.json` when present | The register whose recommendations are added |
| `--profile` | `generic`, `enablon`, `intelex`, `cority`, `sap-ehs` | `generic` | Renames the columns for a target system |
| `--names` | file | `$PMLC_NAMES` | If a listed name appears in the actions, the command exits 1 and writes nothing |
| `--out-dir` | folder | `<run>/outputs` | Where to write the two files |
| `-h`, `--help` | none | | Show the flags and stop |

### Columns

`id`, `lr_id`, `change`, `hoc_tier`, `barrier`, `indicator`, `owner`, `due`, `status`, `capa_ref`, `effectiveness_check`, `cites`, `evidence_strength`. The `id` is `<run>/<pack>/<item id>` for a pack item and `<run>/register/<LR id>/R<n>` for a register recommendation. In the CSV, lists such as `cites` are joined with `; `.

### Profiles

`generic` uses our own column names. The `enablon`, `intelex`, `cority` and `sap-ehs` profiles are editable column mappings in `references/actions-profiles.json`, marked `"verified": false`: the target names are placeholders, not checked against any product. The command says so on stderr; check the names against your system's import template and edit the file before importing.

## Examples

```bash
python3 $E export-actions $WS --profile generic --names names.txt
```

## Common problems

- **Exit 1 with a name scan hit.** A personal name is in a pack or register text. Remove it (roles only), then run again.
- **"already exists and may hold your organisation's entries".** The command never overwrites `actions.csv` or `actions.json`, because your organisation may have filled in the owner, due-date or status columns. Move the old files, or pass a new `--out-dir`. Exit code 1; nothing is written.

## Related

- [templates](templates.md) writes the adoption, distribution and verification files.
- [scan-names](scan-names.md) is the name scan this command uses.
