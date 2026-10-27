# Language checks

The coach checks every pack and register for wording that would turn learning into blame, judge people with hindsight, name individuals, or add facts that are not in the investigation. The check has twelve rules, JC1 to JC12 ("JC" for just culture). This page explains each rule with an example the check flags and a rewrite that passes.

## Where the check runs

- [check-pack](commands/check-pack.md) and [check-register](commands/check-register.md) run it on every pack and register. An error there fails the check, so the agent fixes it before rendering.
- [check-language](commands/check-language.md) runs it alone, on a pack or a register:

```bash
pmlc check-language <ws> <run>/outputs/board-brief.json [--share internal|external|public] [--names FILE] [--orgs FILE]
```

It prints one line per hit, then a total, and exits with 1 when there is at least one error:

```text
ERROR JC2 $.sections[0].items[0].text: "careless": describe what the organisation will change so the work is safer (a check, a design change, a resourced task), not a sanction
check-language: 2 errors, 3 warnings
```

Each line gives the severity, the rule, the place in the JSON file (the path), the words that matched, and a hint for the rewrite.

**Errors and warnings.** An error must be fixed (or, if the wording is right, accepted with `lint_ok`; see below). A warning asks you to look again, and does not fail the check.

**Sharing level.** Some rules are stricter for text that leaves the organisation. The level comes from `--share` when you give it, otherwise from the file's handling classification: `external` and `public` use the external rules; `internal` and `restricted` use the internal ones.

**Names and organisations files.** `--names FILE` and `--orgs FILE` (or the `PMLC_NAMES` and `PMLC_ORGS` environment variables) give lists to look for: one entry per line, blank lines and lines starting with `#` skipped.

**What is not checked.** IDs, citations, the `scope` and `handling` blocks, `lint_ok` itself, and the HFACS labels in `hfacs_level` and `performance_mode`. An HFACS name such as "Routine Violation" in those fields is the taxonomy, not a judgement.

## The rules at a glance

| Rule | What it looks for | Internal | External or public |
|---|---|---|---|
| JC1 | personal names | error | error |
| JC2 | punitive wording | error | error |
| JC3 | counterfactuals ("failed to", "should have") | warning | warning |
| JC4 | hindsight ("obvious") | warning | warning |
| JC5 | legal conclusions ("breach", "negligent") | warning | warning |
| JC6 | only training or administrative fixes for a level 3 or 4 cause | warning (error in a frontline pack) | warning (error in a frontline pack) |
| JC7 | a role that points to one person | warning | error |
| JC8 | a percentage or duration not in the cited records | warning | warning |
| JC9 | organisation names | warning | error |
| JC10 | equipment tags | not checked | warning |
| JC11 | the status phrase is missing | error in a pack, warning in a register | the same |
| JC12 | appeals such as "stay vigilant" | warning (error in a frontline pack) | warning (error in a frontline pack) |

A **frontline pack** is one whose scope is exactly tier T1, such as the [frontline-learning-cards](skills/frontline-learning-cards.md) pack.

**Packs that make a rule an error.** A pack's profile in `pack-profiles.json` can list rules under `lint_errors`. `check-pack`, and `check-language` given that pack, then report those rules as errors for it. JC5 is an error in the [compliance-crosswalk](skills/compliance-crosswalk.md) pack, JC3 and JC4 in the [failure-to-learn-review](skills/failure-to-learn-review.md) and [learning-team-facilitator](skills/learning-team-facilitator.md) packs, and the [people-workforce-learnings](skills/people-workforce-learnings.md) profile lists JC2, which is an error everywhere. `lint_ok` with its reason still suppresses a hit.

The examples below were run through `check-language` on the Hazira workspace.

## JC1: names

Looks for a personal name: an honorific followed by a name or initials (Mr, Mrs, Ms, Dr, Shri, Smt and others), any entry in your names file, and two capitalised words together when neither is a known word: a role, a function, an HFACS term, a day of the week, or a word from the incident's title or location. Learnings use roles only.

> Example of wording the check flags (invented names, about no one in the Hazira enquiry): "Shri A. B. Example replaced the gasket." and "Jane Placeholder released the meter."

```text
ERROR JC1 $.sections[0].items[0].text: "Shri A. B. Example": use the role, not the person, e.g. "the fitter" or "the shift supervisor"; if this is not a person, add lint_ok with the reason
```

**Rewrite:** "The fitter replaced the gasket." Two capitalised words that are not a person, such as the name of a pipeline header, can be accepted with `lint_ok` (see below). Ordinary safety words such as "Control Room Operator" or "Hazira Gas Terminal" pass without one. A month word passes only as part of a date, with a day number or a year next to it ("24 May", "May 2020", "June 24, 2020"); "May Patel" or "June Kumar" is read as a name.

## JC2: punitive wording

Looks for discipline, careless, reckless, "hold … accountable", consequences, punish and "performance review". These describe a sanction or a judgement of character, not something the organisation will change. "Accountable owner" and "the consequences of …" are allowed.

> Example of wording the check flags: "The fitter was careless and faces disciplinary action."

```text
ERROR JC2 $.sections[0].items[2].text: "disciplinary": describe what the organisation will change so the work is safer (a check, a design change, a resourced task), not a sanction
```

**Rewrite:** "The return-to-service step had no check that a design-pressure test was done. Add the test record as a hold point before restart."

## JC3: counterfactuals

Looks for "failed to", "should have", "would have" and "could have prevented". These judge the past against what we now know.

> Example of wording the check flags: "The supervisor failed to check the test record."

```text
WARNING JC3 $.sections[0].items[3].text: "failed to": say what was not done and what the system did not require or support
```

**Rewrite:** "The test record was not checked; nothing in the return-to-service step required it." Write only what the cited records support.

## JC4: hindsight

Looks for "obvious", "obviously", "clearly should" and "simply needed to". What is obvious after the event was rarely obvious at the time.

> Example of wording the check flags: "The leak was obvious from the control room."

```text
WARNING JC4 $.sections[0].items[4].text: "obvious": describe what was knowable at the time and why the action made sense then
```

**Rewrite:** describe the cue as it was then, from the records: "In the control room the gas detectors showed on the annunciator panel only, with no history in the control system [EVD-8657]." The test is: what could a competent person know at that moment, with the information they had?

## JC5: legal conclusions

Looks for breach, negligence, liable, "failed to comply", "non-compliant with", illegal, unlawful and deficiency. Legal conclusions are for the competent authority, not for a learning pack.

> Example of wording the check flags: "This was a breach of the maintenance procedure."

```text
WARNING JC5 $.sections[0].items[5].text: "breach": describe the gap against the requirement ("the procedure did not require X") and leave legal conclusions to the competent authority
```

**Rewrite:** "The maintenance procedure did not require a design-pressure test after a gasket change."

## JC6: retraining only

Looks at recommendations and barriers. It flags an item whose only control tier is training or administrative while a finding it cites sits at level 3 (Supervision) or level 4 (Organisational Influences). A supervision or organisational cause needs a change at its own level. In a frontline pack this is an error, because it hands the crew a fix for something only the organisation can change.

> Example of wording the check flags: a recommendation "Remind supervisors of the test requirement", with `hoc_tier` "training", citing a level 4 finding.

```text
WARNING JC6 $.sections[0].items[6].hoc_tier: "training": the cited cause sits at level 3 or 4 and every control here is training or administrative: add a change at the cause's level (elimination, substitution or engineering), or, if the administrative change is itself the system fix, add lint_ok with the reason
```

**Rewrite:** add a stronger control, for example "Interlock the restart on a signed test record" (engineering). If an administrative change really is the system fix, such as a new decision rule in the emergency plan, accept it with `lint_ok` and say why. The committed Hazira register gives two JC6 warnings.

## JC7: a role that points to one person

Looks for any role listed in the workspace's `singleton_roles.json`: a role with an instance number or letter (such as a gate, post or shift number), or the sole role of its tier in Plant & Asset Leadership or Corporate & Board; group roles and dates alone never count. The full rule is in [Files and folders](Files-and-folders.md#singleton-roles). Even without a name, such a role identifies a person. It is a warning inside the organisation and an error when shared outside.

> Example of wording the check flags: "The Director Offshore (approval authority) signed the change."

```text
WARNING JC7 $.sections[0].items[7].text: "Director Offshore (approval authority)": this role has one holder, so it points to a person: use the generalised role label
```

**Rewrite:** use the general label from `singleton_roles.json`: "The corporate approval function signed the change", or "Corporate & Board (Corporate / board)".

## JC8: outside facts

Looks for percentages and durations, and checks each number against the records the item cites. If the number is not there, it may be an outside fact. Indicators and their measures (`leading_indicator`, `indicator`, `measure`, `deterioration`) are not checked for numbers, because they are proposals, not claims about the incident. Nor are the time settings of a delivery: a toolbox talk's or module's `duration` ("5 min"), a script segment's `seconds` and a drill inject's `offset`.

> Example of wording the check flags: "The meter leaked within 45 minutes of the restart." and "80% of such joints fail."

```text
WARNING JC8 $.sections[0].items[0].text: "45 minutes": cite the record that gives this number, or take it out; add no outside facts
```

**Rewrite:** cite the record that gives the figure, or drop it: "The meter leaked within a year of the earlier gasket change [EVD-1494]." For an engineering value the records do not give, write a decision for the technical authority instead.

## JC9: organisation names

Looks for names from your organisations file, and names that end in Ltd, Pvt, Inc, GmbH, LLC or Limited. A warning inside the organisation, an error when shared outside.

> Example of wording the check flags: "The O-rings came from Acme Seals Pvt Ltd."

```text
WARNING JC9 $.sections[0].items[9].text: "Acme Seals Pvt Ltd.": name the organisation by its function, e.g. "the operator" or "the seal supplier"
```

**Rewrite:** "The O-rings came from a local supplier."

## JC10: equipment tags

Only when shared outside. Looks for equipment tags: letters then digits, such as `PSV-101` or `AO-101`. Finding, Evidence and learning IDs are not tags.

> Example of wording the check flags (with `--share public`): "Valve PSV-101 lifted."

```text
WARNING JC10 $.sections[0].items[1].text: "PSV-101": describe the equipment generically, e.g. "the condensate meter", before sharing outside
```

**Rewrite:** "The relief valve lifted."

## JC11: the status phrase

Every pack and register must say "Learning purposes: not a statutory document" in its `status`. Missing in a pack is an error; missing in a register is a warning, because the register's renderers add the phrase themselves.

> Example of wording the check flags: a pack whose status reads only "Draft learnings".

```text
ERROR JC11 $.status: "": must contain "Learning purposes: not a statutory document"
```

**Rewrite:** `"status": "Learning purposes: not a statutory document"`.

## JC12: appeals instead of changes

Looks for "be careful", "be more careful", "pay attention", "stay vigilant", "remain alert" and "take ownership". An appeal to try harder changes nothing about the work. In a frontline pack this is an error.

> Example of wording the check flags (in a frontline pack): "Crews must stay vigilant near meters."

```text
ERROR JC12 $.sections[0].items[2].text: "stay vigilant": replace the appeal with a change to the work: a check, a hold point, an alarm or a tool
```

**Rewrite:** state a change to the work, for the site to decide, for example "A gas detector alarm at the meter area now starts an isolation check by the shift crew."

## Accepting a hit

Sometimes the wording is right and the rule does not apply: two capitalised words that name a place, or an administrative change that is the system fix. Then add `lint_ok` to that item, naming the rule and the reason:

```json
{"kind": "para", "text": "Gas went to Kribhico Header through the LP line.",
 "lint_ok": {"rule": "JC1", "reason": "Kribhico Header is a pipeline header, not a person"},
 "cites": ["FND-3AB996FC"]}
```

- `lint_ok` covers one item (or one bottom-line entry or register row) and the rule it names. Give a list of `{rule, reason}` objects for more than one rule. On a section or at the top of the file it is an error and accepts nothing.
- The reason must not be empty. An empty reason, or a rule that is not JC1 to JC12, is itself an error and accepts nothing:

```text
ERROR lint_ok $.sections[0].items[2].lint_ok.reason: "": give the reason the rule does not apply here
```

- The reason is shown on the page, so readers see why the wording was kept.
- Fix the wording first. `lint_ok` is for words that are right, not a way to keep blame.

## A worked fix (Hazira)

A draft paragraph for a Hazira board brief read:

> Example of wording the check flags: "The maintenance crew failed to carry out a hydro test, which was obviously careless, and the team should have been held accountable."

`check-language` printed `check-language: 2 errors, 3 warnings`: JC2 for "careless" and "held accountable", JC3 for "failed to" and "should have", and JC4 for "obviously". The rewrite, built from the cited evidence (FND-3AB996FC, EVD-2894), read:

"No hydro test was done after the gasket was replaced; the system was pressurised to operating pressure only. No return-to-service procedure required a design-pressure test."

It gave `check-language: 0 errors, 0 warnings`.

For the principles behind the rules, see the [learning principles](https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/skills/learnings-coach/references/learning-principles.md), sections 1 and 1a. The rule patterns are in [lint-terms.json](https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/skills/learnings-coach/references/lint-terms.json).
