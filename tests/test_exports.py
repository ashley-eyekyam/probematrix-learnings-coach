"""Phase 4, Task 17: the actions CSV (`--format csv`), follow-up.csv, render-all --format, the index listing formats
and shared copies, the pack-xlsx name guard and shared header, tier-unique register-items ids, and the
duplicate-format guard in render.register. Synthetic data only."""
import copy
import csv
import io
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import openpyxl
import pytest

from test_pack import FIX
from test_privacy import SPACK, share_ws, sign, write_doc
from test_pmlc import PMLC, make_export, run
from pmlc_lib import render as R
from pmlc_lib.render import exports as RX

ROOT = Path(__file__).resolve().parents[1]
STATUS = "Learning purposes: not a statutory document"


def cli(*args):
    return subprocess.run([sys.executable, str(PMLC), *args], capture_output=True, text=True)


def actions_pack(**top):
    p = copy.deepcopy(SPACK)
    p["sections"][0]["items"] += [
        {"kind": "decision", "decision": "Hold restarts until the test record exists", "cites": ["FND-0002"]},
        {"kind": "indicator", "name": "Restart tests", "measure": "=SUM(A1)", "cites": ["FND-0001"]},
        {"kind": "recommendation", "change": "-1 start with a minus", "indicator": "None", "hoc_tier": "engineering",
         "cites": ["FND-0002"]},
    ]
    p.update(top)
    return p


@pytest.fixture()
def shws(tmp_path):
    return share_ws(tmp_path)


def rows_of(text):
    return list(csv.reader(io.StringIO(text)))


# ----------------------------------------------------------------------------- actions CSV

def test_actions_csv_matches_export_actions(tmp_path, shws):
    ws, _ = shws
    p = write_doc(tmp_path, actions_pack())
    r = cli("pack", str(ws), str(p), "--format", "csv")
    assert r.returncode == 0, r.stderr
    f = ws.parent / "outputs" / "test-pack.actions.csv"
    assert f.is_file() and not (ws.parent / "outputs" / "test-pack.html").exists()
    r = cli("export-actions", str(ws), "--packs", str(p), "--out-dir", str(tmp_path / "ea"))
    assert r.returncode == 0, r.stderr
    mine = rows_of(f.read_text(encoding="utf-8"))
    theirs = rows_of((tmp_path / "ea" / "actions.csv").read_text(encoding="utf-8"))
    assert mine == theirs and len(mine) == 5
    head = mine[0]
    for row in mine[1:]:
        d = dict(zip(head, row))
        assert d["owner"] == d["due"] == d["status"] == d["capa_ref"] == d["effectiveness_check"] == ""
    assert any(r_[head.index("indicator")].startswith("'=SUM") for r_ in mine[1:])   # formula neutralised
    assert any(r_[head.index("change")].startswith("'-1") for r_ in mine[1:])


def test_actions_csv_refuses_overwrite(tmp_path, shws):
    ws, _ = shws
    p = write_doc(tmp_path, actions_pack())
    assert cli("pack", str(ws), str(p), "--format", "csv").returncode == 0
    f = ws.parent / "outputs" / "test-pack.actions.csv"
    f.write_text("id,owner\nx,Plant Manager\n", encoding="utf-8")                 # the organisation's entries
    r = cli("pack", str(ws), str(p), "--format", "html,csv")
    assert r.returncode == 1
    assert f"{f} already exists and may hold your organisation's entries; move it or pass a new --out" in r.stderr
    assert f.read_text(encoding="utf-8") == "id,owner\nx,Plant Manager\n"
    assert not (ws.parent / "outputs" / "test-pack.html").exists()                  # nothing else was written either
    other = tmp_path / "elsewhere"
    assert cli("pack", str(ws), str(p), "--format", "csv", "--out", str(other)).returncode == 0
    assert (other / "test-pack.actions.csv").is_file()


def test_actions_csv_shared_copy_is_masked_and_separate(tmp_path, shws):
    ws, orgs = shws
    doc = actions_pack()
    doc["sections"][0]["items"][1]["change"] = "Interlock the restart at P-101 after the test"
    p = write_doc(tmp_path, doc)
    sign(ws, p, "--classification", "external", "--legal-review", "cleared")
    assert cli("pack", str(ws), str(p), "--format", "csv").returncode == 0
    r = cli("pack", str(ws), str(p), "--format", "csv", "--share", "external", "--orgs", str(orgs))
    assert r.returncode == 0, r.stderr
    outs = ws.parent / "outputs"
    t = (outs / "test-pack.actions.external.csv").read_text(encoding="utf-8")
    assert "P-101" not in t and "[equipment tag]" in t
    raw = (outs / "test-pack.actions.external.csv").read_bytes()
    assert ws.parent.name.encode() not in raw and b"acme-pump-fire" not in raw          # Ruling X6: no run slug
    assert b"\r\r" not in raw and raw.split(b"\r\n")[1].startswith(b"test-pack/s1-")
    internal = (outs / "test-pack.actions.csv").read_bytes()
    assert ws.parent.name.encode() in internal                                         # internal ids keep it
    assert (outs / "test-pack.actions.csv").is_file()


def test_actions_csv_nothing_to_write(tmp_path, shws):
    ws, _ = shws
    p = write_doc(tmp_path, SPACK)
    p2 = copy.deepcopy(SPACK)
    p2["sections"][0]["items"] = [it for it in p2["sections"][0]["items"] if it["kind"] == "para"]
    write_doc(tmp_path, p2, "pack2.json")
    r = cli("pack", str(ws), str(tmp_path / "pack2.json"), "--format", "csv")
    assert r.returncode == 0 and "csv: nothing to write" in r.stderr
    assert not (ws.parent / "outputs" / "test-pack.actions.csv").exists()
    assert p.is_file()


# ----------------------------------------------------------------------------- follow-up.csv

def test_follow_up_csv_columns(tmp_path, shws):
    ws, _ = shws
    p = ws.parent / "outputs" / "investigator-coach.json"
    p.parent.mkdir(exist_ok=True)
    doc = json.loads((FIX / "investigator-coach.json").read_text(encoding="utf-8"))
    p.write_text(json.dumps(doc), encoding="utf-8")
    r = cli("pack", str(ws), str(p))
    assert r.returncode == 0, r.stderr
    outs = ws.parent / "outputs"
    rows = rows_of((outs / "follow-up.csv").read_text(encoding="utf-8"))
    assert rows[0] == ["Finding ID", "Evidence to Collect", "Key Questions", "Suggested Interviews",
                       "Causal Hypothesis"]
    js = json.loads((outs / "follow-up.json").read_text(encoding="utf-8"))
    assert [x[0] for x in rows[1:]] == list(js)
    assert rows[1][2] == js[rows[1][0]]["key_questions"]
    assert "follow-up.csv written to" in r.stdout
    # a shared copy writes neither follow-up file: interview plans stay inside the team
    for f in ("follow-up.csv", "follow-up.json"):
        (outs / f).unlink()
    sign(ws, p, "--classification", "external", "--legal-review", "cleared")
    r = cli("pack", str(ws), str(p), "--share", "external")
    assert r.returncode == 0, r.stderr
    assert not (outs / "follow-up.csv").exists() and not (outs / "follow-up.json").exists()


def test_follow_up_csv_neutralises_formulas():
    pack = {"sections": [{"items": [{"id": "follow-up", "kind": "table", "rows": [
        ["FND-0001", "=1+1", "-2 why", "plain", "@x"]]}]}]}
    rows = rows_of(RX.follow_up_csv(pack))
    assert rows[1] == ["FND-0001", "'=1+1", "'-2 why", "plain", "'@x"]
    assert RX.follow_up_csv({"sections": []}).splitlines() == [
        "Finding ID,Evidence to Collect,Key Questions,Suggested Interviews,Causal Hypothesis"]


# ----------------------------------------------------------------------------- render-all and index

def std_run(tmp_path):
    x = make_export(tmp_path)
    run("setup", str(x), "--slug", "pump-fire", "--root", str(tmp_path))
    ws = tmp_path / "pmlc-runs" / "2024-03-20-pump-fire" / "workspace"
    outd = ws.parent / "outputs"
    outd.mkdir(exist_ok=True)
    for n in ("board-brief", "supervisor-coach"):
        shutil.copy(FIX / f"{n}.json", outd / f"{n}.json")
    return ws, outd


def test_render_all_format_passthrough(tmp_path):
    ws, outd = std_run(tmp_path)
    assert cli("check-all", str(ws)).returncode == 0
    r = cli("render-all", str(ws), "--format", "html,md,normalised")
    assert r.returncode == 0, r.stderr
    for n in ("board-brief", "supervisor-coach"):
        assert (outd / f"{n}.html").is_file() and (outd / f"{n}.md").is_file()
        assert (outd / f"{n}.normalised.json").is_file()
    r = cli("render-all", str(ws), "--format", "nope")
    assert r.returncode == 2 and "unknown format" in r.stderr
    plain = tmp_path / "plain"
    shutil.copytree(tmp_path / "pmlc-runs", plain / "pmlc-runs")
    ws2 = plain / "pmlc-runs" / "2024-03-20-pump-fire" / "workspace"
    for f in (plain / "pmlc-runs" / "2024-03-20-pump-fire" / "outputs").glob("*.normalised.json"):
        f.unlink()
    assert cli("render-all", str(ws2)).returncode == 0                              # default: html and md only
    assert not list((ws2.parent / "outputs").glob("*.normalised.json"))


def test_render_all_format_docx_when_registered(tmp_path):
    if "docx" not in R.FORMATS:
        pytest.skip("the docx format (Task 10) is not in this branch yet")
    ws, outd = std_run(tmp_path)
    cli("check-all", str(ws))
    assert cli("render-all", str(ws), "--format", "html,md,docx").returncode == 0
    assert (outd / "board-brief.docx").is_file() and (outd / "supervisor-coach.docx").is_file()


def test_index_lists_formats_shared_and_groups_by_skill(tmp_path):
    ws, outd = std_run(tmp_path)
    for name in ("board-brief.external.html", "board-brief.cards.html", "board-brief.normalised.json",
                 "board-brief-questions.xlsx", "board-brief-questions.external.xlsx", "supervisor-coach.md",
                 "board-brief-notes.txt", "board-brief2.html"):
        (outd / name).write_text("x", encoding="utf-8")
    cli("check-all", str(ws))
    assert cli("index", str(ws)).returncode == 0
    page = (outd / "index.html").read_text(encoding="utf-8")
    for name in ("board-brief.external.html", "board-brief.cards.html", "board-brief.normalised.json",
                 "board-brief-questions.xlsx", "board-brief-questions.external.xlsx"):
        assert f'href="{name}"' in page, name
    assert "board-brief-notes.txt" not in page and 'href="board-brief2.html"' not in page
    skill_rows = re.findall(r'<tr class="skill"><th colspan="\d+">([^<]+)</th></tr>', page)
    assert skill_rows == sorted(skill_rows) and {"board-brief", "supervisor-coach"} <= set(skill_rows)
    # the board-brief files sit under their skill heading, before the next one
    seg = page.split('<th colspan="7">board-brief</th>')[1].split('<tr class="skill">')[0]
    assert "board-brief.external.html" in seg and "supervisor-coach.md" not in seg
    assert "Learning purposes: not a statutory document" in page and "<script" not in page


def test_index_groups_a_variant_under_its_skill(tmp_path):
    ws, outd = std_run(tmp_path)
    v = json.loads((FIX / "board-brief.json").read_text(encoding="utf-8"))
    v["pack"] = "board-brief-short"
    v["skill"] = "board-brief"
    (outd / "board-brief-short.json").write_text(json.dumps(v), encoding="utf-8")
    cli("index", str(ws))
    page = (outd / "index.html").read_text(encoding="utf-8")
    seg = page.split('<th colspan="7">board-brief</th>')[1].split('<tr class="skill">')[0]
    assert "board-brief-short.json" in seg or "board-brief-short" in seg


# ----------------------------------------------------------------------------- pack-xlsx

def question_pack(text="Who checked the restart?"):
    d = copy.deepcopy(SPACK)
    d["sections"][0]["items"].append({"kind": "question", "question": text, "why": "No check exists", "to": "Stores",
                                      "cites": ["FND-0001"],
                                      "lint_ok": {"rule": "JC1", "reason": "test of the name guard"}})
    return d


def test_pack_xlsx_name_guard_and_shared_header(tmp_path, shws):
    ws, orgs = shws
    names = tmp_path / "names.txt"
    names.write_text("Quillon Vantress\n", encoding="utf-8")
    bad = write_doc(tmp_path, question_pack("Did Quillon Vantress sign the restart?"), "bad.json")
    r = cli("pack-xlsx", str(ws), str(bad), "--kind", "question", "--names", str(names), "--out",
            str(tmp_path / "bad.xlsx"))          # lint_ok lets the pack through; the guard still refuses the sheet
    assert r.returncode == 1 and "refused: a listed name appears in the output" in r.stderr
    assert not (tmp_path / "bad.xlsx").exists()
    p = write_doc(tmp_path, question_pack(), "good.json")
    sign(ws, p, "--classification", "external", "--legal-review", "cleared")
    internal = tmp_path / "i.xlsx"
    assert cli("pack-xlsx", str(ws), str(p), "--kind", "question", "--out", str(internal)).returncode == 0
    hdr = openpyxl.load_workbook(internal).active.oddHeader.center.text
    assert hdr.startswith(STATUS) and "Shared" not in hdr
    r = cli("pack-xlsx", str(ws), str(p), "--kind", "question", "--share", "external", "--names", str(names))
    assert r.returncode == 0, r.stderr
    sh = ws.parent / "outputs" / "test-pack-questions.external.xlsx"
    assert "Shared external: identifying details are masked" in openpyxl.load_workbook(sh).active.oddHeader.center.text


# ----------------------------------------------------------------------------- INT-A, INT-B, register()

def test_register_items_ids_are_unique_across_tiers(tmp_path):
    from test_items import cli as icli, register
    x = make_export(tmp_path)
    run("ingest", str(x), "--slug", "test-pump", "--date", "2024-03-20", "--root", str(tmp_path))
    ws = tmp_path / "pmlc-runs" / "2024-03-20-test-pump" / "workspace"
    reg = tmp_path / "reg.json"
    reg.write_text(json.dumps(register()), encoding="utf-8")
    ids = {}
    for tier in ("T1", "T2", "T3"):
        r = icli("register-items", str(ws), "--tier", tier, "--register", str(reg))
        assert r.returncode == 0, r.stderr
        ids[tier] = [i["id"] for i in json.loads(r.stdout)]
    assert ids["T3"] == ["t3-lr-03"] and ids["T1"][0].startswith("t1-lr-")
    flat = [x_ for v in ids.values() for x_ in v]
    assert len(flat) == len(set(flat)) and len(ids["T1"]) >= 2
    # a pack that pastes two tiers has no duplicate-id problem
    items = []
    for tier in ("T1", "T3"):
        items += json.loads(icli("register-items", str(ws), "--tier", tier, "--register", str(reg)).stdout)
    from test_items import wrap
    p = tmp_path / "pack.json"
    p.write_text(json.dumps(wrap(*items)), encoding="utf-8")
    r = icli("check-pack", str(ws), str(p))
    assert r.returncode == 0 and "duplicate id" not in r.stdout + r.stderr


def test_check_pack_cite_and_exclude_message_says_how_to_fix(tmp_path):
    """INT-B: table-item interfaces can cite a finding that the pack excludes. The smaller fix: check-pack names
    where the cite is and what to do, instead of adding a flag to table-item."""
    from test_items import wrap
    x = make_export(tmp_path)
    run("ingest", str(x), "--slug", "test-pump", "--date", "2024-03-20", "--root", str(tmp_path))
    ws = tmp_path / "pmlc-runs" / "2024-03-20-test-pump" / "workspace"
    doc = wrap({"kind": "para", "text": "Seen.", "cites": ["FND-0001"]})
    doc["exclusions"] = [{"id": "FND-0001", "reason": "Out of scope for this audience"}]
    p = tmp_path / "pack.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    r = cli("check-pack", str(ws), str(p))
    assert r.returncode == 1
    out = r.stdout + r.stderr
    assert "FND-0001 is also cited at sections[0].items[0].cites" in out
    assert "remove it from that cite list, or from exclusions" in out


def test_register_refuses_a_second_function_under_a_name():
    def one(ctx):
        return []

    def two(ctx):
        return []

    name = "zz-exports-test"
    R.register(name, one)
    try:
        R.register(name, one)                                                       # the same function: fine
        with pytest.raises(ValueError, match="already registered"):
            R.register(name, two)
        assert R.FORMATS[name].fn is one
    finally:
        R.FORMATS.pop(name, None)


# ----------------------------------------------------------------------------- the manual

def test_csv_vs_json_doc():
    t = (ROOT / "docs" / "manual" / "commands" / "export-actions.md").read_text(encoding="utf-8")
    assert "CSV and JSON differ" in t and "leading `-`" in t and "single quote" in t
    pk = (ROOT / "docs" / "manual" / "commands" / "pack.md").read_text(encoding="utf-8")
    assert "| `csv` |" in pk and "follow-up.csv" in pk and "actions.csv" in pk
    ra = (ROOT / "docs" / "manual" / "commands" / "render-all.md").read_text(encoding="utf-8")
    assert "--format" in ra
    ix = (ROOT / "docs" / "manual" / "commands" / "index.md").read_text(encoding="utf-8")
    assert ".external." in ix and "skill" in ix
    px = (ROOT / "docs" / "manual" / "commands" / "pack-xlsx.md").read_text(encoding="utf-8")
    assert "Shared external: identifying details are masked" in px and "listed name" in px


def test_table_item_pack_drops_excluded_ids(tmp_path):
    """INT-B (ruling X13): table-item --pack removes the pack's excluded ids from row_cites and cites."""
    from test_items import wrap
    x = make_export(tmp_path)
    run("ingest", str(x), "--slug", "test-pump", "--date", "2024-03-20", "--root", str(tmp_path))
    ws = tmp_path / "pmlc-runs" / "2024-03-20-test-pump" / "workspace"
    run("classify", str(ws))
    plain = json.loads(cli("table-item", str(ws), "tiers").stdout)
    assert "FND-0001" in plain["cites"]
    doc = wrap({"kind": "para", "text": "Seen.", "cites": ["FND-0002"]})
    doc["exclusions"] = [{"id": i, "reason": "Out of scope for this audience"} for i in plain["cites"]
                         if i != "FND-0002"]
    p = tmp_path / "pack.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    it = json.loads(cli("table-item", str(ws), "tiers", "--pack", str(p)).stdout)
    gone = {e["id"] for e in doc["exclusions"]}
    assert gone and not gone & set(it["cites"]) and all(not gone & set(c) for c in it["row_cites"])
    assert len(it["row_cites"]) == len(plain["row_cites"])                              # rows keep their place
    doc["sections"][0]["items"].append(it)
    p.write_text(json.dumps(doc), encoding="utf-8")
    r = cli("check-pack", str(ws), str(p))
    assert r.returncode == 0, r.stdout + r.stderr                                     # empty row cites are tolerated
    doc["sections"][0]["items"][-1] = plain                                            # without --pack: the trap
    p.write_text(json.dumps(doc), encoding="utf-8")
    assert "is also cited at" in cli("check-pack", str(ws), str(p)).stdout + cli("check-pack", str(ws), str(p)).stderr
