"""The de-identification gate on `library publish` (spec §8.1, Ruling P6-12).

Synthetic data only (owner scope change): every name, site and organisation here is invented. No Hazira data is ever
published into a library."""
import json
import re
from pathlib import Path

import pytest

from test_library import _setup, lines, pub, snapshot_bytes
import pmlc  # noqa: E402
from pmlc_lib.library import deid as lib_deid
from pmlc_lib.library import store as lib_store
from pmlc_lib import privacy

PUBLIC = ("learnings.jsonl", "events.jsonl", "incidents.jsonl")
NAME = "Arlo Penhallow"
SITE_A, SITE_B = "Kestrel Works", "Harrowgate Yard"
CONTEXT = (f"On 24 March 2026 at 14:05 {NAME} restarted the pump at {SITE_A} after Brindlecombe Valves Ltd "
           "replaced the seal.")


def _register(tmp_path: Path, name="reg.json", lesson_extra=""):
    d = {"title": "Synthetic register D (invented content only)", "entries": [
        {"lr_id": "LR-01", "title": f"Restart at {SITE_A} without a test",
         "lesson": f"If a joint at {SITE_A} is disturbed (seen 2026-03-24), test it before service.{lesson_extra}",
         "context": CONTEXT, "finding_ids": ["FND-0001"], "evidence_ids": ["EVD-0001"], "priority": 1,
         "transferability": "other sites",
         "recommendations": [{"what": f"Interlock the restart at {SITE_A} on a test record",
                              "hoc_tier": "engineering", "leading_indicator": "Restarts with a test record"}]},
        {"lr_id": "LR-02", "title": "Spares without a specification",
         "lesson": "If spares are bought without a specification, the wrong part can reach the plant.",
         "finding_ids": ["FND-0003"], "priority": 2}]}
    p = tmp_path / name
    p.write_text(json.dumps(d), encoding="utf-8")
    return p


@pytest.fixture(scope="module")
def dws(tmp_path_factory):
    d = tmp_path_factory.mktemp("libdeid")
    return {"A": _site_ws(d / "a", "site-d-pump", "SYN-D-001", ("Site", SITE_A)),
            "B": _site_ws(d / "b", "site-e-pump", "SYN-E-002", ("Location", SITE_B))}


def _site_ws(root: Path, slug: str, number: str, field):
    from test_pmlc import make_export, run
    root.mkdir(parents=True, exist_ok=True)
    x = make_export(root, summary=[("Incident Number", number), field], name=f"{slug}.xlsx")
    run("ingest", str(x), "--slug", slug, "--date", "2024-03-20", "--root", str(root))
    ws = root / "pmlc-runs" / f"2024-03-20-{slug}" / "workspace"
    run("classify", str(ws))
    return ws


def public_text(lib) -> str:
    return "".join((Path(lib) / n).read_text(encoding="utf-8") for n in PUBLIC if (Path(lib) / n).is_file())


def public_strings(lib):
    def walk(v):
        if isinstance(v, str):
            yield v
        elif isinstance(v, list):
            for x in v:
                yield from walk(x)
        elif isinstance(v, dict):
            for x in v.values():
                yield from walk(x)
    for n in PUBLIC:
        for row in lines(lib, n):
            yield from walk(row)


def test_publish_public_lines_are_deidentified(dws, tmp_path):
    lib = tmp_path / "lib"
    names = tmp_path / "names.txt"
    names.write_text(f"# invented\n{NAME}\n", encoding="utf-8")
    r = pub(dws["A"], _register(tmp_path), lib, "--names", str(names), check=False)
    assert r.returncode == 1 and "Traceback" not in r.stderr
    assert "1 listed name" in r.stderr and "nothing was written" in r.stderr
    assert not lib.exists()
    r = pub(dws["A"], _register(tmp_path), lib, check=False, env={"PMLC_NAMES": str(names)})   # the variable too
    assert r.returncode == 1 and "1 listed name" in r.stderr and not lib.exists()

    out = pub(dws["A"], _register(tmp_path), lib).stdout
    assert "site coded S01" in out
    text = public_text(lib)
    assert "S01" in text and "March 2026" in text and "[organisation]" in text
    assert SITE_A not in text and "Kestrel" not in text and "Brindlecombe" not in text
    assert "14:05" not in text and "24 March" not in text
    snaps = lines(lib, "learnings.jsonl")
    one = snaps[0]["learning"]
    assert one["public_context"] == (f"On March 2026 {NAME} restarted the pump at S01 after [organisation] replaced "
                                     "the seal.")
    assert one["title"] == "Restart at S01 without a test"
    assert one["recommendations"][0] == {"id": "LL-000001/R1", "change": "Interlock the restart at S01 on a test record",
                                         "hoc_tier": "engineering", "indicator": "Restarts with a test record"}
    assert one["finding_refs"][0].endswith("/FND-0001")        # IDs are never masked
    inc = lines(lib, "incidents.jsonl")[0]
    assert inc["site_code"] == "S01" and inc["month"] == "2024-03"
    assert lines(lib, "private/contexts.jsonl")[0]["context"] == CONTEXT
    assert json.loads((lib / "private" / "sites.json").read_text(encoding="utf-8")) == {SITE_A: "S01"}
    # the content hash is of the public learning, as stored
    canon = lib_store.canonical(one)
    import hashlib
    assert snaps[0]["content_hash"] == hashlib.sha256(canon.encode("utf-8")).hexdigest()


def test_publish_month_precision(dws, tmp_path):
    lib = tmp_path / "lib"
    pub(dws["A"], _register(tmp_path, lesson_extra=" Logged 12/03/2026 and March 5, 2026."), lib)
    for s in public_strings(lib):
        assert not privacy.ISO_DATE_RX.search(s), s
        assert not privacy.DMY_TEXT_RX.search(s) and not privacy.MDY_TEXT_RX.search(s), s
        assert not privacy.NUM_DATE_RX.search(s), s
    for i in lines(lib, "incidents.jsonl"):
        assert re.fullmatch(r"\d{4}-\d{2}", i["month"]) and re.fullmatch(r"\d{4}-\d{2}", i["published"])


def test_site_codes_stable(dws, tmp_path):
    lib = tmp_path / "lib"
    pub(dws["A"], _register(tmp_path), lib)
    sites = lib / "private" / "sites.json"
    before = snapshot_bytes(lib)
    out = pub(dws["A"], _register(tmp_path), lib, "--site", SITE_A.lower()).stdout   # same site, any case
    assert "nothing to append" in out and snapshot_bytes(lib) == before
    out = pub(dws["B"], _register(tmp_path), lib).stdout       # the Location field
    assert "site coded S02" in out
    assert json.loads(sites.read_text(encoding="utf-8")) == {SITE_A: "S01", SITE_B: "S02"}
    inc = lines(lib, "incidents.jsonl")
    assert [i["site_code"] for i in inc] == ["S01", "S02"]
    # B's register names site A: a known site is coded wherever it appears
    b = [s for s in lines(lib, "learnings.jsonl") if s["incident_key"] == inc[1]["incident_key"]]
    assert b[0]["learning"]["title"] == "Restart at S01 without a test"
    assert pmlc.site_code(pmlc.open_library(lib), SITE_B) == "S02"
    lb = pmlc.open_library(lib)
    assert pmlc.site_code(lb, "Tern Point") == "S03" and pmlc.site_code(lb, " tern  point ") == "S03"


def test_private_not_referenced(dws, tmp_path):
    lib = tmp_path / "lib"
    pub(dws["A"], _register(tmp_path), lib)
    pub(dws["B"], _register(tmp_path), lib, "--site", "Tern Point")
    keys = json.loads((lib / "private" / "sites.json").read_text(encoding="utf-8"))
    assert set(keys) == {SITE_A, "Tern Point"}
    text = public_text(lib).lower()
    for k in keys:
        assert k.lower() not in text
    assert lines(lib, "incidents.jsonl")[-1]["site_code"] == "S02"


def test_dry_run_reserves_no_site_code(dws, tmp_path):
    lib = tmp_path / "lib"
    out = pub(dws["A"], _register(tmp_path), lib, "--dry-run").stdout
    assert "site coded S01" in out and not lib.exists()
    pub(dws["A"], _register(tmp_path), lib)
    before = snapshot_bytes(lib)
    pub(dws["B"], _register(tmp_path), lib, "--dry-run")
    assert snapshot_bytes(lib) == before


def test_orgs_and_singletons_masked(dws, tmp_path):
    lib = tmp_path / "lib"
    orgs = tmp_path / "orgs.txt"
    orgs.write_text("Quillon Engineering\n", encoding="utf-8")
    reg = _register(tmp_path, lesson_extra=" Quillon Engineering fitted it; PSV-101 lifted.")
    pub(dws["A"], reg, lib, "--orgs", str(orgs))
    text = public_text(lib)
    assert "Quillon" not in text and "PSV-101" not in text and "[equipment tag]" in text


def test_no_site_known(tmp_path):
    """No --site and no Site or Location field: the incident's site_code stays null and nothing is coded."""
    from test_library import FIX
    ws = _setup(tmp_path / "n", "site-n-pump", "SYN-N-009")
    lib = tmp_path / "lib"
    out = pub(ws, FIX / "register-a.json", lib).stdout
    assert "site coded" not in out
    assert lines(lib, "incidents.jsonl")[0]["site_code"] is None
    assert not (lib / "private" / "sites.json").exists()


def test_residual_hit_refuses(monkeypatch, tmp_path):
    """The zero-hit scan runs again on the masked lines: anything masking missed refuses the publish."""
    lib = pmlc.open_library(tmp_path / "lib")
    monkeypatch.setattr(lib_deid.privacy, "share_text", lambda text, ctx: text)
    monkeypatch.setenv("PMLC_ORGS", str(tmp_path / "orgs.txt"))
    (tmp_path / "orgs.txt").write_text("Quillon Engineering\n", encoding="utf-8")
    snap = {"ll_id": "LL-000001", "learning": {"lesson": "Quillon Engineering fitted it."}}
    with pytest.raises(lib_store.LibraryError) as e:
        lib_deid.deidentify([("learnings.jsonl", snap)], {"library": lib, "w": {}, "site": None, "names": None})
    assert e.value.code == 1 and "1 identifying detail" in str(e.value)


def test_deidentify_keeps_ids_and_events(tmp_path):
    lib = pmlc.open_library(tmp_path / "lib")
    ev = {"type": "site_assessment", "ll_id": "LL-000001", "incident_key": "INC-0123456789", "month": "2026-03",
          "source": "organisation", "data": {"site": SITE_A, "snapshot_id": "LL-000001#1", "lr_id": "LR-01",
                                             "site_response": f"Checked at {SITE_A} on 2026-03-24 at 09:30."}}
    w = {"incident": {"fields": {"Site": SITE_A}}}
    out = lib_deid.deidentify([("events.jsonl", ev)], {"library": lib, "w": w, "site": None, "names": None})
    data = out[0][1]["data"]
    assert data == {"site": "S01", "snapshot_id": "LL-000001#1", "lr_id": "LR-01",
                    "site_response": "Checked at S01 on March 2026."}
    assert ev["data"]["site"] == SITE_A                       # the input is not changed
    assert out[0][1]["month"] == "2026-03"


def test_damaged_sites_file_refused(dws, tmp_path):
    lib = tmp_path / "lib"
    pub(dws["A"], _register(tmp_path), lib)
    sites = lib / "private" / "sites.json"
    for bad in ("{not json", '["S01"]', json.dumps({SITE_A: "S01", SITE_B: "S01"}), json.dumps({SITE_A: "X1"})):
        sites.write_text(bad, encoding="utf-8")
        before = snapshot_bytes(lib)
        r = pub(dws["B"], _register(tmp_path), lib, check=False)
        assert r.returncode == 1 and "private/sites.json" in r.stderr and "nothing was written" in r.stderr
        assert snapshot_bytes(lib) == before


def test_blank_site_is_refused(tmp_path):
    lib = pmlc.open_library(tmp_path / "lib")
    with pytest.raises(lib_store.LibraryError):
        pmlc.site_code(lib, "  ")
    assert lib.sites() == {} and not lib.sites_changed
