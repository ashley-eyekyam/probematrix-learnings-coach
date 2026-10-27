---
name: safety-committee-guide
description: Produces a discussion guide from a ProbeMatrix investigation export for joint health and safety committees, workforce safety representatives and union safety reps - a plain-language account, the questions the workforce should raise with management, what to look for on site, a concerns log, and how to keep the discussion about systems rather than blame. Use when someone has a ProbeMatrix export and asks for safety committee material, a worker consultation pack, a guide for safety reps, a workforce engagement session or a town-hall discussion on the investigation. Not for the crews' own cards and toolbox talks (use `frontline-learning-cards`).
---

# Safety Committee Guide

Audience: workforce representatives and joint safety committees. They give the workforce a voice, raise
concerns and check that learning reaches the people who do the work. They need a fair account and good
questions.

## Before you start

Engine: `PMLC` as defined in `skill-common.md` §1 (needs the `learnings-coach` skill installed alongside it).

- Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions).
- Needs: **workspace** and **clusters**.
- Read `learnings-coach/references/learning-principles.md`.
- **Start from the register if present.** `PMLC register-items <ws> --tier T1` and `--tier T2` print the
  learnings that reach the workforce as ready items: keep their wording and carry `learning: "LR-nn"`.

## Gather

```bash
PMLC facts <ws>                                          # level counts and l34_share, for section 2
PMLC select <ws> --tier T1 T2 --brief                    # what the workforce and supervisors were involved in
PMLC select <ws> --level 4 --top-rated --brief           # the organisational conditions that mattered most
PMLC select <ws> --relation norm_setter learner challenger --brief   # norms, learning and challenge
PMLC select <ws> --prefix OIC --top-rated --brief        # culture fallback: organisational climate findings
```

- **Culture fallback.** The relation selection is often thin (four findings on the public Hazira sample). When it
  returns fewer than five findings, use the `--prefix OIC` selection (Organisational Climate,
  `learnings-coach/references/hfacs-levels.md` §2) for the culture questions.
- **Where the causes sit.** Read `l34_share` from `PMLC facts <ws>`: the share of findings at levels 3 and 4.
  When it is 0.5 or more, say in section 2 that the analysis places most causes at supervision and organisational
  level, with the figure (e.g. "71% of the findings sit at levels 3 and 4"). Below 0.5, give the figure and say
  where the causes sit instead. Never compute the share yourself.

## Write

Pack `<run>/outputs/safety-committee-guide.json` (shape: `learnings-coach/references/pack-schema.md`),
`"scope": {"tiers": ["T1", "T2"]}`.

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/safety-committee-guide.json (repository only)

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | What the workforce should know, one line each | `bottom_line` | up to 5 |
| 1 | `what-happened` | What happened | Plain language, roles only, about a page | `para` | up to 3 |
| 2 | `system` | What the investigation says about the system | The learnings most relevant to the workforce | `learning` | up to 5 |
| 2 | `system` | What the investigation says about the system | Where the analysis places the causes, from `l34_share` | `para` | 1 |
| 3 | `questions` | Questions to raise with management | Staffing, training, procedures, equipment, authority to stop work, how concerns are handled; `to` = the management role | `question` | up to 10 |
| 4 | `look-for` | What to look for on site | A walk-round prompt list drawn from the conditions in the findings | `check` | up to 10 |
| 5 | `running` | Running the discussion | Ground rules (no names, no blame, focus on conditions) and the anonymity rules (below) | `para` | up to 2 |
| 5 | `running` | Running the discussion | A 60-minute agenda, columns Minutes and Item | `table` | 1 |
| 6 | `concerns-log` | Concerns log | Columns Concern, Condition seen, Location type, Date raised, Response requested (below) | `table` | 1 |
| 7 | `follow-up` | Follow-up | What the committee should ask to see, `when` = "30 days", "60 days" or "90 days" | `check` | up to 6 |
| 8 | `rights` | Committee and representative rights | The rights note (below) | `para` | 1 |

- **Anonymity and confidentiality.** Offer an anonymous route for concerns. Record concerns by topic, not by who
  raised them. Do not name or describe a person so that the crew can tell who it is (a small crew's single
  operator is identifiable by role alone). Minutes and the concerns log go to management without names.
- **Concerns log.** A template the committee keeps. Start it with one row per condition from the findings that
  the workforce may recognise: Concern (the topic), Condition seen (as the findings describe it), Location type
  (the kind of place, such as "metering area", never an equipment tag), Date raised left blank (`""`), and
  Response requested (what the committee asks management for). Cite each row in `row_cites`. The committee adds
  rows for the concerns it hears; never invent a concern the findings do not show.
- **Rights note.** Say that committees and representatives may have statutory rights (for example to
  consultation, to investigation documents, or to inspect after an incident) that this guide does not replace.
  Name a regime only from `learnings-coach/references/jurisdictions.md` for the run's jurisdiction, marking an
  *(unverified)* item as such, and tell the committee to confirm its rights with its own adviser. State no legal
  conclusion.

```json
{"kind": "question", "question": "Who may stop a restart when the test record is missing?", "why": "…",
 "to": "Maintenance manager", "cites": ["FND-…"]}
```

## If the evidence is thin

- **Thin culture selection:** use the `--prefix OIC` fallback above; if that is empty too, keep the culture
  questions to the ones the findings support and add a `gaps` entry.
- **Few conditions for the concerns log:** one row is enough; the committee fills the rest.
- `skill-common.md` §6 covers the rest.

## Not covered here

- Cards and toolbox talks for the crews themselves: `frontline-learning-cards`.
- Management's own decisions and follow-up plan: `manager-coach` and `site-leadership-coach`.
- Terms of reference for a committee, or legal advice on its rights: outside this skill.
- The delivery record: `distribution.csv` (below), not a table in this pack.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/safety-committee-guide.json --strict
PMLC pack <ws> <run>/outputs/safety-committee-guide.json
PMLC pack <ws> <run>/outputs/safety-committee-guide.json --layout checklist   # the walk-round sheet to print
PMLC pack <ws> <run>/outputs/safety-committee-guide.json --format pptx        # slides for the meeting
PMLC pack <ws> <run>/outputs/safety-committee-guide.json --format ics --start YYYY-MM-DD   # only with the user's date
```

- **Walk-round checklist.** `safety-committee-guide.checklist.html` prints the section 4 and 7 checks with a box
  each and a "Checked by (role) / Date / Shift" line per section. Representatives carry it on site; the sheet
  records roles, never names.
- **Follow-up calendar.** Only when the user gives the meeting date: `--format ics --start <that date>` turns the
  30, 60 and 90-day follow-up checks into all-day reminders with no attendees. Never pick the date yourself.
- **Another language.** For a workforce that reads another language, translate through `strings` and have a
  fluent speaker check it (`skill-common.md` §8).

- **Distribution record.** Each committee session is recorded in `<run>/outputs/distribution.csv`: if the file
  does not exist, `PMLC templates <ws> distribution` writes it with one row per pack (it never overwrites; add a
  row for this pack instead). The committee fills in the delivery columns, including `concerns_escalated`;
  never fill them yourself.
- Next step: the committee's follow-up questions go to the role named in each `check`.

For when and how to check that a learning took hold, use `learning-effectiveness-plan`.
