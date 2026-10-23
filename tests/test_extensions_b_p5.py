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
