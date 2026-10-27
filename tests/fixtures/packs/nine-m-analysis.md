# 9M Analysis: Synthetic pump fire, 2024

**DRAFT**

Review: draft · Classification: internal · Version 1.0

Draft because: no finding is marked as edited by a person

*Learning purposes: not a statutory document · Learnings drafted by an AI agent from AI-assisted findings*

*About 3 min read*

**Audience:** Investigators and the teams designing corrective and preventive actions

**Incident:** Synthetic pump fire · 2024-03-20

## Data quality and limits

- One fact came from the organisation at the interview, not from the export: it is in Context supplied by the organisation, uncited.

## Bottom line

- Two of the nine Ms are relevant: Method (M3) and Maintenance (M9). The other seven have no condition in this export. [FND-0002; FND-0003]
- The seals were bought without a specification (M9), and that fed the missing return-to-service guidance (M3): one learning, counted once. [FND-0003; FND-0002]
- Both directions of change are at the engineering tier. No owner or date is set here: the organisation fills them in the blank actions sheet. [FND-0002; FND-0003]

## The nine Ms

| M | Relevance | Conditions | Top subcategory | Findings in the seed | Cites |
|---|---|---|---|---|---|
| M1 Manpower/Mindpower | not relevant | 0 | - | 0 |  |
| M2 Medium | not relevant | 0 | - | 0 |  |
| M3 Method | relevant | 1 | M3.02 Standard Operating Procedures (SOPs) | 1 | FND-0002 |
| M4 Mission | not relevant | 0 | - | 0 |  |
| M5 Measurement | not relevant | 0 | - | 0 |  |
| M6 Management/Money | not relevant | 0 | - | 1 | FND-0003 |
| M7 Machine | not relevant | 0 | - | 2 | FND-0001; FND-0004 |
| M8 Material | not relevant | 0 | - | 2 | FND-0001; FND-0003 |
| M9 Maintenance | relevant | 1 | M9.07 Spare Parts and Inventory Management | 4 | FND-0003; FND-0002; FND-0001; FND-0004 |

Sources: [FND-0001; FND-0002; FND-0003; FND-0004]

## M3 Method

### c-m3-1

**Learning:** The joint went back into service without a test because no procedure asked for one. [FND-0002; EVD-0002]

Subcategory M3.02 Standard Operating Procedures: the procedure index has no return-to-service entry [EVD-0002]. System driver: the spares programme (OR 2.2, level 4) feeds the missing guidance (SV 1.4). Barrier state: absent.

*(+2 supporting; learning: LR-01)*

**Barrier:** Return-to-service leak test [FND-0002; EVD-0002]
- Failure mode: absent: no procedure required it
- State on the day: absent
- Control tier: administrative

*Language check JC6 accepted: the barrier records the control that existed; the change is at the engineering tier*

**Recommendation:** Corrective: interlock the pump restart on a recorded leak test of the disturbed joint. [FND-0002]
- Control tier: engineering
- Leading indicator: Restarts after seal work with a recorded leak test

## M9 Maintenance

### c-m9-1

**Learning:** Seals were bought locally with no specification to buy against. [FND-0003; EVD-0003]

Subcategory M9.07 Spare Parts and Inventory Management: local seals without specification since March 2022 [EVD-0003]. System driver: the spares programme itself (OR 2.2, level 4). Barrier state: absent.

**Barrier:** Spares specification at goods receipt [FND-0003; EVD-0003]
- Failure mode: absent: no specification on file
- State on the day: absent
- Control tier: engineering

**Recommendation:** Preventive: the stores system refuses to receive a pressure-boundary seal without a specification number. [FND-0003]
- Control tier: engineering
- Leading indicator: Seals held at goods receipt for a missing specification

**Q: Which purchase records show when the original seal specification was last used?** [FND-0003]
- Why it matters: It would date the start of the local buying (FND-0003).
- Good evidence looks like: Purchase order history for the seal part number

## Not relevant

| M | Why not relevant | Cites |
|---|---|---|
| M1 Manpower/Mindpower | The technician followed the work order; the gap was the missing procedure (M3) | FND-0001 |
| M2 Medium | No finding points to the work environment |  |
| M4 Mission | No finding points to goals or production pressure |  |
| M5 Measurement | No finding points to measurement or monitoring |  |
| M6 Management/Money | The spares budget is the M9 condition, not counted twice | FND-0003 |
| M7 Machine | The user judged the alarm design out of scope for this review | FND-0004 |
| M8 Material | The seal itself was sound; the gap was buying without a specification (M9) | FND-0003 |

Sources: [FND-0001; FND-0003; FND-0004]

## Conditions that cross Ms

Graph: 2 nodes, 1 links [FND-0003; FND-0002]

- M9 Maintenance: seals bought without a specification → M3 Method: no return-to-service procedure (OR 2.2 feeds SV 1.4)

## Context supplied by the organisation

The site works two 12-hour shifts, and seal changes are done on the day shift (supplied by the HSE lead at the interview).

## Supporting citations

- M3 Method › 1: FND-0001; FND-0003

---

This pack cites 2 of 2 relevant findings.

2 of 2 top-rated relevant findings cited.

> Generated with ProbeMatrix Learnings Coach v2.0.0a8 (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
