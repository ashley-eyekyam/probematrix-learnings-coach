# Learning principles (read before writing any learning)

These rules apply to every skill in this plugin. They are what make the output usable inside a real organisation.

## 1. Just culture: learning, not blame

People inside the organisation will read these outputs, including the people whose acts appear in the findings. If the text reads as blame, they will defend rather than learn, and the next report will be less honest.

- Describe acts as **practices and decisions in context** ("the replacement was pressurised to operating pressure only, without a design-pressure test"), not as character ("the fitter was careless").
- Ask **why it made sense at the time**: what pressures, norms, tools or gaps made the act reasonable to the person doing it.
- Never recommend punishment, discipline, "holding people accountable", or "consequences" as a control. If an export's text contains punitive wording, do not carry it forward.
- Never name individuals. Use roles only. If a source contains a personal name, replace it with the role.
- Prefer system fixes. "Retrain" and "remind" are the weakest controls; use them only alongside a stronger control, and say so.

## 1a. Hindsight: judge what was knowable then

An investigation knows the outcome; the people at the time did not. Outcome bias turns "this led to the fire" into "they should have seen it". Before you write a sentence about what someone did or did not do, apply the **knowable-then test**:

1. What information, cues and pressures were actually present at that moment, and who held them?
2. Would a competent person with only that information and those pressures have acted differently? If the answer needs facts that came out later, the sentence is hindsight. Rewrite it or drop it.
3. If the cue was knowable but nobody received it, the learning is about how information moves (routes, records, roles), not about the person who did not see it.

Rewrite hindsight wording as a system statement:

| Hindsight wording | Write instead |
|---|---|
| "failed to X" | "X was not done; the system did not require or support X" |
| "should have noticed / realised" | "the cue was [not] visible at that point; what made it hard to see" |
| "ignored the warning" | "the warning reached [role] without a defined response" |
| "did not follow the procedure" | "the procedure did not match the job as it was done, or was not available at the point of work" |
| "Routine Violation" (HFACS label) | "a routine deviation from the written rule, shared by the crew and not corrected" (in prose; keep the HFACS label in `hfacs_level`) |
| "complacent" / "careless" | what the task, tools or pace made normal |

Two further rules:

- **Absence of sanction is not a fix.** Do not treat "no disciplinary action was recorded" as the missing control. Describe the missing system response instead (no review of the repeat deviation, no feedback route, no check at the hold point).
- **Match the fix to the level of the cause.** An organisational condition (L4) gets an organisational fix; a supervision gap (L3) gets a change to checks and oversight. Do not close an L3 or L4 cause with an instruction to the frontline.

## 2. Ground every sentence

- Every learning cites the **Finding IDs** it rests on, and the **Evidence IDs** where a fact is stated.
- Quote evidence only from `Specific Reference` or `AI Justification` text, and keep quotes short.
- Do not add facts that are not in the export. If something important is missing, say what evidence would settle it ("[GAP] no record of who approved the substitute part").
- **Numbers rule.** Every percentage, count, duration, pressure, rating or other figure in your text must appear in a record you cite (a finding or evidence item), with the same value and unit. Do not add statistics, benchmarks or "typical" values from outside the export ("80% of such fires..."). If a figure matters but is not in the record, name the gap instead ("[GAP] no record of the test pressure"). Engineering values (set points, intervals, limits) are for the equipment owner to set.
- Label evidence strength: **direct** (a document or record states it), **corroborated** (two or more independent items), **inferred** (reasoned from the findings, not stated).

## 3. Respect the level

- An Unsafe Act (L1) learning is about practice. A Supervision (L3) learning is about oversight, checks and correction. An Organisational (L4) learning is about systems, resources, policy and culture.
- Do not turn an organisational condition into a frontline instruction. If the cause is that no procedure existed, the learning is for whoever owns procedures.

## 4. Count honestly

- Findings are instances. Several findings can describe one condition. Report **learnings**; report finding counts only as "instance-level" supporting numbers.
- Never claim one method "found more" than another without the comparison method in `comparison-method.md`.
- State what the analysis could not see. A desk analysis of a report does not replace site access, interviews or physical examination.

## 5. Mark the status

Every output carries, near the top:

> Learning purposes: not a statutory document. Derived from a ProbeMatrix investigation export; learnings are evidence-linked but should be validated by the organisation before adoption.

and at the end the branding line from `output-style.md`.

## 6. Recommendations, not action plans

Recommendations say **what should change**, the **barrier** it strengthens, the **evidence basis**, the **hierarchy-of-controls tier**, and a **leading indicator** that would show the change is working. They do not assign named owners or due dates unless the user asks; the organisation decides and implements.

**Owner wording.** Separate "owns the change" from "was involved". A learning's `owner` or recommendation's `owner` names the role that **owns the change** (holds the authority to change the system), never the role that was involved in the event. At site-leadership and board level a role can be one person, so "learning owner" reads as an accusation: write the function ("Maintenance function") rather than the post, and say "owns the change", not "was involved" or "responsible". Never write a named person; owners and due dates are still the organisation's decision.

## Interviews in a just culture

For investigators and auditors who plan interviews from these outputs:

- **Purpose.** The interview is for learning, not discipline. Say so at the start, and keep it separate from any disciplinary process.
- **Representative.** Offer the interviewee a representative or colleague to be present, and say how the notes will be used and who will see them.
- **Local rationality.** Ask what the person saw, knew and was trying to achieve, and what was normal on that shift. Ask "what made this make sense?", not "why did you do that?".
- **No leading questions.** Ask open questions first; do not put the answer in the question or use the outcome as a premise.
- **Hindsight check.** Use the counterfactual-language exercise: take a draft question and rewrite any "should have", "failed to" or "why didn't you" using the table in section 1a.
- **Follow-up tables.** Suggested-interview columns name roles only and run through `check-language` like any other text.

## Quasi-identifiers

A role string can point to one person even with no name in it: a post or gate number, a shift, a grade, or a top post with a single holder ("Plant Head"). `classify` lists these in `<ws>/singleton_roles.json` with a generalised label such as "Operations & Control Room (Supervisors)". Use the generalised label in any output that leaves the investigating team; the language check flags the raw role string (JC7, an error when sharing outside the organisation).
