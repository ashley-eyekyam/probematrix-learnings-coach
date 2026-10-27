# safety-alert

A one-page safety alert for the organisation's other sites and for peer organisations. It says what happened in two or three sentences, why it matters to the reader, the one to three priority-1 learnings from the Learnings Register, what to check now, two questions for the crew and a role to contact. The alert carries a grade (alert, notice or information) and a mode (internal, sister-site or industry), and it fits in 400 words, so it works as a Word page, a single slide, an email and an A3 poster.

## What it is for

- "Our other sites need to know about this incident this week: what should they check?"
- A lessons-learned bulletin or flash report, for the site itself, for the organisation's sister sites or for the industry.
- A short alert graded by urgency, so readers know how fast to act on it.

The alert points at conditions, never at people. It names a role to contact, never a name, a telephone number or an address, and it carries no owner, due date or sign-off: the `no-owner-due` rule makes any `owner` or `by_when` a problem even without `--strict`. Every learning in it must be priority 1 in the register (rule `alert-priority-1`).

## How to start it

- "Write a safety alert for our other terminals from this ProbeMatrix investigation."
- "We need a lessons-learned bulletin for the industry from this export, graded by urgency."
- "Make the alert a single slide for the morning meeting and a poster for the noticeboard."

## What it needs

- The workspace and the Learnings Register (`<run>/outputs/learnings-register.json`). The alert is always written from the register, never from findings alone; build the register first if it is missing.
- One answer from the user: who the alert is for. `internal` is the site and the teams around it; `sister-site` is the organisation's other sites; `industry` is other organisations. The answer is the pack's `mode`.
- The grade comes from the register's `urgency` field when it is filled for the chosen learnings (`grade_source: "register urgency"`). When it is not, the engine suggests a grade from priority and transferability, the skill asks the user one question, and the pack records `grade_source: "chosen by the user"`.

## Engine commands and flags

```bash
pmlc alert-grade <ws> --register <run>/outputs/learnings-register.json
pmlc register-items <ws> --lr LR-01 --lr LR-02 --lr LR-03
pmlc check-pack <ws> <run>/outputs/safety-alert.json --strict
pmlc pack <ws> <run>/outputs/safety-alert.json
pmlc pack <ws> <run>/outputs/safety-alert.json --format docx,pptx,email
pmlc pack <ws> <run>/outputs/safety-alert.json --layout poster
```

- [alert-grade](../commands/alert-grade.md) chooses the default learnings (the priority-1 rows, by transferability, then evidence strength, then LR-ID, top 3) and gives the grade and where it came from; `--lr` names other learnings.
- [register-items](../commands/register-items.md) `--lr` prints the chosen learnings as ready `learning` items with their citations; the skill shortens each lesson and keeps its `LR-nn`.
- [check-pack](../commands/check-pack.md) with `--strict` checks the profile: six sections, 400 words at most, priority-1 learnings only, no owners or dates. A pack with no `grade` or `grade_source` gets a `grade-source` warning.
- [pack](../commands/pack.md) `--format pptx` puts the whole alert on one content slide between the title and closing slides, with the citations in the speaker notes; `--layout poster` writes the A3 print page. A `sister-site` alert rendered without `--share external`, or an `industry` alert rendered without `--share public`, is a review copy: every format opens with "Review copy: not for distribution outside the organisation until it is approved and shared with --share external." An `industry` alert is never shared with `--share external`.

## What you get

`safety-alert.html` and `.md`, with the grade as a badge under the title:

1. **What happened**: two or three sentences;
2. **Why it matters to you**: why the same condition can exist at the reader's site;
3. **What we learned**: one to three priority-1 learnings, each with its `LR-nn`;
4. **What to check now**: one to five checks, a hold point marked as such;
5. **Questions for your crew**: two open questions, each with why it matters;
6. **Who to contact**: a role.

## Worked example (Hazira)

`alert-grade` on the Hazira register chose LR-01, LR-02 and LR-03: all three are priority 1, industry-wide and corroborated. The register gives each of them `urgency: alert`, so the alert is graded **alert** from the register's urgency. The pack is `mode: internal`, because the investigation is still in progress and no finding is marked as edited by a person, so it cannot be approved for sharing. It tells how condensate vapour escaped from a seal six days after it was replaced (FND-8C0BB623, EVD-8645), spread for about 46 minutes and ignited at a damaged flameproof light fitting (FND-CCE6F868, EVD-6916). Its four checks start with a hold point: no opened pressure-boundary joint returns to service until a recorded test to design pressure has passed (FND-212DC9B7, EVD-2894). The contact is the site process-safety lead. The pack has 397 words.

## Related skills

- [frontline-learning-cards](frontline-learning-cards.md): cards the crew keep, with warning signs and what good looks like.
- `could-it-happen-here`: a self-assessment each receiving site fills in and returns.
- [board-brief](board-brief.md): the board's assurance questions.
- [learnings-register](learnings-register.md): where the learnings, their priority and their urgency come from.
