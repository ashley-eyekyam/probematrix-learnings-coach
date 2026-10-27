# safety-committee-guide

A discussion guide for joint health and safety committees, workforce safety representatives and union safety reps. It gives a plain-language account, the questions the workforce should raise with management, what to look for on site, a concerns log, and how to keep the discussion about systems rather than blame.

## What it is for

- Safety committee material from a ProbeMatrix export.
- A worker consultation pack, or a guide for safety reps.
- A workforce engagement session or a town-hall discussion on an investigation.

Workforce representatives give the workforce a voice, raise concerns and check that learning reaches the people who do the work. They need a fair account and good questions.

## How to start it

- "Prepare a discussion guide for our safety committee on this investigation."
- "What questions should the workforce reps raise with management?"
- "Give me a 60-minute agenda, ground rules and a concerns log for a workforce session on this event."

## What it needs

- A workspace with `clusters.json`.
- Optional: the Learnings Register (its T1 and T2 learnings and `LR-nn` ids).

## Engine commands and flags

```bash
pmlc facts <ws>                                     # level counts and l34_share
pmlc select <ws> --tier T1 T2 --brief
pmlc select <ws> --level 4 --top-rated --brief
pmlc select <ws> --relation norm_setter learner challenger --brief
pmlc select <ws> --prefix OIC --top-rated --brief   # culture fallback
pmlc select <ws> --preset safety-committee-guide    # the four select calls above at once
pmlc check-pack <ws> <run>/outputs/safety-committee-guide.json --strict
pmlc pack <ws> <run>/outputs/safety-committee-guide.json
pmlc pack <ws> <run>/outputs/safety-committee-guide.json --layout checklist   # the walk-round sheet
pmlc pack <ws> <run>/outputs/safety-committee-guide.json --format pptx        # slides for the meeting
pmlc pack <ws> <run>/outputs/safety-committee-guide.json --format ics --start YYYY-MM-DD   # only with your meeting date
pmlc templates <ws> distribution                    # the session record, once per run
```

- [facts](../commands/facts.md) gives `l34_share`, the share of findings at the Supervision and Organisational levels. When it is 0.5 or more, the guide says plainly that the analysis places most causes there.
- [select](../commands/select.md): `--tier T1 T2` the frontline and supervision tiers; `--level 4` the Organisational Influences level; `--top-rated` the strongest; `--relation norm_setter learner challenger` findings about what leaders modelled, what people absorbed and where challenge was expected; `--prefix OIC` the Organisational Climate findings, used when the relation selection is thin; `--brief` short entries.
- [check-pack](../commands/check-pack.md) with `--strict` checks the pack against its profile; [pack](../commands/pack.md) renders it.
- [templates](../commands/templates.md) `distribution` writes `distribution.csv`, where the committee records each session and the concerns it escalated. It never overwrites an existing file.

## What you get

`safety-committee-guide.html` and `.md`:

1. **what happened**, in plain language, roles only;
2. up to five learnings most relevant to the workforce, and where the analysis places the causes (from `l34_share`);
3. up to ten **questions to raise with management**: staffing, training, procedures, equipment, authority to stop work, and how concerns are handled;
4. **what to look for on site**: a walk-round prompt list;
5. **running the discussion**: a 60-minute agenda and ground rules (no names, no blame, focus on conditions), with an anonymous route for concerns. Concerns are recorded by topic, not by who raised them;
6. a **concerns log**: a table with the columns Concern, Condition seen, Location type, Date raised and Response requested, started from the conditions in the findings, with the date left for the committee;
7. **follow-up** at 30, 60 and 90 days;
8. a note on **committee and representative rights**: the guide does not replace any statutory right to consultation or to investigation documents. It names a regime only from the coach's [jurisdictions reference](https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/skills/learnings-coach/references/jurisdictions.md) and draws no legal conclusion.

**Formats.** `--layout checklist` writes `safety-committee-guide.checklist.html`: the look-for and follow-up checks with a box each and a "Checked by (role) / Date / Shift" line per section, to print and carry on site. `--format pptx` gives slides for the meeting. `--format ics --start <meeting date>` turns the 30, 60 and 90-day follow-ups into all-day reminders with no attendees. A Hindi or other-language copy goes through [strings](../commands/strings.md). See [pack](../commands/pack.md).

## Worked example (Hazira)

`facts` gave `l34_share` 0.706 (308 of 436 findings at the Supervision and Organisational levels), so the guide can say plainly that most causes sit above the frontline. `select --tier T1 T2 --brief` returned 347 findings and `--level 4 --top-rated --brief` returned 47. The relation filter returned only 4, so the culture questions use the fallback: `--prefix OIC --top-rated --brief` returned 19 Organisational Climate findings.

These counts are from the base classification, before the resolution pass. After you place the remaining roles they will be higher, most for T3 (in one trial pass on Hazira, roughly T1 222→231, T2 237→238, T3 211→257; your numbers depend on how you place roles).

## Related skills

- [frontline-learning-cards](frontline-learning-cards.md): the material the crews will see.
- [supervisor-coach](supervisor-coach.md): what supervisors are being asked to do.
- [board-brief](board-brief.md): the questions the board is asking at the other end.
- [learning-effectiveness-plan](learning-effectiveness-plan.md): when and how to check that a learning took hold (3, 6 and 12 months, plus 30, 60 and 90 days for priority 1).
