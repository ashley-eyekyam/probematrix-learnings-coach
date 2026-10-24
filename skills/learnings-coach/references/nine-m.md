# The nine Ms (9M)

A second lens on the same findings: where HFACS asks *at which level* a condition sat, the 9M lens asks *which part of the work system* it belongs to, so that recommendations can be grouped by who can change it. The `nine-m-analysis` skill works through the Ms with the user one question at a time; `nine-m-seed` gives it a starting profile. The machine-readable copies are `nine-m.json` (the Ms, subcategories, definitions and probe questions) and `nine-m-map.json` (how a Nanocode, its wording and its clusters point to an M).

## Contents
1. The nine Ms, in order
2. Where the Ms overlap
3. M1 is not the people M
4. How nine-m-seed scores a finding
5. Where the words come from
6. The interview, step by step

## 1. The nine Ms, in order

Always work through them in this order, M1 to M9. Each subcategory in `nine-m.json` carries a one-line definition and three probe questions, each answered yes, partly or no.

| Code | Name | What it covers | Subcategories |
|---|---|---|---|
| M1 | Manpower/Mindpower | Whether the people doing the work were ready for it, and what the organisation did to make them ready. | 13 |
| M2 | Medium | The physical and psychological surroundings of the work, and how they made it easier or harder to do safely. | 12 |
| M3 | Method | The procedures, processes and ways of working used to plan, carry out and control the task. | 10 |
| M4 | Mission | The goals, priorities and targets the organisation set, and the pressure they put on decisions about risk. | 10 |
| M5 | Measurement | How the organisation measured, monitored and analysed performance and safety, and acted on what it found. | 11 |
| M6 | Management/Money | How leadership, management practice and money shaped the resources and decisions behind the work. | 10 |
| M7 | Machine | The equipment, tools, instruments and technology used in the work, from design through to retirement. | 10 |
| M8 | Material | The materials, parts, consumables and substances used or handled, including their quality, supply and handling. | 10 |
| M9 | Maintenance | How equipment was kept working and reliable through inspection, servicing, repair and testing over its whole life. | 11 |

**M1 Manpower/Mindpower:** M1.01 Selection and Qualification; M1.02 Training Programme Design and Delivery; M1.03 Competence Assessment and Authorisation; M1.04 Workload Management; M1.05 Fatigue Risk Management; M1.06 Cognitive Readiness and Situational Awareness; M1.07 Psychological Readiness and Support; M1.08 Communication and Coordination; M1.09 Team Dynamics; M1.10 Leadership and Authority Gradient; M1.11 Cultural and Organisational Climate; M1.12 Error Propensity and Human Limitations; M1.13 Competence Sustainability and Continuous Improvement.

**M2 Medium:** M2.01 Physical Environment Controls; M2.02 Workspace Ergonomics and Human Fit; M2.03 Noise and Auditory Environment; M2.04 Visual Environment and Legibility; M2.05 Localised Hazards and Exposure; M2.06 Operational Environment and Tempo; M2.07 Psychological Environment and Stressors; M2.08 Cultural Environment and Norms; M2.09 Environmental Stressors and Extreme Conditions; M2.10 External Environment and Stakeholders; M2.11 Infrastructure, Access, and Traffic Interfaces; M2.12 Emergency Preparedness in Environmental Contexts.

**M3 Method:** M3.01 Procedure Design and Development; M3.02 Standard Operating Procedures (SOPs); M3.03 Compliance and Adherence; M3.04 Flexibility and Adaptability; M3.05 Documentation and Communication; M3.06 Risk Management Integration; M3.07 Alignment with Technology; M3.08 Emergency and Contingency Procedures; M3.09 Continuous Improvement; M3.10 Simplicity and Accessibility.

**M4 Mission:** M4.01 Strategic Objectives and Priorities; M4.02 Operational Goals and Targets; M4.03 Resource Allocation; M4.04 Leadership and Accountability; M4.05 Risk Tolerance and Decision-Making; M4.06 External Influences and Stakeholder Expectations; M4.07 Mission Complexity and Clarity; M4.08 Organisational Culture and Mission Alignment; M4.09 Communication and Mission Integration; M4.10 Continuous Evaluation and Improvement.

**M5 Measurement:** M5.01 Metrics Design and Relevance; M5.02 Data Collection and Accuracy; M5.03 Monitoring and Reporting Systems; M5.04 Analysis and Interpretation; M5.05 Feedback Loops; M5.06 Benchmarking and Comparisons; M5.07 Predictive Analytics and Risk Indicators; M5.08 Communication of Measurements; M5.09 Continuous Improvement through Measurement; M5.10 Integration with Technology; M5.11 Audits and Inspections.

**M6 Management/Money:** M6.01 Strategic Financial Planning; M6.02 Leadership and Decision-Making; M6.03 Budgeting and Resource Allocation; M6.04 Training and Development Investments; M6.05 Risk Management and Compliance; M6.06 Investment in Infrastructure and Technology; M6.07 Performance Monitoring and Accountability; M6.08 Stakeholder Engagement and Communication; M6.09 Financial Controls and Auditing; M6.10 Continuous Improvement and Adaptability.

**M7 Machine:** M7.01 Design and Suitability; M7.02 Maintenance and Reliability; M7.03 Integration and Compatibility; M7.04 Automation and Control Systems; M7.05 Ergonomics and Usability; M7.06 Monitoring and Diagnostics; M7.07 Safety Features and Risk Mitigation; M7.08 Lifecycle Management; M7.09 Environmental Impact and Sustainability; M7.10 Training and Competence.

**M8 Material:** M8.01 Material Quality; M8.02 Material Availability and Supply Chain; M8.03 Material Compatibility; M8.04 Storage and Handling; M8.05 Material Waste and Sustainability; M8.06 Material Cost Management; M8.07 Compliance and Regulatory Requirements; M8.08 Material Traceability; M8.09 Innovation and Material Advancements; M8.10 Emergency and Contingency Planning.

**M9 Maintenance:** M9.01 Preventive Maintenance Programme; M9.02 Predictive Maintenance and Condition Monitoring; M9.03 Corrective Maintenance Execution; M9.04 Maintenance Planning and Scheduling; M9.05 Maintenance Personnel Competence; M9.06 Maintenance Documentation and Records; M9.07 Spare Parts and Inventory Management; M9.08 Maintenance Technology and Tools; M9.09 Software and Control System Maintenance; M9.10 Safety in Maintenance Activities; M9.11 Continuous Improvement in Maintenance.

## 2. Where the Ms overlap

Four pairs of subcategories cover nearby ground. When a condition could sit in either, the skill asks the user which one fits; it never counts the same condition in both, so nothing is double-counted.

| Overlap | The question to ask |
|---|---|
| M7 "Maintenance and Reliability" and M9 | Is the problem the equipment's own reliability (M7), or the work done to keep it reliable (M9)? |
| M7 "Training and Competence" and M1 | Is it about knowing this particular equipment (M7), or about how people are trained and assessed in general (M1)? |
| M6 "Training and Development Investments" and M1 | Is the gap the money and time set aside for training (M6), or the training itself (M1)? |
| The leadership and culture subcategories of M1 and M4 | Is it how a team is led day to day (M1), or what the organisation's goals and culture make normal (M4)? |

## 3. M1 is not the people M

M1 Manpower/Mindpower is about the conditions that make people ready for the work: selection, training, workload, rest, communication and support. It is never a place to record who got something wrong. Before any M1 learning is written, the skill asks why the action made sense at the time and what system drove it (question 3d), or marks the driver unknown. `check-pack` warns when M1 holds the most recommendations while another M has more findings at levels 3 and 4. Discipline, "accountability" and "consequences" are never offered as answers.

## 4. How nine-m-seed scores a finding

`nine-m-seed` reads the workspace and scores every finding for each M (spec §7.3):

| Signal | Weight | Where it comes from |
|---|---|---|
| The Nanocode's primary M | 3 | `nine-m-map.json` `codes` (one Nanocode), else `prefixes` (its prefix's default) |
| Each secondary M of the Nanocode | 1 | the same entry's `secondary` list |
| A keyword hit | 1 per M | `keywords`, matched on the Instance Label and Short Description only |
| An entity hit | 1 per M | `entities`, matched on the finding's Learning Cluster entities in `clusters.json` |

The Nanocode's primary M is the finding's `m_primary`. Its `m_secondary` list holds the Nanocode's secondary Ms and any other M that two signals agree on. A finding whose prefix is not in the map is listed under `unmapped` and reported, never dropped. The justification and causal text are left out of the keyword match because they mention most Ms; they supply quotes, not weight.

Codes alone under-count Material (M8) and Maintenance (M9): few Nanocodes route there, yet many findings describe parts, gaskets, spares, inspection and repair. That is why the skill asks about every M rather than only reading the codes, and why the keyword lists for M8 and M9 are the broadest.

## 5. Where the words come from

Only the nine M codes and titles and the 97 subcategory names come from the ProbeMatrix 9M framework (Eyekyam). Every definition and probe question here and in `nine-m.json` is newly written for the coach. The framework's root-cause signals, corrective and preventive action catalogues, indicators, evidence checklists and app prompts are not copied: Action catalogues remain in the ProbeMatrix CAPA Zone.

`nine-m-map.json` is new work for this repository, under its licence. Change it to fit your organisation and pass your copy with `nine-m-seed --map`.

## 6. The interview, step by step

The `nine-m-analysis` skill asks one question per turn. Each question is printed by `nine-m-suggest --record`, which appends it to `<ws>/nine_m_session.json` with its suggestions and their cites; `nine-m-answer` records the choice or the user's own words. The session file holds every question, what was offered and what was answered, with the source of each answer (`export` when the user took a suggestion, `user` for free text), so a run can be resumed and audited.

| Step | Question | What the answer decides |
|---|---|---|
| 2 scope | Which Ms should we work through? | The Ms asked about, always in the order M1 to M9 |
| 3a relevance | Is this M relevant to the incident? | "Not relevant" ends the M: its reason and cites go in the `not-relevant` table |
| 3b subcategory | Which subcategory fits best? | The subcategory id (`M8.03`) on the condition and in `nine-m-map.json`; an overlap (section 2) is settled here |
| 3c condition | Which condition is it? | One learning per condition; two suggestions that are one condition are merged |
| 3d driver | Why did it make sense at the time, and what system drove it? | The driver in the learning's explanation; for M1 it is asked before any M1 learning is written |
| 3e barrier | What state was the barrier in? | The `barrier` item: absent, degraded, defeated or worked partly |
| 3f change | Which direction of change? | The `recommendation` tier, strongest first; corrective or preventive, said by the user |
| 3g indicator | How would you see the change working? | The recommendation's leading indicator (optional) |
| 4 cross-M | Keep linked Ms as one learning, or separate? | Whether a condition is counted once across two Ms |
| 5 gaps | What evidence would settle each unknown? | A `gaps` entry for every "None / unknown" |

The budget is 6 questions per M plus 4 global questions (scope, cross-M, gaps and one spare), 58 at most; the engine refuses one more. Training is offered only together with a stronger control and is labelled weak on its own. `nine-m-replay --accept-recommended` writes a whole session by taking the first suggestion every time, with `"mode": "replay"`: it is for demonstrations and tests only, and a pack written from it carries the fixed line "Answers chosen for demonstration, not by the organisation."
