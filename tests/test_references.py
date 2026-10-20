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
        assert isinstance(t["do_not_translate"], bool) and t["translations"] == {}, t
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


def test_unverified_marked():
    rx = re.compile(r"API RP 754|HSG254|IOGP 456|Wiegmann")
    bad = []
    for name in NEW_MD:
        for n, line in enumerate((REF / name).read_text(encoding="utf-8").splitlines(), 1):
            if rx.search(line) and "(unverified)" not in line and not re.search(r"\bsource:", line, re.I):
                bad.append(f"{name}:{n}: {line}")
    assert bad == []


def test_new_references_use_no_blame_words():
    rules = _json("lint-terms.json")["rules"]
    rxs = [re.compile(p, re.I) for p in rules["JC2"]["patterns"]]
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
