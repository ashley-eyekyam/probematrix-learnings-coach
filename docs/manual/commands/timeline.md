# timeline

## What it does

Finds **dated precursor candidates**: every date written in the findings and the evidence ("12-13 Nov 2018", "25/02/2019", "since 2018"), with the sentence around it and the IDs it came from. The precursor-timeline skill turns these into the story of the warning signs before the event.

With `--on`, it also collects every **clock time** for one day (for example the event day), so the minutes of the event can be laid out in order.

It writes `timeline_candidates.json` (and, with `--on`, `timeline_event_day.json`) to the workspace and prints a table of the first rows.

## When to use it

For the precursor-timeline and emergency-response skills, or whenever someone asks "what were the warning signs, and when?".

## Synopsis

```text
pmlc timeline ws [--before BEFORE] [--per-date PER_DATE] [--show SHOW] [--on DAY|incident]
                 [--entity F [F ...]] [--min-precision {day,month,year}]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--before` | `YYYY-MM-DD` or `incident` | no limit | Keep only dates up to this day. `incident` means the workspace's incident date |
| `--per-date` | number | 4 | The most sentences kept for any one date |
| `--show` | number | 60 | How many rows to print. The file always holds every candidate |
| `--on` | `YYYY-MM-DD` or `incident` | none | Also write `timeline_event_day.json`: every clock time on that day. Times in sentences without a date count only for the incident date; for any other day, a time counts only when its sentence gives that day's date |
| `--entity` | entity IDs | all | Keep only findings in these parts of the organisation, and the evidence linked to them. Needs [classify](classify.md) |
| `--min-precision` | `day`, `month` or `year` | `year` | The coarsest date to keep. `day` drops "2018" and "Nov 2018"; `year` keeps everything |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

All candidates, and the clock times of the event day:

```bash
python3 $E timeline $WS --on incident --show 8
```

```text
98 dated precursor candidates written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/workspace/timeline_candidates.json (the precursor-timeline skill curates these).

| Date | Precision | Sources | Snippet |
|---|---|---|---|
| 1986-01-01 | year | FND-7A32AC87 | e to replace the failed OEM rectangular-slot gasket with a locally-sourced substitute O-ring. [EVD-8645] documents: 'The meter is very old (1986) and having rec |
…
| 2011-01-01 | year | FND-6D307E93 | y without documented authority or risk assessment. This pattern is reinforced by [EVD-8307]: the 4-year UT cycle itself was not adhered to (2011->2017 = 6 years |
…

29 clock times on 2020-09-24 written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/workspace/timeline_event_day.json.

| Time | Mentions | Sources | Snippet |
|---|---:|---|---|
| 02:11 | 4 | FND-C7F16268, FND-E63EB689, EVD-9587, narrative | omaly to that single luminaire. [EVD-9587] shows the last clean pre-incident CCTV baseline frame at 02:11:43, which the committee used to bound the last documen |
| 02:12 | 271 | FND-20217957, FND-7A32AC87, FND-D4A6F6B6, FND-91B45FF9 | 54 closure) for 46 minutes after the leak was first detected. Timeline from [EVD-6414]: leak onset 02:12:50 (CCTV), first physical detection 02:15 (CISF perimet |
| 02:15 | 168 | FND-20217957, FND-D4A6F6B6, FND-BDD73BA2, FND-44219027 | was first detected. Timeline from [EVD-6414]: leak onset 02:12:50 (CCTV), first physical detection 02:15 (CISF perimeter), shift-in-charge notified ~02:35, MOV  |
…
```

Only day-precise dates before the event, for Mechanical Maintenance (F02):

```bash
python3 $E timeline $WS --before incident --min-precision day --per-date 2 --show 4 --entity F02
```

```text
18 dated precursor candidates written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/workspace/timeline_candidates.json (the precursor-timeline skill curates these).

| Date | Precision | Sources | Snippet |
|---|---|---|---|
| 2018-11-13 | day | FND-35861FFB | t gasket, and the substitute O-ring had become the normal practice. The recurrence record [EVD-1494] — cleaning/servicing/calibration on 12-13 Nov 2018, gasket  |
| 2018-11-13 | day | FND-AC9A1E69 | ing problem and institute a durable correction, but the same inadequate local O-ring fix was repeated. [EVD-1494] records maintenance on 12-13 Nov 2018, a gaske |
| 2019-02-25 | day | FND-69067A1C, FND-54180594, FND-AC8FBB26, FND-D14B8424 | records that "Cleaning/servicing/calibration of meters 1 & 2 was carried out on 12th & 13th Nov 2018. Afterwards, meter no.1 was cleaned on 25/02/2019 & gasket  |
| 2019-02-25 | day | FND-82673283 | the available guidance had no correct part standard to work to. EVD-1494 demonstrates the same defect recurred: "meter no.1 was cleaned on 25/02/2019 & gasket w |
```

## Common problems

- **`--before: use YYYY-MM-DD or "incident"`.** The date was not in `YYYY-MM-DD` form (exit code 2). The same mistake with `--on` gives `--on takes a YYYY-MM-DD date or the word incident.`
- **"Needs clusters.json. Run: pmlc.py classify <ws>".** `--entity` needs [classify](classify.md) first.
- **A year shows as 1 January.** A date written only as a year ("1986") is stored as `1986-01-01` with precision `year`. Read the precision column, or use `--min-precision`.
- **These are candidates, not facts.** A sentence can mention a date for another reason (a design year, a standard's edition). The precursor-timeline skill and a person decide which dates are warning signs.
- **A large mention count is not many events.** Mentions count every place a time is written. Many findings repeat the same timeline, so the 271 mentions of 02:12 describe a handful of moments, not 271 events.

## Related

- [select](select.md) gets the full text of the findings a row cites.
- [Skills](../Skills.md): `precursor-timeline` and `emergency-response-learnings` use this.
