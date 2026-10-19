"""check-language (JC1-JC12) on the synthetic export from test_pmlc.py (fictional event, no real data)."""
import copy
import json
import subprocess
import sys

import pytest

from test_pmlc import PMLC, ws  # noqa: F401  (ws is a module-scoped fixture)
from test_pack import FIX, STATUS, fixture, item, pack_fixtures, pack_with
import pmlc  # noqa: E402
import pmlc_lint as pl  # noqa: E402
import pmlc_pack as pp  # noqa: E402

BAD = FIX / "bad-l3-01.json"


@pytest.fixture(scope="module")
def w(ws):  # noqa: F811
    return pmlc.load_ws(ws)


def rules(hits, severity=None):
    return [h.rule for h in hits if severity is None or h.severity == severity]


def para_pack(text, **top):
    return pack_with(item("para", text=text, cites=["FND-0001"]), **top)


def test_l3_01_bad_pack_fails_check_pack(ws):  # noqa: F811
    r = subprocess.run([sys.executable, str(PMLC), "check-pack", str(ws), str(BAD)], capture_output=True, text=True)
    assert r.returncode == 1, r.stdout + r.stderr
    err = r.stderr
    assert 'bottom_line[0].text: JC2 "careless"' in err
    assert 'bottom_line[0].text: JC2 "disciplined"' in err
    assert 'sections[0].items[1].change: JC2 "hold him accountable"' in err
    assert 'bottom_line[0].text: JC1 "John Smith"' in err
    assert 'warning: sections[0].items[0].text: JC8 "80%"' in r.stdout
    assert 'warning: sections[0].items[1].hoc_tier: JC6' in r.stdout


def test_bad_fixture_is_not_a_golden_fixture():
    assert "bad-l3-01" not in pack_fixtures()


def seeded():
    texts = ["John Smith restarted the pump.",                  # JC1
             "The crew were punished.",                         # JC2
             "The crew should have tested the joint.",          # JC3
             "The leak was obviously visible.",                 # JC4
             "The restart was unlawful.",                       # JC5
             "Leaks start at 40% of flanges.",                  # JC8
             "Seals came from Acme Pumps Ltd.",                 # JC9
             "The leak was on pump P-101.",                     # JC10
             "Crews must stay vigilant."]                       # JC12
    items = [item("para", text=t, cites=["FND-0001"]) for t in texts]
    items.append(item("recommendation", change="Run a refresher course", hoc_tier="training", cites=["FND-0002"]))
    return pack_with(*items, status="Draft for review")             # JC11


def test_each_rule_fires_once(w):
    hits = pl.lint(seeded(), w, kind="pack", share="external")
    want = [f"JC{n}" for n in range(1, 13) if n != 7]
    assert sorted(rules(hits), key=lambda r: int(r[2:])) == want, pl.format_hits(hits)
    assert all(h.hint for h in hits)
    sev = {h.rule: h.severity for h in hits}
    assert sev["JC9"] == "error" and sev["JC10"] == "warning" and sev["JC6"] == "warning"


def test_t1_scope_raises_jc6_and_jc12(w):
    p = seeded()
    p["scope"] = {"tiers": ["T1"]}
    sev = {h.rule: h.severity for h in pl.lint(p, w, kind="pack")}
    assert sev["JC6"] == "error" and sev["JC12"] == "error"


def test_internal_share_hides_tags_and_softens_orgs(w):
    sev = {h.rule: h.severity for h in pl.lint(seeded(), w, kind="pack", share="internal")}
    assert "JC10" not in sev and sev["JC9"] == "warning"


def test_lint_safe_vocabulary_is_clean(w):
    text = ("The accountable owner of the multi-disciplinary review across engineering disciplines; the Control Room "
            "Operator on the night of 24 September; Hazira Gas Terminal")
    p = para_pack(text)
    p["sections"][0]["items"][0]["hfacs_level"] = "Routine Violation"
    hits = pl.lint(p, w, kind="pack")
    assert hits == [], pl.format_hits(hits)


@pytest.mark.parametrize("name", ["Shri R. K. Sharma", "Smt. Patel", "Mr J Smith", "Dr. Anand"])
def test_jc1_honorifics_and_initials(w, name):
    hits = pl.lint(para_pack(f"The permit was signed by {name} at the gate."), w, kind="pack")
    assert rules(hits, "error") == ["JC1"], pl.format_hits(hits)
    assert hits[0].path == "$.sections[0].items[0].text"


def test_jc1_honorific_and_pair_report_once(w):
    hits = pl.lint(para_pack("The permit was signed by Dr Anand Kumar at the gate."), w, kind="pack")
    assert [(h.rule, h.match) for h in hits] == [("JC1", "Dr Anand Kumar")]


def test_jc9_one_hit_per_name(w):
    hits = pl.lint(para_pack("Seals came from Acme Pumps Ltd."), w, kind="pack", orgs=["Acme Pumps"])
    assert rules(hits) == ["JC9"]


def test_jc1_names_file_entries(w):
    hits = pl.lint(para_pack("The permit was signed by the fitter, ravi, at the gate."), w, kind="pack",
                   names=["Ravi"])
    assert rules(hits) == ["JC1"] and hits[0].match == "ravi"


def test_jc1_honorific_role_is_not_vocabulary(w):
    # The synthetic export lists "Mr Fictional Person" as a role; it must not exempt the name.
    hits = pl.lint(para_pack("Fictional Person signed the permit."), w, kind="pack")
    assert rules(hits) == ["JC1"]


def test_lint_ok_suppresses_with_reason(w):
    p = para_pack("The restart was unlawful under the plant rules.")
    assert rules(pl.lint(p, w, kind="pack")) == ["JC5"]
    p["sections"][0]["items"][0]["lint_ok"] = {"rule": "JC5", "reason": "quoting the standard's title"}
    assert pl.lint(p, w, kind="pack") == []
    p["sections"][0]["items"][0]["lint_ok"] = {"rule": "JC5", "reason": " "}
    hits = pl.lint(p, w, kind="pack")
    assert ("lint_ok", "error") in [(h.rule, h.severity) for h in hits] and "JC5" in rules(hits)
    p["sections"][0]["items"][0]["lint_ok"] = {"rule": "JC99", "reason": "x"}
    assert "lint_ok" in rules(pl.lint(p, w, kind="pack"))
    assert any("lint_ok" in x for x in pp.check_pack(p, w).problems)


def test_lint_ok_is_scoped_to_its_item(w):
    p = pack_with(item("para", text="The restart was unlawful.", cites=["FND-0001"],
                       lint_ok={"rule": "JC5", "reason": "quoting the title of the rule"}),
                  item("para", text="The restart was unlawful.", cites=["FND-0001"]))
    hits = pl.lint(p, w, kind="pack")
    assert [(h.rule, h.path) for h in hits] == [("JC5", "$.sections[0].items[1].text")]


def test_jc8_number_found_in_cited_record_passes(w):
    # FND-0003: "Local seals without specification since March 2022." and its evidence; the synthetic
    # records have no durations, so the test writes one into the in-memory finding.
    w2 = copy.deepcopy(w)
    next(f for f in w2["findings"] if f["id"] == "FND-0003")["short"] += " Seals lasted 6 weeks."
    p = pack_with(item("para", text="Local seals lasted 6 weeks.", cites=["FND-0003"]))
    assert pl.lint(p, w2, kind="pack") == []
    p = pack_with(item("para", text="Local seals lasted 9 weeks.", cites=["FND-0003"]))
    assert rules(pl.lint(p, w2, kind="pack")) == ["JC8"]


def test_share_mode_from_classification(w):
    p = para_pack("Seals came from Acme Pumps Ltd.")
    p["handling"] = {"classification": "external"}
    assert [(h.rule, h.severity) for h in pl.lint(p, w, kind="pack")] == [("JC9", "error")]
    assert any("JC9" in x for x in pp.check_pack(p, w).problems)
    p["handling"] = {"classification": "internal"}
    assert [(h.rule, h.severity) for h in pl.lint(p, w, kind="pack")] == [("JC9", "warning")]
    r = pp.check_pack(p, w)
    assert not any("JC9" in x for x in r.problems) and any("JC9" in x for x in r.warnings)
    assert [(h.rule, h.severity) for h in pl.lint(p, w, kind="pack", share="public")] == [("JC9", "error")]


def test_orgs_file_entries(w):
    hits = pl.lint(para_pack("Seals came from the acme works."), w, kind="pack", orgs=["Acme"])
    assert [(h.rule, h.match) for h in hits] == [("JC9", "acme")]


def test_skipped_keys_are_not_scanned(w):
    p = para_pack("Test before service.", scope={"tags": ["John Smith careless"]})
    p["sections"][0]["items"][0]["id"] = "careless-step"
    assert pl.lint(p, w, kind="pack") == []


def test_status_problem_is_reported_once(w):
    p = para_pack("Test before service.", status="Draft")
    got = [x for x in pp.check_pack(p, w).problems if x.startswith("status")]
    assert got == ['status: must contain "Learning purposes: not a statutory document" (JC11)']


def test_register_lint(w):
    reg = {"title": "Synthetic register", "entries": [
        {"lr_id": "LR-01", "finding_ids": ["FND-0002"], "evidence_ids": ["EVD-0002"], "hfacs_level": "L3 careless",
         "lesson": "Add a checklist.", "tier_messages": {"T1": "Make leak tests part of performance reviews."},
         "recommendations": [{"what": "Brief the crews", "hoc_tier": "training", "leading_indicator": "x"}]}]}
    hits = pl.lint(reg, w, kind="register")
    got = sorted((h.rule, h.severity, h.path) for h in hits)
    assert got == [("JC11", "warning", "$.status"), ("JC2", "error", "$.entries[0].tier_messages.T1"),
                   ("JC6", "warning", "$.entries[0].recommendations")], got
    reg["status"] = STATUS
    assert "JC11" not in rules(pl.lint(reg, w, kind="register"))
    assert rules(pl.lint(reg["entries"], w, kind="register")).count("JC11") == 1


def test_check_register_reports_lint(ws, tmp_path):  # noqa: F811
    reg = copy.deepcopy(json.loads(json.dumps(__import__("test_pmlc").MINI_REG)))
    reg["entries"][0]["lesson"] = "The fitter was careless."
    f = tmp_path / "reg.json"
    f.write_text(json.dumps(reg), encoding="utf-8")
    r = subprocess.run([sys.executable, str(PMLC), "check-register", str(ws), str(f)], capture_output=True, text=True)
    assert r.returncode == 1 and 'JC2 "careless"' in r.stdout, r.stdout
    assert 'warning: status: must contain "Learning purposes: not a statutory document" (JC11)' in r.stdout


def test_format_hits():
    hits = [pl.Hit("JC2", "error", "$.a", "careless", "h1"), pl.Hit("JC3", "warning", "$.b", "failed to", "h2")]
    assert pl.format_hits(hits).splitlines() == ['ERROR JC2 $.a: "careless": h1', 'WARNING JC3 $.b: "failed to": h2',
                                                 "check-language: 1 errors, 1 warnings"]


def test_load_terms_schema():
    t = pl.load_terms()
    assert t["version"] == 1
    assert set(t["rules"]) == {f"JC{n}" for n in range(1, 13)}
    assert all(r["severity"] in ("error", "warning") and r["hint"] for r in t["rules"].values())
    assert "accountable owner" in t["allow"]
    for k in ("honorifics", "name_vocabulary", "role_nouns", "single_holder_entities"):
        assert isinstance(t[k], list) and t[k], k
    assert t["rules"]["JC3"]["hint"] == "say what was not done and what the system did not require or support"


def test_lint_hints_use_no_blame_words():
    t = pl.load_terms()
    for r, spec in t["rules"].items():
        assert not any(x in spec["hint"].lower() for x in ("blame", "careless", "punish", "disciplin")), r


def test_check_language_cli_exit_codes(ws, tmp_path, monkeypatch):  # noqa: F811
    ok = subprocess.run([sys.executable, str(PMLC), "check-language", str(ws), str(FIX / "supervisor-coach.json")],
                        capture_output=True, text=True)
    assert ok.returncode == 0, ok.stdout + ok.stderr
    assert ok.stdout.strip().splitlines()[-1].startswith("check-language: 0 errors")
    bad = subprocess.run([sys.executable, str(PMLC), "check-language", str(ws), str(BAD)], capture_output=True,
                         text=True)
    assert bad.returncode == 1
    assert bad.stdout.strip().splitlines()[-1].startswith("check-language: ")
    names = tmp_path / "names.txt"
    names.write_text("# staff\n\nRavi\n", encoding="utf-8")
    p = tmp_path / "p.json"
    p.write_text(json.dumps(para_pack("The fitter, Ravi, signed.")), encoding="utf-8")
    env = dict(__import__("os").environ, PMLC_NAMES=str(names))
    r = subprocess.run([sys.executable, str(PMLC), "check-language", str(ws), str(p)], capture_output=True,
                       text=True, env=env)
    assert r.returncode == 1 and 'JC1 $.sections[0].items[0].text: "Ravi"' in r.stdout, r.stdout
    r = subprocess.run([sys.executable, str(PMLC), "check-pack", str(ws), str(p), "--names", str(names)],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "JC1" in r.stderr
    p.write_text("[", encoding="utf-8")
    r = subprocess.run([sys.executable, str(PMLC), "check-language", str(ws), str(p)], capture_output=True, text=True)
    assert r.returncode != 0 and "invalid JSON" in (r.stdout + r.stderr)


def test_cmd_check_language_in_process(ws, capsys):  # noqa: F811
    a = pmlc.build_parser().parse_args(["check-language", str(ws), str(FIX / "board-brief.json"), "--share",
                                        "internal"])
    with pytest.raises(SystemExit) as e:
        pl.cmd_check_language(a)
    assert e.value.code == 0
    assert capsys.readouterr().out.strip().splitlines()[-1].startswith("check-language: 0 errors")
    with pytest.raises(SystemExit) as e:
        pl.cmd_check_language(pmlc.build_parser().parse_args(["check-language", str(ws), str(BAD)]))
    assert e.value.code == 1


@pytest.mark.parametrize("name", pack_fixtures() + ["all-kinds"])
def test_all_fixture_packs_lint_clean(w, name):
    hits = pl.lint(fixture(name), w, kind="pack")
    assert rules(hits, "error") == [], pl.format_hits(hits)


def test_lint_survives_malformed_documents(w):
    for doc in ([], "x", {"sections": "x", "bottom_line": [1, None]}, {"entries": [1, {"recommendations": "x"}]},
                {"sections": [{"items": [{"kind": "recommendation", "hoc_tier": "training", "cites": "x"}]}]}):
        pl.lint(doc, w, kind="pack" if not (isinstance(doc, dict) and "entries" in doc) else "register")
    assert STATUS in pl.STATUS_PHRASE


def test_jc6_needs_training_and_skips_indicator_targets(w):
    # Calibration on Hazira: an administrative system change alone (a CMMS escalation) is not "retraining only",
    # and a target in an indicator is a proposal, not a fact about the incident.
    admin = item("recommendation", change="Escalate overdue inspections in the CMMS", hoc_tier="administrative",
                 indicator="Overdue inspections closed within 30 days (target 100%)", cites=["FND-0002"])
    assert pl.lint(pack_with(admin), w, kind="pack") == []
    mixed = [item("recommendation", change="Add a decision aid", hoc_tier="administrative", cites=["FND-0002"]),
             item("recommendation", change="Run a refresher", hoc_tier="training", cites=["FND-0001"])]
    assert rules(pl.lint(pack_with(*mixed), w, kind="pack")) == []      # FND-0001 sits at level 1
