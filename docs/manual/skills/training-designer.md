# training-designer

Training designed from the investigation, for training managers, instructors and competence assessors: a training-needs map by role and tier, case-based modules for crews, supervisors and managers, scenario exercises, assessment questions with answer keys (also as a spreadsheet), and a cascade plan. The investigation becomes curriculum rather than a one-off briefing.

## What it is for

- A training needs analysis from a ProbeMatrix export.
- A training module, a lesson plan or e-learning content.
- Assessment or quiz questions, and competence gaps.
- Case-study training from an incident.

Training is the weakest control on its own. This skill designs it alongside the system fixes, never instead of them, and sends needs that training cannot fix to [manager-coach](manager-coach.md). Short crew briefings come from [frontline-learning-cards](frontline-learning-cards.md).

## How to start it

- "Design a training module for fitters from this investigation, with an assessment."
- "What are the training needs by role, including supervisors and managers, and which of them are really system problems?"
- "Write ten assessment questions with answer keys, including some on the level of each cause, as a spreadsheet for our learning system."

## What it needs

- `clusters.json`, which `setup` (or the hub's classify step) builds. This skill reads it but never re-runs classify.
- Optional: the Learnings Register (learnings and `LR-nn` ids for the modules and questions).

## Engine commands and flags

```bash
pmlc select <ws> --text "train|competen|qualif|knowledge|experience|familiar|skill" --brief
pmlc select <ws> --level 1 2 --brief                    # crew modules: acts and individual conditions
pmlc select <ws> --tag people --level 3 4 --brief       # the competence system (HR, training and competence)
pmlc select <ws> --tier T2 T3 --level 3 4 --top-rated --brief --budget-chars 30000   # supervisor and manager modules
pmlc select <ws> --preset training-designer             # the four calls above at once
pmlc check-pack <ws> <run>/outputs/training-designer.json --strict
pmlc pack <ws> <run>/outputs/training-designer.json
pmlc pack-xlsx <ws> <run>/outputs/training-designer.json --kind question
pmlc pack <ws> <run>/outputs/training-designer.json --format gift,qti,quiz-csv        # quiz files for an LMS
pmlc pack <ws> <run>/outputs/training-designer.json --format html,docx --view learner  # the learner's copy
pmlc pack <ws> <run>/outputs/training-designer.json --format srt,narration            # subtitles and voice-over
pmlc templates <ws> distribution                        # the training record, once per run
```

- [select](../commands/select.md): `--text` a regular expression over the finding text (words about training and competence); `--level 1 2` the Unsafe Acts and Preconditions levels; `--tag people` the HR, training and competence function; `--tier T2 T3` the supervision and management tiers; `--level 3 4` the Supervision and Organisational levels; `--top-rated` the strongest; `--budget-chars` caps the output size; `--brief` short entries.
- [check-pack](../commands/check-pack.md) with `--strict` checks the pack against its profile, including an answer key and a cited finding on every assessment question; [pack](../commands/pack.md) renders it.
- [pack-xlsx](../commands/pack-xlsx.md) with `--kind question` writes `training-designer-questions.xlsx`: one row per assessment question, with what it tests, the answer key, good evidence and cites.
- [pack](../commands/pack.md) `--format gift,qti,quiz-csv` writes the assessment for a learning-management system: `training-designer.gift.txt` (Moodle GIFT), `.qti.zip` (QTI 2.1) and `.quiz.csv`. They carry the answer keys. Once the engine lists `scorm` in `pack -h`, `--format scorm` also builds a SCORM 1.2 package from the learner view, scored on the typed questions with a pass mark of 80%.
- [pack](../commands/pack.md) `--view learner` writes `training-designer.learner.html` and `.learner.docx` with the answers, good evidence and correct-option flags left out, for trainees.
- [pack](../commands/pack.md) `--format srt,narration` writes, for each `script` item, subtitles (`training-designer.<item-id>.srt`) and the narration alone (`.narration.txt`), for a video, radio or PA message.
- [templates](../commands/templates.md) `distribution` writes `distribution.csv`, where each session is recorded. It never overwrites an existing file.

## What you get

`training-designer.html` and `.md`:

1. a **training-needs map**: role groups against competences, each row citing findings, and each need marked "Competence gap" or "System problem: send to manager-coach";
2. up to six **modules**: audience, observable objectives, duration, case material (roles only), activities, how competence is checked, and two lines for the organisation's competence system: the competence-standard id and the refresher interval ("to be set by the competence system owner" unless the export or you give them);
3. up to three **scenario exercises** with facilitator notes;
4. up to fifteen **assessment questions** with answer keys and the finding each tests. A scored question has a type (single choice, multiple choice, true or false, or short answer) and its options; one without a type is a discussion question, unscored;
5. a **cascade plan**: who trains whom, the materials, and a measure of transfer at 90 days;
6. optionally, up to three **video and radio scripts**: a `script` item is a shooting script, a table of visual and narration with each segment's time and the total duration, for a short film, a radio or PA message, or a screen.

The pack scope follows the modules: levels 1 and 2 for crew modules, widened to levels 3 and 4 when there is a supervisor or manager module. The quiz files, the learner copy, the subtitles and a Word document come from the engine's formats above.

## Worked example (Hazira)

The training-words search returned 122 findings and `--level 1 2 --brief` returned 128. `--tag people --level 3 4 --brief` returned 21 (F12 HR, Training & Competence has 12 level 3 and 9 level 4 findings on Hazira and only one below, so its gaps appear only once the scope reaches levels 3 and 4), and the supervisor and manager selection matched 100, keeping the 51 top-rated that fit its 30,000-character budget. A scenario could start from the return-to-service gap: "the gasket is replaced and no design-pressure test is arranged: what do you do?", built on FND-3AB996FC. Where the cause is that no procedure required the test, the map marks it as a system problem, not a competence gap.

These counts are from the base classification, before the resolution pass. After you place the remaining roles they will be higher, most for T3 (in one trial pass on Hazira, roughly T1 222→231, T2 237→238, T3 211→257; your numbers depend on how you place roles).

## Related skills

- [frontline-learning-cards](frontline-learning-cards.md): the cards a module can build on.
- [manager-coach](manager-coach.md): where system problems go.
- [investigator-coach](investigator-coach.md): exercises for investigators.
