"""Phase 6 Task 8: the `could-it-happen-here` skill (sister-site HSE). Its manifest, audience entry, profile and
routing, the Hazira golden pack and the CIHH template made from it, and the external share that needs an approved
review (plan Phase 6 Task 8; Rulings P6-2, P6-5, P6-9)."""
import copy
import json
import re
import subprocess
import sys

import pytest

from test_pmlc import PMLC, ROOT, run
from test_privacy import _cli, files, share_ws, sign, write_doc

SKILL = "could-it-happen-here"
SKILLS_DIR = ROOT / "skills"
REFS = SKILLS_DIR / "learnings-coach" / "references"
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
REGISTER = SAMPLE / "outputs" / "learnings-register.json"
GOLDEN = SAMPLE / "outputs" / f"{SKILL}.json"
FIXTURE = ROOT / "tests" / "fixtures" / "packs" / f"{SKILL}.json"
BANNER = "A self-assessment for each site. Results show coverage and conditions, never a ranking of sites."
TRANSFERABLE = ("other sites", "industry-wide")


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def skill_md() -> str:
    return (SKILLS_DIR / SKILL / "SKILL.md").read_text(encoding="utf-8")


def self_checks(pack) -> list:
    return [it for s in pack["sections"] for it in s["items"] if it["kind"] == "self_check"]


# ----------------------------------------------------------------------------------------- manifest and routing

def test_manifest_as_planned():
    m = load(SKILLS_DIR / SKILL / "skill.json")
    assert m["kind"] == "audience" and m["audiences"] == ["sister-sites-hse"]
    assert m["requires"] == ["workspace", "register"] and m["optional_inputs"] == []
    assert m["formats"] == ["docx"] and m["share_default"] == "external"
    assert m["since"] == "2.0.0" and m["embed_default"] == "cited" and m["produces"]["pack"] == SKILL
    assert m["interactive"] is False


def test_audience_entry():
    a = next(x for x in load(REFS / "audiences.json") if x["id"] == "sister-sites-hse")
    assert a["skill"] == SKILL and a["default_scope"] == load(SKILLS_DIR / SKILL / "skill.json")["scope"]
    assert "HSE" in a["typical_people"] and "sister" in a["label"].lower()
    assert f"`{SKILL}`" in (REFS / "audiences.md").read_text(encoding="utf-8")


def test_profile_as_planned():
    p = load(REFS / "pack-profiles.json")[SKILL]
    assert [(s["id"], s["kinds"], s["min"], s["max"]) for s in p["sections"]] == [
        ("banner", ["para"], 1, 1), ("how-to-use", ["para"], 1, 2), ("self-checks", ["self_check"], 3, 12),
        ("after-assessment", ["para"], 1, 2)]
    assert p["rules"] == ["no-owner-due", "banner:cihh"] and p["bottom_line"] == {"min": 1, "max": 3}


def test_unplanned_in_sister_sites():
    steps = load(REFS / "workflows.json")["sister-sites"]["steps"]
    step = next(s for s in steps if s["skill"] == SKILL)
    assert "planned" not in step
    golden = load(ROOT / "tests" / "fixtures" / "plans" / "sister-sites.json")
    st = next(s for s in golden["steps"] if s["skill"] == SKILL)
    assert st["status"] == "todo" and st["planned_for"] is None
    assert f"PMLC check-pack <ws> <run>/outputs/{SKILL}.json --strict" in st["commands"]
    assert "approved review" in st["gate"]                       # share_default external (plan.py)


def test_skill_md_names_the_organisation_files_and_the_share_gate():
    t = skill_md()
    assert "PMLC register-items <ws> --transferable" in t
    assert f"PMLC templates <ws> cihh --pack <run>/outputs/{SKILL}.json" in t
    assert "PMLC consolidate <ws>" in t and "--pack <run>/outputs/could-it-happen-here.json" in t
    assert "never a ranking" in t or "never ranks" in t
    assert "approved" in t and "--share external" in t
    assert f"Worked example: samples/2020-09-24-hazira-gas-release-fire/outputs/{SKILL}.json (repository only)" in t
    assert len(t.splitlines()) <= 150


# ----------------------------------------------------------------------------------------- the Hazira golden

@pytest.fixture(scope="module")
def hz(tmp_path_factory):
    pytest.importorskip("openpyxl")
    root = tmp_path_factory.mktemp("hazira-cihh")
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root),
        "--overlay", "india-process-site")
    return root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"


def test_hazira_golden_passes_strict(hz):
    pack = load(GOLDEN)
    assert pack["pack"] == SKILL and pack["skill"] == SKILL and "handling" not in pack
    assert pack["scope"] == load(SKILLS_DIR / SKILL / "skill.json")["scope"]
    r = subprocess.run([sys.executable, str(PMLC), "check-pack", str(hz), str(GOLDEN), "--strict",
                        "--register", str(REGISTER)], capture_output=True, text=True)
    assert r.returncode == 0 and "OK:" in r.stdout and "problem" not in r.stdout + r.stderr, r.stdout + r.stderr
    r = subprocess.run([sys.executable, str(PMLC), "check-language", str(hz), str(GOLDEN)],
                       capture_output=True, text=True)
    assert r.returncode == 0 and "0 errors" in r.stdout + r.stderr, r.stdout + r.stderr


def test_hazira_golden_content():
    pack = load(GOLDEN)
    items = {s["id"]: s["items"] for s in pack["sections"]}
    assert [s["id"] for s in pack["sections"]] == ["banner", "how-to-use", "self-checks", "after-assessment"]
    assert items["banner"] == [{"kind": "para", "text": BANNER}]
    checks = self_checks(pack)
    assert 3 <= len(checks) <= 12 and checks == items["self-checks"]
    reg = {e["lr_id"]: e for e in load(REGISTER)["entries"]}
    for c in checks:
        e = reg[c["lr_id"]]                                       # every self_check carries a register lr_id
        assert e["transferability"] in TRANSFERABLE, c["lr_id"]  # drawn from register-items --transferable
        assert c["cites"] and set(c["cites"]) <= set(e["finding_ids"]) | set(e["evidence_ids"]), c["lr_id"]
        assert c["condition"].strip() and c["evidence_to_check"].strip() and c.get("look_in", "x").strip()
    assert len({c["lr_id"] for c in checks}) == len(checks)      # one self_check per chosen learning
    # the default choice: every priority-1 transferable learning (11 on Hazira), in register order
    want = [k for k, e in reg.items() if e["priority"] == 1 and e["transferability"] in TRANSFERABLE]
    assert [c["lr_id"] for c in checks] == want
    for v in items.values():                                     # D7: no owners, dates, answers or site names
        assert not any(k in it for it in v for k in ("owner", "by_when", "answer", "site", "assessor"))
    text = json.dumps(pack)
    assert not re.search(r"\[(?:CE|JEA|CCTV CR)\]|\bMr\.|\bHazira\b.*\bsite\b ranks", text)
    assert not re.search(r"\b(?:rank(?:ing|ed)? of sites|league table|score each site)\b", text.replace(BANNER, ""))
    assert 1 <= len(pack["bottom_line"]) <= 3


def test_hazira_golden_cihh_template(hz, tmp_path):
    """The golden makes a return template with one row per self_check and blank organisation columns (P6-9)."""
    openpyxl = pytest.importorskip("openpyxl")
    out = tmp_path / "out"
    out.mkdir()
    pk = out / f"{SKILL}.json"
    pk.write_text(GOLDEN.read_text(encoding="utf-8"), encoding="utf-8")
    xl = out / f"{SKILL}.cihh-template.xlsx"
    r = subprocess.run([sys.executable, str(PMLC), "templates", str(hz), "cihh", "--pack", str(pk), "--out", str(xl)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    wb = openpyxl.load_workbook(xl)
    ws = wb["Return"]
    assert ws["A1"].value == "Site" and ws["B1"].value in (None, "")
    rows = [[c.value for c in row] for row in ws.iter_rows(min_row=5) if row[0].value]
    checks = self_checks(load(GOLDEN))
    assert [r_[0] for r_ in rows] == [c["lr_id"] for c in checks]
    assert all(v in (None, "") for r_ in rows for v in r_[3:6])


# ----------------------------------------------------------------------------------------- sharing (synthetic)

def test_fixture_is_synthetic_and_follows_the_profile():
    pack = load(FIXTURE)
    assert pack["pack"] == SKILL and "Hazira" not in json.dumps(pack)
    assert all(c.get("lr_id") for c in self_checks(pack))
    assert [s["id"] for s in pack["sections"]] == ["banner", "how-to-use", "self-checks", "after-assessment"]


def _shared_pack():
    pack = copy.deepcopy(load(FIXTURE))
    for c in self_checks(pack):
        c["cites"] = ["FND-0001"]
    pack["bottom_line"] = [dict(b, cites=["FND-0001"]) for b in pack["bottom_line"]]
    return pack


def test_external_share_needs_an_approved_review(tmp_path):
    """share_default external: a masked copy of the pack, or of its template, only after an approved review."""
    pytest.importorskip("openpyxl")
    ws_, orgs = share_ws(tmp_path)
    p = write_doc(tmp_path, _shared_pack(), name=f"{SKILL}.json")
    out = tmp_path / "out"
    r = _cli("pack", str(ws_), str(p), "--share", "external", "--orgs", str(orgs), "--out", str(out))
    assert r.returncode == 1 and "cannot share externally: review is draft" in r.stderr
    xl = out / f"{SKILL}.cihh-template.external.xlsx"
    r = _cli("templates", str(ws_), "cihh", "--pack", str(p), "--share", "external", "--orgs", str(orgs),
             "--out", str(xl))
    assert r.returncode == 1 and "review is draft" in r.stderr
    assert files(out) == []
    sign(ws_, p, "--classification", "external", "--legal-review", "cleared")
    r = _cli("pack", str(ws_), str(p), "--share", "external", "--orgs", str(orgs), "--out", str(out))
    assert r.returncode == 0, r.stderr
    r = _cli("templates", str(ws_), "cihh", "--pack", str(p), "--share", "external", "--orgs", str(orgs))
    assert r.returncode == 0, r.stderr
    made = sorted(x.name for x in tmp_path.rglob("*.cihh-template*.xlsx"))      # in <run>/outputs
    assert made == [f"{SKILL}.cihh-template.external.xlsx"], made          # only the masked copy is written
    assert files(out) == [f"{SKILL}.external.html", f"{SKILL}.external.md"]
