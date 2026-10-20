# The Learnings Coach ontology

How one investigation becomes learning for every part and every level of an organisation.

## Contents
1. The idea
2. Method in three steps
3. Learning Clusters: entity (F) × tier (T) × relation (R)
4. Per-cluster sub-divisions S1–S14
5. Cross-cluster products
6. Mapping to the export columns

---

## 1. The idea

A conventional investigation report is organised by **discipline** (facilities, maintenance, electrical, fire-fighting…) and closes with a flat list of root causes and recommendations. It tells the organisation *what went wrong*. It rarely tells each part of the organisation, at each level, *what it should now learn and do differently*.

A ProbeMatrix investigation analyses the same evidence at four human-factors levels (Unsafe Acts → Preconditions → Supervision → Organisational Influences, defined in `hfacs-levels.md`). It produces many evidence-linked findings, and for each one it names the **roles and organisational entities involved**. That field is the bridge. The Learnings Coach clusters findings by the entity that owns the learning and then opens each cluster into structured, audience-ready learning.

The unit of learning is the **learning**, not the finding. Findings are instance-level (one factor can appear several times), so they are always the evidence beneath a learning, never the headline count.

## 2. Method in three steps

1. **Classify** every finding into Learning Clusters, using `Individuals Involved` normalised to the taxonomy in §3 (`pmlc.py classify`, then an LLM pass for roles the rules cannot resolve).
2. **Open each cluster** along the sub-divisions in §4.
3. **Generate each learning piece** with one focused LLM pass per (cluster × sub-division), grounded only in that cluster's findings, their evidence quotes and their causal explanations. Messages for each tier (S9) sit inside each piece.

## 3. Learning Clusters

### 3.1 Layer F: functional entity (who owns the learning)

| ID | Entity | Tags | Typical roles |
|---|---|---|---|
| F01 | Operations & Control Room | operations | control-room operators, shift engineers, shift in-charges |
| F02 | Mechanical Maintenance | operations | fitters, technicians, maintenance supervisors and managers |
| F03 | Electrical Maintenance | engineering | electrical technicians, electrical PM planners, hazardous-area equipment owners |
| F04 | Instrumentation, Control & Calibration | engineering | calibration teams, DCS / F&G engineers, instrument supervisors |
| F05 | Asset Integrity, Corrosion & Inspection | engineering | integrity and corrosion engineers, inspection, reliability |
| F06 | Materials Management (Stores / Procurement) | supply | stores, procurement, spares and quality control |
| F07 | Engineering, Design, Documents & MOC | engineering | engineering authority, design, document control, management of change |
| F08 | Work Management & Planning | operations | planners, CMMS / work-order and notification owners |
| F09a | Fire-fighting Operations & Fire-water Systems | emergency | fire crews, fire station, fire-water and fire-pump maintenance |
| F09b | Emergency Planning & Command | emergency | emergency plan owners, incident / site controllers, drill coordinators |
| F10 | Security & Surveillance | emergency | security staff, CCTV operators, watch posts |
| F11 | HSE, Process Safety & Audit | assurance | HSE function, process safety, audit teams, permit-to-work owners |
| F12 | HR, Training & Competence | people | HR policy owners, training coordinators, rostering and staffing |
| F13 | Plant & Asset Leadership | leadership | plant manager, head of operations, site / area management |
| F14 | Corporate & Board | corporate | directors, corporate functions, the board, recommendation tracking |
| F15 | Regulators & External Bodies | external | regulators, statutory inspectorates |
| F16 | Vendors, OEMs & Suppliers | supply | vendors, OEMs, manufacturers, suppliers |
| F17 | Contractors | contractor, supply | contractors and their crews |
| F99 | Unmapped | | roles the rules could not place; resolve them before publishing |

Before v2.0, F14 also held regulators, vendors and contractors; they are now F15 to F17. The audience skills select by **tag** (`PMLC select <ws> --tag emergency`, pack `"scope": {"tags": [...]}`), not by entity ID, so a renamed or extended taxonomy keeps working as long as its entities carry the same tags. Site- or country-specific role words (e.g. CISF, ERDMP, SIC / CIC, GM / CGM, resident engineer) live in an overlay under `references/overlays/` and are applied with `PMLC classify <ws> --overlay <name>`.

**Taxonomy version.** `taxonomy.json` carries `"version": "2.0"`; `clusters.json` records it with a `taxonomy_fingerprint` (sha256 of the merged taxonomy, overlays and org chart) and the `statutory_roles` found. Changes in 2.0: `leadership` needs a qualifier (plant, site, asset, senior), `sign` variants (signing, signatories, countersigned) count as approver, `document custodian/owner` and `controlled document` map to F07, and deputy and assistant general managers (DGM, Dy. GM, Asst. GM) take T3 and additional general managers T4 (the DGM words live in the India overlay). An organisation's own departments come in with `classify --org-chart FILE.csv`.

Adapt the list to the organisation: rename, split or merge entities in `taxonomy.json`. Keep the IDs stable within one study.

### 3.2 Layer T: organisational tier (which level learns)

| ID | Tier |
|---|---|
| T1 | Frontline / sharp end |
| T2 | First-line supervision / shift in-charge |
| T3 | Function / department management |
| T4 | Plant / asset leadership |
| T5 | Corporate / policy owner / board |
| T9 | Unresolved (resolve before publishing) |

### 3.3 Relation R: how the entity relates to the factor

The AI often qualifies roles ("…(approval authority)", "…(absent)", "…(role model)"). The qualifier decides the *kind* of learning:

| ID (`--relation`) | Relation | Kind of learning it produces |
|---|---|---|
| `actor` | actor / participant (the default when no rule matches) | a practice to change |
| `approver` | approver / authoriser | a check to add or strengthen |
| `owner` | owner / custodian | a system, policy or document to change |
| `absent` | absent / not provided | an organisational-design learning: a function that should exist |
| `norm_setter` | role model / norm-setter | a culture learning about what leaders demonstrate |
| `learner` | learner / norm-receiver | a culture learning about what people absorb |
| `challenger` | expected challenger | a learning about speaking up and challenge authority |

Where the relation comes from: `classify` reads it from the role's own wording with the `relations` rules in `taxonomy.json` (first match wins). It is only as good as the qualifiers the analysis wrote, so a sparse relation (few `norm_setter` roles, say) is a limit to state, not a finding. For culture learnings, fall back to the `OIC` prefix (`hfacs-levels.md`).

### 3.4 Causal direction

The higher level enables the lower: organisational influences (L4) create supervisory conditions (L3), which allow preconditions (L2), in which unsafe acts (L1) happen. Causal links and causal-map arrows run from the enabling factor to the factor it enabled. See `hfacs-levels.md` §5 for links that run the other way.

## 4. Per-cluster sub-divisions

| Code | Sub-division | Question it answers for the cluster |
|---|---|---|
| S1 | Cluster profile (computed) | How much of this event sits with us, at which levels, how strongly rated? |
| S2 | Sharp-end practice (L1) | Which acts in our work contributed, described as practices, without blame? |
| S3 | Conditions we created or tolerated (L2) | Which technical, environmental and team conditions were ours to control? |
| S4 | Supervisory learning (L3) | What should our supervisors see, check, correct and refuse? |
| S5 | Organisational / system learning (L4) | What must change in our systems, resources, policies and norms? |
| S6 | Interface learnings | What fell between us and another function? |
| S7 | Barrier learning | Which barriers do we own, how did they fail, how strong must the fix be? |
| S8 | Weak signals and precursors | What had we already been told, and when? |
| S9 | Tier-specific messages | One message each for frontline, supervisor, manager, leadership, policy owner |
| S10 | Recommendations | What should change, which barrier, which evidence, which control tier, which leading indicator |
| S11 | Competence and training needs | Which competences are missing? |
| S12 | Transferability | Same site / other sites / industry-wide |
| S13 | Comparison with another report | Did the comparator report have a counterpart: yes / partial / none? |
| S14 | Dissemination format | Brief paragraph, Learning Card, toolbox prompt, training question |

## 5. Cross-cluster products

- **Tier × entity map**: where the learning sits across the organisation (`pmlc.py dashboard`).
- **Interface matrix**: which pairs of functions share findings or causal links (`pmlc.py interfaces`).
- **Causal graph**: factor-to-factor links the AI wrote into its causal explanations (`pmlc.py causal`).
- **Precursor timeline**: dated warnings across all entities (`pmlc.py timeline`, curated by the precursor-timeline skill).
- **Learnings Register**: one row per learning, with recommendations (`register-schema.md`, `pmlc.py register-xlsx`).

## 6. Mapping to export columns

| Ontology element | Export column(s) |
|---|---|
| F, T, R | `Individuals Involved` |
| HFACS level and sub-category | `Level`, `Level Name`, `Category`, `Subcategory` |
| Factor | `Nanocode`, `Name` |
| Strength of contribution | `Rating` (higher = stronger) |
| What happened | `Instance Label`, `Short Description` |
| Why it is a factor | `AI Justification` |
| How it connects | `Causal Explanation` (names other factors) and the `Causal Chain` sheet when populated |
| Evidence | `Linked Evidence` + `Evidence Links` sheet (`Relevance`, `Specific Reference`) |
| Investigative follow-up | `Evidence to Collect`, `Key Questions`, `Suggested Interviews`, `Causal Hypothesis` (often empty) |
