"""Task 14 (Phase 5): the latent-conditions-profile skill. Its Hazira golden pack carries the engine's numbers
unchanged (SVI 1.4 x21, OIC 2.1 feeds 36, the level 3-4 share), the profile-limits banner and the "What this profile
cannot tell you" para, and passes check-pack --strict with the register and check-language with no errors."""
import json
import shutil

import pytest

from test_pmlc import ROOT, run
from pmlc_lib.pack.profiles import BANNERS

pytest.importorskip("openpyxl")
SKILL = "latent-conditions-profile"
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
GOLDEN = SAMPLE / "outputs" / f"{SKILL}.json"
REGISTER = SAMPLE / "outputs" / "learnings-register.json"


@pytest.fixture(scope="module")
def hz(tmp_path_factory):
    root = tmp_path_factory.mktemp("hazira-lcp")
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root),
        "--overlay", "india-process-site")
    ws = root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"
    run("hfacs-profile", str(ws))
    shutil.copy(REGISTER, ws.parent / "outputs" / REGISTER.name)
    shutil.copy(GOLDEN, ws.parent / "outputs" / GOLDEN.name)
    return ws


def _pack():
    return json.loads(GOLDEN.read_text(encoding="utf-8"))


def _section(pack, sid):
    return next(s for s in pack["sections"] if s["id"] == sid)


def _table_item(ws, which):
    return json.loads(run("hfacs-profile", str(ws), "--table-item", which))


def test_manifest():
    m = json.loads((ROOT / "skills" / SKILL / "skill.json").read_text(encoding="utf-8"))
    assert (m["kind"], m["scope"]["levels"], m["requires"], m["optional_inputs"]) == \
        ("analysis", [3, 4], ["workspace", "hfacs-profile"], ["register"])
    assert (m["formats"], m["share_default"], m["embed_default"], m["since"]) == \
        (["docx", "pptx"], "internal", "cited", "2.0.0")
    assert m["produces"]["pack"] == SKILL


def test_profile_entry():
    prof = json.loads((ROOT / "skills" / "learnings-coach" / "references" / "pack-profiles.json")
                      .read_text(encoding="utf-8"))[SKILL]
    got = [(s["id"], s["kinds"], s["min"], s["max"]) for s in prof["sections"]]
    assert got == [("heatmap", ["table"], 1, 1), ("feeds", ["table"], 1, 1), ("recurrence", ["table"], 0, 1),
                   ("share", ["para"], 1, 2), ("learnings", ["learning"], 1, 6), ("cannot-tell", ["para"], 1, 1)]
    assert prof["rules"] == ["banner:profile-limits"] and prof["bottom_line"] == {"min": 1, "max": 5}


def test_golden_carries_engine_numbers(hz):
    pack = _pack()
    heat = _section(pack, "heatmap")["items"][0]
    assert heat == _table_item(hz, "heatmap")                     # the heat map is pasted whole
    for sid, which in (("feeds", "feeds"), ("recurrence", "recurrence")):
        got, eng = _section(pack, sid)["items"][0], _table_item(hz, which)
        n = len(got["rows"])
        assert 0 < n <= len(eng["rows"])
        assert got["rows"] == eng["rows"][:n] and got["row_cites"] == eng["row_cites"][:n], sid   # top rows only
        assert n <= 12 and got["cites"] == sorted({x for c in got["row_cites"] for x in c}), sid
    feeds = {r[0]: r[2] for r in _section(pack, "feeds")["items"][0]["rows"]}
    rec = {r[0]: r[2] for r in _section(pack, "recurrence")["items"][0]["rows"]}
    assert feeds["OIC 2.1"] == 36 and rec["SVI 1.4"] == 21
    prof = json.loads((hz / "hfacs_profile.json").read_text(encoding="utf-8"))
    share = f"{prof['share_l34'] * 100:.1f}%"
    assert share == "70.6%"
    assert any(share in it["text"] for it in _section(pack, "share")["items"])


def test_golden_banner_and_limits():
    pack = _pack()
    paras = [it["text"] for s in pack["sections"] for it in s["items"] if it["kind"] == "para"]
    assert BANNERS["profile-limits"] in paras
    ct = _section(pack, "cannot-tell")
    assert ct["heading"] == "What this profile cannot tell you"
    def dicts(x):
        if isinstance(x, dict):
            yield x
            for v in x.values():
                yield from dicts(v)
        elif isinstance(x, list):
            for v in x:
                yield from dicts(v)
    assert all("owner" not in d and "by_when" not in d for d in dicts(pack))      # D7, anywhere in the pack


def test_golden_passes_strict_and_language(hz):
    out = run("check-pack", str(hz), str(hz.parent / "outputs" / GOLDEN.name), "--strict", "--register", str(REGISTER))
    assert "OK:" in out and "problem" not in out, out                 # run() also asserts exit 0
    lang = run("check-language", str(hz), str(hz.parent / "outputs" / GOLDEN.name))
    assert "check-language: 0 errors" in lang, lang


def test_leadership_next_reaches_the_coaches_without_this_pack():
    """The guarded step sits last in `leadership`, so plan --next goes from the register to site-leadership-coach
    when nobody asked for patterns (task 14 review I-1)."""
    from pmlc_lib import plan
    p = json.loads((ROOT / "tests" / "fixtures" / "plans" / "leadership.json").read_text(encoding="utf-8"))
    for s in p["steps"]:
        if s["skill"] == "learnings-register":
            s["status"] = "done"
    assert plan.next_step(p)["skill"] == "site-leadership-coach"
    order = [s["skill"] for s in p["steps"]]
    i = order.index(SKILL)
    assert order[i - 1] == "engine:hfacs-profile" and p["steps"][i]["when"]
    # only guarded steps follow it, and the engine steps that feed them (Phase 6 Task 12: engine:accimap)
    assert all(s["when"] or s["skill"].startswith("engine:") for s in p["steps"][i:])
