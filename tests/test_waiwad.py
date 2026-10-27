"""wai-wad (Phase 6, Task 4): work as imagined against work as done, the counterfactual lexicon and the
learning-team notes template. Synthetic export from test_pmlc.py only; the Hazira numbers are in
test_calibration_p6.py."""
import csv
import json

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
    assert d["notes"] and "no work-as-done evidence" in " ".join(d["notes"]).lower() or "Note:" in out
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
    pack = {"pack": "wai-wad-test", "title": "t", "audience": "learning team",
            "status": "Learning purposes: not a statutory document",
            "sections": [{"id": "s1", "heading": "Questions", "items": items}]}
    (d / "p.json").write_text(json.dumps(pack), encoding="utf-8")
    out = run("check-language", str(ws), str(d / "p.json"), "--json")
    hits = json.loads(out).get("hits") or json.loads(out).get("findings") or []
    mine = [h for h in hits if h.get("rule") in ("JC2", "JC3") and not h["path"].endswith(".why")]
    assert not mine, hits                                          # a matched word sits only in `why`, quoted


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
