# could-it-happen-here

A "could it happen here?" self-assessment for the organisation's other sites, for their HSE managers and advisers. Each transferable learning in the Learnings Register becomes one self-check: the condition to look for, the records or observations that would show it, and where to look. The engine then writes a blank return template for each site, and reads the returns back into a view of coverage and conditions that never ranks sites.

## What it is for

- "Could this incident happen at our other sites?"
- A checklist each sister site works through against its own records and plant, looking for the conditions behind the incident rather than a repeat of the event.
- Bringing several sites' answers together, to see which learnings each site has assessed and which conditions sites found present or partly.

The pack opens with the fixed line "A self-assessment for each site. Results show coverage and conditions, never a ranking of sites." It holds no answer, site name, assessor, score, owner or date: the sites fill those in on their returns, and the `no-owner-due` rule makes any `owner` or `by_when` a problem in this pack even without `--strict`.

## How to start it

- "Using this ProbeMatrix export and our learnings register, could this happen at our other three terminals? Give each site a self-check to fill in."
- "Turn the transferable learnings into a sister-site self-assessment."
- "The sites have sent their could-it-happen-here returns back. Bring them together."

## What it needs

- The workspace and the Learnings Register (`<run>/outputs/learnings-register.json`). With no register, the coach writes it first.
- The self-checks come from the transferable learnings (`transferability` of `other sites` or `industry-wide`): by default every priority-1 one, up to 12, with priority-2 learnings added when there are fewer than 3. The user can name the learnings instead.
- The default scope is HFACS levels 2 to 4.
- This skill's share default is `external`: the pack is meant for other sites. A copy that leaves the organisation needs an approved review with `legal_review: cleared` before `--share external` writes it.

## Engine commands and flags

```bash
pmlc register-items <ws> --transferable
pmlc register-items <ws> --transferable --lr LR-03 --lr LR-07
pmlc check-pack <ws> <run>/outputs/could-it-happen-here.json --strict
pmlc pack <ws> <run>/outputs/could-it-happen-here.json --format docx
pmlc templates <ws> cihh --pack <run>/outputs/could-it-happen-here.json
pmlc consolidate <ws> returns/north.xlsx returns/south.xlsx --pack <run>/outputs/could-it-happen-here.json
```

- [register-items](../commands/register-items.md) `--transferable` prints the learnings whose transferability is other sites or industry-wide, as ready learning items; `--lr` keeps only the learnings named, in that order.
- [check-pack](../commands/check-pack.md) with `--strict` checks the pack against its profile: the banner line (`banner:cihh`), 3 to 12 self-checks and no owners or due dates (`no-owner-due`).
- [templates](../commands/templates.md) `cihh --pack` writes `could-it-happen-here.cihh-template.xlsx`, one row per self-check, with the site, answer, response and assessor cells blank. It never overwrites an existing file. With `--share external` it writes the masked `.external.` copy, after an approved review.
- [consolidate](../commands/consolidate.md) reads the returns into `cihh-consolidated.json` and `cihh-events.jsonl`. It refuses a return made from another version of the pack, a return with no site name, two returns for one site and an answer outside present, partly, absent and n/a; `--keep-going` keeps the good returns.

## What you get

`could-it-happen-here.html` and `.md`, and a Word copy with `--format docx`:

1. **About this self-assessment**: the fixed line;
2. **How to use it**: who fills in the return, the four answers, the response and assessor columns;
3. **Self-checks**: 3 to 12 `self_check` items, each with its condition, what to check, where to look and the register learning (`LR-nn`) as a badge;
4. **After the assessment**: what the organisation does with the returns.

Then, from the engine, the blank return template for each site and, once the returns are back, the consolidated view: for each learning, how many returns assessed it, and for each condition, how many sites found it present or partly. The view lists which learnings each site answered, and nothing that ranks or scores a site.

## Worked example (Hazira)

All 25 Hazira learnings are transferable and 11 are priority 1, so the pack holds 11 self-checks, LR-01 to LR-12 without LR-04 (priority 2). They run from a pressure-boundary seal fitted without a written specification (LR-01; FND-82673283, EVD-8645) and work returned to service without a test to design pressure (LR-02; FND-9174A5B0, EVD-2894), through an emergency plan with no isolation criteria or standing authority (LR-07; FND-82761CC5, EVD-4052) and isolation valves that can be closed only by hand inside the release area (LR-09; FND-05841EDA, EVD-3932), to control-room staff with no defined qualification (LR-12; FND-337CB67F, EVD-5634). Each condition is written so another site can recognise it in its own plant, without the incident site's equipment tags or times. The pack stays a draft: the Hazira export is still in progress, so it cannot be shared outside the organisation.

## Related skills

- [safety-alert](safety-alert.md): the one-page alert sent to the other sites first (`sister-site` mode); this self-check is what each receiving site fills in and returns.
- [top-management-brief](top-management-brief.md): the executive decisions on transferring the learning across the organisation.
- [learnings-register](learnings-register.md): the register the self-checks are drawn from, with each learning's transferability and priority.
- [frontline-learning-cards](frontline-learning-cards.md): cards the crews keep, once a site has found a condition.
