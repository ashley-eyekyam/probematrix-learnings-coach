# Output style

## Default format

Skills that produce a learning pack write JSON (`pack-schema.md`) and render it with `pmlc.py pack` to a self-contained HTML page (the primary deliverable) and generated Markdown, one pack per deliverable, in `<run>/outputs/`. `learnings-register` keeps its own register formats (JSON, .xlsx, .md) and `organisation-learning-map.html`. Convert to .docx, .pdf, .pptx or .xlsx only when the user asks, using whatever document tools the host provides. `pmlc.py register-xlsx` writes the Learnings Register spreadsheet and `pmlc.py dashboard` writes the HTML learning map.

## Every document

1. Title: audience + incident ("Supervisor Coach: Gas terminal fire, 2020").
2. Status line from `learning-principles.md` §5.
3. Bottom line first: the three to five things this audience must take away.
4. Body: the skill's own structure.
5. Evidence trail: Finding IDs and Evidence IDs inline in square brackets, e.g. `[FND-82761CC5; EVD-4052]`.
6. Footer, verbatim:

> Generated with ProbeMatrix Learnings Coach (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com

## Reusable blocks

In a pack these are the `card`, `question` and `test_point` item kinds. A learning written as a one-sentence lesson with its explanation is the `learning` kind.

**Learning Card** (one per learning, fits one page)
- Title (a plain statement, not a slogan)
- What happened (two or three sentences, roles only)
- Why it made sense at the time
- Warning signs to notice
- What good looks like
- Questions for discussion (three)
- Evidence trail

**Learning Brief paragraph**: lesson in one sentence → why it matters here → what changes for this audience → evidence trail.

**Toolbox talk** (five minutes): opening question → the story in 90 seconds → two warning signs → one thing to do differently tomorrow → one question to the crew.

**Board question**: the question → why it matters (one line) → what good assurance evidence would look like.

**Audit test point**: requirement or expectation → what to sample → evidence of conformity → red flags seen in this investigation.

## Hierarchy of controls (for recommendations)

elimination → substitution → engineering → administrative (procedures, checks, permits) → training/awareness → PPE. Name the tier on every recommendation. If the only fix offered is administrative or training, say why a stronger one is not available.

## Leading indicators

Measurable, forward-looking, and owned by the audience reading it: e.g. "% of pressure-boundary jobs released with a documented design-pressure test", "time from confirmed gas release to first isolation in drills", "overdue critical PM notifications older than 30 days".

## Converted files

When converting a pack to .pdf or .docx, blank the author field (and the creator and last-modified-by properties) so the file carries no personal name.
