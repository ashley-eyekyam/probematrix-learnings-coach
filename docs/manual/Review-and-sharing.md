# Review and sharing

Everything the coach writes is a **draft** until a competent person has reviewed it. This page explains how the coach marks that, how a person signs a file off, why some investigations cannot be signed off yet, and how to make a safe copy for people outside the organisation.

In short:

1. Every pack, register and dashboard starts as a draft, with a DRAFT ribbon.
2. A person reviews it, and tells the agent their role. The agent then records a **sign-off**.
3. Any later change to the file turns it back into a draft.
4. Sharing outside the organisation needs an approval, a matching classification, a cleared legal review and a masked copy.

## Why review matters

The findings in a ProbeMatrix export are AI-assisted, and the learnings the coach writes are drafted by an AI agent. Both are evidence-linked, but neither is a decision by the organisation. The outputs say so in fixed wording:

- Every page carries the status phrase **"Learning purposes: not a statutory document"**, and the line **"Learnings drafted by an AI agent from AI-assisted findings"**.
- The export's own justification text is labelled **"AI justification (ProbeMatrix)"**.
- A finding that no person edited in ProbeMatrix carries the chip **"AI-drafted, not human-edited"**.
- When you open a finding or evidence record, a banner says: "This is the investigation's AI-drafted wording, shown as evidence; it is not the coach's learning."

These labels cannot be switched off.

## The handling block

A pack or register records its review state in a small `handling` block inside its JSON file. You do not write it by hand: `sign-off` writes it. It holds:

| Key | Meaning | Values | When absent |
|---|---|---|---|
| `status` | how far the review has gone | `draft`, `reviewed`, `approved` | `draft` |
| `reviewer_role` | the reviewer's role, never a name | text | none |
| `reviewed_on` | the review date | `YYYY-MM-DD` | none |
| `classification` | who may see it | `internal`, `restricted`, `external`, `public` | `internal` |
| `legal_review` | whether legal review is needed, asked for or done | `not-required`, `requested`, `cleared` | `not-required` |
| `distribution` | the audiences it is meant for | a list | empty |
| `version` | your version label | text | `1.0` |
| `retention_review` | when to review whether to keep it | `YYYY-MM-DD` | none |
| `content_hash` | a fingerprint of everything else in the file | `sha256:` and 64 characters | none |

A file with no handling block is still valid. It is shown as a draft for internal use, and the check passes with the warning `no handling block: rendered as draft (internal)`.

The four classifications, from narrowest to widest:

- **internal**: for people inside the organisation;
- **restricted**: inside the organisation, but only for the named distribution;
- **external**: for named people outside, such as a regulator, a client or an insurer;
- **public**: for anyone.

## Forced draft: when nothing can be approved yet

The coach will not let anything be reviewed or approved while either of these is true of the export:

- **"the investigation status is in progress"**: the export's Investigation Status starts with `in_progress`;
- **"no finding is marked as edited by a person"**: not one finding has `User Edited` set.

There is no override. The fix is in ProbeMatrix, not in the coach: finish the investigation (a person reviews and edits the findings, and the status moves on), then export again and re-run the analysis.

The public Hazira sample meets both conditions: its status is `in_progress` and none of its 436 findings was edited. So every Hazira output stays a draft, and `sign-off` on Hazira prints:

```text
cannot sign off: the investigation status is in progress; no finding is marked as edited by a person
```

## The DRAFT ribbon and the handling line

Until a file is **approved**, its pages show a **DRAFT** ribbon at the top. A `reviewed` file still shows it. Under the title, a handling line says where the file stands, and why it is a draft:

```text
Review: draft · Classification: internal · Version 1.0
Draft because: the investigation status is in progress; no finding is marked as edited by a person
```

- The Markdown file shows `**DRAFT**` under the title.
- Each sheet of the register workbook has the status phrase in its page header, followed by "· DRAFT" while it is a draft.
- In print the ribbon keeps its border and text, so it does not depend on colour, and every printed page carries the status phrase in its footer.

Other reasons you may see after "Draft because:" are "edited since sign-off", "not signed off" (the file claims a status but has no valid fingerprint) and "invalid handling block".

## Sign-off

Sign-off records that a person reviewed a file. Ask the agent, giving your role:

> I have reviewed the supervisor coach and approve it. My role is HSE manager.

The agent then runs [sign-off](commands/sign-off.md):

```bash
pmlc sign-off <ws> <run>/outputs/supervisor-coach.json --role "HSE manager" --status approved
```

Optional flags set the other handling keys: `--classification`, `--legal-review`, `--distribution`, `--retention-review`, `--version` and `--date` (the review date; today by default). `--status` is `reviewed` or `approved`.

Rules the coach follows:

- **The agent never signs off on its own.** It runs `sign-off` only when you have said you reviewed the output and given your role. It never writes a reviewer's name, an owner or a due date.
- **Sign-off is refused** while the export is forced to draft, and while the file has any problem in `check-pack` or `check-register`. Fix the problems first.
- **A register must be an object.** A register saved as a bare list is refused with `wrap the entries as {"entries": [...]} before signing off`.

What sign-off writes:

- the `handling` block, with a `content_hash`: a fingerprint of everything in the file except the handling block;
- an entry in the workspace manifest, which `pmlc status <ws>` lists with its status, role, date and whether the file has changed since.

Re-run `pack`, `dashboard` or `register-xlsx` after sign-off, so the pages show the new state.

### After an edit, it is a draft again

If anyone changes a signed-off file afterwards, even by one character, the fingerprint no longer matches. The status falls back to draft, the DRAFT ribbon returns, and the check warns:

```text
edited since sign-off: status is draft until signed off again
```

Review the change and sign off again. This is deliberate: an approval covers the exact text that was reviewed.

## How much evidence a page carries: `--embed`

*This arrives with v2.0.0-alpha.4, on [pack](commands/pack.md) and [dashboard](commands/dashboard.md).*

A pack page carries the full records of the findings and evidence it cites, so a reader can check every sentence. `--embed` decides how much else it carries:

| Mode | What the page carries | Use it for |
|---|---|---|
| `cited` (the default) | Full records only for the cited findings and evidence. Findings the pack does not cite are listed by ID, label and rating only. | normal internal use |
| `summary` | As `cited`, but without evidence descriptions, specific references (quotes), suggested interviews, key questions and reviewers' vote reasons. | anything shared outside; the default when sharing |
| `full` | Every record in full, as in v0.3. | an internal working copy for the investigation team |

If a page would carry witness statements, the command notes `embedded evidence includes witness statements; consider --embed summary`.

**Print only what is cited.** In print, the evidence trail lists only the cited IDs. The findings the pack does not cite print as one line, "x of y relevant findings cited", while the screen keeps the full list you can open.

When an item has a `lint_ok` (an accepted language-check exception), its reason is shown on the page, so a reader can see why the wording was kept. See [Language checks](Language-checks.md#accepting-a-hit).

## Sharing outside the organisation: `--share`

*This arrives with v2.0.0-alpha.4, on [pack](commands/pack.md), [dashboard](commands/dashboard.md) and [register-xlsx](commands/register-xlsx.md), with `--names FILE` and `--orgs FILE`.*

A pack or register is written for the organisation's own learning. Before anything goes to a regulator, a client, an insurer or the public, it needs a separate, masked copy. `--share` has three modes:

- `internal` (the default): no masking.
- `external`: for named people outside the organisation.
- `public`: for anyone.

### The conditions (the legal-review rule)

`--share external` or `--share public` works only when **all** of these hold:

1. The file's effective status is **approved**: signed off, not edited since, and not forced to draft.
2. Its classification is at the sharing level or wider: `external` or `public` for external sharing, `public` for public sharing.
3. Its `legal_review` is **`cleared`**. A person with legal responsibility has read it. The coach's outputs are learning material; they create no legal privilege.
4. The embed mode is `summary`. It is the default when sharing; an explicit `--embed cited` or `--embed full` is refused.

If any condition fails, the command lists every unmet condition, exits, and writes nothing. On Hazira the first condition can never hold, so no Hazira output can be shared this way.

A typical sequence, once the investigation is complete in ProbeMatrix:

```bash
pmlc sign-off <ws> <run>/outputs/board-brief.json --role "HSE manager" --status approved \
     --classification external --legal-review cleared
pmlc pack <ws> <run>/outputs/board-brief.json --share external --names names.txt --orgs orgs.txt
```

### What the shared copy masks

In `external` and `public` mode the copy:

- replaces personal names (from `--names` or `PMLC_NAMES`) with `[name]`;
- replaces organisation names (from `--orgs` or `PMLC_ORGS`, and names ending in Ltd, Pvt, Inc, GmbH, LLC or Limited) with `[organisation]`;
- replaces equipment tags such as `PSV-101` with `[equipment tag]`;
- replaces roles that point to one person (from `singleton_roles.json`) with their general label;
- replaces owners at site-leadership and board level with the general function;
- removes clock times (`HH:MM`);
- coarsens exact dates to month and year, for example "September 2020";
- drops suggested interviews, key questions and reviewers' vote reasons, and the run folder name and generation time.

The page then says "Shared external: identifying details are masked" (or "public").

### The shared files

The masked copy is written beside the internal one, so the internal copy is never overwritten:

- `<pack>.external.html` and `<pack>.external.md`;
- `<pack>.public.html` and `<pack>.public.md`.

### The name guard

In any mode, `pack` and `dashboard` refuse to write a page that still contains a name from your names file. They exit and write nothing. Fix the pack text, or redact the name at ingest.

## Keeping names out from the start

Two tools help at the other end of the process:

- `pmlc ingest <export> --slug <site>-<event> --redact names-map.json` replaces each listed name, and its common variants, with a role as the export is read. Nothing downstream can then quote it. See the recipe [Redact names at ingest](Workflows-and-recipes.md#redact-names-at-ingest).
- `pmlc scan-names names.txt <files or folders> --variants` scans finished files, including Office and PDF metadata, and must print `0 hit(s).` before you share. `--patterns` also flags emails, phone numbers and staff numbers: an aid, not proof.

## Before you share: a checklist

- The investigation is complete in ProbeMatrix, and the export you analysed is the final one.
- `check-pack` (or `check-register`) passes, with the language check run at the sharing level: `--share external` (see [Language checks](Language-checks.md)).
- A competent person has reviewed the file, and you have told the agent your role for the sign-off.
- The classification matches the audience, and legal review is cleared.
- You have read the masked copy yourself, from the reader's side.
- `scan-names` on the files you will send prints `0 hit(s).`
