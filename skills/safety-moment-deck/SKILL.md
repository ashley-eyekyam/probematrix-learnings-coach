---
name: safety-moment-deck
description: Turns a ProbeMatrix investigation export into a short safety moment for session leaders - supervisors, shift in-charges and trainers who run a ten-minute shift-start or toolbox session - as a 3 to 6 slide deck and a one-page poster in the style of a process safety beacon - what happened, did you know, what you can do and questions for the crew - with optional narration and captions for a short video. Use when someone has a ProbeMatrix export and its Learnings Register and wants a safety moment, a short slide deck for a shift briefing, a beacon-style poster or a one-minute narrated clip about the event. Not for cards and toolbox talks the crew keep (use `frontline-learning-cards`), a whole training module with assessment (use `training-designer`) or the supervisors' own checks, hold points and coaching scenarios (use `supervisor-coach`).
---

# Safety Moment Deck

Audience: session leaders (`session-leaders`, tier T2): the supervisor, shift in-charge or trainer who stands in
front of a crew for ten minutes. The crew (T1) hear it. The deck is the **delivery format** for one session;
`frontline-learning-cards` holds the cards the crew keep.

## Before you start

Engine: `PMLC` as defined in `skill-common.md` §1 (needs the `learnings-coach` skill installed alongside it).

- Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions).
- Needs: **workspace** and **register** (`<run>/outputs/learnings-register.json`, checked with
  `check-register --strict`). Optional: **frontline-learning-cards** (`<run>/outputs/frontline-learning-cards.json`).
- Read `learnings-coach/references/learning-principles.md`, and the Learning Card and toolbox talk blocks in
  `learnings-coach/references/output-style.md`: the same plain words, roles only, no blame.
- **Reuse the cards when they exist.** When `frontline-learning-cards.json` is in outputs, build the session from
  its cards: take the same `LR-` IDs (`learning: "LR-nn"` on each item), the same story and the same warning
  signs, so the crew hear in the session what their cards say. Take no learning the cards left out.

## Gather

```bash
PMLC register-items <ws> --lr LR-01 --lr LR-02 --lr LR-05   # the chosen learnings in full (your LR ids)
PMLC facts <ws>                                          # the incident, its date and the headline numbers
```

- **Choose one story.** A safety moment carries one event thread and 1 to 3 learnings a crew can notice or act on
  during work (a warning sign, a test that must not be skipped, a moment to stop and ask). With the cards, pick
  them from the cards' `LR-` IDs; without, from the register entries whose `audiences` name crews or
  technicians, priority 1 first (`learnings-register.md` lists them).
- Read the cited findings' justifications for the facts in "What happened" and "Did you know?". Every fact cites
  the finding or evidence it comes from.

## Write

Pack `<run>/outputs/safety-moment-deck.json` (shape: `learnings-coach/references/pack-schema.md`),
`"scope": {"levels": [1, 2]}` (acts and conditions at the sharp end; a level 3 or 4 cite may explain the trap).

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | What the crew should take away, one line each; `learning` = the LR id | `bottom_line` | up to 3 |
| 1 | `what-happened` | What happened | The story in 2 to 3 sentences, in the crew's words, cited | `para` | 1–2 |
| 2 | `did-you-know` | Did you know? | One surprising, cited fact from the evidence each (a time, a gap, a design limit) | `para` | 1–3 |
| 3 | `what-you-can-do` | What you can do | Actions in the crew's own control; `when` = the moment it applies; `learning` = the LR id | `check` | 2–5 |
| 4 | `questions` | Questions for the crew | Open questions the leader asks; `why` = the cited reason; `answer` = what a good answer covers (speaker notes only) | `question` | 2–4 |
| 5 | `script` | Narration | One short clip: `segments` of visual, narration and seconds, `on_screen` captions | `script` | optional, up to 1 |

- **Bottom line**: 1 to 3 points, each a line the crew can repeat ("No specification, no fit").
- **What you can do** stays inside the crew's control. The organisation's fixes belong to `supervisor-coach` and
  `manager-coach`; never close with "be more careful" or "stay vigilant".
- **Questions** ask about this crew's own work ("Which job on our unit ends without a test we can show?"), never
  "who was at fault". A good answer goes in `answer`, which stays in the speaker notes.
- **Script** (optional): a clip of about one minute, 3 to 6 segments, `channel` = `video` (or `pa` for a
  public-address reading). The narration is what is said aloud, so it carries no IDs; cite in each segment's
  `cites`. Without a script, the `srt` and `narration` formats write nothing.
- No owners, due dates or sign-off (`no-owner-due`); roles only, no names.

```json
{"kind": "check", "text": "Before you hand back, ask for the written test pressure and the witness.",
 "when": "before return to service", "learning": "LR-02", "cites": ["FND-…"]}
{"kind": "question", "question": "Which job on our unit ends without a test we can show?",
 "why": "The joint went back into service with no recorded test [FND-…].", "answer": "…", "learning": "LR-02"}
{"kind": "script", "id": "moment-clip", "title": "…", "channel": "video", "cites": ["FND-…"],
 "segments": [{"visual": "…", "narration": "…", "seconds": 15, "on_screen": "…", "cites": ["FND-…"]}]}
```

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/safety-moment-deck.json (repository only)

## If the evidence is thin

- **No frontline cards:** build from the register's crew learnings; say in `limits` that the session is not
  paired with cards, and suggest `frontline-learning-cards` as the next step.
- **Few crew learnings:** one learning, two checks and two questions are a valid deck; do not promote a manager's
  fix into a crew action.
- **No clip wanted:** leave the `script` section out.
- `skill-common.md` §6 covers the rest.

## Not covered here

- Cards and five-minute toolbox talks the crew keep: `frontline-learning-cards`.
- A training module, scenarios and an assessment: `training-designer`.
- The supervisors' own checks, hold points and coaching scenarios: `supervisor-coach`.
- The delivery record itself: `distribution.csv` (below).

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/safety-moment-deck.json --strict --register <run>/outputs/learnings-register.json
PMLC pack <ws> <run>/outputs/safety-moment-deck.json
PMLC pack <ws> <run>/outputs/safety-moment-deck.json --format pptx --layout poster   # the deck and the poster
PMLC pack <ws> <run>/outputs/safety-moment-deck.json --format srt,narration          # captions and narration
```

- **Deck** (`safety-moment-deck.pptx`): the title slide, one slide for the bottom line, one slide per section
  (questions share theirs), then the closing slide: 3 to 6 content slides. Citations, full text and each
  question's good answer are in the speaker notes, for the leader only.
- **Poster** (`safety-moment-deck.poster.html`, A3): the title, the bottom line and the "What you can do" checks,
  for the notice board after the session.
- **Captions and narration**: `safety-moment-deck.<script id>.srt` and `.narration.txt`, written only when the
  pack has a `script` item.
- **Delivery record.** If `<run>/outputs/distribution.csv` does not exist, `PMLC templates <ws> distribution`
  writes it (it never overwrites; add a row for this pack). The organisation fills in the channel, date, leader
  role and attendees; never fill those in yourself.
- Next step: `frontline-learning-cards`, if the crew have no cards yet.
