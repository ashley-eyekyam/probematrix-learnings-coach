"""tools/sync-wiki.py: mirror docs/manual/ into a wiki clone."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("sync_wiki", ROOT / "tools" / "sync-wiki.py")
sw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sw)


@pytest.fixture()
def manual(tmp_path):
    m = tmp_path / "manual"
    (m / "commands").mkdir(parents=True)
    (m / "skills").mkdir()
    (m / "Home.md").write_text("# Home\nSee [guide](Guide.md#setup) and [cmd](commands/x.md).\n", encoding="utf-8")
    (m / "Guide.md").write_text("# Guide\n[home](Home.md) [ext](https://e.com/a.md) [skill](skills/y.md#top)\n"
                                "![img](pic.png)\n", encoding="utf-8")
    (m / "commands" / "x.md").write_text("# x\n[up](../Guide.md) [sib](../skills/y.md)\n", encoding="utf-8")
    (m / "skills" / "y.md").write_text("# y\n[cmd](../commands/x.md#flags)\n", encoding="utf-8")
    return m


def test_wiki_names():
    assert sw.wiki_name("Home.md") == "Home"
    assert sw.wiki_name("Guide.md") == "Guide"
    assert sw.wiki_name("commands/x.md") == "Command-x"
    assert sw.wiki_name("skills/y.md") == "Skill-y"
    with pytest.raises(ValueError):
        sw.wiki_name("other/deep/z.md")


def test_links_rewritten(manual):
    p = sw.build_pages(manual, "1.2.3")
    assert "[guide](Guide#setup)" in p["Home"] and "[cmd](Command-x)" in p["Home"]
    assert "[ext](https://e.com/a.md)" in p["Guide"] and "[skill](Skill-y#top)" in p["Guide"]
    assert "![img](pic.png)" in p["Guide"]
    assert "[up](Guide)" in p["Command-x"] and "[sib](Skill-y)" in p["Command-x"]
    assert "[cmd](Command-x#flags)" in p["Skill-y"]
    assert ".md)" not in p["Home"].split("\n", 2)[2]


def test_broken_and_escaping_links(manual):
    (manual / "Bad.md").write_text("[x](Nope.md)", encoding="utf-8")
    with pytest.raises(ValueError):
        sw.build_pages(manual, "1")
    (manual / "Bad.md").write_text("[x](../../Out.md)", encoding="utf-8")
    with pytest.raises(ValueError):
        sw.build_pages(manual, "1")


def test_version_stamp_on_every_page(manual):
    p = sw.build_pages(manual, "9.9.9")
    for name in ("Home", "Guide", "Command-x", "Skill-y"):
        first = p[name].split("\n")[0]
        assert first == ("> Documents ProbeMatrix Learnings Coach v9.9.9. Source: [docs/manual/"
                         + {"Home": "Home.md", "Guide": "Guide.md", "Command-x": "commands/x.md",
                            "Skill-y": "skills/y.md"}[name]
                         + "](https://github.com/ashley-eyekyam/probematrix-learnings-coach/blob/main/docs/manual/"
                         + {"Home": "Home.md", "Guide": "Guide.md", "Command-x": "commands/x.md",
                            "Skill-y": "skills/y.md"}[name]
                         + "). Edit there, not here: this page is replaced on every release.")


def test_sidebar_and_footer(manual):
    p = sw.build_pages(manual, "1")
    s = p["_Sidebar"]
    assert "[Home](Home)" in s and "[Guide](Guide)" in s
    assert "**Commands**" in s and "[x](Command-x)" in s and "**Skills**" in s and "[y](Skill-y)" in s
    assert sw.pmlc.BRAND in p["_Footer"]


def test_owner_pages_untouched(manual, tmp_path):
    w = tmp_path / "wiki"
    w.mkdir()
    (w / "Release-notes-2.0.md").write_text("mine", encoding="utf-8")
    ch = sw.sync(manual, w, "1")
    assert "write Home" in ch
    assert (w / "Release-notes-2.0.md").read_text(encoding="utf-8") == "mine"
    assert json.loads((w / ".pmlc-sync.json").read_text())["version"] == "1"
    assert "Release-notes-2.0" not in json.loads((w / ".pmlc-sync.json").read_text())["pages"]
    assert "unchanged Home" in sw.sync(manual, w, "1")


def test_refuses_unowned_collision_without_adopt(manual, tmp_path, capsys):
    w = tmp_path / "wiki"
    w.mkdir()
    (w / "Home.md").write_text("owner's home", encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        sw.sync(manual, w, "1")
    assert e.value.code == 1
    assert "Home" in capsys.readouterr().err
    assert (w / "Home.md").read_text(encoding="utf-8") == "owner's home"
    assert not (w / "Guide.md").exists()
    ch = sw.sync(manual, w, "1", adopt=["Home"])
    assert "write Home" in ch and "Documents ProbeMatrix" in (w / "Home.md").read_text(encoding="utf-8")


def test_deletes_only_owned_removed_pages(manual, tmp_path):
    w = tmp_path / "wiki"
    (manual / "skills" / "z.md").write_text("# z\n", encoding="utf-8")
    sw.sync(manual, w, "1")
    (w / "Mine.md").write_text("x", encoding="utf-8")
    (manual / "skills" / "z.md").unlink()
    ch = sw.sync(manual, w, "1")
    assert "delete Skill-z" in ch
    assert not (w / "Skill-z.md").exists() and (w / "Mine.md").exists()


def test_check_mode_exit_codes(manual, tmp_path, capsys):
    w = tmp_path / "wiki"
    base = ["--wiki-dir", str(w), "--manual-dir", str(manual), "--version", "1"]
    assert sw.main(base + ["--check"]) == 1
    assert not w.exists()
    assert sw.main(base) == 0
    assert sw.main(base + ["--check"]) == 0
    (w / "Home.md").write_text("drift", encoding="utf-8")
    assert sw.main(base + ["--check"]) == 1
    assert (w / "Home.md").read_text(encoding="utf-8") == "drift"
    sw.sync(manual, w, "1")
    (manual / "Extra.md").write_text("# e\n", encoding="utf-8")
    sw.sync(manual, w, "1")
    (manual / "Extra.md").unlink()
    assert sw.main(base + ["--check"]) == 1
    assert (w / "Extra.md").exists()
    capsys.readouterr()


def test_default_version_and_cli_error(manual, tmp_path, capsys):
    w = tmp_path / "wiki"
    assert sw.main(["--wiki-dir", str(w), "--manual-dir", str(manual)]) == 0
    assert f"v{sw.pmlc.__version__}." in (w / "Home.md").read_text(encoding="utf-8")
    (manual / "Bad.md").write_text("[x](Nope.md)", encoding="utf-8")
    assert sw.main(["--wiki-dir", str(w), "--manual-dir", str(manual)]) == 1
    assert "error" in capsys.readouterr().err


def test_never_invokes_git(manual, tmp_path, monkeypatch):
    def boom(*a, **k):
        raise AssertionError("git/subprocess must not run")
    monkeypatch.setattr(subprocess, "run", boom)
    monkeypatch.setattr(subprocess, "Popen", boom)
    sw.sync(manual, tmp_path / "wiki", "1")
    src = (ROOT / "tools" / "sync-wiki.py").read_text(encoding="utf-8")
    assert "subprocess" not in src and "os.system" not in src


def test_cli_subprocess(manual, tmp_path):
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "sync-wiki.py"), "--wiki-dir", str(tmp_path / "w"),
                        "--manual-dir", str(manual)], capture_output=True, text=True)
    assert r.returncode == 0 and "write Home" in r.stdout


@pytest.mark.skipif(not (ROOT / "docs" / "manual").is_dir(), reason="docs/manual not written yet")
def test_real_manual_builds():
    import re
    p = sw.build_pages(ROOT / "docs" / "manual", "1")
    files = list((ROOT / "docs" / "manual").rglob("*.md"))
    assert len(p) == len(files) + 2
    for name, text in p.items():
        body = text.split("\n", 2)[-1] if not name.startswith("_") else text
        assert not re.search(r"\]\([^)\s:]*\.md[#)]", body), name
