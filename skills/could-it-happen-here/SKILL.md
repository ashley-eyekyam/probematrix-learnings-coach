---
name: could-it-happen-here
description: Turns the transferable learnings of a ProbeMatrix investigation export into a "could it happen here?" self-assessment for the organisation's other sites - one self-check per learning, each with the condition to look for, the records or observations that would show it and where to look, written without the incident site's tags, times or names - and hands each site a blank return template to fill in (present, partly, absent or n/a, with the site's response and the assessor's role), then consolidates the returns into a view of coverage and conditions that never ranks sites. Use when someone has a ProbeMatrix export and a Learnings Register and asks whether the incident could happen at their other sites, wants a sister-site self-assessment or checklist, or needs the returns from several sites brought together. Not for a short alert to send other sites first (use `safety-alert`) or the executive decisions on transferring the learning (use `top-management-brief`).
---

# Could It Happen Here?

Audience: HSE managers and advisers at the organisation's other sites (`sister-sites-hse`, tier T3). The pack asks
each site to look for the conditions behind the incident in its own plant. It finds nothing about any site: the sites
supply the answers, and the consolidated view shows coverage and conditions, never a ranking of sites.

## Before you start

Engine: `PMLC` as defined in `skill-common.md` §1 (needs the `learnings-coach` skill installed alongside it).

- Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions).
- Needs: **workspace** and **register** (`<run>/outputs/learnings-register.json`). With no register, run
  `learnings-register` first: the self-checks are drawn from its transferable learnings.
- Read `learnings-coach/references/learning-principles.md`: count learnings, not finding instances, and keep the
  learning a system condition, never a person's act.
- This skill's `share_default` is `external`: the pack goes to other sites. A copy that leaves the organisation needs
  an approved review (below, and `skill-common.md` §7).

## Gather

```bash
PMLC register-items <ws> --transferable                 # the learnings whose transferability is other sites or industry-wide
PMLC register-items <ws> --transferable --lr LR-03 --lr LR-07   # only the learnings the user names, in that order
```

- **Choose the learnings.** By default, every **priority-1** transferable learning, in register order, up to 12. With
  fewer than 3, add priority-2 learnings, `industry-wide` before `other sites`, until there are 3. When the user names
  learnings, use `--lr` and keep their order. On Hazira all 25 learnings are transferable and 11 are priority 1.
- For each chosen learning, read its `lesson`, `explanation` and cites, and the justification of the findings it
  cites. The self-check asks whether the **same condition** exists at another site, not whether the same event did.

## Write

Pack `<run>/outputs/could-it-happen-here.json` (shape: `learnings-coach/references/pack-schema.md`),
`"scope": {"tiers": [], "levels": [2, 3, 4], "tags": []}`.

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | Why the sites should check, and the conditions that matter most, one line each | `bottom_line` | 1–3 |
| 1 | `banner` | About this self-assessment | Exactly "A self-assessment for each site. Results show coverage and conditions, never a ranking of sites." | `para` | 1 |
| 2 | `how-to-use` | How to use it | Who fills in the return, the four answers, the response and assessor columns, and the date the organisation sets for returns (never a date written here) | `para` | 1–2 |
| 3 | `self-checks` | Self-checks | One per chosen learning, in the chosen order: `condition`, `evidence_to_check`, `look_in`, `lr_id`, `cites` | `self_check` | 3–12 |
| 4 | `after-assessment` | After the assessment | What the organisation does with the returns: the consolidated view of coverage and conditions, never a ranking | `para` | 1–2 |

**The self-check** (`self_check`, `pack-schema.md`):
- `condition`: the condition to look for, as one plain sentence a site can recognise in its own plant ("A
  pressure-boundary part is fitted without a written specification"). Write it **site-neutral**: no equipment tag,
  time, date, place or role that belongs to the incident site.
- `evidence_to_check`: the records or observations that would show the condition (work orders, test records,
  the emergency plan, a walk of the area). A site can check it in a day or two.
- `look_in`: where to look (the system, file or area), short.
- `lr_id`: **always**, the register learning (`LR-nn`). The template, the returns and the consolidated view key on it.
- `cites`: the findings and evidence of that learning that show the condition (a few, from its `finding_ids` and
  `evidence_ids`; never a finding the learning does not hold).

```json
{"kind": "self_check", "id": "check-lr-02", "lr_id": "LR-02",
 "condition": "Pressure-boundary work goes back into service without a test to design pressure.",
 "evidence_to_check": "Recent seal or gasket jobs on pressure equipment each have a test record that names the test pressure.",
 "look_in": "Work orders, test certificates and the return-to-service procedure", "cites": ["FND-…", "EVD-2894"]}
```

- **No answers, no sites, no scores (D7).** The pack holds no `answer`, site name, assessor or score; the sites fill
  those in on the template. `no-owner-due` makes any `owner` or `by_when` a problem even without `--strict`.
- **The incident's facts stay in the cites.** Do not retell the event in each self-check; the bottom line may say in
  one sentence what happened, with its cites.

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/could-it-happen-here.json (repository only)

## If the evidence is thin

- **No transferable learning** (every learning is `same site`): say so to the user and stop; the sites have nothing
  to check. Suggest `safety-alert` for an internal alert instead.
- **Fewer than 3 learnings** after the priority-2 step: add the `same site` learnings whose condition another site
  could still hold, and say in `limits` why each was added.
- **A learning with no finding that shows the condition:** leave it out and say so in `limits`.
- `skill-common.md` §6 covers the rest.

## Not covered here

- A short alert for other sites before the self-assessment: `safety-alert`.
- The executive decisions on transferring the learning across the organisation: `top-management-brief`.
- Any site's answer, response or assessor: the site's own, on its return. The coach never fills a return in.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/could-it-happen-here.json --strict
PMLC pack <ws> <run>/outputs/could-it-happen-here.json
PMLC pack <ws> <run>/outputs/could-it-happen-here.json --format docx   # the Word copy for each site
PMLC templates <ws> cihh --pack <run>/outputs/could-it-happen-here.json   # the blank return template
PMLC consolidate <ws> <return.xlsx> --pack <run>/outputs/could-it-happen-here.json   # when the returns are back
```

- **The return template** (`could-it-happen-here.cihh-template.xlsx`) has one row per self-check. Each site fills in
  its name (B1), and for each row the answer (`present`, `partly`, `absent` or `n/a`), its response and the
  assessor's role. Tell the user to send one copy to each site and to keep the pack unchanged until the returns are
  back: a return made from another version of the pack is refused.
- **Consolidate** reads every return (`PMLC consolidate <ws> <return.xlsx> [<return.xlsx> …] --pack <pack>`, with
  `--keep-going` to keep the good returns when one is faulty) into `cihh-consolidated.json`: per learning, how many
  returns assessed it, and per condition, how many sites found it present or partly. The view shows coverage and
  conditions and never ranks or scores a site.
- **Other sites outside the organisation** (a sister company, a contractor): the masked copy and template need an
  approved review with `legal_review: cleared`, then `--share external` on both `pack` and `templates cihh`
  (`skill-common.md` §7). A person signs off; the coach never runs `sign-off`.
- Tell the user how many self-checks the pack holds and which learnings they come from.
