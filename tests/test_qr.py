"""Vendored Nayuki QR encoder (unmodified) and the qr_svg wrapper."""
import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "skills" / "learnings-coach" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from pmlc_lib.render import find_browser, qr  # noqa: E402

VENDOR = SCRIPTS / "pmlc_lib" / "vendor"
TEXT = "https://example.org/p#i/c-1"


def _matrix(text=TEXT):
    q = qr.qr_code(text)
    n = q.get_size()
    return q, [[q.get_module(x, y) for x in range(n)] for y in range(n)]


def test_vendored_file_unmodified():
    digest = hashlib.sha256((VENDOR / "qrcodegen.py").read_bytes()).hexdigest()
    assert digest == qr.VENDOR_SHA256
    lic = (VENDOR / "LICENSE-qrcodegen").read_text(encoding="utf-8")
    assert "MIT" in lic and "Project Nayuki" in lic


def _finder(m, x0, y0):
    # 7x7 finder: dark ring, light ring, dark 3x3 core
    for dy in range(7):
        for dx in range(7):
            ring = max(abs(dx - 3), abs(dy - 3))
            if m[y0 + dy][x0 + dx] != (ring != 2):
                return False
    return True


def _bch_rem(v):
    r = v
    for _ in range(10):
        r = (r << 1) ^ ((r >> 9) * 0x537)
    return (v << 10 | r) & 0x7FFF


def test_qr_structure():
    q, m = _matrix()
    n = q.get_size()
    assert n == 21 + 4 * (q._version - 1)
    assert _finder(m, 0, 0) and _finder(m, n - 7, 0) and _finder(m, 0, n - 7)
    # copy 1 of the format bits: (8,i) i<6, (8,7), (8,8), (7,8), (14-i,8) i>=9
    pos = [(8, i) for i in range(6)] + [(8, 7), (8, 8), (7, 8)] + [(14 - i, 8) for i in range(9, 15)]
    word = 0
    for i, (x, y) in enumerate(pos):
        word |= int(m[y][x]) << i
    word ^= 0x5412
    assert _bch_rem(word >> 10) == word, "BCH(15,5) check fails"
    assert (word >> 13) & 3 == 0, "format bits do not say ECC M"  # M = 0b00


def test_qr_svg_shape():
    svg = qr.qr_svg(TEXT)
    assert svg.startswith("<svg") and svg.rstrip().endswith("</svg>")
    assert 'role="img"' in svg
    assert 'aria-label="QR code: https://example.org/p#i/c-1"' in svg
    assert svg.count("<path") == 1
    assert svg == qr.qr_svg(TEXT)
    q, _ = _matrix()
    side = q.get_size() + 8
    assert f'viewBox="0 0 {side} {side}"' in svg
    assert f'width="{side * 3}"' in svg
    assert f'width="{(q.get_size() + 4) * 5}"' in qr.qr_svg(TEXT, module_px=5, border=2)


def test_qr_svg_escapes_label():
    svg = qr.qr_svg('a"<b>&')
    assert 'aria-label="QR code: a&quot;&lt;b&gt;&amp;"' in svg
    assert "<b>" not in svg


def _browser():
    return find_browser()


@pytest.mark.skipif(not (shutil.which("zbarimg") and _browser()), reason="zbarimg or a browser is missing")
def test_qr_decodes_with_zbar(tmp_path):
    svg = tmp_path / "q.svg"
    svg.write_text("<!doctype html><body style='margin:0'>" + qr.qr_svg(TEXT, module_px=8) + "</body>")
    png = tmp_path / "q.png"
    subprocess.run([_browser(), "--headless", "--no-sandbox", "--disable-gpu", f"--screenshot={png}",
                    "--window-size=400,400", svg.as_uri()], check=True, capture_output=True, timeout=60)
    out = subprocess.run(["zbarimg", "--quiet", "--raw", str(png)], capture_output=True, text=True).stdout
    assert out.strip() == TEXT
    assert re.match(r"https://", out)
