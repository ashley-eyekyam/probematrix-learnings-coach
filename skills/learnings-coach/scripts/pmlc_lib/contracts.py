"""Machine contracts: skill.json manifests, the artefact vocabulary, workflow presets and audiences.

The engine validates manifests with a small inline validator (Ruling P3-6: no JSON Schema dependency). It supports
only the keywords skill.schema.json uses: type, enum, required, properties, additionalProperties: false, items,
pattern and const. `type` may be a string or a list of strings (Ruling X10).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from .util import HERE, REFS

SKILLS_ROOT = HERE.parents[1]          # skills/ (the folder holding learnings-coach/)
SCHEMA_FILE = REFS / "skill.schema.json"
CONTRACT_FILES = ("skill.schema.json", "artefacts.json", "workflows.json", "audiences.json", "select-presets.json")
_TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None), "number": (int, float)}


def _type_ok(obj, t: str) -> bool:
    if t == "integer":
        return isinstance(obj, int) and not isinstance(obj, bool)
    if t == "boolean":
        return isinstance(obj, bool)
    return isinstance(obj, _TYPES[t]) and not isinstance(obj, bool)


def validate(obj, schema: dict, path: str = "$") -> list:
    """Problems with obj against schema (the P3-6 keyword subset), as a list of '<path>: <problem>' strings."""
    if "type" in schema:
        want = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_type_ok(obj, t) for t in want):
            return [f"{path}: expected {'/'.join(want)}"]
    errs = []
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


def _load(p: Path):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        sys.exit(f"cannot read {Path(p).name}: {e}")


def load_schema() -> dict:
    return _load(SCHEMA_FILE)


def skill_dirs(skills_root=None) -> list:
    """Skill folders under skills_root: every folder with a SKILL.md or a skill.json, sorted by name."""
    root = Path(skills_root) if skills_root else SKILLS_ROOT
    return sorted(p for p in root.iterdir() if p.is_dir() and ((p / "SKILL.md").is_file() or (p / "skill.json").is_file()))


def load_manifests(skills_root=None) -> dict:
    """{name: manifest} for every skill folder; exits 1 with 'skill.json for <name>: <errors>' on a bad manifest."""
    schema = load_schema()
    out = {}
    for d in skill_dirs(skills_root):
        p = d / "skill.json"
        if not p.is_file():
            sys.exit(f"skill.json for {d.name}: missing")
        try:
            m = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            sys.exit(f"skill.json for {d.name}: not valid JSON ({e})")
        errs = validate(m, schema)
        if not errs and m["name"] != d.name:
            errs = [f"$.name: {m['name']!r} differs from the folder name"]
        if errs:
            sys.exit(f"skill.json for {d.name}: {'; '.join(errs)}")
        out[d.name] = m
    return out


def load_artefacts(refs=None) -> dict:
    return _load(Path(refs or REFS) / "artefacts.json")


def load_workflows(refs=None) -> dict:
    return _load(Path(refs or REFS) / "workflows.json")


def load_audiences(refs=None) -> list:
    return _load(Path(refs or REFS) / "audiences.json")


def contract_paths(skills_root=None) -> list:
    """Every contract file a plan is built from: the references above plus each skill's skill.json."""
    root = Path(skills_root) if skills_root else SKILLS_ROOT
    return [REFS / n for n in CONTRACT_FILES] + [d / "skill.json" for d in skill_dirs(root)
                                                   if (d / "skill.json").is_file()]
