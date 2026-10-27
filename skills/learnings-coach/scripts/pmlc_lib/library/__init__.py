"""The persistent learnings library (spec §8.1; Phase 6 builds storage and publish only).

`pmlc library publish <ws>` appends a finished run's learnings to an opt-in folder (`--library` or `PMLC_LIBRARY`)
of append-only JSON Lines files, with stable LL- IDs and incident-qualified references."""
from __future__ import annotations

from .ids import allocate, incident_key
from .publish import cmd_library, plan_publish, snapshot
from .store import LIBRARY_NOT_SET, Library, LibraryError, open_library

__all__ = ["LIBRARY_NOT_SET", "Library", "LibraryError", "allocate", "cmd_library", "incident_key", "open_library",
           "plan_publish", "snapshot"]
