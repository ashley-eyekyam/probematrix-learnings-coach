# frontline-learning-cards

Frontline learning in plain language: one-page Learning Cards and five-minute toolbox talks for operators, technicians, fitters, crews, control-room staff, security personnel and contractor crews. Each card says what happened, why it made sense at the time, what the organisation is changing, the warning signs and what good looks like. The pack opens with who delivers each card (usually the crew's supervisor) and closes with a "stop and ask" list.

## What it is for

- Toolbox talks, safety moments and shift briefings from a ProbeMatrix export.
- Learning cards and pre-job talk material for crews, including contractor crews.
- "Make this useful for the people on the floor."

Frontline people (tier T1) control how the task is done today. They do not control procedures, budgets or design, so the cards never hand them an organisational fix as if it were theirs. It is not for the supervisors' own checks ([supervisor-coach](supervisor-coach.md)), training modules ([training-designer](training-designer.md)) or response-phase learning for emergency teams ([emergency-response-learnings](emergency-response-learnings.md)).

## How to start it

- "Make toolbox-talk learning cards for the maintenance crews from this investigation."
- "Give me five-minute talks for the control-room operators, and a stop-and-ask list."
- "Turn this into learning cards for the contractor crews, and say which supervisor delivers each one."

## What it needs

- `clusters.json`, with the frontline roles placed (run the [learning-clusters](learning-clusters.md) resolution pass first if many roles are unplaced).
- Optional: the Learnings Register. When `<run>/outputs/learnings-register.json` exists, the cards take its T1 learnings and carry their `LR-nn` ids.
- If you name a crew or trade, the agent adds that function's entity ID.
- Before wide release: a conversation with the people involved. These cards are read by the people whose acts appear in the findings.

## Engine commands and flags

```bash
pmlc select <ws> --tier T1 --brief                    # what frontline roles were involved in
pmlc select <ws> --tier T1 --level 1 2 --top-rated    # sharp-end acts and conditions that mattered most
pmlc select <ws> --tag contractor --brief             # contractor crews (the contractor-workforce option)
pmlc select <ws> --preset frontline-learning-cards    # all three calls at once
pmlc select <ws> --tier T1 --entity F02 --brief       # for one crew or trade
pmlc register-items <ws> --tier T1                    # the register's T1 learnings, as ready items
pmlc check-pack <ws> <run>/outputs/frontline-learning-cards.json --strict
pmlc pack <ws> <run>/outputs/frontline-learning-cards.json
pmlc pack <ws> <run>/outputs/frontline-learning-cards.json --layout cards --paper A5   # pocket cards
pmlc pack <ws> <run>/outputs/frontline-learning-cards.json --layout field --base-url https://intranet.example.org/learning/frontline-learning-cards.html
pmlc pack <ws> <run>/outputs/frontline-learning-cards.json --layout toolbox           # one sheet per toolbox talk
pmlc strings extract <ws> <run>/outputs/frontline-learning-cards.json --lang hi       # translation, when asked
pmlc strings apply <ws> <run>/outputs/frontline-learning-cards.json <run>/outputs/frontline-learning-cards.strings.xlf --lang hi
pmlc templates <ws> distribution                      # the delivery record, once per run
```

- [select](../commands/select.md): `--tier T1` keeps frontline findings, `--level 1 2` the Unsafe Acts and Preconditions levels, `--top-rated` the strongest, `--tag contractor` the contractor functions, `--entity` one function and `--brief` short entries. The preset runs the first three calls in turn.
- [register-items](../commands/register-items.md) prints the register's learnings for a tier, with their `learning` ids.
- [check-pack](../commands/check-pack.md) with `--strict` also checks the pack against its profile (up to eight cards of at most 250 words, the delivery table, the toolbox talks and the stop-and-ask list). It warns when a card has no "what the organisation is changing" field. Because the pack's scope tiers are exactly `["T1"]`, two language rules are stricter: a JC12 appeal such as "stay vigilant" and a JC6 training-only fix for a level 3 or 4 cause are errors, not warnings (see [Language checks](../Language-checks.md)).
- [pack](../commands/pack.md) renders the page. In print, a card is never split across two pages, and each card carries the status line "Learning purposes: not a statutory document".
- [pack](../commands/pack.md) `--layout cards` prints one page per card, toolbox talk and scenario inject (A4, or A5 with `--paper A5`); `--layout field` adds the citations as end-notes and a printable delivery record; `--layout toolbox` prints one A4 sheet per toolbox talk (and says "nothing to write" when there is none). `--base-url`, the address where you publish the page, puts a QR code on each printed item that links back to it.
- [strings](../commands/strings.md) `extract` and `apply` carry the cards through a translation: the translator fills in the targets and writes a back-translation for each safety-critical item (a hold point, or "stop" or "do not start"); `apply` writes `frontline-learning-cards-hi.json`, which `check-pack` and `pack` treat like any pack. A fluent speaker checks it before use.
- [templates](../commands/templates.md) `distribution` writes `distribution.csv`, where the organisation records each briefing (channel, date, deliverer role, attendees, whether contractors were included, questions and concerns). It never overwrites an existing file.

## What you get

`frontline-learning-cards.html` and `.md`:

- **using these cards**: a facilitator note on using the cards fairly, and a table of who delivers each card, the [supervisor-coach](supervisor-coach.md) coaching scenario to pair it with, and whether the card also goes to contractor crews ("Contractor crews to brief": a plan; the record is `distribution.csv`);
- up to eight **Learning Cards**, each under 250 words, each citing its evidence. The first cite on each card is a level 1 or 2 finding (an act or condition at the sharp end); a level 3 or 4 finding may follow when it explains why the job felt normal;
- optional **Did you know?** and **What can you do?** lines on a card: a surprising fact from the evidence, and actions in the reader's own control;
- up to three **toolbox talks**, grouped by task (for example "returning equipment to service"), each with a discussion scenario and, optionally, the talk itself as a `toolbox` item in five parts: an opening question, the story in 90 seconds, two warning signs, one change for tomorrow and one question to the crew (plus a duration);
- a **"stop and ask" list**: the situations where anyone on the crew should pause the job and ask a supervisor, and the support they should expect when they do.

With the contractor-workforce option, the scope adds the `contractor` tag and the cards speak to contractor crews; the host organisation's system still owns their briefing and supervision. If you ask for a translation, the text is translated and every ID stays the same; the translated page says it was translated with AI assistance until a fluent speaker has checked it.

With the print layouts you also get `frontline-learning-cards.cards.html`, `.field.html` or `.toolbox.html`, made to print from the browser; each printed page carries the status line and, while the pack is a draft, the DRAFT label.

## Worked example (Hazira)

`select --tier T1 --brief` returned 222 findings; `--tier T1 --level 1 2 --top-rated` returned 38, the pool for each card's first cite; and `--tag contractor --brief` returned 2 (F17 Contractors), so on Hazira the "Contractor crews to brief" column mostly reads "Not covered by the findings". A card could rest on a test after a gasket change that must not be skipped (FND-3AB996FC). The agent leaves out learnings only managers can act on.

These counts are from the base classification, before the resolution pass. After you place the remaining roles they will be higher, most for T3 (in one trial pass on Hazira, roughly T1 222→231, T2 237→238, T3 211→257; your numbers depend on how you place roles).

## Related skills

- [supervisor-coach](supervisor-coach.md): the checks behind the hold points on the cards, and the crew briefing plan.
- [training-designer](training-designer.md): turns the cards into a module.
- [safety-committee-guide](safety-committee-guide.md): the workforce representatives' view.
- [supply-chain-contractor-learnings](supply-chain-contractor-learnings.md): the organisation's contractor-management learning and the contract owner's briefing points; the crews' own cards stay here.
- Recipe: [A frontline toolbox talk, and printing it](../Workflows-and-recipes.md#a-frontline-toolbox-talk-and-printing-it).
