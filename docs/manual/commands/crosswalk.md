# crosswalk

## What it does

Reads the Learnings Register and, for one framework, lists every requirement with a status: `evidenced here` when a learning's `clauses` names the requirement, `partly` when only the requirement's `topics` pattern matches the text of a learning, and `needs organisation evidence` for anything else. The engine never sets `not applicable`: that is the organisation's call. Each row names the learnings that speak to it (`evidence_here`), the Finding IDs they cite (`cites`) and what the organisation must still show. A requirement is never marked as met by this command: a learning is evidence of what the investigation found, not a record that the organisation complies.

When `adoption.csv` or `distribution.csv` exists in the outputs folder with rows, ISO 45001 7.3 and 7.4 and PSM (m)(6) move up one step and the row names the file. The files are the organisation's own and are never written.

Requirements the task could not check against primary text carry "(unverified)" in the title and `verified: false`. `--system-csv FILE` (columns `id,title`, optional `topics`) replaces the framework with the organisation's own requirements.

## When to use it

Before writing a compliance crosswalk pack, or when someone asks which clauses of ISO 45001, PSM or the CCPS RBPS elements the learnings speak to.

## Synopsis

```text
pmlc crosswalk ws [--register REGISTER] [--framework {iso45001,psm,rmp,seveso,rbps,icmm,india}] [--system-csv FILE] [--json] [--table-item]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--register` | file | `<run>/outputs/learnings-register.json` | The register to map. A pack is refused |
| `--framework` | name | required unless `--system-csv` | `iso45001`, `psm`, `rmp`, `seveso`, `rbps`, `icmm` or `india` |
| `--system-csv` | file | none | The organisation's own requirements (`id,title[,topics]`) in place of a framework |
| `--json` | none | off | Print the crosswalk as JSON: `framework`, `title` and `rows` |
| `--table-item` | none | off | Print a pack table item with the columns Requirement, Status, Evidence here and Organisation must show, and `row_cites` |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E crosswalk $WS --framework rbps --table-item
```

On Hazira with the sample register, `--framework iso45001` lists 23 requirements, `--framework rbps` lists the 20 CCPS elements, and none is `evidenced here` yet because no learning carries `clauses`; the rest split between `partly` and `needs organisation evidence`.

## Common problems

- **"crosswalk needs a Learnings Register …".** The file is a pack or another file. Pass `learnings-register.json`.
- **"… needs the columns id,title".** The `--system-csv` header is wrong.
- **Every row says `needs organisation evidence`.** No learning text matches and no learning has `clauses`. That is an honest answer, not an error.

## Related

- [pack-xlsx](pack-xlsx.md) writes a table item to Excel, once it is in a pack.
- [table-item](table-item.md) prints the other ready tables.
- [register-items](register-items.md) prints register learnings as pack items.
