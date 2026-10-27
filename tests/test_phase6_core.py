"""Phase 6 core (Task 1): the alert pack fields mode, grade and grade_source, the five new profile rules, the review
copy of a sister-site or industry pack (P6-4) and the grade badge in every format. Synthetic export from
test_pmlc.py only (fictional event, no real data)."""
import json
import re
import subprocess
import sys
import zipfile

import pytest

from test_pmlc import PMLC, run, ws  # noqa: F401  (ws is a module-scoped fixture)
from test_pack import WAVE5, item, pack_with
import pmlc  # noqa: E402
import pmlc_pack as pp  # noqa: E402
from pmlc_lib import alert  # noqa: E402
from pmlc_lib.pack import command as pcmd, profiles  # noqa: E402

_REAL_LOAD = profiles.load
REVIEW = ("Review copy: not for distribution outside the organisation until it is approved and shared with "
          "--share external.")
INFERRED = ("Placements above the company level are inferred from codes and departments. A person confirms them "
            "before this map is shared.")


@pytest.fixture(scope="module")
def w(ws):  # noqa: F811
    return pmlc.load_ws(ws)


def with_profile(monkeypatch, prof):
    """Give the synthetic pack name test-pack a profile, keeping every other profile file as it is."""
    monkeypatch.setattr(profiles, "load", lambda path=None: {"test-pack": prof} if path is None else _REAL_LOAD(path))


def sec(sid, *items):
    return {"id": sid, "heading": sid.replace("-", " ").title(), "items": list(items)}


def test_fixed_copy_verbatim():
    B = profiles.BANNERS
    assert B["alert-review-copy"] == REVIEW
    assert B["cihh"] == ("A self-assessment for each site. Results show coverage and conditions, never a ranking of "
                         "sites.")
    assert B["learning-team"] == "The team supplies the answers. These are questions, not findings about people."
    assert B["restorative"] == ("The export holds no information about the people affected. Every need here is a "
                                "question to ask, or the organisation's own answer.")
    assert B["accimap-inferred"] == INFERRED
    assert B["effectiveness"] == ("The organisation sets owners, dates and statuses. This plan sets out what to check "
                                  "and when, counted from adoption.")
    assert alert.GRADE_SOURCES == ("register urgency", "chosen by the user")
    for r in ("grade-source", "alert-priority-1", "leading-lagging", "needs-are-questions", "inferred-banner"):
        assert r in profiles.RULES
    assert isinstance(WAVE5, list)


def test_grade_fields_validate(w):
    ok = pack_with(item("para"), mode="sister-site", grade="alert", grade_source="chosen by the user")
    assert not [x for x in pp.check_pack(ok, w, strict=True).problems if x.split(":")[0] in ("mode", "grade",
                                                                                             "grade_source")]
    res = pp.check_pack(pack_with(item("para"), grade="urgent"), w)
    assert "grade: must be one of alert, notice, information" in res.problems
    res = pp.check_pack(pack_with(item("para"), grade="alert", grade_source="suggested"), w)
    assert "grade_source: must be one of register urgency, chosen by the user" in res.problems
    res = pp.check_pack(pack_with(item("para"), mode="external"), w)
    assert "mode: must be one of internal, sister-site, industry" in res.problems
    res = pp.check_pack(pack_with(item("para")), w, strict=True)
    assert not [x for x in res.problems + res.warnings if x.startswith(("mode", "grade"))]


def test_grade_source_rule_warns(w, monkeypatch):
    with_profile(monkeypatch, {"sections": [{"id": "s1", "kinds": ["para"], "min": 0, "max": 99}],
                               "rules": ["grade-source"]})
    for strict in (False, True):
        res = pp.check_pack(pack_with(item("para"), grade="alert"), w, strict=strict)
        hits = [x for x in res.warnings if x.startswith("grade-source")]
        assert len(hits) == 1, res.warnings
        assert not [x for x in res.problems if "grade" in x], res.problems
    res = pp.check_pack(pack_with(item("para"), grade="notice", grade_source="register urgency"), w)
    assert not [x for x in res.warnings + res.problems if x.startswith("grade-source")]


REG = {"entries": [{"lr_id": "LR-01", "priority": 1}, {"lr_id": "LR-02", "priority": 2}]}
PROF_ALERT = {"sections": [{"id": "learnings", "kinds": ["learning"], "min": 0, "max": 99}],
              "rules": ["alert-priority-1"]}


def test_alert_priority_1_rule(w, monkeypatch):
    with_profile(monkeypatch, PROF_ALERT)
    pack = pack_with(sections=[sec("learnings", item("learning", id="l-1", learning="LR-01"),
                                   item("learning", id="l-2", learning="LR-02"))])
    res = pp.check_pack(pack, w, register=REG)
    hits = [x for x in res.problems if "alert-priority-1" in x]
    assert len(hits) == 1 and "LR-02" in hits[0] and "l-2" in hits[0], res.problems
    assert not [x for x in res.problems if "alert-priority-1" in x and "LR-01" in x]
    nolr = pack_with(sections=[sec("learnings", item("learning", id="l-3"))])
    assert [x for x in pp.check_pack(nolr, w, register=REG).problems if "alert-priority-1" in x and "l-3" in x]
    assert not [x for x in pp.check_pack(pack, w).problems if "alert-priority-1" in x]   # no register: skipped


PROF_IND = {"sections": [{"id": "indicators", "kinds": ["table"], "min": 0, "max": 99}], "rules": ["leading-lagging"]}


def test_leading_lagging_rule(w, monkeypatch):
    with_profile(monkeypatch, PROF_IND)
    tab = item("table", id="ind", columns=["Learning", "Leading", "Lagging"],
               rows=[["LR-01", "permits checked", "repeat releases"], ["LR-02", "drills held", " "]])
    res = pp.check_pack(pack_with(sections=[sec("indicators", tab)]), w)
    hits = [x for x in res.problems if x.startswith("leading-lagging")]
    assert len(hits) == 1 and "ind" in hits[0] and "row 2" in hits[0] and "Lagging" in hits[0], res.problems
    good = item("table", columns=["Learning", "Leading", "Lagging"], rows=[["LR-01", "a", "b"]])
    assert not [x for x in pp.check_pack(pack_with(sections=[sec("indicators", good)]), w).problems
                if x.startswith("leading-lagging")]
    nocol = item("table", id="t2", columns=["Learning", "Leading"], rows=[["LR-01", "a"]])
    assert [x for x in pp.check_pack(pack_with(sections=[sec("indicators", nocol)]), w).problems
            if x.startswith("leading-lagging") and "Lagging" in x]


def test_needs_are_questions_rule(w, monkeypatch):
    with_profile(monkeypatch, {"sections": [{"id": "needs", "kinds": ["question", "para"], "min": 0, "max": 99}],
                               "rules": ["needs-are-questions"]})
    pack = pack_with(sections=[sec("needs", item("question"), item("para", id="p-1"))])
    res = pp.check_pack(pack, w)
    assert [x for x in res.warnings if "needs are asked, never inferred" in x and "p-1" in x], res.warnings
    assert [x for x in pp.check_pack(pack, w, strict=True).problems if "needs are asked, never inferred" in x]
    ok = pack_with(sections=[sec("needs", item("question"))])
    assert not [x for x in pp.check_pack(ok, w, strict=True).problems if "never inferred" in x]


def test_inferred_banner_rule(w, monkeypatch):
    with_profile(monkeypatch, {"sections": [{"id": "s1", "kinds": ["graph", "para"], "min": 0, "max": 99}],
                               "rules": ["inferred-banner"]})
    g = item("graph", nodes=[{"id": "a", "label": "Regulator", "inferred": True}, {"id": "b", "label": "Crew"}],
             edges=[{"from": "a", "to": "b"}])
    res = pp.check_pack(pack_with(g), w)
    assert [x for x in res.problems if x.startswith("inferred-banner")], res.problems
    assert not [x for x in pp.check_pack(pack_with(item("para", text=INFERRED), g), w, strict=True).problems
                if "inferred-banner" in x]
    plain = item("graph")
    assert not [x for x in pp.check_pack(pack_with(plain), w, strict=True).problems if "inferred-banner" in x]


def test_review_copy_needed():
    f = pcmd.review_copy_needed
    assert f({"mode": "sister-site"}, "internal") and f({"mode": "industry"}, "internal")
    assert f({"mode": "industry"}, "external")
    assert not f({"mode": "sister-site"}, "external") and not f({"mode": "sister-site"}, "public")
    assert not f({"mode": "industry"}, "public")
    assert not f({"mode": "internal"}, "internal") and not f({}, "internal")


def _write(tmp_path, pack, name="p.json"):
    p = tmp_path / name
    p.write_text(json.dumps(pack, indent=1), encoding="utf-8")
    return p


def test_review_copy_sister_site(ws, tmp_path):  # noqa: F811
    pack = pack_with(item("para", text="Check the seal before service."), mode="sister-site")
    p = _write(tmp_path, pack)
    before = p.read_bytes()
    out = tmp_path / "out"
    run("pack", str(ws), str(p), "--out", str(out))
    assert p.read_bytes() == before
    page = (out / "test-pack.html").read_text(encoding="utf-8")
    first = re.search(r'id="s-s1".*?<div class="item [^"]*"[^>]*><p>(.*?)</p>', page, re.S)
    assert first and first.group(1) == REVIEW, page[-3000:]
    md = (out / "test-pack.md").read_text(encoding="utf-8")
    body = md.split("## Section one", 1)[1].strip().splitlines()
    assert body[0].strip() == REVIEW, body[:3]
    internal = _write(tmp_path, pack_with(item("para", text="Check the seal before service.")), "q.json")
    run("pack", str(ws), str(internal), "--out", str(tmp_path / "out2"))
    assert REVIEW not in (tmp_path / "out2" / "test-pack.md").read_text(encoding="utf-8")


def test_industry_needs_public(ws, tmp_path):  # noqa: F811
    p = _write(tmp_path, pack_with(item("para"), mode="industry"))
    r = subprocess.run([sys.executable, str(PMLC), "pack", str(ws), str(p), "--share", "external", "--out",
                        str(tmp_path / "o")], capture_output=True, text=True)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "an industry alert is shared with --share public" in r.stderr
    assert "Traceback" not in r.stderr and not (tmp_path / "o").exists()


def test_grade_badge_every_format(ws, tmp_path):  # noqa: F811
    p = _write(tmp_path, pack_with(item("para"), grade="alert", grade_source="chosen by the user"))
    out = tmp_path / "out"
    run("pack", str(ws), str(p), "--out", str(out), "--format", "html,md,docx,pptx,email")
    want = "Grade: Alert"
    assert want in (out / "test-pack.html").read_text(encoding="utf-8")
    assert want in (out / "test-pack.md").read_text(encoding="utf-8")
    assert want in (out / "test-pack.email.html").read_text(encoding="utf-8")
    assert want in (out / "test-pack.email.txt").read_text(encoding="utf-8")
    with zipfile.ZipFile(out / "test-pack.docx") as z:
        assert want in z.read("word/document.xml").decode("utf-8")
    with zipfile.ZipFile(out / "test-pack.pptx") as z:
        assert want in z.read("ppt/slides/slide1.xml").decode("utf-8")
    p2 = _write(tmp_path, pack_with(item("para")), "plain.json")
    run("pack", str(ws), str(p2), "--out", str(tmp_path / "o2"), "--format", "html,md")
    assert "Grade:" not in (tmp_path / "o2" / "test-pack.md").read_text(encoding="utf-8")


LAYOUT_ITEMS = ("para", "card", "check", "toolbox")      # something for each of the six layouts to print


@pytest.mark.parametrize("mode", ["sister-site", "industry"])
def test_review_copy_every_layout(ws, tmp_path, mode):  # noqa: F811
    """Final review I1 (P6-4): every print layout carries the review-copy line and the grade on each printed page;
    an internal pack carries neither the line nor a grade it does not have."""
    from pmlc_lib.render.layouts import LAYOUTS
    p = _write(tmp_path, pack_with(*(item(k) for k in LAYOUT_ITEMS), mode=mode, grade="alert",
                                   grade_source="chosen by the user"))
    internal = _write(tmp_path, pack_with(*(item(k) for k in LAYOUT_ITEMS)), "internal.json")
    for layout in LAYOUTS:
        out, out2 = tmp_path / f"o-{mode}-{layout}", tmp_path / f"i-{mode}-{layout}"
        run("pack", str(ws), str(p), "--out", str(out), "--layout", layout)
        page = (out / f"test-pack.{layout}.html").read_text(encoding="utf-8")
        n_pages = page.count('<section class="page')
        assert n_pages and page.count(REVIEW) == n_pages, (layout, page.count(REVIEW), n_pages)
        assert page.count("Grade: Alert") == n_pages, layout
        run("pack", str(ws), str(internal), "--out", str(out2), "--layout", layout)
        page2 = (out2 / f"test-pack.{layout}.html").read_text(encoding="utf-8")
        assert REVIEW not in page2 and "Grade:" not in page2, layout


def test_alert_fields_are_not_translated():
    from pmlc_lib import strings
    assert {"mode", "grade", "grade_source"} <= strings.LOCKED_FIELDS
