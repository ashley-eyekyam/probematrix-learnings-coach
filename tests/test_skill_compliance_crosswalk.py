"""Phase 5 Task 19: the compliance-crosswalk skill. Its manifest, profile, workflow step, evals and hub row follow the
plan, and its Hazira golden pack pastes the engine's crosswalk tables (ISO 45001 and CCPS RBPS, on the sample
register) unchanged, carries the fixed banner, raises JC5 to an error, and passes check-pack --strict --register and
check-language with no errors."""
import json
import shutil

import pytest

from test_pmlc import ROOT, run, run_fail

SKILL = "compliance-crosswalk"
REFS = ROOT / "skills" / "learnings-coach" / "references"
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
GOLDEN = SAMPLE / "outputs" / f"{SKILL}.json"
REGISTER = SAMPLE / "outputs" / "learnings-register.json"
BANNER = "Aid to assurance, not a compliance opinion."
FRAMEWORKS = ("iso45001", "rbps")


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def test_manifest():
    m = load(ROOT / "skills" / SKILL / "skill.json")
    assert (m["kind"], m["audiences"]) == ("analysis", [])
    assert m["requires"] == ["workspace", "register"] and m["optional_inputs"] == ["adoption", "distribution"]
    assert m["produces"]["pack"] == SKILL and m["formats"] == ["docx"]
    assert (m["share_default"], m["embed_default"], m["since"]) == ("internal", "cited", "2.0.0")
    assert len(m["questions"]) == 1
    q = m["questions"][0]
    assert q.startswith("Which framework?")
    for answer in ("iso45001", "psm", "rbps", "seveso", "icmm", "india", "CSV"):
        assert answer in q, answer


def test_profile():
    p = load(REFS / "pack-profiles.json")[SKILL]
    assert [(s["id"], s["kinds"], s["min"], s["max"]) for s in p["sections"]] == [
        ("banner", ["para"], 1, 1), ("crosswalk-*", ["table"], 1, 3), ("by-element", ["learning"], 1, 12),
        ("unverified", ["para"], 0, 1)]
    assert p["bottom_line"] == {"min": 1, "max": 5}
    assert p["rules"] == ["banner:crosswalk"] and p["lint_errors"] == ["JC5"]


def test_workflow_step_unplanned():
    wf = load(REFS / "workflows.json")
    steps = [s for s in wf["assurance"]["steps"] if s["skill"] == SKILL]
    assert len(steps) == 1 and "planned" not in steps[0]


def test_evals_fragment():
    ev = load(ROOT / "evals" / "skills" / f"{SKILL}.json")["evals"]
    kinds = {e["kind"] for e in ev}
    assert {"trigger", "no-trigger", "collision", "router"} <= kinds and len(ev) >= 4
    router = [e for e in ev if e["kind"] == "router"]
    assert any(x.get("value") == SKILL for e in router for x in e["expectations"])
    assert all(e["owner"] == SKILL for e in ev if e["kind"] != "router")


def test_hub_routes_to_it():
    hub = (ROOT / "skills" / "learnings-coach" / "SKILL.md").read_text(encoding="utf-8")
    step2 = hub.split("## Step 2", 1)[1].split("## Step 3", 1)[0]
    assert f"| `{SKILL}` |" in step2
    assert len(hub.splitlines()) <= 150


# ----------------------------------------------------------------------------------------- the Hazira golden

@pytest.fixture(scope="module")
def hz(tmp_path_factory):
    pytest.importorskip("openpyxl")
    root = tmp_path_factory.mktemp("hazira-cw")
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root),
        "--overlay", "india-process-site")
    ws = root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"
    shutil.copy(REGISTER, ws.parent / "outputs" / REGISTER.name)
    shutil.copy(GOLDEN, ws.parent / "outputs" / GOLDEN.name)
    return ws


def _items(pack, sec):
    return [it for s in pack["sections"] if s["id"] == sec for it in s["items"]]


def test_golden_pastes_the_engine_tables(hz):
    pack = load(GOLDEN)
    for fw in FRAMEWORKS:
        want = json.loads(run("crosswalk", str(hz), "--framework", fw, "--table-item"))
        got = _items(pack, f"crosswalk-{fw}")
        assert len(got) == 1 and got[0]["kind"] == "table", fw
        assert {k: got[0][k] for k in ("id", "columns", "rows", "row_cites", "lint_ok")} == \
            {k: want[k] for k in ("id", "columns", "rows", "row_cites", "lint_ok")}, fw


def test_golden_shows_iso_and_rbps():
    pack = load(GOLDEN)
    iso = _items(pack, "crosswalk-iso45001")[0]["rows"]
    rbps = _items(pack, "crosswalk-rbps")[0]["rows"]
    assert len(iso) == 23 and len(rbps) == 20
    assert {r[1] for r in iso + rbps} <= {"evidenced here", "partly", "needs organisation evidence"}


def test_golden_banner_roles_and_learnings():
    pack = load(GOLDEN)
    assert [it["text"] for it in _items(pack, "banner")] == [BANNER]
    assert pack["skill"] == SKILL and "handling" not in pack
    items = [it for s in pack["sections"] for it in s["items"]]
    assert not [it for it in items if it.get("owner") or it.get("by_when")]            # D7
    lr = {e["lr_id"] for e in load(REGISTER)["entries"]}
    elements = _items(pack, "by-element")
    assert 1 <= len(elements) <= 12
    ids = {r["id"] for fw in load(REFS / "standards-crosswalk.json")["frameworks"].values()
           for r in fw["requirements"]}
    for it in elements:                     # each names the requirement it speaks to and the register learning
        assert it["kind"] == "learning" and it["learning"] in lr and it["cites"]
        assert it["clauses"] and set(it["clauses"]) <= ids, it
    assert len(_items(pack, "unverified")) == 1      # every RBPS element outside "learn from experience" is unverified


def test_golden_passes_strict_and_language(hz):
    out = run("check-pack", str(hz), str(hz.parent / "outputs" / GOLDEN.name), "--strict", "--register",
              str(REGISTER))
    assert out.splitlines()[-1].startswith("OK:"), out                   # run() asserts exit 0: no problems
    lang = json.loads(run("check-language", str(hz), str(hz.parent / "outputs" / GOLDEN.name), "--json"))
    assert lang["ok"] and lang["output"][-1].startswith("check-language: 0 errors"), lang


def test_jc5_is_an_error_in_this_pack(hz, tmp_path):
    """P5-5: the profile raises JC5 (legal-judgment words) to an error, so a pack that says a site 'breached' a clause
    fails check-pack even without --strict."""
    pack = load(GOLDEN)
    _items(pack, "by-element")[0]["explanation"] = "The site breached the clause."
    p = hz.parent / "outputs" / GOLDEN.name
    bad = tmp_path / GOLDEN.name
    bad.write_text(json.dumps(pack), encoding="utf-8")
    shutil.copy(bad, p)
    try:
        r = run_fail("check-pack", str(hz), str(p))
        assert "JC5" in r.stdout + r.stderr
    finally:
        shutil.copy(GOLDEN, p)


def test_golden_is_rendered():
    """Task 24 rendered the golden beside its JSON (OD4-4), so it is no longer staged in RENDER_PENDING."""
    from pmlc_lib import samples
    assert f"{SKILL}.json" not in samples.RENDER_PENDING
    assert all(GOLDEN.with_suffix(f".{ext}").is_file() for ext in ("html", "md"))
