# Fire Services Readiness Indicators: from the Hazira gas terminal vapour release and fire, 24 September 2020 (draft)

*For the Head of Fire Services and installation Chief Fire Officers. A set of leading indicators that would have shown the weaknesses behind the Hazira event before the night.*

> Learning purposes: not a statutory document. Derived from a ProbeMatrix investigation export; learnings are evidence-linked but should be validated by the organisation before adoption.

## Why these indicators

On the night of 23–24 September 2020, a condensate leak at Hazira's Gas Terminal metering skid formed a vapour cloud. CISF guards saw it at 02:15 and informed the Fire Station among others. Nobody could reach the leak or the isolation valves through the cloud, and the emergency plan gave no isolation criteria. The first valve was closed at 03:01, and the cloud ignited at 03:08:15. The fire was contained with no injuries inside the plant: cooling began at about 03:50 and the fire was out by about 06:00. Fire water held because the electric pumps ran. Three of the four diesel pumps were under maintenance or unreliable [EVD-2432]. The drill records showed dates, not lessons [EVD-2130]. Gas detection only displayed an alarm, and alarmed after people had already seen the cloud [EVD-8657]. And the night could not be timed reliably afterwards [EVD-5532]. *(Full account: 02 Fire Services Learnings, Part A.)*

Every one of these conditions existed **before** the leak, and every one can be measured. The indicators below are **leading**: they move before an incident, not after one.

**How to read the table.**
- **Owner** marks who controls the measure: **FS** is Fire Services; **Interface** is owned elsewhere but tracked by Fire Services.
- **Hazira baseline** is what the record shows for that measure before or during the event. *Not recorded* means the record is silent, not that the answer was zero.
- **Target** (your installation's own) is left blank on purpose. Set it from your ERDMP, the applicable OISD standard or internal standards. Eyekyam does not propose targets.

---

## A. Fire-water readiness (learning FS-1)

| # | Indicator | Definition | When | Owner | Hazira baseline | Target |
|---|---|---|---|---|---|---|
| R1 | **Diesel fire-water capacity availability** | Hours in the period when available diesel fire-pump capacity meets the design basis ÷ total hours × 100 | Monthly | FS | 1 of 4 diesel pumps usable at the time of the event [EVD-2432] |  |
| R2 | **Pump faults without a recorded cause** | Number of fire-pump trips or failed starts with no recorded cause 7 days after the event | Weekly | FS | One pump "tripping after 2 minutes", reason not identified or recorded [EVD-2432] |  |
| R3 | **Full-duration pump test compliance** | Diesel pumps tested at rated flow for the full specified duration ÷ diesel pumps due for test × 100 | Monthly | FS | *Not recorded* |  |
| R4 | **Open fire-water impairments** | Number of declared impairments open, and the age of the oldest in days | Weekly | FS | No impairment practice recorded |  |

**What would have shown at Hazira.** R1 and R2 would have flagged a backup that had largely gone, months before the night. R4 would have shown whether anyone had declared it.

---

## B. Drill effectiveness (learning FS-2)

| # | Indicator | Definition | When | Owner | Hazira baseline | Target |
|---|---|---|---|---|---|---|
| R5 | **Drills with timed decision points** | Drills whose record includes timed decision points and observations ÷ drills held × 100 | Quarterly | FS | SAP drill records held no actions or observations [EVD-2130] |  |
| R6 | **Drill action closure** | Drill actions closed within 30 days ÷ drill actions raised × 100 | Quarterly | FS | No drill actions recorded [EVD-2130] |  |
| R7 | **Scenario coverage** | Credible major-event scenarios in the ERDMP exercised in the last 12 months ÷ total such scenarios × 100. Count "large unignited release" separately | Annually | FS | *Not recorded* |  |
| R8 | **Night drills** | Drills held between 22:00 and 06:00 in the last 12 months | Annually | FS | *Not recorded*. The event began at 02:12 |  |

---

## C. Pre-ignition response (learning FS-3; measured in Drill 1)

| # | Indicator | Definition | When | Owner | Hazira baseline | Target |
|---|---|---|---|---|---|---|
| R9 | **Call to ignition control checklist complete** | Minutes from gas-release call to completion of the fire-service ignition-control actions (vehicles, hot work, agreed electrical isolation) | Each relevant drill | FS | ~20 min to the halt on vehicle movement (02:15 to ~02:35) [EVD-4286; EVD-9612]; rest not recorded |  |
| R10 | **Call to water-curtain decision** | Minutes from gas-release call to a recorded decision on water curtain / dispersion | Each relevant drill | FS | *Not recorded* |  |
| R11 | **High inventory sections with a pre-ignition plan** | Sections with a written fire-service unignited-release plan (staging, curtain, ignition control) ÷ high-inventory sections × 100 | Annually | FS | No such plan in the record; the DMP had no isolation actions for the leak scenario [EVD-4052] |  |

---

## D. Timing and logging (learning FS-4)

| # | Indicator | Definition | When | Owner | Hazira baseline | Target |
|---|---|---|---|---|---|---|
| R12 | **Clock drift** | Largest difference found between the fire control room clock and the DCS / CCTV clocks | Monthly | FS with instrument engineers | 2–12 min between control-room DCS clocks [EVD-5532] |  |
| R13 | **Complete fire-service logs** | Incidents and drills with a time-stamped fire-service log from first call to stand-down ÷ total × 100 | Quarterly | FS | No fire-service log in the record [GAP] |  |

---

## E. Interface indicators (owned elsewhere, tracked by Fire Services)

These seven measures belong to other owners. Fire Services track them, report them upward and test them in drills.

| # | Indicator | Definition | When | Owner | Hazira baseline | Target |
|---|---|---|---|---|---|---|
| R14 | **Detection to isolation in drills** | Minutes from first detection to first isolation of the release source in drills | Each relevant drill | Interface (operations) | 46 min (02:15 to 03:01) [EVD-6414] |  |
| R15 | **Isolations operable from a safe location** | High-inventory isolation points that can be operated from outside the credible cloud envelope ÷ total such points × 100 | Annually | Interface (operations / engineering) | Gas Terminal MOVs local only [EVD-3932] |  |
| R16 | **ERDMP scenarios with isolation criteria and delegated authority** | Major-release scenarios that state the trigger and who may isolate without seeking permission ÷ total × 100 | Annually | Interface (ERDMP owner) | 0: the DMP/ERDMP gave neither [EVD-4052] |  |
| R17 | **Gas alarms repeated at the fire control room** | High-hazard areas whose gas detection is visible at the fire control room ÷ total × 100 | Annually | Interface (instrumentation) | *Not recorded*. Detection showed on a local annunciator only [EVD-8657] |  |
| R18 | **Security report to controlling control room** | Minutes from a security-detected release to the controlling control room being informed (tabletop or drill) | Each Drill 4 / Drill 1 | Interface (CISF / operations) | 3–5 min, via the CCTV room [EVD-8871] |  |
| R19 | **Open flameproof-fitting defects in hazardous areas** | Number of flameproof enclosures reported open or damaged and not yet repaired, and the age of the oldest | Monthly | Interface (electrical) | Probable ignition source: an open flameproof fitting with 3 bolts missing [EVD-6916] |  |
| R20 | **CCTV coverage visible to fire control** | High-hazard areas with live CCTV visible at the fire control room or ECR ÷ total × 100 | Annually | Interface (security) | One PTZ camera, ~90 s pan; lost 7 s after ignition [EVD-0210; EVD-2752] |  |

---

## Using the set

- **Start small.** If you adopt only five, choose R1, R2, R5, R9 and R12. They are owned by Fire Services and need no one else's agreement.
- **Report the interface set upward.** R14–R20 belong in the installation's safety committee report, with Fire Services as the reporter and the named owner as the actor.
- **Keep the targets local.** A target from your ERDMP or standard, written into the blank column, makes each indicator yours.
- **Watch for gaming.** Counting drills is easy; R5 and R6 ask whether drills taught anything. Counting pump tests is easy; R3 asks for the full duration at rated flow.

**See also:** OISD-STD-116, *Fire Protection Facilities for Petroleum Refineries and Oil/Gas Processing Plants* (R1–R4), and PNGRB *Codes of Practices for ERDMP Regulations, 2010*, as amended (R5–R8, R16). Check the current editions and their applicability. The analysis tests no clause.

## Evidence and limits

Baselines come from the investigation narrative and the EVD items cited. The supporting findings are listed in *02 Fire Services Learnings*. This is a desk analysis. Where the record is silent the table says so, and it makes no assumption about Hazira's actual practice.

---

> Generated with ProbeMatrix Learnings Coach (open source, MIT) from a ProbeMatrix four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com
