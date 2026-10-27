---
name: learning-team-facilitator
description: Prepares a learning-team session from a ProbeMatrix investigation export with the user, one question at a time - the scope and who will be in the room, by role - then writes a facilitator pack that sets work as imagined (documents) against work as done (witness statements, logs, recordings), turns the export's counterfactual wording into "what made sense at the time" questions, and gives a 60 to 90 minute session plan, facilitator notes and a blank notes sheet the team fills in. Use when someone with a ProbeMatrix export asks for a learning team, a work-as-done or work-as-imagined session, a learning review with the crew, or questions to ask the people who do the job rather than findings about them. Not for coaching the investigation method or the next interviews (use `investigator-coach`), for the safety committee's agenda (use `safety-committee-guide`), or for support to the people affected (use `restorative-response-guide`).
---

# Learning Team Facilitator

Engine: `PMLC` as in `learnings-coach/references/skill-common.md` §1; this skill needs the `learnings-coach` skill installed alongside it.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions; run `PMLC setup`
when only an .xlsx was given). Needs: `workspace` and `wai-wad` (the first Gather line writes `wai_wad.json`).
Optional: the register; when it exists, a scope of one learning uses its `LR-nn` (§2 "Start from the register").
Read `learnings-coach/references/learning-principles.md` (§1: just culture; §1a: hindsight; §1b: learning teams,
Conklin) before you write a question.

**A learning team asks; it never finds.** The team are the experts on their own work. This pack holds questions,
the evidence the questions come from, and a plan for the session. It holds no answer, no judgement of a person and
no fix: the team supplies those, in its own words, in the session.

## Gather

This skill asks the user **two questions, one per turn**, through the host's question tool where there is one,
otherwise as a numbered list. Each offers the suggestions in `skill.json`, the recommended one first, and the user's
own words are always allowed:

1. **What is the session's scope?** One activity the work-as-done evidence covers (for example the emergency
   isolation, or the job before the event), one cluster (a function), one learning from the register (`LR-nn`), or
   unknown (the top prompts across the export).
2. **Who will be in the room?** Roles only, never names: the people who do the work, one facilitator who did not
   investigate, and a supervisor only if the team agrees. The answer becomes the pack's `audience`.

Then run:

```bash
PMLC wai-wad <ws>                                  # writes wai_wad.json; prints the counts
PMLC wai-wad <ws> --table-item gaps                # codes with both document and work-as-done evidence
PMLC wai-wad <ws> --items prompts --top 12         # "What made sense at the time" questions, top-rated first
PMLC wai-wad <ws> --items prompts                  # up to 30, when the scope is narrow and 12 are not enough
PMLC register-items <ws> --lr <LR-nn>              # a scope of one learning: the findings it cites
PMLC templates <ws> learning-team                  # the blank learning-team-notes.csv the team fills in
```

- **Fit the scope.** Keep the gap-table rows and the prompts whose findings belong to the scope: for an activity, the
  findings whose text describes it; for a cluster, the findings that function holds; for a learning, the findings
  its register entry cites. Say in `data_quality` how you chose them.
- **Prompts as printed.** Keep each prompt's `question` opening ("What made sense at the time about …"), its `why`,
  its `cites` and its `lint_ok`. You may shorten the topic after the colon; never add a judgement to it.
- `templates` never overwrites an existing notes file. Its header is `prompt_id, prompt, team_answer, source`; the
  team writes every answer and its source. **Never fill in `team_answer`**, not even as an example.

## Write

Write `<run>/outputs/learning-team-facilitator.json` in the shape in `learnings-coach/references/pack-schema.md`.

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/learning-team-facilitator.json (repository only).

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | What the session is for, where documents and accounts differ most in the scope, and where to start; each cites | `bottom_line` | 1–3 |
| 1 | `banner` | About this session | One `para` whose `text` is exactly the learning-team banner below | `para` | 1 |
| 2 | `wai-wad` | Work as imagined and work as done | The `--table-item gaps` table, cut to the rows in scope, with its `row_cites` and `lint_ok` | `table` | 1 |
| 3 | `prompts` | Questions for the team | The prompts in scope, as printed by `--items prompts` | `question` | 4–12 |
| 4 | `session-plan` | Session plan | One table, columns Minutes, Activity and Purpose; whole minutes that add up to 60–90 | `table` | 1 |
| 5 | `facilitator-notes` | Notes for the facilitator | How to run the session, after Conklin | `check` | 3–6 |

**The banner.** Its `text` is exactly, character for character:
`The team supplies the answers. These are questions, not findings about people.`
`check-pack` reports it missing (rule `banner:learning-team`; `BANNERS` in `pack/profiles.py`).

**The session plan** (60 to 90 minutes in all; a test adds them up):
- open with the ground rules and the banner read aloud;
- walk through the work as it is normally done before the day of the event;
- work through the prompts, one at a time;
- a soak: a pause, then what surprised the team;
- close with what would make the job easier to do safely, as the team's ideas, not decisions.
Cite in `row_cites` the findings a row's prompts or gap rows come from; an opening or a break row cites nothing.

**Facilitator notes** (`check` items, after Conklin, `learning-principles.md` §1b): the workers are the experts;
learn first and fix later, with the fixes in a second meeting after a soak; ask how the work normally goes, not only
about the event; write the team's own words; the facilitator did not investigate and judges no one.

**Language.** JC3 (hindsight: "failed to", "should have") and JC4 ("obviously", "clearly should") are errors in this
pack, even without `--strict`. The engine's `why` lines quote the export's own counterfactual words and carry a
`lint_ok`; keep it, and never repeat those words in your own text.

**Never** an `owner`, a `by_when` or a date to act by (rule `no-owner-due`), and never a name: roles only.

## If the evidence is thin

Follow `skill-common.md` §6, and:
- **No work-as-done evidence** (no witness statement, log or recording): `wai-wad` says so in a note and the gaps
  table is empty. Do not invent a comparison: keep the table with one row saying the export holds no work-as-done
  evidence, cite nothing in it, and make the session's first activity collecting the team's account of the work.
- **Fewer than 4 prompts in scope:** widen the scope with the user (one more question), or take the next prompts
  from `--items prompts`; say which in `data_quality`.
- **No counterfactual wording:** ask "How does this job normally go?" about the gap rows' findings instead, citing them.

## Not covered here

- The investigation method, the next interviews and the evidence still to collect: `investigator-coach`.
- The safety committee's agenda and the workforce reps' questions: `safety-committee-guide`.
- Support for the people affected and what they need: `restorative-response-guide`.
- The team's answers: the team writes them in `learning-team-notes.csv`; this pack never holds them.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/learning-team-facilitator.json --strict   # fix every problem it lists
PMLC pack <ws> <run>/outputs/learning-team-facilitator.json                  # -> .html and .md
PMLC pack <ws> <run>/outputs/learning-team-facilitator.json --format docx    # -> a Word handout for the room
```

Tell the user the scope and the roles in the room, how many gap rows and prompts the pack holds, that the session
runs 60 to 90 minutes, and that `learning-team-notes.csv` is for the team to fill in: the model never writes an answer.
