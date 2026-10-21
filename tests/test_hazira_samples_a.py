"""Hazira golden packs, group A (leadership): each committed pack passes check-pack --strict and the language
check against a freshly built Hazira workspace (P4-27, Ruling X2). The packs stay drafts: no handling block."""
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
GROUP_A = ["board-brief", "top-management-brief", "site-leadership-coach", "manager-coach",
           "safety-committee-guide", "organisation-learning-plan"]


@pytest.fixture(scope="module")
def hz_ws(tmp_path_factory):
    root = tmp_path_factory.mktemp("hazira-a")
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root),
        "--overlay", "india-process-site")
    run_dir = root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire"
    shutil.copy(REGISTER, run_dir / "outputs" / "learnings-register.json")
    return run_dir / "workspace"


@pytest.mark.parametrize("name", GROUP_A)
def test_group_a_samples_pass_strict(hz_ws, name):
    path = OUTPUTS / f"{name}.json"
    pack = json.loads(path.read_text(encoding="utf-8"))
    assert pack["pack"] == name
    assert "Learning purposes: not a statutory document" in pack["status"]
    assert "handling" not in pack  # a draft: only sign-off writes handling, and the model never runs it
    r = subprocess.run([sys.executable, str(PMLC), "check-pack", str(hz_ws), str(path), "--strict",
                        "--register", str(REGISTER)], capture_output=True, text=True)
    assert r.returncode == 0 and "\nOK: " in "\n" + r.stdout, r.stdout + r.stderr
    r = subprocess.run([sys.executable, str(PMLC), "check-language", str(hz_ws), str(path)],
                       capture_output=True, text=True)
    assert r.returncode == 0 and "check-language: 0 errors" in r.stdout, r.stdout + r.stderr
