"""The de-identification gate of `library publish` (spec §8.1, Ruling P6-12).

Every public line (learnings.jsonl, events.jsonl, incidents.jsonl) passes through `deidentify` before it is hashed:

1. **Zero-hit gate.** A scan-names pass over every string of every line, with the names from --names or PMLC_NAMES,
   must find nothing. A listed name is refused, never masked: the register's wording is fixed (a role, not a name).
2. **Sites.** The site (--site, else the export's Site or Location field) gets a code S01, S02 ... kept in
   private/sites.json, and every site the library knows is replaced by its code wherever it appears.
3. **Masking.** The text goes through the `--share external` transform (privacy.share_text): name variants and
   honorific forms, organisations (--orgs, PMLC_ORGS and company suffixes), equipment tags and singleton roles are
   masked, clock times are removed (strip_times) and dates are rounded to the month (coarsen_dates).
4. **Residual scan.** The masked lines are scanned again for the listed names, organisations and site names; any hit
   refuses the publish.

Only free text is masked: IDs, references, hashes and the YYYY-MM months are kept as they are. A refusal raises
LibraryError (exit 1) before anything is written."""
from __future__ import annotations

import copy
import re

from .. import privacy
from .store import LIBRARY_SITE_RX, LibraryError

SITE_FIELDS = ("Site", "Location")
# Keys inside a learning or an event's data whose values are IDs, never prose: kept as written.
DEID_ID_KEYS = frozenset({"id", "finding_refs", "evidence_refs", "lr_id", "ll_id", "snapshot_id", "supersedes",
                          "after", "event_hash", "incident_key", "content_hash"})
DEID_LISTED_NAME = ("library publish refused: {n} listed name{s} in the public lines (from --names or PMLC_NAMES), "
                    "so nothing was written. Name a role instead in the register, then publish again")
DEID_RESIDUAL = ("library publish refused: {n} identifying detail{s} (a listed name, organisation or site) left in the "
                 "public lines after masking, so nothing was written")
_DEID_OPEN, _DEID_CLOSE = "", ""     # a site placeholder no share_text rule touches


def _deid_norm(site) -> str:
    return " ".join(str(site or "").split())


def site_code(lib, site: str) -> str:
    """The code of a site in this library: the one private/sites.json holds (names compared ignoring case and spacing),
    else the next free S-number, reserved for this session and written by Library.write_sites."""
    name = _deid_norm(site)
    if not name:
        raise LibraryError("a site name is blank, so it cannot be coded")
    sites = lib.sites()
    for k, v in sites.items():
        if _deid_norm(k).casefold() == name.casefold():
            return v
    nums = [int(m.group(1)) for m in (LIBRARY_SITE_RX.match(str(v)) for v in sites.values()) if m]
    code = f"S{(max(nums) + 1 if nums else 1):02d}"
    sites[name] = code
    lib.sites_changed = True
    return code


def incident_site(ctx: dict) -> str:
    """The run's real site name: --site, else the export's Site or Location field ('' when none is known)."""
    site = _deid_norm(ctx.get("site"))
    if site:
        return site
    fields = ((ctx.get("w") or {}).get("incident") or {}).get("fields") or {}
    return next((_deid_norm(fields[f]) for f in SITE_FIELDS if _deid_norm(fields.get(f))), "")


def _deid_strings(v):
    if isinstance(v, str):
        yield v
    elif isinstance(v, list):
        for x in v:
            yield from _deid_strings(x)
    elif isinstance(v, dict):
        for x in v.values():
            yield from _deid_strings(x)


def _deid_count(rx, lines) -> int:
    return sum(len(rx.findall(s)) for _, obj in lines for s in _deid_strings(obj)) if rx else 0


def deidentify(lines: list, ctx: dict) -> list:
    """lines is [(file, obj)]; returns de-identified copies in the same order, or raises LibraryError (exit 1).
    ctx: library, w (the loaded workspace), site (--site), names (--names), orgs (--orgs)."""
    lib = ctx["library"]
    names = privacy.load_names(ctx.get("names"))
    n = _deid_count(privacy.name_pattern(names), lines)
    if n:
        raise LibraryError(DEID_LISTED_NAME.format(n=n, s="" if n == 1 else "s"), 1)

    site = incident_site(ctx)
    code = site_code(lib, site) if site else None
    for _, obj in lines:                      # code every event's site first, so the text pass knows it too
        data = obj.get("data") if isinstance(obj, dict) else None
        if isinstance(data, dict) and isinstance(data.get("site"), str) and data["site"].strip():
            site_code(lib, data["site"])
    w = ctx.get("w") or {}
    share = privacy.ShareCtx("external", names, privacy.load_orgs(ctx.get("orgs")), privacy.load_singletons(w))
    sites = sorted(lib.sites().items(), key=lambda kv: len(_deid_norm(kv[0])), reverse=True)
    codes = [c for _, c in sites]
    site_rx = privacy.name_pattern([k for k, _ in sites])
    by_name = {_deid_norm(k).casefold(): i for i, (k, _) in enumerate(sites)}

    def text(s: str) -> str:
        if site_rx:
            s = site_rx.sub(lambda m: f"{_DEID_OPEN}{by_name[_deid_norm(m.group(0)).casefold()]}{_DEID_CLOSE}", s)
        s = privacy.share_text(s, share)
        return re.sub(_DEID_OPEN + r"(\d+)" + _DEID_CLOSE, lambda m: codes[int(m.group(1))], s)

    def walk(v, key=None):
        if key in DEID_ID_KEYS:
            return v
        if key == "site" and isinstance(v, str) and v.strip():
            return site_code(lib, v)          # an event's site field (site assessments) is always a code
        if isinstance(v, str):
            return text(v)
        if isinstance(v, list):
            return [walk(x) for x in v]
        if isinstance(v, dict):
            return {k: walk(x, k) for k, x in v.items()}
        return v

    out = []
    for f, obj in lines:
        obj = copy.deepcopy(obj)
        if f == "learnings.jsonl" and isinstance(obj.get("learning"), dict):
            obj["learning"] = walk(obj["learning"])
        elif f == "events.jsonl" and isinstance(obj.get("data"), dict):
            obj["data"] = walk(obj["data"])
        elif f == "incidents.jsonl" and code:
            obj["site_code"] = code
        out.append((f, obj))

    rx = privacy.name_pattern(list(names) + list(share.orgs) + [k for k, _ in lib.sites().items()])
    n = _deid_count(rx, out)
    if n:
        raise LibraryError(DEID_RESIDUAL.format(n=n, s="" if n == 1 else "s"), 1)
    return out

