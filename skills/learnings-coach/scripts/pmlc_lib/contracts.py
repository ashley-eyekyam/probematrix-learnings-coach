"""Machine contracts: skill.json manifests, the artefact vocabulary, workflow presets and audiences.

The engine validates manifests and packs with a small inline validator (Ruling P3-6: no JSON Schema dependency). It
supports only SUPPORTED_KEYWORDS: type, enum, const, pattern, required, properties, additionalProperties: false, items,
$defs, $ref (local "#/$defs/<name>" only), anyOf, minItems, minLength, minimum, maximum, and if/then (the `if` is
tested as a schema). `type` may be a string or a list of strings (Ruling X10). A boolean is never an integer or a
number. An unknown `type` name is reported, not raised.
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
_TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None), "number": (int, float),
          "integer": int}
SUPPORTED_KEYWORDS = frozenset({"type", "enum", "const", "pattern", "required", "properties", "additionalProperties",
                                "items", "$defs", "$ref", "anyOf", "minItems", "minLength", "minimum", "maximum",
                                "if", "then"})
ANNOTATIONS = frozenset({"$schema", "$id", "title", "description", "$comment"})
_REF_PREFIX = "#/$defs/"


def _type_ok(obj, t: str) -> bool:
    if t == "boolean":
        return isinstance(obj, bool)
    return isinstance(obj, _TYPES[t]) and not isinstance(obj, bool)


def unsupported_keywords(schema, path: str = "$") -> list:
    """Schema keywords the validator would silently ignore, as '<path>: <keyword>' strings (property names are not keywords)."""
    if not isinstance(schema, dict):
        return []
    out = [f"{path}: {k}" for k in schema if k not in SUPPORTED_KEYWORDS and k not in ANNOTATIONS]
    for k in ("properties", "$defs"):
        for name, sub in (schema.get(k) or {}).items():
            out += unsupported_keywords(sub, f"{path}.{k}.{name}")
    for k in ("items", "if", "then"):
        out += unsupported_keywords(schema.get(k), f"{path}.{k}")
    for i, sub in enumerate(schema.get("anyOf") or []):
        out += unsupported_keywords(sub, f"{path}.anyOf[{i}]")
    return out


def _selected(obj, branch: dict) -> bool:
    """True when obj is a dict that satisfies every const test in branch.properties (the branch's discriminator)."""
    if not isinstance(obj, dict):
        return False
    consts = [(k, v["const"]) for k, v in branch.get("properties", {}).items() if "const" in v]
    return bool(consts) and all(k in obj and obj[k] == c for k, c in consts)


def validate(obj, schema: dict, path: str = "$", _root: dict = None) -> list:
    """Problems with obj against schema (the P3-6 keyword subset), as a list of '<path>: <problem>' strings."""
    root = schema if _root is None else _root
    if "$ref" in schema:
        ref = schema["$ref"]
        name = ref[len(_REF_PREFIX):] if isinstance(ref, str) and ref.startswith(_REF_PREFIX) else None
        target = (root.get("$defs") or {}).get(name) if name else None
        if target is None:
            return [f"{path}: unresolved $ref {ref!r} (only {_REF_PREFIX}<name> is supported)"]
        return validate(obj, target, path, root)
    if "type" in schema:
        want = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        unknown = [t for t in want if t not in _TYPES]
        if unknown:
            return [f"{path}: unknown type {unknown[0]!r} in the schema"]
        if not any(_type_ok(obj, t) for t in want):
            return [f"{path}: expected {'/'.join(want)}"]
    errs = []
    if "const" in schema and obj != schema["const"]:
        errs.append(f"{path}: must equal {schema['const']!r}")
    if "enum" in schema and obj not in schema["enum"]:
        errs.append(f"{path}: {obj!r} not in {schema['enum']}")
    if isinstance(obj, str):
        if "pattern" in schema and not re.search(schema["pattern"], obj):
            errs.append(f"{path}: {obj!r} does not match {schema['pattern']}")
        if "minLength" in schema and len(obj) < schema["minLength"]:
            errs.append(f"{path}: must be at least {schema['minLength']} characters")
    if isinstance(obj, (int, float)) and not isinstance(obj, bool):
        if "minimum" in schema and obj < schema["minimum"]:
            errs.append(f"{path}: must be at least {schema['minimum']}")
        if "maximum" in schema and obj > schema["maximum"]:
            errs.append(f"{path}: must be at most {schema['maximum']}")
    if isinstance(obj, dict):
        for k in schema.get("required", []):
            if k not in obj:
                errs.append(f"{path}: missing {k}")
        props = schema.get("properties", {})
        for k, v in obj.items():
            if k in props:
                errs += validate(v, props[k], f"{path}.{k}", root)
            elif schema.get("additionalProperties") is False:
                errs.append(f"{path}: unknown key {k}")
    if isinstance(obj, list):
        if "minItems" in schema and len(obj) < schema["minItems"]:
            errs.append(f"{path}: needs at least {schema['minItems']} item(s)")
        if "items" in schema:
            for i, v in enumerate(obj):
                errs += validate(v, schema["items"], f"{path}[{i}]", root)
    if "anyOf" in schema:
        branches = schema["anyOf"]
        results = [validate(obj, b, path, root) for b in branches]
        if not any(r == [] for r in results):
            chosen = [r for b, r in zip(branches, results) if _selected(obj, _resolve(b, root))]
            errs += chosen[0] if chosen else [f"{path}: matches none of the {len(branches)} allowed shapes"]
    if "if" in schema and "then" in schema and validate(obj, schema["if"], path, root) == []:
        errs += validate(obj, schema["then"], path, root)
    return errs


def _resolve(branch: dict, root: dict) -> dict:
    ref = branch.get("$ref")
    if isinstance(ref, str) and ref.startswith(_REF_PREFIX):
        return (root.get("$defs") or {}).get(ref[len(_REF_PREFIX):]) or {}
    return branch


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
