# ProbeMatrix Learnings Coach user manual

The Learnings Coach turns one **ProbeMatrix investigation export** (an `.xlsx` file) into learnings for every part and level of an organisation: frontline crews, supervisors, managers, site leaders, top management, the board, auditors, investigators, trainers, emergency responders, engineers, the supply chain and workforce representatives.

ProbeMatrix by Eyekyam is a human-in-the-loop, AI-assisted incident investigation service built on the four-level Human Factors Analysis and Classification System (HFACS). The coach reads what that investigation found and helps you share the learning. It does not investigate, and every output is marked *Learning purposes: not a statutory document*.

## Who this manual is for

- **HSE professionals, investigators and managers** who want learnings from an investigation. Start with [Getting started](Getting-started.md), then [Workflows and recipes](Workflows-and-recipes.md).
- **People who review or share outputs** before they leave the team. Read [Review and sharing](Review-and-sharing.md) and [Language checks](Language-checks.md).
- **People who run the engine by hand or in a script.** The [command reference](Commands.md) covers every command and every option.
- **Contributors and maintainers.** See [Developer tools](Developer-tools.md).

You do not need to type commands to use the coach. In Claude Code, Codex or another agent, you share the export and ask for what you need ("a board brief", "learning cards for the crews"). The agent runs the commands described here for you. This manual tells you what it is doing, so you can check it.

When the request is broad ("what should we learn from this?"), the agent asks what the learnings are for, one question at a time, then proposes a **plan**: one of nine workflow presets, such as `leadership` or `full-cascade`, as a numbered list of steps. Nothing runs until you say OK, and each step must pass its check before the next starts. See [Let the coach plan the work](Workflows-and-recipes.md#let-the-coach-plan-the-work) and [Pick a workflow preset](Workflows-and-recipes.md#pick-a-workflow-preset).

## How the manual is organised

| Page | What it covers |
|---|---|
| [Getting started](Getting-started.md) | Install, your first run on the Hazira sample, what you get |
| [Workflows and recipes](Workflows-and-recipes.md) | Common jobs from start to finish |
| [Skills](Skills.md) | The 23 skills: which audience each serves and what it produces |
| [Commands](Commands.md) | Every engine command, flag by flag, with real examples |
| [Files and folders](Files-and-folders.md) | The run folder, the workspace, the outputs, the files your organisation fills in and the shared contracts |
| [Review and sharing](Review-and-sharing.md) | Draft status, sign-off by a reviewer, sharing outside the organisation |
| [Language checks](Language-checks.md) | The just-culture and grounding checks (JC1 to JC12) |
| [Troubleshooting](Troubleshooting.md) | Messages you may see and what to do |
| [Glossary](Glossary.md) | HFACS levels, clusters, tiers, relations and other terms |
| [Developer tools](Developer-tools.md) | Repository tools, the eval runner and environment variables |

## The worked example

Every example in this manual uses the public **Hazira sample**: the hydrocarbon release and fire at the gas terminal of ONGC's Hazira plant on 24 September 2020, analysed from the published PNGRB enquiry report. Its export has 436 findings and 46 evidence items. You can find it in the repository at [samples/2020-09-24-hazira-gas-release-fire](https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/samples/2020-09-24-hazira-gas-release-fire/README.md). The investigation is still marked *in progress*, so everything made from it stays a draft.

The output shown on each page is real output from running the command on that sample, trimmed where it is long (shown with `…`).

## Three rules the coach always follows

1. **Grounded.** Every learning cites the Finding IDs and Evidence IDs it comes from. Nothing is added from outside the export.
2. **Just culture.** Roles only, never personal names; no blame or punishment language; system fixes before retraining.
3. **A person decides.** The coach drafts. A reviewer reads, edits and signs off. An owner is always a role that owns the change, never a person, and the coach leaves owners and due dates to you unless you ask. The files your organisation fills in (adoption, distribution, verification and the actions export) are written with their owner, date and response columns blank.

## More

- [README](https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/README.md): what the project is and what is new.
- [Installation guide](https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/docs/INSTALL.md).
- [AGENTS.md](https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/AGENTS.md): instructions for coding agents.
- Contact: ashley@eyekyam.com.
