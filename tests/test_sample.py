"""Tests on the committed Hazira sample (public record). Later tasks reuse the module fixture `hz`."""
import html
import json
import re
import shutil
import subprocess
import sys
import types
from pathlib import Path

import pytest

from test_pmlc import PMLC, ROOT, pmlc, run

pytest.importorskip("openpyxl")
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
REGISTER = SAMPLE / "outputs" / "learnings-register.json"
EXPECTED_JUSTIFICATION_ONLY = 56  # measured; matches the planning research figure
GOLDEN = Path(__file__).resolve().parent / "fixtures" / "roles-golden.json"


@pytest.fixture(scope="module")
def hz(tmp_path_factory):
    root = tmp_path_factory.mktemp("hazira")
    run("ingest", str(EXPORT), "--slug", "hazira-gas-release-fire", "--root", str(root))
    ws = root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"
    run("classify", str(ws), "--overlay", "india-process-site")

    def select(*args):
        return json.loads(run("select", str(ws), *args, "--format", "json"))

    return types.SimpleNamespace(
        ws=ws, select=select,
        clusters=json.loads((ws / "clusters.json").read_text(encoding="utf-8")),
        incident=json.loads((ws / "incident.json").read_text(encoding="utf-8")))


def test_baseline(hz):
    findings = json.loads((hz.ws / "findings.json").read_text(encoding="utf-8"))
    assert len(findings) == 436
    assert len(json.loads((hz.ws / "evidence.json").read_text(encoding="utf-8"))) == 46
    assert max(f["rating"] or 0 for f in findings) == 4
    assert len(hz.clusters["role_map"]) == 630
    assert len(hz.select("--entity", "F02", "F06")) == 196


def test_golden_roles(hz):
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    assert len(golden) >= 50
    rm = hz.clusters["role_map"]
    wrong = {r: ({k: rm[r][k] for k in "FTR"} if r in rm else None, want) for r, want in golden.items()
             if r not in rm or {k: rm[r][k] for k in "FTR"} != want}
    assert wrong == {}


def test_no_design_role_is_approver(hz):
    assert not [r for r, m in hz.clusters["role_map"].items() if "design" in r.lower() and m["R"] == "approver"]


def test_plant_policy_roles_are_t4(hz):
    roles = {r: m["T"] for r, m in hz.clusters["role_map"].items() if re.search(r"(?i)plant manag.*polic", r)}
    assert roles and set(roles.values()) == {"T4"}, roles


def test_register_still_clean(hz):
    r = subprocess.run([sys.executable, str(PMLC), "check-register", str(hz.ws), str(REGISTER)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "; 0 problem(s)." in r.stdout


def test_select_by_tag_on_hazira(hz):
    emergency = {d["id"] for d in hz.select("--tag", "emergency")}
    assert emergency == {d["id"] for d in hz.select("--entity", "F09a", "F09b", "F10")}
    assert hz.clusters["taxonomy"]["overlays"] == ["india-process-site"]


def test_entity_mode_all_is_intersection(hz):
    assert len(hz.select("--entity", "F02", "F06")) == 196
    assert len(hz.select("--entity", "F02", "F06", "--entity-mode", "all")) == 27


def test_budget_truncates_by_rating(hz):
    r = subprocess.run([sys.executable, str(PMLC), "select", str(hz.ws), "--tier", "T2", "--budget-chars", "60000"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert len(r.stdout) <= 60000
    ratings = [int(x) for x in re.findall(r"· rating (\d+)", r.stdout)]
    assert ratings and ratings == sorted(ratings, reverse=True)
    m = re.search(r"Dropped for budget: (\d+) findings", r.stdout)
    assert m and int(m.group(1)) > 0
    assert len(ratings) + int(m.group(1)) == len(hz.select("--tier", "T2"))


def _preset(hz, *extra):
    r = subprocess.run([sys.executable, str(PMLC), "select", str(hz.ws), "--preset", "site-leadership-coach", *extra],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r


def test_preset_budget_is_shared_across_calls(hz):                                  # ruling 27
    floor = _preset(hz, "--budget-chars", "0")
    parts = re.split(r"(?m)^(?=# Preset site-leadership-coach: )", floor.stdout)[1:]
    assert len(parts) == 4 and "below the minimum output" in floor.stderr        # Task 22 added culture-oic
    min_len = max(len(x) for x in parts)
    capped = _preset(hz, "--budget-chars", "20000").stdout
    uncapped = _preset(hz).stdout
    assert len(capped) < 20000 + len(parts) * min_len
    assert len(uncapped) > 5 * 20000


def test_analysis_stats_cross_check(hz):
    st = hz.incident["analysis_stats"]
    assert st["total"] == 436
    assert {int(k): v for k, v in st["by_level"].items()} == {1: 36, 2: 92, 3: 167, 4: 141}


def test_export_schema_doc_matches_sample(hz):
    import openpyxl
    wb = openpyxl.load_workbook(EXPORT, read_only=True)
    for sheet, known in pmlc.KNOWN_COLUMNS.items():
        header = [c for c in next(wb[sheet].iter_rows(values_only=True)) if c]
        assert header == known, sheet
    doc = (ROOT / "skills" / "learnings-coach" / "references" / "export-schema.md").read_text(encoding="utf-8")
    for name in [c for cols in pmlc.KNOWN_COLUMNS.values() for c in cols] + pmlc.KNOWN_SUMMARY_FIELDS:
        assert name in doc, name
    assert set(hz.incident["fields"]) <= set(pmlc.KNOWN_SUMMARY_FIELDS)


def test_event_day_sequence(hz):
    run("timeline", str(hz.ws), "--on", "incident")
    seq = json.loads((hz.ws / "timeline_event_day.json").read_text(encoding="utf-8"))
    times = [x["time"] for x in seq]
    assert times == sorted(times) and {"02:12", "03:01", "03:08"} <= set(times)
    assert len(times) == len(set(times)) and len(seq) < 60
    assert all((x["sources"] or x.get("narrative")) and 1 <= len(x["snippets"]) <= 3 and x["mentions"] >= len(x["sources"])
               for x in seq)                  # A53: a narrative-only time has no citable ID, so it is flagged
    e308 = next(x for x in seq if x["time"] == "03:08")
    assert e308["mentions"] > 1 and len(e308["sources"]) > 1


def test_event_day_other_day_keeps_only_dated_times(hz):                            # ruling 26
    run("timeline", str(hz.ws), "--on", "2019-01-01")
    seq = json.loads((hz.ws / "timeline_event_day.json").read_text(encoding="utf-8"))
    assert seq == []                             # no Hazira sentence dated 2019-01-01 gives a clock time
    run("timeline", str(hz.ws), "--on", "incident")
    assert len(json.loads((hz.ws / "timeline_event_day.json").read_text(encoding="utf-8"))) == 29


def test_min_precision_month_drops_years(hz):
    run("timeline", str(hz.ws), "--min-precision", "month")
    t = json.loads((hz.ws / "timeline_candidates.json").read_text(encoding="utf-8"))
    assert t and all(x["precision"] != "year" for x in t)
    assert all("months_before" in x for x in t)


def test_justification_only_links_count(hz):
    w = pmlc.load_ws(hz.ws)
    only = sum(len(pmlc.linked_evidence(f) - set(f["evidence"])) for f in w["findings"])
    # Measured on the committed export (planning research estimated 56); pairs named only in AI Justification.
    assert only > 0
    assert only == EXPECTED_JUSTIFICATION_ONLY
    r = subprocess.run([sys.executable, str(PMLC), "check-register", str(hz.ws), str(REGISTER)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_sample_register_vocab(hz, capsys):
    r = subprocess.run([sys.executable, str(PMLC), "check-register", str(hz.ws), str(REGISTER)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    warns = [ln for ln in r.stdout.splitlines() if ln.startswith("warning: ")]
    # A28: the language-check warnings are exactly the two calibrated JC6 ones, not merely "some warnings"
    jc = [ln for ln in warns if " JC" in ln]
    assert len(jc) == 2 and all("JC6" in ln for ln in jc), jc
    assert any(ln.startswith("warning: entries[7].recommendations: JC6") for ln in jc)
    assert any(ln.startswith("warning: entries[11].recommendations: JC6") for ln in jc)
    with capsys.disabled():
        print(f"\nHazira vocabulary warnings: {len(warns)}")


def test_hazira_register_lint_calibration(hz):
    import time
    import pmlc_lint
    w = pmlc.load_ws(hz.ws)
    reg = json.loads(REGISTER.read_text(encoding="utf-8"))
    t0 = time.perf_counter()
    hits = pmlc_lint.lint(reg, w, kind="register")
    took = time.perf_counter() - t0
    report = pmlc_lint.format_hits(hits)
    assert [h for h in hits if h.severity == "error"] == [], report
    assert len([h for h in hits if h.severity == "warning"]) == 2 and len(hits) == 2, report
    assert took < 2, took
    assert reg["status"].startswith("Learning purposes: not a statutory document; draft")
    r = subprocess.run([sys.executable, str(PMLC), "check-language", str(hz.ws), str(REGISTER)],
                       capture_output=True, text=True)
    assert r.returncode == 0 and r.stdout.strip().splitlines()[-1].startswith("check-language: 0 errors, 2 warnings"), r.stdout
    md = (SAMPLE / "outputs" / "learnings-register.md").read_text(encoding="utf-8").splitlines()
    assert md[2] == "*" + reg["status"] + "*"


# ----------------------------------------------------------------------------- Task 7: the 2-card print budget

PRINT_2_CARD = Path(__file__).resolve().parent / "fixtures" / "hazira" / "print-2-card.json"
CHROME = next((shutil.which(x) for x in ("google-chrome", "chromium", "chromium-browser") if shutil.which(x)), None)


@pytest.fixture(scope="module")
def two_card(hz, tmp_path_factory):
    out = tmp_path_factory.mktemp("two-card")
    for mode in ("cited", "summary"):
        run("pack", str(hz.ws), str(PRINT_2_CARD), "--out", str(out / mode), "--embed", mode)
    pack = json.loads(PRINT_2_CARD.read_text(encoding="utf-8"))
    return types.SimpleNamespace(pack=pack, out=out,
                                 html=(out / "cited" / "frontline-learning-cards.html"),
                                 summary=(out / "summary" / "frontline-learning-cards.html"))


def test_hazira_2_card_fixture_passes_check_pack(hz):
    r = subprocess.run([sys.executable, str(PMLC), "check-pack", str(hz.ws), str(PRINT_2_CARD)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    pack = json.loads(PRINT_2_CARD.read_text(encoding="utf-8"))
    cards = [it for s in pack["sections"] for it in s["items"] if it["kind"] == "card"]
    assert len(cards) == 2 and pack["scope"] == {"tiers": ["T1"]} and pack["pack"] == "frontline-learning-cards"
    assert all(c.get("organisation_changing") and c.get("why_made_sense") for c in cards)


def test_hazira_2_card_print_budget(two_card):
    import pmlc_pack as pp
    raw = two_card.html.read_bytes()
    assert len(raw) < 200_000, len(raw)
    t = raw.decode("utf-8")
    trail = re.search(r'<section class="trail">(.*?)</section>', t, re.S).group(1)
    fids, eids = pp.cited_ids(two_card.pack)
    assert re.findall(r"<dt>([^<]+)</dt>", trail) == fids + eids
    assert '<p class="printonly">2 of 227 relevant findings cited</p>' in t


def test_hazira_2_card_summary_leaks_no_quotes(hz, two_card):
    """Review Focus 5 on real data: no evidence description or Specific Reference of a cited record anywhere."""
    import pmlc_pack as pp
    t = two_card.summary.read_text(encoding="utf-8")
    ev = json.loads((hz.ws / "evidence.json").read_text(encoding="utf-8"))
    findings = {f["id"]: f for f in json.loads((hz.ws / "findings.json").read_text(encoding="utf-8"))}
    fids, eids = pp.cited_ids(two_card.pack)
    linked = [x for f in fids for x in findings[f]["evidence"]]
    quotes = [ev[x]["description"] for x in dict.fromkeys(eids + linked) if x in ev]
    quotes += [ln["reference"] for x in dict.fromkeys(eids + linked) if x in ev for ln in ev[x]["links"] if ln["reference"]]
    assert quotes
    forms = lambda q: (q, json.dumps(q, ensure_ascii=False)[1:-1], html.escape(q), html.escape(q, quote=False),   # noqa: E731
                       pmlc.embed_json(q)[1:-1])
    escaped = [q for q in quotes if q and any(f in t for f in forms(q))]
    assert escaped == []


@pytest.mark.skipif(not CHROME, reason="no headless Chrome or Chromium")
def test_hazira_2_card_prints_4_pages_or_fewer(two_card, tmp_path):
    pdf = tmp_path / "two-card.pdf"
    r = subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf}", two_card.html.as_uri()], capture_output=True, text=True, timeout=120)
    assert pdf.exists(), r.stderr
    if shutil.which("pdfinfo"):
        info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
        pages = int(re.search(r"^Pages:\s+(\d+)", info, re.M).group(1))
    else:
        pages = len(re.findall(rb"/Type\s*/Page(?!s)", pdf.read_bytes()))
    assert 1 <= pages <= 4, pages


def test_share_refused_on_hazira_draft(hz, tmp_path):
    """P2-7: the Hazira investigation is in progress, so no copy of it can leave the organisation, even with a
    handling block typed in that claims approval, clearance and an external classification."""
    doc = json.loads(PRINT_2_CARD.read_text(encoding="utf-8"))
    doc["handling"] = {"status": "approved", "reviewer_role": "HSE manager", "reviewed_on": "2026-10-19",
                       "classification": "public", "legal_review": "cleared"}
    doc["handling"]["content_hash"] = pmlc.content_hash(doc)
    p = tmp_path / "cards.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    out = tmp_path / "out"
    for mode, word in (("external", "externally"), ("public", "publicly")):
        r = subprocess.run([sys.executable, str(PMLC), "pack", str(hz.ws), str(p), "--share", mode, "--out", str(out)],
                           capture_output=True, text=True)
        assert r.returncode == 1
        last = r.stderr.strip().splitlines()[-1]
        assert last.startswith(f"cannot share {word}: review is draft (the investigation status is in progress"), last
        assert not out.exists() or not any(out.iterdir())


def test_smoke_run_checks_language():
    """tools/smoke_sample.py (the CI smoke job) also runs check-language on the sample register: 0 errors."""
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "smoke_sample.py")], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip().splitlines()[-1] == ("smoke OK: 436 findings, 46 evidence, register 0 problems, "
                                                 "language 0 errors")
