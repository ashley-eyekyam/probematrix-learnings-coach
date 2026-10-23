# nine-m-replay

## What it does

Writes a whole 9M session by taking suggestion 1, the recommended one, at every question: the scope question, then for each M in scope its relevance question and, when it is relevant, the subcategory, condition, driver, barrier and change questions; then the cross-M question (when two or more Ms are relevant) and the gaps question. The session is written to `<ws>/nine_m_session.json` with `"mode": "replay"`, keeps the question budget (6 per M plus 4) and is byte-identical when run again.

A pack written from a replay must carry the banner "Answers chosen for demonstration, not by the organisation." `check-pack` asks for it only when the session is a replay.

## When to use it

To build the worked example of a 9M analysis, or to see what the interview would suggest before running it with the organisation. A real analysis is an interview: [nine-m-suggest](nine-m-suggest.md) records each question and [nine-m-answer](nine-m-answer.md) each answer.

## Synopsis

```text
pmlc nine-m-replay ws [--accept-recommended] [--ms MS]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder, with `nine_m_seed.json` |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--accept-recommended` | none | off | Required: take suggestion 1 at every question. Without it nothing is written |
| `--ms` | comma list, e.g. `M3,M8` | the recommended scope | Work through these Ms only. The scope answer is then recorded as the user's |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E nine-m-seed $WS
python3 $E nine-m-replay $WS --accept-recommended
```

On Hazira the replay asks 57 questions and finds all nine Ms relevant, Material (M8) and Maintenance (M9) included, although their Nanocodes seed only 9 and 27 findings.

```bash
python3 $E nine-m-replay $WS --accept-recommended --ms M8,M9
```

## Common problems

- **"nine-m-replay writes a scripted session only with --accept-recommended".** Add the flag (exit code 2).
- **"… holds an interview (n question(s)); move it aside before a replay".** A real interview is never overwritten.
- **"--ms takes M1-M9, not M12".** Use the codes M1 to M9.
- **"… has no nine_m_seed.json: run nine-m-seed first".** Run [nine-m-seed](nine-m-seed.md).

## Related

- [nine-m-suggest](nine-m-suggest.md) and [nine-m-answer](nine-m-answer.md) run the real interview.
- [check-pack](check-pack.md) asks for the demonstration banner on a pack written from a replay.
