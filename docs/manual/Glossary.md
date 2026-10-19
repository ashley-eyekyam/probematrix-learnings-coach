# Glossary

The words this manual uses, in plain language, in alphabetical order. Where a word is also a file, a flag or a field, the term is given in that form too.

## A to C

### AI justification

The export's own explanation of why the evidence supports a finding, written by ProbeMatrix's AI and checked by investigators. Pages label it "AI justification (ProbeMatrix)" so it is never mistaken for the coach's learning.

### AI-drafted chip

The label "AI-drafted, not human-edited" shown on a finding that no person edited in ProbeMatrix (its `User Edited` column is empty).

### Audience skill

A skill written for one group of readers, such as [supervisor-coach](skills/supervisor-coach.md) or [board-brief](skills/board-brief.md). Compare *analysis skill*: one that analyses the whole investigation, such as [causal-map](skills/causal-map.md). See [Skills](Skills.md).

### Barrier

A control that should stand between a hazard and harm: a design feature, a test, a procedure, an alarm, an isolation valve, an emergency plan. **Prevention** barriers act before control is lost; **mitigation** barriers act after. See [barrier-learnings](skills/barrier-learnings.md).

### Bottom line

The three to five things a reader must take away, at the top of every pack. Each one cites its evidence.

### Causal graph

The map of links between factors that the engine reads from each finding's causal explanation. The higher-level factor enables the lower-level one. Written to `causal_graph.json` by `causal`. See [causal-map](skills/causal-map.md).

### Cite, citation

A Finding or Evidence ID attached to a sentence, showing the record it rests on, for example `[FND-3AB996FC; EVD-2894]`. On a pack page each ID opens the full record.

### Classification

Who may see a file: `internal`, `restricted`, `external` or `public`. Part of the *handling* block. See [Review and sharing](Review-and-sharing.md).

### Content hash

A fingerprint of a file's content, recorded at sign-off. If the file changes, the fingerprint no longer matches and the file is a draft again.

### Coverage

How many of the findings a pack should cover it actually cites, shown on the page as "This pack cites x of y relevant findings". The relevant findings come from the pack's scope.

## D to F

### Data-quality flag

A problem the profile found in the export, such as an empty column, a wrong summary-sheet date, or no finding edited by a person. Outputs state these corrections openly.

### Downgrade vote

A reviewer's vote in ProbeMatrix to downgrade, reject or remove a finding. Learnings leave such findings out, or say why they kept them. `select --exclude-downgraded` drops them.

### DRAFT ribbon

The "DRAFT" label at the top of every page until the file is approved. In Markdown it is `**DRAFT**`; in the workbook it follows the status phrase in each sheet's header.

### Embed mode (`--embed`)

How much of the investigation's records a page carries: `cited` (the default: full records only for what the pack cites), `summary` (as cited, without quotes, evidence descriptions, interviews, key questions and vote reasons) or `full` (everything). A flag of `pack` and `dashboard`.

### Entity

The function or department that owns a learning, such as F02 Mechanical Maintenance or F09b Emergency Planning & Command. The first of the three parts of a *Learning Cluster*. F99 means "not yet placed".

### Evidence

An item in the investigation's evidence: a document, a log record, a witness statement, a recording, a physical item or a photograph. Each has an Evidence ID such as `EVD-2894`. The Hazira export has 46.

### Export

The Excel file (`.xlsx`) you export from a ProbeMatrix investigation. The coach reads its findings, evidence, incident summary, causal chain and statistics sheets.

### Finding

One factor the investigation identified, at one HFACS level, with its rating, description, justification, causal explanation, the roles involved and its linked evidence. Each has a Finding ID such as `FND-3AB996FC`. Several findings can describe the same condition, so findings are counted as instances, not as learnings.

### Forced draft

The rule that nothing may be reviewed or approved until the investigation status is completed, and while no finding is marked as edited by a person. There is no override.

## G to I

### Handling

The review record in a pack or register: its status, the reviewer's role, the review date, classification, legal review, distribution, version, retention review date and content hash. Written by `sign-off`. See [Review and sharing](Review-and-sharing.md).

### HFACS

The Human Factors Analysis and Classification System: a way of analysing an event at four levels, from the acts at the sharp end up to the organisation's influences. ProbeMatrix uses a four-level HFACS-based taxonomy, and every finding sits at one level.

### Hierarchy of controls

The order of strength of a fix: elimination, substitution, engineering, administrative (procedures, checks, permits), training and awareness, and PPE. Every recommendation names its tier (`hoc_tier`). Training and reminders alone are the weakest.

### Hindsight bias

Judging what people did by what is known only after the event. The *knowable-then test* and the language check's JC3 and JC4 rules guard against it.

### Hold point

A point in a job where work stops until a check is done and recorded, for example a test record before equipment returns to service.

### Interface

The seam between two functions: a handover, a shared piece of equipment, a decision one side assumed the other made. See [interface-learnings](skills/interface-learnings.md).

## J to L

### Just culture

A culture in which people are not blamed for honest mistakes and system problems, so that they report and learn openly. The organisation still draws a clear line for acts that are not honest mistakes, through its own processes, never through a learning pack. The coach writes for a just culture: roles only, no blame wording, system fixes before retraining.

### Knowable-then test

The question the coach asks before writing about an act: what could a competent person know at that moment, with the information and pressures they had? If the answer needs facts that came out later, the sentence is hindsight.

### Language check

The check of every pack and register against the rules JC1 to JC12: names, blame, hindsight, legal conclusions, retraining-only fixes, single-holder roles, outside facts, organisation names, equipment tags, the status phrase and appeals. See [Language checks](Language-checks.md).

### Leading indicator

A measure that shows whether a fix is working before the next event, owned by the audience that reads it. For example "% of pressure-boundary jobs released with a design-pressure test record".

### Learning

One generalisable lesson that one or more findings support, written so another site could use it. The unit the coach counts: a few hundred findings typically become 15 to 40 learnings.

### Learning Card

A one-page learning for frontline readers: what happened, why it made sense at the time, what the organisation is changing, warning signs, what good looks like and three discussion questions. See [frontline-learning-cards](skills/frontline-learning-cards.md).

### Learning Cluster

The group of findings that one function at one tier must learn from: an *entity* times a *tier* times a *relation*. See [learning-clusters](skills/learning-clusters.md).

### Level 1: Unsafe Acts

The first HFACS level: the acts and decisions at the sharp end, such as errors and deviations from the rule. Learnings at this level are about practice, never about character.

### Level 2: Preconditions

The second HFACS level: the conditions in which the acts happened, such as the state of the equipment, the environment, teamwork and communication.

### Level 3: Supervision

The third HFACS level: oversight, planning of work, correcting known problems and supervisory departures from the rules. Often the largest level in a ProbeMatrix analysis; on Hazira it holds 167 of the 436 findings.

### Level 4: Organisational Influences

The fourth HFACS level: resources, organisational climate and culture, policies and processes. Learnings here are about systems, and they need organisational fixes.

### lint_ok

A field on a pack item that accepts one language-check hit, naming the rule and the reason the rule does not apply. The reason is shown on the page. See [Language checks](Language-checks.md#accepting-a-hit).

### LR-ID

The ID of a learning in the Learnings Register, such as `LR-01`. A learning with no counterpart in a comparator report also gets an `ML-` ("missed learning") number.

## M to P

### Manifest

The workspace's bookkeeping file, `manifest.json`: fingerprints of every file and its inputs, pack check history and sign-offs. `status` reads it.

### Nanocode

The factor code in the ProbeMatrix taxonomy, such as `OIR 1.6` or `SVF 3.4`. The letters show the level and sub-category.

### Overlay

A small file of site-specific or country-specific role words added to the standard list of functions, such as `india-process-site`. Applied with `classify --overlay`.

### Pack

A learning deliverable for one audience or analysis: a JSON file the skill writes, which `check-pack` checks and `pack` renders to an offline HTML page and a Markdown file.

### Preset

A recorded set of `select` calls for a skill, run with `select --preset <skill>`. Sixteen skills have one.

### Precursor

A warning before the event that someone could have seen at the time: an inspection result, a repeated repair, an overdue schedule, an open audit action. See [precursor-timeline](skills/precursor-timeline.md).

## Q to S

### Quasi-identifier

A detail that can point to one person without naming them: a post with one holder, a gate or shift number, a date in a role string. See *singleton role*.

### Rating

The strength of a finding's causal contribution; higher is stronger. On Hazira ratings run from 2 to 4, and the *top rating* is 4.

### Redaction

Replacing personal names with roles as the export is read, with `ingest --redact`. See [Review and sharing](Review-and-sharing.md).

### Register (Learnings Register)

The formal register of learnings: one row per learning, with its evidence, HFACS level, barrier, organisational system, audiences, priority, recommendations and tier messages. Written as JSON, Markdown and Excel. See [learnings-register](skills/learnings-register.md).

### Relation

How a role relates to a factor: actor, approver, owner, absent, norm-setter, learner or expected challenger. It decides the kind of learning, for example a practice to change (actor) or a function that should exist (absent).

### Role override

Your decision about where a role belongs, kept in `role_overrides.json` and applied on every `classify`.

### Run folder

The folder for one investigation, `pmlc-runs/<date>-<site>-<event>/`, holding `workspace/` and `outputs/`. See [Files and folders](Files-and-folders.md).

### Scope

The part of a pack that says which findings it should cover, using the same filters as `select` (tiers, levels, entities, tags, a minimum rating). Coverage is measured against it.

### Share mode (`--share`)

Who a rendered copy is for: `internal` (the default), `external` or `public`. External and public copies need an approved, matching, legally cleared file, and mask identifying details. A flag of `pack`, `dashboard` and `register-xlsx`.

### Sighted comparison

A comparison with another report in which the investigation's evidence already included that report's recommendations, so matches show coverage, not independent discovery.

### Sign-off

The record that a person reviewed a file, made with `sign-off` and the reviewer's role. The agent runs it only when you say you reviewed the file.

### Singleton role

A role that points to one person, listed in `singleton_roles.json` with a general label to use instead. The language check flags it (JC7).

### Slug

The short name of a run: the site and the event in lowercase words joined by hyphens, such as `hazira-gas-release-fire`. With the date it names the run folder.

### Stale file

A workspace file built before one of its inputs changed. `status` lists it with the reason and the command to re-run.

### Status phrase

The fixed line "Learning purposes: not a statutory document" that every output carries.

### Sub-division

One of the fourteen angles (S1 to S14) a cluster dossier opens: profile, practice, conditions, supervision, system, interfaces, barriers, precursors, tier messages, recommendations, competence, transferability, comparison and formats.

## T to Z

### Taxonomy

The list of functions (entities), tiers and relations, with the role words that place a role string in each, in `taxonomy.json`. It can be copied and adapted for another kind of organisation.

### Tier

The level of the organisation that must learn: T1 frontline, T2 first-line supervision, T3 function management, T4 site leadership and T5 corporate and board. T9 means "not yet placed".

### Tier message

One short, concrete message for each tier that must act on a learning. Tier messages turn the register into a learning plan.

### Toolbox talk

A five-minute talk for a crew: an opening question, the story in 90 seconds, two warning signs, one thing to do differently and one question to the crew.

### Top-rated

The findings at the workspace's highest rating. `select --top-rated` keeps them; `run-path` prints the top rating.

### Transferability

How far a learning applies beyond the site: this site only, likely at similar sites, or enterprise-wide or industry-wide.

### Workspace

The folder of working files for one investigation (`<run>/workspace/`), made by `ingest` and filled by the other commands. Everything in it can be rebuilt from the export, except your role overrides.
