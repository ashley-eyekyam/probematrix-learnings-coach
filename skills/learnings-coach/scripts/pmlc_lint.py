"""Shim: the v1 module pmlc_lint, now pmlc_lib (LINT_MODULES in pmlc_lib/_compat.py). Kept for the whole of v2.0."""
from __future__ import annotations

import sys
from pathlib import Path

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from pmlc_lib import _compat  # noqa: E402

_compat.export(globals(), _compat.LINT_MODULES)

import pmlc as core  # noqa: E402,F401  (v1 name: pmlc_lint.core)
