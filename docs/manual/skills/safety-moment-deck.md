# safety-moment-deck

A short safety moment for the people who lead one: supervisors, shift in-charges and trainers running a ten-minute shift-start or toolbox session. It turns the investigation into a deck of 3 to 6 slides and a one-page poster, in the style of a process safety beacon: what happened, did you know, what you can do, and questions for the crew. An optional script adds narration and captions for a one-minute clip.

## What it is for

- "Give me a safety moment on this incident for tomorrow's shift briefing."
- A short slide deck a supervisor can talk through in ten minutes, with the citations and good answers in the speaker notes.
- A beacon-style poster for the notice board after the session.
- A one-minute narrated clip, with subtitles, to open the session.

The deck is the delivery format for one session. The cards the crew keep come from `frontline-learning-cards`; when those cards exist, the deck uses the same learnings (`LR-` ids) and the same story, so the crew hear in the session what their cards say.

## How to start it

- "Make a safety moment from this ProbeMatrix export for our maintenance crews."
- "I need a short deck and a poster for a toolbox session on the seal failure."
- "Turn the frontline cards into a ten-minute session with a short narrated video."

## What it needs

- The workspace and the Learnings Register (`<run>/outputs/learnings-register.json`, passing `check-register --strict`).
- Optional: the frontline Learning Cards (`<run>/outputs/frontline-learning-cards.json`). With them, the session reuses their learnings and story; without them, it is built from the register's learnings for crews and technicians, priority 1 first.
- The default scope is HFACS levels 1 and 2, the acts and conditions at the sharp end; a level 3 or 4 finding may still be cited where it explains the trap.

## Engine commands and flags

```bash
pmlc register-items <ws> --lr LR-01 --lr LR-02 --lr LR-05
pmlc facts <ws>
pmlc check-pack <ws> <run>/outputs/safety-moment-deck.json --strict --register <run>/outputs/learnings-register.json
pmlc pack <ws> <run>/outputs/safety-moment-deck.json
pmlc pack <ws> <run>/outputs/safety-moment-deck.json --format pptx --layout poster
pmlc pack <ws> <run>/outputs/safety-moment-deck.json --format srt,narration
```

- [register-items](../commands/register-items.md): `--lr` (repeatable) prints the chosen learnings as ready items, in full and in the order given.
- [facts](../commands/facts.md) gives the incident, its date and the headline numbers for "What happened".
- [check-pack](../commands/check-pack.md) with `--strict` and `--register` checks the pack against its profile and the register: every `LR-` id must exist there, and no item may carry an owner or a due date (`no-owner-due`).
- [pack](../commands/pack.md) `--format pptx` writes the deck; `--layout poster` the A3 poster; `--format srt,narration` the subtitles and the narration text of the script, and nothing when the pack has no script.

## What you get

`safety-moment-deck.html` and `.md`, and on request:

1. **the deck** (`safety-moment-deck.pptx`): a title slide, one slide for the bottom line (1 to 3 points), one slide per section, and a closing slide with the coverage lines: 3 to 6 content slides. The questions share one slide; each question's good answer, the citations and the full text are in the speaker notes, for the leader only;
2. **the poster** (`safety-moment-deck.poster.html`, A3 landscape): the title, the bottom line and the "What you can do" checks as tiles;
3. **captions and narration** (`safety-moment-deck.<script id>.srt` and `.narration.txt`): only when the pack has a `script` item. They hold the spoken words only, with no IDs.

The sections are: **What happened** (2 to 3 sentences), **Did you know?** (1 to 3 surprising, cited facts), **What you can do** (2 to 5 actions in the crew's own control, each with its moment), **Questions for the crew** (2 to 4) and an optional **Narration** script. The deck never closes with "be more careful": the organisation's fixes belong to `supervisor-coach` and `manager-coach`.

## Worked example (Hazira)

The Hazira deck is built from the frontline Learning Cards and reuses three of their learnings: LR-01 (no specification, no fit), LR-02 (a joint is not proven until it passes a recorded test) and LR-05 (a repeat failure is a warning). "What happened" tells the seal story in three sentences: the 1986 condensate meter's seal was changed on 18 Sep 2020 with a locally bought O-ring because the maker's specification was lost, the system was held only at operating pressure (FND-8C0BB623, FND-212DC9B7, EVD-8645, EVD-2894), and on 24 Sep that seal was the probable source of the release (FND-15279F97). "Did you know?" adds that it was the third seal change on the same meter in about 22 months (FND-69067A1C, EVD-1494). The three checks and three questions follow the same learnings, and a four-segment script gives a one-minute clip ending "No recorded test, no hand-back". The deck has six content slides. Rendered as a draft, because the investigation is still in progress.

## Related skills

- [frontline-learning-cards](frontline-learning-cards.md): the cards and toolbox talks the crew keep; the deck reuses their learnings.
- [training-designer](training-designer.md): a whole training module, with scenarios and an assessment.
- [supervisor-coach](supervisor-coach.md): the supervisors' own checks, hold points and coaching scenarios.
