# Output style

## Default format

Skills that produce a learning pack write JSON (`pack-schema.md`) and render it with `pmlc.py pack` to a self-contained HTML page (the primary deliverable) and generated Markdown, one pack per deliverable, in `<run>/outputs/`. The engine writes every other format from the same JSON: `pack --format docx`, `pptx`, `email`, `csv` and the data formats, and `pack --layout cards|field|toolbox|checklist|poster|paper` for print. Which format suits which channel, and each skill's offered formats, are in `skill-common.md` §8. `learnings-register` keeps its own formats: the JSON, `register-md` (.md), `register-xlsx` (.xlsx), `register-render --format docx,email` (Word and email) and the `dashboard` (`organisation-learning-map.html`).

Never rebuild a pack by hand in another tool, and never hand-edit a rendered file: change the JSON and render again, so the status line, footer, citations and checks stay with every copy. There is no PDF format: print the HTML or a print layout to PDF from the browser, or save the .docx as PDF in Word. For a format the engine does not write (such as a spreadsheet of one pack's questions or test points, `PMLC pack-xlsx`), use the engine command first and the host's document tools only when the user asks for something none of them writes.

## Every document

1. Title: audience + incident ("Supervisor Coach: Gas terminal fire, 2020").
2. Status line from `learning-principles.md` §5.
3. Bottom line first: the three to five things this audience must take away.
4. Body: the skill's own structure.
5. Evidence trail: Finding IDs and Evidence IDs inline in square brackets, e.g. `[FND-82761CC5; EVD-4052]`.
6. Footer. It carries the engine's version stamp (`__version__` in `pmlc_lib/__init__.py`), where `aN` stands for the installed alpha number, for example:

> Generated with ProbeMatrix Learnings Coach v2.0.0aN (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com

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

**Toolbox talk** (five minutes): opening question → the story in 90 seconds → two warning signs → one thing to do differently tomorrow → one question to the crew. Write it as one `toolbox` item (`pack-schema.md`): `opening_question`, `story`, `warning_signs` (two), `one_change`, `crew_question`, and an optional `duration`; the page and the Markdown show the five parts in this order.

**Board question**: the question → why it matters (one line) → what good assurance evidence would look like.

**Audit test point**: requirement or expectation → what to sample → evidence of conformity → red flags seen in this investigation.

## Hierarchy of controls (for recommendations)

elimination → substitution → engineering → administrative (procedures, checks, permits) → training/awareness → PPE. Name the tier on every recommendation. If the only fix offered is administrative or training, say why a stronger one is not available.

## Shared copies

A copy for outside the organisation is rendered with `--share external` or `--share public` (see `skill-common.md` §7). It is written beside the internal copy as `<name>.external.html` and `.md` (`.public.` for public; `organisation-learning-map.external.html`, `learnings-register.external.xlsx`), and its handling lines end with `Shared external: identifying details are masked`. Write such a pack without names, company names, tags or one-person role strings in the first place; the masks (`[name]`, `[organisation]`, `[equipment tag]`) are a safety net, and a page full of them reads badly.

## Leading indicators

Measurable, forward-looking, and owned by the audience reading it: e.g. "% of pressure-boundary jobs released with a documented design-pressure test", "time from confirmed gas release to first isolation in drills", "overdue critical PM notifications older than 30 days".

## Converted files

The engine's own files carry no personal name: the .docx and .pptx it writes have no creator and no last-modified-by property, the .xlsx names only the library that wrote it (`openpyxl`), and the email, calendar and data files name no sender, organiser or attendee. Keep it so:

- Saving a .docx or .pptx again in Word or PowerPoint stamps the editor's name as last-modified-by; clear it (File > Info > Inspect Document, or the host's equivalent) before the file leaves.
- When the user asks for a conversion the engine does not make (for example a PDF of the .docx), blank the author, creator and last-modified-by properties of the converted file.
- A converted file keeps the status line, the DRAFT label and the ProbeMatrix footer exactly as the engine wrote them.
