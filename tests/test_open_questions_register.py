"""Phase 5, Task 15: the open-questions-register skill. Its manifest, and the Hazira golden pack: it passes
check-pack --strict against the sample register with no language errors, its numbers and questions are the engine's
(`open-questions`), its other-pack questions are the gaps the sample packs record, and the CSV it hands over has one
row per finding. Public Hazira sample and synthetic data only."""
import json
import re
import shutil

import pytest

from test_exports import rows_of
from test_pmlc import ROOT, run
import pmlc  # noqa: E402
from pmlc_lib import samples as SAMPLES

pytest.importorskip("openpyxl")
SKILL = "open-questions-register"
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
OUTPUTS = SAMPLE / "outputs"
REGISTER = OUTPUTS / "learnings-register.json"
GOLDEN = OUTPUTS / f"{SKILL}.json"


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def section(pack, sid):
    return next(s for s in pack["sections"] if s["id"] == sid)


@pytest.fixture(scope="module")
def hz(tmp_path_factory):
    """A Hazira workspace with the sample register, and open_questions.json written."""
    root = tmp_path_factory.mktemp("hazira-oqr")
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root),
        "--overlay", "india-process-site")
    ws = root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"
    shutil.copy(REGISTER, ws.parent / "outputs" / REGISTER.name)
    run("open-questions", str(ws))
    return ws


def test_manifest_as_planned():
    m = load(ROOT / "skills" / SKILL / "skill.json")
    assert (m["kind"], m["audiences"], m["since"], m["embed_default"], m["share_default"]) == \
        ("analysis", [], "2.0.0", "cited", "internal")
    assert m["requires"] == ["workspace", "open-questions"]
    assert m["optional_inputs"] == ["gaps", "evidence-audit"]
    assert m["produces"] == {"pack": SKILL, "files": []}


def test_golden_passes_strict_with_the_register(hz):
    out = run("check-pack", str(hz), str(GOLDEN), "--strict", "--register", str(REGISTER))
    assert "OK:" in out, out
    lang = run("check-language", str(hz), str(GOLDEN))
    assert "check-language: 0 errors" in lang, lang


def test_golden_questions_are_the_engine_items(hz):
    """The questions section is `open-questions --items`, pasted unchanged."""
    items = json.loads(run("open-questions", str(hz), "--items"))
    assert section(load(GOLDEN), "questions")["items"] == items


def test_golden_tables_and_summary_follow_the_engine(hz):
    oq = load(hz / "open_questions.json")
    pack = load(GOLDEN)
    cols = section(pack, "follow-up-columns")["items"]
    assert len(cols) == 1 and [r[0] for r in cols[0]["rows"]] == oq["empty_follow_up_columns"]
    items = json.loads(run("open-questions", str(hz), "--items"))
    src = {}
    for it in items:
        if it.get("cites"):
            continue
        quoted = re.findall(r"'([^']+)'", it["question"])
        assert quoted, f"engine question no longer quotes the column name: {it['question']!r}"
        src[quoted[0]] = it["good_evidence"]
    assert {r[0]: r[2] for r in cols[0]["rows"]} == src
    fields = section(pack, "summary-fields")["items"][0]
    got = [x for r in fields["rows"] for x in r[1].split(", ")]
    assert sorted(got) == sorted(oq["blank_summary_fields"]) and len(got) == len(set(got))
    text = " ".join(it["text"] for it in section(pack, "summary")["items"])
    n = len(pmlc.load_ws(hz)["findings"])
    for x in (f"{len(oq['absence'])} of the {n}", f"{len(oq['hedged'])}",
              f"{len(oq['blank_summary_fields'])} of {oq['summary_fields']}"):
        assert x in text, x


def test_golden_other_pack_questions_are_the_sample_gaps():
    """Each from-other-packs question carries one gap a sample pack records: its cites and evidence_needed, and the
    pack named in `why`."""
    gaps = []
    for p in sorted(OUTPUTS.glob("*.json")):
        d = load(p)
        if isinstance(d, dict) and d.get("pack") and d["pack"] != SKILL:
            gaps += [(d["pack"], tuple(g.get("cites") or []), g["evidence_needed"]) for g in d.get("gaps") or []]
    got = [(tuple(it["cites"]), it["good_evidence"], it["why"]) for it in section(load(GOLDEN), "from-other-packs")["items"]]
    assert sorted((c, e) for c, e, _ in got) == sorted((c, e) for _, c, e in gaps)
    by = {(c, e): p for p, c, e in gaps}
    assert all(f"`{by[(c, e)]}`" in why or by[(c, e)] in why for c, e, why in got)


def test_golden_hand_over_csv(hz, tmp_path):
    """The rendered pack writes open-questions-follow-up.csv: one row per cited finding, in the export's columns."""
    run("pack", str(hz), str(GOLDEN), "--out", str(tmp_path))
    rows = rows_of((tmp_path / "open-questions-follow-up.csv").read_text(encoding="utf-8"))
    assert rows[0] == ["Finding ID", "Evidence to Collect", "Key Questions", "Suggested Interviews", "Causal Hypothesis"]
    ids = [r[0] for r in rows[1:]]
    cited = {x for s in load(GOLDEN)["sections"] for it in s["items"] if it["kind"] == "question"
             for x in it.get("cites") or [] if x.startswith("FND-")}
    assert len(ids) == len(set(ids)) and set(ids) == cited
    assert all(r[3] == "" and r[4] == "" for r in rows[1:])                  # interviews and hypotheses: blank


def test_golden_is_rendered():
    """Plan checklist item 6: Task 24 rendered the golden beside its JSON, so check-samples holds it to OD4-4."""
    assert all(GOLDEN.with_suffix(f".{ext}").is_file() for ext in ("html", "md"))
    assert GOLDEN.name not in SAMPLES.RENDER_PENDING
    assert run("check-samples", str(ROOT / "samples")).strip().endswith("0 problem(s) in " + str(ROOT / "samples"))
