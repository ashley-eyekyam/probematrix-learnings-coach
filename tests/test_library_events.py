"""Library events from the files an organisation fills in (spec §8.1, Ruling P6-11): site assessments, verification
readings and adoption responses become events on `library publish`.

Synthetic data only (owner scope change): invented sites, roles and answers; no Hazira data."""
import json
import shutil
from pathlib import Path

import pytest

from test_library import reg, pub, lines, snapshot_bytes, wss  # noqa: F401,F811  (wss is a fixture)
from pmlc_lib.library import events as lib_events

SITE = "Kestrel Works"                     # invented


def outputs(ws) -> Path:
    from pmlc_lib.workspace import outputs_dir
    out = outputs_dir(ws)
    out.mkdir(exist_ok=True)
    return out


@pytest.fixture
def ws(wss, tmp_path):  # noqa: F811                    # a private copy of run A, so each test starts with an empty outputs folder
    dest = tmp_path / "run" / "workspace"
    shutil.copytree(wss["A"], dest)
    return dest


def cihh(ws, rows):
    (outputs(ws) / "cihh-events.jsonl").write_text(
        "".join(json.dumps(dict(r, source="organisation"), sort_keys=True) + "\n" for r in rows), encoding="utf-8")


def verif(ws, rows):
    (outputs(ws) / "verification.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")


def adopt(ws, rows):
    head = "lr_id,title,response,reason,owning_role,target_window\r\n"
    (outputs(ws) / "adoption.csv").write_text(head + "".join(",".join(r) + "\r\n" for r in rows), encoding="utf-8")


def org_events(lib):
    return [e for e in lines(lib, "events.jsonl") if e.get("source") == "organisation"]


def test_events_from_cihh(ws, tmp_path):
    cihh(ws, [{"type": "site_assessment", "lr_id": "LR-01", "site": SITE, "answer": "partly",
               "site_response": f"{SITE} tests some restarts"},
              {"type": "site_assessment", "lr_id": "LR-02", "site": "Harrowgate Yard", "answer": "absent",
               "site_response": ""}])
    lib = tmp_path / "lib"
    out = pub(ws, reg(tmp_path), lib).stdout
    assert "2 site assessments" in out
    ev = org_events(lib)
    assert [e["type"] for e in ev] == ["site_assessment"] * 2
    a, b = ev
    assert a["data"]["site"] == "S01" and b["data"]["site"] == "S02" and a["data"]["answer"] == "partly"
    assert a["data"]["site_response"] == "S01 tests some restarts"          # the site name is coded in free text too
    assert "site_response" not in b["data"]
    assert a["ll_id"] == "LL-000001" and b["ll_id"] == "LL-000002" and a["source"] == "organisation"
    assert a["incident_key"] == lines(lib, "incidents.jsonl")[0]["incident_key"]
    assert SITE not in (lib / "events.jsonl").read_text(encoding="utf-8")


def test_events_from_verification(ws, tmp_path):
    verif(ws, [{"lr_id": "LR-01", "check_date": "2026-05-14", "level": "applied",
                "evidence": "Test records seen on 6 of 6 restarts", "assessed_by_role": "Maintenance supervisor"},
               {"lr_id": "LR-03", "check_date": None, "level": "understood", "evidence": None, "assessed_by_role": None}])
    lib = tmp_path / "lib"
    out = pub(ws, reg(tmp_path), lib).stdout
    assert "2 verification readings" in out
    v1, v2 = org_events(lib)
    assert v1["type"] == "verification" and v1["month"] == "2026-05" and v1["data"]["level"] == "applied"
    assert "check_date" not in v1["data"] and "2026-05-14" not in (lib / "events.jsonl").read_text(encoding="utf-8")
    assert v2["month"] == lines(lib, "incidents.jsonl")[0]["published"]       # no date: the publish month
    assert v2["data"] == {"lr_id": "LR-03", "level": "understood"}


def test_events_from_adoption(ws, tmp_path):
    adopt(ws, [["LR-01", "Return to service", "accepted", "", "Maintenance manager", "90 days"],
               ["LR-02", "Spares", "", "", "", ""],
               ["LR-03", "Gas alarm", "modified", "Shutdown phased in", "", ""]])
    lib = tmp_path / "lib"
    out = pub(ws, reg(tmp_path), lib).stdout
    assert "2 adoption responses" in out
    a, c = org_events(lib)
    assert a["type"] == c["type"] == "status"
    assert a["data"] == {"lr_id": "LR-01", "adoption": "accepted", "owning_role": "Maintenance manager",
                         "target_window": "90 days"}
    assert c["data"]["adoption"] == "modified" and c["data"]["reason"] == "Shutdown phased in"
    # a blank response (LR-02) records nothing
    assert all(e["ll_id"] != "LL-000002" for e in org_events(lib))


def test_events_dedupe(ws, tmp_path):
    cihh(ws, [{"type": "site_assessment", "lr_id": "LR-01", "site": SITE, "answer": "present", "site_response": ""}])
    verif(ws, [{"lr_id": "LR-01", "check_date": "2026-05-14", "level": "applied", "evidence": "x",
                "assessed_by_role": "Auditor"}])
    adopt(ws, [["LR-01", "t", "accepted", "", "", ""]])
    lib = tmp_path / "lib"
    pub(ws, reg(tmp_path), lib)
    before = snapshot_bytes(lib)
    assert len(org_events(lib)) == 3
    out = pub(ws, reg(tmp_path), lib).stdout
    assert "nothing to append" in out and snapshot_bytes(lib) == before
    # a changed answer is a new event; changing it back is one more
    for ans in ("absent", "present"):
        cihh(ws, [{"type": "site_assessment", "lr_id": "LR-01", "site": SITE, "answer": ans, "site_response": ""}])
        pub(ws, reg(tmp_path), lib)
    assert [e["data"]["answer"] for e in org_events(lib) if e["type"] == "site_assessment"] == \
        ["present", "absent", "present"]
    assert len({e["event_hash"] for e in lines(lib, "events.jsonl")}) == len(lines(lib, "events.jsonl"))


def test_events_blank_verification_template_records_nothing(ws, tmp_path):
    verif(ws, [{"lr_id": f"LR-0{i}", "check_date": None, "level": None, "evidence": None, "assessed_by_role": None}
               for i in (1, 2, 3)])
    lib = tmp_path / "lib"
    pub(ws, reg(tmp_path), lib)
    assert org_events(lib) == []


def test_events_same_key_readings_publish_twice(ws, tmp_path):
    rows = [{"lr_id": "LR-01", "check_date": "2026-05-14", "level": "applied", "evidence": e, "assessed_by_role": "A"}
            for e in ("first look", "second look")]
    verif(ws, rows)
    lib = tmp_path / "lib"
    pub(ws, reg(tmp_path), lib)
    before = snapshot_bytes(lib)
    assert len(org_events(lib)) == 1
    out = pub(ws, reg(tmp_path), lib).stdout
    assert "nothing to append" in out and snapshot_bytes(lib) == before


def test_events_undated_reading_not_repeated_in_a_later_month(ws, tmp_path):
    verif(ws, [{"lr_id": "LR-01", "check_date": None, "level": "applied", "evidence": "seen", "assessed_by_role": "A"}])
    lib = tmp_path / "lib"
    pub(ws, reg(tmp_path), lib)
    before = snapshot_bytes(lib)
    assert len(org_events(lib)) == 1
    out = pub(ws, reg(tmp_path), lib, env={"SOURCE_DATE_EPOCH": "1793664000"}).stdout
    assert "nothing to append" in out and snapshot_bytes(lib) == before


def test_events_bad_cihh_answer(ws, tmp_path):
    cihh(ws, [{"type": "site_assessment", "lr_id": "LR-01", "site": SITE, "answer": "excellent", "site_response": ""}])
    r = pub(ws, reg(tmp_path), tmp_path / "lib", check=False)
    assert r.returncode == 1 and "cihh-events.jsonl line 1: answer 'excellent'" in r.stderr


def test_events_unknown_lr(ws, tmp_path):
    cihh(ws, [{"type": "site_assessment", "lr_id": "LR-99", "site": SITE, "answer": "present", "site_response": ""},
              {"type": "site_assessment", "lr_id": "LR-01", "site": SITE, "answer": "present", "site_response": ""}])
    r = pub(ws, reg(tmp_path), tmp_path / "lib")
    assert "note: skipped an event for LR-99" in r.stdout and "Traceback" not in r.stderr
    assert [e["data"]["lr_id"] for e in org_events(tmp_path / "lib")] == ["LR-01"]


def test_events_bad_org_file(ws, tmp_path):
    verif(ws, [{"lr_id": "LR-01", "check_date": None, "level": "great", "evidence": None, "assessed_by_role": None}])
    adopt(ws, [["LR-01", "t", "maybe", "", "", ""]])
    lib = tmp_path / "lib"
    r = pub(ws, reg(tmp_path), lib, check=False)
    assert r.returncode == 1 and "Traceback" not in r.stderr and "nothing was written" in r.stderr
    assert "verification.jsonl line 1: level 'great'" in r.stderr and "adoption.csv row 2: response 'maybe'" in r.stderr
    assert not lib.exists()
    # a cut or foreign cihh-events file is refused the same way
    (outputs(ws) / "verification.jsonl").unlink()
    (outputs(ws) / "adoption.csv").unlink()
    (outputs(ws) / "cihh-events.jsonl").write_text('{"type": "site_assess\n[1]\n', encoding="utf-8")
    r = pub(ws, reg(tmp_path), lib, check=False)
    assert r.returncode == 1 and "cihh-events.jsonl line 1: not valid JSON" in r.stderr
    assert "cihh-events.jsonl line 2: not a site assessment" in r.stderr and not lib.exists()


def test_events_do_not_disturb_state_events(ws, tmp_path):
    lib = tmp_path / "lib"
    pub(ws, reg(tmp_path), lib)
    adopt(ws, [["LR-01", "t", "accepted", "", "", ""]])
    pub(ws, reg(tmp_path), lib)

    def drop(d):
        d["entries"] = [e for e in d["entries"] if e["lr_id"] != "LR-01"]
    pub(ws, reg(tmp_path, edit=drop), lib)
    w = [e for e in lines(lib, "events.jsonl") if e["type"] == "withdrawn"]
    assert len(w) == 1 and "after" not in w[0]["data"]            # the adoption event is not a state to follow


def test_event_key():
    e = {"type": "verification", "ll_id": "LL-000001", "month": "2026-05", "data": {"level": "applied"}}
    assert lib_events.event_key(e) == ("verification", "LL-000001", "2026-05", "applied")
