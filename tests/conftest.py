"""Session-wide test helpers."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "learnings-coach" / "scripts"))

PROBE_SVG = ('<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 20" '
             'width="40" height="20"><rect width="40" height="20" fill="#fff"/></svg>\n')


@pytest.fixture(scope="session")
def png_probe():
    """None when `--format png` really renders on this machine, else the reason it does not (final review C1).

    A browser on PATH is not enough: on a stock Ubuntu 24.04 runner Chrome is found, yet its sandbox may refuse to
    start. So the probe renders one tiny SVG through the engine's own code path (with its --no-sandbox retry), and
    the png tests skip with the reason it records, so a CI log says why."""
    from pmlc_lib.render import find_browser, graphs
    browser = find_browser()
    if not browser:
        return "no Chromium-family browser"
    data, why = graphs._gx_png(browser, PROBE_SVG)
    return None if data else f"{browser}: {why}"


@pytest.fixture
def needs_png(png_probe):
    """Skip (a plain pytest.skip, not a Node marker) unless png really renders here."""
    if png_probe:
        pytest.skip(f"png does not render here: {png_probe}")
