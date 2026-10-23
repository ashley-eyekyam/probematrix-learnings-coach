# Industry reference packs

An industry reference pack is method reference for one sector: extra role words for the classifier, a barrier list, indicator starters and a glossary. It is not evidence. Nothing in a pack states a fact about an incident; facts come only from the export.

| Folder | Sector | Status |
|---|---|---|
| `process/` | Process industries: refining, chemicals, gas, storage terminals | v2.0 |

Other sectors (construction, mining, aviation, rail) are not in v2.0.

## What a pack holds

| File | Use |
|---|---|
| `overlay.json` | The role words. Same format as `../overlays/*.json`; `classify --industry <name>` loads it like `--overlay` and records it in `clusters.json` the same way. |
| `barriers.md` | Common barriers, written with the words of `../barriers-and-controls.md`. |
| `indicators.md` | Leading indicator starters that follow the template in `../indicators-and-effectiveness.md`. |
| `glossary.json` | Terms and definitions in the shape of `../glossary.json`. |

## Using one

```
python3 skills/learnings-coach/scripts/pmlc.py classify <ws> --industry process
python3 skills/learnings-coach/scripts/pmlc.py setup <export.xlsx> --slug <site>-<event> --industry process
```

`classify` prints `Industry reference: process (method reference, not evidence)`. An unknown name exits 2 and lists the folders here. `--industry` combines with `--overlay`; the site overlay is applied after the industry one. Without `--industry` nothing changes, so the Hazira calibration numbers do not move.
