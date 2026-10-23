"""Task 5 (spec §7.3, §7.6; D9): the 9M references and the nine-m-seed command. Synthetic exports only (fictional
event, no real data); the Hazira numbers are in test_calibration_p5.py."""
import json
import re
import subprocess
import sys

import pytest

from test_pmlc import PMLC, make_export, make_thin_export, run, run_fail
import pmlc  # noqa: E402,F401
from pmlc_lib import ninem  # noqa: E402

openpyxl = pytest.importorskip("openpyxl")

# The 97 subcategory names, copied from docs/superpowers/local-tools/phase-5/ninem.md (the D9 port list).
NAMES = {
    "M1": ("Manpower/Mindpower", [
        "Selection and Qualification", "Training Programme Design and Delivery",
        "Competence Assessment and Authorisation", "Workload Management", "Fatigue Risk Management",
        "Cognitive Readiness and Situational Awareness", "Psychological Readiness and Support",
        "Communication and Coordination", "Team Dynamics", "Leadership and Authority Gradient",
        "Cultural and Organisational Climate", "Error Propensity and Human Limitations",
        "Competence Sustainability and Continuous Improvement"]),
    "M2": ("Medium", [
        "Physical Environment Controls", "Workspace Ergonomics and Human Fit", "Noise and Auditory Environment",
        "Visual Environment and Legibility", "Localised Hazards and Exposure", "Operational Environment and Tempo",
        "Psychological Environment and Stressors", "Cultural Environment and Norms",
        "Environmental Stressors and Extreme Conditions", "External Environment and Stakeholders",
        "Infrastructure, Access, and Traffic Interfaces", "Emergency Preparedness in Environmental Contexts"]),
    "M3": ("Method", [
        "Procedure Design and Development", "Standard Operating Procedures (SOPs)", "Compliance and Adherence",
        "Flexibility and Adaptability", "Documentation and Communication", "Risk Management Integration",
        "Alignment with Technology", "Emergency and Contingency Procedures", "Continuous Improvement",
        "Simplicity and Accessibility"]),
    "M4": ("Mission", [
        "Strategic Objectives and Priorities", "Operational Goals and Targets", "Resource Allocation",
        "Leadership and Accountability", "Risk Tolerance and Decision-Making",
        "External Influences and Stakeholder Expectations", "Mission Complexity and Clarity",
        "Organisational Culture and Mission Alignment", "Communication and Mission Integration",
        "Continuous Evaluation and Improvement"]),
    "M5": ("Measurement", [
        "Metrics Design and Relevance", "Data Collection and Accuracy", "Monitoring and Reporting Systems",
        "Analysis and Interpretation", "Feedback Loops", "Benchmarking and Comparisons",
        "Predictive Analytics and Risk Indicators", "Communication of Measurements",
        "Continuous Improvement through Measurement", "Integration with Technology", "Audits and Inspections"]),
    "M6": ("Management/Money", [
        "Strategic Financial Planning", "Leadership and Decision-Making", "Budgeting and Resource Allocation",
        "Training and Development Investments", "Risk Management and Compliance",
        "Investment in Infrastructure and Technology", "Performance Monitoring and Accountability",
        "Stakeholder Engagement and Communication", "Financial Controls and Auditing",
        "Continuous Improvement and Adaptability"]),
    "M7": ("Machine", [
        "Design and Suitability", "Maintenance and Reliability", "Integration and Compatibility",
        "Automation and Control Systems", "Ergonomics and Usability", "Monitoring and Diagnostics",
        "Safety Features and Risk Mitigation", "Lifecycle Management", "Environmental Impact and Sustainability",
        "Training and Competence"]),
    "M8": ("Material", [
        "Material Quality", "Material Availability and Supply Chain", "Material Compatibility",
        "Storage and Handling", "Material Waste and Sustainability", "Material Cost Management",
        "Compliance and Regulatory Requirements", "Material Traceability", "Innovation and Material Advancements",
        "Emergency and Contingency Planning"]),
    "M9": ("Maintenance", [
        "Preventive Maintenance Programme", "Predictive Maintenance and Condition Monitoring",
        "Corrective Maintenance Execution", "Maintenance Planning and Scheduling",
        "Maintenance Personnel Competence", "Maintenance Documentation and Records",
        "Spare Parts and Inventory Management", "Maintenance Technology and Tools",
        "Software and Control System Maintenance", "Safety in Maintenance Activities",
        "Continuous Improvement in Maintenance"]),
}
ABOUT = ("Derived from the ProbeMatrix 9M framework (Eyekyam). Action catalogues remain in the ProbeMatrix "
         "CAPA Zone.")
REAL_CODES = {"AB 1.1": "ASBE 1.3", "SV 1.4": "SVI 1.4", "OR 2.2": "OIR 1.6", "PE 2.1": "PTE 2.2"}


def real_prefix_export(d):
    """The synthetic export with its four invented Nanocodes swapped for codes whose prefixes ProbeMatrix emits."""
    x = make_export(d, name="real-prefix.xlsx")
    wb = openpyxl.load_workbook(x)
    for sheet, col in (("Identified Findings", 2), ("Evidence Links", 1)):
        s = wb[sheet]
        for r in range(2, s.max_row + 1):
            v = s.cell(r, col).value
            if v in REAL_CODES:
                s.cell(r, col).value = REAL_CODES[v]
    wb.save(x)
    return x


@pytest.fixture(scope="module")
def rws(tmp_path_factory):
    d = tmp_path_factory.mktemp("ninem")
    x = real_prefix_export(d)
    run("ingest", str(x), "--legacy-out", str(d / "ws"))
    run("classify", str(d / "ws"))
    return d / "ws"


# --- the references ------------------------------------------------------------------------------------------

def test_nine_m_names():
    nm = ninem.load_nine_m()
    assert [c["code"] for c in nm["chapters"]] == [f"M{i}" for i in range(1, 10)]
    assert [len(c["subcategories"]) for c in nm["chapters"]] == [13, 12, 10, 10, 11, 10, 10, 10, 11]
    for c in nm["chapters"]:
        title, names = NAMES[c["code"]]
        assert c["title"] == title
        assert [s["name"] for s in c["subcategories"]] == names
        assert [s["id"] for s in c["subcategories"]] == [f"{c['code']}.{i:02d}" for i in range(1, len(names) + 1)]
    assert sum(len(c["subcategories"]) for c in nm["chapters"]) == 97


def test_nine_m_ip_shape():
    nm = ninem.load_nine_m()
    assert set(nm) == {"_about", "version", "chapters"}
    assert nm["_about"] == ABOUT and nm["version"] == 1
    banned = re.compile(r"action|signal|indicator|checklist|prompt", re.I)

    def keys(o):
        if isinstance(o, dict):
            for k, v in o.items():
                yield k
                yield from keys(v)
        elif isinstance(o, list):
            for v in o:
                yield from keys(v)
    assert not [k for k in keys(nm) if banned.search(k)]
    for c in nm["chapters"]:
        assert set(c) == {"code", "title", "definition", "subcategories"}
        assert 0 < len(c["definition"].split()) <= 30, c["code"]
        for s in c["subcategories"]:
            assert set(s) == {"id", "name", "definition", "probes"}
            assert 0 < len(s["definition"].split()) <= 30, s["id"]
            assert len(s["probes"]) == 3 and len(set(s["probes"])) == 3, s["id"]
            assert all(p.endswith("?") and p.strip() == p for p in s["probes"]), s["id"]
    texts = [c["definition"] for c in nm["chapters"]] + [x for c in nm["chapters"] for s in c["subcategories"]
                                                         for x in [s["definition"], *s["probes"]]]
    assert len(texts) == len(set(texts))          # each line written for its own place


def test_nine_m_md_reader_page():
    md = (ninem.REFS / "nine-m.md").read_text(encoding="utf-8")
    pos = [md.index(f"M{i} ") for i in range(1, 10)]
    assert pos == sorted(pos)                     # the order M1 -> M9
    for t in ("Maintenance and Reliability", "Training and Competence", "Training and Development Investments",
              "M1 is not the people M", "Action catalogues remain in the ProbeMatrix CAPA Zone", "double-count"):
        assert t in md, t


def test_nine_m_map_shape():
    mp = ninem.load_map()
    assert set(mp) == {"_about", "version", "prefixes", "codes", "keywords", "entities"}
    codes = json.loads((ninem.REFS / "hfacs-codes.json").read_text(encoding="utf-8"))["prefixes"]
    assert set(mp["prefixes"]) == set(codes)      # every prefix ProbeMatrix emits has a default (P5-12)
    ms = {f"M{i}" for i in range(1, 10)}
    for v in list(mp["prefixes"].values()) + list(mp["codes"].values()):
        assert v["primary"] in ms and set(v["secondary"]) <= ms - {v["primary"]}
    for c in mp["codes"]:
        assert re.fullmatch(r"[A-Z]{2,4} \d\.\d{1,2}", c) and c.split()[0] in codes, c
    assert set(mp["keywords"]) == ms and set(mp["entities"]) == ms
    for rx in (r for v in mp["keywords"].values() for r in v):
        re.compile(rx)
    assert mp["keywords"]["M8"] and mp["keywords"]["M9"]


def test_load_map_refuses_a_bad_map(tmp_path):
    p = tmp_path / "bad-map.json"
    p.write_text(json.dumps({"version": 1, "prefixes": {"SVI": {"primary": "M10", "secondary": []}}, "codes": {},
                             "keywords": {}, "entities": {}}), encoding="utf-8")
    with pytest.raises(SystemExit, match="M10"):
        ninem.load_map(p)


# --- scoring -------------------------------------------------------------------------------------------------

TINY_MAP = {"version": 7, "prefixes": {"TST": {"primary": "M3", "secondary": ["M6"]}},
            "codes": {"TST 9.9": {"primary": "M7", "secondary": []}},
            "keywords": {"M8": [r"\bgaskets?\b"], "M3": [r"\bprocedure\b"]}, "entities": {"M9": ["F02"]}}


def tiny_ws(*findings, ents=None):
    F = [dict({"level": 2, "rating": 3, "label": "", "short": "", "name": "Test code"}, **f) for f in findings]
    cl = {"findings": {f["id"]: {"F": (ents or {}).get(f["id"], ["F99"]), "T": [], "R": []} for f in F}}
    return {"findings": F, "clusters": cl}


def test_seed_weights():
    w = tiny_ws({"id": "FND-1", "code": "TST 1.1", "label": "Gasket swapped"}, ents={"FND-1": ["F02"]})
    s = ninem.seed(w, TINY_MAP)
    f = s["findings"]["FND-1"]
    assert f["scores"] == {"M3": 3, "M6": 1, "M8": 1, "M9": 1}       # primary 3, secondary 1, keyword 1, entity 1
    assert f["m_primary"] == "M3" and f["m_secondary"] == ["M6"]
    assert s["map_version"] == 7 and s["unmapped"] == []
    # a keyword hit for the primary M adds to it; a code override wins over the prefix default
    w = tiny_ws({"id": "FND-2", "code": "TST 1.2", "short": "The procedure was unclear"},
                {"id": "FND-3", "code": "TST 9.9", "label": "gaskets and procedure"}, ents={"FND-3": ["F02"]})
    s = ninem.seed(w, TINY_MAP)
    assert s["findings"]["FND-2"]["scores"] == {"M3": 4, "M6": 1}
    f3 = s["findings"]["FND-3"]
    assert f3["m_primary"] == "M7" and f3["scores"] == {"M3": 1, "M7": 3, "M8": 1, "M9": 1}
    assert f3["m_secondary"] == []


def test_seed_two_signals_make_a_secondary():
    w = tiny_ws({"id": "FND-1", "code": "TST 9.9", "label": "gasket"}, ents={"FND-1": ["F02"]})
    mp = dict(TINY_MAP, entities={"M8": ["F02"]})
    f = ninem.seed(w, mp)["findings"]["FND-1"]
    assert f["scores"] == {"M7": 3, "M8": 2} and f["m_secondary"] == ["M8"]


def test_seed_profile_counts_primary():
    w = tiny_ws({"id": "FND-1", "code": "TST 1.1", "level": 3, "rating": 4},
                {"id": "FND-2", "code": "TST 1.1", "level": 4, "rating": 2},
                {"id": "FND-3", "code": "TST 9.9", "level": 2, "rating": 4})
    p = ninem.seed(w, TINY_MAP)["profile"]
    assert list(p) == [f"M{i}" for i in range(1, 10)]
    assert p["M3"]["findings"] == 2 and p["M3"]["by_level"] == {"1": 0, "2": 0, "3": 1, "4": 1}
    assert p["M3"]["top_rated"] == 1 and p["M3"]["top_findings"] == ["FND-1", "FND-2"]
    assert p["M3"]["top_codes"] == [{"code": "TST 1.1", "n": 2, "name": "Test code"}]
    assert p["M7"]["findings"] == 1 and p["M1"] == {"findings": 0, "by_level": {"1": 0, "2": 0, "3": 0, "4": 0},
                                                    "top_rated": 0, "top_codes": [], "top_findings": []}


def test_seed_unknown_prefix_is_unmapped_not_a_crash():
    w = tiny_ws({"id": "FND-1", "code": "ZZ 1.1", "label": "gasket"}, {"id": "FND-2", "code": "TST 1.1"})
    s = ninem.seed(w, TINY_MAP)
    assert s["unmapped"] == ["FND-1"]
    assert s["findings"]["FND-1"] == {"m_primary": None, "m_secondary": [], "scores": {"M8": 1}}
    assert any("ZZ" in n for n in s["notes"])


def test_seed_all_mapped_synthetic(rws):
    out = run("nine-m-seed", str(rws))
    s = json.loads((rws / "nine_m_seed.json").read_text(encoding="utf-8"))
    assert s["unmapped"] == [] and len(s["findings"]) == 4
    assert {k: v["m_primary"] for k, v in s["findings"].items()} == {
        "FND-0001": "M3", "FND-0002": "M3", "FND-0003": "M9", "FND-0004": "M7"}
    assert s["findings"]["FND-0003"]["scores"]["M8"] >= 2                 # seals bought locally: a material signal
    assert "| M8 | Material |" in out and "Unmapped: none" in out
    assert s["version"] == 1 and s["map_version"] == ninem.load_map()["version"]


def test_seed_deterministic(rws, tmp_path):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    o1 = run("nine-m-seed", str(rws), "--out", str(a))
    o2 = run("nine-m-seed", str(rws), "--out", str(b))
    assert a.read_bytes() == b.read_bytes() and o1.replace(str(a), "") == o2.replace(str(b), "")
    text = a.read_text(encoding="utf-8")
    assert text == json.dumps(json.loads(text), sort_keys=True, indent=1, ensure_ascii=False)


def test_seed_recorded_for_status(rws):
    run("nine-m-seed", str(rws))
    m = json.loads((rws / "manifest.json").read_text(encoding="utf-8"))
    assert set(m["files"]["nine_m_seed.json"]["inputs"]) == {"findings.json", "clusters.json"}
    st = json.loads(run("status", str(rws), "--json"))
    assert {f["file"]: f["state"] for f in st["files"]}["nine_m_seed.json"] == "current"


def test_seed_custom_map(rws, tmp_path):
    mp = dict(ninem.load_map(), version=99)
    p = tmp_path / "my-map.json"
    p.write_text(json.dumps(mp), encoding="utf-8")
    run("nine-m-seed", str(rws), "--map", str(p), "--out", str(tmp_path / "s.json"))
    assert json.loads((tmp_path / "s.json").read_text(encoding="utf-8"))["map_version"] == 99


def test_seed_thin_export(tmp_path):
    """Review Focus 3: no clusters, no evidence sheet, invented prefixes: exit 0, unmapped listed, a note."""
    x = make_thin_export(tmp_path)
    run("ingest", str(x), "--legacy-out", str(tmp_path / "ws"))
    out = run("nine-m-seed", str(tmp_path / "ws"))
    s = json.loads((tmp_path / "ws" / "nine_m_seed.json").read_text(encoding="utf-8"))
    assert s["unmapped"] == ["FND-0001", "FND-0002", "FND-0003", "FND-0004"]
    assert any("classify" in n for n in s["notes"]) and any("AB" in n for n in s["notes"])
    assert "Unmapped: 4" in out
    x = make_export(tmp_path, name="fake.xlsx")      # the invented AB/SV/OR/PE prefixes, with clusters
    run("ingest", str(x), "--legacy-out", str(tmp_path / "ws2"))
    run("classify", str(tmp_path / "ws2"))
    run("nine-m-seed", str(tmp_path / "ws2"))


def test_seed_refuses_capa_planner(capa_planner_xlsx):
    assert ninem.is_capa_planner(capa_planner_xlsx)
    r = subprocess.run([sys.executable, str(PMLC), "nine-m-seed", str(capa_planner_xlsx)], capture_output=True,
                       text=True)
    assert r.returncode == 2
    assert r.stderr.strip() == ("This is a ProbeMatrix CAPA Planner workbook. nine-m-analysis reads the findings "
                                "export only (Identified Findings); export that instead.")
    assert "Traceback" not in r.stderr


def test_seed_refuses_a_findings_export_and_a_missing_folder(tmp_path):
    x = make_export(tmp_path)
    assert not ninem.is_capa_planner(x) and not ninem.is_capa_planner(tmp_path / "nope.xlsx")
    r = subprocess.run([sys.executable, str(PMLC), "nine-m-seed", str(x)], capture_output=True, text=True)
    assert r.returncode == 2 and "setup" in r.stderr and "Traceback" not in r.stderr
    r = run_fail("nine-m-seed", str(tmp_path / "no-such-ws"))
    assert "Traceback" not in r.stderr


def test_none_constant():
    assert ninem.NINE_M_NONE == "None / unknown (record as a gap)"
