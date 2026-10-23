"""Phase 5, Task 21: extensions B to existing skills. manager-coach (work management for planners and schedulers,
select --prefix SVIO), auditor-assurance-pack (the assurance lens, P5-17), investigator-coach (evidence-audit
scorecard), learning-clusters (industry reference pack, P5-16), organisation-learning-map (the nine-m table, P5-18)
and the dossier reading budget (P5-19). Synthetic export from test_pmlc.py only (fictional event, no real data);
the Hazira numbers are in test_calibration_p5.py."""
import json
import re

import pytest

from test_pmlc import ROOT, ws  # noqa: F401  (ws is a module-scoped fixture)
import pmlc  # noqa: E402

SKILLS = ROOT / "skills"
REFS = SKILLS / "learnings-coach" / "references"
SAMPLE_OUT = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire" / "outputs"


@pytest.fixture(scope="module")
def w(ws):  # noqa: F811
    return pmlc.load_ws(ws)


def read(p) -> str:
    return p.read_text(encoding="utf-8")


def load(p):
    return json.loads(read(p))


def section(text, heading) -> str:
    m = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    assert m, heading
    return m.group(1)


# ----------------------------------------------------------------------------- manager-coach

def test_manager_coach_gathers_planned_operations():
    """The work-management section gains select --prefix SVIO, with its preset."""
    gather = section(read(SKILLS / "manager-coach" / "SKILL.md"), "Gather")
    assert re.search(r"^PMLC select <ws> --prefix SVIO --brief\s+#.*", gather, re.M), gather
    presets = load(REFS / "select-presets.json")["manager-coach"]
    assert {"name": "work-management-svio", "args": ["--prefix", "SVIO", "--brief"]} in presets


def test_hub_routes_planners_to_manager_coach():
    s2 = section(read(SKILLS / "learnings-coach" / "SKILL.md"), "Step 2: work out the intent")
    rows = [x for x in s2.splitlines() if x.startswith("| planners and schedulers")]
    assert len(rows) == 1 and "`manager-coach` (work-management section)" in rows[0], rows


def test_router_eval_for_planners():
    frag = load(ROOT / "evals" / "skills" / "manager-coach.json")
    routers = [e for e in frag["evals"] if e["kind"] == "router"]
    assert any(e["expectations"] == [{"type": "routes_to", "value": "manager-coach"}]
               and "planner" in e["prompt"].lower() for e in routers), routers


# ----------------------------------------------------------------------------- auditor-assurance-pack: lenses (P5-17)

LENSES = ["regulator", "insurer", "jv-partner", "client"]


def _lens_pack(lens=None, with_section=True):
    from test_pack import item, pack_with
    p = pack_with(item("para", text="Critical controls first.", cites=["FND-0002"]))
    if with_section:
        p["sections"].insert(0, {"id": "lens", "heading": "Assurance lens",
                                 "items": [item("para", text="For an insurer: critical controls first.",
                                                cites=["FND-0002"])]})
    if lens is not None:
        p["lens"] = lens
    return p


def test_lens_values_are_checked(w):
    import pmlc_pack as pp
    for v in LENSES:
        res = pp.check_pack(_lens_pack(v), w, strict=True)
        assert not [x for x in res.problems + res.warnings if x.startswith("lens")], (v, res.problems)
    res = pp.check_pack(_lens_pack("auditor"), w)
    assert "lens: must be one of regulator, insurer, jv-partner, client (leave it out for internal audit)" \
        in res.problems


def test_lens_needs_its_section(w):
    import pmlc_pack as pp
    msg = "lens: the insurer lens needs a lens section with one para on what that reader needs"
    res = pp.check_pack(_lens_pack("insurer", with_section=False), w)
    assert msg in res.warnings and msg not in res.problems
    assert msg in pp.check_pack(_lens_pack("insurer", with_section=False), w, strict=True).problems
    assert not [x for x in pp.check_pack(_lens_pack(None, with_section=False), w, strict=True).problems
                if x.startswith("lens")]


def test_lens_in_schema_labels_and_locked_fields():
    from pmlc_lib import strings
    from pmlc_lib.render import fields
    sch = load(REFS / "pack.schema.json")
    assert sch["properties"]["lens"] == {"enum": LENSES, "description": sch["properties"]["lens"]["description"]}
    for lang in ("en", "hi"):
        lab = load(REFS / "labels" / f"{lang}.json")
        assert lab["f.lens"] and all(lab[f"ui.lens.{v}"] for v in LENSES), lang
    assert "lens" in strings.LOCKED_FIELDS and "lens" in fields.RF_SKIP_KEYS
    assert "`lens` (optional)" in read(REFS / "pack-schema.md")


def test_lens_shown_in_the_header(w):
    import pmlc_pack as pp
    md = pp.render_pack_md(_lens_pack("jv-partner"), w)
    assert "**Assurance for:** a joint-venture partner" in md
    page = pp.render_pack_html(w, _lens_pack("jv-partner"), "2024-03-20-pump-fire", "2026-10-16")
    assert "Assurance for: a joint-venture partner" in page
    assert "Assurance for" not in pp.render_pack_md(_lens_pack(None), w)


def test_auditor_skill_asks_who_the_assurance_is_for():
    sk = load(SKILLS / "auditor-assurance-pack" / "skill.json")
    q = [x for x in sk["questions"] if x.startswith("Who is the assurance for?")]
    assert len(q) == 1 and all(v in q[0] for v in LENSES + ["internal audit"]), q
    prof = load(REFS / "pack-profiles.json")["auditor-assurance-pack"]
    assert {"id": "lens", "kinds": ["para"], "min": 0, "max": 1} in prof["sections"]
    fx = load(ROOT / "tests" / "fixtures" / "packs" / "auditor-assurance-pack.json")
    assert fx["lens"] == "insurer" and [s for s in fx["sections"] if s["id"] == "lens"]
    golden = load(SAMPLE_OUT / "auditor-assurance-pack.json")
    assert "lens" not in golden and not [s for s in golden["sections"] if s["id"] == "lens"]   # internal audit
    text = read(SKILLS / "auditor-assurance-pack" / "SKILL.md")
    for v in LENSES:
        assert f"`{v}`" in text, v


# ----------------------------------------------------------------------------- investigator-coach: evidence audit

def test_investigator_coach_reads_the_evidence_audit():
    sk = load(SKILLS / "investigator-coach" / "skill.json")
    assert "evidence-audit" in sk["optional_inputs"]
    text = read(SKILLS / "investigator-coach" / "SKILL.md")
    gather = section(text, "Gather")
    assert "PMLC evidence-audit <ws> --table-item scorecard" in gather
    assert "PMLC table-item <ws> evidence-types" in gather                    # the fallback stays
    row = next(x for x in section(text, "Write").splitlines() if x.startswith("| 1 | `evidence-audit` |")
               and "`table`" in x)
    assert "scorecard" in row and "evidence-types" in row, row
    golden = load(SAMPLE_OUT / "investigator-coach.json")
    first = golden["sections"][0]
    assert first["id"] == "evidence-audit" and first["items"][0]["id"] == "evidence-scorecard-table"


# ----------------------------------------------------------------------------- learning-clusters: industry pack (P5-16)

def test_learning_clusters_shows_the_industry_pack():
    from pmlc_lib.util import INDUSTRY_BANNER
    text = read(SKILLS / "learning-clusters" / "SKILL.md")
    before = section(text, "Before you start")
    assert "--industry process" in before and "learnings-coach/references/industry/process/" in before, before
    assert "PMLC classify <ws> --industry process" in section(text, "Gather")
    banner = INDUSTRY_BANNER.format("process")
    taxonomy = [x for x in section(text, "Write").splitlines() if "`taxonomy`" in x or "**Taxonomy" in x]
    assert any(banner in x for x in taxonomy), taxonomy


# ----------------------------------------------------------------------------- organisation-learning-map: nine-m (P5-18)

def _nine_m_register(tmp_path, values):
    import copy
    from test_pmlc import MINI_REG
    reg = copy.deepcopy(MINI_REG)
    second = dict(copy.deepcopy(reg["entries"][0]), lr_id="LR-02", priority=2, finding_ids=["FND-0003"])
    reg["entries"].append(second)
    for e, v in zip(reg["entries"], values):
        if v:
            e["nine_m"] = v
    p = tmp_path / "learnings-register.json"
    p.write_text(json.dumps(reg), encoding="utf-8")
    return p


def test_table_item_nine_m(ws, w, tmp_path):  # noqa: F811
    import pmlc_pack as pp
    from test_pmlc import run
    reg = _nine_m_register(tmp_path, ["M3", "M3"])
    it = json.loads(run("table-item", str(ws), "nine-m", "--register", str(reg)))
    assert it["kind"] == "table" and it["id"] == "nine-m-table"
    assert it["columns"] == ["M", "Name", "Learnings", "Priority 1", "LR-IDs"]
    assert [r[0] for r in it["rows"]] == [f"M{i}" for i in range(1, 10)]
    m3 = it["rows"][2]
    assert m3[0] == "M3" and m3[2:] == [2, 1, "LR-01, LR-02"] and m3[1]
    assert it["row_cites"][2] == ["FND-0001", "FND-0002", "FND-0003"]
    assert all(r[2] == 0 and r[4] == "none" for i, r in enumerate(it["rows"]) if i != 2)
    assert all(c == [] for i, c in enumerate(it["row_cites"]) if i != 2)
    pack = {"pack": "test-pack", "schema": 1, "title": "Test", "audience": "Testers",
            "status": "Learning purposes: not a statutory document",
            "bottom_line": [{"text": "Tested.", "cites": ["FND-0002"]}],
            "sections": [{"id": "nine-m", "heading": "Learnings by M", "items": [it]}]}
    assert pp.check_pack(pack, w).problems == []
    half = json.loads(run("table-item", str(ws), "nine-m", "--register", str(_nine_m_register(tmp_path, ["M3", None]))))
    assert half["rows"][-1] == ["none", "No 9M value recorded", 1, 0, "LR-02"]


def test_table_item_nine_m_needs_values(ws, tmp_path):  # noqa: F811
    from test_pmlc import run_fail
    r = run_fail("table-item", str(ws), "nine-m", "--register", str(_nine_m_register(tmp_path, [None, None])))
    assert "The register has no nine_m values" in r.stderr and "Traceback" not in r.stderr


def test_organisation_map_profile_and_skill_have_the_nine_m_table():
    prof = load(REFS / "pack-profiles.json")["organisation-learning-plan"]
    assert {"id": "nine-m", "kinds": ["table"], "min": 0, "max": 1} in prof["sections"]
    text = read(SKILLS / "organisation-learning-map" / "SKILL.md")
    assert "PMLC table-item <ws> nine-m --register <run>/outputs/learnings-register.json" in section(text, "Gather")
    assert "table-item <ws> <clusters|tiers|relations|hubs|interfaces|evidence-types|entity-tier|hoc|adoption|nine-m>" \
        in read(ROOT / "AGENTS.md").replace("$WS", "<ws>")
