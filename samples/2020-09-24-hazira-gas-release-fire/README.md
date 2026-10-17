# Hazira gas terminal release and fire, 24 September 2020

A ProbeMatrix findings export and its Learnings Coach outputs for the hydrocarbon release and fire at the gas terminal of ONGC's Hazira plant in the early hours of 24 September 2020. Nobody was injured.

## Source

**Public source:** PNGRB Enquiry Committee report on the fire at ONGC Hazira Plant, 24 September 2020 (36 pages). The enquiry committee was constituted by the Petroleum and Natural Gas Regulatory Board.

**What the analysis had access to:** a desk analysis of the published enquiry report only. There was no site access, no interviews and no access to ONGC records.

**Sighted analysis:** the committee's own remedial measures (report pages 33 to 36) were part of the evidence pack. Some findings cite those recommendations, so the learnings were not written independently of them; read any comparison with the committee's recommendations as coverage, not independent discovery.

## Files

| File | What it is |
|---|---|
| `2020-09-24-hazira-gas-release-fire_official-report.pdf` | The official PNGRB Enquiry Committee report, as published |
| `2020-09-24-hazira-gas-release-fire_probematrix-report.pdf` | The ProbeMatrix HFMAP investigation report (222 pages) |
| `2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx` | The export: 436 findings and 789 evidence links, five sheets only |
| `outputs/learnings-register.json`, `.md`, `.xlsx` | Learnings Register: 25 learnings and 44 recommendations covering 435 of 436 findings |
| `outputs/organisation-learning-map.html` | Organisation learning map with the detailed register tab (self-contained, works offline) |

## How it was prepared

- The export went through `tools/make-public-sample.py`: only the five sheets the coach reads were kept, and the name scan returned zero hits against a list of every personal name in the enquiry report. `pmlc.py scan-names` over the ProbeMatrix report and `outputs/` also returned zero hits. The ProbeMatrix material names roles only.
- **Summary-sheet corrections:** the date was changed from 2020-08-24 to 2020-09-24 and the incident type from aviation to fire, to match the enquiry report. The ProbeMatrix report was generated before this correction and still shows 2020-08-24 on its cover.
- The guidance printed under each HFACS code in the ProbeMatrix report is the generic code library text, so some lines (for example on aviation brownout landings) are not about this event.
- One finding (FND-44219027) is left out of the register because a reviewer voted to downgrade it.

## Status

**Draft.** The ProbeMatrix investigation status is `in_progress`, and the findings have not been reviewed by a person in ProbeMatrix (no finding is marked as edited by a user). Treat the learnings as a worked example of the method, not as conclusions about the event.

To rebuild the workspace, copy the export to a working folder outside the repo and run `python3 skills/learnings-coach/scripts/pmlc.py ingest <folder>/2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx --slug hazira-gas-release-fire`.
