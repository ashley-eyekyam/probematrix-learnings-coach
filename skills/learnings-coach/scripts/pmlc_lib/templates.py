"""The files the organisation fills in (adoption.csv, distribution.csv, verification.jsonl): the `templates` command
that writes them, and the loaders that read them back. The engine prefills only ids and titles; every column that
records an organisational decision is written blank (D7)."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

from .workspace import is_standard_ws, outputs_dir

ADOPTION_COLUMNS = ["lr_id", "title", "response", "reason", "owning_role", "target_window"]
DISTRIBUTION_COLUMNS = ["pack", "audience", "channel", "date", "delivered_by_role", "attendees",
                        "contractors_included", "questions_raised", "concerns_escalated"]
VERIFICATION_KEYS = ["lr_id", "check_date", "level", "evidence", "assessed_by_role"]
RESPONSES = ("accepted", "modified", "rejected")
YES_NO = ("yes", "no")
VERIFICATION_LEVELS = ("communicated", "understood", "applied", "effective")
FILES = {"adoption": "adoption.csv", "distribution": "distribution.csv", "verification": "verification.jsonl"}
REGISTER_FILE = "learnings-register.json"


class OrgFileError(Exception):
    """A file the organisation filled in holds an invalid value; the message names the file and row."""


# ----------------------------------------------------------------------------- locating files

def _outputs(run) -> Path:
    """The outputs folder for a run folder, a workspace or an outputs folder."""
    p = Path(run)
    if (p / "findings.json").is_file():
        return outputs_dir(p)
    if (p / "outputs").is_dir():
        return p / "outputs"
    if p.name == "workspace" and is_standard_ws(p):
        return p.parent / "outputs"
    return p


def pack_files(out: Path) -> list:
    """The learning pack JSON files in an outputs folder, as (path, document), sorted by file name."""
    found = []
    for f in sorted(out.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(d, dict) and d.get("pack") and isinstance(d.get("sections"), list):
            found.append((f, d))
    return found


def load_register_entries(path) -> list:
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    return d["entries"] if isinstance(d, dict) else d


# ----------------------------------------------------------------------------- loaders

def _read_csv(run, name: str, columns: list) -> list:
    f = _outputs(run) / name
    if not f.is_file():
        return []
    with open(f, encoding="utf-8-sig", newline="") as fh:
        rd = csv.reader(fh)
        header = next(rd, None)
        if header is None:
            return []
        keys = [h.strip().lower() for h in header]
        rows = []
        for n, cells in enumerate(rd, 2):
            vals = [c.strip() for c in cells]
            if not any(vals):
                continue
            row = {c: "" for c in columns}
            for k, v in zip(keys, vals):
                if k:
                    row[k] = v
            row["_row"] = n
            rows.append(row)
    return rows


def _check_enum(row: dict, name: str, col: str, allowed: tuple) -> None:
    v = row.get(col, "")
    if v == "":
        return
    if v.lower() not in allowed:
        raise OrgFileError(f"{name} row {row['_row']}: {col} '{v}' must be one of {', '.join(allowed)} (or blank)")
    row[col] = v.lower()


def load_adoption(run) -> list:
    rows = _read_csv(run, FILES["adoption"], ADOPTION_COLUMNS)
    for r in rows:
        _check_enum(r, "adoption.csv", "response", RESPONSES)
    return rows


def load_distribution(run) -> list:
    rows = _read_csv(run, FILES["distribution"], DISTRIBUTION_COLUMNS)
    for r in rows:
        _check_enum(r, "distribution.csv", "contractors_included", YES_NO)
    return rows


def load_verification(run) -> list:
    f = _outputs(run) / FILES["verification"]
    if not f.is_file():
        return []
    rows = []
    with open(f, encoding="utf-8-sig", newline="") as fh:
        for n, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                d = json.loads(line)
            except ValueError as e:
                raise OrgFileError(f"verification.jsonl line {n}: not valid JSON ({e})") from None
            if not isinstance(d, dict):
                raise OrgFileError(f"verification.jsonl line {n}: each line must be a JSON object")
            if not d.get("lr_id"):
                raise OrgFileError(f"verification.jsonl line {n}: lr_id is required")
            lvl = d.get("level")
            if lvl is not None and str(lvl).strip() != "":
                if str(lvl).strip().lower() not in VERIFICATION_LEVELS:
                    raise OrgFileError(f"verification.jsonl line {n}: level '{lvl}' must be one of "
                                       f"{', '.join(VERIFICATION_LEVELS)} (or null)")
                d["level"] = str(lvl).strip().lower()
            for k in VERIFICATION_KEYS:
                d.setdefault(k, None)
            d["_row"] = n
            rows.append(d)
    return rows


# ----------------------------------------------------------------------------- the command

def _write_csv(path: Path, columns: list, rows: list) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\r\n")
        w.writerow(columns)
        for r in rows:
            w.writerow([r.get(c, "") for c in columns])


def cmd_templates(a):
    ws = Path(a.ws)
    out_dir = outputs_dir(ws)
    target = Path(a.out) if a.out else out_dir / FILES[a.mode]
    if target.exists():
        sys.exit(f"{target} already exists and may hold your organisation's entries; move it or pass a new --out")
    if a.mode == "distribution":
        rows = [{"pack": d["pack"], "audience": d.get("audience", "")} for _, d in pack_files(out_dir)]
    else:
        reg = Path(a.register) if a.register else out_dir / REGISTER_FILE
        if not reg.is_file():
            sys.exit(f"No Learnings Register at {reg}: write it first, or pass --register FILE")
        entries = load_register_entries(reg)
        rows = [{"lr_id": e.get("lr_id", ""), "title": e.get("title", "")} for e in entries]
    target.parent.mkdir(parents=True, exist_ok=True)
    if a.mode == "adoption":
        _write_csv(target, ADOPTION_COLUMNS, rows)
    elif a.mode == "distribution":
        _write_csv(target, DISTRIBUTION_COLUMNS, rows)
    else:
        with open(target, "w", encoding="utf-8", newline="") as fh:
            for r in rows:
                fh.write(json.dumps({"lr_id": r["lr_id"], "check_date": None, "level": None, "evidence": None,
                                     "assessed_by_role": None}) + "\n")
    print(f"wrote {target} ({len(rows)} row{'s' if len(rows) != 1 else ''}); the organisation fills in the blank columns")
