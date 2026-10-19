# Learning principles (read before writing any learning)

These rules apply to every skill in this plugin. They are what make the output usable inside a real organisation.

## 1. Just culture: learning, not blame

People inside the organisation will read these outputs, including the people whose acts appear in the findings. If the text reads as blame, they will defend rather than learn, and the next report will be less honest.

- Describe acts as **practices and decisions in context** ("the replacement was pressurised to operating pressure only, without a design-pressure test"), not as character ("the fitter was careless").
- Ask **why it made sense at the time**: what pressures, norms, tools or gaps made the act reasonable to the person doing it.
- Never recommend punishment, discipline, "holding people accountable", or "consequences" as a control. If an export's text contains punitive wording, do not carry it forward.
- Never name individuals. Use roles only. If a source contains a personal name, replace it with the role.
- Prefer system fixes. "Retrain" and "remind" are the weakest controls; use them only alongside a stronger control, and say so.

## 2. Ground every sentence

- Every learning cites the **Finding IDs** it rests on, and the **Evidence IDs** where a fact is stated.
- Quote evidence only from `Specific Reference` or `AI Justification` text, and keep quotes short.
- Do not add facts that are not in the export. If something important is missing, say what evidence would settle it ("[GAP] no record of who approved the substitute part").
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

## Quasi-identifiers

A role string can point to one person even with no name in it: a post or gate number, a shift, a grade, or a top post with a single holder ("Plant Head"). `classify` lists these in `<ws>/singleton_roles.json` with a generalised label such as "Operations & Control Room (Supervisors)". Use the generalised label in any output that leaves the investigating team; the language check flags the raw role string (JC7, an error when sharing outside the organisation).
