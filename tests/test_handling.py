"""The handling block, forced draft and sign-off (Phase 2, Task 3), on synthetic exports."""
import copy
import json
import subprocess
import sys

import pytest

from test_pmlc import MINI_REG, PMLC, make_export, run
import pmlc  # noqa: E402  (test_pmlc put the engine folder on sys.path)

STATUS = "Learning purposes: not a statutory document"
PACK = {"pack": "test-pack", "schema": 1, "title": "Test pack: synthetic pump fire", "audience": "Testers",
        "status": STATUS, "bottom_line": [{"text": "Test before service.", "cites": ["FND-0002"]}],
        "sections": [{"id": "s1", "heading": "Section one",
                      "items": [{"kind": "para", "text": "Test before service.", "cites": ["FND-0001"]}]}]}


def build(tmp_path, status="completed", edited=None, name="ws"):
    d = tmp_path / f"exp-{name}"
    d.mkdir()
    x = make_export(d, status=status, edited=edited)
    run("ingest", str(x), "--legacy-out", str(tmp_path / name))
    return tmp_path / name


@pytest.fixture()
def okws(tmp_path):
    return build(tmp_path, edited={"FND-0001": "Yes"})


def write(tmp_path, doc, name="pack.json"):
    p = tmp_path / name
    p.write_text(json.dumps(doc), encoding="utf-8")
    return p


def cli(*args):
    return subprocess.run([sys.executable, str(PMLC), *args], capture_output=True, text=True)


def test_forced_draft_reasons_in_progress_and_unedited(tmp_path, okws):
    w = pmlc.load_ws(build(tmp_path, status="in_progress", name="ws2"))
    assert pmlc.forced_draft_reasons(w) == ["the investigation status is in progress",
                                            "no finding is marked as edited by a person"]
    assert pmlc.forced_draft_reasons(pmlc.load_ws(okws)) == []


def test_content_hash_ignores_handling_and_key_order():
    a = {"x": 1, "y": {"b": 2, "a": 3}}
    b = {"y": {"a": 3, "b": 2}, "x": 1, "handling": {"status": "approved"}}
    assert pmlc.content_hash(a) == pmlc.content_hash(b)
    assert pmlc.content_hash(a).startswith("sha256:") and len(pmlc.content_hash(a)) == 71
    assert pmlc.content_hash(a) != pmlc.content_hash({"x": 2, "y": a["y"]})


@pytest.mark.parametrize("block,key", [
    ({"status": "validated"}, "handling.status"),
    ({"classification": "confidential"}, "handling.classification"),
    ({"legal_review": "maybe"}, "handling.legal_review"),
    ({"reviewed_on": "19/10/2026"}, "handling.reviewed_on"),
    ({"retention_review": "2026-13-40"}, "handling.retention_review"),
    ({"privilege_note": "x"}, "handling.privilege_note"),
    ({"content_hash": "sha256:abc"}, "handling.content_hash"),
    ({"distribution": "board"}, "handling.distribution"),
    ({"version": " "}, "handling.version"),
    ({"status": "approved", "reviewer_role": "HSE manager", "reviewed_on": "2026-10-19"}, "handling.content_hash"),
])
def test_check_handling_rejects_bad_values(block, key):
    problems, _ = pmlc.check_handling({"handling": block})
    assert any(p.startswith(key) for p in problems), problems


def test_check_handling_clean_missing_and_non_object():
    assert pmlc.check_handling({"handling": {"status": "draft"}}) == ([], [])
    assert pmlc.check_handling({}) == ([], ["no handling block: rendered as draft (internal)"])
    assert pmlc.check_handling([]) == ([], [])
    assert pmlc.check_handling({"handling": "x"})[0] == ["handling: must be an object"]


def test_pack_without_handling_renders_draft_and_warns(tmp_path, okws):
    p = write(tmp_path, PACK)
    r = cli("check-pack", str(okws), str(p))
    assert r.returncode == 0, r.stderr
    assert [x for x in r.stdout.splitlines() if x.startswith("warning:")] == [
        "warning: no handling block: rendered as draft (internal)"]
    eff = pmlc.effective_handling(PACK, pmlc.load_ws(okws))
    assert eff["effective_status"] == "draft" and eff["classification"] == "internal"
    assert eff["distribution"] == [] and eff["version"] == "1.0"


def test_sign_off_refused_on_forced_draft(tmp_path):
    ws = build(tmp_path, status="in_progress")
    p = write(tmp_path, PACK)
    r = cli("sign-off", str(ws), str(p), "--role", "HSE manager")
    assert r.returncode == 1
    assert "the investigation status is in progress" in r.stderr
    assert "no finding is marked as edited by a person" in r.stderr
    assert "handling" not in json.loads(p.read_text())


def test_sign_off_approved_writes_hash_and_manifest(tmp_path, okws):
    p = write(tmp_path, PACK)
    r = cli("sign-off", str(okws), str(p), "--status", "approved", "--role", "HSE manager", "--date", "2026-10-19",
            "--classification", "restricted", "--distribution", "board", "T2", "--version", "2.0")
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == f"Signed off {p}: approved by HSE manager on 2026-10-19"
    doc = json.loads(p.read_text())
    h = doc["handling"]
    assert h["status"] == "approved" and h["reviewer_role"] == "HSE manager" and h["reviewed_on"] == "2026-10-19"
    assert h["classification"] == "restricted" and h["distribution"] == ["board", "T2"] and h["version"] == "2.0"
    assert h["content_hash"] == pmlc.content_hash(doc)
    m = json.loads((okws / "manifest.json").read_text())
    assert m["sign_offs"]["pack.json"]["status"] == "approved"
    eff = pmlc.effective_handling(doc, pmlc.load_ws(okws))
    assert eff["effective_status"] == "approved" and eff["draft_reasons"] == []
    ok = cli("check-pack", str(okws), str(p))
    assert ok.returncode == 0 and "warning" not in ok.stdout
    assert "pack.json | approved" in cli("status", str(okws)).stdout


def test_sign_off_default_status_is_reviewed(tmp_path, okws):
    p = write(tmp_path, PACK)
    assert cli("sign-off", str(okws), str(p), "--role", "Site HSE lead").returncode == 0
    h = json.loads(p.read_text())["handling"]
    assert h["status"] == "reviewed" and h["reviewed_on"]


def test_edit_after_sign_off_reverts_to_draft(tmp_path, okws):
    p = write(tmp_path, PACK)
    assert cli("sign-off", str(okws), str(p), "--status", "approved", "--role", "HSE manager").returncode == 0
    doc = json.loads(p.read_text())
    doc["sections"][0]["items"][0]["text"] = "Test before service!"  # one character
    p.write_text(json.dumps(doc), encoding="utf-8")
    eff = pmlc.effective_handling(doc, pmlc.load_ws(okws))
    assert eff["effective_status"] == "draft"
    assert "edited since sign-off" in eff["draft_reasons"]
    r = cli("check-pack", str(okws), str(p))
    assert r.returncode == 0
    assert "edited since sign-off: status is draft until signed off again" in r.stdout + r.stderr
    assert "| approved | HSE manager | 2026-10-19 | yes |" in cli("status", str(okws)).stdout


def test_sign_off_refused_when_pack_has_problems(tmp_path, okws):
    bad = copy.deepcopy(PACK)
    bad["sections"][0]["items"][0]["cites"] = ["FND-9999"]
    p = write(tmp_path, bad)
    r = cli("sign-off", str(okws), str(p), "--role", "HSE manager")
    assert r.returncode == 1 and "FND-9999" in r.stderr
    assert "handling" not in json.loads(p.read_text())


def test_sign_off_register_bare_list_refused(tmp_path, okws):
    p = write(tmp_path, [{"lr_id": "LR-01"}], "reg.json")
    r = cli("sign-off", str(okws), str(p), "--role", "HSE manager")
    assert r.returncode == 1
    assert 'wrap the entries as {"entries": [...]} before signing off' in r.stderr


def test_sign_off_register_refused_with_problems_then_signs_when_sound(tmp_path, okws):
    run("classify", str(okws))
    bad = copy.deepcopy(MINI_REG)
    bad["entries"][0]["finding_ids"] = ["FND-9999"]
    p = write(tmp_path, bad, "reg.json")
    r = cli("sign-off", str(okws), str(p), "--role", "HSE manager")
    assert r.returncode == 1 and "FND-9999" in r.stderr
    good = write(tmp_path, copy.deepcopy(MINI_REG), "reg2.json")
    assert cli("check-register", str(okws), str(good)).returncode == 0  # precondition: MINI_REG is sound
    assert cli("sign-off", str(okws), str(good), "--role", "HSE manager").returncode == 0
    reg = json.loads(good.read_text())
    reg["entries"][0]["title"] += "x"
    good.write_text(json.dumps(reg), encoding="utf-8")
    assert "edited since sign-off" in cli("check-register", str(okws), str(good)).stdout


def test_sign_off_rejects_unknown_documents(tmp_path, okws):
    for text in ('{"hello": 1}', "{not json", "[]", '"x"'):
        p = tmp_path / "x.json"
        p.write_text(text, encoding="utf-8")
        assert cli("sign-off", str(okws), str(p), "--role", "R").returncode == 1
    assert cli("sign-off", str(okws), str(tmp_path / "missing.json"), "--role", "R").returncode == 1


def test_sign_off_bad_date_refused(tmp_path, okws):
    p = write(tmp_path, PACK)
    r = cli("sign-off", str(okws), str(p), "--role", "R", "--date", "19/10/2026")
    assert r.returncode == 1 and "handling.reviewed_on" in r.stderr


def test_typed_in_status_without_sign_off_is_draft(okws):
    w = pmlc.load_ws(okws)
    doc = {**PACK, "handling": {"status": "approved"}}
    eff = pmlc.effective_handling(doc, w)
    assert eff["effective_status"] == "draft"
    assert "invalid handling block" in eff["draft_reasons"]
    full = {**PACK, "handling": {"status": "approved", "reviewer_role": "R", "reviewed_on": "2026-10-19"}}
    assert pmlc.effective_handling(full, w)["effective_status"] == "draft"


def test_invalid_handling_values_do_not_pass_through(okws):
    w = pmlc.load_ws(okws)
    eff = pmlc.effective_handling({**PACK, "handling": {"status": "validated", "classification": "confidential"}}, w)
    assert eff["effective_status"] == "draft" and eff["classification"] == "internal"
    assert "invalid handling block" in eff["draft_reasons"]


def test_valid_signed_block_still_approved(tmp_path, okws):
    p = write(tmp_path, PACK)
    assert cli("sign-off", str(okws), str(p), "--status", "approved", "--role", "R").returncode == 0
    eff = pmlc.effective_handling(json.loads(p.read_text()), pmlc.load_ws(okws))
    assert eff["effective_status"] == "approved" and eff["draft_reasons"] == []
