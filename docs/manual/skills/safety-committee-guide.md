# safety-committee-guide

A discussion guide for joint health and safety committees, workforce safety representatives and union safety reps. It gives a plain-language account, the questions the workforce should raise with management, what to look for on site, and how to keep the discussion about systems rather than blame.

## What it is for

- Safety committee material.
- A worker consultation pack, or a guide for safety reps.
- A workforce engagement session or a town-hall discussion on an investigation.

Workforce representatives give the workforce a voice, raise concerns and check that learning reaches the people who do the work. They need a fair account and good questions.

## How to start it

- "Prepare a discussion guide for our safety committee on this investigation."
- "What questions should the workforce reps raise with management?"
- "Give me a 60-minute agenda and ground rules for a workforce session on this event."

## What it needs

- A workspace with `clusters.json`.

## Engine commands and flags

```bash
pmlc profile <ws>
pmlc select <ws> --tier T1 T2 --brief
pmlc select <ws> --level 4 --top-rated --brief
pmlc select <ws> --relation norm_setter learner challenger --brief
pmlc select <ws> --preset safety-committee-guide   # the three select calls above at once
pmlc check-pack <ws> <run>/outputs/safety-committee-guide.json
pmlc pack <ws> <run>/outputs/safety-committee-guide.json
```

- [profile](../commands/profile.md) gives the share of causes at supervision and organisational level.
- [select](../commands/select.md): `--tier T1 T2` the frontline and supervision tiers; `--level 4` the Organisational Influences level; `--top-rated` the strongest; `--relation norm_setter learner challenger` findings about what leaders modelled, what people absorbed and where challenge was expected; `--brief` short entries.
- [check-pack](../commands/check-pack.md) and [pack](../commands/pack.md) render the pack.

## What you get

`safety-committee-guide.html` and `.md`:

1. **what happened**, in a page, in plain language, roles only;
2. the five learnings most relevant to the workforce, and where the analysis places the causes;
3. ten **questions to raise with management**: staffing, training, procedures, equipment, authority to stop work, and how concerns are handled;
4. **what to look for on site**: a walk-round prompt list;
5. **running the discussion**: a 60-minute agenda and ground rules (no names, no blame, focus on conditions), with an anonymous route for concerns. Concerns are recorded by topic, not by who raised them;
6. **follow-up** at 30, 60 and 90 days.

## Worked example (Hazira)

`profile` showed 308 of 436 findings (71%) at the Supervision and Organisational levels, so the guide can say plainly that most causes sit above the frontline. `select --tier T1 T2 --brief` returned 347 findings, `--level 4 --top-rated --brief` returned 47, and the relation filter returned 4.

These counts are from the base classification, before the resolution pass. After you place the remaining roles they will be somewhat higher, most for T3 (in a trial resolution pass on Hazira: T1 222→231, T2 237→238, T3 211→257).

## Related skills

- [frontline-learning-cards](frontline-learning-cards.md): the material the crews will see.
- [supervisor-coach](supervisor-coach.md): what supervisors are being asked to do.
- [board-brief](board-brief.md): the questions the board is asking at the other end.
