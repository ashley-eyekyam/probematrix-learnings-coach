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

- **the investigation is not completed**: the export's Investigation Status is anything but `completed` (capitals, spaces and hyphens do not matter). The reason reads "the investigation status is in progress" for `in_progress` (or "In Progress", "in-progress"), and "the investigation status is not completed" for anything else, such as `draft` or a blank status;
- **"no finding is marked as edited by a person"**: not one finding has `User Edited` set to `Yes` (`y`, `true` and `1` count too; `No`, `N`, `false` or a blank do not).

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

Other reasons you may see after "Draft because:" are:

- "edited since sign-off": the file changed after it was signed off;
- "not signed off": the file claims `reviewed` or `approved`, but this workspace has no sign-off of it (the block was typed by hand, edited by hand, or the file was copied from another folder or workspace);
- "no workspace to check": `register-xlsx` was given a register outside the run layout and no `--ws`, so nothing can be checked;
- "invalid handling block": a key or value in the block is wrong.

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
- **The reviewer is a role.** A `--role` or `--distribution` value that looks like a personal name is refused with `--role: looks like a personal name ("…"); give a role`.
- **A register must be an object.** A register saved as a bare list is refused with `wrap the entries as {"entries": [...]} before signing off`.

What sign-off writes:

- the `handling` block, with a `content_hash`: a fingerprint of everything in the file except the handling block;
- an entry in the workspace manifest, which `pmlc status <ws>` lists with its status, role, date and whether the file has changed since. The entry holds the whole handling block and the file's full path.

A status counts only when the manifest entry matches: the same file, at the same path, in the same workspace, with the same handling block. A handling block typed or changed by hand, or a signed file copied to another folder or workspace, is a draft with the reason "not signed off", and the check warns:

```text
not signed off in this workspace: status is draft until sign-off records it
```

Re-run `pack`, `dashboard` or `register-xlsx` after sign-off, so the pages show the new state.

### After an edit, it is a draft again

If anyone changes a signed-off file afterwards, even by one character, the fingerprint no longer matches. The status falls back to draft, the DRAFT ribbon returns, and the check warns:

```text
edited since sign-off: status is draft until signed off again
```

Review the change and sign off again. This is deliberate: an approval covers the exact text that was reviewed.

## How much evidence a page carries: `--embed`

`--embed` is a flag of [pack](commands/pack.md) and [dashboard](commands/dashboard.md). A register workbook embeds no records, so [register-xlsx](commands/register-xlsx.md) has no such flag.

A pack page carries the full records of the findings and evidence it cites, so a reader can check every sentence. `--embed` decides how much else it carries (for a dashboard, read "the register" for "the pack"):

| Mode | What the page carries | Use it for |
|---|---|---|
| `cited` (the default) | Full records only for the cited findings and evidence. Findings the pack does not cite are listed by ID, label and rating only. | normal internal use |
| `summary` | As `cited`, but without evidence descriptions, specific references (quotes), suggested interviews, key questions and reviewers' vote reasons. | anything shared outside; the default when sharing |
| `full` | Every relevant record in full, as in v0.3. | an internal working copy for the investigation team |

In `summary` mode, word-for-word repeats of an evidence description or reference elsewhere in the embedded text (for example inside an AI justification) are replaced with `[quote omitted]`.

If a page would carry witness statements, the command prints this note (a reminder, not an error):

```text
note: embedded evidence includes witness statements; consider --embed summary
```

The Hazira learning map with the sample register prints it. On a small Hazira board brief that cites three findings, the page is about 205 KB with `cited`, 168 KB with `summary` and 1.2 MB with `full`.

**Print only what is cited.** In print, the evidence trail lists only the cited IDs, in the order they are cited, and it follows the pack on the same page instead of starting a new one. The findings the pack does not cite print as one line, "x of y relevant findings cited", while the screen keeps the full list you can open.

When an item has a `lint_ok` (an accepted language-check exception), its reason is shown on the page, so a reader can see why the wording was kept. See [Language checks](Language-checks.md#accepting-a-hit).

## Sharing outside the organisation: `--share`

`--share` is a flag of [pack](commands/pack.md), [dashboard](commands/dashboard.md) and [register-xlsx](commands/register-xlsx.md), together with `--names FILE` and `--orgs FILE` (or the `PMLC_NAMES` and `PMLC_ORGS` variables).

A pack or register is written for the organisation's own learning. Before anything goes to a regulator, a client, an insurer or the public, it needs a separate, masked copy. `--share` has three modes:

- `internal` (the default): no masking.
- `external`: for named people outside the organisation.
- `public`: for anyone.

### The conditions (the legal-review rule)

`--share external` or `--share public` works only when **all** of these hold:

1. The file's effective status is **approved**: signed off, not edited since, and not forced to draft.
2. Its classification is at the sharing level or wider: `external` or `public` for external sharing, `public` for public sharing.
3. Its `legal_review` is **`cleared`**. A person with legal responsibility has read it. The coach's outputs are learning material; they create no legal privilege.
4. For a pack or a dashboard, the embed mode is `summary`. It is the default when sharing; an explicit `--embed cited` or `--embed full` is refused.

Two more conditions apply to particular commands:

- **dashboard** checks the register given with `--register`. Without a register there is nothing signed off, so the copy is refused.
- **register-xlsx** needs the workspace, to see whether the investigation is finished. It finds it when the register sits in its run's `outputs/` folder; otherwise pass `--ws`, or the copy is refused with `no workspace (pass --ws)`.

If any condition fails, the command lists every unmet condition after `cannot share externally:` (or `cannot share publicly:`), exits with code 1 and writes nothing. On Hazira the first condition can never hold, so no Hazira output can be shared this way:

```text
cannot share externally: review is draft (the investigation status is in progress, no finding is marked as edited by a person); classification is "internal" (needs "external" or "public"); legal_review is not "cleared"
```

The other messages you may see after the colon are `review is reviewed (needs approved)`, `classification is "external" (needs "public")` and `--embed full is refused (use --embed summary)` (or `--embed cited`).

A typical sequence, once the investigation is complete in ProbeMatrix:

```bash
pmlc sign-off <ws> <run>/outputs/board-brief.json --role "HSE manager" --status approved \
     --classification external --legal-review cleared
pmlc pack <ws> <run>/outputs/board-brief.json --share external --names names.txt --orgs orgs.txt
```

### What the shared copy masks

In `external` and `public` mode the copy is made from masked copies of the pack (or register) and of the workspace records it embeds. It:

- replaces personal names with `[name]`: the names in `--names` or `PMLC_NAMES` with their common variants (surname, initials and surname, honorific and surname; a surname that is also a role word, such as "Officer", is not masked on its own), and any honorific followed by a name, such as "Mr" or "Shri", even without a names file;
- replaces organisation names with `[organisation]`: the names in `--orgs` or `PMLC_ORGS`, and any name ending in Ltd, Pvt, Inc, GmbH, LLC or Limited;
- replaces equipment tags (letters then digits, such as `PSV-101` or `AO-101`) with `[equipment tag]`. Finding, evidence, LR and ML IDs, function IDs such as `F02` and tier IDs such as `T4` are not tags. The pack links `learning`, `clauses`, `comparator_refs` and a test point's `clause` are kept as written; a `barrier_id` is masked like any other text, since it can hold a tag;
- replaces roles that point to one person with their function and tier, for example "Security Guard - Gate 3" becomes "Security & Surveillance (Unresolved)". These are the roles in `singleton_roles.json`: a role with an instance number or letter (such as a gate, post, shift, desk or control room number), or the only role at its tier in Plant & Asset Leadership or Corporate & Board. Group roles such as "Control Room Operators" or "seal change crew" are never singletons, and a date alone never makes one (full rule: [Singleton roles](Files-and-folders.md#singleton-roles));
- replaces owners at site-leadership and board level (T4 and T5) with the function and tier;
- removes clock times, such as "at 14:05", "14:05:30", "1405 hrs", "9.15 am", "21.30 hrs", and a four-digit time after a preposition ("At 0216", "at about 0300", "from 0200 until 0415"). A ratio such as "a ratio of 1:10" is kept. Years are kept too: after "about", "around", "by", "from", "until" or "till", a number from 1900 to 2099 reads as a year ("from 2017", "by 2020"); only after "at" is it a time ("at 1930"). A number followed by a unit ("at 1500 rpm", "about 1200 m") is a quantity and is kept;
- coarsens full dates to month and year: "2024-03-12", "12 March 2024" and "12/03/2024" all become "March 2024";
- drops suggested interviews, key questions, causal hypotheses, evidence to collect and reviewers' vote reasons, and the run folder name and generation date;
- in `public` mode, also drops the AI justification and the causal explanation from the embedded finding records;
- for a register, replaces the source file name with "a ProbeMatrix investigation export".

`pack` on the investigator-coach pack writes `follow-up.json` only for the internal copy: interview plans stay with the investigation team.

The page then says "Shared external: identifying details are masked" (or "Shared public: …"), and `pack` and `dashboard` print the same line when they finish. The workbook carries it as a "Sharing" row on its About sheet.

Masking covers the export's own text that the page embeds. The language check covers your wording: at the external level, an organisation's name or a singleton role in the pack's own text is an error, so fix the wording before you share.

### The shared files

The masked copy is written beside the internal one, so the internal copy is never overwritten:

- `<pack>.external.html` and `<pack>.external.md`, or `<pack>.public.html` and `<pack>.public.md`;
- `organisation-learning-map.external.html` or `organisation-learning-map.public.html`;
- `learnings-register.external.xlsx` or `learnings-register.public.xlsx`.

With `--out`, the dashboard and the workbook go exactly where you say, so choose a name that cannot overwrite the internal copy. For `pack`, `--out` is a folder and the `.external` or `.public` name is kept.

### The name guard

In any mode, `pack` and `dashboard` refuse to write a page that still contains a name from your names file. They exit with code 1, write nothing, and print:

```text
refused: a listed name appears in the output (<n> times); fix the pack text or use ingest --redact
```

Fix the pack text, or redact the name at ingest.

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
