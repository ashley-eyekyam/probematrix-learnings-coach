"""The organisation brand (Ruling P4-16): brand.json sets the organisation name, one accent colour and a logo, and
nothing else. The footer and the status line are fixed; an accent must reach WCAG AA (4.5:1) against white."""
from __future__ import annotations

import base64
import html
import json
import pathlib
import re

from . import Brand

BRAND_KEYS = ("organisation", "accent", "logo")
LOCKED = "brand.json may set organisation, accent and logo only; the footer and status line are fixed"
MIN_CONTRAST = 4.5
MAX_LOGO_BYTES = 200 * 1024
ACCENT_RX = re.compile(r"#[0-9A-Fa-f]{6}")
LOGO_TYPES = ((b"\x89PNG\r\n\x1a\n", "image/png", (".png",)), (b"\xff\xd8\xff", "image/jpeg", (".jpg", ".jpeg")))


def _br_channel(v: int) -> float:
    c = v / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def _br_luminance(hex_colour: str) -> float:
    h = hex_colour.lstrip("#")
    r, g, b = (_br_channel(int(h[i:i + 2], 16)) for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(hex_a: str, hex_b: str) -> float:
    """The WCAG contrast ratio of two #RRGGBB colours, 1.0 to 21.0."""
    a, b = _br_luminance(hex_a), _br_luminance(hex_b)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def _br_logo(path: pathlib.Path, name) -> tuple:
    if not isinstance(name, str) or not name.strip():
        raise SystemExit("brand.json: logo must be a file path relative to the brand file")
    p = path.parent / name
    if not p.is_file():
        raise SystemExit(f"brand.json: logo {name} not found next to the brand file")
    ext = p.suffix.lower()
    if ext not in (e for _, _, exts in LOGO_TYPES for e in exts):
        raise SystemExit(f"brand.json: logo {name} must be a PNG or JPEG file")
    if p.stat().st_size > MAX_LOGO_BYTES:
        raise SystemExit(f"brand.json: logo {name} is {p.stat().st_size // 1024} KB; the limit is 200 KB")
    data = p.read_bytes()
    for magic, mime, exts in LOGO_TYPES:
        if ext in exts and data.startswith(magic):
            return data, mime
    raise SystemExit(f"brand.json: logo {name} must be a PNG or JPEG file")


def load_brand(path) -> Brand:
    """Read brand.json. Raises SystemExit (exit 1) with the P4-16 message for a key outside organisation, accent and
    logo, an accent under 4.5:1 against white, or a logo that is not a PNG or JPEG of at most 200 KB."""
    path = pathlib.Path(path)
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise SystemExit(f"brand.json: cannot read {path}: {e}")
    if not isinstance(d, dict):
        raise SystemExit("brand.json: expected a JSON object")
    if any(k not in BRAND_KEYS for k in d):
        raise SystemExit(LOCKED)
    org, accent = d.get("organisation"), d.get("accent")
    if org is not None and (not isinstance(org, str) or not org.strip()):
        raise SystemExit("brand.json: organisation must be a non-empty string")
    if accent is not None:
        if not isinstance(accent, str) or not ACCENT_RX.fullmatch(accent):
            raise SystemExit(f"brand.json: accent must be a #RRGGBB colour, got {accent!r}")
        ratio = contrast_ratio(accent, "#ffffff")
        if ratio < MIN_CONTRAST:
            raise SystemExit(f"accent {accent} has contrast {ratio:.1f}:1 against white; WCAG AA needs 4.5:1")
    data, mime = _br_logo(path, d["logo"]) if d.get("logo") is not None else (None, None)
    return Brand(org.strip() if org else None, accent, data, mime)


def shared_brand(brand, share):
    """The brand as a --share external|public copy shows it (final review I1): the organisation name goes through the
    same masking as the pack text, so a name the orgs list holds becomes [organisation]; a public copy also drops the
    logo, which identifies the organisation by itself. No share, or no brand: the brand unchanged."""
    if brand is None or share is None:
        return brand
    from ..privacy import share_text
    org = share_text(brand.organisation, share) if brand.organisation else brand.organisation
    if getattr(share, "mode", None) == "public":
        return brand._replace(organisation=org, logo_bytes=None, logo_mime=None)
    return brand._replace(organisation=org)


def brand_css(brand) -> str:
    """The accent override (light theme; the dark theme's own rule is more specific) and the logo rule; "" for no brand."""
    if brand is None:
        return ""
    out = []
    if brand.accent:
        out.append(f":root{{--acc:{brand.accent};--accent:{brand.accent}}}")
    if brand.logo_bytes or brand.organisation:
        out.append(".brand-id{display:flex;align-items:center;gap:10px;margin:0 0 8px;font-weight:600}"
                   ".brand-logo{max-height:48px;max-width:200px;width:auto;height:auto}")
    return "\n".join(out)


def brand_logo_uri(brand) -> str:
    return (f"data:{brand.logo_mime};base64," + base64.b64encode(brand.logo_bytes).decode("ascii")
            if brand is not None and brand.logo_bytes else "")


def brand_header(brand) -> str:
    """The logo (a data URI) and the organisation name, or "" for no brand or neither."""
    if brand is None or not (brand.logo_bytes or brand.organisation):
        return ""
    name = html.escape(brand.organisation or "", quote=True)
    img = f'<img class="brand-logo" src="{brand_logo_uri(brand)}" alt="{name}">' if brand.logo_bytes else ""
    return f'<div class="brand-id">{img}<span>{name}</span></div>\n' if name else f'<div class="brand-id">{img}</div>\n'
