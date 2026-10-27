"""Hazira golden packs, group F (the Phase 6 skills): each committed pack passes check-pack --strict and the language
check against a freshly built Hazira workspace with the Phase 6 artefacts, with its warnings pinned; the register
still gives 0 problems; the Phase 6 showcases keep the organisation's columns blank (Ruling X2: one file per group;
Phase 6 plan Task 18)."""
import json
import os
import shutil
import subprocess
import sys

import pytest

from test_hazira_samples import _epoch, _same
from test_pmlc import PMLC, ROOT, run

openpyxl = pytest.importorskip("openpyxl")
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
OUTPUTS = SAMPLE / "outputs"
REGISTER = OUTPUTS / "learnings-register.json"
# pack -> (check-pack --strict warnings, check-language warnings); errors and problems are 0 for every pack. The
# warnings are the uncited framing items, the coverage note and the draft (no handling block) line.
GROUP_F = {"safety-alert": (2, 0), "could-it-happen-here": (5, 0), "safety-moment-deck": (2, 0),
           "learning-team-facilitator": (11, 0), "restorative-response-guide": (9, 0), "systemic-accimap": (2, 0),
           "learning-effectiveness-plan": (3, 1)}
# the engine artefacts the Phase 6 skills gather from (each skill's SKILL.md runs these before writing its pack)
P6_COMMANDS = [("wai-wad",), ("accimap",), ("effect-plan", "--register", str(REGISTER))]


@pytest.fixture(scope="module")
def hz_f(tmp_path_factory):
    root = tmp_path_factory.mktemp("hazira-f")
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root),
        "--overlay", "india-process-site")
    ws = root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"
    for name in ("comparator.json", "comparison-map.json"):
        shutil.copy(SAMPLE / "comparator" / name, ws / name)
    for cmd, *flags in P6_COMMANDS:
        run(cmd, str(ws), *flags)
    for p in OUTPUTS.glob("*.json"):                     # the register and the goldens
        shutil.copy(p, ws.parent / "outputs" / p.name)
    return ws


def _cli(*args):
    r = subprocess.run([sys.executable, str(PMLC), *map(str, args)], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def test_group_f_packs_are_phase_6_goldens():
    skills = {json.loads((OUTPUTS / f"{p}.json").read_text(encoding="utf-8"))["skill"] for p in GROUP_F}
    since = {p.parent.name for p in (ROOT / "skills").glob("*/skill.json")
             if json.loads(p.read_text(encoding="utf-8")).get("since") == "2.0.0"}
    assert skills == set(GROUP_F) and skills <= since, skills - since     # each pack is its Phase 6 skill's golden


@pytest.mark.parametrize("pack", sorted(GROUP_F))
def test_group_f_samples_pass_strict(hz_f, pack):
    path = hz_f.parent / "outputs" / f"{pack}.json"
    warnings, lang_warnings = GROUP_F[pack]
    rc, out = _cli("check-pack", hz_f, path, "--strict", "--register", REGISTER)
    assert rc == 0 and "OK:" in out, out
    assert sum(line.startswith("warning:") for line in out.splitlines()) == warnings, out
    rc, out = _cli("check-language", hz_f, path)
    assert rc == 0 and f"check-language: 0 errors, {lang_warnings} warnings" in out, out
    for ext in ("html", "md"):                           # rendered beside the JSON (OD4-4)
        assert (OUTPUTS / f"{pack}.{ext}").is_file(), f"{pack}.{ext}"


def test_group_f_register_still_has_no_problems(hz_f):
    """Task 7 added `urgency` to the sample register (OD6-1): strict gives 0 problems and at most 17 warnings."""
    rc, out = _cli("check-register", hz_f, REGISTER, "--strict")
    assert rc == 0, out
    assert sum(line.startswith("warning:") for line in out.splitlines()) <= 17, out
    entries = json.loads(REGISTER.read_text(encoding="utf-8"))["entries"]
    assert any(e.get("urgency") for e in entries)
    md = (OUTPUTS / "learnings-register.md").read_text(encoding="utf-8")
    assert "Urgency" in md or "urgency" in md                  # the committed rendering is from the urgency register


def test_group_f_showcases_leave_organisation_columns_blank():
    """D7: the committed CIHH return template and learning-team notes carry no site, answer, response, assessor or
    team answer; the organisation fills them in."""
    wb = openpyxl.load_workbook(OUTPUTS / "could-it-happen-here.cihh-template.xlsx")
    ws = wb["Return"]
    assert ws["A1"].value == "Site" and ws["B1"].value in (None, "") and ws["A2"].value == "Pack"
    header = [c.value for c in ws[4]]
    assert header[:6] == ["lr_id", "condition", "evidence_to_check", "answer", "site_response", "assessed_by_role"]
    rows = [[c.value for c in r] for r in ws.iter_rows(min_row=5) if any(c.value for c in r)]
    pack = json.loads((OUTPUTS / "could-it-happen-here.json").read_text(encoding="utf-8"))
    checks = [it for s in pack["sections"] for it in s["items"] if it["kind"] == "self_check"]
    assert len(rows) == len(checks) > 0
    assert all(r[3] in (None, "") and r[4] in (None, "") and r[5] in (None, "") for r in rows)
    notes = (OUTPUTS / "learning-team-notes.csv").read_text(encoding="utf-8").splitlines()
    assert notes == ["prompt_id,prompt,team_answer,source"]


def test_group_f_register_renderings_are_fresh(hz_f, tmp_path):
    """The register's Markdown, workbook and dashboard were re-rendered after Task 7 added `urgency` (OD6-1): each is
    what the engine writes from the committed register today (the dashboard after the date normalisation, the
    workbook by cell values)."""
    env = dict(os.environ, SOURCE_DATE_EPOCH=_epoch())
    for cmd, name in (("register-md", "learnings-register.md"), ("register-xlsx", "learnings-register.xlsx"),
                      ("dashboard", "organisation-learning-map.html")):
        args = {"register-md": [hz_f, REGISTER], "register-xlsx": [REGISTER, "--ws", hz_f],
                "dashboard": [hz_f, "--register", REGISTER]}[cmd]
        r = subprocess.run([sys.executable, str(PMLC), cmd, *map(str, args), "--out", str(tmp_path / name)],
                           capture_output=True, text=True, env=env)
        assert r.returncode == 0, r.stdout + r.stderr
        _same(tmp_path / name, OUTPUTS / name)
