"""Stable keys of the library (Ruling P6-11).

- `incident_key` is "INC-" plus the first 10 hex characters of sha256 of the export's Incident Number, or of the run
  slug when that field is blank. Re-exports of the same incident give the same key.
- An LL- ID is allocated once per (incident_key, lr_id) and looked up on every later publish; it is never recomputed
  from content, so a reworded learning keeps its ID."""
from __future__ import annotations

import hashlib

from .store import LIBRARY_LL_RX, Library

INCIDENT_NUMBER_FIELD = "Incident Number"


def incident_key(w: dict) -> str:
    """The incident's key from a loaded workspace (load_ws). The run slug is read from w["slug"] when the export has
    no Incident Number (publish sets it from the run folder)."""
    fields = (w.get("incident") or {}).get("fields") or {}
    basis = str(fields.get(INCIDENT_NUMBER_FIELD) or "").strip() or str(w.get("slug") or "").strip()
    if not basis:
        raise ValueError("the export has no Incident Number and the run has no slug")
    return "INC-" + hashlib.sha256(basis.encode("utf-8")).hexdigest()[:10]


def _ids_index(lib: Library) -> dict:
    """{(incident_key, lr_id): ll_id} of the library, plus what this session has reserved, and the next number."""
    idx = lib._ll_index
    if idx is None:
        idx, top = {}, 0
        for s in lib.learnings():
            m = LIBRARY_LL_RX.match(str(s.get("ll_id", "")))
            if not m:
                continue
            idx.setdefault((s.get("incident_key"), s.get("lr_id")), s["ll_id"])
            top = max(top, int(m.group(1)))
        lib._ll_index, lib._ll_next = idx, top + 1
    return idx


def allocate(lib: Library, incident_key: str, lr_id: str) -> str:
    """The LL- ID of (incident_key, lr_id): the one the library already holds, else the next free number (reserved
    for this session, written when the snapshot is appended)."""
    idx = _ids_index(lib)
    key = (incident_key, lr_id)
    if key not in idx:
        idx[key] = f"LL-{lib._ll_next:06d}"
        lib._ll_next += 1
    return idx[key]
