"""Hazira golden packs, group D (assurance and comparison): each committed pack passes check-pack --strict and the
language check against a freshly built Hazira workspace (L4-28, P4-27; Ruling X2: one file per group)."""
import json
import shutil
import subprocess
import sys

import pytest

from test_pmlc import PMLC, ROOT, run

pytest.importorskip("openpyxl")
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
REGISTER = SAMPLE / "outputs" / "learnings-register.json"
COMPARATOR = SAMPLE / "comparator"
GROUP_D = ["auditor-assurance-pack", "investigator-coach", "report-comparison", "report-comparison-client-safe",
           "report-comparison-regulator-safe"]


@pytest.fixture(scope="module")
def hz_d(tmp_path_factory):
    root = tmp_path_factory.mktemp("hazira-d")
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root),
        "--overlay", "india-process-site")
    ws = root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"
    for name in ("comparator.json", "comparison-map.json"):       # comparator_refs are checked against these
        shutil.copy(COMPARATOR / name, ws / name)
    out = ws.parent / "outputs"
    shutil.copy(REGISTER, out / REGISTER.name)
    items = json.loads(run("compare", str(ws), "--register", str(REGISTER), "--json"))   # the inputs are sound
    assert {r[0]: r[1] for r in items[1]["rows"]} == {"observation": 43, "root_cause": 6, "recommendation": 35,
                                                      "action": 0}
    assert items[2]["rows"][0][1:] == [21, 4, 0]        # every register learning has a counterpart
    return ws


@pytest.mark.parametrize("pack", GROUP_D)
def test_group_d_samples_pass_strict(hz_d, pack):
    path = SAMPLE / "outputs" / f"{pack}.json"
    r = subprocess.run([sys.executable, str(PMLC), "check-pack", str(hz_d), str(path), "--strict",
                        "--register", str(REGISTER)], capture_output=True, text=True)
    assert r.returncode == 0 and "OK:" in r.stdout, r.stdout + r.stderr
    r = subprocess.run([sys.executable, str(PMLC), "check-language", str(hz_d), str(path)],
                       capture_output=True, text=True)
    assert r.returncode == 0 and "0 errors" in r.stdout + r.stderr, r.stdout + r.stderr
    if pack.startswith("report-comparison-"):           # a variant keeps the main pack's sections, in order
        run("compare", str(hz_d), "--client-safe", str(path), "--main",
            str(SAMPLE / "outputs" / "report-comparison.json"))
        out = run("check-pack", str(hz_d), str(path), "--strict", "--share", "external",   # the skill's variant gate
                  "--register", str(REGISTER))
        assert "OK:" in out, out
