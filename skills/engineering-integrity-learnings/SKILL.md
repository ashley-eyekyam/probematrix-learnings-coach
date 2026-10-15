---
name: engineering-integrity-learnings
description: Produce learning for engineering, design, asset integrity, inspection, reliability, instrumentation and management-of-change functions from a ProbeMatrix investigation export - specifications and documents, change control, inspection and corrosion programmes, testing after maintenance, alarm and safety-system design, ageing equipment - with technical recommendations rated on the hierarchy of controls. Use when someone asks what engineers, the technical authority, integrity or reliability teams, MOC owners or instrument engineers should learn, or wants a technical lessons pack from an incident.
---

# Engineering & Integrity Learnings

Audience: Learning Clusters F04 (instrumentation, control and calibration), F05 (asset integrity, corrosion and inspection), F07 (engineering, design, documents and MOC), plus F03 where hazardous-area equipment is involved.

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py`. Read `learnings-coach/references/learning-principles.md`.

## Gather

```bash
PMLC select <ws> --entity F03 F04 F05 F07 --brief
PMLC select <ws> --entity F04 F05 F07 --level 3 4 --min-rating <top>
PMLC select <ws> --text "specification|drawing|P&ID|MOC|change|inspection|thickness|corrosion|calibrat|interlock|test|design" --brief
PMLC timeline <ws> --before <incident date>
```

## Write

1. **Technical learnings by theme**: specification and substitution of parts; testing after maintenance; change management; inspection and corrosion programmes; documents and as-built records; detection, alarm and shutdown design; hazardous-area equipment integrity; ageing equipment. Only themes the evidence supports.
2. **For each learning**: the technical condition, how it persisted (L3–L4), the barrier it weakened, a recommendation with HoC tier (engineering controls first where credible), and a technical leading indicator.
3. **Engineering decisions pending**: questions the technical authority must settle (e.g. test pressure policy after pressure-boundary work, acceptance of substitute components), stated as decisions, not answers.
4. **Data and records**: what technical records were missing or unreliable, and what the minimum record should be.

## Output

`<ws>/outputs/engineering-integrity-learnings.md`. Do not specify engineering values (pressures, thicknesses, intervals) beyond what the evidence states; flag them as decisions for the technical authority.
