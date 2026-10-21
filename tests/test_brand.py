"""Phase 4, Task 19: the organisation brand (locked footer, AA contrast, logo limits), the reading time and the
word limits (Rulings P4-16, P4-19). Synthetic fixtures only."""
import base64
import copy
import json
import math
import os
import shutil
import subprocess
import sys

import pytest

from test_pmlc import PMLC, ws  # noqa: F401  (ws is a module-scoped fixture)
from test_pack import FIX, GOLDEN_EPOCH, RUN, fixture
import pmlc  # noqa: E402

from pmlc_lib import render as R  # noqa: E402
from pmlc_lib.render import brand as RB, fields as RF  # noqa: E402
from pmlc_lib.pack import profiles  # noqa: E402

PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")
LOCKED = "brand.json may set organisation, accent and logo only; the footer and status line are fixed"


@pytest.fixture()
def std_ws(ws, tmp_path):  # noqa: F811
    d = tmp_path / "pmlc-runs" / RUN / "workspace"
    shutil.copytree(ws, d)
    return d


def _cli(*args):
    env = dict(os.environ, SOURCE_DATE_EPOCH=GOLDEN_EPOCH)
    return subprocess.run([sys.executable, str(PMLC), *args], capture_output=True, text=True, env=env)


def _brand(tmp_path, _name="brand.json", **kw):
    p = tmp_path / _name
    p.write_text(json.dumps(kw), encoding="utf-8")
    return p


def _exit_msg(path):
    with pytest.raises(SystemExit) as e:
        RB.load_brand(path)
    return e.value.code


def test_brand_keys_locked(tmp_path, std_ws):
    assert _exit_msg(_brand(tmp_path, footer="x")) == LOCKED
    assert _exit_msg(_brand(tmp_path, organisation="Acme", status="x")) == LOCKED
    r = _cli("pack", str(std_ws), str(FIX / "board-brief.json"), "--out", str(tmp_path / "o"),
             "--brand", str(_brand(tmp_path, footer="x")))
    assert r.returncode == 1 and LOCKED in r.stderr
    assert not (tmp_path / "o").exists()                       # nothing written


def test_brand_contrast(tmp_path):
    assert RB.contrast_ratio("#FFFFFF", "#000000") == pytest.approx(21.0)
    assert RB.contrast_ratio("#ffffff", "#ffffff") == pytest.approx(1.0)
    msg = _exit_msg(_brand(tmp_path, accent="#FFFF00"))
    ratio = RB.contrast_ratio("#FFFF00", "#ffffff")
    assert msg == f"accent #FFFF00 has contrast {ratio:.1f}:1 against white; WCAG AA needs 4.5:1"
    assert f"{ratio:.1f}:1" in msg and ratio < 1.5
    b = RB.load_brand(_brand(tmp_path, accent="#1A7070"))
    assert b.accent == "#1A7070" and b.organisation is None and b.logo_bytes is None
    for bad in ("1A7070", "#1A70", "teal", 5):
        assert "accent" in str(_exit_msg(_brand(tmp_path, accent=bad)))


def test_brand_logo_limits(tmp_path):
    (tmp_path / "big.png").write_bytes(PNG + b"\0" * (300 * 1024))
    assert "200 KB" in _exit_msg(_brand(tmp_path, logo="big.png"))
    (tmp_path / "x.gif").write_bytes(b"GIF89a" + b"\0" * 20)
    assert "PNG or JPEG" in _exit_msg(_brand(tmp_path, logo="x.gif"))
    (tmp_path / "fake.png").write_bytes(b"not a png")
    assert "PNG or JPEG" in _exit_msg(_brand(tmp_path, logo="fake.png"))
    assert "not found" in _exit_msg(_brand(tmp_path, logo="nope.png"))
    (tmp_path / "ok.png").write_bytes(PNG)
    (tmp_path / "ok.jpg").write_bytes(b"\xff\xd8\xff\xe0" + b"\0" * 20)
    b = RB.load_brand(_brand(tmp_path, logo="ok.png", organisation="Acme Ltd"))
    assert b.logo_bytes == PNG and b.logo_mime == "image/png" and b.organisation == "Acme Ltd"
    assert RB.load_brand(_brand(tmp_path, logo="ok.jpg")).logo_mime == "image/jpeg"
    assert "organisation" in _exit_msg(_brand(tmp_path, organisation=3))
    assert "cannot read" in _exit_msg(tmp_path / "missing.json")


def test_brand_html_and_dashboard(tmp_path, std_ws):
    (tmp_path / "logo.png").write_bytes(PNG)
    bf = _brand(tmp_path, organisation="Acme <Ltd>", accent="#1A7070", logo="logo.png")
    brand = RB.load_brand(bf)
    css = RB.brand_css(brand)
    assert "#1A7070" in css and "--accent" in css and ".brand-logo" in css
    assert RB.brand_css(RB.load_brand(_brand(tmp_path, "empty.json"))) == ""
    out = tmp_path / "o"
    r = _cli("pack", str(std_ws), str(FIX / "board-brief.json"), "--out", str(out), "--brand", str(bf))
    assert r.returncode == 0, r.stderr
    page = (out / "board-brief.html").read_text(encoding="utf-8")
    assert "#1A7070" in page and "data:image/png;base64," + base64.b64encode(PNG).decode() in page
    assert "Acme &lt;Ltd&gt;" in page and "Acme <Ltd>" not in page
    assert pmlc.BRAND in page and pmlc.STATUS_PHRASE in page
    md = (out / "board-brief.md").read_text(encoding="utf-8")
    assert md.endswith(pmlc.BRAND + "\n") and "#1A7070" not in md
    plain = tmp_path / "p"
    assert _cli("pack", str(std_ws), str(FIX / "board-brief.json"), "--out", str(plain)).returncode == 0
    assert "#1A7070" not in (plain / "board-brief.html").read_text(encoding="utf-8")
    # the dashboard
    pm = _run_dashboard(std_ws, tmp_path / "d.html", "--brand", str(bf))
    assert pm.returncode == 0, pm.stderr
    d = (tmp_path / "d.html").read_text(encoding="utf-8")
    assert "#1A7070" in d and "data:image/png;base64," in d and "Acme &lt;Ltd&gt;" in d
    assert pmlc.BRAND in d and pmlc.STATUS_PHRASE in d
    bad = _run_dashboard(std_ws, tmp_path / "d2.html", "--brand", str(_brand(tmp_path, "bad.json", footer="x")))
    assert bad.returncode == 1 and LOCKED in bad.stderr and not (tmp_path / "d2.html").exists()


def _run_dashboard(ws_dir, out, *extra):
    return _cli("dashboard", str(ws_dir), "--out", str(out), *extra)


def test_reading_time_line(std_ws, tmp_path):
    pack = fixture("board-brief")
    n = RF.reading_minutes(pack)
    line = R.READING_TIME.format(n=n)
    out = tmp_path / "o"
    assert _cli("pack", str(std_ws), str(FIX / "board-brief.json"), "--out", str(out)).returncode == 0
    page = (out / "board-brief.html").read_text(encoding="utf-8")
    head, _, rest = page.partition('<p class="status">')
    assert line in head and head.index(line) > head.index("<h1>") and "<main>" in head
    md = (out / "board-brief.md").read_text(encoding="utf-8").split("\n\n")
    i = next(k for k, x in enumerate(md) if x.startswith(f"*{pmlc.STATUS_PHRASE}"))
    assert md[i + 1] == f"*{line}*"
    # 201 words give 2 minutes, 200 give 1, none gives 1
    words = lambda k: {"bottom_line": [{"text": " ".join(["word"] * k), "cites": ["FND-0001"]}], "sections": []}  # noqa: E731
    assert RF.pack_words(words(201)) == 201 and RF.reading_minutes(words(201)) == 2
    assert RF.reading_minutes(words(200)) == 1 and RF.reading_minutes(words(0)) == 1
    assert RF.reading_minutes(words(401)) == math.ceil(401 / 200) == 3


def test_reading_time_with_learner_banner(std_ws, tmp_path):
    out = tmp_path / "o"
    r = _cli("pack", str(std_ws), str(FIX / "training-designer.json"), "--out", str(out), "--view", "learner")
    assert r.returncode == 0, r.stderr
    page = (out / "training-designer.learner.html").read_text(encoding="utf-8")
    assert R.LEARNER_BANNER in page and "min read" in page
    assert page.index("min read") < page.index(R.LEARNER_BANNER)
    md = (out / "training-designer.learner.md").read_text(encoding="utf-8")
    assert R.LEARNER_BANNER in md and "min read" in md


def test_max_words_warning_then_strict(ws):  # noqa: F811
    w = pmlc.load_ws(ws)
    import pmlc_lib.pack.schema as PS
    prof = profiles.load()
    assert prof["board-brief"]["max_words"] == 1500 and prof["top-management-brief"]["max_words"] == 2000
    assert prof["dossier-F02"]["max_words"] == 9000
    pack = fixture("board-brief")
    assert [m for m in profiles.check(pack, prof["board-brief"]) if "words" in m and "allows" in m] == []
    big = copy.deepcopy(pack)
    big["bottom_line"][0]["text"] += " " + " ".join(["filler"] * 1600)
    n = RF.pack_words(big)
    msgs = profiles.check(big, prof["board-brief"])
    assert f"pack has {n} words; the board-brief profile allows 1500" in msgs
    res = PS.check_pack(big, w)
    assert any("allows 1500" in x for x in res.warnings + res.problems)
    strict = PS.check_pack(big, w, strict=True)
    assert any("allows 1500" in x for x in strict.problems)
    assert not any("allows 1500" in x for x in PS.check_pack(big, w).problems)
