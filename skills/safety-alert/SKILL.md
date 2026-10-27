---
name: safety-alert
description: Writes a one-page safety alert from a ProbeMatrix investigation export and its Learnings Register for other sites and peer organisations - what happened in two or three sentences, why it matters to the reader, the one to three priority-1 learnings, what to check now, two questions for the crew and a role to contact - graded alert, notice or information from the register's urgency (or the user's choice), in one of three modes (internal, sister-site or industry), and rendered as Word, a one-slide deck, an email and an A3 poster. Use when someone has a ProbeMatrix export and asks for a safety alert, a lessons-learned bulletin, a flash report for other sites, a sister-site or industry alert, or "what should our other sites check now". Not for the cards the crew keep (use `frontline-learning-cards`), the receiving sites' self-assessment (use `could-it-happen-here`) or the board's questions (use `board-brief`).
---

# Safety Alert

Audience: other sites and peer organisations (`other-sites`): HSE leads, operations and maintenance managers and their
crews at the organisation's other sites, and, in `industry` mode, peer operators. The alert is short (400 words at
most) and points at conditions, never at people.

## Before you start

Engine: `PMLC` as defined in `skill-common.md` §1 (needs the `learnings-coach` skill installed alongside it).

- Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions).
- Needs: **workspace** and the **register** (`<run>/outputs/learnings-register.json`). An alert carries priority-1
  learnings from the register, so build the register first (`learnings-register`) if it is missing.
- Read `learnings-coach/references/learning-principles.md`.
- **Ask once: "Who is the alert for?"** The answer sets the pack's top-level `mode`:
  - `internal`: this site and the teams around it (the default, and the only mode for a draft);
  - `sister-site`: the organisation's other sites, shared with `--share external` after an approved review;
  - `industry`: other organisations, shared with `--share public` after an approved review.
- A `sister-site` or `industry` pack rendered without that `--share` is a **review copy**: every format opens with
  "Review copy: not for distribution outside the organisation until it is approved and shared with --share
  external." The pack file is not changed. An `industry` pack is never shared with `--share external`.

## Gather

```bash
PMLC alert-grade <ws> --register <run>/outputs/learnings-register.json   # the default learnings and the grade
PMLC register-items <ws> --lr LR-01 --lr LR-02 --lr LR-03                 # the chosen learnings as ready items
```

- **The learnings.** `alert-grade` chooses the priority-1 learnings by transferability (industry-wide, then other
  sites, then same site), then evidence strength, then LR-ID, top 3. If the user names other learnings, pass each
  with `--lr` to both commands; a learning that is not priority 1 gets a note, and `check-pack` refuses it.
- **The grade.** With grade_source "register urgency", write the grade it prints and
  `"grade_source": "register urgency"`. With `suggested` (the register has no `urgency` for them), ask **one** question:
  "Grade this alert as alert, notice or information? The engine suggests <grade> (<the rule it prints>)." Write the
  user's answer as `grade` and `"grade_source": "chosen by the user"`. Never write `suggested` into the pack.
- **No priority-1 learning:** `alert-grade` says "no priority-1 learning: choose with --lr". Tell the user the
  register has no learning an alert should carry, and stop unless they choose one.
- For `what-happened`, read the register's `context` of the chosen learnings and the cited findings; for the checks,
  their `recommendations` and `barrier`.

## Write

Pack `<run>/outputs/safety-alert.json` (shape: `learnings-coach/references/pack-schema.md`),
`"scope": {"tiers": [], "levels": [], "tags": []}`, with the top-level `mode`, `grade` and `grade_source`.

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | What every reader must take away, one line each | `bottom_line` | 1–3 |
| 1 | `what-happened` | What happened | Two or three sentences: the event and its consequence, in plain words, no names | `para` | 1 |
| 2 | `why-it-matters` | Why it matters to you | Why the same condition can exist at the reader's site (the learnings' transferability) | `para` | 1 |
| 3 | `learnings` | What we learned | One per chosen learning: a shortened `lesson`, `learning: "LR-nn"`, cites | `learning` | 1–3 |
| 4 | `checks` | What to check now | Concrete checks a site can make this week; `hold_point: true` for a stop-and-check | `check` | 1–5 |
| 5 | `crew-questions` | Questions for your crew | `question` and `why`; open questions about their own work | `question` | 2 |
| 6 | `contact` | Who to contact | A role only ("the site process-safety lead"), never a name, number or address | `para` | 1 |

- **400 words at most** for the whole pack (`max_words`): shorten the register's lessons, keep their meaning, and
  keep `learning: "LR-nn"` on each. The register's explanation is optional and short.
- **Priority 1 only.** `alert-priority-1` makes a `learnings` item whose `learning` is not priority 1 a problem.
- **No owner, date or sign-off (D7).** `no-owner-due` makes any `owner` or `by_when` a problem even without
  `--strict`. A check says what to look at, never who does it or by when.
- **Roles only, no blame.** `what-happened` names the condition and the work, never a person or a mistake.
- In `sister-site` and `industry` mode write for a reader outside the site: no equipment tags, no internal job or
  notification numbers, no company names (JC9, JC10).

```json
{"pack": "safety-alert", "skill": "safety-alert", "mode": "internal", "grade": "alert",
 "grade_source": "register urgency", "sections": [{"id": "learnings", "heading": "What we learned", "items": [
  {"kind": "learning", "learning": "LR-01", "lesson": "A seal with no specification on file becomes whatever is to hand.",
   "cites": ["FND-…", "EVD-…"]}]}]}
```

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/safety-alert.json (repository only)

## If the evidence is thin

- **No register:** build it with `learnings-register` first; an alert is never written from findings alone.
- **No priority-1 learning:** stop, as in Gather; never promote a learning's priority to fill the alert.
- **A register with no `urgency`:** ask the grade question (Gather); `check-pack` warns `grade-source` when the
  pack has no `grade` or `grade_source`.
- **Fewer than three good checks:** write the ones the evidence supports (one is enough).
- `skill-common.md` §6 covers the rest.

## Not covered here

- Cards the crew keep, with warning signs and what good looks like: `frontline-learning-cards`.
- A self-assessment each receiving site fills in and returns: `could-it-happen-here`.
- The board's assurance questions: `board-brief`.
- Approving or sending the alert: the organisation's review (`skill-common.md` §7), never the coach's.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/safety-alert.json --strict
PMLC pack <ws> <run>/outputs/safety-alert.json
PMLC pack <ws> <run>/outputs/safety-alert.json --format docx,pptx,email   # Word, the one-slide deck, the email
PMLC pack <ws> <run>/outputs/safety-alert.json --layout poster            # the A3 poster for the noticeboard
```

- The deck is one content slide (`pptx_slides: 1`) between the title and closing slides; citations go to the notes.
- **Shared copies** (only after a person has approved the alert, `skill-common.md` §7): a `sister-site` alert is
  rendered with `--share external`, an `industry` alert with `--share public`; until then each format is the review
  copy. The model never runs `sign-off`.
- Tell the user the grade and where it came from, the mode, the learnings it carries and that the alert stays
  internal until it is approved.
