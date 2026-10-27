"""Machine contracts: skill.json manifests, schema, artefacts, workflow presets and audiences."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
REFS = SKILLS_DIR / "learnings-coach" / "references"
SKILLS = sorted(p.name for p in SKILLS_DIR.iterdir() if (p / "SKILL.md").exists())
SKILL_COUNT = len(list(SKILLS_DIR.glob("*/skill.json")))     # P5-1: the count is the skill folders, not a constant
KEYWORDS = {"type", "enum", "required", "properties", "additionalProperties", "items", "pattern", "const", "minItems"}
ALLOWED = KEYWORDS | {"$schema", "$id", "title", "description"}
KINDS = {"learnings-coach": "hub", "learnings-register": "register", "organisation-learning-map": "dissemination",
         "nine-m-analysis": "interactive", "learning-team-facilitator": "interactive"}
ANALYSIS = {"learning-clusters", "causal-map", "precursor-timeline", "interface-learnings", "barrier-learnings",
            "report-comparison", "cluster-learning-dossier", "latent-conditions-profile", "failure-to-learn-review",
            "compliance-crosswalk", "open-questions-register", "evidence-strength-scorecard",
            "recommendation-strength-review", "systemic-accimap", "learning-effectiveness-plan"}
sys.path.insert(0, str(SKILLS_DIR / "learnings-coach" / "scripts"))
from pmlc_lib.contracts import load_manifests, validate  # noqa: E402  (the engine's P3-6 validator)

PRESETS = ["first-48-hours", "full-cascade", "leadership", "assurance", "investigation-quality", "action-design",
           "sister-sites", "training", "follow-up"]


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def test_validator_catches_problems():
    schema = load(REFS / "skill.schema.json")
    good = load(SKILLS_DIR / "board-brief" / "skill.json")
    assert validate(good, schema) == []
    bad = dict(good, kind="nope", extra=1)
    del bad["since"]
    msgs = " ".join(validate(bad, schema))
    assert "kind" in msgs and "unknown key extra" in msgs and "missing since" in msgs
    assert validate(dict(good, scope=dict(good["scope"], levels=[5])), schema)
    assert validate(dict(good, interactive="yes"), schema)


def test_validator_type_list_and_const():
    """X10: `type` may be a list, as produces.pack is ["string", "null"]."""
    schema = load(REFS / "skill.schema.json")
    good = load(SKILLS_DIR / "board-brief" / "skill.json")
    for pack in ("board-brief", None):
        assert validate(dict(good, produces={"pack": pack, "files": []}), schema) == []
    assert "expected string/null" in " ".join(validate(dict(good, produces={"pack": 3, "files": []}), schema))
    assert validate(1, {"type": "integer"}) == [] and validate(True, {"type": "integer"})
    assert validate(1.5, {"type": "number"}) == [] and validate(True, {"type": "number"})
    assert validate(False, {"type": "boolean"}) == []
    assert validate("x", {"const": "y"}) == ["$: must equal 'y'"]


def test_engine_loads_every_manifest():
    assert sorted(load_manifests()) == SKILLS


def test_every_skill_has_manifest():
    schema = load(REFS / "skill.schema.json")
    assert len(SKILLS) == SKILL_COUNT
    for s in SKILLS:
        m = load(SKILLS_DIR / s / "skill.json")
        assert m["name"] == s
        assert validate(m, schema) == [], s
        want = KINDS.get(s, "analysis" if s in ANALYSIS else "audience")
        assert m["kind"] == want, s
        assert "workspace" in m["requires"], s
        assert m["embed_default"] == "cited"
        external = ("board-brief", "supply-chain-contractor-learnings", "could-it-happen-here")
        assert m["share_default"] == ("external" if s in external else "internal"), s


def test_clusters_required_where_filtering():
    for s in SKILLS:
        m = load(SKILLS_DIR / s / "skill.json")
        sc = m["scope"]
        if sc["tiers"] or sc["tags"] or sc.get("entities") or s in ("learnings-register",):
            assert "clusters" in m["requires"], s
    assert "register" in load(SKILLS_DIR / "organisation-learning-map" / "skill.json")["requires"]


# A Gather step that filters by tier, entity, relation or tag, or reads the classify outputs, needs clusters.json.
CLUSTERS_USE = re.compile(r"--(?:tier|entity|relation|tag|owner)\b|clusters\.json|role_overrides\.json"
                          r"|table-item <ws> (?:clusters|tiers|relations)")


def test_clusters_required_where_gather_uses_it():
    """I-5 (FR-2): any sub-skill whose SKILL.md or select presets use the classify outputs requires clusters."""
    presets = load(REFS / "select-presets.json")
    missing = []
    for s in SKILLS:
        if s == "learnings-coach":
            continue
        text = (SKILLS_DIR / s / "SKILL.md").read_text(encoding="utf-8")
        pre = json.dumps(presets.get(s, []))
        uses = CLUSTERS_USE.search(text) or re.search(r'"(?:tiers?|entit(?:y|ies)|relations?|tags?|owner)"', pre)
        if uses and "clusters" not in load(SKILLS_DIR / s / "skill.json")["requires"]:
            missing.append(s)
    assert not missing, missing


def test_schema_keyword_subset():
    def walk(node):
        assert isinstance(node, dict)
        for k, v in node.items():
            assert k in ALLOWED, f"keyword {k} is outside the P3-6 subset"
            if k == "properties":
                for sub in v.values():
                    walk(sub)
            elif k == "items":
                walk(v)
    walk(load(REFS / "skill.schema.json"))


def test_artefact_names_closed():
    art = load(REFS / "artefacts.json")
    assert len(art) == 27
    for name, a in art.items():
        assert set(a) <= {"file", "producer", "org_filled", "planned"}, name
        kind, _, who = a["producer"].partition(":")
        assert kind in ("engine", "skill") and who, name
        if kind == "skill":
            assert who in SKILLS or "planned" in a, name
            assert not (who in SKILLS and "planned" in a), f"{name}: {who} has shipped; drop planned"
    for s in SKILLS:
        m = load(SKILLS_DIR / s / "skill.json")
        for n in m["requires"] + m["optional_inputs"]:
            assert n in art, f"{s}: {n}"
        assert not set(m["requires"]) & set(m["optional_inputs"]), s


def test_workflows_reference_known_skills():
    wf = load(REFS / "workflows.json")
    assert list(wf) == PRESETS
    for name, w in wf.items():
        assert w["title"] and w["steps"], name
        for st in w["steps"]:
            assert set(st) <= {"skill", "mode", "planned", "when"}, name
            sk = st["skill"]
            assert sk in SKILLS or re.fullmatch(r"engine:[a-z-]+", sk) or "planned" in st, f"{name}: {sk}"
            if sk in SKILLS:
                assert "planned" not in st, f"{name}: {sk} has shipped"
    assert [s["skill"] for s in wf["full-cascade"]["steps"]][-1] == "engine:templates"
    assert wf["investigation-quality"]["steps"][-1]["when"] == "an official report is supplied"


def run_gen(*args):
    return subprocess.run([sys.executable, str(ROOT / "tools" / "make-audiences-md.py"), *args],
                          capture_output=True, text=True)


def test_audiences_md_generated(tmp_path):
    assert run_gen("--check").returncode == 0
    refs = tmp_path / "refs"
    refs.mkdir()
    (refs / "audiences.json").write_text((REFS / "audiences.json").read_text(encoding="utf-8"), encoding="utf-8")
    (refs / "audiences.md").write_text("stale\n", encoding="utf-8")
    assert run_gen("--check", "--refs", str(refs)).returncode == 1
    assert run_gen("--write", "--refs", str(refs)).returncode == 0
    assert (refs / "audiences.md").read_bytes() == (REFS / "audiences.md").read_bytes()
    assert run_gen("--check", "--refs", str(refs)).returncode == 0


def test_audiences_cover_audience_skills():
    auds = load(REFS / "audiences.json")
    keys = {"id", "label", "typical_people", "controls", "needs", "tier", "levels", "default_scope",
            "reading_level", "skill"}
    ids = [a["id"] for a in auds]
    assert len(ids) == len(set(ids)) == sum(load(SKILLS_DIR / s / "skill.json")["kind"] == "audience" for s in SKILLS)
    for a in auds:
        assert set(a) == keys
        assert a["tier"] in (None, "T1", "T2", "T3", "T4", "T5")
        assert a["reading_level"] in ("plain", "working", "executive", "technical")
    aud_skills = [a["skill"] for a in auds]
    expected = sorted(s for s in SKILLS if load(SKILLS_DIR / s / "skill.json")["kind"] == "audience")
    assert sorted(aud_skills) == expected
    for a in auds:
        m = load(SKILLS_DIR / a["skill"] / "skill.json")
        assert m["audiences"] == [a["id"]]
        assert m["scope"] == a["default_scope"]


# --- Phase 4 hygiene (Task 4 minor): pin what the manifests only checked loosely -------------------------------

PINNED_ARTEFACTS = {
    "workspace": ("workspace/findings.json", "engine:ingest", None),
    "clusters": ("workspace/clusters.json", "engine:classify", None),
    "causal_graph": ("workspace/causal_graph.json", "engine:causal", None),
    "timeline": ("workspace/timeline_candidates.json", "engine:timeline", None),
    "interfaces": ("workspace/interfaces.json", "engine:interfaces", None),
    "accimap": ("workspace/accimap.json", "engine:accimap", None),
    "register": ("outputs/learnings-register.json", "skill:learnings-register", None),
    "gaps": ("outputs/gaps.json", "engine:pack", None),
    "comparator": ("workspace/comparator.json", "skill:report-comparison", None),
    "adoption": ("outputs/adoption.csv", "engine:templates", None),
    "distribution": ("outputs/distribution.csv", "engine:templates", None),
    "verification": ("outputs/verification.jsonl", "engine:templates", None),
    "actions": ("outputs/actions.csv", "engine:export-actions", None),
    "open-questions": ("workspace/open_questions.json", "engine:open-questions", None),
    "nine-m-map": ("outputs/nine-m-map.json", "engine:pack", None),
    "evidence-audit": ("workspace/evidence_audit.json", "engine:evidence-audit", None),
    "hfacs-profile": ("workspace/hfacs_profile.json", "engine:hfacs-profile", None),
    "missed-opportunities": ("workspace/missed_opportunities.json", "engine:missed-opportunities", None),
    "library": ("$PMLC_LIBRARY", "engine:library", None),
    "nine-m-seed": ("workspace/nine_m_seed.json", "engine:nine-m-seed", None),
    "effect-plan": ("workspace/effect_plan.json", "engine:effect-plan", None),
    "wai-wad": ("workspace/wai_wad.json", "engine:wai-wad", None),
    "learning-team-notes": ("outputs/learning-team-notes.csv", "engine:templates", None),
    "cihh-template": ("outputs/<pack>.cihh-template.xlsx", "engine:templates", None),
    "cihh-consolidated": ("outputs/cihh-consolidated.json", "engine:consolidate", None),
    "frontline-learning-cards": ("outputs/frontline-learning-cards.json", "skill:frontline-learning-cards", None),
    # Task 14: top-management-brief reads it when present; Task 8 shipped the skill.
    "could-it-happen-here": ("outputs/could-it-happen-here.json", "skill:could-it-happen-here", None),
}


def test_p4h_artefact_files_and_producers_pinned():
    art = load(REFS / "artefacts.json")
    got = {n: (a["file"], a["producer"], a.get("planned")) for n, a in art.items()}
    assert got == PINNED_ARTEFACTS
    assert {n for n, a in art.items() if a["org_filled"]} == {"adoption", "distribution", "verification",
                                                              "learning-team-notes",
                                                              "cihh-template"}


def test_p4h_workflow_modes_planned_phases_and_when_pinned():
    wf = load(REFS / "workflows.json")
    modes = {(n, s["skill"]): s["mode"] for n, w in wf.items() for s in w["steps"] if "mode" in s}
    assert modes == {("first-48-hours", "learnings-register"): "draft",
                     ("first-48-hours", "safety-alert"): "internal",
                     ("sister-sites", "safety-alert"): "sister-site",
                     ("follow-up", "engine:templates"): "verification"}
    planned = {(n, s["skill"]): s["planned"] for n, w in wf.items() for s in w["steps"] if "planned" in s}
    assert planned == {}
    whens = {(n, s["skill"]): s["when"] for n, w in wf.items() for s in w["steps"] if "when" in s}
    assert whens == {("investigation-quality", "report-comparison"): "an official report is supplied",
                     ("investigation-quality", "learning-team-facilitator"):
                         "the user asks for a learning team or work-as-done session",
                     ("leadership", "failure-to-learn-review"): "the user asks for patterns or latent conditions",
                     ("leadership", "latent-conditions-profile"): "the user asks for patterns or latent conditions",
                     ("leadership", "risk-register-update"): "the user asks for risk-register or bow-tie changes",
                     ("leadership", "systemic-accimap"): "the user asks for patterns or latent conditions"}
    # plan --next stops on the first todo step and does not read "when": a guarded step must come after every
    # unguarded step of its preset, or a user who never asked for it cannot reach the rest (task 14 review I-1)
    for name, w in wf.items():
        kinds = ["when" in s for s in w["steps"]]
        assert kinds == sorted(kinds), name
