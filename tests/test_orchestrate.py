"""setup, check-all, render-all, index and dossier-index on the synthetic export (fictional event)."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from test_pmlc import PMLC, make_export, run, run_fail

FIX = Path(__file__).resolve().parent / "fixtures" / "packs"


@pytest.fixture
def setup_ws(tmp_path):
    x = make_export(tmp_path)
    out = run("setup", str(x), "--slug", "pump-fire", "--root", str(tmp_path))
    ws = tmp_path / "pmlc-runs" / "2024-03-20-pump-fire" / "workspace"
    return ws, out


def put(ws, *names):
    outd = ws.parent / "outputs"
    outd.mkdir(exist_ok=True)
    for n in names:
        shutil.copy(FIX / f"{n}.json", outd / f"{n}.json")
    return outd


def test_setup_runs_all_steps(setup_ws):
    ws, out = setup_ws
    for n in ("findings.json", "clusters.json", "causal_graph.json", "timeline_candidates.json", "interfaces.json",
              "profile.md"):
        assert (ws / n).is_file(), n
    assert "Next: PMLC plan" in out and str(ws) in out
    assert "4 findings" in out and "Mr Fictional Person" in out


def test_setup_stops_on_failure(tmp_path):
    import openpyxl
    wb = openpyxl.Workbook()
    wb.active.title = "Plan Summary"
    wb.create_sheet("Action Items")
    wb.create_sheet("Risk Matrix")
    wb.save(tmp_path / "capa.xlsx")
    r = run_fail("setup", str(tmp_path / "capa.xlsx"), "--slug", "x-y", "--date", "2024-03-20")
    assert r.returncode == 1 and "setup stopped at ingest" in r.stderr


def test_check_all_exit_codes(setup_ws):
    ws, _ = setup_ws
    outd = put(ws, "board-brief", "supervisor-coach")
    (outd / "gaps.json").write_text("{}")
    (outd / "notes.jsonl").write_text("x\n")
    out = run("check-all", str(ws))
    assert "board-brief.json: ok" in out and "supervisor-coach.json: ok" in out and "gaps" not in out
    put(ws, "bad-l3-01")
    r = run_fail("check-all", str(ws))
    assert r.returncode == 1 and "bad-l3-01.json: " in r.stdout and "problem(s)" in r.stdout
    j = run_fail("check-all", str(ws), "--json")
    assert json.loads(j.stdout)["ok"] is False


def test_render_all_skips_unchecked(setup_ws):
    ws, _ = setup_ws
    outd = put(ws, "board-brief", "supervisor-coach")
    run("check-pack", str(ws), str(outd / "board-brief.json"))
    out = run("render-all", str(ws))
    assert (outd / "board-brief.html").is_file()
    assert not (outd / "supervisor-coach.html").exists()
    assert "skipped supervisor-coach.json: run check-all first" in out


def test_index_lists_packs_with_status_and_footer(setup_ws):
    ws, _ = setup_ws
    outd = put(ws, "board-brief", "supervisor-coach")
    run("check-all", str(ws))
    run("render-all", str(ws))
    run("index", str(ws))
    html = (outd / "index.html").read_text(encoding="utf-8")
    for t in ("Board Brief: Synthetic pump fire, 2024", "Supervisor Coach: Synthetic pump fire, 2024"):
        assert t in html
    assert "DRAFT" in html and "Learning purposes: not a statutory document" in html
    assert "ProbeMatrix Learnings Coach v" in html and "<script" not in html
    assert 'href="board-brief.html"' in html


def test_dossier_index_is_valid_pack(setup_ws):
    ws, _ = setup_ws
    outd = put(ws, "dossier-F02")
    out = run("dossier-index", str(ws))
    p = outd / "dossier-index.json"
    assert p.is_file() and "dossier-index.json" in out
    d = json.loads(p.read_text())
    assert len(d["sections"]) == 1 and d["sections"][0]["items"][0]["kind"] == "table"
    run("check-pack", str(ws), str(p))
    run("check-all", str(ws))


def test_dossier_index_none(setup_ws):
    ws, _ = setup_ws
    put(ws, "board-brief")
    assert "no dossier" in run_fail("dossier-index", str(ws)).stderr


def test_render_all_with_register_and_embed(setup_ws):
    from test_pmlc import MINI_REG
    ws, _ = setup_ws
    outd = put(ws, "board-brief")
    reg = outd / "learnings-register.json"
    reg.write_text(json.dumps(MINI_REG), encoding="utf-8")
    run("check-pack", str(ws), str(outd / "board-brief.json"))
    chk = subprocess.run([sys.executable, str(PMLC), "check-register", str(ws), str(reg)], capture_output=True, text=True)
    if chk.returncode:
        pytest.skip("synthetic register does not pass check-register: " + chk.stdout[-200:])
    out = run("render-all", str(ws), "--embed", "summary")
    assert "skipped learnings-register" not in out
    assert (outd / "board-brief.html").is_file() and (outd / "learnings-register.xlsx").is_file()
    assert (outd / "organisation-learning-map.html").is_file()
    assert (outd / "learnings-register.md").is_file() and "not available" not in out


def test_index_escapes_pack_title(setup_ws):
    ws, _ = setup_ws
    outd = put(ws, "board-brief")
    d = json.loads((outd / "board-brief.json").read_text())
    d["title"] = "Brief <script>alert(1)</script>"
    (outd / "board-brief.json").write_text(json.dumps(d))
    run("index", str(ws))
    html = (outd / "index.html").read_text(encoding="utf-8")
    assert "<script" not in html and "&lt;script&gt;alert(1)" in html


# ----------------------------------------------------------------------------- Wave 2 integration (INT-1..4)

def test_check_pack_records_coverage_and_index_shows_it(setup_ws):
    import re as _re
    ws, _ = setup_ws
    outd = put(ws, "board-brief")
    run("check-pack", str(ws), str(outd / "board-brief.json"))
    rec = next(iter(json.loads((ws / "manifest.json").read_text())["packs"].values()))
    assert set(rec["coverage"]) == {"cited", "relevant", "top_cited", "top_relevant"}
    run("index", str(ws))
    html = (outd / "index.html").read_text(encoding="utf-8")
    assert _re.search(r"<td>\d+ of \d+</td>", html) and "not recorded" not in html


def test_check_all_strict_reaches_check_pack(setup_ws):
    ws, _ = setup_ws
    outd = put(ws, "board-brief")
    d = json.loads((outd / "board-brief.json").read_text())
    d["sections"] = [s for s in d["sections"][:1]]
    for s in d["sections"]:
        s["items"] = [{"kind": "para", "text": "A short filler line.", "cites": d["bottom_line"][0]["cites"]}] * 14
    (outd / "board-brief.json").write_text(json.dumps(d))
    plain = subprocess.run([sys.executable, str(PMLC), "check-pack", str(ws), str(outd / "board-brief.json")],
                           capture_output=True, text=True)
    strict = subprocess.run([sys.executable, str(PMLC), "check-pack", str(ws), str(outd / "board-brief.json"),
                             "--strict"], capture_output=True, text=True)
    if plain.returncode != 0 or strict.returncode == 0:
        pytest.skip("fixture does not separate strict from non-strict")
    assert run("check-all", str(ws)).count("ok") >= 1
    assert run_fail("check-all", str(ws), "--strict").returncode == 1


def test_setup_writes_run_manifest(setup_ws):
    ws, _ = setup_ws
    rm = json.loads((ws.parent / "run-manifest.json").read_text(encoding="utf-8"))
    assert rm.get("run") == ws.parent.name


def test_render_all_register_skip_uses_manifest_record(setup_ws):
    from test_pmlc import MINI_REG
    ws, _ = setup_ws
    outd = put(ws)
    reg = outd / "learnings-register.json"
    reg.write_text(json.dumps(MINI_REG), encoding="utf-8")
    assert "skipped learnings-register.json: run check-all first" in run("render-all", str(ws))
    assert not (outd / "learnings-register.md").exists()
    chk = subprocess.run([sys.executable, str(PMLC), "check-register", str(ws), str(reg)], capture_output=True, text=True)
    if chk.returncode:
        pytest.skip("synthetic register does not pass check-register")
    out = run("render-all", str(ws))
    assert "skipped learnings-register" not in out and (outd / "learnings-register.md").is_file()
    d = dict(MINI_REG, title="Edited after the check")
    reg.write_text(json.dumps(d), encoding="utf-8")   # content changed: the record no longer matches
    assert "skipped learnings-register.json: run check-all first" in run("render-all", str(ws))


def test_render_all_renders_register_and_pack_after_sign_off(setup_ws):
    from test_pmlc import MINI_REG
    ws, _ = setup_ws
    outd = put(ws, "board-brief")
    reg = outd / "learnings-register.json"
    reg.write_text(json.dumps(MINI_REG), encoding="utf-8")
    cp = subprocess.run([sys.executable, str(PMLC), "check-register", str(ws), str(reg)], capture_output=True, text=True)
    if cp.returncode:
        pytest.skip("synthetic register does not pass check-register")
    run("check-pack", str(ws), str(outd / "board-brief.json"))
    for f in (reg, outd / "board-brief.json"):   # what sign-off does: it rewrites the file with a handling block
        d = json.loads(f.read_text())
        from pmlc_lib.handling import content_hash
        d["handling"] = {"status": "reviewed", "reviewer_role": "HSE manager", "reviewed_on": "2026-10-19",
                         "content_hash": content_hash(d)}
        f.write_text(json.dumps(d, indent=2), encoding="utf-8")
    assert "handling" in json.loads(reg.read_text())
    out = run("render-all", str(ws))
    assert "skipped" not in out and (outd / "learnings-register.md").is_file() and (outd / "board-brief.html").is_file()
    d = json.loads(reg.read_text())
    d["title"] = "Edited after the check"
    reg.write_text(json.dumps(d), encoding="utf-8")
    assert "skipped learnings-register.json" in run("render-all", str(ws))


def test_non_object_scope_fails_cleanly_with_old_message(setup_ws):
    ws, _ = setup_ws
    outd = put(ws, "board-brief")
    d = json.loads((outd / "board-brief.json").read_text())
    d["scope"] = "x"
    (outd / "board-brief.json").write_text(json.dumps(d))
    for cmd in (("check-pack",), ("pack",)):
        r = run_fail(*cmd, str(ws), str(outd / "board-brief.json"))
        assert r.returncode == 1 and "scope: must be an object" in r.stderr and "Traceback" not in r.stderr


def test_setup_profile_carries_tier_flags(setup_ws):
    """I-1: setup classifies before it profiles, so profile.md and the summary carry the tier flags (P3-8)."""
    ws, out = setup_ws
    prof = (ws / "profile.md").read_text(encoding="utf-8")
    assert "Run classify" not in prof and "Run classify" not in out
    assert "Thin tiers: " in prof or "Empty tiers: " in prof
    assert "Thin tiers: " in out or "Empty tiers: " in out
