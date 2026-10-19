# frontline-learning-cards

Frontline learning in plain language: one-page Learning Cards and five-minute toolbox talks for operators, technicians, fitters, crews, control-room staff and security personnel. Each card says what happened, why it made sense at the time, what the organisation is changing, the warning signs and what good looks like. The pack closes with a "stop and ask" list.

## What it is for

- Toolbox talks, safety moments and shift briefings.
- Learning cards and pre-job talk material for crews.
- "Make this useful for the people on the floor."

Frontline people (tier T1) control how the task is done today. They do not control procedures, budgets or design, so the cards never hand them an organisational fix as if it were theirs.

## How to start it

- "Make toolbox-talk learning cards for the maintenance crews from this investigation."
- "Give me five-minute talks for the control-room operators, and a stop-and-ask list."
- "Turn this into learning cards I can print for the shift briefing."

## What it needs

- `clusters.json`, with the frontline roles placed (run the [learning-clusters](learning-clusters.md) resolution pass first if many roles are unplaced).
- If you name a crew or trade, the agent adds that function's entity ID.
- Before wide release: a conversation with the people involved. These cards are read by the people whose acts appear in the findings.

## Engine commands and flags

```bash
pmlc select <ws> --tier T1 --brief            # what frontline roles were involved in
pmlc select <ws> --tier T1 --level 1 2        # acts and conditions at the sharp end
pmlc select <ws> --tier T1 --top-rated        # the ones that mattered most
pmlc select <ws> --preset frontline-learning-cards   # all three calls at once
pmlc select <ws> --tier T1 --entity F02 --brief      # for one crew or trade
pmlc check-pack <ws> <run>/outputs/frontline-learning-cards.json
pmlc pack <ws> <run>/outputs/frontline-learning-cards.json
```

- [select](../commands/select.md): `--tier T1` keeps frontline findings, `--level 1 2` the Unsafe Acts and Preconditions levels, `--top-rated` the strongest, `--entity` one function and `--brief` short entries. The preset runs the first three calls in turn.
- [check-pack](../commands/check-pack.md) warns when a card has no "what the organisation is changing" field. Because the pack's scope is exactly `["T1"]`, two language rules are stricter: a JC12 appeal such as "stay vigilant" and a JC6 training-only fix for a level 3 or 4 cause are errors, not warnings (see [Language checks](../Language-checks.md)).
- [pack](../commands/pack.md) renders the page. In print, a card is never split across two pages, and each card carries the status line "Learning purposes: not a statutory document".

## What you get

`frontline-learning-cards.html` and `.md`:

- a facilitator note on how to use the cards fairly;
- five to eight **Learning Cards**, each under 250 words, each citing its evidence;
- two or three **toolbox talks**, grouped by task (for example "returning equipment to service"), each with a discussion scenario;
- a **"stop and ask" list**: the situations where anyone on the crew should pause the job and ask a supervisor, and the support they should expect when they do.

If you ask for a translation, the text is translated and every ID stays the same.

## Worked example (Hazira)

`select --tier T1 --brief` returned 222 findings; `--tier T1 --level 1 2` returned 94; and `--tier T1 --top-rated` returned 83. From these the agent picks five to eight learnings a crew member can notice or act on, such as a test after a gasket change that must not be skipped (FND-3AB996FC). It leaves out learnings only managers can act on.

These counts are from the base classification, before the resolution pass. After you place the remaining roles they will be somewhat higher, most for T3 (in a trial resolution pass on Hazira: T1 222→231, T2 237→238, T3 211→257).

## Related skills

- [supervisor-coach](supervisor-coach.md): the checks behind the hold points on the cards.
- [training-designer](training-designer.md): turns the cards into a module.
- [safety-committee-guide](safety-committee-guide.md): the workforce representatives' view.
- Recipe: [A frontline toolbox talk, and printing it](../Workflows-and-recipes.md#a-frontline-toolbox-talk-and-printing-it).
