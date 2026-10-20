"""Run manifest, retention, purge and the statutory-report line (Phase 3, Task 16), on synthetic exports."""
import copy
import json
import os
import subprocess
import sys


from test_pmlc import PMLC, make_export, run, run_fail
from test_handling import PACK
import pmlc  # noqa: E402
import pmlc_pack as pp  # noqa: E402

SLUG = "2024-03-20-pump-fire"


def make_run(tmp_path, name="export-with-a-name.xlsx"):
    x = make_export(tmp_path, name=name)
    run("ingest", str(x), "--slug", "pump-fire")
    return tmp_path / "pmlc-runs" / SLUG


def rm(run_dir):
    return json.loads((run_dir / "run-manifest.json").read_text(encoding="utf-8"))


def test_ingest_writes_run_manifest(tmp_path):
    rd = make_run(tmp_path)
    m = rm(rd)
    assert m["run"] == SLUG and m["export_file"] == f"{SLUG}.xlsx"
    assert len(m["export_sha256"]) == 64 and m["classification"] == "internal"
    assert m["retention_review"] is None and m["jurisdiction"] == [] and m["purged_on"] is None and m["purged"] == []
    run("run-manifest", str(rd / "workspace"), "--jurisdiction", "in,uk", "--retention-review", "2030-01-01",
        "--intended-use", "board learning", "--classification", "restricted")
    m = rm(rd)
    assert (m["jurisdiction"], m["retention_review"], m["intended_use"], m["classification"]) == (
        ["in", "uk"], "2030-01-01", "board learning", "restricted")
    run("ingest", str(tmp_path / "export-with-a-name.xlsx"), "--slug", "pump-fire", "--force")
    assert rm(rd)["jurisdiction"] == ["in", "uk"]       # a person's settings survive a re-ingest
    assert "jurisdiction" in run("status", str(rd / "workspace"))
    r = run_fail("run-manifest", str(rd / "workspace"), "--jurisdiction", "xx")
    assert "unknown code" in r.stderr


def test_run_manifest_under_redact_hides_export_name(tmp_path):
    x = make_export(tmp_path, name="Seeded-Person-export.xlsx")
    mp = tmp_path / "redact.json"
    mp.write_text(json.dumps({"Seeded Person": "the operator"}), encoding="utf-8")
    run("ingest", str(x), "--slug", "pump-fire", "--redact", str(mp))
    text = (tmp_path / "pmlc-runs" / SLUG / "run-manifest.json").read_text(encoding="utf-8")
    assert "Seeded" not in text and "export.xlsx" not in text and f"{SLUG}.xlsx" in text


def purge(*args):
    return subprocess.run([sys.executable, str(PMLC), "purge", *args], capture_output=True, text=True)


def test_purge_dry_run_without_yes(tmp_path):
    rd = make_run(tmp_path)
    r = purge(str(rd))
    assert r.returncode == 1 and "workspace" in r.stdout and "--yes" in r.stderr
    assert (rd / "workspace" / "findings.json").exists() and (rd / "outputs").is_dir()
    assert rm(rd)["purged_on"] is None


def test_purge_keeps_outputs(tmp_path):
    rd = make_run(tmp_path)
    (rd / "outputs" / "x.md").write_text("keep", encoding="utf-8")
    assert purge(str(rd), "--keep", "outputs", "--yes").returncode == 0
    assert not (rd / "workspace").exists() and (rd / "outputs" / "x.md").read_text() == "keep"
    m = rm(rd)
    assert m["purged"] == ["workspace"] and m["purged_on"]


def test_purge_removes_outputs_by_default(tmp_path):
    rd = make_run(tmp_path)
    (rd / "outputs" / "x.md").write_text("gone", encoding="utf-8")
    assert purge(str(rd), "--yes").returncode == 0
    assert not (rd / "workspace").exists() and not (rd / "outputs").exists()
    m = rm(rd)
    assert m["purged"] == ["outputs", "workspace"] and m["purged_on"]
    assert purge(str(rd), "--yes").returncode == 1       # a second purge refuses: nothing left to purge


def test_purge_refuses_non_run_folder(tmp_path):
    for d in (tmp_path / "pmlc-runs" / "notes", tmp_path / "other" / SLUG, tmp_path / "pmlc-runs" / SLUG):
        (d / "workspace").mkdir(parents=True)
        if d.name != SLUG or d.parent.name != "pmlc-runs":
            (d / "workspace" / "manifest.json").write_text("{}")
        (d / "keep.txt").write_text("x")
        r = purge(str(d), "--yes")      # last one: right name, but no workspace/manifest.json
        assert r.returncode == 1 and "refused" in r.stderr, d
        assert (d / "workspace").exists() and (d / "keep.txt").exists()
    assert purge(str(tmp_path), "--yes").returncode == 1
    assert purge(str(tmp_path / "missing"), "--yes").returncode == 1


def test_purge_refuses_symlink_escape(tmp_path):
    rd = make_run(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "precious.txt").write_text("x")
    (rd / "outputs").rmdir()
    os.symlink(outside, rd / "outputs")
    r = purge(str(rd), "--yes")
    assert r.returncode == 1 and "symlink" in r.stderr
    assert (outside / "precious.txt").exists() and (rd / "workspace" / "findings.json").exists()
    # a run folder that is itself a link to a real run
    link = tmp_path / "pmlc-runs" / "2024-03-21-linked"
    os.symlink(rd, link)
    assert purge(str(link), "--yes").returncode == 1
    assert (rd / "workspace" / "findings.json").exists()
    # a link inside the workspace is removed, never followed
    (rd / "outputs").unlink()
    (rd / "outputs").mkdir()
    os.symlink(outside, rd / "workspace" / "dir-link")
    assert purge(str(rd), "--yes").returncode == 0
    assert (outside / "precious.txt").exists()


def line_ws(tmp_path, jur=None, retention=None):
    rd = make_run(tmp_path)
    args = []
    if jur:
        args += ["--jurisdiction", jur]
    if retention:
        args += ["--retention-review", retention]
    if args:
        run("run-manifest", str(rd / "workspace"), *args)
    return rd / "workspace"


def render(ws, pack=None):
    w = pmlc.load_ws(ws)
    eh = pmlc.effective_handling(pack or PACK, w, ws=ws)
    return pp.render_pack_md(copy.deepcopy(pack or PACK), w, eh=eh), pp.render_pack_html(
        w, copy.deepcopy(pack or PACK), "r", "d", eh=eh), eh


def test_statutory_line_in_pack_and_register_md(tmp_path):
    ws = line_ws(tmp_path, jur="in")
    md, html, eh = render(ws)
    expected = "Statutory report still required: " + "; ".join(pmlc.regimes_for(["in"]))
    assert "Factories Act 1948 s.88; OSH Code 2020 s.10" in expected
    assert expected in md and expected.replace("&", "&amp;") in html
    assert expected in pmlc.handling_lines(eh)       # the register Markdown renders handling_lines (register-md is Task 5)
    (tmp_path / "b").mkdir()
    assert "Statutory report" not in render(line_ws(tmp_path / "b"))[0]


def test_retention_line_rendered(tmp_path):
    ws = line_ws(tmp_path, retention="2031-05-06")
    md, html, _ = render(ws)
    assert "Retention review: 2031-05-06" in md and "Retention review: 2031-05-06" in html
    pack = copy.deepcopy(PACK)
    pack["handling"] = {"retention_review": "2032-01-02"}      # the block's own date wins
    assert "Retention review: 2032-01-02" in render(ws, pack)[0]
    plain = pmlc.handling_lines({"classification": "internal", "version": "1.0", "effective_status": "draft",
                                 "draft_reasons": []})
    assert plain == ["Review: draft · Classification: internal · Version 1.0"]
