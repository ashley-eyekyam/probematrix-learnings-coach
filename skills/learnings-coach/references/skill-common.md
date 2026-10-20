# Skill common reference (every skill links this)

What every skill in this plugin does the same way. A SKILL.md says only what is particular to it and points here
for the rest. Read [`learning-principles.md`](learning-principles.md) before writing any learning.

## 1. Engine and paths

- **Engine.** `PMLC = python3 <skills-root>/learnings-coach/scripts/pmlc.py` (Python 3.9+, needs `openpyxl`:
  `pip install openpyxl`). `<skills-root>` is the folder that holds the skills. Every skill needs the
  `learnings-coach` folder installed beside it: the engine and the shared references live there.
- **References** are `<skills-root>/learnings-coach/references/<file>`. A SKILL.md names them by that path
  (`learnings-coach/references/<file>`).
- **Run folder (strict).** `<run>` is `<export-dir>/pmlc-runs/<YYYY-MM-DD>-<site>-<event>/`. `<ws>` is
  `<run>/workspace/` (the engine's files) and every output goes to `<run>/outputs/`. Never write anywhere else.
- `PMLC run-path <ws>` prints `<run>`, the outputs folder, the slug, `top_rating` and `incident_date`. Use those
  values for `<top>`, the top rating and the incident date; do not work them out yourself.
- `PMLC status <ws>` says which workspace files are out of date and when each pack was last checked.
- A path a SKILL.md marks "(repository only)" exists in the source repository, not in an installed copy.

## 2. Before you start: preconditions and direct invocation

- **Only an .xlsx was given** (no workspace yet, or the skill was invoked directly): run `PMLC setup` silently,
  then continue with the skill. Do not send the user back to the hub.

      PMLC setup <export.xlsx> --slug <site>-<event> [--date YYYY-MM-DD]   # ingest, profile, classify, causal, timeline, interfaces

  Name the site and event in plain lowercase words joined by hyphens. Use the corrected incident date when the
  profile flags the summary-sheet date. If the export folder is read-only, add `--root <a writable folder>`.
  `setup` prints the workspace path (`Workspace: …`), the unresolved roles and the profile flags. Tell the user in
  two or three lines what the export holds and which flags matter, then go on.
- **A workspace exists:** run `PMLC status <ws>` and re-run only what it marks stale. `classify` re-applies
  `<ws>/role_overrides.json` by itself.
- **What a skill needs** (its "Before you start" line, matching `skill.json` `requires`):

  | Needs | File | Made by |
  |---|---|---|
  | workspace | `<ws>/findings.json` | `setup` (or `ingest`) |
  | clusters | `<ws>/clusters.json` | `setup` (or `classify`) |
  | causal_graph, timeline, interfaces | `<ws>/causal_graph.json`, `timeline_candidates.json`, `interfaces.json` | `setup` |
  | register | `<run>/outputs/learnings-register.json` | the `learnings-register` skill |

  If the register is required and missing, build it with `learnings-register` first, or tell the user and stop.
- **Unresolved roles.** When `setup` lists unresolved roles and the skill selects by tier or entity, run the
  `learning-clusters` resolution pass first; for a quick first answer, go on and say which roles are not placed.
- **Start from the register if present.** When `<run>/outputs/learnings-register.json` exists, take the
  learnings from it rather than re-deriving them: `PMLC register-items <ws> --tier T<n>` prints a tier's learnings
  as ready items. Keep their wording and IDs, and carry `learning: "LR-nn"` (§3).

## 3. Pack conventions

- **File.** Write the pack to `<run>/outputs/<pack>.json`, in the shape in
  `learnings-coach/references/pack-schema.md`. The pack name and its sections come from the skill's Write table:
  one row per section `id` and kind, with a count ("up to N" is a ceiling, not a target; §6).
- **Scope.** Set `scope` as the skill says; `check-pack` measures coverage against the top-rated findings in it.
- **Citations.** Every item cites Finding IDs, and Evidence IDs where a fact is stated. Label `evidence_strength`
  as `direct`, `corroborated` or `inferred` (`learning-principles.md` §2).
- Put data-quality corrections in `data_quality`, findings left out on purpose (with the reason) in
  `exclusions`, and further findings for the same condition in `supporting_cites`. A finding is either cited or
  excluded, never both.
- **Register learnings.** An item that expresses a register learning carries `learning: "LR-nn"`. `check-pack`
  checks the id against the register.
- **Standards.** `clauses` holds requirement ids from `standards-crosswalk.json` (such as `ISO45001-10.2`), only
  where the item's evidence touches that requirement. An unknown id is a warning, and a problem under `--strict`.
- **Gaps and limits.** What the evidence cannot show goes in top-level `gaps` (`text`, `cites`,
  `evidence_needed`); `pack` collects them into `<run>/outputs/gaps.json` for `investigator-coach`. What the pack
  does not cover goes in `limits`.
- **Generated items.** Paste the output of `causal-item`, `table-item`, `timeline-item` and `register-items`
  unchanged; never retype its numbers. Drop rows only if the skill says so.
- **Owners and dates.** `owner` is a role that owns the change, never a person. Leave owners and due dates out
  unless the user asks (`learning-principles.md` §6). The files the organisation fills in (`templates`,
  `export-actions`) have their owner, due-date, response and assessed-by columns written blank, and you never fill
  them. Never write the `handling` block: only `sign-off` writes it.
- **Status line and footer.** Set the required top-level `status` field to contain
  `Learning purposes: not a statutory document` (`check-pack` refuses a pack without it). `pack` adds the
  ProbeMatrix footer from `output-style.md`. Do not remove either from any copy.
- **Translation.** If the user asks for another language, translate the text fields only. Keep every ID, kind,
  field name and controlled value unchanged, then run §4 again.

## 4. The check and pack loop

    PMLC check-pack <ws> <run>/outputs/<pack>.json --strict   # fix every problem it lists; re-run until none
    PMLC pack <ws> <run>/outputs/<pack>.json                  # -> <pack>.html (open this first) and <pack>.md

- Fix the pack text, not the check. Read the warnings as well: the coverage line ("x of y top-rated relevant
  findings cited"), padding, scope drift and unverified `learning` ids.
- Accept a language-check hit with an item-level `"lint_ok": {"rule": "JCn", "reason": "…"}` only when the
  wording is right (`learning-principles.md` §1 and §1a).
- To change the HTML or Markdown, change the JSON and run the loop again. Never hand-edit the rendered files.
- Several packs: `PMLC check-all <ws> --strict`, then `PMLC render-all <ws>` and `PMLC index <ws>`.
- The register has its own loop (`check-register --strict`, `register-md`, `register-xlsx`; see
  `learnings-register`).
- Any edit after a sign-off returns the file to draft. Never run `sign-off` unless the user says they reviewed
  the file and gives their role.

## 5. Hand-over checklist

Tick each before you reply:

- [ ] `check-pack --strict` reports no problems, and `pack` wrote the HTML.
- [ ] The status line and the ProbeMatrix footer are on the page.
- [ ] Roles only: no personal names, and no role string that points to one person.
- [ ] No blame or punishment wording, and no hindsight wording ("failed to", "should have").
- [ ] Every figure appears in a cited record (`learning-principles.md` §2).
- [ ] No owners or due dates, unless the user asked.
- [ ] The share of fixes at the administrative or training tier is stated honestly.
- [ ] Data-quality corrections, exclusions and gaps are in the pack, and the coverage line has been read.
- [ ] The pack is a draft until a person reviews it; say so.

Then tell the user the HTML path first (`<run>/outputs/<pack>.html`), then the `.md` and the JSON, in two or
three lines: what the pack holds, what the evidence could not show, and the next step the skill names.

## 6. If the evidence is thin

- **Read the profile flags** (`<ws>/profile.md`, also printed by `setup`) and act on each:

  | Flag | What to do |
  |---|---|
  | No Evidence Links sheet | Cite Finding IDs only, set `evidence_strength: "inferred"`, and add a `data_quality` note. |
  | No narrative text | Describe the event only as the findings do; add a `limits` line. |
  | No dated text | Timelines show order only; mark unknown dates as unknown, never guess them. |
  | High F99 share, High T9 share | Run the `learning-clusters` resolution pass before tier or entity packs, or say which roles are not placed. |
  | An empty or thin tier | Say so. Do not promote another level's findings into that tier's instructions. |

- **Counts are "up to N; at least one per supported theme".** Write one item for each theme the evidence
  supports, up to N, and stop there. Never pad to reach a number: items that repeat the same cites are padding,
  and `check-pack` warns `possible padding`.
- **Never invent to fill a section.** Where the evidence is missing, write a `gaps` entry that says what evidence
  would settle it, and keep the section to the items you can ground. If a required section has no supported theme
  at all, write one item of that section's kind that states what the evidence does not show, citing the findings
  that show the gap.
- **Say what is missing.** Tell the user which sections are short and why. If a selection returns no findings at
  all, stop before writing the pack and say what you searched for.
- The skill's own "If the evidence is thin" section adds its particular cases.

## 7. Sharing outside the organisation

A copy for a regulator, client, contractor, insurer, sister company or the public is the organisation's decision, never the coach's. Do not offer it unprompted. A copy may leave the organisation only when **all** of these hold:

1. **Legal review.** The organisation's legal adviser has reviewed the copy and cleared it. Record this as `legal_review: cleared` with `sign-off --legal-review cleared`. These outputs create no legal privilege: a pack, register or dashboard is not a privileged document, and writing it does not make anything privileged. Whether to share, and on what terms, is for legal review.
2. **Approved sign-off at the right classification.** A person who reviewed the file signs it off as `approved`, with `--classification external` (or `public` for a public copy). Any edit after sign-off returns the file to draft. Nothing from an investigation still in progress, or with no finding edited by a person, can be approved.
3. **`--share external`** (or `--share public`) on `pack`, `dashboard` or `register-xlsx`. The engine refuses, listing every unmet condition and writing nothing, unless all four checks hold: an approved sign-off that still matches the file, a classification of `external` or `public` (`public` for a public copy), `legal_review: cleared`, and an embed mode of `summary`. The shared copy is written as `<name>.external.html` (or `.public.html`) beside the internal one, and it says `Shared external: identifying details are masked`.
4. **`--embed summary`.** The page carries no evidence descriptions, quotes, interview plans, key questions or reviewer-vote reasons. Sharing uses `summary` when `--embed` is left out, and refuses `cited` or `full`. A public copy also drops the AI justification and causal text of each finding, keeping its label and ID.
5. **A client-safe (or regulator-safe) variant.** Write the pack for that reader: functions instead of posts, no company names (JC9), no equipment tags (JC10), no role string that points to one person (JC7), and nothing the reader does not need to learn. Run `check-pack --share external` and fix every error before signing off.

What the engine masks in a shared copy: listed names (`--names` or `PMLC_NAMES`) and honorific forms become `[name]`; listed organisations (`--orgs` or `PMLC_ORGS`) and company-suffix names become `[organisation]`; equipment tags become `[equipment tag]`; singleton roles become their generalised label; a site-leadership or board `owner` becomes its function; clock times are removed and full dates become the month and year; the run slug and generated date are left out. Masking is a safety net, not the review: read the shared copy before it leaves.

In every mode, `pack` and `dashboard` refuse to write a page in which a listed name appears. Fix the pack text, or redact the workspace with `ingest --redact`.
