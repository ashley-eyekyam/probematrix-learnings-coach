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
    assert pmlc.sign_off_entry(m, p)["status"] == "approved"
    eff = pmlc.effective_handling(doc, pmlc.load_ws(okws), src=p, ws=okws)
    assert eff["effective_status"] == "approved" and eff["draft_reasons"] == []
    rec = pmlc.sign_off_entry(m, p)               # the whole block and the resolved path are recorded (X25)
    assert {k: v for k, v in rec.items() if k != "path"} == h and rec["path"] == str(p.resolve())
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
    assert cli("sign-off", str(okws), str(p), "--status", "approved", "--role", "HSE manager",
               "--date", "2026-10-19").returncode == 0
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
    eff = pmlc.effective_handling(json.loads(p.read_text()), pmlc.load_ws(okws), src=p, ws=okws)
    assert eff["effective_status"] == "approved" and eff["draft_reasons"] == []


# ----------------------------------------------------------------------------- rendering (Task 6)

import pmlc_pack as pp  # noqa: E402

RIBBON = '<div class="ribbon" role="note">DRAFT</div>'
AI_STATUS = "Learnings drafted by an AI agent from AI-assisted findings"


def signed(tmp_path, ws, doc, name="pack.json", *extra):
    p = write(tmp_path, doc, name)
    r = cli("sign-off", str(ws), str(p), "--status", "approved", "--role", "HSE manager", "--date", "2026-10-19",
            *extra)
    assert r.returncode == 0, r.stderr
    return json.loads(p.read_text())


def eh_of(tmp_path, ws, doc, name="pack.json"):
    """The effective handling of doc as the file tmp_path/name in workspace ws (what pack computes)."""
    return pmlc.effective_handling(doc, pmlc.load_ws(ws), src=tmp_path / name, ws=ws)


def test_pack_without_handling_renders_ribbon_and_handling_line(okws):
    w = pmlc.load_ws(okws)
    t = pp.render_pack_html(w, copy.deepcopy(PACK), "r", "d")
    assert t.count(RIBBON) == 1
    assert '<p class="handling">Review: draft · Classification: internal · Version 1.0</p>' in t
    md = pp.render_pack_md(copy.deepcopy(PACK), w)
    assert md.startswith(f"# {PACK['title']}\n\n**DRAFT**\n\nReview: draft · Classification: internal · Version 1.0\n\n")


def test_html_ribbon_until_approved(tmp_path, okws):
    w = pmlc.load_ws(okws)
    draft = pp.render_pack_html(w, copy.deepcopy(PACK), "r", "d")
    assert RIBBON in draft
    doc = signed(tmp_path, okws, PACK)
    t = pp.render_pack_html(w, doc, "r", "d", eh=eh_of(tmp_path, okws, doc))
    assert RIBBON not in t and 'class="ribbon"' not in t
    assert "Review: approved by HSE manager on 2026-10-19 · Classification: internal · Version 1.0" in t
    assert "Draft because" not in t
    doc["title"] += "!"                           # edited after sign-off: the ribbon comes back, with the reason
    t = pp.render_pack_html(w, doc, "r", "d", eh=eh_of(tmp_path, okws, doc))
    assert RIBBON in t and "Draft because: edited since sign-off" in t
    assert "Review: draft · Classification" in t   # no reviewer shown for a status that no longer holds


def test_html_draft_reasons_and_status_line(tmp_path):
    w = pmlc.load_ws(build(tmp_path, status="in_progress"))
    t = pp.render_pack_html(w, copy.deepcopy(PACK), "r", "d")
    assert ('<p class="handling">Draft because: the investigation status is in progress; '
            "no finding is marked as edited by a person</p>") in t
    assert f'<p class="status">{STATUS} · {AI_STATUS}</p>' in t


def test_md_handling_and_ai_status(tmp_path, okws):
    w = pmlc.load_ws(build(tmp_path, status="in_progress", name="ws2"))
    md = pp.render_pack_md(copy.deepcopy(PACK), w)
    assert md.startswith(
        f"# {PACK['title']}\n\n**DRAFT**\n\nReview: draft · Classification: internal · Version 1.0\n\n"
        "Draft because: the investigation status is in progress; no finding is marked as edited by a person\n\n"
        f"*{STATUS} · {AI_STATUS}*\n\n**Audience:** Testers")
    doc = signed(tmp_path, okws, PACK)
    md = pp.render_pack_md(doc, pmlc.load_ws(okws), eh=eh_of(tmp_path, okws, doc))
    assert "**DRAFT**" not in md and "Draft because" not in md
    assert f"Review: approved by HSE manager on 2026-10-19 · Classification: internal · Version 1.0\n\n*{STATUS}" in md
    own = dict(copy.deepcopy(PACK), status=f"{STATUS}. {AI_STATUS}.")
    assert md.count(AI_STATUS) == 1 and pp.render_pack_md(own, w).count(AI_STATUS) == 1


def test_dashboard_ribbon_and_handling(tmp_path, okws):
    run("classify", str(okws))
    out = tmp_path / "map.html"
    run("dashboard", str(okws), "--out", str(out))
    t = out.read_text(encoding="utf-8")
    assert RIBBON in t and "Review: draft · Classification: internal · Version 1.0" in t
    assert AI_STATUS in t and "@bottom-center" in t
    reg = signed(tmp_path, okws, copy.deepcopy(MINI_REG), "reg.json")
    rp = write(tmp_path, reg, "reg.json")
    run("dashboard", str(okws), "--register", str(rp), "--out", str(out))
    t = out.read_text(encoding="utf-8")
    assert RIBBON not in t and "Review: approved by HSE manager on 2026-10-19" in t


def test_xlsx_about_handling_rows(tmp_path, okws):
    openpyxl = pytest.importorskip("openpyxl")
    run("classify", str(okws))
    rp = write(tmp_path, copy.deepcopy(MINI_REG), "reg.json")
    out = tmp_path / "reg.xlsx"
    run("register-xlsx", str(rp), "--out", str(out), "--ws", str(okws))
    wb = openpyxl.load_workbook(out)
    about = {r[0]: r[1] for r in wb["About"].iter_rows(values_only=True) if len(r) > 1 and r[1] is not None}
    assert about["Review status"].startswith("draft")
    assert about["Classification"] == "internal" and about["Legal review"] == "not-required"
    assert about["Distribution"] == "not set" and about["Version"] == "1.0" and about["Retention review"] == "not set"
    for s in wb.worksheets:
        assert s.oddHeader.center.text == f"{STATUS} · DRAFT", s.title
    signed(tmp_path, okws, copy.deepcopy(MINI_REG), "reg.json", "--distribution", "board", "T2",
           "--retention-review", "2027-10-19")
    run("register-xlsx", str(rp), "--out", str(out), "--ws", str(okws))
    wb = openpyxl.load_workbook(out)
    about = {r[0]: r[1] for r in wb["About"].iter_rows(values_only=True) if len(r) > 1 and r[1] is not None}
    assert about["Review status"] == "approved by HSE manager on 2026-10-19"
    assert about["Distribution"] == "board, T2" and about["Retention review"] == "2027-10-19"
    assert all(s.oddHeader.center.text == STATUS for s in wb.worksheets)


def test_every_card_has_print_footer(okws):
    w = pmlc.load_ws(okws)
    card = {"kind": "card", "title": "t", "what_happened": "w", "warning_signs": ["s"], "good_looks_like": "g",
            "cites": ["FND-0001"]}
    tp = {"kind": "test_point", "requirement": "r", "sample": "s", "conformity_evidence": "c", "cites": ["EVD-0001"]}
    doc = copy.deepcopy(PACK)
    doc["sections"][0]["items"] += [dict(card), dict(card, title="u"), dict(tp)]
    t = pp.render_pack_html(w, doc, "r", "d")
    assert t.count('class="pfoot"') == 3
    assert t.count(f'<p class="pfoot">{STATUS}</p>') == 3


def test_page_margin_footer_css(okws):
    t = pp.render_pack_html(pmlc.load_ws(okws), copy.deepcopy(PACK), "r", "d")
    assert f'@page{{@bottom-center{{content:"{STATUS} · ProbeMatrix Learnings Coach"}}}}' in t
    assert "@media print{.ribbon{border:2px solid #000;color:#000" in t   # border plus text, not colour alone
    css = (pmlc.DASHBOARD_ASSETS / "pack.css").read_text(encoding="utf-8")
    assert ".pfoot{display:none}" in css and ".pfoot{display:block" in css[css.index("@media print"):]


def test_no_inc_date_global():
    assert not hasattr(pp, "_INC_DATE")


# ----------------------------------------------------------------------------- final review I1: sign-off binding (X25)

def self_hashed(doc, **over):
    """A hand-typed approved block with a self-computed content_hash: what a model could write without sign-off."""
    d = copy.deepcopy(doc)
    d["handling"] = dict({"status": "approved", "reviewer_role": "HSE manager", "reviewed_on": "2026-10-19",
                          "classification": "public", "legal_review": "cleared"}, **over)
    d["handling"]["content_hash"] = pmlc.content_hash(d)
    return d


def test_self_hashed_block_without_sign_off_is_draft(tmp_path, okws):
    p = write(tmp_path, self_hashed(PACK))
    eff = pmlc.effective_handling(json.loads(p.read_text()), pmlc.load_ws(okws), src=p, ws=okws)
    assert eff["effective_status"] == "draft" and "not signed off" in eff["draft_reasons"]
    r = cli("check-pack", str(okws), str(p))
    assert r.returncode == 0
    assert "warning: not signed off in this workspace: status is draft until sign-off records it" in r.stdout
    r = cli("pack", str(okws), str(p), "--share", "public", "--out", str(tmp_path / "o"))
    assert r.returncode == 1 and "review is draft (not signed off)" in r.stderr
    assert not (tmp_path / "o" / "test-pack.public.html").exists()
    r = cli("pack", str(okws), str(p), "--out", str(tmp_path / "o"))
    t = (tmp_path / "o" / "test-pack.html").read_text(encoding="utf-8")
    assert RIBBON in t and "Draft because: not signed off" in t and "approved by" not in t


def test_hand_edited_handling_after_sign_off_is_draft(tmp_path, okws):
    """The hash leaves out the handling block, so raising classification or legal_review by hand must not count."""
    p = write(tmp_path, PACK)
    assert cli("sign-off", str(okws), str(p), "--status", "approved", "--role", "HSE manager").returncode == 0
    doc = json.loads(p.read_text())
    doc["handling"].update(classification="public", legal_review="cleared")
    p.write_text(json.dumps(doc), encoding="utf-8")
    eff = pmlc.effective_handling(doc, pmlc.load_ws(okws), src=p, ws=okws)
    assert eff["effective_status"] == "draft" and "not signed off" in eff["draft_reasons"]
    r = cli("pack", str(okws), str(p), "--share", "public", "--out", str(tmp_path / "o"))
    assert r.returncode == 1


def test_pack_signed_in_one_workspace_is_draft_in_another(tmp_path, okws):
    p = write(tmp_path, PACK)
    assert cli("sign-off", str(okws), str(p), "--status", "approved", "--role", "HSE manager").returncode == 0
    other = build(tmp_path, edited={"FND-0001": "Yes"}, name="wsb")
    q = other / "pack.json"
    q.write_bytes(p.read_bytes())
    doc = json.loads(q.read_text())
    eff = pmlc.effective_handling(doc, pmlc.load_ws(other), src=q, ws=other)
    assert eff["effective_status"] == "draft" and "not signed off" in eff["draft_reasons"]
    moved = tmp_path / "moved.json"                          # the same workspace, but another file
    moved.write_bytes(p.read_bytes())
    eff = pmlc.effective_handling(doc, pmlc.load_ws(okws), src=moved, ws=okws)
    assert eff["effective_status"] == "draft"
    assert pmlc.effective_handling(doc, pmlc.load_ws(okws), src=p, ws=okws)["effective_status"] == "approved"
    eff = pmlc.effective_handling(doc, pmlc.load_ws(okws))     # no workspace given: nothing to check against
    assert eff["effective_status"] == "draft" and "no workspace to check" in eff["draft_reasons"]


def test_register_xlsx_outside_run_layout_without_ws_is_draft(tmp_path, okws):
    openpyxl = pytest.importorskip("openpyxl")
    run("classify", str(okws))
    rp = write(tmp_path, copy.deepcopy(MINI_REG), "reg.json")
    assert cli("sign-off", str(okws), str(rp), "--status", "approved", "--role", "HSE manager").returncode == 0
    loose = tmp_path / "loose"
    loose.mkdir()
    cp = loose / "reg.json"
    cp.write_bytes(rp.read_bytes())
    out = tmp_path / "loose.xlsx"
    run("register-xlsx", str(cp), "--out", str(out))
    wb = openpyxl.load_workbook(out)
    about = {r[0]: r[1] for r in wb["About"].iter_rows(values_only=True) if len(r) > 1 and r[1] is not None}
    assert about["Review status"] == "draft. Draft because: no workspace to check"
    assert all(s.oddHeader.center.text == f"{STATUS} · DRAFT" for s in wb.worksheets)


# ----------------------------------------------------------------------------- final review I2: forced draft (X26)

def _ws_fields(status, edited):
    return {"incident": {"fields": {"Investigation Status": status}},
            "findings": [{"id": "FND-0001", "user_edited": edited}]}


@pytest.mark.parametrize("status,reason", [
    ("draft", "the investigation status is not completed"),
    ("In Progress", "the investigation status is in progress"),
    ("in-progress", "the investigation status is in progress"),
    ("in_progress", "the investigation status is in progress"),
    ("", "the investigation status is not completed"),
    (None, "the investigation status is not completed"),
    ("closed", "the investigation status is not completed"),
])
def test_forced_draft_unless_completed(status, reason):
    assert pmlc.forced_draft_reasons(_ws_fields(status, "Yes")) == [reason]


@pytest.mark.parametrize("status", ["completed", "Completed", " COMPLETED "])
def test_completed_is_not_forced(status):
    assert pmlc.forced_draft_reasons(_ws_fields(status, "Yes")) == []


@pytest.mark.parametrize("edited,forced", [("N", True), ("false", True), ("No", True), ("", True), (None, True),
                                           ("maybe", True), ("Yes", False), ("y", False), ("TRUE", False),
                                           ("1", False), (True, False), (1, False)])
def test_user_edited_counts_only_yes(edited, forced):
    got = pmlc.forced_draft_reasons(_ws_fields("completed", edited))
    assert got == (["no finding is marked as edited by a person"] if forced else [])


def test_sign_off_refused_on_draft_status(tmp_path):
    ws = build(tmp_path, status="draft", edited={"FND-0001": "Yes"}, name="wsd")
    p = write(tmp_path, PACK)
    r = cli("sign-off", str(ws), str(p), "--role", "HSE manager")
    assert r.returncode == 1
    assert r.stderr.strip() == "cannot sign off: the investigation status is not completed"


# ----------------------------------------------------------------------------- final review I4: --role is a role

@pytest.mark.parametrize("role,match", [("Mr John Smith", "Mr John Smith"), ("John Smith", "John Smith"),
                                        ("Shri R. K. Sharma", "Shri R. K. Sharma"), ("Dr. Anand", "Dr. Anand")])
def test_sign_off_refuses_a_name_as_role(tmp_path, okws, role, match):
    p = write(tmp_path, PACK)
    r = cli("sign-off", str(okws), str(p), "--role", role, "--status", "approved")
    assert r.returncode == 1
    assert r.stderr.strip() == f'--role: looks like a personal name ("{match}"); give a role'
    assert "handling" not in json.loads(p.read_text())


def test_sign_off_refuses_a_name_in_distribution(tmp_path, okws):
    p = write(tmp_path, PACK)
    r = cli("sign-off", str(okws), str(p), "--role", "HSE manager", "--distribution", "board", "Jane Placeholder")
    assert r.returncode == 1
    assert r.stderr.strip() == '--distribution: looks like a personal name ("Jane Placeholder"); give a role'


def test_sign_off_role_checks_the_names_file(tmp_path, okws):
    names = tmp_path / "names.txt"
    names.write_text("# fictional\nOfficer Placeholder\n", encoding="utf-8")
    p = write(tmp_path, PACK)
    r = cli("sign-off", str(okws), str(p), "--role", "officer placeholder", "--names", str(names))
    assert r.returncode == 1 and "--role: looks like a personal name" in r.stderr


@pytest.mark.parametrize("role", ["HSE Manager", "Site HSE lead", "Shift Supervisor", "Plant Manager",
                                  "Head of Safety", "Control Room Operator"])
def test_sign_off_accepts_roles(tmp_path, okws, role):
    p = write(tmp_path, PACK)
    r = cli("sign-off", str(okws), str(p), "--role", role, "--distribution", "board", "T2", "site-leadership")
    assert r.returncode == 0, r.stderr


# ---- phase 3, task 18: manifest records keyed by resolved path, bare-name keys still read
def _sub(tmp_path, d, doc=None):
    (tmp_path / d).mkdir(exist_ok=True)
    return write(tmp_path / d, doc or PACK)


def test_old_name_keyed_sign_off_still_honoured(tmp_path, okws):
    p = write(tmp_path, PACK)
    assert cli("sign-off", str(okws), str(p), "--status", "approved", "--role", "HSE manager",
               "--date", "2026-10-19").returncode == 0
    mp = okws / "manifest.json"
    m = json.loads(mp.read_text())
    assert list(m["sign_offs"]) == [str(p.resolve())]            # new records are keyed by the resolved path
    m["sign_offs"] = {"pack.json": m["sign_offs"][str(p.resolve())]}   # an alpha.4 manifest: keyed by bare name
    mp.write_text(json.dumps(m), encoding="utf-8")
    doc = json.loads(p.read_text())
    assert pmlc.effective_handling(doc, pmlc.load_ws(okws), src=p, ws=okws)["effective_status"] == "approved"
    out = cli("status", str(okws)).stdout
    assert "| pack.json | approved | HSE manager | 2026-10-19 | no |" in out
    assert cli("sign-off", str(okws), str(p), "--role", "HSE manager", "--date", "2026-10-20").returncode == 0
    assert list(json.loads(mp.read_text())["sign_offs"]) == [str(p.resolve())]   # the old key is replaced


def test_failed_check_recorded_not_ok(tmp_path, okws):
    bad = dict(PACK, bottom_line=[{"text": "Test before service.", "cites": ["FND-9999"]}])
    p = write(tmp_path, bad)
    r = cli("check-pack", str(okws), str(p))
    assert r.returncode == 1
    rec = pmlc.pack_record(json.loads((okws / "manifest.json").read_text()), p)
    assert rec is not None and rec["ok"] is False and rec["problems"] >= 1 and rec["path"] == str(p.resolve())
    assert "problem(s)" in cli("status", str(okws)).stdout


def test_two_runs_same_pack_name_do_not_collide(tmp_path, okws):
    a = _sub(tmp_path, "run-a")
    b = _sub(tmp_path, "run-b", dict(PACK, title="Test pack: the second run"))
    assert cli("sign-off", str(okws), str(a), "--role", "HSE manager").returncode == 0
    assert cli("check-pack", str(okws), str(a)).returncode == 0
    assert cli("check-pack", str(okws), str(b)).returncode == 0
    m = json.loads((okws / "manifest.json").read_text())
    assert len(m["packs"]) == 2
    assert pmlc.sign_off_entry(m, a)["path"] == str(a.resolve())
    ea = pmlc.effective_handling(json.loads(a.read_text()), pmlc.load_ws(okws), src=a, ws=okws)
    eb = pmlc.effective_handling(json.loads(b.read_text()), pmlc.load_ws(okws), src=b, ws=okws)
    assert ea["effective_status"] == "reviewed"
    assert eb["effective_status"] == "draft"        # signing a did not sign b
    assert cli("sign-off", str(okws), str(b), "--role", "Site HSE lead").returncode == 0
    m = json.loads((okws / "manifest.json").read_text())
    assert pmlc.sign_off_entry(m, a)["reviewer_role"] == "HSE manager"
    assert pmlc.sign_off_entry(m, b)["reviewer_role"] == "Site HSE lead"
