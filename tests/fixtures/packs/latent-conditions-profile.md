# Latent Conditions Profile: Synthetic pump fire, 2024

**DRAFT**

Review: draft · Classification: internal · Version 1.0

Draft because: no finding is marked as edited by a person

*Learning purposes: not a statutory document · Learnings drafted by an AI agent from AI-assisted findings*

*About 1 min read*

**Audience:** Corporate HSE and top management

**Incident:** Synthetic pump fire · 2024-03-20

## Data quality and limits

- The prefixes AB, OR, PE and SV are not in hfacs-codes.json; the profile keeps each finding at the level the export gives.

## Bottom line

- Two of the four findings (50.0%) sit at levels 3 and 4. [FND-0002; FND-0003]
  *Language check JC8 accepted: the level 3 and 4 share is share\_l34 from hfacs-profile, counted from the export*
- The spares programme (OR 2.2) feeds the most other factors: 3 links out. No code recurs. [FND-0003]

## Where the findings sit

| Level | Subcategory | Prefix | Top rated | Other | Cites |
|---|---|---|---|---|---|
| L1 | Errors | AB | 0 | 1 | FND-0001 |
| L2 | Technological Environment | PE | 0 | 1 | FND-0004 |
| L3 | Supervision Inadequate | SV | 1 | 0 | FND-0002 |
| L4 | Resource Management | OR | 1 | 0 | FND-0003 |

Sources: [FND-0001; FND-0002; FND-0003; FND-0004]

## Factors that feed the most others

| Code | Name | Links out | Links in | Cites |
|---|---|---|---|---|
| OR 2.2 | Spares Programme Failure | 3 | 0 | FND-0003; FND-0001; FND-0004 |
| SV 1.4 | No Guidance Provided | 1 | 1 | FND-0002; FND-0003; FND-0001 |
| AB 1.1 | Step Omitted | 0 | 2 | FND-0002; FND-0003; FND-0001 |
| PE 2.1 | Alarm Not Configured | 0 | 1 | FND-0004 |

Sources: [FND-0001; FND-0002; FND-0003; FND-0004]

## Supervision and organisation

For one incident these counts describe this investigation only. They are not rates, trends or a benchmark.

Two of the four findings (50.0%) sit at levels 3 and 4: one supervision finding and one organisational one. [FND-0002; FND-0003]

*Language check JC8 accepted: the level 3 and 4 share is share\_l34 from hfacs-profile, counted from the export*

## Latent conditions

**Learning:** Seals were bought with no approved specification to buy against. [FND-0003; FND-0002; EVD-0003]

The spares programme feeds the most other factors in the export (OR 2.2, 3 links out), down to the missing return-to-service check and the restart [EVD-0003].

*(evidence: corroborated; learning: LR-01)*

## What this profile cannot tell you

The counts show how often the investigation coded a factor and named a link, not how much each one contributed. Four findings are too few to show a pattern. [FND-0001; FND-0004]

---

This pack cites 2 of 2 relevant findings.

2 of 2 top-rated relevant findings cited.

> Generated with ProbeMatrix Learnings Coach v2.0.0a6 (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
