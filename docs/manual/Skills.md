# Skills

The Learnings Coach is 35 agent skills that share one engine. You rarely need to name a skill: describe what you want and who it is for, and the hub skill picks the right one. This page lists every skill, grouped by the audience it serves. Each name links to the skill's own page.

**Start here:** [learnings-coach](skills/learnings-coach.md) sets up the workspace for an export and routes your request. Every other skill relies on it.

## Set-up and analysis

These skills prepare the ground or analyse the whole investigation. Their outputs feed the audience packs.

| Skill | What it gives you | Typical request |
|---|---|---|
| [learnings-coach](skills/learnings-coach.md) | workspace, profile, routing | "What should we learn from this export?" |
| [learning-clusters](skills/learning-clusters.md) | findings by function, level and relation; unplaced roles resolved | "Who in the organisation should learn?" |
| [organisation-learning-map](skills/organisation-learning-map.md) | offline dashboard and rollout plan | "Who needs to learn what?" |
| [learnings-register](skills/learnings-register.md) | the Learnings Register in JSON, Markdown and Excel | "A lessons-learned register in Excel" |
| [cluster-learning-dossier](skills/cluster-learning-dossier.md) | every learning for one function | "What does maintenance need to learn?" |
| [causal-map](skills/causal-map.md) | causal graph and pathway stories | "How do the factors connect?" |
| [latent-conditions-profile](skills/latent-conditions-profile.md) | HFACS heat map, the factors that recur and feed the most others | "Which conditions keep coming up?" |
| [precursor-timeline](skills/precursor-timeline.md) | dated warnings and how they were handled | "Did we see this coming?" |
| [failure-to-learn-review](skills/failure-to-learn-review.md) | why earlier warnings did not lead to change, and which step of the learning cycle broke | "Why didn't we learn from the earlier leaks?" |
| [interface-learnings](skills/interface-learnings.md) | what fell between departments | "What fell through the cracks?" |
| [barrier-learnings](skills/barrier-learnings.md) | failed barriers and how strong the fixes should be | "Why didn't our safeguards work?" |
| [nine-m-analysis](skills/nine-m-analysis.md) | a question-by-question 9M analysis: which part of the work system each condition belongs to, with a direction of change per M | "Work through the 9Ms with me" |
| [recommendation-strength-review](skills/recommendation-strength-review.md) | how strong the register's (and the 9M analysis's) recommendations are, which deep causes get only a weak fix, and directions for stronger change | "How strong are these corrective actions?" |
| [report-comparison](skills/report-comparison.md) | a fair comparison with an official report | "Compare this with the enquiry report" |
| [compliance-crosswalk](skills/compliance-crosswalk.md) | which clauses of ISO 45001, PSM, RBPS or another framework the learnings speak to | "Which ISO 45001 clauses does this cover?" |
| [open-questions-register](skills/open-questions-register.md) | what the investigation could not answer, with a follow-up CSV for the export | "What is still open in this investigation?" |
| [evidence-strength-scorecard](skills/evidence-strength-scorecard.md) | how well each finding is evidenced, and the evidence that would strengthen it | "How solid is the evidence behind these findings?" |

## By level of the organisation

One skill for each tier, from the sharp end to the board.

| Audience | Tier | Skill | What it gives you |
|---|---|---|---|
| Operators, technicians, fitters, crews, security staff | T1 | [frontline-learning-cards](skills/frontline-learning-cards.md) | Learning Cards, toolbox talks, a "stop and ask" list |
| Shift in-charges, supervisors, permit issuers, signatories | T2 | [supervisor-coach](skills/supervisor-coach.md) | checklists, hold points, what to refuse |
| Department and function managers | T3 | [manager-coach](skills/manager-coach.md) | system learnings, indicators, a 90-day agenda |
| Plant manager, site leadership team | T4 | [site-leadership-coach](skills/site-leadership-coach.md) | decisions, trade-offs, culture signals, a workshop |
| CEO, executive committee, corporate functions | T5 | [top-management-brief](skills/top-management-brief.md) | transferability, policy, enterprise decisions |
| The board and its safety or risk committee | T5 | [board-brief](skills/board-brief.md) | governance learnings, questions to ask, assurance |

## By specialist audience

| Audience | Skill | What it gives you |
|---|---|---|
| Auditors, inspectors, certification bodies, insurers | [auditor-assurance-pack](skills/auditor-assurance-pack.md) | audit test points, sampling, evidence requests |
| Investigators and HSE professionals | [investigator-coach](skills/investigator-coach.md) | evidence gaps, key questions, interviews, method lessons |
| Training managers and instructors | [training-designer](skills/training-designer.md) | training-needs map, modules, assessments |
| Fire services, emergency teams, incident command | [emergency-response-learnings](skills/emergency-response-learnings.md) | response timeline, plan gaps, drills |
| Engineering, integrity, change control, instrumentation | [engineering-integrity-learnings](skills/engineering-integrity-learnings.md) | technical learnings and pending decisions |
| Procurement, stores, vendors, contractors | [supply-chain-contractor-learnings](skills/supply-chain-contractor-learnings.md) | sourcing and contractor learnings |
| Enterprise risk management, risk owners, insurers' risk engineers | [risk-register-update](skills/risk-register-update.md) | proposed risk-register and bow-tie changes, as proposals for the risk owner |
| HR, workforce planners, rostering and competence-framework owners | [people-workforce-learnings](skills/people-workforce-learnings.md) | people-system learnings and competence-framework changes |
| Leaders and peer supporters responding to the people involved | [restorative-response-guide](skills/restorative-response-guide.md) | restorative questions to ask, obligations and second-victim support |
| HSE managers and advisers at the organisation's other sites | [could-it-happen-here](skills/could-it-happen-here.md) | a self-assessment for each site, with a return template and a consolidated view of coverage and conditions |
| Other sites and peer organisations | [safety-alert](skills/safety-alert.md) | a one-page alert graded alert, notice or information, with what to check now |
| Safety committees and workforce representatives | [safety-committee-guide](skills/safety-committee-guide.md) | a discussion guide and questions to raise |

## What every skill does the same way

- It reads the findings through the engine's [select](commands/select.md) command, with filters for tier, level, function and rating. Twenty-two skills also have a recorded **preset** (`pmlc select <ws> --preset <skill>`) that runs the same gather calls in one go.
- It writes a **pack**: a JSON file the engine checks with [check-pack](commands/check-pack.md) and renders with [pack](commands/pack.md) to an offline HTML page and a Markdown file. The register skill writes a register instead.
- It follows the [learning principles](https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/skills/learnings-coach/references/learning-principles.md): roles only, no blame, every sentence traced to Finding and Evidence IDs, learnings counted rather than finding instances.
- Its outputs are marked "Learning purposes: not a statutory document" and stay **draft** until a person signs them off (see [Review and sharing](Review-and-sharing.md)).

For ready-made sequences of skills, see [Workflows and recipes](Workflows-and-recipes.md). Each page uses the words in the [Glossary](Glossary.md).
