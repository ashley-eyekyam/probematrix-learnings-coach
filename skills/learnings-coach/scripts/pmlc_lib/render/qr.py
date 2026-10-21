"""QR code as an inline SVG, built on the vendored Project Nayuki encoder (MIT, v1.8.0)."""
from __future__ import annotations

from html import escape

from pmlc_lib.vendor.qrcodegen import QrCode, QrSegment

# sha256 of pmlc_lib/vendor/qrcodegen.py, as published at tag v1.8.0 (python/qrcodegen.py). A test pins it.
VENDOR_SHA256 = "b089855caf16185c61421ea4927c1b213cf9468940d71fa8ab11ef83662dcc84"


def qr_code(text: str) -> QrCode:
    """Encode text at error correction M exactly (boostecl is off, so the level is never raised silently)."""
    return QrCode.encode_segments(QrSegment.make_segments(text), QrCode.Ecc.MEDIUM, boostecl=False)


def qr_svg(text: str, *, module_px: int = 3, border: int = 4) -> str:
    """Return an inline <svg> QR code for text (error correction M) as one <path> of unit squares."""
    qr = qr_code(text)
    n = qr.get_size()
    side = n + 2 * border
    cells = []
    for y in range(n):
        for x in range(n):
            if qr.get_module(x, y):
                cells.append("M%d %dh1v1h-1z" % (x + border, y + border))
    label = escape("QR code: " + text, quote=True)
    px = side * module_px
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="%s" viewBox="0 0 %d %d" '
        'width="%d" height="%d" shape-rendering="crispEdges">'
        '<rect width="100%%" height="100%%" fill="#fff"/>'
        '<path d="%s" fill="#000"/></svg>' % (label, side, side, px, px, "".join(cells))
    )
