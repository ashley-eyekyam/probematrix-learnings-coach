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
KEYWORDS = {"type", "enum", "required", "properties", "additionalProperties", "items", "pattern", "const"}
ALLOWED = KEYWORDS | {"$schema", "$id", "title", "description"}
KINDS = {"learnings-coach": "hub", "learnings-register": "register", "organisation-learning-map": "dissemination"}
ANALYSIS = {"learning-clusters", "causal-map", "precursor-timeline", "interface-learnings", "barrier-learnings",
            "report-comparison", "cluster-learning-dossier"}
PRESETS = ["first-48-hours", "full-cascade", "leadership", "assurance", "investigation-quality", "action-design",
           "sister-sites", "training", "follow-up"]


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def validate(obj, schema, path="$"):
    """Inline validator for the P3-6 keyword subset; returns a list of problems."""
    errs = []
    types = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}
    if "type" in schema:
        want = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]

        def ok(t):
            if t == "integer":
                return isinstance(obj, int) and not isinstance(obj, bool)
            return isinstance(obj, types[t]) and not (t != "boolean" and isinstance(obj, bool))
        if not any(ok(t) for t in want):
            return [f"{path}: expected {'/'.join(want)}"]
    if "const" in schema and obj != schema["const"]:
        errs.append(f"{path}: must equal {schema['const']!r}")
    if "enum" in schema and obj not in schema["enum"]:
        errs.append(f"{path}: {obj!r} not in {schema['enum']}")
    if isinstance(obj, str) and "pattern" in schema and not re.search(schema["pattern"], obj):
        errs.append(f"{path}: {obj!r} does not match {schema['pattern']}")
    if isinstance(obj, dict):
        for k in schema.get("required", []):
            if k not in obj:
                errs.append(f"{path}: missing {k}")
        props = schema.get("properties", {})
        for k, v in obj.items():
            if k in props:
                errs += validate(v, props[k], f"{path}.{k}")
            elif schema.get("additionalProperties") is False:
                errs.append(f"{path}: unknown key {k}")
    if isinstance(obj, list) and "items" in schema:
        for i, v in enumerate(obj):
            errs += validate(v, schema["items"], f"{path}[{i}]")
    return errs


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


def test_every_skill_has_manifest():
    schema = load(REFS / "skill.schema.json")
    assert len(SKILLS) == 23
    for s in SKILLS:
        m = load(SKILLS_DIR / s / "skill.json")
        assert m["name"] == s
        assert validate(m, schema) == [], s
        want = KINDS.get(s, "analysis" if s in ANALYSIS else "audience")
        assert m["kind"] == want, s
        assert "workspace" in m["requires"], s
        assert m["embed_default"] == "cited"
        assert m["share_default"] == ("external" if s in ("board-brief", "supply-chain-contractor-learnings")
                                      else "internal"), s


def test_clusters_required_where_filtering():
    for s in SKILLS:
        m = load(SKILLS_DIR / s / "skill.json")
        sc = m["scope"]
        if sc["tiers"] or sc["tags"] or sc.get("entities") or s in ("learnings-register",):
            assert "clusters" in m["requires"], s
    assert "register" in load(SKILLS_DIR / "organisation-learning-map" / "skill.json")["requires"]


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
    assert len(art) == 16
    for name, a in art.items():
        assert set(a) <= {"file", "producer", "org_filled", "planned"}, name
        kind, _, who = a["producer"].partition(":")
        assert kind in ("engine", "skill") and who, name
        if kind == "skill":
            assert who in SKILLS or "planned" in a, name
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
    assert len(ids) == len(set(ids)) == 13
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
