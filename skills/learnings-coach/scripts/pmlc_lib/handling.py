"""The handling block, forced draft, content hash, sign-off and the --share gate."""
from __future__ import annotations

import argparse
import contextlib
import copy
import datetime as dt
import hashlib
import html
import io
import json
import re
import sys
from pathlib import Path

from . import AI_STATUS, DRAFT_LABEL, STATUS_PHRASE
from .classify import _load_taxonomy, map_role, TIER_LABELS
from .util import _overlay_path, _s, iso_date, write_json
from .workspace import _save_manifest, load_manifest, load_ws, sign_off_entry
from . import lint
from . import privacy


# ----------------------------------------------------------------------------- handling and sign-off

HANDLING_DEFAULTS = {"status": "draft", "classification": "internal", "legal_review": "not-required",
                     "distribution": [], "version": "1.0"}
HANDLING_KEYS = ("status", "reviewer_role", "reviewed_on", "classification", "legal_review", "distribution",
                 "version", "retention_review", "content_hash")
HANDLING_ENUMS = {"status": ("draft", "reviewed", "approved"),
                  "classification": ("internal", "restricted", "external", "public"),
                  "legal_review": ("not-required", "requested", "cleared")}
REASON_IN_PROGRESS = "the investigation status is in progress"
REASON_UNEDITED = "no finding is marked as edited by a person"
REASON_NOT_COMPLETED = "the investigation status is not completed"
EDITED_YES = ("yes", "y", "true", "1")
REASON_EDITED_SINCE = "edited since sign-off"
REASON_NOT_SIGNED = "not signed off"
REASON_INVALID = "invalid handling block"
REASON_NO_WORKSPACE = "no workspace to check"
WARN_NO_HANDLING = "no handling block: rendered as draft (internal)"
WARN_EDITED_SINCE = "edited since sign-off: status is draft until signed off again"
WARN_NOT_SIGNED = "not signed off in this workspace: status is draft until sign-off records it"
_HASH_RX = re.compile(r"sha256:[0-9a-f]{64}")


def _norm_status(v) -> str:
    """An Investigation Status as a key: lower case, stripped, spaces and hyphens as underscores."""
    return re.sub(r"[\s-]+", "_", _s(v).strip().lower())


def is_edited(v) -> bool:
    """A User Edited cell marks a finding as edited by a person only when it reads yes, y, true or 1."""
    return _s(v).strip().lower() in EDITED_YES


def forced_draft_reasons(w) -> list:
    """Why nothing from this workspace may be reviewed or approved yet (empty when it may be). X26: anything but a
    completed investigation is forced (ProbeMatrix statuses are draft, in_progress and completed), and only an
    explicit yes in User Edited counts. No workspace ({}) gives no reasons: there is nothing to read."""
    if not w:
        return []
    out = []
    status = _norm_status(((w.get("incident") or {}).get("fields") or {}).get("Investigation Status"))
    if status != "completed":
        out.append(REASON_IN_PROGRESS if status == "in_progress" else REASON_NOT_COMPLETED)
    F = w.get("findings") or []
    if F and not any(is_edited(f.get("user_edited")) for f in F):
        out.append(REASON_UNEDITED)
    return out


def content_hash(doc: dict) -> str:
    """sha256 of the document without its handling block (key order and whitespace do not matter)."""
    body = {k: v for k, v in doc.items() if k != "handling"}
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _hash_mismatch(doc) -> bool:
    h = doc.get("handling") if isinstance(doc, dict) else None
    return isinstance(h, dict) and isinstance(h.get("content_hash"), str) and h["content_hash"] != content_hash(doc)


def check_handling(doc) -> tuple:
    """(problems, warnings) for a pack's or register's handling block."""
    if not isinstance(doc, dict):
        return [], []
    if "handling" not in doc:
        return [], [WARN_NO_HANDLING]
    h = doc["handling"]
    if not isinstance(h, dict):
        return ["handling: must be an object"], []
    P, W = [], []
    for k, v in h.items():
        if k not in HANDLING_KEYS:
            P.append(f"handling.{k}: unknown key; use {', '.join(HANDLING_KEYS)}")
        elif k in HANDLING_ENUMS and v not in HANDLING_ENUMS[k]:
            P.append(f"handling.{k}: must be one of {', '.join(HANDLING_ENUMS[k])}")
        elif k in ("reviewed_on", "retention_review") and not (isinstance(v, str) and iso_date(v) == v):
            P.append(f"handling.{k}: must be YYYY-MM-DD")
        elif k == "content_hash" and not (isinstance(v, str) and _HASH_RX.fullmatch(v)):
            P.append(f"handling.{k}: must be sha256:<64 hex digits>")
        elif k in ("reviewer_role", "version") and not (isinstance(v, str) and v.strip()):
            P.append(f"handling.{k}: must be non-empty text")
        elif k == "distribution" and not (isinstance(v, list) and all(isinstance(x, str) for x in v)):
            P.append(f"handling.{k}: must be a list of audience names")
    if h.get("status") in ("reviewed", "approved"):
        for k in ("reviewer_role", "reviewed_on", "content_hash"):
            if k not in h:
                P.append(f"handling.{k}: required when status is {h['status']}")
        if _hash_mismatch(doc):
            W.append(WARN_EDITED_SINCE)
    return P, W


def sign_off_record(ws, src):
    """The manifest's sign-off record for the file at src, or None: it must be under the file's name and carry the
    file's resolved path (a copy elsewhere, or in another workspace, has no record)."""
    if ws is None or src is None:
        return None
    rec = sign_off_entry(load_manifest(Path(ws)), src)
    return rec if rec is not None and rec.get("path") == str(Path(src).resolve()) else None


def _signed_here(h: dict, ws, src) -> bool:
    """X25: a reviewed or approved block counts only when sign-off recorded this very block for this file in this
    workspace. Every handling key must match the record, so a hand edit of classification or legal_review (which
    the content hash leaves out) does not count either."""
    rec = sign_off_record(ws, src)
    return rec is not None and all(rec.get(k) == h.get(k) for k in HANDLING_KEYS)


def effective_handling(doc, w, src=None, ws=None) -> dict:
    """The handling that applies: defaults merged with the block, forced down to draft when it must be. src is the
    document's file and ws its workspace folder: a reviewed or approved status holds only when the workspace's
    manifest records a sign-off of this block for this file (X25). Without ws the reason is 'no workspace to check'."""
    h = doc.get("handling") if isinstance(doc, dict) else None
    out = {**HANDLING_DEFAULTS, **{k: v for k, v in (h if isinstance(h, dict) else {}).items() if k in HANDLING_KEYS}}
    out["distribution"] = list(out["distribution"]) if isinstance(out["distribution"], list) else []
    for k, ok in HANDLING_ENUMS.items():  # an invalid value never passes through as effective
        if out.get(k) not in ok:
            out[k] = HANDLING_DEFAULTS[k]
    reasons = forced_draft_reasons(w)
    problems = check_handling(doc)[0] if isinstance(h, dict) else []
    claims = isinstance(h, dict) and h.get("status") in ("reviewed", "approved")
    if problems:
        reasons.append(REASON_INVALID)
    if claims:
        if _hash_mismatch(doc):
            reasons.append(REASON_EDITED_SINCE)
        elif not (isinstance(h.get("content_hash"), str) and not problems):
            reasons.append(REASON_NOT_SIGNED)
        elif ws is None:
            reasons.append(REASON_NO_WORKSPACE)
        elif not _signed_here(h, ws, src):
            reasons.append(REASON_NOT_SIGNED)
    out["draft_reasons"] = list(dict.fromkeys(reasons))
    signed = claims and not reasons
    out["effective_status"] = h["status"] if signed else "draft"
    return out


def unsigned_warning(doc, w, src, ws) -> list:
    """[WARN_NOT_SIGNED] when the file claims reviewed or approved but this workspace has no sign-off record of it."""
    if not (isinstance(doc, dict) and isinstance(doc.get("handling"), dict)):
        return []
    return [WARN_NOT_SIGNED] if REASON_NOT_SIGNED in effective_handling(doc, w, src=src, ws=ws)["draft_reasons"] else []


RIBBON_HTML = f'<div class="ribbon" role="note">{DRAFT_LABEL}</div>'
# The per-page status in print: a page margin box, so every printed page carries it.
PAGE_FOOTER_CSS = f'@page{{@bottom-center{{content:"{STATUS_PHRASE} · ProbeMatrix Learnings Coach"}}}}'
# The DRAFT ribbon and handling line, shared by the pack page and the dashboard. In print the ribbon keeps a
# border and its text, so it never depends on colour alone.
HANDLING_CSS = PAGE_FOOTER_CSS + """
.ribbon{display:inline-block;border:2px solid var(--warn,#c2410c);color:var(--warn,#c2410c);font-weight:700;letter-spacing:.12em;padding:2px 12px;border-radius:4px;margin:0 0 8px}
p.handling{color:var(--mut);font-size:13px;margin:0 0 6px}
@media print{.ribbon{border:2px solid #000;color:#000;background:none}}"""


def is_draft(eh: dict) -> bool:
    """True when the DRAFT ribbon must show: anything short of an effective approval."""
    return eh["effective_status"] != "approved"


def review_text(eh: dict) -> str:
    """'approved by <role> on <date>', or the bare effective status (no reviewer for a status that does not hold)."""
    st = eh["effective_status"]
    who = (f" by {eh['reviewer_role']} on {eh['reviewed_on']}"
           if st != "draft" and eh.get("reviewer_role") and eh.get("reviewed_on") else "")
    return st + who


def handling_lines(eh: dict) -> list:
    """The handling line, then 'Draft because: ...' when there are reasons."""
    out = [f"Review: {review_text(eh)} · Classification: {eh['classification']} · Version {eh['version']}"]
    if eh["draft_reasons"]:
        out.append("Draft because: " + "; ".join(eh["draft_reasons"]))
    return out


def status_line(status="") -> str:
    """A document's status text, always carrying STATUS_PHRASE and AI_STATUS (each once)."""
    s = _s(status)
    bits = ([] if STATUS_PHRASE in s else [STATUS_PHRASE]) + ([s] if s else [])
    return " · ".join(bits + ([] if AI_STATUS in s else [AI_STATUS]))


def record_sign_off(ws, path, h: dict) -> None:
    """The whole handling block sign-off wrote, with the file's resolved path (effective_handling checks both)."""
    m = load_manifest(Path(ws))
    m.setdefault("sign_offs", {})[Path(path).name] = {
        **{k: copy.deepcopy(h[k]) for k in HANDLING_KEYS if k in h}, "path": str(Path(path).resolve())}
    _save_manifest(ws, m)


ROLE_NAME_REFUSAL = '{flag}: looks like a personal name ("{match}"); give a role'


def _refuse_names_in_roles(a, w) -> None:
    """D7 and just culture: the reviewer and the audiences are roles, never people (JC1, with --names)."""
    names = privacy.load_names(getattr(a, "names", None))
    for flag, vals in (("--role", [a.role]), ("--distribution", a.distribution or [])):
        for v in vals:
            hit = lint.personal_name(v, w, names)
            if hit:
                sys.exit(ROLE_NAME_REFUSAL.format(flag=flag, match=hit))


def cmd_sign_off(a):
    from .pack.schema import check_pack   # both import this module
    from .register.check import cmd_check_register
    w = load_ws(a.ws)
    _refuse_names_in_roles(a, w)
    path = Path(a.file)
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        sys.exit(f"cannot read {path} as JSON ({e.__class__.__name__})")
    if isinstance(doc, list):
        sys.exit('wrap the entries as {"entries": [...]} before signing off')
    if not isinstance(doc, dict):
        sys.exit(f"{path} must be a JSON object")
    reasons = forced_draft_reasons(w)
    if reasons:
        sys.exit("cannot sign off: " + "; ".join(reasons))
    # M3: the check runs at the classification the file will have, so an external sign-off meets the external rules
    old = doc.get("handling") if isinstance(doc.get("handling"), dict) else {}
    target = a.classification or old.get("classification") or HANDLING_DEFAULTS["classification"]
    names = privacy.load_names(getattr(a, "names", None))
    if "pack" in doc:
        problems = check_pack(doc, w, share=target, names=names).problems
    elif "entries" in doc:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                cmd_check_register(argparse.Namespace(ws=a.ws, register=str(path), share=target, names=a.names))
                problems = []
            except SystemExit as e:
                problems = [x for x in buf.getvalue().splitlines() if x.startswith(" - ")] if e.code else []
                if e.code and not problems:
                    problems = [f"check-register failed ({e.code})"]
    else:
        sys.exit(f"{path} is neither a pack (no 'pack' key) nor a register (no 'entries')")
    if problems:
        sys.exit("cannot sign off: the file has problems; run the check and fix them first\n" + "\n".join(problems[:20]))
    h = dict(doc.get("handling") or {}) if isinstance(doc.get("handling"), dict) else {}
    h.pop("content_hash", None)
    h.update(status=a.status, reviewer_role=a.role, reviewed_on=a.date or dt.date.today().isoformat())
    for k in ("classification", "legal_review", "version", "retention_review"):
        if getattr(a, k) is not None:
            h[k] = getattr(a, k)
    if a.distribution:
        h["distribution"] = list(a.distribution)
    doc["handling"] = h
    h["content_hash"] = content_hash(doc)
    bad, _ = check_handling(doc)
    if bad:
        sys.exit("cannot sign off: " + "; ".join(bad))
    write_json(path, doc)
    record_sign_off(a.ws, path, h)
    print(f"Signed off {path}: {h['status']} by {h['reviewer_role']} on {h['reviewed_on']}")


# ----------------------------------------------------------------------------- --share (L5-08, L1-12, P2-9)

SHARE_MODES = ("internal", "external", "public")
SHARE_ADVERB = {"external": "externally", "public": "publicly"}
SHARE_NEEDS = {"external": ("external", "public"), "public": ("public",)}
SHARED_LINE = "Shared {mode}: identifying details are masked"
NAME_GUARD = "refused: a listed name appears in the output ({n} times); fix the pack text or use ingest --redact"
# --share public also drops the AI justification and causal free text from embedded finding records: summary
# mode removes exact quotes only, and these fields can paraphrase a witness. Labels and IDs stay.
PUBLIC_DROP_KEYS = ("justification", "causal")
OWNER_TIERS = ("T4", "T5")
SHARED_SOURCE = "a ProbeMatrix investigation export"      # replaces a register's source file name in shared copies


def share_mode(a) -> str:
    """The share mode a renderer uses: --share when given, else internal."""
    return getattr(a, "share", None) or "internal"


def share_unmet(doc, w, mode, embed=None, embeds=True, src=None, ws=None) -> list:
    """P2-9: every condition a --share external|public copy does not meet (empty when it may be shared). The doc's
    effective handling must be approved, its classification at the mode's level or higher, legal_review cleared,
    and (for pages that embed records) --embed omitted or summary."""
    eh = effective_handling(doc if isinstance(doc, dict) else {}, w, src=src, ws=ws)
    out = []
    st = eh["effective_status"]
    if st == "draft":
        out.append("review is draft" + (f" ({', '.join(eh['draft_reasons'])})" if eh["draft_reasons"] else ""))
    elif st != "approved":
        out.append(f"review is {st} (needs approved)")
    need = SHARE_NEEDS[mode]
    if eh["classification"] not in need:
        out.append(f'classification is "{eh["classification"]}" (needs ' + " or ".join(f'"{x}"' for x in need) + ")")
    if eh["legal_review"] != "cleared":
        out.append('legal_review is not "cleared"')
    if embeds and embed not in (None, "summary"):
        out.append(f"--embed {embed} is refused (use --embed summary)")
    return out


def share_gate(doc, w, a, embeds=True, extra=(), src=None, ws=None) -> str:
    """The share mode, after exiting 1 with every unmet condition when a shared copy is refused. src and ws: see
    effective_handling."""
    mode = share_mode(a)
    if mode == "internal":
        return mode
    unmet = list(extra) + share_unmet(doc, w, mode, getattr(a, "embed", None), embeds, src=src, ws=ws)
    if unmet:
        sys.exit(f"cannot share {SHARE_ADVERB[mode]}: " + "; ".join(unmet))
    return mode


def owner_generaliser(w):
    """owners(value) for share_doc (L5-21): a role that maps to T4 or T5 becomes its function label,
    '<entity> (<tier label>)', as singleton roles do; any other value gives None (kept). Roles classify mapped are
    looked up; others are mapped with the taxonomy and the built-in overlays classify used."""
    cl = w.get("clusters") or {}
    rm = cl.get("role_map") or {}
    names = (cl.get("taxonomy") or {}).get("entities") or {}
    cache = {}

    def tax():
        if "t" not in cache:
            ovs = [x for x in (cl.get("taxonomy") or {}).get("overlays", []) if _overlay_path(x).exists()]
            cache["t"] = _load_taxonomy(None, ovs)
        return cache["t"]

    def label(role):
        role = _s(role).strip()
        if not role:
            return None
        m = rm.get(role) or map_role(role, tax())
        if m.get("T") not in OWNER_TIERS:
            return None
        ents = [e for e in m.get("F") or [] if e != "F99"]
        tier = TIER_LABELS.get(m["T"], m["T"])
        if not ents:
            return tier
        ent = names.get(ents[0]) or next((e["name"] for e in tax()["entities"] if e["id"] == ents[0]), ents[0])
        return f"{ent} ({tier})"

    return label


def share_ctx(a, w, mode):
    return privacy.ShareCtx(mode, privacy.load_names(getattr(a, "names", None)),
                            privacy.load_orgs(getattr(a, "orgs", None)), privacy.load_singletons(w))


def shared_copy(obj, ctx, w):
    """share_doc with the workspace's owner generaliser."""
    return privacy.share_doc(obj, ctx, owners=owner_generaliser(w))


def public_records(findings: dict) -> dict:
    """--share public: embedded finding records without PUBLIC_DROP_KEYS."""
    return {k: {x: v for x, v in r.items() if x not in PUBLIC_DROP_KEYS} if isinstance(r, dict) else r
            for k, r in findings.items()}


def shared_name(path: Path, mode: str) -> Path:
    """<name>.<mode><suffix> for a shared copy, so the internal copy is never overwritten."""
    return path if mode == "internal" else path.with_name(f"{path.stem}.{mode}{path.suffix}")


def name_guard(texts, a) -> None:
    """L5-03 part 2: exit 1 when a name from --names or PMLC_NAMES appears in any rendered text (in any mode)."""
    rx = privacy.name_pattern(privacy.load_names(getattr(a, "names", None)))
    # HTML escaping changes a name ("O'Brien" -> "O&#x27;Brien"), so the unescaped text is searched as well.
    n = sum(max(len(rx.findall(t)), len(rx.findall(html.unescape(t)))) for t in texts) if rx else 0
    if n:
        sys.exit(NAME_GUARD.format(n=n))
