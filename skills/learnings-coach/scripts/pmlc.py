#!/usr/bin/env python3
"""pmlc: the ProbeMatrix Learnings Coach engine. The code lives in the pmlc_lib package next to this file; this
shim keeps `python3 pmlc.py <subcommand>` and `import pmlc` working (every v1 name stays reachable as pmlc.X).
Run `python3 pmlc.py -h` for the subcommands."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from pmlc_lib import _compat, cli  # noqa: E402

_compat.export(globals(), _compat.MODULES)
__doc__ = cli.__doc__  # the subcommand list, as in v1


def _pack_module():
    """v1 helper: the pack module (now the pmlc_pack shim over pmlc_lib.pack)."""
    import pmlc_pack
    return pmlc_pack


def _lint_module():
    import pmlc_lint
    return pmlc_lint


if __name__ == "__main__":
    sys.exit(cli.main())
