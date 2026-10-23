"""Phase 5, Task 4: open-questions, the absence and hedge lexicons, blank Incident Summary fields, and the
follow-up.csv of an open-questions-register pack. Synthetic data only."""
import json
import subprocess
import sys

import pytest

from test_exports import cli, rows_of
from test_pack import FIX
from test_pmlc import PMLC, make_export, make_thin_export, run
from test_privacy import share_ws, sign
from pmlc_lib import open_questions as OQ


def jrun(*args):
    return json.loads(run(*args))


def _ws(tmp_path, **kw):
    x = make_export(tmp_path, **kw)
    d = tmp_path / "ws"
    run("ingest", str(x), "--legacy-out", str(d))
    return d


def test_lexicon_word_boundaries():
    rx = OQ.oq_pattern(["may", "no record"])
    assert not rx.search("The mayor was not there")
    assert rx.search("It MAY have leaked") and rx.search("There was  no\nrecord of it")
    assert not rx.search("mayhem, maybe")


def test_lexicon_file_shape():
    lex = OQ.load_lexicons()
    for k in ("absence", "hedge", "drift"):
        assert lex[k] and all(isinstance(x, str) and x == x.strip() for x in lex[k])
    assert "normalised" in lex["drift"] and "routine" in lex["drift"]


def test_collect_counts_words_in_the_justification_only():
    w = {"findings": [{"id": "FND-0001", "justification": "There was no record of the test.", "short": "may"},
                      {"id": "FND-0002", "justification": "The valve might have stuck; the mayor agreed.", "short": ""},
                      {"id": "FND-0003", "justification": "Work order shows it.", "short": "no record, may"}],
         "incident": {}}
    oq = OQ.collect(w)
    assert oq["absence"] == ["FND-0001"] and oq["hedged"] == ["FND-0002"]


def test_items_deterministic(tmp_path):
    d = _ws(tmp_path)
    a = run("open-questions", str(d), "--items")
    b = run("open-questions", str(d), "--items")
    assert a == b
    first = (d / "open_questions.json").read_bytes()
    run("open-questions", str(d))
    assert (d / "open_questions.json").read_bytes() == first


def test_items_order_and_cap():
    f = [{"id": f"FND-{i:04d}", "rating": r, "justification": j, "label": f"thing {i}", "short": ""}
         for i, (r, j) in enumerate([(2, "no record"), (4, "no record"), (4, "it may"), (1, "missing"), (3, "plain")], 1)]
    w = {"findings": f, "incident": {}}
    oq = {"empty_follow_up_columns": ["Key Questions"], "absence": ["FND-0001", "FND-0002", "FND-0004"],
          "hedged": ["FND-0002", "FND-0003"]}
    items = OQ.question_items(oq, w)
    assert all(i["kind"] == "question" and i["why"] and i["good_evidence"] for i in items)
    assert "Key Questions" in items[0]["question"] and "cites" not in items[0]
    assert [i["cites"][0] for i in items[1:]] == ["FND-0002", "FND-0001", "FND-0004", "FND-0003"]
    assert "FND-0002" in items[1]["why"]
    many = {"findings": [{"id": f"FND-{i:04d}", "rating": 1, "justification": "unknown", "label": "x", "short": ""}
                         for i in range(1, 60)], "incident": {}}
    assert len(OQ.question_items({"empty_follow_up_columns": [], "absence": [f["id"] for f in many["findings"]],
                                  "hedged": []}, many)) == OQ.MAX_QUESTIONS


def test_good_evidence_comes_from_the_keyword_table():
    f = [{"id": "FND-0001", "rating": 1, "label": "x", "short": "", "justification": "The alarm log is missing."},
         {"id": "FND-0002", "rating": 1, "label": "x", "short": "", "justification": "No record of who was told."}]
    items = OQ.question_items({"empty_follow_up_columns": [], "absence": ["FND-0001", "FND-0002"], "hedged": []},
                              {"findings": f})
    assert [i["good_evidence"] for i in items] == ["data log", "witness statement"]


def test_blank_summary_fields_recorded_at_ingest(tmp_path):
    d = _ws(tmp_path, summary=[("Time", None), ("CONSEQUENCE CLASSIFICATION", None), ("Fatalities", None),
                               ("Location", "Yard")])
    inc = json.loads((d / "incident.json").read_text(encoding="utf-8"))
    assert inc["blank_summary_fields"] == ["Time", "Fatalities"]
    assert inc["summary_fields"] == ["Incident Title", "Date", "Investigation Status", "Time", "Fatalities", "Location"]
    prof = jrun("profile", str(d), "--json")
    assert prof["blank_summary_fields"] == ["Time", "Fatalities"]
    assert any("2 of 6 Incident Summary fields are blank" in x for x in prof["flags"])
    oq = json.loads(run("open-questions", str(d), "--json"))
    assert oq["blank_summary_fields"] == ["Time", "Fatalities"] and oq["summary_fields"] == 6
    assert oq["empty_follow_up_columns"] == ["Evidence to Collect", "Key Questions", "Suggested Interviews",
                                             "Causal Hypothesis"]


def test_open_questions_thin_export(tmp_path):
    x = make_thin_export(tmp_path)
    d = tmp_path / "thin"
    run("ingest", str(x), "--legacy-out", str(d))
    r = subprocess.run([sys.executable, str(PMLC), "open-questions", str(d), "--items"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    items = json.loads(r.stdout)
    assert isinstance(items, list)
    oq = json.loads((d / "open_questions.json").read_text(encoding="utf-8"))
    assert oq["version"] == 1 and oq["gaps"] == [] and isinstance(oq["notes"], list)


def test_old_workspace_without_blank_fields_gets_a_note(tmp_path):
    d = _ws(tmp_path)
    p = d / "incident.json"
    inc = json.loads(p.read_text(encoding="utf-8"))
    del inc["summary_fields"], inc["blank_summary_fields"]
    p.write_text(json.dumps(inc), encoding="utf-8")
    oq = json.loads(run("open-questions", str(d), "--json"))
    assert oq["summary_fields"] == 0 and any("re-run ingest" in n for n in oq["notes"])


def test_gaps_json_is_merged(tmp_path):
    d = _ws(tmp_path)
    (tmp_path / "outputs").mkdir()                   # legacy layout: ws/outputs
    out = d / "outputs"
    out.mkdir()
    (out / "gaps.json").write_text(json.dumps({"gaps": [{"pack": "board-brief", "text": "Why was the test skipped?",
                                                         "cites": ["FND-0001"], "evidence_needed": "work order"}]}),
                                   encoding="utf-8")
    oq = json.loads(run("open-questions", str(d), "--json"))
    assert oq["gaps"] == [{"pack": "board-brief", "text": "Why was the test skipped?", "cites": ["FND-0001"],
                           "evidence_needed": "work order"}]


def test_status_lists_open_questions(tmp_path):
    d = _ws(tmp_path)
    run("open-questions", str(d))
    st = {f["file"]: f["state"] for f in jrun("status", str(d), "--json")["files"]}
    assert st["open_questions.json"] == "current"
    x = make_export(tmp_path, name="again.xlsx", summary=[("Time", None)])
    run("ingest", str(x), "--legacy-out", str(d))
    st = {f["file"]: f["state"] for f in jrun("status", str(d), "--json")["files"]}
    assert st["open_questions.json"] == "stale"


# ----------------------------------------------------------------------------- follow-up.csv for the register pack

def _oq_pack(ws):
    doc = json.loads((FIX / "investigator-coach.json").read_text(encoding="utf-8"))
    doc["pack"] = "open-questions-register"
    p = ws.parent / "outputs" / "open-questions-register.json"
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(doc), encoding="utf-8")
    return p


def test_follow_up_csv_for_open_questions(tmp_path):
    ws, _ = share_ws(tmp_path)
    p = _oq_pack(ws)
    r = cli("pack", str(ws), str(p))
    assert r.returncode == 0, r.stderr
    rows = rows_of((ws.parent / "outputs" / "follow-up.csv").read_text(encoding="utf-8"))
    assert rows[0] == ["Finding ID", "Evidence to Collect", "Key Questions", "Suggested Interviews", "Causal Hypothesis"]
    assert len(rows) > 1 and "follow-up.csv written to" in r.stdout


def test_follow_up_csv_no_overwrite(tmp_path):
    ws, _ = share_ws(tmp_path)
    p = _oq_pack(ws)
    f = ws.parent / "outputs" / "follow-up.csv"
    f.write_text("organisation filled this in\n", encoding="utf-8")
    r = cli("pack", str(ws), str(p))
    assert r.returncode == 0, r.stderr
    assert f.read_text(encoding="utf-8") == "organisation filled this in\n"
    assert "left as it is" in r.stderr


@pytest.mark.parametrize("mode", ["external"])
def test_open_questions_shared_copy(tmp_path, mode):
    ws, _ = share_ws(tmp_path)
    p = _oq_pack(ws)
    sign(ws, p, "--classification", "external", "--legal-review", "cleared")
    r = cli("pack", str(ws), str(p), "--share", mode)
    assert r.returncode == 0, r.stderr
    outs = ws.parent / "outputs"
    assert (outs / f"follow-up.{mode}.csv").is_file()
    assert not (outs / "follow-up.csv").exists() and not (outs / "follow-up.json").exists()
