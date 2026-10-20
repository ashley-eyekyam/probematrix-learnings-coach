"""profile: thin-export data-quality flags (P3-8) and the HFACS levels table."""
import json

import pytest

from test_pmlc import make_export, make_thin_export, run, pmlc  # noqa: F401

pytest.importorskip("openpyxl")

NO_EVIDENCE = 'No Evidence Links sheet: learnings rest on findings only; use evidence_strength "inferred"'


def _thin(tmp_path, roles=None, classify=True):
    x = make_thin_export(tmp_path) if roles is None else make_thin_export(tmp_path, roles=roles)
    ws = tmp_path / "ws"
    run("ingest", str(x), "--legacy-out", str(ws))
    if classify:
        run("classify", str(ws))
    return ws


def test_thin_export_flags_all_fire(tmp_path):
    ws = _thin(tmp_path, classify=False)
    out = run("profile", str(ws))
    for line in (f"- {NO_EVIDENCE}", "- No narrative text", "- No dated text: timelines will show order only",
                 "- Run classify to check the F99 and T9 shares"):
        assert line in out
    run("classify", str(ws))
    out = run("profile", str(ws))
    assert "Run classify" not in out
    assert "- Empty tiers: T2, T3, T4, T5" in out
    assert "- Thin tiers: T1 (4)" in out
    assert "High F99" not in out and "High T9" not in out


def test_high_f99_and_t9_shares_fire(tmp_path):
    ws = _thin(tmp_path, roles=["Mr Fictional Person", "Mr Fictional Person", "Pump Technician", "Pump Technician"])
    out = run("profile", str(ws))
    assert "- High F99 share: 2 of 4 findings unmapped (over 10%)" in out
    assert "- High T9 share: 2 of 4 findings touch unresolved roles (over 25%)" in out


def test_default_export_has_no_thin_flags(tmp_path):
    x = make_export(tmp_path, narrative="Pump fire on 12 March 2024. " * 12)
    ws = tmp_path / "ws"
    run("ingest", str(x), "--legacy-out", str(ws))
    out = run("profile", str(ws))
    assert "No Evidence Links" not in out and "No narrative" not in out and "No dated text" not in out


def test_hazira_profile_flags(tmp_path_factory):
    from test_sample import EXPORT
    root = tmp_path_factory.mktemp("hz15")
    run("ingest", str(EXPORT), "--slug", "hazira-gas-release-fire", "--root", str(root))
    ws = root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"
    run("classify", str(ws), "--overlay", "india-process-site")
    out = run("profile", str(ws))
    assert "- Thin tiers: T5 (1)" in out
    for absent in ("No Evidence Links", "No narrative", "No dated text", "High F99", "High T9", "Empty tiers",
                   "Run classify"):
        assert absent not in out


def test_profile_hfacs_levels_table(tmp_path):
    ws = _thin(tmp_path, classify=False)
    out = run("profile", str(ws))
    levels = json.loads((pmlc.REFS / "hfacs-codes.json").read_text(encoding="utf-8"))["levels"]
    assert "## HFACS levels" in out and "| Level | Name | Definition | Findings |" in out
    for k, d in levels.items():
        assert f"| {k} | {d['name']} | {d['definition']} |" in out


def test_thin_workspace_honest_pack_passes_strict(tmp_path):
    # check-pack --strict arrives with Task 10; until then this asserts a clean check-pack (switch on merge).
    ws = _thin(tmp_path)
    pack = {"pack": "test-pack", "schema": 1, "title": "Thin pack: frontline only", "audience": "Frontline",
            "status": "Learning purposes: not a statutory document",
            "bottom_line": [{"text": "Test before service.", "cites": ["FND-0001"]}],
            "sections": [{"id": "s1", "heading": "Frontline", "items": [
                {"kind": "learning", "lesson": "Check the seal before restart.", "cites": ["FND-0001"]}]}]}
    p = tmp_path / "pack.json"
    p.write_text(json.dumps(pack), encoding="utf-8")
    out = run("check-pack", str(ws), str(p))
    assert "OK" in out
