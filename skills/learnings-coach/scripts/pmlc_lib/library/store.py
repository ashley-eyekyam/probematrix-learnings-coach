"""The library's append-only store (spec §8.1, Ruling P6-11): a folder the user chooses, holding JSON Lines files.

    library.json            {"kind": "pmlc-library", "version": 1}, written when the folder is new or empty
    learnings.jsonl         learning snapshots, never edited; a changed learning appends a superseding snapshot
    events.jsonl            status changes, site assessments, verification readings, withdrawals and merges
    incidents.jsonl         one line per published state of an incident (the latest line for a key is current)
    private/sites.json      real site name -> S01..., never published (Task 16)
    private/contexts.jsonl  each snapshot's original context, never published

Nothing here edits or deletes a line. `validate()` lists every problem of the files as they stand, so `publish` can
refuse before it writes anything."""
from __future__ import annotations

import json
import re
from pathlib import Path

# Fixed copy (Phase 6, verbatim).
LIBRARY_NOT_SET = "no library folder: pass --library <dir> or set PMLC_LIBRARY"
LIBRARY_HEADER = {"kind": "pmlc-library", "version": 1}
LIBRARY_FILES = ("learnings.jsonl", "events.jsonl", "incidents.jsonl")
LIBRARY_PRIVATE = ("private/contexts.jsonl",)
LIBRARY_LL_RX = re.compile(r"^LL-(\d{6})$")
# The keys each line must carry before publish trusts the file.
LIBRARY_REQUIRED = {
    "learnings.jsonl": ("ll_id", "snapshot_id", "incident_key", "lr_id", "content_hash", "learning"),
    "events.jsonl": ("event_hash", "type", "ll_id", "incident_key"),
    "incidents.jsonl": ("incident_key", "learnings"),
    "private/contexts.jsonl": ("ll_id", "snapshot_id"),
}


class LibraryError(Exception):
    """A library that cannot be used: the message is one plain sentence, `code` the exit code."""

    def __init__(self, message: str, code: int = 2):
        super().__init__(message)
        self.code = code


def canonical(obj) -> str:
    """The one JSON spelling of an object: sorted keys, no spaces, UTF-8 kept (what hashes and lines use)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class Library:
    """An opened library folder. `new` is True while the folder holds no library yet (publish creates it)."""

    def __init__(self, path: Path, new: bool = False):
        self.path = Path(path)
        self.new = new
        self._rows = {}
        self._ll_index = None       # ids.allocate's index, built on first use
        self._ll_next = 1

    # ---- reading
    def _raw(self, name: str) -> str:
        p = self.path / name
        return p.read_text(encoding="utf-8") if p.is_file() else ""

    def rows(self, name: str) -> list:
        """The parsed lines of one file (bad lines are skipped: validate() reports them)."""
        if name not in self._rows:
            out = []
            for line in self._raw(name).splitlines():
                try:
                    v = json.loads(line)
                except ValueError:
                    continue
                if isinstance(v, dict):
                    out.append(v)
            self._rows[name] = out
        return self._rows[name]

    def learnings(self) -> list:
        return self.rows("learnings.jsonl")

    def events(self) -> list:
        return self.rows("events.jsonl")

    def incidents(self) -> list:
        return self.rows("incidents.jsonl")

    def contexts(self) -> list:
        return self.rows("private/contexts.jsonl")

    # ---- checking
    def validate(self) -> list:
        """Every problem of the files as they stand, one sentence each (empty when the library is sound)."""
        probs = []
        for name in LIBRARY_FILES + LIBRARY_PRIVATE:
            raw = self._raw(name)
            if raw and not raw.endswith("\n"):
                probs.append(f"{name}: the last line is cut short (it has no line end)")
            for n, line in enumerate(raw.splitlines(), 1):
                try:
                    v = json.loads(line)
                except ValueError:
                    probs.append(f"{name} line {n} is not valid JSON")
                    continue
                if not isinstance(v, dict):
                    probs.append(f"{name} line {n} is not a JSON object")
                    continue
                miss = [k for k in LIBRARY_REQUIRED[name] if k not in v]
                if miss:
                    probs.append(f"{name} line {n} has no {', '.join(miss)}")
        owner, keyed, snaps = {}, {}, set()
        for n, s in enumerate(self.learnings(), 1):
            ll, key = s.get("ll_id"), (s.get("incident_key"), s.get("lr_id"))
            if not isinstance(ll, str) or not LIBRARY_LL_RX.match(ll):
                probs.append(f"learnings.jsonl: {ll!r} is not an LL- ID")
                continue
            if owner.setdefault(ll, key) != key:
                probs.append(f"learnings.jsonl: {ll} is used for two learnings "
                             f"({owner[ll][0]}/{owner[ll][1]} and {key[0]}/{key[1]})")
            if keyed.setdefault(key, ll) != ll:
                probs.append(f"learnings.jsonl: the learning {key[0]}/{key[1]} has two LL- IDs "
                             f"({keyed[key]} and {ll})")
            sid = s.get("snapshot_id")
            if sid in snaps:
                probs.append(f"learnings.jsonl: the snapshot {sid} appears twice")
            snaps.add(sid)
        return list(dict.fromkeys(probs))

    # ---- writing
    def init(self) -> None:
        """Write library.json into a new or empty folder."""
        self.path.mkdir(parents=True, exist_ok=True)
        (self.path / "library.json").write_text(json.dumps(LIBRARY_HEADER, indent=1, sort_keys=True) + "\n",
                                                encoding="utf-8")
        for name in LIBRARY_FILES:          # the three public files exist from the first publish, even when empty
            (self.path / name).touch()
        self.new = False

    def append(self, name: str, lines: list) -> None:
        """Append canonical lines to one file in a single write."""
        if not lines:
            return
        p = self.path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8", newline="\n") as fh:
            fh.write("".join(canonical(x) + "\n" for x in lines))
        self._rows.pop(name, None)


def open_library(path, create: bool = False) -> Library:
    """The library at path. A missing or empty folder is a new library (written only when create is True). Raises
    LibraryError with LIBRARY_NOT_SET when no path is given, and one sentence when the folder is not a library."""
    if not path:
        raise LibraryError(LIBRARY_NOT_SET)
    p = Path(path)
    if p.exists() and not p.is_dir():
        raise LibraryError(f"{p} is not a library: it is a file, not a folder")
    head = p / "library.json"
    if head.is_file():
        try:
            d = json.loads(head.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            d = None
        if not (isinstance(d, dict) and d.get("kind") == LIBRARY_HEADER["kind"]):
            raise LibraryError(f"{p} is not a library: its library.json is not a pmlc library header")
        if d.get("version") != LIBRARY_HEADER["version"]:
            raise LibraryError(f"{p} is a library of version {d.get('version')!r}; this engine reads version "
                               f"{LIBRARY_HEADER['version']}")
        return Library(p)
    if p.is_dir() and any(p.iterdir()):
        raise LibraryError(f"{p} is not a library: it holds other files and no library.json; choose a new or "
                           "empty folder")
    lib = Library(p, new=True)
    if create:
        lib.init()
    return lib
