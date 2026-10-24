"""Phase 5 Task 18: the `risk-register-update` skill (enterprise risk management). Its manifest, audience entry,
profile and routing, the Hazira select counts it is written against, and its Hazira golden pack."""
import csv
import io
import json
import re
import subprocess
import sys

import pytest

from test_pmlc import PMLC, ROOT, run

SKILL = "risk-register-update"
SKILLS_DIR = ROOT / "skills"
REFS = SKILLS_DIR / "learnings-coach" / "references"
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
REGISTER = SAMPLE / "outputs" / "learnings-register.json"
GOLDEN = SAMPLE / "outputs" / f"{SKILL}.json"
# The six Hazira codes whose name contains "risk" (calibration: 68 findings, Task 8)
RISK_CODES = ["OIC 2.7", "OIP 3.2", "SVF 3.4", "SVI 1.8", "SVIO 2.4", "SVV 4.5"]
BANNER = "Proposals for the risk owner to assess: no loss estimates and no rating decisions."
WHEN = "the user asks for risk-register or bow-tie changes"


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def skill_md() -> str:
    return (SKILLS_DIR / SKILL / "SKILL.md").read_text(encoding="utf-8")


def code_line_codes() -> list:
    """The codes on the SKILL.md `PMLC select <ws> --code …` line."""
    line = next(x for x in skill_md().splitlines() if x.startswith("PMLC select <ws> --code "))
    return re.findall(r'"([A-Z]+ \d+\.\d+)"', line.split("#", 1)[0])


def test_manifest_as_planned():
    m = load(SKILLS_DIR / SKILL / "skill.json")
    assert m["kind"] == "audience" and m["audiences"] == ["enterprise-risk"]
    assert m["scope"]["levels"] == [2, 3, 4]
    assert m["requires"] == ["workspace"] and m["optional_inputs"] == ["register"]
    assert m["formats"] == ["risk-csv", "bowtie-csv"] and m["share_default"] == "internal"
    assert m["since"] == "2.0.0" and m["embed_default"] == "cited" and m["produces"]["pack"] == SKILL


def test_audience_entry():
    a = next(x for x in load(REFS / "audiences.json") if x["id"] == "enterprise-risk")
    assert a["label"] == "Enterprise risk management" and a["tier"] == "T4" and a["skill"] == SKILL
    for who in ("ERM leads", "risk owners", "insurers' risk engineers"):
        assert who in a["typical_people"], who
    assert a["default_scope"] == load(SKILLS_DIR / SKILL / "skill.json")["scope"]


def test_profile_as_planned():
    p = load(REFS / "pack-profiles.json")[SKILL]
    assert [(s["id"], s["kinds"], s["min"], s["max"]) for s in p["sections"]] == [
        ("banner", ["para"], 1, 1), ("risk-changes", ["risk_change"], 1, 15), ("kri", ["indicator"], 1, 8),
        ("bowtie", ["barrier"], 0, 10)]
    assert p["rules"] == ["banner:risk", "no-owner-due"] and p["bottom_line"] == {"min": 1, "max": 5}


def test_routed_in_leadership_after_top_management_brief():
    # guarded steps sit after every unguarded step (task 14 review I-1), so this one follows board-brief
    steps = load(REFS / "workflows.json")["leadership"]["steps"]
    names = [s["skill"] for s in steps]
    step = steps[names.index(SKILL)]
    assert names.index("top-management-brief") < names.index("board-brief") < names.index(SKILL)
    assert step["when"] == WHEN and all("when" in s for s in steps[names.index(SKILL):])
    assert SKILL in json.dumps(load(ROOT / "tests" / "fixtures" / "plans" / "leadership.json"))


def test_select_line_matches_the_preset():
    pre = {p["name"]: p["args"] for p in load(REFS / "select-presets.json")[SKILL]}
    assert pre == {"risk-codes": ["--code", *RISK_CODES, "--brief"]}
    assert code_line_codes() == RISK_CODES


@pytest.fixture(scope="module")
def hz(tmp_path_factory):
    pytest.importorskip("openpyxl")
    root = tmp_path_factory.mktemp("hazira-risk")
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root),
        "--overlay", "india-process-site")
    return root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"


def test_hazira_risk_codes_and_count(hz):
    """The --code list is every Hazira code whose name contains "risk": 6 codes, 68 findings. The taxonomy has no
    `barrier` tag, so the plan's `--tag barrier` line does not apply."""
    F = load(hz / "findings.json")
    assert sorted({f["code"] for f in F if "risk" in f["name"].lower()}) == RISK_CODES
    out = run("select", str(hz), "--code", *RISK_CODES, "--format", "json")
    assert len(json.loads(out[out.index("["):])) == 68
    tags = {t for e in load(REFS / "taxonomy.json")["entities"] for t in e.get("tags", [])}
    assert "barrier" not in tags


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


def test_owner_on_an_item_fails_even_without_strict(hz, tmp_path):
    """no-owner-due (D7): a risk owner or a date written into the pack is a problem without --strict."""
    pack = load(GOLDEN)
    kri = next(s for s in pack["sections"] if s["id"] == "kri")
    kri["items"][0]["owner"] = "Head of enterprise risk"
    bad = tmp_path / f"{SKILL}.json"
    bad.write_text(json.dumps(pack), encoding="utf-8")
    r = subprocess.run([sys.executable, str(PMLC), "check-pack", str(hz), str(bad)], capture_output=True, text=True)
    assert r.returncode != 0 and "owner and due dates are set by the organisation" in r.stdout + r.stderr


def test_hazira_golden_content():
    pack = load(GOLDEN)
    items = {s["id"]: s["items"] for s in pack["sections"]}
    assert items["banner"] == [{"kind": "para", "text": BANNER}]
    changes = items["risk-changes"]
    # at least one item for each change_type the evidence supports (all four named types are supported on Hazira)
    assert {"missing-threat", "control-rating", "accepted-without-authority", "kri"} <= {c["change_type"] for c in changes}
    assert all(c.get("id") and c["cites"] for c in changes)
    assert len({c["id"] for c in changes}) == len(changes)
    assert all(it.get("cites") for it in items["kri"])
    assert all(b["group"] in ("Prevention", "Mitigation") for b in items.get("bowtie", []))
    for v in items.values():                                                          # D7: no owners or dates
        assert not any("owner" in it or "by_when" in it for it in v)
    text = json.dumps(pack)
    assert not re.search(r"\[(?:CE|JEA|CCTV CR)\]|\bMr\.", text)                       # roles only
    assert not re.search(r"(?:₹|Rs\.?\s?\d|INR|USD|\$\s?\d|\bcrore\b|\blakh\b)", text, re.I)   # no cost figures (JC8)
    assert any(c.get("learning") == "LR-07" for c in changes)
    assert "cost" in " ".join(pack["limits"]).lower()


def test_hazira_golden_risk_csv(hz, tmp_path):
    """The golden's risk-changes.csv has one row per risk_change item and a blank risk_owner_decision column."""
    out = tmp_path / "out"
    out.mkdir()
    pk = out / f"{SKILL}.json"
    pk.write_text(GOLDEN.read_text(encoding="utf-8"), encoding="utf-8")
    r = subprocess.run([sys.executable, str(PMLC), "pack", str(hz), str(pk), "--format", "risk-csv,bowtie-csv",
                        "--out", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    rows = list(csv.reader(io.StringIO((out / f"{SKILL}.risk-changes.csv").read_text(encoding="utf-8"))))
    n = sum(1 for s in load(GOLDEN)["sections"] for it in s["items"] if it["kind"] == "risk_change")
    assert rows[0][-1] == "risk_owner_decision" and len(rows) == n + 1 and all(r[-1] == "" for r in rows[1:])
    assert (out / f"{SKILL}.bowtie.csv").exists()
