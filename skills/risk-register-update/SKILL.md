---
name: risk-register-update
description: Proposes risk-register and bow-tie changes from a ProbeMatrix investigation export for enterprise risk management - ERM leads, risk owners and insurers' risk engineers - each change with the current assumption, what the evidence says and the proposed change - missing threats, control ratings to revisit, risks accepted without authority, and key risk and control indicators - plus the barriers for the bow-tie, written as proposals for the risk owner with no loss estimates, no rating decisions and no owners or dates, and exported as a risk-changes CSV and a bow-tie CSV for the organisation's risk tool. Use when someone has a ProbeMatrix export and asks what should change in the risk register, which risks or controls the incident shows were mis-rated, which key risk indicators to add, or what to tell the insurer's risk engineer. Not for the barrier-by-barrier analysis of which defences failed (use `barrier-learnings`) or the board's assurance questions (use `board-brief`).
---

# Risk Register Update

Audience: enterprise risk management (`enterprise-risk`, tier T4): ERM leads, risk owners and, as a second
audience, insurers' risk engineers. The pack **proposes**; the risk owner assesses and decides. It never rates a
risk, never estimates a loss and never names an owner or a date.

## Before you start

Engine: `PMLC` as defined in `skill-common.md` §1 (needs the `learnings-coach` skill installed alongside it).

- Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions).
- Needs: **workspace**. Optional: the register.
- Read `learnings-coach/references/learning-principles.md`, and `learnings-coach/references/barriers-and-controls.md`
  for the barrier names and sides of the bow-tie section.
- **Start from the register if present.** In `<run>/outputs/learnings-register.json`, take the entries whose
  findings are risk-coded (below) or whose `barrier` the risk register would hold: keep their wording and carry
  `learning: "LR-nn"`.
- Ask once whether the organisation's **risk register or bow-tie** is to hand. If it is, name its risk in `risk` as
  the register writes it; if not, name the risk plainly ("Loss of containment at the gas metering skid").

## Gather

```bash
PMLC select <ws> --code "OIC 2.7" "OIP 3.2" "SVF 3.4" "SVI 1.8" "SVIO 2.4" "SVV 4.5" --brief   # risk-management codes
```

- **The `--code` list** is every code in this export whose name contains "risk", written out as literal codes. For
  another export, rebuild it from the `code` and `name` of each finding in `<ws>/findings.json`. On Hazira it is 6
  codes and 68 findings.
- The taxonomy has no barrier entity tag, so the gather has no tag filter. For the bow-tie section, take the barriers
  the risk-coded findings name; a `barrier-learnings` pack in `<run>/outputs/`, if there is one, gives the same names.
- Read each finding's justification for what the organisation **assumed** about the risk (a control in place, a
  risk assessed, an action approved) and what the evidence **shows**. That pair is a `risk_change`.

## Write

Pack `<run>/outputs/risk-register-update.json` (shape: `learnings-coach/references/pack-schema.md`),
`"scope": {"tiers": [], "levels": [2, 3, 4], "tags": []}`.

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | The changes the risk owner should look at first, one line each | `bottom_line` | up to 5 |
| 1 | `banner` | About this pack | Exactly "Proposals for the risk owner to assess: no loss estimates and no rating decisions." | `para` | 1 |
| 2 | `risk-changes` | Proposed risk-register changes | One per change: `id`, `risk`, `change_type`, `current_assumption`, `evidence_says`, `proposed_change`, `cites`; `learning` where the register has it | `risk_change` | up to 15 |
| 3 | `kri` | Key risk and control indicators | `name`, `measure` (what is counted, from which record), `deterioration` (what a worsening looks like); no owner | `indicator` | up to 8 |
| 4 | `bowtie` | Barriers for the bow-tie | `group` = "Prevention" or "Mitigation", `barrier`, `type`, `state`, `failure_mode`, `fix`, `hoc_tier`; no owner | `barrier` | optional, up to 10 |

**`change_type`**, one of five (`pack-schema.md`):
- `missing-threat`: a threat or cause the incident shows that the register does not hold (a seal substitution, an
  inaccessible isolation valve);
- `control-rating`: a control the register would rate as effective, which the evidence shows absent, degraded or
  unused (an MOC procedure not used since 2018): propose that the rating be revisited, never the new rating;
- `accepted-without-authority`: a risk carried, or an action deferred, without the approval the procedure requires;
- `kri`: an indicator the register should carry; put the measure itself in the `kri` section;
- `other`: anything else; say what in `proposed_change`.

Write one item per change for each type the evidence supports. Group findings that describe one condition into one
item (count learnings, not finding instances).

- **Proposals only.** `proposed_change` says what to add, review or reassess ("add the threat", "reassess the
  rating against the 2018–2020 records"), never a score, a likelihood or a consequence class.
- **No cost figures (JC8).** The export holds no cost or loss data: never estimate one, and say so in `limits`.
- **No owner, date or decision (D7).** `no-owner-due` makes any `owner` or `by_when` a problem even without
  `--strict`. The risk owner fills the `risk_owner_decision` column of the CSV.
- **Roles only** in `current_assumption` and `evidence_says`.

```json
{"kind": "risk_change", "id": "rc-moc-rating", "risk": "Uncontrolled change to hydrocarbon equipment",
 "change_type": "control-rating", "current_assumption": "Changes go through the 2016 MOC procedure.",
 "evidence_says": "No MOC had been implemented since 2018 [EVD-2986].",
 "proposed_change": "Reassess the MOC control's rating against its use since 2018.", "learning": "LR-06",
 "cites": ["FND-…", "EVD-2986"]}
```

Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/risk-register-update.json (repository only)

## If the evidence is thin

- **No risk-coded findings:** rebuild the list from the level 3 and 4 findings that describe a risk assessment, an
  accepted hazard or an unclosed action, and say in `limits` that the export carries no risk-management codes.
- **A change type with no evidence:** leave it out; never write an item to fill a type.
- **No barrier named:** leave the `bowtie` section out.
- `skill-common.md` §6 covers the rest.

## Not covered here

- Which barriers failed, their states and the strength of each fix: `barrier-learnings`.
- The board's assurance questions and decisions: `board-brief`.
- Risk scoring, loss estimates, insurance terms and the decision on each proposal: the risk owner's, outside
  ProbeMatrix.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/risk-register-update.json --strict
PMLC pack <ws> <run>/outputs/risk-register-update.json
PMLC pack <ws> <run>/outputs/risk-register-update.json --format risk-csv,bowtie-csv   # the risk tool's two CSVs
```

- **risk-csv** (`risk-register-update.risk-changes.csv`): one row per `risk_change`, with the
  `risk_owner_decision` column blank for the risk owner. **bowtie-csv** (`risk-register-update.bowtie.csv`): one
  row per barrier, threat side for Prevention and consequence side for Mitigation. Neither carries a status line:
  send them with the pack.
- Tell the user how many changes of each type the pack proposes, and that every decision stays with the risk owner.
