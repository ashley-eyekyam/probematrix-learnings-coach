"""alert-grade, register-items --lr/--transferable, the one-slide pptx and the P6-4 share gate (plan Phase 6 Task 2;
Rulings P6-3, P6-4; OD6-1)."""
import copy
import json
import subprocess
import sys

import pytest

from test_pmlc import MINI_REG, PMLC, ROOT, run, ws  # noqa: F401  (ws is a module-scoped fixture)
from test_pack import item, pack_with, render_fixture
from test_privacy import _cli, files, share_ws, sign, SPACK, write_doc
import pmlc  # noqa: E402
from pmlc_lib import alert  # noqa: E402
from pmlc_lib.pack import profiles  # noqa: E402
from pmlc_lib.pack.items import register_items  # noqa: E402
from pmlc_lib.render.pptx import pptx_notes_text, pptx_slides_text  # noqa: E402

HAZIRA_REG = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire" / "outputs" / "learnings-register.json"
_REAL_LOAD = profiles.load
REVIEW = profiles.BANNERS["alert-review-copy"]


def entry(lr, priority=1, transferability="industry-wide", strength="corroborated", **over):
    e = {"lr_id": lr, "title": f"Learning {lr}", "lesson": f"Lesson of {lr}", "priority": priority,
         "transferability": transferability, "evidence_strength": strength, "finding_ids": ["FND-0001"],
         "evidence_ids": ["EVD-0001"], "tiers": ["T3"]}
    e.update(over)
    return e


def _reg(tmp_path, entries, name="reg.json"):
    p = tmp_path / name
    p.write_text(json.dumps({"title": "Synthetic register", "entries": entries}), encoding="utf-8")
    return p


def _pmlc(*args):
    return subprocess.run([sys.executable, str(PMLC), *args], capture_output=True, text=True)


# ----------------------------------------------------------------------------- register-items --lr / --transferable

def test_register_items_lr_and_transferable(ws, tmp_path):  # noqa: F811
    reg = _reg(tmp_path, [entry("LR-01"), entry("LR-02", 2, "same site"), entry("LR-05", 3, "other sites"),
                          entry("LR-07", 1, "same site")])
    got = json.loads(run("register-items", str(ws), "--register", str(reg), "--lr", "LR-05", "--lr", "LR-02"))
    assert [it["learning"] for it in got] == ["LR-05", "LR-02"]          # in the order asked for
    assert [it["id"] for it in got] == ["lr-05", "lr-02"]
    assert all(it["kind"] == "learning" and it["cites"] == ["FND-0001", "EVD-0001"] for it in got)
    got = json.loads(run("register-items", str(ws), "--register", str(reg), "--transferable"))
    assert [it["learning"] for it in got] == ["LR-01", "LR-05"]
    got = json.loads(run("register-items", str(ws), "--register", str(reg), "--tier", "T3", "--transferable"))
    assert [it["id"] for it in got] == ["t3-lr-01", "t3-lr-05"]
    hz = json.loads(run("register-items", str(ws), "--register", str(HAZIRA_REG), "--transferable"))
    assert len(hz) == 25
    r = _pmlc("register-items", str(ws), "--register", str(reg))
    assert r.returncode == 2 and r.stdout == ""
    assert r.stderr.strip() == "register-items: give --tier, --lr or --transferable"
    r = _pmlc("register-items", str(ws), "--register", str(reg), "--lr", "LR-99")
    assert r.returncode == 2 and "Traceback" not in r.stderr
    assert r.stderr.strip() == f"register-items: LR-99 is not in the register {reg}"


def test_register_items_tier_alone_unchanged(ws, tmp_path):  # noqa: F811
    reg = tmp_path / "mini.json"
    reg.write_text(json.dumps(MINI_REG), encoding="utf-8")
    got = json.loads(run("register-items", str(ws), "--register", str(reg), "--tier", "T1"))
    assert got == register_items(MINI_REG["entries"], "T1")
    assert [it["id"] for it in got] == ["t1-lr-01"]


# ----------------------------------------------------------------------------- grade (P6-3)

def test_grade_from_urgency():
    es = [entry("LR-01", urgency="notice"), entry("LR-02", urgency="alert"), entry("LR-03", urgency="information")]
    g = alert.grade(es)
    assert g["grade"] == "alert" and g["grade_source"] == "register urgency" and g["suggested"] is None
    assert g["learnings"] == ["LR-01", "LR-02", "LR-03"] and g["notes"] == []
    assert g["grade_source"] in alert.GRADE_SOURCES
    g = alert.grade(es, ["LR-01", "LR-03"])
    assert g["grade"] == "notice" and g["learnings"] == ["LR-01", "LR-03"]
    mixed = alert.grade([entry("LR-01", urgency="information"), entry("LR-02")], ["LR-01", "LR-02"])
    assert mixed["grade"] == "information" and mixed["grade_source"] == "register urgency"
    assert mixed["notes"] == ["no urgency in the register for LR-02"]


def test_grade_suggested():
    g = alert.grade([entry("LR-01", 1, "industry-wide")])
    assert {k: g[k] for k in ("grade", "grade_source")} == {"grade": "alert", "grade_source": "suggested"}
    assert g["suggested"]["grade"] == "alert" and g["suggested"]["by_learning"] == {"LR-01": "alert"}
    assert alert.grade([entry("LR-01", 1, "other sites")])["grade"] == "alert"
    assert alert.grade([entry("LR-01", 1, "same site")])["grade"] == "notice"
    assert alert.grade([entry("LR-02", 2, "industry-wide")], ["LR-02"])["grade"] == "notice"
    assert alert.grade([entry("LR-03", 3, "industry-wide")], ["LR-03"])["grade"] == "information"
    assert alert.suggest_grade(entry("LR-04", None, None)) == "information"
    assert "suggested" not in alert.GRADE_SOURCES                         # never in a pack (OD6-1)
    g = alert.grade([entry("LR-01", 1, "same site"), entry("LR-02", 2), entry("LR-03", 3)], ["LR-03", "LR-02", "LR-01"])
    assert g["grade"] == "notice" and g["suggested"]["by_learning"] == {"LR-01": "notice", "LR-02": "notice",
                                                                         "LR-03": "information"}


def test_default_choice_order():
    es = [entry("LR-01", 1, "same site"), entry("LR-02", 1, "other sites", "direct"),
          entry("LR-03", 1, "industry-wide", "inferred"), entry("LR-04", 1, "industry-wide", "direct"),
          entry("LR-05", 2, "industry-wide"), entry("LR-06", 1, "other sites"), entry("LR-07", 1, "industry-wide")]
    assert alert.default_choice(es) == ["LR-07", "LR-04", "LR-03"]
    assert alert.grade(es)["learnings"] == ["LR-07", "LR-04", "LR-03"]
    assert alert.default_choice(es[:3]) == ["LR-03", "LR-02", "LR-01"]
    assert alert.default_choice([entry("LR-09", 1, "same site"), entry("LR-08", 1, "same site", "inferred"),
                                 entry("LR-10", 1, "same site", None)]) == ["LR-09", "LR-08", "LR-10"]


def test_alert_grade_thin_register(ws, tmp_path):  # noqa: F811
    g = alert.grade([entry("LR-01", 2), entry("LR-02", 3)])
    assert g == {"grade": None, "grade_source": None, "suggested": None, "learnings": [],
                 "notes": ["no priority-1 learning: choose with --lr"]}
    reg = _reg(tmp_path, [entry("LR-01", 2), entry("LR-02", 3)])
    r = _pmlc("alert-grade", str(ws), "--register", str(reg), "--json")
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout)["learnings"] == []
    r = _pmlc("alert-grade", str(ws), "--register", str(reg))
    assert r.returncode == 0 and "no priority-1 learning: choose with --lr" in r.stdout


def test_alert_grade_cli(ws, tmp_path):  # noqa: F811
    reg = _reg(tmp_path, [entry("LR-01"), entry("LR-02", 2, "same site"), entry("LR-03", 1, "same site")])
    r = _pmlc("alert-grade", str(ws), "--register", str(reg), "--json")
    assert r.returncode == 0, r.stderr
    d = json.loads(r.stdout)
    assert d["grade"] == "alert" and d["grade_source"] == "suggested" and d["learnings"] == ["LR-01", "LR-03"]
    assert r.stdout == json.dumps(d, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    r = _pmlc("alert-grade", str(ws), "--register", str(reg), "--lr", "LR-02")
    assert r.returncode == 0, r.stderr
    assert r.stdout.splitlines()[0] == "alert-grade: suggested notice for LR-02 (no urgency in the register)"
    assert 'ask the user; the pack records grade_source "chosen by the user"' in r.stdout
    reg2 = _reg(tmp_path, [entry("LR-01", urgency="notice")], "u.json")
    r = _pmlc("alert-grade", str(ws), "--register", str(reg2))
    assert r.stdout.splitlines()[0] == 'alert-grade: notice for LR-01 (grade_source "register urgency")'
    r = _pmlc("alert-grade", str(ws), "--register", str(reg), "--lr", "LR-09")
    assert r.returncode == 2 and r.stderr.strip() == f"alert-grade: LR-09 is not in the register {reg}"
    r = _pmlc("alert-grade", str(ws), "--register", str(tmp_path / "none.json"))
    assert r.returncode == 2 and "Traceback" not in r.stderr and "none.json" in r.stderr


def test_alert_grade_refuses_pack(ws, tmp_path):  # noqa: F811
    p = tmp_path / "board-brief.json"
    p.write_text(json.dumps(pack_with(item("para"))), encoding="utf-8")
    r = _pmlc("alert-grade", str(ws), "--register", str(p))
    assert r.returncode == 2 and r.stdout == "" and "Traceback" not in r.stderr
    assert r.stderr.strip() == f"alert-grade reads a learnings register, and {p} is not one"
    assert len(r.stderr.strip().splitlines()) == 1


def test_alert_grade_default_register(tmp_path):
    """Without --register, alert-grade reads <outputs>/learnings-register.json; both branches pinned (review m3)."""
    w = tmp_path / "w"
    w.mkdir()
    want = pmlc.outputs_dir(w) / "learnings-register.json"
    r = _pmlc("alert-grade", str(w))
    assert r.returncode == 2 and str(want) in r.stderr and "Traceback" not in r.stderr
    want.parent.mkdir(parents=True, exist_ok=True)
    want.write_text(json.dumps({"title": "Synthetic register", "entries": [entry("LR-04", urgency="notice")]}),
                    encoding="utf-8")
    r = _pmlc("alert-grade", str(w))
    assert r.returncode == 0, r.stderr
    assert r.stdout.splitlines()[0] == 'alert-grade: notice for LR-04 (grade_source "register urgency")'


def test_alert_grade_notes_odd_urgency_and_priority(ws, tmp_path):  # noqa: F811
    """Review m1/m2: an urgency outside alert, notice, information is named and ignored; a --lr learning that is not
    priority 1 gets a note, since the safety-alert check refuses it."""
    g = alert.grade([entry("LR-01", urgency="High")])
    assert g["grade_source"] == "suggested" and g["grade"] == "alert"
    assert g["notes"] == ["LR-01 has urgency 'High', not one of alert, notice or information: it is ignored"]
    g = alert.grade([entry("LR-01", urgency="High"), entry("LR-02", urgency="notice"), entry("LR-03")])
    assert g["grade"] == "notice" and g["notes"] == [
        "no urgency in the register for LR-03",
        "LR-01 has urgency 'High', not one of alert, notice or information: it is ignored"]
    g = alert.grade([entry("LR-01"), entry("LR-02", 2)], ["LR-02", "LR-01"])
    assert g["notes"] == ["LR-02 is priority 2; the safety-alert check needs priority 1"]
    assert alert.grade([entry("LR-01"), entry("LR-02", 2)])["notes"] == []      # the default choice is priority 1
    reg = _reg(tmp_path, [entry("LR-01"), entry("LR-02", 2, urgency="High")])
    r = _pmlc("alert-grade", str(ws), "--register", str(reg), "--lr", "LR-02")
    assert r.returncode == 0, r.stderr
    assert r.stdout.splitlines()[-2:] == [
        "note: LR-02 has urgency 'High', not one of alert, notice or information: it is ignored",
        "note: LR-02 is priority 2; the safety-alert check needs priority 1"]


# ----------------------------------------------------------------------------- the one-slide pptx

def _with_profile(monkeypatch, prof):
    monkeypatch.setattr(profiles, "load", lambda path=None: {"test-pack": prof} if path is None else _REAL_LOAD(path))


def _deck_pack():
    p = pack_with(item("para", text="Check the seal before service.", cites=["FND-0001"]),
                  item("recommendation", change="Interlock the restart on a test record", indicator="Restarts tested",
                       hoc_tier="engineering", cites=["FND-0001"]),
                  item("question", question="Could a pump restart here without a test?", cites=["FND-0002"]))
    p["sections"].append({"id": "s2", "heading": "Section two", "items": [
        item("para", text="Ask the night shift. " + "Long text. " * 40, cites=["FND-0002"])]})
    return p


def test_pptx_one_slide(monkeypatch):
    pack = _deck_pack()
    _with_profile(monkeypatch, {"sections": [], "pptx_slides": 1})
    o = render_fixture("board-brief", "pptx", pack=copy.deepcopy(pack))[0]
    slides, notes = pptx_slides_text(o.data), pptx_notes_text(o.data)
    assert len(slides) == 3 and len(notes) == 3                         # cover, one content slide, closing
    one = slides[1]
    for want in ("Test before service.", "Section one", "Check the seal before service.",
                 "Interlock the restart on a test record", "Could a pump restart here without a test?", "Section two"):
        assert want in one, want
    assert one.index("Section one") < one.index("Check the seal") < one.index("Section two")
    assert "Long text. " * 40 not in one and "…" in one                  # clipped by _px_clip
    assert ("Long text. " * 39).strip() in notes[1]                      # the full text stays in the notes
    assert "Cites: FND-0002" in notes[1]                                 # the bottom line's citations, as on the normal deck
    assert "This pack cites" in slides[2]
    _with_profile(monkeypatch, {"sections": []})
    plain = render_fixture("board-brief", "pptx", pack=copy.deepcopy(pack))[0]
    monkeypatch.setattr(profiles, "load", _REAL_LOAD)
    base = render_fixture("board-brief", "pptx", pack=copy.deepcopy(pack))[0]
    assert plain.data == base.data and len(pptx_slides_text(base.data)) > 3


def _slide_paras(data: bytes, n: int) -> list:
    """(size in points, text, bullet, space after in points) of every paragraph in the body box of slide n of a pptx."""
    import io
    import re
    import zipfile
    xml = zipfile.ZipFile(io.BytesIO(data)).read(f"ppt/slides/slide{n}.xml").decode("utf-8")
    body = re.search(r'name="Body".*?</p:sp>', xml, re.S).group(0)
    out = []
    for p in re.findall(r"<a:p>.*?</a:p>", body, re.S):
        sz = int(re.search(r'sz="(\d+)"', p).group(1)) / 100
        after = int(re.search(r'<a:spcPts val="(\d+)"', p).group(1)) / 100
        out.append((sz, "".join(re.findall(r"<a:t>([^<]*)</a:t>", p)), "marL=" in p, after))
    return out


def test_pptx_one_slide_fits_at_the_profile_maxima(monkeypatch):
    """I1 (Task 2 review): 3 bottom-line entries, 6 sections and 13 items of 180+ characters fit the body box. The
    height is estimated here independently of the renderer: 0.52 em per character, 1.2 em line height."""
    from pmlc_lib.render import pptx as px
    long = ("Interlock the restart of the transfer pump on a recorded seal test so that no pump returns to service "
            "without a second check by the area operator and the maintenance technician on shift. ")
    bl = [{"text": f"Bottom line {k}: " + long, "cites": ["FND-0002"]} for k in range(3)]
    p = pack_with(*[item("para", text=f"Item {k}. " + long * 2, cites=["FND-0001"]) for k in range(3)], bottom_line=bl)
    for n in range(2, 7):
        p["sections"].append({"id": f"s{n}", "heading": f"Section {n}", "items": [
            item("para", text=f"Item {n}.{k}. " + long * 2, cites=["FND-0001"]) for k in range(2)]})
    assert sum(len(s["items"]) for s in p["sections"]) == 13 and len(p["sections"]) == 6
    _with_profile(monkeypatch, {"sections": [], "pptx_slides": 1})
    o = render_fixture("board-brief", "pptx", pack=copy.deepcopy(p))[0]
    paras = _slide_paras(o.data, 2)
    assert len(paras) == 3 + 6 + 13
    width = (px.PX_BODY[2] - 2 * 91440) / 12700
    h = 0.0
    for sz, text, bullet, after in paras:
        per = int((width - (27 if bullet else 0)) / (0.52 * sz))
        h += -(-len(text) // per) * 1.2 * sz + after
    assert h <= (px.PX_BODY[3] - 91440) / 12700, h                    # fits above the footer
    assert min(sz for sz, *_ in paras) >= 9
    assert all(len(t) <= 110 for sz, t, bullet, _ in paras if bullet)  # the items clipped harder to fit
    small = render_fixture("board-brief", "pptx", pack=copy.deepcopy(_deck_pack()))[0]    # a short pack keeps full size
    sizes = {sz for sz, *_ in _slide_paras(small.data, 2)}
    assert sizes == {18.0, 16.0, 14.0}


# ----------------------------------------------------------------------------- the P6-4 share gate, per mode

@pytest.fixture()
def shws(tmp_path):
    return share_ws(tmp_path)


def test_sister_site_share_needs_approval(tmp_path, shws):
    ws_, orgs = shws
    p = write_doc(tmp_path, dict(copy.deepcopy(SPACK), mode="sister-site"))
    out = tmp_path / "out"
    r = _cli("pack", str(ws_), str(p), "--share", "external", "--orgs", str(orgs), "--out", str(out))
    assert r.returncode == 1 and "cannot share externally: review is draft" in r.stderr
    assert files(out) == []
    sign(ws_, p, "--classification", "external", "--legal-review", "cleared")
    r = _cli("pack", str(ws_), str(p), "--share", "external", "--orgs", str(orgs), "--out", str(out))
    assert r.returncode == 0, r.stderr
    assert files(out) == ["test-pack.external.html", "test-pack.external.md"]
    assert REVIEW not in (out / "test-pack.external.md").read_text(encoding="utf-8")
    r = _cli("pack", str(ws_), str(p), "--out", str(tmp_path / "int"))      # the internal copy stays a review copy
    assert r.returncode == 0, r.stderr
    assert REVIEW in (tmp_path / "int" / "test-pack.md").read_text(encoding="utf-8")


def test_shared_layouts_drop_the_review_copy(tmp_path, shws):
    """Final review I1: an approved sister-site pack shared externally prints no review-copy line in any layout,
    while its internal print layouts all keep it."""
    from pmlc_lib.render.layouts import LAYOUTS
    ws_, orgs = shws
    pk = dict(copy.deepcopy(SPACK), mode="sister-site")
    pk["sections"][0]["items"] += [item("card"), item("check"), item("toolbox")]
    p = sign(ws_, write_doc(tmp_path, pk), "--classification", "external", "--legal-review", "cleared")
    for layout in LAYOUTS:
        out, inner = tmp_path / f"x-{layout}", tmp_path / f"n-{layout}"
        r = _cli("pack", str(ws_), str(p), "--share", "external", "--orgs", str(orgs), "--out", str(out),
                 "--layout", layout)
        assert r.returncode == 0, r.stderr
        assert REVIEW not in (out / f"test-pack.{layout}.external.html").read_text(encoding="utf-8"), layout
        r = _cli("pack", str(ws_), str(p), "--out", str(inner), "--layout", layout)
        assert r.returncode == 0, r.stderr
        assert REVIEW in (inner / f"test-pack.{layout}.html").read_text(encoding="utf-8"), layout


def test_industry_share_needs_public_approval(tmp_path, shws):
    ws_, orgs = shws
    p = write_doc(tmp_path, dict(copy.deepcopy(SPACK), mode="industry"))
    out = tmp_path / "out"
    r = _cli("pack", str(ws_), str(p), "--share", "public", "--orgs", str(orgs), "--out", str(out))
    assert r.returncode == 1 and "cannot share publicly: review is draft" in r.stderr
    assert files(out) == []
    sign(ws_, p, "--classification", "public", "--legal-review", "cleared")
    r = _cli("pack", str(ws_), str(p), "--share", "external", "--orgs", str(orgs), "--out", str(out))
    assert r.returncode == 1 and "an industry alert is shared with --share public" in r.stderr
    assert files(out) == []
    r = _cli("pack", str(ws_), str(p), "--share", "public", "--orgs", str(orgs), "--out", str(out))
    assert r.returncode == 0, r.stderr
    assert files(out) == ["test-pack.public.html", "test-pack.public.md"]
    assert REVIEW not in (out / "test-pack.public.md").read_text(encoding="utf-8")


def test_internal_mode_shares_as_before(tmp_path, shws):
    ws_, orgs = shws
    p = sign(ws_, write_doc(tmp_path, dict(copy.deepcopy(SPACK), mode="internal")), "--classification", "external",
             "--legal-review", "cleared")
    out = tmp_path / "out"
    r = _cli("pack", str(ws_), str(p), "--share", "external", "--orgs", str(orgs), "--out", str(out))
    assert r.returncode == 0, r.stderr
    assert files(out) == ["test-pack.external.html", "test-pack.external.md"]
    r = _cli("pack", str(ws_), str(p), "--out", str(tmp_path / "int"))
    assert REVIEW not in (tmp_path / "int" / "test-pack.md").read_text(encoding="utf-8")
