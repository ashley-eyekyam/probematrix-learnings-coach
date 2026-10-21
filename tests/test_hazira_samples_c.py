"""Hazira golden packs, group C (analysis): each committed pack passes check-pack --strict against the register and
has no check-language errors (L4-28, P4-27; Ruling X2: group C keeps its own test file)."""
import re
import shutil
import subprocess
import sys

import pytest

from test_pmlc import PMLC, ROOT, run

pytest.importorskip("openpyxl")
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
REGISTER = SAMPLE / "outputs" / "learnings-register.json"
GROUP_C = ["learning-clusters", "causal-map", "precursor-timeline", "interface-learnings", "barrier-learnings",
           "dossier-F02", "dossier-index"]


@pytest.fixture(scope="module")
def hz_c(tmp_path_factory):
    """One Hazira workspace for the whole group, built as the brief says (setup with the India overlay)."""
    root = tmp_path_factory.mktemp("hazira-c")
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root),
        "--overlay", "india-process-site")
    run_dir = root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire"
    shutil.copy(REGISTER, run_dir / "outputs" / "learnings-register.json")
    return run_dir / "workspace"


@pytest.mark.parametrize("pack", GROUP_C)
def test_group_c_samples_pass_strict(hz_c, pack):
    path = SAMPLE / "outputs" / f"{pack}.json"
    assert path.is_file(), f"{path} is missing"
    r = subprocess.run([sys.executable, str(PMLC), "check-pack", str(hz_c), str(path), "--strict",
                        "--register", str(REGISTER)], capture_output=True, text=True)
    assert r.returncode == 0 and re.search(r"^OK: ", r.stdout, re.M) and "problem(s)" not in r.stdout, \
        r.stdout + r.stderr
    r = subprocess.run([sys.executable, str(PMLC), "check-language", str(hz_c), str(path)],
                       capture_output=True, text=True)
    assert r.returncode == 0 and re.search(r"check-language: 0 errors", r.stdout), r.stdout + r.stderr
