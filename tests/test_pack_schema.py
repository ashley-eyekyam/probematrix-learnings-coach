"""references/pack.schema.json and the contracts validator keywords it relies on (Phase 4, Task 3)."""
import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
REFS = ROOT / "skills" / "learnings-coach" / "references"
FIX = Path(__file__).resolve().parent / "fixtures" / "packs"
sys.path.insert(0, str(ROOT / "skills" / "learnings-coach" / "scripts"))
from pmlc_lib.contracts import unsupported_keywords, validate  # noqa: E402
from pmlc_lib.pack.schema import KINDS  # noqa: E402

SCHEMA = json.loads((REFS / "pack.schema.json").read_text(encoding="utf-8"))


def _load(name):
    return json.loads((FIX / name).read_text(encoding="utf-8"))


def _item(pack, kind):
    return next(it for s in pack["sections"] for it in s["items"] if it["kind"] == kind)


def _is_pack(path):
    """A pack fixture is a JSON object with a `sections` key; other fixtures (e.g. html-golden.json) are not packs."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return isinstance(data, dict) and "sections" in data


def test_every_fixture_validates():
    files = [f for f in sorted(FIX.glob("*.json")) if _is_pack(f)]
    assert len(files) >= 20
    for f in files:
        assert validate(json.loads(f.read_text(encoding="utf-8")), SCHEMA) == [], f.name
    assert (FIX / "all-kinds.json") in files
    assert (FIX / "html-golden.json") not in files


def _bad_missing_sections(p):
    del p["sections"]


def _bad_schema_2(p):
    p["schema"] = 2


def _bad_card(p):
    del _item(p, "card")["warning_signs"]


def _bad_option(p):
    it = _item(p, "question")
    it["type"] = "single"
    it["options"] = [{"text": "A", "correct": True}, {"text": "B"}]


def _bad_lang(p):
    p["lang"] = "english"


def _bad_toolbox(p):
    p["sections"][0]["items"].append(
        {"kind": "toolbox", "opening_question": "q", "story": "s", "warning_signs": "one, two", "one_change": "c",
         "crew_question": "q", "cites": ["FND-0001"]})


@pytest.mark.parametrize("mutate,needle", [
    (_bad_missing_sections, "missing sections"), (_bad_schema_2, "schema"), (_bad_card, "missing warning_signs"),
    (_bad_option, "missing correct"), (_bad_lang, "lang"), (_bad_toolbox, "warning_signs")])
def test_bad_packs_fail(mutate, needle):
    pack = copy.deepcopy(_load("all-kinds.json"))
    mutate(pack)
    errs = validate(pack, SCHEMA)
    assert errs and needle in " ".join(errs), errs


def test_new_fields_and_kinds_validate():
    pack = copy.deepcopy(_load("all-kinds.json"))
    pack.update(skill="frontline-learning-cards", lang="hi", dir="ltr", translation_of="all-kinds")
    items = pack["sections"][0]["items"]
    items.append({"kind": "question", "type": "single", "question": "q", "why": "w", "back_translation": "b",
                  "source_text": {"question": "q"}, "options": [{"text": "A", "correct": True}]})
    items.append({"kind": "scenario", "situation": "s", "prompts": ["p"],
                  "injects": [{"offset": "+00:15", "text": "t", "decision": "d"}]})
    items.append({"kind": "toolbox", "opening_question": "q", "story": "s", "warning_signs": ["a", "b"],
                  "one_change": "c", "crew_question": "q", "duration": "5 min", "cites": ["FND-0001"]})
    items.append({"kind": "script", "title": "t", "channel": "pa", "cites": ["FND-0001"],
                  "segments": [{"visual": "v", "narration": "n", "seconds": 30, "on_screen": "o"}]})
    items.append({"kind": "card", "title": "t", "what_happened": "w", "warning_signs": ["a"], "good_looks_like": "g",
                  "did_you_know": ["x"], "what_you_can_do": ["y"], "cites": ["FND-0001"]})
    assert validate(pack, SCHEMA) == []
    items[-2]["segments"][0]["seconds"] = 601
    items[-2]["segments"][0]["narration"] = ""
    msg = " ".join(validate(pack, SCHEMA))
    assert "at most 600" in msg and "at least 1 characters" in msg
    items[-4]["injects"][0]["offset"] = "15 min"
    assert "offset" in " ".join(validate(pack, SCHEMA))


def test_unknown_kind_and_discriminator_message():
    pack = copy.deepcopy(_load("all-kinds.json"))
    pack["sections"][0]["items"].append({"kind": "mystery"})
    assert "matches none of the" in " ".join(validate(pack, SCHEMA))


def test_schema_covers_kinds():
    defs = SCHEMA["$defs"]
    by_kind = {d["properties"]["kind"]["const"]: d for n, d in defs.items()
               if n.startswith("item_") and "kind" in d.get("properties", {})}
    for kind, spec in KINDS.items():
        assert kind in by_kind, f"{kind} has no $defs entry"
        d = by_kind[kind]
        for f in spec["req"]:
            assert f in d["properties"] and f in d["required"], f"{kind}.{f}"
        for f in spec["opt"]:
            assert f in d["properties"], f"{kind}.{f}"
        if spec.get("cite"):
            assert "cites" in d["required"], kind
    for new in ("toolbox", "script"):
        assert new in by_kind
    assert {r["$ref"].split("/")[-1] for r in defs["item"]["anyOf"]} == {f"item_{k}" for k in by_kind}


def test_validator_keywords_closed():
    for f in sorted(REFS.glob("*.schema.json")):
        assert unsupported_keywords(json.loads(f.read_text(encoding="utf-8"))) == [], f.name
    assert unsupported_keywords({"properties": {"if": {"type": "string"}}, "allOf": []}) == ["$: allOf"]


def test_bool_not_integer():
    assert validate(True, {"type": "integer"}) and validate(True, {"type": "number"})
    assert validate(True, {"type": ["integer", "string"]})
    assert validate(1, {"type": "integer"}) == [] and validate(2.5, {"type": "number"}) == []
    assert validate(True, {"minimum": 0}) == []          # a bool is not compared as a number
    assert validate(True, {"type": "boolean"}) == []


def test_unknown_type_message():
    assert validate(1, {"type": "int"}) == ["$: unknown type 'int' in the schema"]
    assert "unknown type" in validate(1, {"type": ["string", "nope"]})[0]


def test_new_keywords():
    sch = {"$defs": {"n": {"type": "integer", "minimum": 2, "maximum": 4}},
           "type": "object", "properties": {"a": {"$ref": "#/$defs/n"},
                                            "l": {"type": "array", "minItems": 2},
                                            "s": {"type": "string", "minLength": 3},
                                            "x": {"anyOf": [{"type": "string"}, {"type": "integer"}]}}}
    assert validate({"a": 3, "l": [1, 2], "s": "abc", "x": 1}, sch) == []
    msg = " ".join(validate({"a": 1, "l": [1], "s": "ab", "x": None}, sch))
    assert "at least 2" in msg and "needs at least 2" in msg and "at least 3 characters" in msg and "none of the 2" in msg
    assert "at most 4" in validate({"a": 5}, sch)[0]
    assert "unresolved $ref" in validate({}, {"$ref": "#/nowhere"})[0]
    assert "unresolved $ref" in validate({"a": 1}, {"properties": {"a": {"$ref": "#/$defs/zzz"}}})[0]
    cond = {"if": {"required": ["t"], "properties": {"t": {"const": "short"}}},
            "then": {"required": ["o"]}}
    assert validate({"t": "short"}, cond) == ["$: missing o"]
    assert validate({"t": "long"}, cond) == [] and validate({}, cond) == []
    assert validate({"t": "short", "o": 1}, cond) == []
    one = {"anyOf": [{"$ref": "#/$defs/p"}, {"$ref": "#/$defs/q"}],
           "$defs": {"p": {"type": "object", "required": ["k", "u"], "properties": {"k": {"const": "p"}}},
                     "q": {"type": "object", "properties": {"k": {"const": "q"}}}}}
    assert validate({"k": "p"}, one) == ["$: missing u"]       # the branch its discriminator picks reports
    assert validate({"k": "q"}, one) == []


def test_produces_pack_pattern():
    sk = json.loads((REFS / "skill.schema.json").read_text(encoding="utf-8"))
    pat = sk["properties"]["produces"]["properties"]["pack"]
    assert "pattern" in pat and "comma" in pat["description"]
    from pmlc_lib.contracts import load_manifests
    for name, m in load_manifests().items():
        assert m["produces"]["pack"] is None or "," not in m["produces"]["pack"], name
