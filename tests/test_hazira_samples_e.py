"""Hazira golden packs, group E (the Phase 5 skills): each committed pack passes check-pack --strict and the language
check against a freshly built Hazira workspace with the Phase 5 artefacts (L4-28, P4-27; Ruling X2: one file per group;
plan Task 24)."""
import json
import shutil
import subprocess
import sys

import pytest

from test_pmlc import PMLC, ROOT, run

pytest.importorskip("openpyxl")
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
OUTPUTS = SAMPLE / "outputs"
REGISTER = OUTPUTS / "learnings-register.json"
GROUP_E = ["compliance-crosswalk", "evidence-strength-scorecard", "failure-to-learn-review",
           "latent-conditions-profile", "nine-m-analysis", "open-questions-register", "people-workforce-learnings",
           "recommendation-strength-review", "risk-register-update"]
# the engine artefacts the Phase 5 skills gather from (each skill's SKILL.md runs these before writing its pack)
P5_COMMANDS = ["evidence-audit", "hfacs-profile", "open-questions", "nine-m-seed", "missed-opportunities"]


@pytest.fixture(scope="module")
def hz_e(tmp_path_factory):
    root = tmp_path_factory.mktemp("hazira-e")
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root),
        "--overlay", "india-process-site")
    ws = root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"
    for name in ("comparator.json", "comparison-map.json"):
        shutil.copy(SAMPLE / "comparator" / name, ws / name)
    shutil.copy(OUTPUTS / "nine-m-session.json", ws / "nine_m_session.json")   # the scripted session (OD5-1)
    for cmd in P5_COMMANDS:
        run(cmd, str(ws))
    for p in OUTPUTS.glob("*.json"):                     # the register, the 9M map and the goldens
        shutil.copy(p, ws.parent / "outputs" / p.name)
    return ws


def test_group_e_packs_are_phase_5_goldens():
    skills = {json.loads((OUTPUTS / f"{p}.json").read_text(encoding="utf-8"))["skill"] for p in GROUP_E}
    since = {p.parent.name for p in (ROOT / "skills").glob("*/skill.json")
             if json.loads(p.read_text(encoding="utf-8")).get("since") == "2.0.0"}
    assert skills == set(GROUP_E) and skills <= since, skills - since     # each pack is its Phase 5 skill's golden


@pytest.mark.parametrize("pack", GROUP_E)
def test_group_e_samples_pass_strict(hz_e, pack):
    path = hz_e.parent / "outputs" / f"{pack}.json"
    r = subprocess.run([sys.executable, str(PMLC), "check-pack", str(hz_e), str(path), "--strict",
                        "--register", str(REGISTER)], capture_output=True, text=True)
    assert r.returncode == 0 and "OK:" in r.stdout, r.stdout + r.stderr
    r = subprocess.run([sys.executable, str(PMLC), "check-language", str(hz_e), str(path)],
                       capture_output=True, text=True)
    assert r.returncode == 0 and "0 errors" in r.stdout + r.stderr, r.stdout + r.stderr
    for ext in ("html", "md"):                           # rendered beside the JSON (OD4-4)
        assert (OUTPUTS / f"{pack}.{ext}").is_file(), f"{pack}.{ext}"
