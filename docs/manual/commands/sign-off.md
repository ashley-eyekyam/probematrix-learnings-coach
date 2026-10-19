# sign-off

## What it does

Records that **a person reviewed** a learning pack or a Learnings Register. It writes a `handling` block into the JSON file and records the sign-off in the workspace manifest. The block holds:

| Key | What it holds |
|---|---|
| `status` | `reviewed` or `approved` (a file never signed off counts as `draft`) |
| `reviewer_role` | the reviewer's role, never their name |
| `reviewed_on` | the review date |
| `classification` | `internal`, `restricted`, `external` or `public`: who may read it |
| `legal_review` | `not-required`, `requested` or `cleared` |
| `distribution` | the audiences it goes to |
| `version` | the document version |
| `retention_review` | when to review whether to keep it |
| `content_hash` | a fingerprint of the content at sign-off |

The fingerprint matters: **if anyone edits the file after sign-off, even by one character, it counts as a draft again**, the DRAFT label comes back and [check-pack](check-pack.md) warns that it was edited since sign-off.

sign-off refuses, and changes nothing, when:

- the investigation is not finished in ProbeMatrix: its status is anything but completed ("the investigation status is in progress", or "the investigation status is not completed" for a draft or blank status), or no finding is marked as edited by a person. There is no override; finish the review in ProbeMatrix and export again;
- the file has problems in its own check ([check-pack](check-pack.md) or [check-register](check-register.md)). The check runs at the classification the file will have, so `--classification external` or `public` applies the stricter rules for outside readers (an organisation name, JC9, is then an error);
- the file is a register written as a bare list. Wrap it as `{"entries": [...]}` first;
- `--role` or a `--distribution` value looks like a personal name: an honorific form ("Mr …", "Shri R. K. …"), two capitalised words that are not role words, or a name from the names file. The reviewer and the audiences are always roles.

**Only a person signs off.** An AI agent runs this command only when you have told it that you reviewed the output, and given your role.

## When to use it

After you have read, and where needed edited, a pack or register, and you are ready to stand behind it in your role. Before sharing outside the organisation, the file must be `approved`, classified `external` or `public`, and have `legal_review` set to `cleared`.

## Synopsis

```text
pmlc sign-off ws file --role ROLE [--status {reviewed,approved}]
              [--classification {internal,restricted,external,public}]
              [--legal-review {not-required,requested,cleared}]
              [--distribution AUDIENCE [AUDIENCE ...]] [--retention-review YYYY-MM-DD]
              [--version VERSION] [--date YYYY-MM-DD] [--names NAMES]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |
| `file` | The pack or register JSON to sign off. It is updated in place |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--role` | text | required | The reviewer's role, for example "HSE manager". Never a name |
| `--status` | `reviewed` or `approved` | `reviewed` | `reviewed`: a competent person has checked it. `approved`: it is released for its distribution |
| `--classification` | `internal`, `restricted`, `external` or `public` | kept from the file, else `internal` | Who may read it |
| `--legal-review` | `not-required`, `requested` or `cleared` | kept from the file, else `not-required` | The state of any legal review |
| `--distribution` | audiences | kept from the file, else none | Who it goes to, for example `board site-leadership` |
| `--retention-review` | `YYYY-MM-DD` | none | When to review whether to keep the file |
| `--version` | text | kept from the file, else `1.0` | The document version |
| `--date` | `YYYY-MM-DD` | today | The review date |
| `--names` | file | `$PMLC_NAMES` | A names file, one name per line. `--role` and `--distribution` must not contain a listed name |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

The Hazira investigation is still in progress in ProbeMatrix, and no finding has been edited by a person, so nothing made from it can be signed off:

```bash
python3 $E sign-off $WS $OUT/learnings-register.json --role "HSE manager"
```

```text
cannot sign off: the investigation status is in progress; no finding is marked as edited by a person
```

The exit code is 1 and the file is unchanged. This is deliberate: learnings from an unfinished investigation stay drafts.

A person's name in place of a role is refused, and the file is unchanged:

```bash
python3 $E sign-off $WS $OUT/learnings-register.json --role "Mr John Smith" --status approved
```

```text
--role: looks like a personal name ("Mr John Smith"); give a role
```

On a finished investigation, a successful sign-off prints one line in the form `Signed off <file>: <status> by <role> on <date>`, and [status](status.md) and [check-pack](check-pack.md) then show the handling.

## Common problems

- **"cannot sign off: the investigation status is in progress …" or "… is not completed".** Finish the investigation in ProbeMatrix (status completed, findings reviewed and edited by a person), export again, [ingest](ingest.md) with `ingest --force`, then sign off.
- **"cannot sign off: the file has problems; run the check and fix them first".** The lines below it list the problems. Run [check-pack](check-pack.md) or [check-register](check-register.md).
- **'wrap the entries as {"entries": [...]} before signing off'.** A register written as a bare list cannot carry a handling block.
- **"… is neither a pack (no 'pack' key) nor a register (no 'entries')".** The wrong file was given.
- **'--role: looks like a personal name ("…"); give a role'.** Give the reviewer's role, such as "HSE manager", not their name. The same check applies to each `--distribution` value.
- **The DRAFT label came back.** The file was edited after sign-off. Review the change and sign off again.

## Related

- [Review and sharing](../Review-and-sharing.md): the full review and sharing workflow.
- [check-pack](check-pack.md) and [check-register](check-register.md) run before sign-off.
- [status](status.md) shows each pack's last check.
