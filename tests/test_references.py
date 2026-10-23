"""Reference files under skills/learnings-coach/references/: shape, coverage of the Hazira sample, and wording rules."""
import json
import re

import pytest

from test_pmlc import ROOT, run
import pmlc  # noqa: E402  (test_pmlc put the engine folder on sys.path)
import pmlc_pack  # noqa: E402

REF = ROOT / "skills" / "learnings-coach" / "references"
SAMPLE_EXPORT = (ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
                 / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx")
NEW_MD = ("hfacs-levels.md", "barriers-and-controls.md", "indicators-and-effectiveness.md")
HAZIRA_PREFIXES = {1: {"AJDE", "APE", "ASBE", "AV"}, 2: {"PPE", "PPI", "PSE", "PTE", "PTF"},
                   3: {"SVF", "SVI", "SVIO", "SVV"}, 4: {"OIC", "OIP", "OIR", "OIS"}}
# L3-09 / M4: terms that must stay stable across languages
L309_TERMS = ("Finding", "Evidence", "Nanocode", "Instance", "Learning", "Learning Cluster", "Tier", "Relation",
              "Barrier", "Precursor", "Weak signal", "Near miss", "Hold point", "Permit-to-work",
              "Management of change (MOC)", "Lockout/tagout (LOTO)", "Critical control", "Leading indicator",
              "Lagging indicator", "Sighted", "Blind", "Just culture", "HFACS", "HFMAP")


def _json(name):
    return json.loads((REF / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def hazira_findings(tmp_path_factory):
    root = tmp_path_factory.mktemp("hz-refs")
    run("ingest", str(SAMPLE_EXPORT), "--slug", "hazira-gas-release-fire", "--root", str(root))
    ws = root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"
    return json.loads((ws / "findings.json").read_text(encoding="utf-8"))


def test_hfacs_codes_cover_sample(hazira_findings):
    codes = _json("hfacs-codes.json")["prefixes"]
    seen = set()
    for f in hazira_findings:
        prefix = f["code"].split()[0]
        seen.add(prefix)
        assert prefix in codes, prefix
        assert codes[prefix]["level"] == f["level"], prefix
        assert codes[prefix]["subcategory"] == f["subcategory"], prefix
    assert seen == set().union(*HAZIRA_PREFIXES.values())


def test_hfacs_codes_shape():
    data = _json("hfacs-codes.json")
    assert sorted(data["levels"]) == ["1", "2", "3", "4"]
    for n, lv in data["levels"].items():
        assert lv["name"] == pmlc.LEVEL_NAMES[int(n)] and lv["definition"].strip()
    for prefix, p in data["prefixes"].items():
        assert re.fullmatch(r"[A-Z]{2,5}", prefix), prefix
        assert p["level"] in (1, 2, 3, 4) and p["subcategory"].strip() and p["plain"].strip()
        in_sample = prefix in HAZIRA_PREFIXES[p["level"]]
        assert p.get("seen_in_sample", True) is in_sample, prefix
    # the subcategory strings map 1:1 to prefixes
    subs = [p["subcategory"] for p in data["prefixes"].values()]
    assert len(subs) == len(set(subs))


def test_hfacs_levels_md_names_every_code():
    text = (REF / "hfacs-levels.md").read_text(encoding="utf-8")
    for prefix, p in _json("hfacs-codes.json")["prefixes"].items():
        assert f"`{prefix}`" in text and p["subcategory"] in text, prefix
    assert "Wiegmann & Shappell's HFACS, as adapted by ProbeMatrix" in text
    assert "HFMAP" in text


def test_glossary_min_terms():
    data = _json("glossary.json")
    assert data["version"] == 1
    terms = data["terms"]
    assert len(terms) >= 50
    for t in terms:
        assert set(t) == {"term", "definition", "do_not_translate", "translations"}, t
        assert t["term"].strip() and t["definition"].strip(), t
        assert isinstance(t["do_not_translate"], bool), t
        assert set(t["translations"]) == (set() if t["do_not_translate"] else {"hi"}), t   # OD4-1: Hindi
    folded = [t["term"].casefold() for t in terms]
    assert len(folded) == len(set(folded))
    missing = [w for w in L309_TERMS if w.casefold() not in folded]
    assert missing == []


def test_barriers_reference_names_every_barrier_state():
    text = (REF / "barriers-and-controls.md").read_text(encoding="utf-8")
    for state in pmlc_pack.BARRIER_STATES:
        assert f"`{state}`" in text, state
    for tier in pmlc.HOC_TIERS:
        assert f"`{tier}`" in text, tier
    for cue in ("review", "procedur", "checklist", "audit", "permit", "plan", "instruction", "sign"):
        assert f"`{cue}`" in text, cue


def test_indicators_reference_covers_l307():
    text = (REF / "indicators-and-effectiveness.md").read_text(encoding="utf-8").lower()
    for phrase in ("owner role", "data source", "numerator", "denominator", "threshold", "deterioration trigger",
                   "lead or lag", "gaming risk", "kirkpatrick", "communicated", "understood", "applied", "effective",
                   "30/60/90", "3/6/12", "lesson identified", "lesson learned", "single-loop", "double-loop",
                   "competence gap", "system problem"):
        assert phrase in text, phrase


def test_p4h_unverified_marked_source_line_only():
    rx = re.compile(r"API RP 754|HSG254|IOGP 456|Wiegmann")
    bad = []
    for name in NEW_MD:
        for n, line in enumerate((REF / name).read_text(encoding="utf-8").splitlines(), 1):
            if rx.search(line) and "(unverified)" not in line and not line.lstrip().startswith("Source:"):
                bad.append(f"{name}:{n}: {line}")
    assert bad == []


def test_p4h_new_references_use_no_blame_words_every_rule():
    rules = _json("lint-terms.json")["rules"]
    rxs = [re.compile(p, 0 if spec.get("case") == "sensitive" else re.I)
           for rid, spec in rules.items() if rid != "JC8" for p in spec["patterns"]]   # JC8 flags numbers, which these references must state
    hits = []
    for name in NEW_MD:
        for n, line in enumerate((REF / name).read_text(encoding="utf-8").splitlines(), 1):
            hits += [f"{name}:{n}: {m.group(0)}" for rx in rxs for m in rx.finditer(line)]
    for t in _json("glossary.json")["terms"]:
        hits += [f"glossary {t['term']}: {m.group(0)}" for rx in rxs for m in rx.finditer(t["definition"])]
    assert hits == []


def test_ontology_matches_taxonomy():
    text = (REF / "ontology.md").read_text(encoding="utf-8")
    tax = _json("taxonomy.json")
    for e in tax["entities"]:
        assert f"| {e['id']} | {e['name']} |" in text, e["id"]
    for r in tax["relations"] + [tax["default_relation"]]:
        assert f"`{r['id']}`" in text, r["id"]
    assert "higher level enables the lower" in text


REFS = REF

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
            assert {"id", "title", "verified"} <= set(r) <= {"id", "title", "verified", "topics", "source", "must_show"}, r
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
