"""The run manifest (<run>/run-manifest.json), retention, `purge` and the jurisdiction regimes (P3-26)."""
from __future__ import annotations

import datetime as dt
import json
import re
import shutil
import sys
from pathlib import Path

from .util import _abs, iso_date, REFS, write_json
from .workspace import is_standard_ws, MANIFEST, RUNS_DIR, valid_run_slug

RUN_MANIFEST = "run-manifest.json"
JURISDICTIONS = ("in", "uk", "us", "eu")
CLASSIFICATIONS = ("internal", "restricted", "external", "public")
RUN_FOLDER_RX = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9-]+$")
PURGE_PARTS = ("workspace", "outputs")


def run_manifest_path(ws) -> Path | None:
    """<run>/run-manifest.json for a workspace in the standard layout, else None (a legacy folder has no run)."""
    p = _abs(ws)
    return p.parent / RUN_MANIFEST if is_standard_ws(p) else None


def new_run_manifest(run: str, sha256: str = "", ingested_on: str | None = None) -> dict:
    """A fresh run manifest. export_file is always <run>.xlsx, never the export's own name (A36)."""
    return {"run": run, "export_sha256": sha256, "export_file": f"{run}.xlsx",
            "ingested_on": ingested_on or dt.date.today().isoformat(), "classification": "internal",
            "retention_review": None, "intended_use": None, "jurisdiction": [], "purged_on": None, "purged": []}


def load_run_manifest(ws) -> dict:
    """The run manifest of a workspace, or {} when there is none or it cannot be read."""
    p = run_manifest_path(ws)
    if p is None or not p.is_file():
        return {}
    try:
        m = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return m if isinstance(m, dict) else {}


def write_run_manifest(ws, sha256: str) -> None:
    """Ingest: create the run manifest, or refresh the export hash and date of an existing one (keeping the
    classification, retention date, intended use and jurisdiction a person set)."""
    p = run_manifest_path(ws)
    if p is None:
        return
    m = load_run_manifest(ws) or new_run_manifest(p.parent.name)
    m.update(run=p.parent.name, export_sha256=sha256, export_file=f"{p.parent.name}.xlsx",
             ingested_on=dt.date.today().isoformat(), purged_on=None, purged=[])
    write_json(p, m)


def regimes_for(codes) -> list:
    """The `Regimes:` entries of jurisdictions.md for each code, in order, without repeats."""
    text = (REFS / "jurisdictions.md").read_text(encoding="utf-8")
    sections = re.split(r"(?m)^## ", text)[1:]
    by_code = {}
    for s in sections:
        code, _, body = s.partition("\n")
        m = re.search(r"(?m)^Regimes:\s*(.+?)\s*$", body)
        if m:
            by_code[code.strip()] = [x.strip() for x in m.group(1).split(",") if x.strip()]
    out = []
    for c in codes or []:
        for r in by_code.get(c, []):
            if r not in out:
                out.append(r)
    return out


def statutory_line(codes) -> str | None:
    regimes = regimes_for(codes)
    return "Statutory report still required: " + "; ".join(regimes) if regimes else None


def run_handling_facts(ws) -> dict:
    """What effective_handling takes from the run manifest: {'retention_review': date|None, 'regimes': [..]}."""
    m = load_run_manifest(ws) if ws is not None else {}
    rr = m.get("retention_review")
    codes = [c for c in (m.get("jurisdiction") or []) if c in JURISDICTIONS] if isinstance(m.get("jurisdiction"), list) else []
    return {"retention_review": rr if isinstance(rr, str) and iso_date(rr) == rr else None,
            "regimes": regimes_for(codes)}


def cmd_run_manifest(a):
    ws = _abs(a.ws)
    p = run_manifest_path(ws)
    if p is None:
        sys.exit(f"{ws} is not a workspace in the standard layout <dir>/{RUNS_DIR}/<YYYY-MM-DD>-<site>-<event>/workspace; "
                 "a legacy folder has no run manifest.")
    m = load_run_manifest(ws) or new_run_manifest(p.parent.name)
    if a.intended_use is not None:
        m["intended_use"] = a.intended_use
    if a.jurisdiction is not None:
        codes = [c.strip().lower() for c in a.jurisdiction.split(",") if c.strip()]
        bad = [c for c in codes if c not in JURISDICTIONS]
        if bad:
            sys.exit(f"--jurisdiction: unknown code(s) {', '.join(bad)}; use {', '.join(JURISDICTIONS)}")
        m["jurisdiction"] = list(dict.fromkeys(codes))
    if a.retention_review is not None:
        if iso_date(a.retention_review) != a.retention_review:
            sys.exit("--retention-review must be YYYY-MM-DD")
        m["retention_review"] = a.retention_review
    if a.classification is not None:
        m["classification"] = a.classification
    write_json(p, m)
    print(f"Run manifest {p}")
    for k in ("run", "export_file", "ingested_on", "classification", "retention_review", "intended_use",
              "jurisdiction", "purged_on", "purged"):
        print(f"  {k}: {m.get(k)}")


# ----------------------------------------------------------------------------- purge

def _inside(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def purge_plan(run) -> Path:
    """The resolved run folder after every safety check; exits 1 with the reason when one fails. Only a
    real (non-symlink) run folder named <YYYY-MM-DD>-<slug> directly under pmlc-runs/, holding workspace/manifest.json,
    qualifies; a part that is a symlink, or resolves outside the run folder, refuses the whole purge."""
    raw = Path(run)
    if raw.is_symlink():
        sys.exit(f"refused: {raw} is a symlink, not a run folder")
    root = raw.resolve()
    if not (root.is_dir() and RUN_FOLDER_RX.match(root.name) and valid_run_slug(root.name)
            and root.parent.name == RUNS_DIR):
        sys.exit(f"refused: {raw} is not a run folder (<dir>/{RUNS_DIR}/<YYYY-MM-DD>-<site>-<event>)")
    if not (root / "workspace" / MANIFEST).is_file():
        sys.exit(f"refused: {raw} has no workspace/{MANIFEST}; nothing to purge, or not a run folder")
    return root


def cmd_purge(a):
    root = purge_plan(a.run)
    parts = [x for x in PURGE_PARTS if not (a.keep == "outputs" and x == "outputs")]
    targets = []
    for name in parts:
        t = root / name
        if t.is_symlink():
            sys.exit(f"refused: {t} is a symlink; remove it by hand")
        if t.exists():
            if not (_inside(t.resolve(), root) and t.resolve() != root and t.is_dir()):
                sys.exit(f"refused: {t} resolves outside the run folder")
            targets.append(t)
    if not a.yes:
        print(f"Would delete from {root}:")
        for t in targets:
            print(f"  {t}")
        print(f"  (kept: {RUN_MANIFEST}" + (", outputs" if a.keep == "outputs" else "") + ")")
        sys.exit("nothing deleted: pass --yes to delete")
    done = []
    for t in targets:
        shutil.rmtree(t)
        done.append(t.name)
    mp = root / RUN_MANIFEST
    try:
        m = json.loads(mp.read_text(encoding="utf-8")) if mp.is_file() else None
    except (OSError, ValueError):
        m = None
    if not isinstance(m, dict):
        m = new_run_manifest(root.name)
    m["purged_on"] = dt.date.today().isoformat()
    m["purged"] = sorted(set(m.get("purged") or []) | set(done)) if isinstance(m.get("purged"), list) else done
    write_json(mp, m)
    print(f"Purged {', '.join(done) or 'nothing'} from {root}; {RUN_MANIFEST} kept (purged_on {m['purged_on']})")
