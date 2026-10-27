# learning-team-facilitator

A pack that prepares a learning-team session: a meeting where the people who do the work explain how it is really done. The skill asks you two questions, one at a time: the session's scope and who will be in the room, by role. It then sets the export's document evidence (work as imagined) against its witness statements, logs and recordings (work as done), turns the findings whose wording is counterfactual ("did not", "would have") into "What made sense at the time …?" questions, and adds a session plan of 60 to 90 minutes and notes for the facilitator. The team supplies every answer; the pack holds none.

## What it is for

- A learning team, or a work-as-done session, with the crew after an investigation.
- Comparing what the procedures and records say with what the people who do the job describe.
- Questions to put to the team about their work, instead of findings about them.

## How to start it

- "Set up a learning team with the fitters about the meter seal job."
- "I want to hear from the operators how the job really goes on a normal shift, without pointing fingers."
- "Give me questions and a session plan for a work-as-done review of the emergency isolation."

## What it needs

- A workspace (`setup` writes it).
- `wai_wad.json`, which the skill writes with [wai-wad](../commands/wai-wad.md) in its first step.
- Optional: the Learnings Register, when the scope is one learning (`LR-nn`).
- Your answers to its two questions: the scope (one activity, one function's cluster or one learning) and the roles in the room. Roles only, never names.

## Engine commands and flags

```bash
pmlc wai-wad <ws>                                  # the comparison and its counts -> wai_wad.json
pmlc wai-wad <ws> --table-item gaps                # codes with both document and work-as-done evidence
pmlc wai-wad <ws> --items prompts --top 12         # "What made sense at the time" questions, top-rated first
pmlc register-items <ws> --lr LR-05                # a scope of one learning: the findings it cites
pmlc templates <ws> learning-team                  # the blank learning-team-notes.csv
pmlc check-pack <ws> <run>/outputs/learning-team-facilitator.json --strict
pmlc pack <ws> <run>/outputs/learning-team-facilitator.json --format docx   # a Word handout
```

- [wai-wad](../commands/wai-wad.md) reads the Evidence Links: `document` evidence is work as imagined; `witness_statement`, `log_record` and `recording` are work as done. `--table-item gaps` prints the codes that have both, with the evidence on each side; `--items prompts` prints one question per finding whose justification uses counterfactual wording, top-rated first.
- [templates](../commands/templates.md) `learning-team` writes `learning-team-notes.csv` with only its header, `prompt_id, prompt, team_answer, source`. The team fills it in; the model never writes `team_answer`, and the file is never overwritten.
- [check-pack](../commands/check-pack.md) needs the banner "The team supplies the answers. These are questions, not findings about people." word for word, and refuses an owner or a due date.

In this pack the hindsight wording rules are errors, not warnings: "failed to", "should have" (JC3) and "obviously", "clearly should" (JC4) stop `check-pack` even without `--strict`. The engine's prompts quote the export's own counterfactual words only in their `why` line, with the reason recorded.

## What you get

`learning-team-facilitator.html` and `.md`, and with `--format docx` a Word handout for the room:

- **About this session:** the banner, read aloud at the start.
- **Work as imagined and work as done:** the codes in scope with both kinds of evidence, and the evidence on each side.
- **Questions for the team:** 4 to 12 "What made sense at the time …?" questions, each citing its finding.
- **Session plan:** Minutes, Activity and Purpose, adding up to 60 to 90 minutes: ground rules, the job as it normally goes, the questions, a pause to let the answers soak, and the team's own ideas.
- **Notes for the facilitator:** 3 to 6 points after Conklin's learning teams: the workers are the experts, learn first and fix later, ask about normal work, write the team's own words.
- `learning-team-notes.csv`, blank below its header, for the team's answers.

## Worked example (Hazira)

`wai-wad` found 94 codes with linked evidence, 68 of them with both document and work-as-done evidence, 92 findings with both, 210 findings with any work-as-done evidence, and 337 findings whose justification uses counterfactual wording.

The golden pack's scope is one activity, the gasket replacement on condensate meter 310FT01 and its return to service, and the room is a facilitator who did not investigate, mechanical maintenance fitters, an instrument technician, a gas-terminal field operator and a stores clerk. It keeps the 10 seal-job prompts among the 30 top-rated (repeat reseals, locally purchased O-rings, the job plan, testing before return to service) and the 10 gap rows of their codes, from `AJDE 2.7` to `SVIO 2.5`. Its bottom line points to `LR-05` (repeat failures treated as routine) and `LR-02` (return to service without a test to design pressure). The session plan runs 80 minutes.

## Related skills

- [investigator-coach](investigator-coach.md): the investigation's method, evidence gaps and next interviews.
- [safety-committee-guide](safety-committee-guide.md): a discussion guide for the safety committee and workforce representatives.
- [frontline-learning-cards](frontline-learning-cards.md): the learnings as cards the crew keep, once the session is done.
