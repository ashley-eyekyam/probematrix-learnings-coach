# risk-register-update

Proposed risk-register and bow-tie changes for enterprise risk management: ERM leads, risk owners and, as a second audience, insurers' risk engineers. Each change sets what the organisation assumed about a risk beside what the evidence shows, and proposes what to add, review or reassess: missing threats, control ratings to revisit, risks accepted without authority, and key risk and control indicators. The pack ends with the barriers for the organisation's bow-tie, and it exports two CSV files for the risk tool.

## What it is for

- "What should change in our risk register after this incident?"
- Which threats the register missed, and which controls the incident shows were rated higher than the evidence supports.
- Which risks were carried, or actions deferred, without the approval the procedure requires.
- Which key risk indicators to add, and what to tell the insurer's risk engineer.

The pack proposes; the risk owner decides. It opens with the fixed line "Proposals for the risk owner to assess: no loss estimates and no rating decisions." It never rates a risk, never estimates a loss (the export holds no cost data, and cost wording is language rule JC8) and never names an owner or a date: the `no-owner-due` rule makes any `owner` or `by_when` a problem in this pack even without `--strict`.

## How to start it

- "Using this ProbeMatrix export, what changes should our ERM team make to the gas terminal's risk register?"
- "Which of our controls did this incident show were over-rated, and which risks were accepted without the right sign-off?"
- "Give me the risk-register changes from this investigation as a CSV our risk tool can import."

## What it needs

- The workspace. The skill reads the risk-coded findings: every code in the export whose name contains "risk".
- Optional: the Learnings Register. Changes that express a register learning carry its `LR-nn` id and keep its wording.
- Optional: the organisation's risk register or bow-tie, so each change names the risk as the register writes it.
- The default scope is HFACS levels 2 to 4.

## Engine commands and flags

```bash
pmlc select <ws> --code "OIC 2.7" "OIP 3.2" "SVF 3.4" "SVI 1.8" "SVIO 2.4" "SVV 4.5" --brief
pmlc select <ws> --preset risk-register-update          # the same call
pmlc check-pack <ws> <run>/outputs/risk-register-update.json --strict
pmlc pack <ws> <run>/outputs/risk-register-update.json
pmlc pack <ws> <run>/outputs/risk-register-update.json --format risk-csv,bowtie-csv
```

- [select](../commands/select.md): `--code` takes the literal codes whose names contain "risk" in this export (rebuild the list for another export from `findings.json`); `--brief` gives short entries. The taxonomy has no `barrier` entity tag, so there is no `--tag` line.
- [check-pack](../commands/check-pack.md) with `--strict` checks the pack against its profile: the banner line (`banner:risk`) and no owners or due dates (`no-owner-due`).
- [pack](../commands/pack.md) `--format risk-csv` writes `risk-register-update.risk-changes.csv`, one row per `risk_change` item with the `risk_owner_decision` column left blank for the risk owner (an existing file is never overwritten: move it or pass a new `--out`); `--format bowtie-csv` writes `risk-register-update.bowtie.csv`, one row per barrier, threat side for Prevention and consequence side for Mitigation. Neither file carries a status line, so send them with the pack.

## What you get

`risk-register-update.html` and `.md`:

1. **About this pack**: the fixed line "Proposals for the risk owner to assess: no loss estimates and no rating decisions.";
2. **proposed risk-register changes**: one `risk_change` item per change, each with the risk, the change type (`missing-threat`, `control-rating`, `accepted-without-authority`, `kri` or `other`), the current assumption, what the evidence says and the proposed change;
3. **key risk and control indicators**: what to count, from which record, and what a worsening looks like;
4. optional **barriers for the bow-tie**: prevention and mitigation barriers with their state on the day, failure mode and fix, without owners.

## Worked example (Hazira)

`select --code` with the six Hazira risk codes returned 68 findings. The pack proposes 13 changes. Three are missing threats: repeat seal failure on the 1986 meter (FND-E0AE86A6, EVD-1494, LR-05), a vapour cloud that denies access to manual isolation (FND-05841EDA, EVD-3932, LR-09) and an indirect warning path from perimeter security (FND-0A64F629, LR-13). Six are control ratings to revisit, among them management of change, unused since 2018 (FND-3FEE59DF, EVD-2986, LR-06), and the emergency plan, which named the leak scenario but held no isolation criteria (FND-730D0DCA, EVD-4052, LR-07). Two are risks accepted without authority: the locally bought O-ring with no record of who decided the switch (FND-EBB66554, EVD-8645, LR-01) and twelve external-audit actions extended without the required approval (FND-856F80CE, EVD-6852, LR-21). Two propose indicators. Six key risk indicators and nine bow-tie barriers follow. The pack gives no loss estimate, because the export holds no cost data.

## Related skills

- [barrier-learnings](barrier-learnings.md): which barriers failed, their states and the strength of each fix; its barriers use the same names.
- [board-brief](board-brief.md): the board's assurance questions and decisions.
- [top-management-brief](top-management-brief.md): the enterprise decisions that sit above the risk register.
