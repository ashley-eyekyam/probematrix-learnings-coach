"""The engine split (Task 1): pmlc_lib/ behind the pmlc.py, pmlc_pack.py, pmlc_lint.py and pmlc_privacy.py shims."""
import ast
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "learnings-coach" / "scripts"
LIB = SCRIPTS / "pmlc_lib"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(SCRIPTS))
import pmlc  # noqa: E402


@pytest.mark.parametrize("module", ["pmlc", "pmlc_pack", "pmlc_lint", "pmlc_privacy"])
def test_every_old_name_still_exported(module):
    old = set(json.loads((FIXTURES / f"{module}-names.json").read_text(encoding="utf-8")))
    missing = sorted(old - set(dir(importlib.import_module(module))))
    assert not missing, f"{module} no longer exports: {missing}"


def test_pmlc_py_is_a_shim():
    text = (SCRIPTS / "pmlc.py").read_text(encoding="utf-8")
    assert len(text.splitlines()) < 40 and "pmlc_lib" in text


def test_version_single_source():
    import pmlc_lib
    assert pmlc.__version__ is pmlc_lib.__version__
    hits = sorted(str(p.relative_to(ROOT)) for p in (ROOT / "skills").rglob("*.py")
                  if '__version__ = "' in p.read_text(encoding="utf-8"))
    assert hits == ["skills/learnings-coach/scripts/pmlc_lib/__init__.py"]


def test_shim_runs_from_copied_folder(tmp_path):
    from test_pmlc import make_export
    import pmlc_lib
    shutil.copytree(ROOT / "skills", tmp_path / "s", ignore=shutil.ignore_patterns("__pycache__"))
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    script = "s/learnings-coach/scripts/pmlc.py"
    r = subprocess.run([sys.executable, script, "--version"], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == f"pmlc {pmlc_lib.__version__}"
    x = make_export(tmp_path / "exp")
    r = subprocess.run([sys.executable, script, "ingest", str(x), "--slug", "site-event", "--date", "2024-03-20"],
                       cwd=tmp_path, env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert (tmp_path / "exp" / "pmlc-runs" / "2024-03-20-site-event" / "workspace" / "findings.json").is_file()


def _fstring_lengths(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr):
            yield node.end_lineno - node.lineno + 1


def test_dashboard_uses_templates():
    assert sorted((LIB / "dashboard" / "templates").glob("*.html"))
    longest = max(_fstring_lengths(LIB / "dashboard" / "render.py"), default=0)
    assert longest <= 20, f"render.py has an f-string of {longest} lines"


def test_release_targets_lib(tmp_path):
    for rel in ("skills/learnings-coach/scripts/pmlc_lib/__init__.py", ".claude-plugin/plugin.json",
                ".claude-plugin/marketplace.json"):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / rel, tmp_path / rel)
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "release.py"), "--root", str(tmp_path), "2.0.0a9"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    init = (tmp_path / "skills/learnings-coach/scripts/pmlc_lib/__init__.py").read_text(encoding="utf-8")
    assert re.search(r'^__version__ = "2\.0\.0a9"$', init, flags=re.M)
