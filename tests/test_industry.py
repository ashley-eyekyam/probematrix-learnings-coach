"""The industry reference pack and `classify --industry` (Task 10, L3-10, Ruling P5-16)."""
import json
import re

import pytest

from conftest import process_export
from test_pmlc import ROOT, pmlc, run, run_fail

pytest.importorskip("openpyxl")
REF = ROOT / "skills" / "learnings-coach" / "references"
IND = REF / "industry" / "process"
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
BANNER = "Industry reference: process (method reference, not evidence)"


@pytest.fixture(scope="module")
def pws(tmp_path_factory):
    d = tmp_path_factory.mktemp("proc")
    x = process_export(d)
    run("ingest", str(x), "--slug", "proc-release", "--root", str(d))
    return d / "pmlc-runs" / [p.name for p in (d / "pmlc-runs").iterdir()][0] / "workspace"


def _f99(ws):
    cl = json.loads((ws / "clusters.json").read_text())
    n = len(cl["findings"])
    return sum(1 for v in cl["findings"].values() if "F99" in v["F"]), n


def test_industry_loads_overlay():
    base = pmlc._load_taxonomy(None, [])["_fingerprint"]
    ind = pmlc._load_taxonomy(None, [str(IND / "overlay.json")])["_fingerprint"]
    assert base != ind


def test_industry_unknown(pws):
    r = run_fail("classify", str(pws), "--industry", "aerospace")
    assert r.returncode == 2 and "process" in r.stderr and "Traceback" not in r.stderr


def test_process_export_f99_under_10pct(pws):
    run("classify", str(pws), "--no-overlay")
    base, n = _f99(pws)
    assert base * 10 > n                                  # the base taxonomy alone leaves the export unmapped
    out = run("classify", str(pws), "--industry", "process")
    f99, n = _f99(pws)
    assert f99 * 10 < n, (f99, n)
    assert BANNER in out


def test_industry_banner_printed(pws):
    out = run("classify", str(pws), "--industry", "process")
    assert out.count(BANNER) == 1
    assert BANNER not in run("classify", str(pws), "--no-overlay")


def test_industry_remembered_in_manifest(pws):
    run("classify", str(pws), "--industry", "process")
    cl = json.loads((pws / "clusters.json").read_text())
    assert any("industry" in o and "process" in o for o in cl["taxonomy"]["overlays"])
    again = run("classify", str(pws))                       # remembered like --overlay
    assert BANNER in again
    assert _f99(pws)[0] * 10 < _f99(pws)[1]


def test_industry_with_overlay(pws):
    run("classify", str(pws), "--industry", "process", "--overlay", "india-process-site")
    cl = json.loads((pws / "clusters.json").read_text())
    assert len(cl["taxonomy"]["overlays"]) == 2


def test_setup_accepts_industry(tmp_path):
    x = process_export(tmp_path)
    out = run("setup", str(x), "--slug", "p", "--root", str(tmp_path), "--industry", "process")
    assert BANNER in out


def test_hazira_unchanged_without_industry(tmp_path):
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(tmp_path),
        "--overlay", "india-process-site")
    ws = next((tmp_path / "pmlc-runs").iterdir()) / "workspace"
    cl = json.loads((ws / "clusters.json").read_text())
    tiers = {t: sum(1 for v in cl["findings"].values() if t in v["T"]) for t in ("T2", "T3", "T4")}
    assert tiers == {"T2": 219, "T3": 247, "T4": 63}
    assert not any("industry" in o for o in cl["taxonomy"]["overlays"])


def test_industry_files_shape():
    for n in ("overlay.json", "barriers.md", "indicators.md", "glossary.json"):
        assert (IND / n).is_file(), n
    g = json.loads((IND / "glossary.json").read_text())
    base = json.loads((REF / "glossary.json").read_text())
    assert set(g) <= set(base) and {"version", "terms"} <= set(g)
    assert len(g["terms"]) >= 10
    for t in g["terms"]:
        assert set(t) == set(base["terms"][0]) and t["definition"].strip()
        assert isinstance(t["do_not_translate"], bool) and isinstance(t["translations"], dict)
    assert len({t["term"] for t in g["terms"]}) == len(g["terms"])
    ov = json.loads((IND / "overlay.json").read_text())
    assert ov["name"] == "industry:process" and ov["extend"]["entities"]
    for grp in ov["extend"].values():
        for rx in grp.values():
            re.compile(rx)


def test_industry_md_shape():
    b = (IND / "barriers.md").read_text()
    i = (IND / "indicators.md").read_text()
    assert "method reference" in b.lower() and "method reference" in i.lower()
    for state in ("absent", "degraded", "defeated"):
        assert state in b
    for field in ("Owner role", "Data source", "Threshold", "Gaming risk"):
        assert field in i
    assert (REF / "industry" / "README.md").is_file()
    assert not re.search(r"FND-\d|EVD-\d", b + i)         # no incident facts


def test_industry_remembered_once(pws):
    run("classify", str(pws), "--industry", "process")
    out = run("classify", str(pws), "--industry", "process")
    assert out.count(BANNER) == 1 and "warning: previous classify" not in out
