# Learnings Register schema

One row per **learning** (`LR-nn`). Each learning carries its recommendations. Learnings with no counterpart in a comparator report also get an `ML-nn` ("missed learning") number.

## Sections

| Section | Fields |
|---|---|
| A. Identity | `lr_id`, `ml_id` (if no counterpart), `title` |
| B. Lesson | `lesson` (one generalisable sentence), `context` (short, de-identified narrative), `owner_entity` (F-cluster), `tiers` (T-levels that must learn) |
| C. Evidence | `finding_ids`, `evidence_ids`, `evidence_strength` (direct / corroborated / inferred), `confidence` (high / medium / low) |
| D. Causal classification | `hfacs_level` (level + sub-category), `causal_role` (initiating / contributory / escalating / failed mitigation), `barrier` (prevention or mitigation side, which barrier), `hazard`, `activity`, `performance_mode` (skill / rule / knowledge; slip / lapse / mistake / violation), `org_system` |
| E. Pattern | `pattern` (recurrence or cross-incident pattern), `precursors` (dated weak signals) |
| F. Comparison | `comparison` (yes / partial / none / not compared), `reason_class` for none (see `comparison-method.md`) |
| G. Significance | `worst_case`, `transferability` (same site / other sites / industry-wide), `priority` (1 = highest) |
| H. Dissemination | `audiences`, `learning_level` (individual / team / organisational; single- or double-loop), `formats` (Brief, Card, toolbox talk, module) |
| I. Recommendations | list of `{what, level_barrier, evidence_basis, hoc_tier, leading_indicator}` |
| J. Tier messages | `tier_messages`: `{"T1": "...", "T2": "...", "T3": "...", "T4": "...", "T5": "..."}`, one short message per tier that must act (omit tiers with nothing to do). Feeds the Learning Plan sheet and the dashboard |

**Owner rule.** `owner_entity` is the entity with the most findings among the learning's findings (from `clusters.json`), written as `F-id Name`; list co-owners after it, e.g. `F02 Mechanical Maintenance (co-owners: F06, F07)`. Choose a different owner only when the learning is about a system another entity owns, and say why in `context`.

**Excluded findings.** Do not cite findings with a reviewer downgrade vote (shown by `profile` and `check-register`) unless you say why.

Controlled values (keep to these so summaries count cleanly; put detail in another field):
- `hfacs_level`: start with `L1`, `L2`, `L3` or `L4`, then the sub-category.
- `hoc_tier`: one of `elimination`, `substitution`, `engineering`, `administrative`, `training`, `ppe`.
- `priority`: `1`, `2` or `3`.
- `comparison`: `yes`, `partial`, `none`, `not compared`.
- `evidence_strength`, `confidence`, `causal_role`, `transferability`, `performance_mode` (starts with `skill-based`, `rule-based`, `knowledge-based` or `n/a`), the `tier_messages` keys (`T1` to `T5`), the EVD IDs in `evidence_basis` and the `hfacs_level` sub-category (matching the export, `isation` and `ization` treated alike) use the values listed under Sections.

`check-register` reports drift from these as `warning:` lines after the summary. In v2.0 drift is a warning and never changes the exit code; in v2.1 it becomes an error.

Organisational systems vocabulary: procedures; training and competence; supervision; staffing and fatigue; communication and handover; design and human–machine interface; maintenance regime; management of change; contractor and supply chain; emergency preparedness; resourcing; safety culture; assurance and audit.

## Handling and sign-off

Every pack and register may carry a top-level `handling` object. It is optional: without one the document is treated as `draft` / `internal` and `check-pack` (or `check-register`) passes with the warning `no handling block: rendered as draft (internal)`.

| Key | Values | Default |
|---|---|---|
| `status` | `draft`, `reviewed`, `approved` | `draft` |
| `reviewer_role` | the reviewer's role, never a name | none |
| `reviewed_on` | `YYYY-MM-DD` | none |
| `classification` | `internal`, `restricted`, `external`, `public` | `internal` |
| `legal_review` | `not-required`, `requested`, `cleared` | `not-required` |
| `distribution` | list of audience names | `[]` |
| `version` | text | `1.0` |
| `retention_review` | `YYYY-MM-DD` | none |
| `content_hash` | `sha256:` and 64 hex digits | none |

Unknown keys, bad values and `reviewed` or `approved` without `reviewer_role`, `reviewed_on` and `content_hash` are problems.

**Forced draft.** Nothing may be reviewed or approved while the export's Investigation Status starts with `in_progress` ("the investigation status is in progress") or while no finding is marked as edited by a person ("no finding is marked as edited by a person"). There is no override: finish the investigation in ProbeMatrix first.

**Sign-off.** After a person has reviewed the document and given their role, run `pmlc sign-off <ws> <file> --role "<role>" [--status reviewed|approved] [--classification ...] [--legal-review ...] [--distribution AUDIENCE ...] [--retention-review YYYY-MM-DD] [--version V] [--date YYYY-MM-DD]`. It refuses on forced-draft reasons and on any check problem, writes the `handling` block into the file with a `content_hash` of everything except `handling`, and records it in the manifest (`status` lists it). Any later edit, even one character, changes the hash: the effective status falls back to `draft` and the check warns `edited since sign-off: status is draft until signed off again`. A bare-list register cannot be signed off; wrap it as `{"entries": [...]}`.

## JSON shape for `pmlc.py register-xlsx`

```json
{
  "title": "Learnings Register: <incident>",
  "source": "<export file name>",
  "entries": [
    {
      "lr_id": "LR-01",
      "ml_id": "",
      "title": "Emergency isolation had no decision rule and no delegated authority",
      "owner_entity": "F09b Emergency Planning & Command",
      "tiers": ["T2", "T4"],
      "lesson": "If an emergency plan names a release scenario but not who may isolate, and on what criteria, isolation waits for escalation.",
      "context": "…",
      "finding_ids": ["FND-…"],
      "evidence_ids": ["EVD-…"],
      "evidence_strength": "direct",
      "confidence": "high",
      "hfacs_level": "L4 Organisational Climate/Culture",
      "causal_role": "escalating",
      "barrier": "mitigation: emergency isolation",
      "hazard": "flammable vapour release",
      "activity": "emergency response",
      "performance_mode": "rule-based; no rule available",
      "org_system": "emergency preparedness",
      "pattern": "…",
      "precursors": "…",
      "comparison": "partial",
      "reason_class": "",
      "worst_case": "…",
      "transferability": "industry-wide",
      "priority": 1,
      "audiences": ["shift in-charges", "plant leadership", "emergency planners"],
      "learning_level": "organisational; double-loop",
      "formats": ["Brief", "Card"],
      "tier_messages": {"T2": "On a confirmed major release, isolate first; do not wait for the call chain.",
                        "T4": "Decide and write down who may isolate, on what criteria, without calling up."},
      "recommendations": [
        {"what": "…", "level_barrier": "L4 / emergency isolation", "evidence_basis": "EVD-…",
         "hoc_tier": "engineering", "leading_indicator": "…"}
      ]
    }
  ]
}
```
