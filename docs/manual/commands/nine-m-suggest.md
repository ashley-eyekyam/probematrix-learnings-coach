# nine-m-suggest

## What it does

Prints the suggestions for one question of a 9M analysis, the recommended one first, and always ends the list with "None / unknown (record as a gap)". With `--record` it appends the question, with its suggestions and their cites, to `<ws>/nine_m_session.json`, so the session can be resumed and audited. The answer is recorded with [nine-m-answer](nine-m-answer.md).

The suggestions are deterministic: the same workspace gives the same list, in rating order. Each one that states a fact cites at least one Finding ID. There are 2 to 4 of them before "None / unknown":

| Step | Where the suggestions come from |
|---|---|
| `relevance` | The findings the seed links to the M (by Nanocode, wording or cluster): relevant, partly relevant (one code only) or not relevant, each with its cites |
| `subcategory` | The M's subcategories in `references/nine-m.json`, ranked by the words they share with the M's findings. A subcategory that overlaps another M (for example M7.02 and M9) says so, so that you ask which M owns it |
| `condition` | One condition per Nanocode among the M's findings, in rating order, worded from the finding's short description |
| `driver` | Causal links in `causal_graph.json` from a level 3 or 4 code into the M's codes (why it made sense), then the M's own level 3 and 4 findings |
| `barrier` | Evidence quotes from the M's findings, one finding at a time, with a barrier state from the shared vocabulary (absent, degraded, defeated, worked partly) |
| `change` | Directions of change, strongest first: elimination, substitution (M7 and M8 only), engineering, administrative. Training is offered only together with an engineered control and is labelled "(weak on its own)". Each asks you to say whether this change is corrective or preventive, since the tier alone does not decide it |
| `scope` | Which Ms to work through: every M with seed weight, the top four by top-rated findings, or a list you choose (answered with `nine-m-answer --text`, naming the Ms) |
| `cross-m` | Pairs of relevant Ms that a causal link joins, to keep as one learning or separate |
| `gaps` | Evidence requests for every question answered "None / unknown" |

Discipline, accountability and consequences (as a sanction) are never offered, whatever the export's wording. A process-safety condition such as "consequence analysis not done" is kept. No suggestion names an owner or a date.

## When to use it

During the `nine-m-analysis` interview, once per question: one question per turn, through the host's question tool or as a numbered list. Run [nine-m-seed](nine-m-seed.md) first.

## Synopsis

```text
pmlc nine-m-suggest ws [--m {M1,M2,M3,M4,M5,M6,M7,M8,M9}]
                    --step {relevance,subcategory,condition,driver,barrier,change,scope,cross-m,gaps}
                    [--subcategory SUBCATEGORY] [--top TOP] [--record] [--json]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder, with `nine_m_seed.json` |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--m` | `M1`, `M2`, `M3`, `M4`, `M5`, `M6`, `M7`, `M8` or `M9` | none | The M the question is about. Required for `relevance`, `subcategory`, `condition`, `driver`, `barrier` and `change`; ignored for `scope`, `cross-m` and `gaps` |
| `--step` | a step | required | The question: `relevance`, `subcategory`, `condition`, `driver`, `barrier` or `change` for one M; `scope`, `cross-m` or `gaps` for the whole analysis |
| `--subcategory` | an id such as `M8.02` | none | The subcategory chosen for this M. It brings the findings that share its words to the front for the later steps. It must belong to `--m` |
| `--top` | 2 to 4 | 4 | How many suggestions come before "None / unknown" |
| `--record` | none | off | Append the question to `<ws>/nine_m_session.json` and print its question id (Q01, Q02, ...). The budget is 6 questions per M and 4 global questions; one more is refused |
| `--json` | none | off | Print the suggestions as JSON: a list of `{"text", "cites"}` |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

```bash
python3 $E nine-m-seed $WS
python3 $E nine-m-suggest $WS --step scope --record
python3 $E nine-m-suggest $WS --m M8 --step relevance --record
```

On Hazira the M8 (Material) relevance question recommends "Relevant": 162 findings point to Material, only 9 of them by their Nanocode and the rest by their wording, led by OIR 1.5 (Failure in Timely Acquisition/ Procurement/ Upgrade). This is how the under-coded Material and Maintenance Ms reach a condition.

```bash
python3 $E nine-m-suggest $WS --m M8 --step condition --subcategory M8.03 --record
```

## Common problems

- **"… has no nine_m_seed.json: run nine-m-seed first".** Run [nine-m-seed](nine-m-seed.md) on the workspace (exit code 2).
- **"--step relevance asks about one M: give --m M1..M9".** The per-M steps need `--m` (exit code 2).
- **"M3.99 is not a subcategory of M3".** Use an id from `references/nine-m.json` that belongs to the M.
- **"The question budget for M7 is used up".** An M has had its 6 questions. Write what the session holds, or record the rest as gaps.
- **"… is a replay (answers chosen for demonstration)".** The session file was written by [nine-m-replay](nine-m-replay.md). Move it aside to start a real interview.

## Related

- [nine-m-answer](nine-m-answer.md) records the answer.
- [nine-m-replay](nine-m-replay.md) writes a whole scripted session.
- [nine-m-seed](nine-m-seed.md) scores the findings per M.
- [nine-m-actions-template](nine-m-actions-template.md) writes the blank actions sheet after the pack.
