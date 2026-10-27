"""Small shared helpers: cell coercion, paths, JSON writes, dates."""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]   # the scripts folder, next to pmlc.py
REFS = HERE.parent / "references"
CODE_RX = re.compile(r"\b([A-Z]{2,5})\s?(\d{1,2}\.\d{1,2})\b")
# A date or a deadline in free text (D7): owners and due dates are the organisation's, never the pack's. Shared by the
# 9M interview (answer-time note) and the no-owner-due profile rule (a warning on a date in a recommendation).
DUE_DATE_RX = re.compile(
    r"\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b|\b\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|"
    r"sep|oct|nov|dec)[a-z]*\b|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}\b|\bby\s+(?:end of|"
    r"next|this)\s+\w+", re.I)


# ----------------------------------------------------------------------------- helpers

def _need_openpyxl():
    try:
        import openpyxl  # noqa: F401
        return openpyxl
    except ImportError:
        sys.exit("openpyxl is required: pip install openpyxl")


def _int(v, default=None):
    """An int from a cell: '436', 436 or the float cell '436.0'; anything else (4.5, nan, text) is `default`."""
    try:
        return int(str(v).strip())
    except (TypeError, ValueError):
        pass
    try:
        f = float(str(v).strip())
    except (TypeError, ValueError):
        return default
    return int(f) if f == f and abs(f) != float("inf") and f == int(f) else default


def _n(n, word) -> str:
    """'1 finding', '2 findings'."""
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def _s(v) -> str:
    return "" if v is None else str(v).strip()


def split_outside_parens(s: str) -> list[str]:
    """Split a comma-separated role list, ignoring commas inside parentheses."""
    out, buf, depth = [], "", 0
    for ch in s or "":
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            if buf.strip():
                out.append(buf.strip())
            buf = ""
        else:
            buf += ch
    if buf.strip():
        out.append(buf.strip())
    return out


def norm_code(prefix: str, num: str) -> str:
    return f"{prefix} {num}"


def emit_json(obj) -> None:
    """Print obj as the one JSON object on stdout (the --json contract: nothing else goes to stdout)."""
    sys.stdout.write(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")


JSON_EXTRA: dict = {}   # structured fields a command adds to its --json object (see cli.run_json)


def json_extra(**kw) -> None:
    JSON_EXTRA.update(kw)


def write_json(path: Path, obj) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp.write_text(json.dumps(obj, indent=1, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def iso_date(v) -> str | None:
    """'2020-09-24' (or a value starting with it, e.g. an Excel datetime) -> '2020-09-24'; else None."""
    m = re.match(r"\s*(\d{4}-\d{2}-\d{2})(?!\d)", _s(v))
    if not m:
        return None
    try:
        dt.date.fromisoformat(m.group(1))
    except ValueError:
        return None
    return m.group(1)


def _abs(path) -> Path:
    """Absolute path without following symlinks (folder names are what the layout rule checks)."""
    return Path(os.path.abspath(path))


# ----------------------------------------------------------------------------- classify

def industry_names() -> list:
    """The industry reference packs shipped under references/industry/ (folders that hold an overlay.json)."""
    base = REFS / "industry"
    return sorted(d.name for d in base.iterdir() if (d / "overlay.json").is_file()) if base.is_dir() else []


def industry_arg(v: str) -> str:
    """argparse type for --industry: an unknown name exits 2 and lists what is available."""
    import argparse
    if v not in industry_names():
        raise argparse.ArgumentTypeError(f"unknown industry {v!r}; available: {', '.join(industry_names()) or 'none'}")
    return v


INDUSTRY_BANNER = "Industry reference: {} (method reference, not evidence)"


def _overlay_path(x) -> Path:
    """A bare name resolves to references/overlays/<name>.json; `industry:<name>` to
    references/industry/<name>/overlay.json (Ruling P5-16); anything with a slash or .json is a path."""
    if x.startswith("industry:"):
        return REFS / "industry" / x.split(":", 1)[1] / "overlay.json"
    if x.endswith(".json") or "/" in x or os.sep in x:
        return Path(x)
    return REFS / "overlays" / f"{x}.json"


def _flat(v):
    if isinstance(v, list):
        return "; ".join(_flat(x) for x in v)
    if isinstance(v, dict):
        return "; ".join(f"{k}: {_flat(x)}" for k, x in v.items())
    return "" if v is None else str(v)
