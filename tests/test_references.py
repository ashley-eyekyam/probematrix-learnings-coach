"""Shared reference files under skills/learnings-coach/references/.

Task 3 (Phase 3): jurisdictions.md, standards-crosswalk.json and data-handling.md (L7-10, L7-01, L7-15)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / "skills" / "learnings-coach" / "references"

# --- Task 3: jurisdictions, standards crosswalk, data handling -------------------------------------------------

CROSSWALK_ID = re.compile(r"^[A-Z0-9]+-[A-Za-z0-9.()-]+$")
CROSSWALK_FRAMEWORKS = ["iso45001", "psm", "rmp", "seveso", "rbps", "icmm", "india"]
# Spec section 3.6 and lens-7 L7-01: the requirement IDs the crosswalk must carry.
CROSSWALK_SPEC_IDS = [
    *(f"ISO45001-{c}" for c in ("5.4", "7.2", "7.3", "7.4", "9.1", "9.2", "9.3", "10.2")),
    *(f"PSM-(m)({n})" for n in range(1, 8)),
    *(f"PSM-(o)({n})" for n in range(1, 6)),
    "RMP-68.81",
    "SEVESO-AnnexIII(vi)", "SEVESO-AnnexIII(vii)", "COMAH-SMS",
    "RBPS-incident-investigation", "RBPS-measurement-and-metrics", "RBPS-auditing", "RBPS-management-review",
    "ICMM-CCM-8", "ICMM-CCM-9",
    "IN-FactoriesAct-s.41G", "IN-FactoriesAct-s.88", "IN-OSHCode2020-s.10", "IN-OSHCode2020-s.11",
    "IN-OSHCode2020-s.22", "IN-MSIHC-r.5", "IN-ERDMP", "IN-OISD", "IN-DGMS-s.23",
]
# Lens-7 / spec section 10: citations that could not be confirmed against primary text.
UNVERIFIED_MARKERS = ["2026 amendment", "dgms", "mines act", "srsc", "safety representatives",
                      "contract labour", "contract-labour", "legitimate uses"]
PSM_OTHER_LETTER = re.compile(r"1910\.119\((?![mo]\))[a-z]\)")
JURISDICTIONS = ["in", "uk", "us", "eu"]
DATA_HANDLING_HEADINGS = ["Lawful basis", "Data minimisation", "Role identifiability", "Disclosure to the AI host",
                          "Retention", "GDPR", "DPDP Act 2023", "This is not the investigation record"]


def _crosswalk() -> dict:
    return json.loads((REFS / "standards-crosswalk.json").read_text(encoding="utf-8"))


def _crosswalk_requirements() -> list:
    return [r for fw in _crosswalk()["frameworks"].values() for r in fw["requirements"]]


def test_crosswalk_shape():
    cw = _crosswalk()
    assert cw["version"] == 1
    assert list(cw["frameworks"]) == CROSSWALK_FRAMEWORKS
    for key, fw in cw["frameworks"].items():
        assert isinstance(fw["title"], str) and fw["title"], key
        assert fw["requirements"], key
        for r in fw["requirements"]:
            assert set(r) == {"id", "title", "verified"}, r
            assert isinstance(r["title"], str) and r["title"], r
            assert isinstance(r["verified"], bool), r


def test_crosswalk_ids_unique_and_wellformed():
    ids = [r["id"] for r in _crosswalk_requirements()]
    assert len(ids) == len(set(ids)), sorted({i for i in ids if ids.count(i) > 1})
    bad = [i for i in ids if not CROSSWALK_ID.match(i)]
    assert not bad, bad


def test_crosswalk_covers_spec_list():
    ids = {r["id"] for r in _crosswalk_requirements()}
    missing = [i for i in CROSSWALK_SPEC_IDS if i not in ids]
    assert not missing, missing


def test_unverified_flags():
    """A title that names an unverified item has verified false, and verified false iff the title says (unverified)."""
    bad = []
    for r in _crosswalk_requirements():
        t = r["title"].lower()
        if (any(m in t for m in UNVERIFIED_MARKERS) or PSM_OTHER_LETTER.search(t)) and r["verified"]:
            bad.append(f"{r['id']}: names an unverified item but is verified")
        if r["verified"] == ("(unverified)" in t):
            bad.append(f"{r['id']}: verified={r['verified']} disagrees with the (unverified) mark")
    assert not bad, bad


def _jurisdiction_sections() -> dict:
    text = (REFS / "jurisdictions.md").read_text(encoding="utf-8")
    parts = re.split(r"^## (\S+)[ \t]*$", text, flags=re.M)
    return dict(zip(parts[1::2], parts[2::2]))


def test_jurisdictions_regimes_lines():
    secs = _jurisdiction_sections()
    assert list(secs) == JURISDICTIONS
    for code, body in secs.items():
        lines = [x for x in body.splitlines() if x.strip()]
        regimes = [x for x in lines if x.startswith("Regimes: ")]
        checked = [x for x in lines if re.fullmatch(r"Last checked: \d{4}-\d{2}-\d{2}", x)]
        assert len(regimes) == 1 and lines[0] == regimes[0], f"{code}: first line must be the one Regimes: line"
        assert len(checked) == 1, f"{code}: needs one Last checked: YYYY-MM-DD line"
        items = [x.strip() for x in regimes[0][len("Regimes: "):].split(",")]
        assert items and all(items), f"{code}: empty regime in {regimes[0]!r}"
        assert "Sources" in body, f"{code}: no sources"


def test_data_handling_sections():
    text = (REFS / "data-handling.md").read_text(encoding="utf-8")
    heads = re.findall(r"^## (.+?)\s*$", text, flags=re.M)
    missing = [h for h in DATA_HANDLING_HEADINGS if h not in heads]
    assert not missing, missing
    assert "(unverified)" in text   # the DPDP "legitimate uses" clause
