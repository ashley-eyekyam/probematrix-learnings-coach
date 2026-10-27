"""The library foundation (spec §8.1, P6-11): `library publish`, the append-only store and stable LL- IDs.

Synthetic data only (owner scope change): two invented exports A and B built with test_pmlc.make_export, and the
registers in tests/fixtures/library/. No Hazira data is ever published into a library."""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from test_pmlc import PMLC, make_export, run
import pmlc  # noqa: E402
from pmlc_lib.library import store as lib_store

FIX = Path(__file__).resolve().parent / "fixtures" / "library"
LL_RX = re.compile(r"^LL-\d{6}$")
REF_RX = re.compile(r"^INC-[0-9a-f]{10}/(FND|EVD)-")
INCIDENT_KEYS = {"incident_key", "site_code", "month", "taxonomy_version", "taxonomy_fingerprint",
                 "export_fingerprint", "engine_version", "published", "learnings"}
SNAPSHOT_KEYS = {"ll_id", "snapshot_id", "supersedes", "incident_key", "lr_id", "content_hash", "review_status",
                 "learning"}
LEARNING_KEYS = {"title", "lesson", "public_context", "hfacs_level", "org_system", "barrier", "priority",
                 "transferability", "evidence_strength", "urgency", "finding_refs", "evidence_refs", "recommendations"}
EVENT_KEYS = {"event_hash", "type", "ll_id", "incident_key", "month", "source", "data"}


def _setup(root: Path, slug: str, number):
    root.mkdir(parents=True, exist_ok=True)
    summary = [("Incident Number", number)] if number else []
    x = make_export(root, summary=summary, name=f"{slug}.xlsx")
    run("ingest", str(x), "--slug", slug, "--date", "2024-03-20", "--root", str(root))
    ws = root / "pmlc-runs" / f"2024-03-20-{slug}" / "workspace"
    run("classify", str(ws))
    return ws


@pytest.fixture(scope="module")
def wss(tmp_path_factory):
    d = tmp_path_factory.mktemp("lib")
    return {"A": _setup(d / "a", "site-a-pump", "SYN-A-001"), "B": _setup(d / "b", "site-b-pump", "SYN-B-002"),
            "N": _setup(d / "n", "site-n-pump", None)}


def reg(tmp_path, name="register-a.json", edit=None):
    d = json.loads((FIX / name).read_text(encoding="utf-8"))
    if edit:
        edit(d)
    p = tmp_path / f"{name}.{len(list(tmp_path.glob('*.json')))}.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    return p


def pub(ws, register, lib, *extra, env=None, check=True):
    e = {k: v for k, v in os.environ.items() if k != "PMLC_LIBRARY"}
    e.update(env or {})
    args = [sys.executable, str(PMLC), "library", "publish", str(ws), "--register", str(register)]
    if lib is not None:
        args += ["--library", str(lib)]
    r = subprocess.run(args + list(extra), capture_output=True, text=True, env=e)
    if check:
        assert r.returncode == 0, r.stderr + r.stdout
    return r


def lines(lib, name):
    p = Path(lib) / name
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()] if p.is_file() else []


def snapshot_bytes(lib):
    return {p.relative_to(lib).as_posix(): p.read_bytes() for p in sorted(Path(lib).rglob("*")) if p.is_file()}


def test_library_not_set(wss, tmp_path):
    r = pub(wss["A"], reg(tmp_path), None, check=False)
    assert r.returncode == 2 and lib_store.LIBRARY_NOT_SET in r.stderr and "Traceback" not in r.stderr
    assert lib_store.LIBRARY_NOT_SET == "no library folder: pass --library <dir> or set PMLC_LIBRARY"


def test_env_sets_the_library(wss, tmp_path):
    lib = tmp_path / "envlib"
    pub(wss["A"], reg(tmp_path), None, env={"PMLC_LIBRARY": str(lib)})
    assert (lib / "library.json").is_file()


def test_not_a_library(wss, tmp_path):
    lib = tmp_path / "busy"
    lib.mkdir()
    (lib / "notes.txt").write_text("x", encoding="utf-8")
    r = pub(wss["A"], reg(tmp_path), lib, check=False)
    assert r.returncode == 2 and "Traceback" not in r.stderr
    assert len(r.stderr.strip().splitlines()) == 1 and "is not a library" in r.stderr
    assert sorted(p.name for p in lib.iterdir()) == ["notes.txt"]
    (lib / "library.json").write_text('{"kind": "something-else"}', encoding="utf-8")
    r = pub(wss["A"], reg(tmp_path), lib, check=False)
    assert r.returncode == 2 and "is not a library" in r.stderr
    f = tmp_path / "plain-file"
    f.write_text("x", encoding="utf-8")
    r = pub(wss["A"], reg(tmp_path), f, check=False)
    assert r.returncode == 2 and "is not a library" in r.stderr


def test_first_publish_layout(wss, tmp_path):
    lib = tmp_path / "lib"
    out = pub(wss["A"], reg(tmp_path), lib).stdout
    assert "3 new" in out
    assert json.loads((lib / "library.json").read_text(encoding="utf-8")) == {"kind": "pmlc-library", "version": 1}
    for name in ("learnings.jsonl", "events.jsonl", "incidents.jsonl"):
        assert (lib / name).is_file(), name
    inc = lines(lib, "incidents.jsonl")
    assert len(inc) == 1 and set(inc[0]) == INCIDENT_KEYS
    i = inc[0]
    assert re.fullmatch(r"INC-[0-9a-f]{10}", i["incident_key"])
    assert i["incident_key"] == "INC-" + hashlib.sha256(b"SYN-A-001").hexdigest()[:10]
    assert i["month"] == "2024-03" and re.fullmatch(r"\d{4}-\d{2}", i["published"])
    assert i["engine_version"] == pmlc.__version__
    manifest = json.loads((wss["A"] / "manifest.json").read_text(encoding="utf-8"))
    assert i["export_fingerprint"] == manifest["export"]["sha256"]
    snaps = lines(lib, "learnings.jsonl")
    assert [s["lr_id"] for s in snaps] == ["LR-01", "LR-02", "LR-03"]
    assert [s["ll_id"] for s in snaps] == ["LL-000001", "LL-000002", "LL-000003"] == i["learnings"]
    for s in snaps:
        assert set(s) == SNAPSHOT_KEYS and LL_RX.match(s["ll_id"])
        assert s["snapshot_id"] == f"{s['ll_id']}#1" and s["supersedes"] is None
        assert s["incident_key"] == i["incident_key"] and s["review_status"] == "draft"
        assert set(s["learning"]) <= LEARNING_KEYS and None not in s["learning"].values()
        canon = json.dumps(s["learning"], sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        assert s["content_hash"] == hashlib.sha256(canon.encode("utf-8")).hexdigest()
    one = snaps[0]["learning"]
    assert set(one) == LEARNING_KEYS
    assert one["recommendations"] == [
        {"id": "LL-000001/R1", "change": "Interlock pressurisation on a signed test record", "hoc_tier": "engineering",
         "indicator": "Share of restarts with a test record"},
        {"id": "LL-000001/R2", "change": "Add the leak test to the return-to-service checklist",
         "hoc_tier": "administrative"}]
    assert lines(lib, "events.jsonl") == []
    ctx = lines(lib, "private/contexts.jsonl")
    assert [(c["ll_id"], c["snapshot_id"]) for c in ctx] == [("LL-000001", "LL-000001#1"), ("LL-000002", "LL-000002#1")]
    # every line is canonical JSON plus a line end
    for name in ("learnings.jsonl", "incidents.jsonl", "private/contexts.jsonl"):
        for raw in (lib / name).read_text(encoding="utf-8").splitlines(keepends=True):
            assert raw.endswith("\n")
            assert raw[:-1] == json.dumps(json.loads(raw), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def test_ids_stable(wss, tmp_path):
    lib = tmp_path / "lib"
    r = reg(tmp_path)
    pub(wss["A"], r, lib)
    before = snapshot_bytes(lib)
    out = pub(wss["A"], r, lib).stdout
    assert snapshot_bytes(lib) == before
    assert "nothing to append" in out


def test_republish_supersedes(wss, tmp_path):
    lib = tmp_path / "lib"
    pub(wss["A"], reg(tmp_path), lib)

    def edit(d):
        d["entries"][1]["lesson"] = "If spares arrive without a specification, the wrong part can be fitted."
    pub(wss["A"], reg(tmp_path, edit=edit), lib)
    snaps = lines(lib, "learnings.jsonl")
    assert len(snaps) == 4
    new = snaps[-1]
    assert (new["ll_id"], new["lr_id"], new["snapshot_id"], new["supersedes"]) == (
        "LL-000002", "LR-02", "LL-000002#2", "LL-000002#1")
    assert new["content_hash"] != snaps[1]["content_hash"]
    assert len(lines(lib, "incidents.jsonl")) == 1      # the incident line did not change
    assert lines(lib, "private/contexts.jsonl")[-1]["snapshot_id"] == "LL-000002#2"


def test_republish_withdrawn(wss, tmp_path):
    lib = tmp_path / "lib"
    pub(wss["A"], reg(tmp_path), lib)

    def drop(d):
        d["entries"] = [e for e in d["entries"] if e["lr_id"] != "LR-03"]
    r = reg(tmp_path, edit=drop)
    out = pub(wss["A"], r, lib).stdout
    assert "1 withdrawn" in out
    ev = lines(lib, "events.jsonl")
    assert len(ev) == 1 and set(ev[0]) == EVENT_KEYS
    e = ev[0]
    assert (e["type"], e["ll_id"], e["source"]) == ("withdrawn", "LL-000003", "engine")
    assert e["data"] == {"lr_id": "LR-03", "snapshot_id": "LL-000003#1"}
    body = {k: v for k, v in e.items() if k != "event_hash"}
    canon = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    assert e["event_hash"] == hashlib.sha256(canon.encode("utf-8")).hexdigest()
    inc = lines(lib, "incidents.jsonl")
    assert len(inc) == 2 and inc[-1]["learnings"] == ["LL-000001", "LL-000002"]
    before = snapshot_bytes(lib)
    pub(wss["A"], r, lib)                     # withdrawn once only
    assert snapshot_bytes(lib) == before
    out = pub(wss["A"], reg(tmp_path), lib).stdout   # LR-03 back: reinstated with its old ID, no new snapshot
    ev = lines(lib, "events.jsonl")
    assert (ev[-1]["type"], ev[-1]["ll_id"], ev[-1]["data"]["status"]) == ("status", "LL-000003", "reinstated")
    assert "1 reinstated" in out and len(lines(lib, "learnings.jsonl")) == 3


def test_two_incidents(wss, tmp_path):
    lib = tmp_path / "lib"
    pub(wss["A"], reg(tmp_path), lib)
    pub(wss["B"], reg(tmp_path, "register-b.json"), lib)
    inc = lines(lib, "incidents.jsonl")
    assert len({i["incident_key"] for i in inc}) == 2
    snaps = lines(lib, "learnings.jsonl")
    assert [s["ll_id"] for s in snaps] == [f"LL-{n:06d}" for n in range(1, 6)]
    assert [(s["incident_key"] == inc[1]["incident_key"], s["lr_id"]) for s in snaps[3:]] == [
        (True, "LR-01"), (True, "LR-02")]
    # A again after B: A's LR-01 keeps LL-000001 (looked up, never recomputed)
    pub(wss["A"], reg(tmp_path), lib)
    assert len(lines(lib, "learnings.jsonl")) == 5
    assert pmlc.allocate(pmlc.open_library(lib), inc[0]["incident_key"], "LR-01") == "LL-000001"
    assert pmlc.allocate(pmlc.open_library(lib), inc[0]["incident_key"], "LR-09") == "LL-000006"


def test_incident_key_falls_back_to_the_slug(wss, tmp_path):
    lib = tmp_path / "lib"
    pub(wss["N"], reg(tmp_path), lib)
    key = lines(lib, "incidents.jsonl")[0]["incident_key"]
    assert key == "INC-" + hashlib.sha256(b"2024-03-20-site-n-pump").hexdigest()[:10]
    w = pmlc.load_ws(wss["A"])
    assert pmlc.incident_key(w) == "INC-" + hashlib.sha256(b"SYN-A-001").hexdigest()[:10]


def test_refs_incident_qualified(wss, tmp_path):
    lib = tmp_path / "lib"
    pub(wss["A"], reg(tmp_path), lib)
    refs = [r for s in lines(lib, "learnings.jsonl") for k in ("finding_refs", "evidence_refs")
            for r in s["learning"].get(k, [])]
    assert len(refs) == 8 and all(REF_RX.match(r) for r in refs)
    first = lines(lib, "learnings.jsonl")[0]
    assert first["learning"]["finding_refs"] == [f"{first['incident_key']}/FND-0001",
                                                 f"{first['incident_key']}/FND-0002"]


def test_taxonomy_fingerprint_recorded(wss, tmp_path):
    lib = tmp_path / "lib"
    pub(wss["A"], reg(tmp_path), lib)
    c = json.loads((wss["A"] / "clusters.json").read_text(encoding="utf-8"))
    i = lines(lib, "incidents.jsonl")[0]
    assert i["taxonomy_fingerprint"] == c["taxonomy_fingerprint"]
    assert i["taxonomy_version"] == c["taxonomy_version"]


def test_publish_migrates_v03_register(wss, tmp_path):
    lib = tmp_path / "lib"
    out = pub(wss["A"], FIX / "register-v03.json", lib).stdout
    assert "note: the register has no context, hfacs_level, org_system" in out     # review r0 m4
    snaps = lines(lib, "learnings.jsonl")
    assert [s["lr_id"] for s in snaps] == ["LR-01", "LR-02"]
    one, two = (s["learning"] for s in snaps)
    assert set(one) == {"title", "lesson", "finding_refs", "recommendations"}
    assert one["recommendations"] == [{"id": "LL-000001/R1", "change": "Interlock pressurisation on a signed test record",
                                       "hoc_tier": "Engineering control: interlock"}]
    assert set(two) == {"title", "lesson", "finding_refs"}
    assert all(s["review_status"] == "draft" for s in snaps)
    assert lines(lib, "private/contexts.jsonl") == []


@pytest.mark.parametrize("damage", ["truncated", "duplicate"])
def test_publish_refuses_damaged_library(wss, tmp_path, damage):
    lib = tmp_path / "lib"
    pub(wss["A"], reg(tmp_path), lib)
    pub(wss["B"], reg(tmp_path, "register-b.json"), lib)
    f = lib / "learnings.jsonl"
    raw = f.read_bytes()
    if damage == "truncated":
        f.write_bytes(raw[:-15])
        words = "learnings.jsonl"
    else:   # B's LR-01 claims A's LL-000001
        rows = raw.decode("utf-8").splitlines()
        b = json.loads(rows[3])
        b["ll_id"], b["snapshot_id"] = "LL-000001", "LL-000001#9"
        rows[3] = json.dumps(b, sort_keys=True, separators=(",", ":"))
        f.write_text("\n".join(rows) + "\n", encoding="utf-8")
        words = "LL-000001"
    before = snapshot_bytes(lib)

    def edit(d):
        d["entries"][0]["lesson"] = "A changed lesson that would append a snapshot."
    r = pub(wss["A"], reg(tmp_path, edit=edit), lib, check=False)
    assert r.returncode == 1 and "Traceback" not in r.stderr
    assert words in r.stderr and "nothing was written" in r.stderr
    assert snapshot_bytes(lib) == before


def test_validate_reports_bad_lines(tmp_path):
    lib = tmp_path / "lib"
    lib.mkdir()
    (lib / "library.json").write_text('{"kind": "pmlc-library", "version": 1}', encoding="utf-8")
    (lib / "events.jsonl").write_text('not json\n{"type": "withdrawn"}\n', encoding="utf-8")
    (lib / "incidents.jsonl").write_text('[1]\n', encoding="utf-8")
    probs = pmlc.open_library(lib).validate()
    assert any("events.jsonl line 1" in p and "not valid JSON" in p for p in probs)
    assert any("events.jsonl line 2" in p and "event_hash" in p for p in probs)
    assert any("incidents.jsonl line 1" in p for p in probs)


def test_dry_run_writes_nothing(wss, tmp_path):
    lib = tmp_path / "lib"
    out = pub(wss["A"], reg(tmp_path), lib, "--dry-run").stdout
    assert not lib.exists()
    assert "dry run" in out and "learnings.jsonl: 3" in out and "LL-000001#1" in out
    pub(wss["A"], reg(tmp_path), lib)
    before = snapshot_bytes(lib)

    def drop(d):
        d["entries"] = d["entries"][:2]
    out = pub(wss["A"], reg(tmp_path, edit=drop), lib, "--dry-run").stdout
    assert "withdrawn LL-000003" in out and snapshot_bytes(lib) == before


def test_bad_register_refused(wss, tmp_path):
    lib = tmp_path / "lib"
    pack = tmp_path / "pack.json"
    pack.write_text(json.dumps({"schema": "pmlc-pack", "sections": []}), encoding="utf-8")
    for bad in (pack, tmp_path / "missing.json"):
        r = pub(wss["A"], bad, lib, check=False)
        assert r.returncode == 2 and "Traceback" not in r.stderr and "register" in r.stderr
    dup = reg(tmp_path, edit=lambda d: d["entries"].append(dict(d["entries"][0])))
    r = pub(wss["A"], dup, lib, check=False)
    assert r.returncode == 2 and "LR-01" in r.stderr and "twice" in r.stderr
    assert not lib.exists()


def test_snapshot_function_shape():
    e = {"lr_id": "LR-01", "title": "T", "lesson": "L", "priority": 1, "urgency": "", "barrier": None,
         "finding_ids": ["FND-0001"], "evidence_ids": [], "recommendations": [{"change": "C", "indicator": "I"}]}
    s = pmlc.snapshot(e, "INC-0123456789", "LL-000004", 2, "LL-000004#1")
    assert s["snapshot_id"] == "LL-000004#2" and s["supersedes"] == "LL-000004#1"
    assert s["learning"] == {"title": "T", "lesson": "L", "priority": 1,
                             "finding_refs": ["INC-0123456789/FND-0001"],
                             "recommendations": [{"id": "LL-000004/R1", "change": "C", "indicator": "I"}]}


def test_status_change_is_an_event(wss, tmp_path, monkeypatch):
    """A register whose effective review status changes gets a status event, not a new snapshot."""
    from pmlc_lib.library import publish as lib_publish
    lib = tmp_path / "lib"
    r = reg(tmp_path)
    pub(wss["A"], r, lib)
    monkeypatch.setattr(lib_publish, "_publish_status", lambda doc, w, src, ws: "approved")
    a = pmlc.build_parser().parse_args(["library", "publish", str(wss["A"]), "--register", str(r),
                                        "--library", str(lib)])
    a.fn(a)
    ev = lines(lib, "events.jsonl")
    assert [(e["type"], e["data"]) for e in ev] == [
        ("status", {"review_status": "approved", "snapshot_id": f"LL-00000{n}#1"}) for n in (1, 2, 3)]
    before = snapshot_bytes(lib)
    a.fn(a)                                   # recorded once: the same status again appends nothing
    assert snapshot_bytes(lib) == before
    assert len(lines(lib, "learnings.jsonl")) == 3


def test_artefacts_entry_unplanned():
    art = json.loads((Path(pmlc.HERE).parent / "references" / "artefacts.json").read_text(encoding="utf-8"))
    assert art["library"] == {"file": "$PMLC_LIBRARY", "producer": "engine:library", "org_filled": False}


def test_copy_of_library_keeps_working(wss, tmp_path):
    """A moved library (copied folder) is still a library and its IDs carry on."""
    lib = tmp_path / "lib"
    pub(wss["A"], reg(tmp_path), lib)
    moved = tmp_path / "moved"
    shutil.copytree(lib, moved)
    pub(wss["B"], reg(tmp_path, "register-b.json"), moved)
    assert lines(moved, "learnings.jsonl")[-1]["ll_id"] == "LL-000005"


def test_withdraw_cycle_keeps_every_event(wss, tmp_path):
    """Review r0 C1: full, drop, full, drop in one month gives withdrawn, reinstated, withdrawn, and the printed
    counts match what was appended."""
    lib = tmp_path / "lib"
    full = reg(tmp_path)

    def drop(d):
        d["entries"] = [e for e in d["entries"] if e["lr_id"] != "LR-03"]
    part = reg(tmp_path, edit=drop)
    pub(wss["A"], full, lib)
    assert "1 withdrawn" in pub(wss["A"], part, lib).stdout
    assert "1 reinstated" in pub(wss["A"], full, lib).stdout
    out = pub(wss["A"], part, lib).stdout
    assert "1 withdrawn" in out and "events.jsonl: 1" in out
    ev = lines(lib, "events.jsonl")
    assert [(e["type"], e["data"].get("status")) for e in ev] == [
        ("withdrawn", None), ("status", "reinstated"), ("withdrawn", None)]
    assert "after" not in ev[0]["data"]
    assert ev[1]["data"]["after"] == ev[0]["event_hash"] and ev[2]["data"]["after"] == ev[1]["event_hash"]
    assert len({e["event_hash"] for e in ev}) == 3
    for e in ev:
        body = {k: v for k, v in e.items() if k != "event_hash"}
        assert e["event_hash"] == hashlib.sha256(lib_store.canonical(body).encode("utf-8")).hexdigest()
    before = snapshot_bytes(lib)
    out = pub(wss["A"], part, lib).stdout     # still withdrawn: nothing more, and nothing counted
    assert snapshot_bytes(lib) == before and "0 withdrawn" in out and "nothing to append" in out


def test_review_status_toggle_keeps_every_event(wss, tmp_path, monkeypatch):
    """Review r0 C1: approved, draft, approved in one month gives three status events per learning."""
    from pmlc_lib.library import publish as lib_publish
    lib = tmp_path / "lib"
    r = reg(tmp_path)
    pub(wss["A"], r, lib)
    a = pmlc.build_parser().parse_args(["library", "publish", str(wss["A"]), "--register", str(r),
                                        "--library", str(lib)])
    for st in ("approved", "draft", "approved"):
        monkeypatch.setattr(lib_publish, "_publish_status", lambda doc, w, src, ws, st=st: st)
        a.fn(a)
    ev = [e for e in lines(lib, "events.jsonl") if e["ll_id"] == "LL-000001"]
    assert [e["data"]["review_status"] for e in ev] == ["approved", "draft", "approved"]
    assert len({e["event_hash"] for e in ev}) == 3


def test_validate_one_learning_two_ids(tmp_path):
    """Review r0 m2: one (incident_key, lr_id) recorded under two LL- IDs is reported."""
    lib = tmp_path / "lib"
    lib.mkdir()
    (lib / "library.json").write_text('{"kind": "pmlc-library", "version": 1}', encoding="utf-8")
    row = {"incident_key": "INC-0000000000", "lr_id": "LR-01", "content_hash": "x", "learning": {}}
    (lib / "learnings.jsonl").write_text(
        "".join(lib_store.canonical(dict(row, ll_id=ll, snapshot_id=f"{ll}#1")) + "\n"
                for ll in ("LL-000001", "LL-000002")), encoding="utf-8")
    probs = pmlc.open_library(lib).validate()
    assert any("INC-0000000000/LR-01 has two LL- IDs (LL-000001 and LL-000002)" in p for p in probs)


def test_incident_key_without_basis_is_a_library_error():
    """Review r0 m3."""
    from pmlc_lib.library.ids import incident_key
    with pytest.raises(lib_store.LibraryError):
        incident_key({"incident": {"fields": {}}, "slug": " "})
