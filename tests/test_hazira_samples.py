"""Hazira golden samples (L4-28, P4-27, OD4-4): the committed packs carry the Phase 4 fields, the Hindi variant
passes check-pack --strict, and every committed rendering (HTML, MD and the format showcases) is what the engine
writes from the committed JSON today. Re-render with SOURCE_DATE_EPOCH at the committed generated date; the HTML is
compared after the P4-27 date normalisation, the MD and the other text files byte for byte, the zips by part
contents."""
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone

import pytest

from test_pmlc import PMLC, ROOT, run
from pmlc_lib.samples import RENDER_PENDING

pytest.importorskip("openpyxl")
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
OUTPUTS = SAMPLE / "outputs"
REGISTER = OUTPUTS / "learnings-register.json"
# OD4-4: one showcase of each other document format: (command, pack, flags, files it contributes). "pack" runs
# `pmlc pack <ws> <pack> --out <dir> <flags>`; the other commands write their one file to `--out <dir>/<file>`.
SHOWCASES = [
    ("pack", "board-brief", ["--format", "docx", "--layout", "paper"], ["board-brief.docx", "board-brief.paper.docx"]),
    ("pack", "board-brief", ["--format", "email"], ["board-brief.email.html", "board-brief.email.txt"]),
    ("pack", "site-leadership-coach", ["--format", "pptx"], ["site-leadership-coach.pptx"]),
    ("pack", "frontline-learning-cards", ["--layout", "cards"], ["frontline-learning-cards.cards.html"]),
    ("pack", "training-designer", ["--format", "gift"], ["training-designer.gift.txt"]),
    ("pack", "causal-map", ["--format", "svg,graphml"], ["causal-map.causal-map.svg", "causal-map.causal-map.graphml"]),
    # Task 22 (OD5-1): pack writes the 9M map from the golden pack and the committed scripted session
    ("pack", "nine-m-analysis", [], ["nine-m-map.json"]),
    # Task 24: the Phase 5 formats and organisation files
    ("pack", "risk-register-update", ["--format", "risk-csv"], ["risk-register-update.risk-changes.csv"]),
    ("nine-m-actions-template", "nine-m-analysis", [], ["nine-m-analysis.actions-template.xlsx"]),
    ("pack-xlsx", "compliance-crosswalk", ["--kind", "table"], ["compliance-crosswalk.xlsx"]),
]
# Inputs committed beside the packs: the scripted 9M session the nine-m-analysis golden was written from (OD5-1),
# copied into the workspace as nine_m_session.json
SESSION_FILES = {"nine-m-session.json": "nine_m_session.json"}
REGISTER_FILES = {"learnings-register.json", "learnings-register.md", "learnings-register.xlsx",
                  "organisation-learning-map.html"}
DATE_RX = re.compile(r"generated \d{4}-\d{2}-\d{2}")


def _packs(pending=False):
    """The rendered pack JSONs in outputs/ (pending=True: the Phase 5 goldens still waiting for Task 24's render,
    `samples.RENDER_PENDING`; they are checked by each skill's own test until then)."""
    out = []
    for p in sorted(OUTPUTS.glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(d, dict) and "pack" in d and (p.name in RENDER_PENDING) == pending:
            out.append(p.stem)
    return out


PACKS = _packs()
# Phase 5: golden JSONs waiting for Task 24 to render them and list them in the README (pmlc_lib.samples)
PENDING = sorted(n[: -len(".json")] for n in RENDER_PENDING)
RENDERED = [p for p in PACKS if p not in PENDING]
README_PACK_ROW = re.compile(r"^\| `outputs/([a-z0-9-]+|dossier-F\d+)\.json`[^|]*\|[^|]*\|[^|]*\bpack JSON\b", re.M)


def readme_packs() -> list:
    """The pack JSONs the sample README lists (P5-1: the sample count is the README's, not a constant)."""
    return sorted(README_PACK_ROW.findall((SAMPLE / "README.md").read_text(encoding="utf-8")))


def _epoch() -> str:
    """SOURCE_DATE_EPOCH for the date the committed samples were generated on (P4-6)."""
    m = re.search(r"generated (\d{4}-\d{2}-\d{2})", (OUTPUTS / "board-brief.html").read_text(encoding="utf-8"))
    day = datetime.strptime(m.group(1), "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return str(int(day.timestamp()))


@pytest.fixture(scope="module")
def hz(tmp_path_factory):
    root = tmp_path_factory.mktemp("hazira-render")
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root),
        "--overlay", "india-process-site")
    ws = root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"
    for name in ("comparator.json", "comparison-map.json"):
        shutil.copy(SAMPLE / "comparator" / name, ws / name)
    for p in OUTPUTS.glob("*.json"):                     # the register, and the source of the Hindi variant
        shutil.copy(p, ws.parent / "outputs" / p.name)
    for name, ws_name in SESSION_FILES.items():
        shutil.copy(OUTPUTS / name, ws / ws_name)
    return ws


def _pack(ws, name, out, *flags, command="pack"):
    env = dict(os.environ, SOURCE_DATE_EPOCH=_epoch())
    r = subprocess.run([sys.executable, str(PMLC), command, str(ws), str(ws.parent / "outputs" / f"{name}.json"),
                        "--out", str(out), *flags], capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stdout + r.stderr


def _cells(path) -> dict:
    """An xlsx workbook's sheets and cell values: openpyxl stamps the save time into the package, so a fresh render
    is compared by content, not bytes."""
    import openpyxl
    wb = openpyxl.load_workbook(path)
    return {ws.title: [[c.value for c in row] for row in ws.iter_rows()] for ws in wb.worksheets}


def _parts(path) -> dict:
    with zipfile.ZipFile(path) as z:
        return {n: z.read(n) for n in z.namelist()}


def _same(new, old):
    if old.suffix in (".docx", ".pptx", ".zip"):
        assert _parts(new) == _parts(old), old.name
    elif old.suffix == ".xlsx":
        assert _cells(new) == _cells(old), old.name
    elif old.suffix == ".html":
        norm = [DATE_RX.sub("generated <date>", p.read_text(encoding="utf-8")) for p in (new, old)]
        assert norm[0] == norm[1], f"{old.name} differs from a fresh render"
    else:
        assert new.read_bytes() == old.read_bytes(), f"{old.name} differs from a fresh render"


def test_hazira_samples_hold_exactly_the_od4_4_files():
    want = set(REGISTER_FILES) | set(SESSION_FILES) | {f for _, _, _, files in SHOWCASES for f in files}
    want |= {f"{p}.{ext}" for p in RENDERED for ext in ("json", "html", "md")} | {f"{p}.json" for p in PENDING}
    assert {p.name for p in OUTPUTS.iterdir()} == want
    assert sorted(RENDERED) == readme_packs() and len(RENDERED) >= 25 and "frontline-learning-cards-hi" in PACKS


def test_hazira_samples_carry_phase_4_fields():
    packs = {p: json.loads((OUTPUTS / f"{p}.json").read_text(encoding="utf-8")) for p in PACKS}
    assert all(d.get("skill") for d in packs.values())
    assert all("handling" not in d for d in packs.values())       # drafts: the model never signs off (D7)
    items = {p: [it for s in d["sections"] for it in s["items"]] for p, d in packs.items()}
    fl = items["frontline-learning-cards"]
    assert sum(it["kind"] == "toolbox" for it in fl) == 2
    assert all(it.get("did_you_know") and it.get("what_you_can_do") for it in fl if it["kind"] == "card")
    assert all(it.get("injects") for it in items["emergency-response-learnings"] if it["kind"] == "scenario")
    assert sum(bool(it.get("type")) for it in items["training-designer"] if it["kind"] == "question") >= 6
    hi = packs["frontline-learning-cards-hi"]
    assert (hi["lang"], hi["translation_of"], hi["skill"]) == ("hi", "frontline-learning-cards",
                                                                "frontline-learning-cards")


def test_hazira_hindi_variant_passes_strict(hz):
    out = run("check-pack", str(hz), str(hz.parent / "outputs" / "frontline-learning-cards-hi.json"), "--strict",
              "--register", str(REGISTER))
    assert "OK:" in out, out
    html = (OUTPUTS / "frontline-learning-cards-hi.html").read_text(encoding="utf-8")
    assert "Translated with AI assistance: have a fluent speaker check it before use" in html


def test_hazira_samples_render_identically(hz, tmp_path):
    for name in RENDERED:
        out = tmp_path / name
        _pack(hz, name, out)
        for ext in ("html", "md"):
            _same(out / f"{name}.{ext}", OUTPUTS / f"{name}.{ext}")
    for n, (command, name, flags, files) in enumerate(SHOWCASES):
        out = tmp_path / f"showcase-{n}"
        if command == "pack":
            _pack(hz, name, out, *flags)
        else:                                       # one organisation file, written to the path given
            out.mkdir()
            _pack(hz, name, out / files[0], *flags, command=command)
        for f in files:
            _same(out / f, OUTPUTS / f)


def test_no_hazira_pack_waits_for_its_render():
    """Task 24: every Phase 5 golden is rendered beside its JSON and listed in the README, so the staging set is
    empty and check-samples holds every pack to the OD4-4 rule again."""
    assert RENDER_PENDING == frozenset() and PENDING == []
    assert len(RENDERED) == len(PACKS) == len(readme_packs()) >= 34


MANUAL = ROOT / "docs" / "manual"


def test_manual_hazira_counts_match_the_engine(hz, tmp_path):
    """Final review I3: the Hazira numbers the manual quotes for Phase 4 outputs are what the engine writes from the
    committed golden packs today (strings units, pptx slides, bow-tie barriers)."""
    out = run("strings", "extract", str(hz), str(hz.parent / "outputs" / "frontline-learning-cards.json"), "--lang",
              "hi", "--out", str(tmp_path / "fl.strings.xlf"))
    units = int(re.search(r"\((\d+) units, xliff, en -> hi\)", out).group(1))
    recipes = (MANUAL / "Workflows-and-recipes.md").read_text(encoding="utf-8")
    assert f"({units} units, xliff, en -> hi)" in (MANUAL / "commands" / "strings.md").read_text(encoding="utf-8")
    assert f"`strings extract` writes {units} units to translate" in recipes
    _pack(hz, "site-leadership-coach", tmp_path / "p", "--format", "pptx")
    slides = [n for n in _parts(tmp_path / "p" / "site-leadership-coach.pptx")
              if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]
    assert f"`site-leadership-coach.pptx` has {len(slides)} slides" in recipes
    _pack(hz, "barrier-learnings", tmp_path / "b", "--format", "bowtie-csv")
    rows = (tmp_path / "b" / "barrier-learnings.bowtie.csv").read_text(encoding="utf-8").splitlines()[1:]
    sides = [r.split(",", 1)[0] for r in rows]
    assert (f"has {len(rows)} barriers: {sides.count('threat')} on the threat side" in recipes
            and f"{sides.count('consequence')} on the consequence side" in recipes)
