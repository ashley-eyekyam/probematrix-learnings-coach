"""Phase 5, Task 4: open-questions, the absence and hedge lexicons, blank Incident Summary fields, and the
follow-up.csv of an open-questions-register pack. Synthetic data only."""
import json
import shutil
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
    assert oq["version"] == 1 and oq["gaps"] == [] and any("word lists" in n for n in oq["notes"])


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


# ----------------------------------------------------------------------------- the register pack's CSV

OQ_CSV = "open-questions-follow-up.csv"


def _oq_pack(ws, name="open-questions-register", cited=True, why="The justification says a record is absent"):
    """A pack shaped like Task 15's: question items with cites, no investigator-coach follow-up table."""
    doc = json.loads((FIX / "investigator-coach.json").read_text(encoding="utf-8"))
    doc["pack"] = name
    q = {"kind": "question", "question": "What record would settle the seal change?", "why": why,
         "good_evidence": "maintenance record"}
    if cited:
        q["cites"] = ["FND-0001", "FND-0002"]
    doc["sections"] = [{"id": "questions", "heading": "Questions", "items": [q]}]
    p = ws.parent / "outputs" / f"{name}.json"
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(doc), encoding="utf-8")
    return p


def test_follow_up_csv_for_open_questions(tmp_path):
    ws, _ = share_ws(tmp_path)
    p = _oq_pack(ws)
    r = cli("pack", str(ws), str(p))
    assert r.returncode == 0, r.stderr
    rows = rows_of((ws.parent / "outputs" / OQ_CSV).read_text(encoding="utf-8"))
    assert rows[0] == ["Finding ID", "Evidence to Collect", "Key Questions", "Suggested Interviews", "Causal Hypothesis"]
    assert [x[0] for x in rows[1:]] == ["FND-0001", "FND-0002"] and rows[1][1] == "maintenance record"
    assert f"{OQ_CSV} written to" in r.stdout and not (ws.parent / "outputs" / "follow-up.csv").exists()


def test_open_questions_csv_skipped_without_data_rows(tmp_path):
    ws, _ = share_ws(tmp_path)
    r = cli("pack", str(ws), str(_oq_pack(ws, cited=False)))
    assert r.returncode == 0, r.stderr
    assert not (ws.parent / "outputs" / OQ_CSV).exists()          # no header-only file to block the real one


def test_follow_up_csv_no_overwrite(tmp_path):
    ws, _ = share_ws(tmp_path)
    p = _oq_pack(ws)
    f = ws.parent / "outputs" / OQ_CSV
    f.write_text("organisation filled this in\n", encoding="utf-8")
    r = cli("pack", str(ws), str(p))
    assert r.returncode == 0, r.stderr
    assert f.read_text(encoding="utf-8") == "organisation filled this in\n"
    assert "left as it is" in r.stderr


def test_coach_and_open_questions_files_do_not_collide(tmp_path):
    ws, _ = share_ws(tmp_path)
    outs = ws.parent / "outputs"
    coach = _oq_pack(ws, name="investigator-coach")
    shutil.copy(FIX / "investigator-coach.json", coach)
    oq = _oq_pack(ws)
    assert cli("pack", str(ws), str(oq)).returncode == 0
    (outs / OQ_CSV).write_text("ORG FILLED\n", encoding="utf-8")
    assert cli("pack", str(ws), str(coach)).returncode == 0
    assert (outs / OQ_CSV).read_text(encoding="utf-8") == "ORG FILLED\n"
    assert (outs / "follow-up.csv").is_file() and "ORG FILLED" not in (outs / "follow-up.csv").read_text(encoding="utf-8")


@pytest.mark.parametrize("mode", ["external"])
def test_open_questions_shared_copy(tmp_path, mode):
    ws, orgs = share_ws(tmp_path)
    p = _oq_pack(ws, why="Bharat Seals did not keep the record")
    q = json.loads(p.read_text(encoding="utf-8"))
    q["sections"][0]["items"][0]["good_evidence"] = "Bharat Seals work order"
    q["sections"][0]["items"][0]["lint_ok"] = {"rule": "JC1", "reason": "an organisation name, not a person"}
    p.write_text(json.dumps(q), encoding="utf-8")
    internal = cli("pack", str(ws), str(p))
    assert "Bharat Seals" in (ws.parent / "outputs" / OQ_CSV).read_text(encoding="utf-8")    # the fixture does seed it
    sign(ws, p, "--classification", "external", "--legal-review", "cleared")
    r = cli("pack", str(ws), str(p), "--share", mode, "--names", str(orgs))
    assert r.returncode == 0, internal.stderr + r.stderr
    outs = ws.parent / "outputs"
    text = (outs / f"follow-up.{mode}.csv").read_text(encoding="utf-8") if (outs / f"follow-up.{mode}.csv").exists() \
        else (outs / f"open-questions-follow-up.{mode}.csv").read_text(encoding="utf-8")
    assert "Bharat Seals" not in text and "FND-0001" in text
    assert not (outs / "follow-up.csv").exists() and not (outs / "follow-up.json").exists()


def test_open_questions_csv_one_row_per_finding():
    """Task 15: the CSV pastes back into the export, so it has one row per Finding ID. Evidence IDs in `cites` are
    not findings and give no row; two questions on one finding share its row, joined with '; ' in cite order."""
    from pmlc_lib.render.exports import open_questions_csv
    q1 = {"kind": "question", "question": "Who approved the seal?", "why": "w", "good_evidence": "purchase record",
          "cites": ["FND-0001", "EVD-0001"]}
    q2 = {"kind": "question", "question": "Was it tested?", "why": "w", "good_evidence": "test record",
          "cites": ["FND-0002", "FND-0001"]}
    q3 = {"kind": "question", "question": "Was it tested?", "why": "w", "good_evidence": "test record",
          "cites": ["FND-0002"]}
    rows = rows_of(open_questions_csv({"sections": [{"id": "q", "items": [q1, q2, q3]}]}))
    assert [r[0] for r in rows[1:]] == ["FND-0001", "FND-0002"]
    assert rows[1][1:3] == ["purchase record; test record", "Who approved the seal?; Was it tested?"]
    assert rows[2][1:3] == ["test record", "Was it tested?"]                     # the same text is not repeated
    assert open_questions_csv({"sections": [{"id": "q", "items": [dict(q1, cites=["EVD-0001"])]}]}) == ""
