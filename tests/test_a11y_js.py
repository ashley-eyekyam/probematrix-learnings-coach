"""Accessibility (WCAG 2.2 AA, L4-18): axe-core over every generated page type (Ruling P4-17), the dashboard matrix
text and the pack page's skip link (Task 20)."""
import importlib.util
import io
import json
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest

from test_pack import fixture, render_fixture
from test_pmlc import MINI_REG, make_export, run

ROOT = Path(__file__).resolve().parents[1]
JS_DIR = ROOT / "tests" / "js"
AXE_RUN = JS_DIR / "axe_run.js"
NODE = shutil.which("node")
NPM_HINT = "run: npm ci --prefix tests/js"
BLOCKING = ("serious", "critical")
FIXTURES = ("all-kinds", "board-brief", "dossier-F02")      # the html of 3 fixtures
LAYOUTS = ("cards", "toolbox", "poster", "checklist", "paper", "field")
LAYOUT_PACK = "frontline-learning-cards"


def need_node_modules(js_dir: Path = JS_DIR) -> None:
    """P4-17: with Node present, a missing tests/js/node_modules is a failure, never a silent skip."""
    for pkg in ("axe-core", "jsdom"):
        if not (js_dir / "node_modules" / pkg / "package.json").is_file():
            pytest.fail(f"axe-core and jsdom are not installed in {js_dir}; {NPM_HINT}", pytrace=False)


def axe(page: Path, fragment: str = "") -> list:
    """axe_run.js over one page: its violations, as [{"id", "impact", "nodes"}]."""
    need_node_modules()
    r = subprocess.run([NODE, str(AXE_RUN), str(page)] + ([fragment] if fragment else []),
                       capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stderr + r.stdout
    return json.loads(r.stdout)["violations"]


def blocking(violations: list) -> list:
    return [v for v in violations if v["impact"] in BLOCKING]


# ----------------------------------------------------------------------------- the pages

@pytest.fixture(scope="module")
def run_outputs(tmp_path_factory):
    """A standard run of the synthetic export with two packs and the synthetic register, then check-all, render-all
    (which writes the dashboard), index and a dashboard with organisation files."""
    d = tmp_path_factory.mktemp("a11y")
    run("setup", str(make_export(d)), "--slug", "pump-fire", "--root", str(d))
    ws = d / "pmlc-runs" / "2024-03-20-pump-fire" / "workspace"
    out = ws.parent / "outputs"
    out.mkdir(exist_ok=True)
    for n in ("board-brief", LAYOUT_PACK):
        pk = fixture(n)
        if n == "board-brief":   # one item names a learning, so the learnings x packs matrix has a row
            pk["sections"][0]["items"][0]["learning"] = "LR-01"
        (out / f"{n}.json").write_text(json.dumps(pk), encoding="utf-8")
    (out / "learnings-register.json").write_text(json.dumps(MINI_REG), encoding="utf-8")
    (out / "distribution.csv").write_text("pack,audience,date,attendees,contractors_included\n"
                                          "board-brief,Board,2026-10-01,9,y\n", encoding="utf-8")
    (out / "adoption.csv").write_text("lr_id,title,response\nLR-01,x,accepted\n", encoding="utf-8")
    run("check-all", str(ws))
    run("render-all", str(ws))
    run("index", str(ws))
    run("dashboard", str(ws), "--register", str(out / "learnings-register.json"))
    return ws, out


def _write(tmp_path, name, data) -> Path:
    p = tmp_path / name
    p.write_text(data, encoding="utf-8") if isinstance(data, str) else p.write_bytes(data)
    return p


def _registered(fmt: str, task: int) -> None:
    from pmlc_lib import render as R
    if fmt not in R.FORMATS:
        pytest.skip(f"the {fmt} format is not registered yet (Task {task})")


def _layout_page(layout: str, tmp_path) -> Path:
    """<pack>.<layout>.html of the frontline fixture. Layouts come from Task 13: through the registry when it is
    there (a format named after the layout, or html with ctx.layout), else skipped."""
    from pmlc_lib import render as R
    if importlib.util.find_spec("pmlc_lib.render.layouts") is None:
        pytest.skip("the layouts are not registered yet (Task 13)")
    want = R.output_name(LAYOUT_PACK, "html", layout=layout)
    outs = render_fixture(LAYOUT_PACK, layout if layout in R.FORMATS else "html", layout=layout)
    page = [o for o in outs if o.name == want]
    assert page, f"no {want} among {[o.name for o in outs]}"
    return _write(tmp_path, want, page[0].data)


def _page(kind: str, arg: str, tmp_path, run_outputs) -> Path:
    if kind == "html":
        return _write(tmp_path, f"{arg}.html", render_fixture(arg, "html")[0].data)
    if kind == "layout":
        return _layout_page(arg, tmp_path)
    if kind == "email":
        _registered("email", 12)
        outs = [o for o in render_fixture(arg, "email") if o.name.endswith(".email.html")]
        assert outs, "the email format wrote no .email.html"
        return _write(tmp_path, outs[0].name, outs[0].data)
    if kind == "scorm":
        _registered("scorm", 21)
        outs = [o for o in render_fixture(arg, "scorm") if o.name.endswith(".scorm.zip")]
        assert outs, "the scorm format wrote no .scorm.zip"
        z = tmp_path / "scorm"
        zipfile.ZipFile(io.BytesIO(outs[0].data)).extractall(z)
        return z / "index.html"
    _, out = run_outputs
    return out / {"index": "index.html", "dashboard": "organisation-learning-map.html"}[kind]


PAGES = ([("html", n, "") for n in FIXTURES] + [("layout", x, "") for x in LAYOUTS]
         + [("email", "board-brief", ""), ("index", "", ""), ("dashboard", "", ""), ("dashboard", "", "#detail"),
            ("scorm", "frontline-learning-cards", "")])


@pytest.mark.skipif(not NODE, reason="node not installed")
@pytest.mark.parametrize("kind,arg,fragment", PAGES, ids=[f"{k}-{a or 'page'}{f}" for k, a, f in PAGES])
def test_axe_zero_serious(kind, arg, fragment, tmp_path, request):
    rs = request.getfixturevalue("run_outputs") if kind in ("index", "dashboard") else None
    page = _page(kind, arg, tmp_path, rs)
    assert page.is_file(), page
    bad = blocking(axe(page, fragment))
    assert bad == [], json.dumps(bad, indent=1)


@pytest.mark.skipif(not NODE, reason="node not installed")
def test_axe_node_modules_required(tmp_path):
    with pytest.raises(pytest.fail.Exception, match=re.escape(NPM_HINT)):
        need_node_modules(tmp_path)
    (tmp_path / "node_modules" / "axe-core").mkdir(parents=True)
    (tmp_path / "node_modules" / "axe-core" / "package.json").write_text("{}")
    with pytest.raises(pytest.fail.Exception, match="jsdom"):
        need_node_modules(tmp_path)


@pytest.mark.skipif(not NODE, reason="node not installed")
def test_axe_run_reports_serious_violations(tmp_path):
    """The checker itself: a page with an unnamed button and an image without alt text fails."""
    p = _write(tmp_path, "bad.html", '<!doctype html><html><head><title>x</title></head><body><main>'
                                     '<img src="a.png"><button></button></main></body></html>')
    ids = {v["id"]: v for v in axe(p)}
    assert {"image-alt", "button-name", "html-has-lang"} <= set(ids)
    assert ids["button-name"]["impact"] == "critical" and ids["button-name"]["nodes"] == ["button"]


# ----------------------------------------------------------------------------- the dashboard matrix and the skip link

def _tier_matrix(t: str) -> str:
    m = re.search(r'<table id="lr-matrix"[^>]*>.*?</table>', t, re.S)
    assert m, "no learnings matrix"
    return m.group(0)


def test_matrix_cells_have_text(tmp_path):
    d = tmp_path / "d"
    d.mkdir()
    run("ingest", str(make_export(d)), "--legacy-out", str(d / "ws"))
    run("classify", str(d / "ws"))
    reg = tmp_path / "r.json"
    reg.write_text(json.dumps(MINI_REG), encoding="utf-8")
    out = tmp_path / "d.html"
    run("dashboard", str(d / "ws"), "--register", str(reg), "--out", str(out))
    t = out.read_text(encoding="utf-8")
    mx = _tier_matrix(t)
    msgs = MINI_REG["entries"][0]["tier_messages"]
    cells = re.findall(r"<td[^>]*>.*?</td>", mx.split("<tbody>")[1], re.S)
    full = [c for c in cells if "●" in c]
    assert len(full) == len(msgs)
    for c, (tier, msg) in zip(full, msgs.items()):
        assert f'<span class="vh">{msg}</span>' in c, c
        assert 'aria-hidden="true">●' in c
    assert "title=" not in mx, "a tier message must not live only in a title attribute"
    assert re.search(r'<button type="button" class="mx-toggle"[^>]*aria-controls="lr-matrix"[^>]*aria-pressed="false"', t)
    css = re.search(r"<style>(.*?)</style>", t, re.S).group(1)
    assert ".vh{" in css and "table.show-msg td:not(.z) .vh{" in css
    assert re.search(r"@media \(max-width:600px\)\{[^}]*tbody th\{white-space:normal", css)


@pytest.mark.skipif(not NODE, reason="node not installed")
def test_matrix_toggle_shows_messages(run_outputs):
    """detail.js unhides the toggle; a click sets aria-pressed and shows the messages, a second click hides them."""
    need_node_modules()
    _, out = run_outputs
    page = out / "organisation-learning-map.html"
    script = f"""
const {{ JSDOM }} = require({json.dumps(str(JS_DIR / "node_modules" / "jsdom"))});
const fs = require("fs");
const dom = new JSDOM(fs.readFileSync({json.dumps(str(page))}, "utf8"), {{runScripts: "dangerously"}});
dom.window.addEventListener("load", () => {{
  const d = dom.window.document, b = d.querySelector("button.mx-toggle"), t = d.getElementById("lr-matrix");
  const seen = [b.hidden, b.getAttribute("aria-pressed"), t.classList.contains("show-msg")];
  b.click(); seen.push(b.getAttribute("aria-pressed"), t.classList.contains("show-msg"));
  b.click(); seen.push(b.getAttribute("aria-pressed"), t.classList.contains("show-msg"));
  console.log(JSON.stringify(seen));
}});
"""
    r = subprocess.run([NODE, "-e", script], capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout.strip().splitlines()[-1]) == [False, "false", False, "true", True, "false", False]

def test_skip_link():
    t = render_fixture("board-brief", "html")[0].data
    body = t.split("<body>", 1)[1]
    assert body.startswith('<a class="skip" href="#content">Skip to the sections</a>'), body[:120]
    assert '<div class="content" id="content" tabindex="-1">' in t
    assert ".skip{" in t and ".skip:focus{" in t
    hi = fixture("board-brief")
    hi["lang"] = "hi"
    th = render_fixture("board-brief", "html", pack=hi)[0].data
    assert '<a class="skip" href="#content">खंडों पर जाएँ</a>' in th


@pytest.mark.skipif(not NODE, reason="node not installed")
def test_axe_run_cli_usage():
    """axe_run.js with no file prints its usage (no Node packages needed: it stops before loading them)."""
    r = subprocess.run([NODE, str(AXE_RUN)], capture_output=True, text=True)
    assert r.returncode == 2 and "usage: node axe_run.js <html-file>" in r.stderr

