# HFACS levels and categories

The four levels, their sub-categories and the Nanocode prefixes that ProbeMatrix exports use. Cite this file whenever a pack defines a level, places a cause at a level, or teaches people to tell the levels apart. The machine-readable copy is `hfacs-codes.json`.

Source: Wiegmann & Shappell's HFACS, as adapted by ProbeMatrix. The level and sub-category names below are the ones ProbeMatrix writes into the export; they differ in places from the published HFACS wording. Where this file adds a plain-language example, the example is illustrative and is never evidence about an incident.

## Contents
1. The four levels
2. Sub-categories and prefixes
3. Classic categories not seen in the sample
4. Spotting a finding at the wrong level
5. Causal direction
6. The name: HFACS or HFMAP

## 1. The four levels

| Level | Name | What it covers |
|---|---|---|
| 1 | Unsafe Acts | What people at the sharp end did or did not do just before the event: errors and violations. A level 1 finding describes an act, never the person. |
| 2 | Preconditions | The conditions present at the time that made the act more likely: physical, technological and task environment, the state of the people involved, and teamwork. |
| 3 | Supervision | How work was planned, resourced, checked and corrected by supervision. |
| 4 | Organisational Influences | The decisions, systems and norms set by the organisation: resources, policies and processes, climate and culture, selection and staffing. |

The export's `Level Name` column spells level 4 "Organizational Influences" (US spelling) while its sub-categories use "Organisational". The engine and the packs use the UK spelling. Match on the `Level` number, never on the level name.

## 2. Sub-categories and prefixes

A Nanocode such as `OIR 1.1` is a prefix plus a factor number. The prefix fixes the level and the sub-category, one to one. The sub-category strings are the export's own, character for character, including the space after some slashes.

| Prefix | Level | Sub-category (export string) | Plain example |
|---|---|---|---|
| `AJDE` | 1 | Errors - Judgment & Decision-Making Errors | A task continued after the plan no longer fitted the situation. |
| `APE` | 1 | Errors - Perception Errors | A gauge was misread in poor light. |
| `ASBE` | 1 | Errors - Skill/Performance Based Errors | A step in a familiar job was skipped or done out of order. |
| `AV` | 1 | Violations | Work departed from a procedure that had stopped fitting the job; the learning is why the rule did not fit. |
| `PPE` | 2 | Environmental Factors - Physical Environment | Heat, noise, darkness or a congested layout made the work harder. |
| `PPI` | 2 | Condition of Individuals - Perceptual Factors/ Sensory Misperception | A release could not be seen or smelt, so it was not perceived. |
| `PSE` | 2 | Environmental Factors - Situational/Task Environment | Time pressure or simultaneous operations added risk to the task. |
| `PTE` | 2 | Environmental Factors - Technological Environment | A detector was out of service, or a display hid an alarm. |
| `PTF` | 2 | Personnel Factors - Teamwork (Coordination/ Communication/ Planning Factors) | A shift handover left out a live hazard. |
| `SVF` | 3 | Failure to Correct Known Problem | A defect already reported was not put right before the event. |
| `SVI` | 3 | Supervision Inadequate | No one confirmed that the isolations were in place. |
| `SVIO` | 3 | Planned Inappropriate Operations | A job was scheduled with too few people or out of sequence. |
| `SVV` | 3 | Supervisory Violations | A task was authorised without the required permit. |
| `OIC` | 4 | Organisational Climate/ Culture Influences | Production signals outweighed raising concerns. |
| `OIP` | 4 | Organisational Policy & Process Issues | No process existed to review a known design weakness. |
| `OIR` | 4 | Resource Management | A replacement was deferred for budget reasons. |
| `OIS` | 4 | Personnel Selection & Staffing | A role was filled without the required qualification. |

All 17 prefixes appear in the public Hazira sample. Select by prefix with `PMLC select <ws> --prefix OIC` or by sub-category with `--subcategory "Failure to Correct Known Problem"`; for culture learnings, `--prefix OIC` is the fallback when the `norm_setter` relation is too sparse.

## 3. Classic categories not seen in the sample

The published HFACS framework also has these categories. ProbeMatrix may emit them, but their prefixes are not yet confirmed, so they are not in `hfacs-codes.json`. If an export contains a prefix that is not in the JSON, read its level and sub-category from the export's own `Level` and `Subcategory` columns and add the prefix with `"seen_in_sample": false`.

- Level 2: Condition of Individuals - Adverse Mental States (attention, complacency, distraction); Adverse Physiological States (fatigue, illness); Physical/Mental Limitations; Personnel Factors - Personal Readiness (rest, fitness for duty).
- Level 1: the published framework splits Violations into routine and exceptional; ProbeMatrix exports one Violations sub-category.

## 4. Spotting a finding at the wrong level

A finding is mis-levelled when its wording describes something owned at a different level from its code. Use these tests when coaching investigators or writing answer keys; do not re-code findings in a pack. Report the observation instead, citing the Finding ID.

1. **Who could have changed it?** If only a manager, a budget holder or a policy owner could have changed the condition, it belongs at level 3 or 4, even when the sharp-end act is the visible part.
2. **Act or condition?** A level 1 finding names an act at a moment in time. "The detector was out of service" is a condition (level 2, `PTE`); "the out-of-service detector was not reported for months" is supervision (level 3, `SVF`); "there was no budget or process to replace detectors" is organisational (level 4, `OIR` or `OIP`).
3. **Known before?** If the problem was reported, logged or audited before the event and stayed open, it is at least level 3 (`SVF`).
4. **Planned or improvised?** Risk built into the schedule, crewing or sequence is level 3 (`SVIO`), not a level 1 decision error.
5. **Norm or one-off?** A departure that had become normal practice points to level 4 climate (`OIC`) or level 3 supervision, as well as to the level 1 act.
6. **Coded too low is the common case.** When in doubt between two levels, ask what the higher level did to make the lower-level act likely, and say so.

## 5. Causal direction

The convention in every Learnings Coach output: the higher level enables the lower. Organisational influences (4) create the supervisory conditions (3), which allow the preconditions (2), in which the unsafe acts (1) happen. Causal-map arrows run from the enabling factor to the factor it enabled. A link that runs the other way (a lower-level factor said to cause a higher-level one) is unusual; keep it only when the export's `Causal Chain` or `Causal Explanation` says so, and label it.

## 6. The name: HFACS or HFMAP

The export's `Analysis Statistics` sheet labels the levels "HFMAP Level". It is a label for the same four HFACS-based levels used everywhere else in the export, not a different framework. In outputs, call the method "HFACS-based (Human Factors Analysis and Classification System)" and do not use "HFMAP" in audience-facing text.
