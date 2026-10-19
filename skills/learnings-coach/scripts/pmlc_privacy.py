"""Privacy core: names, organisations and equipment tags, shared by check-language and the share tools.
This is the first part (names and orgs files, the tag pattern); the singleton map and share transforms follow."""
from __future__ import annotations

import os
import re
from pathlib import Path

# Equipment tags such as AO-101 or PSV12A: letters then digits. Finding, Evidence, LR and ML IDs are not tags.
TAG_RX = re.compile(r"\b(?!(?:FND|EVD|LR|ML)-)[A-Z]{1,5}-?\d{2,6}[A-Z]?\b")


def _list_file(path, env) -> list:
    """Stripped lines of a text file, skipping blank lines and lines starting with '#'. A staff ID is written
    'ID #4471', so it is kept. The path falls back to the environment variable env; neither gives []."""
    p = path or os.environ.get(env)
    if not p:
        return []
    out = []
    for line in Path(p).read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#") and s not in out:
            out.append(s)
    return out


def load_names(path=None) -> list:
    """Names from a names file (one per line), falling back to PMLC_NAMES."""
    return _list_file(path, "PMLC_NAMES")


def load_orgs(path=None) -> list:
    """Organisation names from an orgs file (one per line), falling back to PMLC_ORGS."""
    return _list_file(path, "PMLC_ORGS")
