---
name: causal-map
description: Explains how organisational influences enabled supervisory conditions, preconditions and unsafe acts in a ProbeMatrix investigation export, as an interactive causal graph (HTML, with a Mermaid file for other tools), ranked hub factors, causal pathways read top-down and a plain-language narrative, built from the factor links in each finding's causal explanation even when the export's Causal Chain sheet is empty. Use when someone with a ProbeMatrix export asks how the factors connect, for a causal chain, causal tree or root-cause pathway, "how did the organisation set this up", or a diagram of the investigation. Not for warnings before the event (use `precursor-timeline`) or for which barriers failed (use `barrier-learnings`).
---

# Causal Map

Engine: `PMLC` as in `learnings-coach/references/skill-common.md` §1; this skill needs the `learnings-coach` skill installed alongside it.

## Before you start

Follow `learnings-coach/references/skill-common.md` §1 (engine and paths) and §2 (preconditions; run `PMLC setup`
when only an .xlsx was given). Needs: `workspace`, `causal_graph` (`setup` writes it). Optional: the register.
Read `learnings-coach/references/learning-principles.md` (§1a: read a pathway as the people saw it then) and
`learnings-coach/references/hfacs-levels.md` for the level names.

## Gather

```bash
PMLC causal <ws> --top 60 --hubs                         # links from the causal explanations, plus the hub factors
PMLC causal <ws> --top 60 --include-justification        # wider net when the first run finds few links
PMLC table-item <ws> hubs --top 10                       # the hubs table, ready to paste
PMLC causal-item <ws> --top 40                           # the graph item, ready to paste
```

`causal` writes `<ws>/causal_graph.json` (nodes, edges with mention counts and supporting finding IDs) and
`<ws>/causal_graph.mmd` (a Mermaid flowchart for hosts that draw Mermaid; the pack's HTML graph is the primary
view). Edges run from the higher-level factor to the lower one; same-level links have no implied direction, so
tell them as "alongside", never as cause and effect. Paste the `table-item` and `causal-item` output unchanged;
never retype a link or a count.

For each pathway, read the findings behind its links: `PMLC select <ws> --code "<code>" --brief`, then the full
text of the highest-rated ones.

## Write

Write `<run>/outputs/causal-map.json` in the shape in `learnings-coach/references/pack-schema.md`.

| § | id | Heading | Content rule | Kind | Count |
|---|---|---|---|---|---|
| — | bottom_line | — | The hubs that fed the most downstream factors, and the pathway that matters most; cite the hub findings | `bottom_line` | up to 7 |
| 1 | `map` | Causal map | The `causal-item` graph, kept to the top 30–40 links for legibility | `graph` | 1 |
| 2 | `hubs` | Hub factors | The `table-item hubs` table (Factor, Level, Links out, Mentions, Name, `row_cites`); L4 and L3 hubs first | `table` | 1 |
| 3 | `pathways` | Causal pathways | One `para` per pathway, `group` = its name: four sentences, one per level, **top-down** (L4 → L3 → L2 → L1), ending on the sharp-end **condition**, never on a person's act or character | `para` | up to 6 |
| 4 | `breaks` | Breaks in the chain | Where the story needs a link the graph lacks: say so as a gap and add a `gaps` entry; never invent the link | `para` | up to 5 |
| 5 | `sequence` | Event sequence | Latent conditions → trigger → escalation → response, aligned to dated text where the export gives it | `timeline` | 1 |

Pathways read top-down and end on a condition, for example "the replacement was returned to service without a design-pressure
test", not "the fitter did not test it". Carry `learning: "LR-nn"` on a pathway that expresses a register
learning (`skill-common.md` §3).

```json
{"kind": "para", "group": "Spares to leak", "text": "Purchasing allowed local seals (L4) … so the joint went back into service untested (L1).",
 "cites": ["FND-0003", "FND-0002", "FND-0001"], "evidence_strength": "direct"}
```

## If the evidence is thin

Follow `skill-common.md` §6, and:
- **`causal-item` says "no links"**, or the graph has fewer than about ten links: re-run `causal` with
  `--include-justification`. If it is still sparse, keep the map, write one pathway per supported chain, and put
  the missing links in `breaks` and `gaps`.
- **No chain reaches L1 or starts at L4:** write the pathway as far as the evidence goes and say where it stops.
- **No dated text:** the `sequence` timeline shows order only; mark unknown dates as unknown.

## Not covered here

- Dated warnings and weak signals before the event: `precursor-timeline`.
- Which barriers failed and how strong the fix should be: `barrier-learnings`.
- What passes between two departments: `interface-learnings`.
- Pathways told for site leaders: `site-leadership-coach` reuses `causal-item`.

## Check and hand over

Run `skill-common.md` §4, then tick §5:

```bash
PMLC check-pack <ws> <run>/outputs/causal-map.json --strict   # fix every problem it lists
PMLC pack <ws> <run>/outputs/causal-map.json                  # -> causal-map.html (drawn graph) and causal-map.md
```

Tell the user which hubs carry the most links, and where the chain breaks.
