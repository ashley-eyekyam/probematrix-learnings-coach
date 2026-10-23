---
name: compliance-crosswalk
description: Maps the learnings of a ProbeMatrix investigation export onto the requirements of a management-system framework - ISO 45001 clauses, OSHA PSM, the 20 CCPS Risk Based Process Safety elements, Seveso III, ICMM critical control management, the Indian regimes or the organisation's own elements from a CSV - showing per requirement whether the register gives evidence here, partly, or the organisation must still show it, all set by the engine from the Learnings Register, never judged. Use when someone with a ProbeMatrix export and its register asks which clauses or elements the learnings speak to, wants a standards crosswalk, an ISO 45001 or RBPS gap view, or a clause-by-clause aid for an audit or a certification visit. Not for audit test points, sampling and evidence requests (use `auditor-assurance-pack`) or writing the learnings themselves (use `learnings-register`).
---

# Compliance Crosswalk

Engine: `PMLC` as in `learnings-coach/references/skill-common.md` §1; this skill needs the `learnings-coach` skill installed alongside it.

Audience: HSE leads, management-system owners and auditors preparing for an audit. The crosswalk is an aid to
assurance: it shows where the learnings give evidence against a framework and what the organisation must still show.
It is never a compliance opinion, and it never says a site conformed or did not.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions; run `PMLC setup`
when only an .xlsx was given). Needs: `workspace` and the register (`<run>/outputs/learnings-register.json`; write
it with `learnings-register` first). Optional: the organisation's `adoption.csv` and `distribution.csv`. Read
`learnings-coach/references/learning-principles.md` (§2 ground every sentence, §4 count honestly).

- **Ask one question: "Which framework?"** Answers: `iso45001`, `psm`, `rbps`, `seveso`, `icmm`, `india`, or the
  organisation's own elements as a company system CSV (columns `id,title`, optional `topics`). Up to three
  frameworks in one pack; one is the usual answer.
- Requirement ids and titles come from `learnings-coach/references/standards-crosswalk.json`. A title marked
  "(unverified)" has not been checked against the primary text.

## Gather

```bash
PMLC crosswalk <ws> --framework iso45001                     # the summary: status and learnings per requirement
PMLC crosswalk <ws> --framework iso45001 --table-item        # one per chosen framework: paste it unchanged
PMLC crosswalk <ws> --framework rbps --table-item
PMLC crosswalk <ws> --system-csv <org-elements.csv> --table-item   # the organisation's own elements instead
PMLC crosswalk <ws> --framework rbps --json                  # rows with evidence_here and cites, for the learnings
```

The register defaults to `<run>/outputs/learnings-register.json` (`--register FILE` for another). Paste each table
item unchanged; never retype a status, add a learning to a row or change "needs organisation evidence". The status
is the engine's: `evidenced here` (a learning's `clauses` names the requirement), `partly` (only the requirement's
topic words match a learning's text) or `needs organisation evidence`. The engine never sets `not applicable`: that
is the organisation's call. When `adoption.csv` or `distribution.csv` has rows, ISO 45001 7.3 and 7.4 and PSM (m)(6)
move up one step and name the file.

Then read the `--json` rows: `evidence_here` gives the learnings per requirement, `cites` their findings. Pick the
`by-element` learnings from the rows where the learning's own text speaks to the requirement; a `partly` match on
one topic word is a lead to read, not a link to copy.

## Write

Write `<run>/outputs/compliance-crosswalk.json` in the shape in `learnings-coach/references/pack-schema.md`. Set
`"scope": {"levels": [1, 2, 3, 4], "min_rating": "top"}`, and name each crosswalk section `crosswalk-<framework>`
(`crosswalk-system` for a CSV); the table item keeps its own id, `crosswalk-<framework>-table`.

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/compliance-crosswalk.json (repository only).

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | Where the learnings give most evidence, and the requirements the organisation must still show, each with its counts from the tables | `bottom_line` | 1–5 |
| 1 | `banner` | About this crosswalk | The fixed banner, word for word (below) | `para` | 1 |
| 2 | `crosswalk-*` | The framework's title | The `--table-item` output for one framework, unchanged; one section per framework | `table` | 1–3 |
| 3 | `by-element` | What the learnings show, requirement by requirement | One `learning` per requirement the learnings speak to most directly (below) | `learning` | 1–12 |
| 4 | `unverified` | Requirements not checked against the primary text | Which rows carry "(unverified)" and what that means (below) | `para` | optional, up to 1 |

The `banner` is one `para` whose `text` is exactly: "Aid to assurance, not a compliance opinion." (`check-pack`
checks it word for word.)

Each `by-element` item is a `learning`:
- `lesson`: what the learning shows about the system the requirement covers, in one sentence;
- `explanation`: the requirement, what the register learning says about it, and what the organisation must still
  show (its own records, not this pack);
- `clauses`: the crosswalk ids it speaks to (`ISO45001-8.1`, `RBPS-management-of-change`);
- `learning`: the register's `LR-nn`; `cites` the learning's top findings and Evidence IDs.

```json
{"kind": "learning", "lesson": "Changes of part went ahead without a change review.",
 "explanation": "RBPS Management of Change: LR-06 shows the procedure existed but was not triggered. The site must show its own change records.",
 "clauses": ["RBPS-management-of-change"], "learning": "LR-06", "cites": ["FND-0003", "EVD-0001"]}
```

In `unverified`, name the frameworks whose rows carry "(unverified)", say the ids and titles were not checked
against the primary text, and that the auditor should confirm them against the current edition.

Describe the gap against the requirement ("the procedure did not require a test"), never a legal conclusion:
`check-pack` treats legal-judgment words (JC5) as errors in this pack. No owners and no due dates.

## If the evidence is thin

Follow `skill-common.md` §6, and:
- **No register:** stop and write it first with `learnings-register`; the crosswalk maps learnings, not findings.
- **Every row says `needs organisation evidence`:** keep the table; it is an honest answer. Write one `by-element`
  learning for the requirement the register comes closest to, and say so in the bottom line.
- **Only verified rows:** leave the `unverified` section out.

## Not covered here

- Audit test points, sampling and evidence requests per clause: `auditor-assurance-pack`.
- The learnings themselves, and the `clauses` column of the register: `learnings-register`.
- Whether the organisation conforms: that is the auditor's and the organisation's judgement.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/compliance-crosswalk.json --strict   # fix every problem it lists
PMLC pack <ws> <run>/outputs/compliance-crosswalk.json                  # -> compliance-crosswalk.html and .md
PMLC pack <ws> <run>/outputs/compliance-crosswalk.json --format docx    # -> a Word copy for the audit file
PMLC pack-xlsx <ws> <run>/outputs/compliance-crosswalk.json --kind table   # -> the crosswalk tables in Excel
```

Offer the docx for the audit file and the Excel view for working through the rows. Tell the user how many
requirements per framework the register gives evidence for (`evidenced here` and `partly`), how many the
organisation must still show, and the three `by-element` learnings that speak most directly to a requirement.
