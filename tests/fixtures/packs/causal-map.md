# Causal Map: Synthetic pump fire, 2024

**DRAFT**

Review: draft · Classification: internal · Version 1.0

Draft because: no finding is marked as edited by a person

*Learning purposes: not a statutory document · Learnings drafted by an AI agent from AI-assisted findings*

**Audience:** Investigators and site leaders

**Incident:** Synthetic pump fire · 2024-03-20

## Bottom line

- The spares programme failure feeds both the missing checklist and the skipped test. [FND-0003]

## Causal map

Graph: 4 nodes, 4 links [FND-0001; FND-0002; FND-0003; FND-0004]

- L4 OR 2.2 Spares Programme Failure → L1 AB 1.1 Step Omitted (2 mentions)
- L3 SV 1.4 No Guidance Provided → L1 AB 1.1 Step Omitted (2 mentions)
- L4 OR 2.2 Spares Programme Failure → L2 PE 2.1 Alarm Not Configured (1 mention)
- L4 OR 2.2 Spares Programme Failure → L3 SV 1.4 No Guidance Provided (1 mention)

## Hubs

| Factor | Level | Out-links | Cites |
|---|---|---|---|
| OR 2.2 Spares Programme Failure | L4 | 3 | FND-0003 |
| SV 1.4 No Guidance Provided | L3 | 1 | FND-0002 |

## Pathways

### Pathway 1: spares to the skipped test

Seals were bought without a specification [FND-0003]. No checklist asked for a leak test [FND-0002]. The pump restarted untested [FND-0001].

## Breaks in the map

No finding links the alarm configuration to the restart, so the map shows no such link [FND-0004].

## Event sequence

- 2022-03 (24 months before): Latent condition: local seal purchases begin *(weak signal)* [FND-0003]
- 2024-03-12: Trigger: seal changed and pump restarted untested [FND-0001]

---

This pack cites 2 of 2 relevant findings.

> Generated with ProbeMatrix Learnings Coach v2.0.0a4 (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
