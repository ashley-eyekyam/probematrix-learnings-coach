"""wai-wad (Phase 6, Task 4): work as imagined against work as done, the counterfactual lexicon and the
learning-team notes template. Synthetic export from test_pmlc.py only; the Hazira numbers are in
test_calibration_p6.py."""
import csv
import json
import subprocess
import sys

import pytest

from test_pmlc import PMLC, make_export, make_thin_export, run, run_fail, _changed_export
from pmlc_lib import waiwad


def _ev(**types):
    return {k: {"id": k, "type": t} for k, t in types.items()}


@pytest.fixture(scope="module")
def wsd(tmp_path_factory):
    d = tmp_path_factory.mktemp("ww")
    run("ingest", str(make_export(d)), "--legacy-out", str(d / "ws"))
    run("classify", str(d / "ws"))
    return d / "ws"


def test_wai_wad_gaps(wsd):
    """OR 2.2 is linked to a purchase log (work as done) and a work order (document): it is a gap, with both lists."""
    out = run("wai-wad", str(wsd))
    d = json.loads((wsd / "wai_wad.json").read_text(encoding="utf-8"))
    assert "Work as imagined" in out
    gap = next(g for g in d["gaps"] if g["code"] == "OR 2.2")
    assert gap["doc_evidence"] == ["EVD-0001"] and gap["wad_evidence"] == ["EVD-0003"]
    assert gap["findings"] == ["FND-0003"]
    assert d["codes"]["OR 2.2"]["both"] == ["FND-0003"]
    assert d["counts"]["codes_both"] == len(d["gaps"]) == 1
    assert d["counts"]["findings_both"] == 1 and d["counts"]["findings_wad"] == 1
    assert d["doc_types"] == ["document"] and d["wad_types"] == ["witness_statement", "log_record", "recording"]
    first = (wsd / "wai_wad.json").read_bytes()
    run("wai-wad", str(wsd))
    assert (wsd / "wai_wad.json").read_bytes() == first          # byte-identical re-run


def test_wai_wad_pools_evidence_per_code():
    """The code rule pools its findings: one finding with a document and a sibling with a witness is a gap, though
    no single finding has both."""
    w = {"findings": [{"id": "F1", "code": "AB 1.1", "name": "n", "evidence": ["A"], "justification": ""},
                      {"id": "F2", "code": "AB 1.1", "name": "n", "evidence": ["B"], "justification": ""}],
         "evidence": _ev(A="document", B="witness_statement")}
    d = waiwad.waiwad_compare(w)
    assert [g["code"] for g in d["gaps"]] == ["AB 1.1"]
    assert d["counts"]["findings_both"] == 0 and d["counts"]["codes_both"] == 1


def test_wai_wad_thin_export(tmp_path):
    run("ingest", str(make_thin_export(tmp_path)), "--legacy-out", str(tmp_path / "ws"))
    run("classify", str(tmp_path / "ws"))
    out = run("wai-wad", str(tmp_path / "ws"))                    # exits 0
    d = json.loads((tmp_path / "ws" / "wai_wad.json").read_text(encoding="utf-8"))
    assert d["gaps"] == [] and d["counts"]["findings_wad"] == 0
    assert waiwad.waiwad_lexicon()["notes"]["no_wad"] in d["notes"]
    assert ("Note: " + waiwad.waiwad_lexicon()["notes"]["no_wad"]) in out
    for which in ("gaps", "codes"):
        assert json.loads(run("wai-wad", str(tmp_path / "ws"), "--table-item", which))["kind"] == "table"
    assert json.loads(run("wai-wad", str(tmp_path / "ws"), "--items", "prompts")) is not None


def test_counterfactual_lexicon():
    """Whole words only, case-insensitive: 'failed tolerance' is not 'failed to'."""
    assert waiwad.counterfactual_hits("The valve failed tolerance checks.") == []
    assert waiwad.counterfactual_hits("The crew FAILED TO test it and didn’t log it") == ["failed to", "didn't"]
    assert waiwad.counterfactual_hits("A lack of cover; the guard lacked a lock") == ["lack of", "lacked"]
    assert waiwad.counterfactual_hits("unfailed tolerance, outdid nothing, shoulder") == []
    assert waiwad.counterfactual_hits("It could have been worse") == ["could have"]


def test_counterfactual_lexicon_is_the_jc3_patterns_plus_p6_6():
    lex = waiwad.waiwad_lexicon()
    terms = json.loads((PMLC.parent.parent / "references" / "lint-terms.json").read_text(encoding="utf-8"))
    assert set(terms["rules"]["JC3"]["patterns"]) <= set(lex["counterfactual"])
    words = " ".join(lex["counterfactual"])
    for phrase in ("failure to", "did not", "could have", "was not", "were not", "wasn", "weren", "inadequate",
                   "lack of", "lacked"):
        assert phrase in words, phrase


def test_prompt_items_are_questions(tmp_path):
    """Every item is a `question` that passes check-pack and holds no JC2/JC3 term of its own: the matched words
    appear only in `why`, quoted."""
    d = tmp_path
    run("ingest", str(make_export(d, summary=[])), "--legacy-out", str(d / "ws"))
    run("classify", str(d / "ws"))
    ws = d / "ws"
    # make the export's wording counterfactual by editing the ingested findings (a derived copy, not the export)
    fs = json.loads((ws / "findings.json").read_text(encoding="utf-8"))
    fs[0]["justification"] = "The crew failed to test the joint and did not log it."
    fs[0]["short"] = "Pump restarted; the crew failed to run a leak test"
    fs[1]["justification"] = "There was a lack of guidance."
    (ws / "findings.json").write_text(json.dumps(fs), encoding="utf-8")
    items = json.loads(run("wai-wad", str(ws), "--items", "prompts"))
    assert len(items) == 2
    for it in items:
        assert it["kind"] == "question" and it["question"].startswith("What made sense at the time about ")
        assert it["question"].endswith("?") and it["cites"][0].startswith("FND-")
        assert it["why"].startswith("The export's wording is counterfactual: \"")
        assert not waiwad.counterfactual_hits(it["question"])
    assert '"failed to"' in items[0]["why"] or '"failed to"' in items[1]["why"]
    assert len(json.loads(run("wai-wad", str(ws), "--items", "prompts", "--top", "1"))) == 1
    pack = {"pack": "wai-wad-test", "schema": 1, "title": "t", "audience": "learning team",
            "status": "Learning purposes: not a statutory document",
            "bottom_line": [{"text": "Ask what made sense at the time.", "cites": [items[0]["cites"][0]]}],
            "sections": [{"id": "s1", "heading": "Questions", "items": items}]}
    (d / "p.json").write_text(json.dumps(pack), encoding="utf-8")
    cp = subprocess.run([sys.executable, str(PMLC), "check-pack", str(ws), str(d / "p.json")],
                        capture_output=True, text=True)
    assert "sections[" not in cp.stdout + cp.stderr, cp.stdout + cp.stderr       # no problem under the items
    out = run("check-language", str(ws), str(d / "p.json"), "--json")
    hits = json.loads(out).get("hits") or json.loads(out).get("findings") or []
    mine = [h for h in hits if h.get("rule") in ("JC2", "JC3") and not h["path"].endswith(".why")]
    assert not mine, hits                                          # a matched word sits only in `why`, quoted


def test_ready_items_pass_a_profile_that_promotes_jc3_and_jc4(tmp_path):
    """Task 10's profile makes JC3/JC4 errors: the prompt items (the why line quotes the export's words) and the
    HFACS-named tables carry lint_ok, so a pack built from them gives no error."""
    from pmlc_lib import lint as jc
    from pmlc_lib.workspace import load_ws
    run("ingest", str(make_export(tmp_path, summary=[])), "--legacy-out", str(tmp_path / "ws"))
    run("classify", str(tmp_path / "ws"))
    ws = tmp_path / "ws"
    fs = json.loads((ws / "findings.json").read_text(encoding="utf-8"))
    fs[0]["justification"] = "The crew failed to test the joint and did not log it."
    (ws / "findings.json").write_text(json.dumps(fs), encoding="utf-8")
    run("wai-wad", str(ws))
    items = (json.loads(run("wai-wad", str(ws), "--items", "prompts"))
             + [json.loads(run("wai-wad", str(ws), "--table-item", k)) for k in ("gaps", "codes")])
    tbl = next(i for i in items if i["id"] == "wai-wad-codes-table")
    tbl["rows"][0][1] = "Failed to correct a known problem"             # a taxonomy name that trips JC3
    pack = {"pack": "x", "schema": 1, "title": "t", "audience": "learning team",
            "status": "Learning purposes: not a statutory document",
            "bottom_line": [{"text": "Ask.", "cites": ["FND-0001"]}],
            "sections": [{"id": "s1", "heading": "H", "items": items}]}
    w = load_ws(ws)
    prof = {"lint_errors": ["JC3", "JC4"]}
    errs = [h for h in jc.lint(pack, w, kind="pack", profile=prof) if h.severity == "error" and h.rule in ("JC3", "JC4", "JC5")]
    assert not errs, errs
    for it in items:                                                       # without lint_ok the profile would bite
        it2 = {k: v for k, v in it.items() if k != "lint_ok"}
        pack["sections"][0]["items"] = [it2]
        assert any(h.rule == "JC3" for h in jc.lint(pack, w, kind="pack", profile=prof)) or it["kind"] == "table" and it["id"] == "wai-wad-gaps-table"


def test_codes_table_values_and_json_envelope(wsd):
    t = json.loads(run("wai-wad", str(wsd), "--table-item", "codes"))
    d = json.loads((wsd / "wai_wad.json").read_text(encoding="utf-8"))
    assert t["columns"][2:] == ["Findings", "With documents", "With work-as-done evidence", "With both"]
    for row in t["rows"]:
        c = d["codes"][row[0]]
        assert row[2:] == [len(c["findings"]), len(c["doc"]), len(c["wad"]), len(c["both"])]
    assert len(t["rows"]) == len(t["row_cites"]) == d["counts"]["codes"]
    env = json.loads(run("wai-wad", str(wsd), "--json"))
    assert env["command"] == "wai-wad" and env["ok"] is True and env["exit_code"] == 0
    assert env["wai_wad"] == d


def test_top_guards_and_overlapping_hits(wsd):
    assert "--items" in run_fail("wai-wad", str(wsd), "--top", "3").stderr
    assert "1 or more" in run_fail("wai-wad", str(wsd), "--items", "prompts", "--top", "-2").stderr
    assert waiwad.counterfactual_hits("It could have prevented the fire") == ["could have prevented"]


def test_finding_without_a_code_gets_a_named_key():
    d = waiwad.waiwad_compare({"findings": [{"id": "F1", "name": "n", "evidence": [], "justification": ""}],
                               "evidence": {}})
    assert list(d["codes"]) == [waiwad.WAIWAD_NO_CODE]


def test_unmoded_templates_step_leaves_out_learning_team_notes(wsd):
    p = json.loads(run("plan", str(wsd), "--workflow", "full-cascade", "--json"))
    tpl = next(s for s in p["steps"] if s["skill"] == "engine:templates")
    assert "learning-team-notes" not in tpl["produces"] and "learning-team" not in " ".join(tpl["commands"])


def test_learning_team_template_blank(tmp_path):
    run("ingest", str(make_export(tmp_path)), "--legacy-out", str(tmp_path / "ws"))
    out = tmp_path / "learning-team-notes.csv"
    msg = run("templates", str(tmp_path / "ws"), "learning-team", "--out", str(out))
    assert "header only" in msg
    rows = list(csv.reader(out.read_text(encoding="utf-8").splitlines()))
    assert rows == [["prompt_id", "prompt", "team_answer", "source"]]    # the header and nothing else
    r = run_fail("templates", str(tmp_path / "ws"), "learning-team", "--out", str(out))   # never overwritten
    assert "already exists" in r.stderr + r.stdout
    assert out.read_text(encoding="utf-8").count("\n") == 1


def test_learning_team_template_needs_no_register(tmp_path):
    """Unlike adoption, the learning-team file does not read a register."""
    run("ingest", str(make_export(tmp_path)), "--legacy-out", str(tmp_path / "ws"))
    run("templates", str(tmp_path / "ws"), "learning-team", "--out", str(tmp_path / "x.csv"))


def test_status_knows_wai_wad(tmp_path):
    x = make_export(tmp_path)
    d = tmp_path / "ws"
    run("ingest", str(x), "--legacy-out", str(d))
    run("classify", str(d))
    run("wai-wad", str(d))
    state = {f["file"]: f["state"] for f in json.loads(run("status", str(d), "--json"))["files"]}
    assert state.get("wai_wad.json") == "current", state
    (tmp_path / "changed").mkdir()
    run("ingest", str(_changed_export(tmp_path / "changed")), "--legacy-out", str(d), "--force")
    state = {f["file"]: f["state"] for f in json.loads(run("status", str(d), "--json"))["files"]}
    assert state.get("wai_wad.json") == "stale", state


def test_artefacts_json_lists_wai_wad():
    refs = PMLC.parent.parent / "references"
    a = json.loads((refs / "artefacts.json").read_text(encoding="utf-8"))
    assert a["wai-wad"] == {"file": "workspace/wai_wad.json", "producer": "engine:wai-wad", "org_filled": False}
    assert a["learning-team-notes"]["org_filled"] is True
