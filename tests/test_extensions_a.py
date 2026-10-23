"""Phase 5 Task 20, extensions A: precursor-timeline (P5-8: the missed section and knowable-then),
emergency-response-learnings (P5-10: the event-day timeline and the gaps between steps) and
engineering-integrity-learnings (the alarms-automation triplets from select --prefix PTE). The profiles, the SKILL.md
wording, the synthetic fixtures and the Hazira golden packs, checked against what the engine prints on Hazira."""
import json

import pytest

from test_pmlc import ROOT, run

pytest.importorskip("openpyxl")
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
OUTPUTS = SAMPLE / "outputs"
FIX = ROOT / "tests" / "fixtures" / "packs"
SKILLS = ROOT / "skills"
PROFILES = json.loads((SKILLS / "learnings-coach" / "references" / "pack-profiles.json").read_text(encoding="utf-8"))
GAP_COLUMNS = ["From", "To", "Minutes", "What the export says"]


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _entries(pack, sid):
    return {k: (e["min"], e["max"]) for e in PROFILES[pack]["sections"] if e["id"] == sid for k in e["kinds"]}


def _section(pack, sid):
    return next((s for s in pack["sections"] if s["id"] == sid), None)


def _minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


@pytest.fixture(scope="module")
def hz(tmp_path_factory):
    root = tmp_path_factory.mktemp("hazira-ext-a")
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root),
        "--overlay", "india-process-site")
    ws = root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"
    run("timeline", str(ws), "--before", "incident")
    return ws


# ----------------------------------------------------------------------------- precursor-timeline (P5-8)

def test_precursor_profile_has_missed_and_knowable_then():
    assert _entries("precursor-timeline", "missed") == {"timeline": (0, 1)}
    assert "knowable-then" in PROFILES["precursor-timeline"]["rules"]


def test_precursor_skill_md_splits_missed_opportunities():
    md = (SKILLS / "precursor-timeline" / "SKILL.md").read_text(encoding="utf-8")
    assert "PMLC missed-opportunities <ws> --timeline-item" in md
    assert "list them as signals only" not in md
    assert "`failure-to-learn-review`" in md and "`missed`" in md
    assert len(md.splitlines()) <= 150


def test_precursor_golden_missed_events_cite_prior_recommendations(hz):
    m = json.loads(run("missed-opportunities", str(hz), "--json"))
    prior = set(m["prior_recommendation"])
    dated = {d["date"] for d in m["dated"]}
    pack = _load(OUTPUTS / "precursor-timeline.json")
    sec = _section(pack, "missed")
    assert sec and len(sec["items"]) == 1 and sec["items"][0]["kind"] == "timeline"
    events = sec["items"][0]["events"]
    assert len(events) >= 3
    for e in events:
        assert "knowable_then" in e, e
        assert set(e["cites"]) & prior, e["date"]
        assert e["date"] in dated, e["date"]          # placed at a date the engine found before the incident
    for s in pack["sections"]:                        # the knowable-then rule covers every timeline in the pack
        for it in s["items"]:
            if it["kind"] == "timeline":
                assert all("knowable_then" in e for e in it["events"]), s["id"]


def test_precursor_fixture_has_missed_section():
    sec = _section(_load(FIX / "precursor-timeline.json"), "missed")
    assert sec and sec["items"][0]["kind"] == "timeline"
    assert all("knowable_then" in e for e in sec["items"][0]["events"])
