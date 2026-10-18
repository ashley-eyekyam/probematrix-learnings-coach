---
name: engineering-integrity-learnings
description: Produce learning for engineering, design, asset integrity, inspection, reliability, instrumentation and management-of-change functions from a ProbeMatrix investigation export - specifications and documents, change control, inspection and corrosion programmes, testing after maintenance, alarm and safety-system design, ageing equipment - with technical recommendations rated on the hierarchy of controls. Use when someone asks what engineers, the technical authority, integrity or reliability teams, MOC owners or instrument engineers should learn, or wants a technical lessons pack from an incident.
---

# Engineering & Integrity Learnings

Audience: the Learning Clusters tagged `engineering` (in the default taxonomy F04 instrumentation, control and calibration, F05 asset integrity, corrosion and inspection, F07 engineering, design, documents and MOC, and F03 electrical, for hazardous-area equipment).

Engine: `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py`. Read `learnings-coach/references/learning-principles.md`.

## Gather

```bash
PMLC select <ws> --tag engineering --brief
PMLC select <ws> --tag engineering --level 3 4 --top-rated
PMLC select <ws> --text "specification|drawing|P&ID|MOC|change|inspection|thickness|corrosion|calibrat|interlock|test|design" --brief
PMLC timeline <ws> --before incident
```

## Write

1. **Technical learnings by theme**: specification and substitution of parts; testing after maintenance; change management; inspection and corrosion programmes; documents and as-built records; detection, alarm and shutdown design; hazardous-area equipment integrity; ageing equipment. Only themes the evidence supports.
2. **For each learning**: the technical condition, how it persisted (L3–L4), the barrier it weakened, a recommendation with HoC tier (engineering controls first where credible), and a technical leading indicator.
3. **Engineering decisions pending**: questions the technical authority must settle (e.g. test pressure policy after pressure-boundary work, acceptance of substitute components), stated as decisions, not answers.
4. **Data and records**: what technical records were missing or unreliable, and what the minimum record should be.

## Output

Write the pack `<run>/outputs/engineering-integrity-learnings.json` (schema: `learnings-coach/references/pack-schema.md`), then:

```bash
PMLC check-pack <ws> <run>/outputs/engineering-integrity-learnings.json   # fix every problem it lists
PMLC pack <ws> <run>/outputs/engineering-integrity-learnings.json         # -> engineering-integrity-learnings.html (primary) and .md
```

Sections → kinds:
1. For each learning, write three items with the same `group` (the theme):
   - a `learning`: the technical condition and how it persisted;
   - a `barrier` for the barrier it weakened (type, owner, state, failure_mode, hoc_tier, fix, indicator);
   - a `recommendation`, engineering controls first where credible.
2. `decision` items (options, no answers), with `owner` = the technical authority.
3. `check` items stating the minimum record, with `when` = the point in the work.

Set `"scope": {"tags": ["engineering"]}`. Put data-quality corrections in `data_quality`, findings left out on purpose in `exclusions`, and same-condition findings in `supporting_cites`.

```json
{"kind": "barrier", "group": "Specification and substitution", "barrier": "…", "type": "prevention", "owner": "…",
 "state": "absent", "failure_mode": "…", "hoc_tier": "engineering", "fix": "…", "indicator": "…", "cites": ["FND-…"]}
```

Do not specify engineering values (pressures, thicknesses, intervals) beyond what the evidence states; make them `decision` items for the technical authority.
