"""Hazira golden packs, group B (workforce): each committed pack passes check-pack --strict and check-language
against a Hazira workspace built once for the module (Phase 4, Task 6; Ruling X2)."""
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
GROUP_B = ["frontline-learning-cards", "supervisor-coach", "emergency-response-learnings", "training-designer",
           "supply-chain-contractor-learnings", "engineering-integrity-learnings"]


@pytest.fixture(scope="module")
def hz_ws_b(tmp_path_factory):
    root = tmp_path_factory.mktemp("hazira-b")
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root),
        "--overlay", "india-process-site")
    run_dir = root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire"
    shutil.copy(REGISTER, run_dir / "outputs" / "learnings-register.json")
    return run_dir / "workspace"


def _engine(*args):
    return subprocess.run([sys.executable, str(PMLC), *args], capture_output=True, text=True)


@pytest.mark.parametrize("pack", GROUP_B)
def test_group_b_samples_pass_strict(hz_ws_b, pack):
    path = OUTPUTS / f"{pack}.json"
    assert path.is_file(), f"missing golden pack {path.name}"
    r = _engine("check-pack", str(hz_ws_b), str(path), "--strict", "--register", str(REGISTER))
    assert r.returncode == 0 and "OK:" in r.stdout, r.stdout + r.stderr
    r = _engine("check-language", str(hz_ws_b), str(path))
    assert r.returncode == 0 and "check-language: 0 errors" in r.stdout, r.stdout + r.stderr
