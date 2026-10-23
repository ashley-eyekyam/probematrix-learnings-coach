"""Phase 5 Task 7: missed opportunities (P5-8, P5-9), the event-day sequence (P5-10) and whole-word snippets (P5-11,
T5 M1). Synthetic exports from test_pmlc.py only (fictional event, no real data)."""
import json
import re
import subprocess
import sys

from test_pmlc import PMLC, make_export, make_thin_export, run
import pmlc  # noqa: E402  (test_pmlc put the engine folder on sys.path)
from pmlc_lib import missed as missed_mod  # noqa: E402
from pmlc_lib.analysis import timeline as tl  # noqa: E402
from pmlc_lib.pack import items  # noqa: E402

FILLER = ("The maintenance crew followed the planned isolation steps and recorded each reading in the shift log "
          "while the supervisor reviewed the permit conditions with the control room operator on duty. ")
NARRATIVE = ("The night shift took over the plant. At 10:30 hrs the gas alarm sounded in the control room. "
             "The first valve was closed at 11.45 after a long walk.\nEarlier, at 09.05 the leak began at the skid. "
             "A second report repeated that 9:05 was the onset.")


def cli(*args):
    return subprocess.run([sys.executable, str(PMLC), *args], capture_output=True, text=True)


def _ws(tmp_path, narrative=None, edit=None, slug="test-pump"):
    x = make_export(tmp_path, narrative=narrative)
    run("ingest", str(x), "--slug", slug, "--date", "2024-03-20", "--root", str(tmp_path))
    ws = tmp_path / "pmlc-runs" / f"2024-03-20-{slug}" / "workspace"
    if edit:
        fp = ws / "findings.json"
        fs = json.loads(fp.read_text(encoding="utf-8"))
        edit(fs)
        fp.write_text(json.dumps(fs), encoding="utf-8")
    return ws


def _clean(snip):
    return snip[1:] if snip.startswith("…") else snip


# ----------------------------------------------------------------------------- P5-11: whole-word snippets

def _in_source(text, snip):
    """True when the snippet (ellipses dropped, whitespace collapsed) starts and ends on a word boundary of text."""
    core = snip.strip("…").strip()
    flat = " ".join(text.split())
    i = flat.find(core)
    assert i >= 0, (core, flat)
    j = i + len(core)
    return (i == 0 or flat[i - 1] == " ") and (j == len(flat) or flat[j] == " ")


def test_snippet_word_boundaries(tmp_path):
    long_text = FILLER * 3 + "The seal was replaced on 12/03/2024 without a leak test. " + FILLER * 3

    def edit(fs):
        fs[0]["short"] = long_text
        fs[2]["justification"] = "Seals bought locally since March 2022. " + FILLER * 4

    ws = _ws(tmp_path, edit=edit)
    run("timeline", str(ws), "--before", "incident")
    cands = json.loads((ws / "timeline_candidates.json").read_text(encoding="utf-8"))
    assert cands
    fs = {f["id"]: f for f in json.loads((ws / "findings.json").read_text(encoding="utf-8"))}
    for c in cands:
        src = " ".join(" ".join([f["label"], f["short"], f["justification"], f["causal"]])
                       for f in fs.values() if f["id"] in c["sources"])
        assert _in_source(src, c["snippet"]), c["snippet"]
    cut = [c for c in cands if "12/03/2024" in c["snippet"]][0]["snippet"]
    assert cut.startswith("…") and cut.endswith("…")
    it = json.loads(cli("timeline-item", str(ws), "--before", "incident").stdout)
    for e in it["events"]:
        assert len(e["text"]) <= 240
        if e["text"].endswith("…"):
            assert not e["text"][-2].isspace()


def test_snippet_helper_edges():
    text = "alpha beta gamma delta epsilon"
    # a cut inside "gamma" on both sides widens to the whole word, with ellipses where text was cut
    assert tl.word_snippet(text, 13, 14, reach=4, slack=40) == "…beta gamma delta…"
    assert tl.word_snippet(text, 0, 5, reach=200) == text
    # no whitespace within the slack: move inward instead of cutting a word
    word = "x" * 100
    s = tl.word_snippet(word + " DATE " + word, 101, 105, reach=10, slack=5)
    assert s == "…DATE…"
    assert items.trim_words("short text") == "short text"
    long = ("word " * 80).strip()
    t = items.trim_words(long)
    assert len(t) <= 240 and t.endswith("word…")


# ----------------------------------------------------------------------------- P5-8: missed opportunities

def _missed_edit(fs):
    fs[0]["justification"] = "An audit in 2021 recommended a leak test before return to service [EVD-0001]."
    fs[1]["code"] = "SVF 1.1"
    fs[1]["subcategory"] = "Failure to Correct"
    fs[1]["short"] = "The known seal weakness was reported on 05/01/2023 and not corrected."
    fs[3]["justification"] = "Running without the shutdown link had become routine over time."


def test_missed_sets(tmp_path):
    ws = _ws(tmp_path, edit=_missed_edit)
    run("timeline", str(ws), "--before", "incident")
    m = missed_mod.missed(pmlc.load_ws(ws), candidates=json.loads((ws / "timeline_candidates.json").read_text()),
                          drift=["routine", "over time"])
    assert m["version"] == 1
    assert m["prior_recommendation"] == ["FND-0001"]
    assert m["failure_to_correct"] == ["FND-0002"]
    assert m["drift"] == ["FND-0004"]
    assert m["dated"] and all(d["date"] < "2024-03-20" for d in m["dated"])
    assert {x for d in m["dated"] for x in d["findings"]} <= {"FND-0001", "FND-0002"}
    assert any(d["date"] == "2023-01-05" and d["findings"] == ["FND-0002"] for d in m["dated"])
    assert all(not _clean(d["snippet"])[:1].isspace() for d in m["dated"])
    # word boundaries for the drift lexicon: "routinely" is not "routine"
    assert missed_mod.missed(pmlc.load_ws(ws), candidates=[], drift=["rout"])["drift"] == []


def test_missed_cli_writes_artefact_and_timeline_item(tmp_path):
    ws = _ws(tmp_path, edit=_missed_edit)
    run("timeline", str(ws), "--before", "incident")
    out = run("missed-opportunities", str(ws))
    assert "missed_opportunities.json" in out
    art = ws / "missed_opportunities.json"
    first = art.read_bytes()
    run("missed-opportunities", str(ws))
    assert art.read_bytes() == first                                   # re-runs are byte-identical
    assert list(json.loads(first)) == sorted(json.loads(first))         # sort_keys
    assert "missed_opportunities.json" in json.loads((ws / "manifest.json").read_text())["files"]
    j = json.loads(run("missed-opportunities", str(ws), "--json"))
    assert j["prior_recommendation"] == ["FND-0001"] and j["failure_to_correct"] == ["FND-0002"]
    it = json.loads(run("missed-opportunities", str(ws), "--timeline-item"))
    assert it["kind"] == "timeline" and it["id"] == "missed-opportunities" and it["events"]
    assert all(e["knowable_then"] is True and e["cites"] for e in it["events"])
    assert [e["date"] for e in it["events"]] == sorted(e["date"] for e in it["events"])
    assert it["cites"] == sorted({c for e in it["events"] for c in e["cites"]})
    one = json.loads(run("missed-opportunities", str(ws), "--timeline-item", "--top", "1"))["events"]
    assert len(one) == 1 and one[0] in it["events"]
    assert len(one[0]["cites"]) == max(len(e["cites"]) for e in it["events"])
    pack = {"pack": "test-pack", "schema": 1, "title": "Test pack: synthetic pump fire", "audience": "Testers",
            "status": "Learning purposes: not a statutory document", "incident": {"date": "2024-03-20"},
            "bottom_line": [{"text": "Test before service.", "cites": ["FND-0002"]}],
            "sections": [{"id": "s1", "heading": "Section one", "items": [it]}]}
    p = tmp_path / "test-pack.json"
    p.write_text(json.dumps(pack), encoding="utf-8")
    r = cli("check-pack", str(ws), str(p))
    assert r.returncode == 0, r.stdout + r.stderr


def test_missed_without_candidates_notes_it(tmp_path):
    ws = _ws(tmp_path, edit=_missed_edit)
    run("missed-opportunities", str(ws))
    m = json.loads((ws / "missed_opportunities.json").read_text(encoding="utf-8"))
    assert m["dated"] == [] and any("timeline" in n for n in m["notes"])


def test_missed_thin_export(tmp_path):
    x = make_thin_export(tmp_path)
    run("ingest", str(x), "--legacy-out", str(tmp_path / "w"))
    w = tmp_path / "w"
    run("timeline", str(w))
    r = cli("missed-opportunities", str(w))
    assert r.returncode == 0, r.stderr
    m = json.loads((w / "missed_opportunities.json").read_text(encoding="utf-8"))
    assert m["prior_recommendation"] == m["failure_to_correct"] == m["dated"] == []
    assert m["notes"]
    r = cli("missed-opportunities", str(w), "--timeline-item")
    assert r.returncode == 0 and json.loads(r.stdout)["events"] == []
    assert r.stderr.strip()


def test_drift_lexicon_from_references(monkeypatch, tmp_path):
    ref = tmp_path / "open-questions.json"
    monkeypatch.setattr(missed_mod, "LEXICON", ref)
    assert missed_mod.drift_terms() == []                                # Task 4 not merged: empty list
    ref.write_text(json.dumps({"version": 1, "absence": [], "hedge": [], "drift": ["routine"]}), encoding="utf-8")
    assert missed_mod.drift_terms() == ["routine"]


# ----------------------------------------------------------------------------- P5-10: event-day sequence

def test_event_day_sequence(tmp_path):
    def edit(fs):
        fs[2]["justification"] += " The leak began at 09:05 by the camera record."
        fs[3]["short"] += " Alarm logged at 10.30 hrs."

    ws = _ws(tmp_path, narrative=NARRATIVE, edit=edit)
    r = cli("timeline-item", str(ws), "--event-day")
    assert r.returncode == 0, r.stderr
    it = json.loads(r.stdout)
    assert it["kind"] == "timeline" and it["id"] == "event-day"
    assert [e["time"] for e in it["events"]] == ["09:05", "10:30", "11:45"]
    assert all(e["date"] == "2024-03-20" and e["knowable_then"] is True for e in it["events"])
    ev = {e["time"]: e for e in it["events"]}
    assert ev["09:05"]["text"] == "Earlier, at 09.05 the leak began at the skid."
    assert ev["10:30"]["text"] == "At 10:30 hrs the gas alarm sounded in the control room."
    assert ev["09:05"]["cites"] == ["FND-0003"] and ev["10:30"]["cites"] == ["FND-0004"]
    assert ev["11:45"]["cites"] == []
    assert it["cites"] == ["FND-0003", "FND-0004"]
    assert cli("timeline-item", str(ws), "--event-day").stdout == r.stdout        # deterministic


def test_event_day_no_times(tmp_path):
    ws = _ws(tmp_path)
    r = cli("timeline-item", str(ws), "--event-day")
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout)["events"] == [] and "no hh:mm" in r.stderr.lower()
    x = make_thin_export(tmp_path)
    run("ingest", str(x), "--legacy-out", str(tmp_path / "w"))
    r = cli("timeline-item", str(tmp_path / "w"), "--event-day")
    assert r.returncode == 0 and json.loads(r.stdout)["events"] == []


def test_timeline_item_needs_before_or_event_day(tmp_path):
    ws = _ws(tmp_path)
    r = cli("timeline-item", str(ws))
    assert r.returncode != 0 and "--before" in r.stderr and "--event-day" in r.stderr
    assert "Traceback" not in r.stderr


def test_event_day_dotted_times_are_not_dates():
    seq = items.event_day_events("Report filed 24.09.2020. At 9.05 the leak began. Report 1.10.2020 attached.",
                                 [], "2020-09-24")
    assert [e["time"] for e in seq] == ["09:05"]
    assert re.fullmatch(r"At 9\.05 the leak began\.", seq[0]["text"])


def test_event_day_table_rows_are_one_unit():
    narrative = ("| Time | Event | Source |\n|---|---|---|\n| ~02:15 | **Guard sees a cloud.** Calls the gate. | Witness |\n"
                 "| 23 Mar 20:00 | Night shift takes over. | Roster |\n## Notes\n- Walk-down at 08.30 hrs began.")
    seq = items.event_day_events(narrative, [{"id": "FND-0001", "short": "Seen at 02:15 hrs."}], "2024-03-24")
    assert [(e["time"], e["text"], e["cites"]) for e in seq] == [
        ("20:00", "23 Mar 20:00 | Night shift takes over. | Roster", []),
        ("02:15", "Guard sees a cloud. Calls the gate. | Witness", ["FND-0001"]),
        ("08:30", "Walk-down at 08.30 hrs began.", [])]
    assert [e["date"] for e in seq] == ["2024-03-23", "2024-03-24", "2024-03-24"]


def test_event_day_named_day_dates_the_event():
    narrative = ("On 31 Dec at 23:50 the purge began. On 1st January 00:10 the alarm sounded. "
                 "At 00:40 a crew arrived; 31 Feb is not a date at 00:50. The 02:00 log names 5 Jan after it.")
    seq = items.event_day_events(narrative, [], "2021-01-01")
    assert [(e["date"], e["time"]) for e in seq] == [
        ("2020-12-31", "23:50"), ("2021-01-01", "00:10"), ("2021-01-01", "00:40"), ("2021-01-01", "00:50"),
        ("2021-01-01", "02:00")]
