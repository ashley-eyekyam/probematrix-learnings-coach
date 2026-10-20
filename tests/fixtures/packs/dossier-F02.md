# Cluster Learning Dossier F02 Mechanical Maintenance: Synthetic pump fire, 2024

**DRAFT**

Review: draft · Classification: internal · Version 1.0

Draft because: no finding is marked as edited by a person

*Learning purposes: not a statutory document · Learnings drafted by an AI agent from AI-assisted findings*

**Audience:** Mechanical Maintenance (F02), all tiers

**Incident:** Synthetic pump fire · 2024-03-20

## Bottom line

- Return to service had no test step, and the crew restarted the pump untested. [FND-0001; FND-0002]

## S1 Profile

| Level | Findings | Cites |
|---|---|---|
| L1 Unsafe acts | 1 | FND-0001 |
| L3 Supervision | 1 | FND-0002 |

## S2 Practice (L1)

**Learning:** Restarting without a test went unchallenged because nothing asked for one. [FND-0001]

The work order shows no test [EVD-0001].

**Learning:** A seal change was treated as routine work with no test step in the plan. [FND-0001; EVD-0001]

The work order lists the seal change and no test [EVD-0001].

**Learning:** The crew relied on the part being right because nothing told them otherwise. [FND-0001; FND-0003]

The seal came from a local purchase with no specification [FND-0003].

## Preconditions

**Learning:** An unfamiliar seal gave no cue that a test mattered more than usual. [FND-0003; EVD-0003]

The findings show local seals without a specification [FND-0003].

**Learning:** No test record field on the work order made the omission invisible. [FND-0001]

The work order closed without a test entry [EVD-0001].

**Learning:** The gas alarm gave the crew no automatic protection once the leak started. [FND-0004; EVD-0002]

The alarm was display-only [FND-0004].

## S4 Supervision (L3)

**Learning:** Supervisors had no checklist to refuse a restart against. [FND-0002]

The procedure index has no entry [EVD-0002].

**Learning:** Release to service depended on memory, not a signed hold point. [FND-0002; EVD-0002]

No return-to-service checklist exists [EVD-0002].

**Learning:** Supervision had no record to check before approving the restart. [FND-0001; FND-0002]

The work order shows no test [EVD-0001].

## Organisational influences

**Learning:** The spares programme let critical seals in without a specification. [FND-0003]

Purchase records show local buying since March 2022 [EVD-0003].

**Learning:** The procedure set had no owner checking that hold points covered return to service. [FND-0002]

The procedure index has no entry [EVD-0002].

**Learning:** Budget pressure on spares was not weighed against the risk of unknown parts. [FND-0002; FND-0003]

The findings name the plant manager as budget owner [FND-0003].

## Interfaces

Maintenance fits what stores buys, and neither side checked the specification [FND-0003; FND-0001].

**Learning:** Maintenance and stores need one owner for the specification of a critical spare. [FND-0001; FND-0003; EVD-0001]

## S7 Barriers

**Barrier:** Leak test before return to service [FND-0001; FND-0002]
- Failure mode: No checklist required it
- Type: prevention
- State on the day: absent
- Control tier: administrative
- Fix: Signed hold point

## S8 Precursors

- 2024-03-12: Seal changed; no test recorded [FND-0001; EVD-0001]

## S9 Tier messages

### T1 Frontline

Do not restart without a signed leak-test record [FND-0001].

### T2 Supervision

Make the leak test a hold point you sign [FND-0002].

## S10 Recommendations

**Recommendation:** Signed leak-test hold point on every return to service [FND-0002; EVD-0002]
- Control tier: administrative
- Barrier: Leak test before return to service
- Leading indicator: % of restarts with a test record

## Competence

| Tier | Competence | Cites |
|---|---|---|
| T1 Frontline | Carry out and record a leak test | FND-0001 |
| T2 Supervision | Check the test record before release | FND-0002 |

## S12 Transferability

| Learning | Reach | Reason | Cites |
|---|---|---|---|
| No test step at return to service | Same site | Only this site's procedure index is in evidence | FND-0002 |

## S14 Formats

| Learning | Format | Cites |
|---|---|---|
| Test what you disturb | Learning Card and toolbox talk | FND-0001 |

---

This pack cites 2 of 2 relevant findings.

1 of 1 top-rated relevant findings cited.

> Generated with ProbeMatrix Learnings Coach v2.0.0a4 (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
