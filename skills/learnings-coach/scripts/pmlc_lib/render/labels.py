"""Render labels (Ruling P4-15): references/labels/<locale>.json is a flat object of _language, _dir (ltr|rtl),
_review (null or a note) and the f.<field>, k.<kind> and ui.<name> keys. Missing keys fall back to English."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from ..util import REFS

LABELS_DIR = REFS / "labels"
LOCALE_RX = re.compile(r"^[a-z]{2,3}(-[A-Za-z0-9]{2,8})*$")      # BCP 47, as the pack's `lang`


def _lb_dirs() -> list:
    """Where locale files are looked up: $PMLC_LABELS_DIR first (tests only), then references/labels/."""
    extra = os.environ.get("PMLC_LABELS_DIR")
    return ([Path(extra)] if extra else []) + [LABELS_DIR]


def _lb_read(path: Path) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(d, dict):
        raise ValueError(f"{path}: a labels file is a JSON object")
    return d


def load_labels(locale: str = "en") -> dict:
    """The labels for locale, merged over English. English itself is references/labels/en.json, with an en.json in
    $PMLC_LABELS_DIR laid over it; another locale is the first <locale>.json found in _lb_dirs()."""
    if not isinstance(locale, str) or not LOCALE_RX.fullmatch(locale):
        raise ValueError(f"{locale!r} is not a language tag such as en or hi")
    out = _lb_read(LABELS_DIR / "en.json")
    dirs = _lb_dirs()
    if locale == "en":
        for d in dirs[:-1]:
            if (d / "en.json").is_file():
                out.update(_lb_read(d / "en.json"))
        return out
    for d in dirs:
        if (d / f"{locale}.json").is_file():
            out.update(_lb_read(d / f"{locale}.json"))
            break
    return out


def label(labels: dict, key: str, **fmt) -> str:
    """labels[key], formatted with fmt. A missing key is a KeyError, never a silent blank (a drift guard)."""
    v = labels[key]
    return v.format(**fmt) if fmt else v


def text_dir(labels: dict) -> str:
    """"rtl" or "ltr", from the labels' _dir."""
    return "rtl" if labels.get("_dir") == "rtl" else "ltr"
