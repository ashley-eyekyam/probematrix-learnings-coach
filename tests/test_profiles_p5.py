"""Phase 5 core (Task 1): the profile rules no-owner-due, banner:<key> and knowable-then, per-pack lint escalation
(lint_errors, P5-5), eval fragments (P5-2), strict png mode and the status contract for the Phase 5 artefacts.
Synthetic export from test_pmlc.py only (fictional event, no real data)."""
import json
import shutil
import subprocess
import sys

import pytest

from test_pmlc import PMLC, ROOT, make_export, run, ws  # noqa: F401  (ws is a module-scoped fixture)
from test_pack import item, pack_with
import pmlc  # noqa: E402
import pmlc_lint as pl  # noqa: E402
import pmlc_pack as pp  # noqa: E402
from pmlc_lib.pack import profiles  # noqa: E402

RUNNER = ROOT / "evals" / "run_evals.py"
_REAL_LOAD = profiles.load


@pytest.fixture(scope="module")
def w(ws):  # noqa: F811
    return pmlc.load_ws(ws)


def with_profile(monkeypatch, prof):
    """Give the synthetic pack name test-pack a profile, keeping every other profile file as it is."""
    monkeypatch.setattr(profiles, "load", lambda path=None: {"test-pack": prof} if path is None else _REAL_LOAD(path))


PROF = {"sections": [{"id": "s1", "kinds": ["para", "recommendation", "timeline"], "min": 0, "max": 99}]}


def test_no_owner_due_rule(ws, w, tmp_path, monkeypatch, capsys):  # noqa: F811
    with_profile(monkeypatch, dict(PROF, rules=["no-owner-due"]))
    pack = pack_with(item("recommendation", id="rec-1", owner="shift manager"))
    res = pp.check_pack(pack, w)
    assert "rec-1: owner and due dates are set by the organisation, not in this pack" in res.problems
    assert not [x for x in res.warnings if "owner and due dates" in x]
    pack = pack_with(item("recommendation", by_when="2026-06-30"))
    assert [x for x in pp.check_pack(pack, w).problems if "owner and due dates are set by the organisation" in x]
    p = tmp_path / "p.json"
    p.write_text(json.dumps(pack_with(item("recommendation", id="rec-1", owner="shift manager"))), encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        pp.cmd_check_pack(pmlc.build_parser().parse_args(["check-pack", str(ws), str(p)]))
    assert e.value.code not in (0, None)
    assert "owner and due dates are set by the organisation" in capsys.readouterr().err
    clean = pack_with(item("recommendation", owner="", by_when=""))
    assert not [x for x in pp.check_pack(clean, w).problems if "owner and due" in x]


def test_no_owner_due_needs_the_rule(w, monkeypatch):
    with_profile(monkeypatch, PROF)
    pack = pack_with(item("recommendation", owner="shift manager"))
    assert not [x for x in pp.check_pack(pack, w).problems + pp.check_pack(pack, w).warnings if "owner and due" in x]


def test_banner_rule(w, monkeypatch):
    assert profiles.BANNERS["crosswalk"] == "Aid to assurance, not a compliance opinion."
    assert set(profiles.BANNERS) == {"crosswalk", "people", "risk", "evidence", "profile-limits", "nine-m-demo"}
    with_profile(monkeypatch, dict(PROF, rules=["banner:crosswalk"]))
    res = pp.check_pack(pack_with(item("para", text="Something else.")), w)
    assert [x for x in res.warnings if "banner" in x and "crosswalk" in x], res.warnings
    assert not [x for x in res.problems if "crosswalk" in x]
    strict = pp.check_pack(pack_with(item("para", text="Something else.")), w, strict=True)
    assert [x for x in strict.problems if "crosswalk" in x]
    ok = pp.check_pack(pack_with(item("para", text=profiles.BANNERS["crosswalk"])), w)
    assert not [x for x in ok.warnings + ok.problems if "banner" in x]
    near = pp.check_pack(pack_with(item("para", text=profiles.BANNERS["crosswalk"] + " ")), w)
    assert [x for x in near.warnings if "banner" in x]
    with_profile(monkeypatch, dict(PROF, rules=["banner:nope"]))
    assert [x for x in pp.check_pack(pack_with(item("para")), w).warnings if "nope" in x]


def test_knowable_then_rule(w, monkeypatch):
    with_profile(monkeypatch, dict(PROF, rules=["knowable-then"]))
    tl = item("timeline", id="tl", events=[{"date": "2024-03-12", "text": "seal change", "knowable_then": True},
                                           {"date": "2024-03-13", "text": "restart"}])
    res = pp.check_pack(pack_with(tl), w)
    assert [x for x in res.warnings if "knowable_then" in x and "events[1]" in x], res.warnings
    assert not [x for x in res.warnings if "events[0]" in x and "knowable_then" in x]
    tl["events"][1]["knowable_then"] = False
    assert not [x for x in pp.check_pack(pack_with(tl), w).warnings if "knowable_then" in x]


def test_lint_errors_escalate(ws, w, tmp_path, monkeypatch):  # noqa: F811
    pack = pack_with(item("para", text="The work was negligent.", cites=["FND-0001"]))
    hits = pl.lint(pack, w, kind="pack")
    assert [h.severity for h in hits if h.rule == "JC5"] == ["warning"]
    hits = pl.lint(pack, w, kind="pack", profile={"lint_errors": ["JC5"]})
    assert [h.severity for h in hits if h.rule == "JC5"] == ["error"]
    with_profile(monkeypatch, dict(PROF, lint_errors=["JC5"]))
    res = pp.check_pack(pack, w)
    assert [x for x in res.problems if "JC5" in x], res.problems
    p = tmp_path / "p.json"
    p.write_text(json.dumps(pack), encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        pl.cmd_check_language(pmlc.build_parser().parse_args(["check-language", str(ws), str(p)]))
    assert e.value.code == 1
    with_profile(monkeypatch, PROF)
    assert not [x for x in pp.check_pack(pack, w).problems if "JC5" in x]
    with pytest.raises(SystemExit) as e:
        pl.cmd_check_language(pmlc.build_parser().parse_args(["check-language", str(ws), str(p)]))
    assert e.value.code == 0


def test_lint_errors_keep_lint_ok(w):
    it = item("para", text="The work was negligent.", cites=["FND-0001"],
              lint_ok=[{"rule": "JC5", "reason": "quoted from the regulator's notice"}])
    hits = pl.lint(pack_with(it), w, kind="pack", profile={"lint_errors": ["JC5"]})
    assert not [h for h in hits if h.rule == "JC5"]


def _evals_copy(tmp_path):
    d = tmp_path / "evals"
    d.mkdir()
    shutil.copy(ROOT / "evals" / "evals.json", d / "evals.json")
    (d / "skills").mkdir()
    for f in (ROOT / "evals" / "skills").glob("*.json"):     # the shipped fragments are part of the base set
        shutil.copy(f, d / "skills" / f.name)
    return d


def _check(path):
    return subprocess.run([sys.executable, str(RUNNER), "check", "--file", str(path)], capture_output=True, text=True)


def test_eval_fragments_loaded(tmp_path):
    d = _evals_copy(tmp_path)
    base = _check(d / "evals.json")
    assert base.returncode == 0, base.stdout + base.stderr
    n = int(base.stdout.split(" evals over ")[0].split()[-1])
    data = json.loads((d / "evals.json").read_text(encoding="utf-8"))
    one = next(e for e in data["evals"] if e["kind"] == "no-trigger")
    ids = [e["id"] for e in data["evals"]] + [e["id"] for f in (d / "skills").glob("*.json")
                                               for e in json.loads(f.read_text(encoding="utf-8"))["evals"]]
    new = dict(one, id=max(ids) + 1000)
    (d / "skills" / "x.json").write_text(json.dumps({"evals": [new]}), encoding="utf-8")
    r = _check(d / "evals.json")
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.startswith(f"{n + 1} evals over ")
    (d / "skills" / "y.json").write_text(json.dumps({"evals": [dict(new)]}), encoding="utf-8")
    r = _check(d / "evals.json")
    assert r.returncode == 1 and "duplicate id" in r.stdout, r.stdout
    (d / "skills" / "y.json").write_text("[]", encoding="utf-8")
    r = _check(d / "evals.json")
    assert r.returncode == 1 and "y.json" in r.stdout, r.stdout


def test_require_png_env(monkeypatch):
    import conftest
    from pmlc_lib import render
    monkeypatch.setattr(render, "find_browser", lambda: None)
    reason = conftest.probe_png()
    assert reason == "no Chromium-family browser"
    monkeypatch.setenv("PMLC_REQUIRE_PNG", "1")
    with pytest.raises(pytest.fail.Exception, match="png does not render here"):
        conftest.png_gate(reason)
    monkeypatch.delenv("PMLC_REQUIRE_PNG")
    with pytest.raises(pytest.skip.Exception, match="png does not render here"):
        conftest.png_gate(reason)
    conftest.png_gate(None)                 # renders: nothing happens


P5_ARTEFACTS = {"evidence_audit.json": ["evidence-audit"], "hfacs_profile.json": ["hfacs-profile"],
                "open_questions.json": ["open-questions"], "nine_m_seed.json": ["nine-m-seed"],
                "missed_opportunities.json": ["missed-opportunities"]}


@pytest.mark.xfail(strict=True, reason="each Phase 5 engine task registers its artefact with status; Task 24 "
                                       "removes this marker")
def test_status_knows_p5_artefacts(tmp_path):
    x = make_export(tmp_path)
    d = tmp_path / "ws"
    run("ingest", str(x), "--legacy-out", str(d))
    run("classify", str(d))
    run("causal", str(d))
    run("timeline", str(d))
    for cmd in P5_ARTEFACTS.values():
        run(*cmd, str(d))
    run("ingest", str(x), "--legacy-out", str(d))
    out = json.loads(run("status", str(d), "--json"))
    state = {f["file"]: f["state"] for f in out["files"]}
    for name in P5_ARTEFACTS:
        assert state.get(name) == "stale", (name, state)
