# nine-m-answer

## What it does

Records the answer to one 9M question in `<ws>/nine_m_session.json`. `--choice N` takes suggestion N as it was shown (source `export`); `--text` stores the user's own words exactly as given (source `user`). Answering again replaces the earlier answer. An option that asks for the user's own words ("Describe it in your own words …", "A list you choose …") is answered with `--text`, never `--choice`, because its wording is an instruction, not an answer. A relevance answer of "Skip the rest of this M" leaves the M open, not relevant.

Facts that the user supplies are context from the organisation: the pack puts them in its "Context supplied by the organisation" section and in `data_quality`, never with a Finding ID. If a free-text answer names a date or a deadline, it is still stored as given, and a note reminds you that owners and due dates are set by the organisation and stay out of the pack (D7).

## When to use it

After each question asked with `nine-m-suggest --record`, before the next question.

## Synopsis

```text
pmlc nine-m-answer ws --q Q (--choice CHOICE | --text TEXT)
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder that holds `nine_m_session.json` |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--q` | a question id | required | The question, as `nine-m-suggest --record` printed it, for example `Q03` |
| `--choice` | a number | none | The suggestion chosen; 1 is the recommended one, and the last is "None / unknown" |
| `--text` | text | none | The user's own answer, stored verbatim. Give `--choice` or `--text`, not both |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E nine-m-answer $WS --q Q02 --choice 1
python3 $E nine-m-answer $WS --q Q05 --text "The spares were ordered by phone, with no specification"
```

## Common problems

- **"… has no nine_m_session.json yet".** Ask a question with `nine-m-suggest … --record` first (exit code 2).
- **"Q09 is not a question in nine_m_session.json".** The message lists the question ids the session holds.
- **"--choice must be 1 to 5 for Q02".** The number is outside the list that was shown.
- **"suggestion 3 of Q01 asks for your own words: answer with --text".** That option is a prompt for free text; give the answer with `--text` (exit code 2).
- **"note: the answer names a date or a deadline …".** The answer is stored, but do not carry the owner or the date into the pack: the organisation sets them.

## Related

- [nine-m-suggest](nine-m-suggest.md) asks the question.
- [nine-m-replay](nine-m-replay.md) answers every question with the recommended suggestion.
- [check-pack](check-pack.md) refuses a recommendation with an owner or a due date in the nine-m-analysis pack.
