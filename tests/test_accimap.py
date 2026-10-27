"""accimap (Phase 6 Task 5): Rasmussen level placement by rule, gaps, inferred levels, the --map file, the graph item."""
import json

import pytest

import pmlc  # noqa: E402
from test_pmlc import make_export, make_thin_export, run, run_fail

pytest.importorskip("openpyxl")
from pmlc_lib import accimap  # noqa: E402


def _f(i, code, level, sub="Other", roles=(), label=""):
    return {"id": f"FND-{i:04d}", "code": code, "name": code, "level": level, "subcategory": sub,
            "roles": list(roles), "label": label, "rating": 3}


def _w(findings, ents=None):
    return {"findings": findings,
            "clusters": {"findings": {f["id"]: {"F": (ents or {}).get(f["id"], [])} for f in findings}}}


T6 = "Environmental Factors - Technological Environment"
P6 = "Environmental Factors - Physical Environment"


def test_accimap_rules():
    fs = [_f(1, "OIC 2.1", 4), _f(2, "SVI 1.4", 3), _f(3, "PTE 1.1", 2, T6), _f(4, "PPE 1.1", 2, P6),
          _f(5, "PTF 1.1", 2, "Teamwork"), _f(6, "AV 1.1", 1), _f(7, "OIP 1.1", 4), _f(8, "OIP 1.2", 4),
          _f(9, "OIP 1.3", 4), _f(10, "SVI 1.5", 3)]
    ents = {"FND-0007": ["F15"], "FND-0008": ["F14"], "FND-0009": ["F17"], "FND-0010": ["F15", "F14"]}
    d = accimap.place(_w(fs, ents))
    got = {k: (v["level"], v.get("tag")) for k, v in d["placements"].items()}
    assert got == {"FND-0001": (3, None), "FND-0002": (4, None), "FND-0003": (6, None), "FND-0004": (6, None),
                   "FND-0005": (5, None), "FND-0006": (5, None), "FND-0007": (2, None), "FND-0008": (3, None),
                   "FND-0009": (3, "contractor"), "FND-0010": (2, None)}
    assert d["levels"]["3"]["findings"] == ["FND-0001", "FND-0008", "FND-0009"]
    assert sum(len(v["findings"]) for v in d["levels"].values()) == 10


def test_accimap_gaps():
    d = accimap.place(_w([_f(1, "OIC 2.1", 4), _f(2, "AV 1.1", 1)]))
    assert 1 in d["gaps"]
    assert d["levels"]["1"]["findings"] == []
    assert any("Level 1" in n for n in d["notes"])


def test_accimap_inferred():
    d = accimap.place(_w([_f(1, "OIC 2.1", 4), _f(2, "SVI 1.4", 3), _f(3, "AV 1.1", 1)]))
    assert d["placements"]["FND-0001"]["inferred"] is True
    assert d["placements"]["FND-0002"]["inferred"] is False
    assert d["placements"]["FND-0003"]["inferred"] is False
    assert d["levels"]["3"]["inferred"] is True and d["levels"]["4"]["inferred"] is False


def test_accimap_map_adds_government(tmp_path):
    m = tmp_path / "m.json"
    m.write_text(json.dumps({"keywords": {"1": ["ministry"]}}))
    d = accimap.place(_w([_f(1, "OIP 1.1", 4, roles=["Ministry liaison"])]), accimap.accimap_load_map(m))
    assert d["placements"]["FND-0001"]["level"] == 1 and d["placements"]["FND-0001"]["inferred"] is True
    assert 1 not in d["gaps"]


@pytest.mark.parametrize("body", ['{"keywords": {"1": ["("]}}', '{"keywords": {"1": [3]}}', '{"keywords": {"9": ["x"]}}',
                                  '{"entities": {"F14": {"level": "3"}}}', '{"hfacs_levels": {"4": 7}}', '[1]',
                                  'not json'])
def test_accimap_map_override(tmp_path, body):
    m = tmp_path / "m.json"
    m.write_text(body)
    with pytest.raises(SystemExit) as e:
        accimap.accimap_load_map(m)
    assert e.value.code == 2


def test_accimap_bad_map_cli(tmp_path):
    x = make_export(tmp_path)
    d = tmp_path / "ws"
    run("ingest", str(x), "--legacy-out", str(d))
    run("classify", str(d))
    m = tmp_path / "m.json"
    m.write_text('{"keywords": {"1": ["("]}}')
    r = run_fail("accimap", str(d), "--map", str(m))
    assert r.returncode == 2 and "Traceback" not in r.stderr and "does not compile" in r.stderr
    assert len(r.stderr.strip().splitlines()) == 1


def test_accimap_thin_export(tmp_path):
    x = make_thin_export(tmp_path)
    d = tmp_path / "ws"
    run("ingest", str(x), "--legacy-out", str(d))
    out = run("accimap", str(d))                      # no classify at all
    a = json.loads((d / "accimap.json").read_text(encoding="utf-8"))
    assert a["notes"] and "Note:" in out
    run("classify", str(d))
    run("accimap", str(d))
    a = json.loads((d / "accimap.json").read_text(encoding="utf-8"))
    assert any("F14" in n for n in a["notes"])
    assert 1 in a["gaps"] and a["version"] == 1
    assert pmlc.stale_files(d) == []
    first = (d / "accimap.json").read_bytes()
    run("accimap", str(d))
    assert (d / "accimap.json").read_bytes() == first


def test_graph_item_valid(tmp_path):
    x = make_export(tmp_path, causal_rows=True)
    d = tmp_path / "ws"
    run("ingest", str(x), "--legacy-out", str(d))
    run("classify", str(d))
    run("causal", str(d))
    it = json.loads(run("accimap", str(d), "--graph-item"))
    assert it["kind"] == "graph" and [n["id"] for n in it["nodes"] if n["id"].startswith("L") and "-" not in n["id"]] \
        == [f"L{i}" for i in range(1, 7)]
    for i in range(1, 7):
        assert sum(1 for n in it["nodes"] if n["id"].startswith(f"L{i}-")) <= 4
    ids = {n["id"] for n in it["nodes"]}
    assert all(e["from"] in ids and e["to"] in ids for e in it["edges"])
    from pmlc_lib.pack.profiles import BANNERS
    cite = it["cites"][:1]
    pack = {"pack": "causal-map", "schema": 1, "title": "AcciMap check", "audience": "Test readers",
            "status": "Learning purposes: not a statutory document",
            "bottom_line": [{"text": "Levels reached.", "cites": cite}],
            "sections": [{"id": "map", "heading": "Map",
                          "items": [{"kind": "para", "text": BANNERS["accimap-inferred"]}, it]}]}
    p = tmp_path / "p.json"
    p.write_text(json.dumps(pack))
    out = run("check-pack", str(d), str(p))
    assert "problem" not in out.lower() or "0 problem" in out.lower()
    from pmlc_lib.pack.profiles import _check_inferred_banner
    pack["sections"][0]["items"].pop(0)              # without the banner the inferred nodes are refused (rule)
    out = []
    _check_inferred_banner(pack, out)
    assert out and out[0].startswith("inferred-banner")


def test_table_item_cites(tmp_path):
    x = make_export(tmp_path)
    d = tmp_path / "ws"
    run("ingest", str(x), "--legacy-out", str(d))
    run("classify", str(d))
    t = json.loads(run("accimap", str(d), "--table-item", "levels"))
    assert t["kind"] == "table" and len(t["row_cites"]) == len(t["rows"]) > 0
    assert all(c and all(x.startswith("FND-") for x in c) for c in t["row_cites"])
