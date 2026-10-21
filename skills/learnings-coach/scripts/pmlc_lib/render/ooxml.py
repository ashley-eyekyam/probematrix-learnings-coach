"""Office Open XML helpers for the docx and pptx renderers (standard library only): a reproducible zip (P4-6), XML
text escaping that drops the characters XML 1.0 forbids, and the package parts every OOXML file needs."""
from __future__ import annotations

import datetime as dt
import io
import re
import zipfile

CONTENT_TYPES_PART = "[Content_Types].xml"
ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)
XML_DECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
# Everything outside XML 1.0's Char production: #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FFFF].
XML_INVALID_RX = re.compile("[^\t\n\r -퟿-�\U00010000-\U0010ffff]")
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
OFFICE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL_TYPES = {
    "officeDocument": f"{OFFICE_REL}/officeDocument",
    "core-properties": "http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties",
    "extended-properties": f"{OFFICE_REL}/extended-properties",
    "styles": f"{OFFICE_REL}/styles",
    "settings": f"{OFFICE_REL}/settings",
    "footer": f"{OFFICE_REL}/footer",
    "header": f"{OFFICE_REL}/header",
    "endnotes": f"{OFFICE_REL}/endnotes",
    "footnotes": f"{OFFICE_REL}/footnotes",
    "numbering": f"{OFFICE_REL}/numbering",
    "image": f"{OFFICE_REL}/image",
    "hyperlink": f"{OFFICE_REL}/hyperlink",
    "slide": f"{OFFICE_REL}/slide",
    "slideLayout": f"{OFFICE_REL}/slideLayout",
    "slideMaster": f"{OFFICE_REL}/slideMaster",
    "notesSlide": f"{OFFICE_REL}/notesSlide",
    "notesMaster": f"{OFFICE_REL}/notesMaster",
    "theme": f"{OFFICE_REL}/theme",
    "presProps": f"{OFFICE_REL}/presProps",
    "viewProps": f"{OFFICE_REL}/viewProps",
    "tableStyles": f"{OFFICE_REL}/tableStyles",
}


def _ox_zip_time() -> tuple:
    """Midnight of build_date() when SOURCE_DATE_EPOCH is set, else 1980-01-01 00:00:00 (P4-6)."""
    from . import build_date, epoch_date
    if epoch_date() is None:
        return ZIP_EPOCH
    d = dt.date.fromisoformat(build_date())
    return (max(d.year, 1980), d.month, d.day, 0, 0, 0)


def zip_bytes(parts: dict) -> bytes:
    """A deflated zip of parts (name -> bytes or str, str written UTF-8): [Content_Types].xml first, then the other
    names sorted, every entry stamped with the same time, so the same parts always give the same bytes."""
    stamp = _ox_zip_time()
    names = sorted(parts, key=lambda n: (n != CONTENT_TYPES_PART, n))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for n in names:
            zi = zipfile.ZipInfo(n, date_time=stamp)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            data = parts[n]
            z.writestr(zi, data.encode("utf-8") if isinstance(data, str) else data)
    return buf.getvalue()


def xml_text(s) -> str:
    """s as XML character data (safe in attributes too): &, <, > and " escaped, and every character XML 1.0 forbids
    (control characters such as \\x0b copied from an export) dropped. None is ""."""
    if s is None:
        return ""
    t = XML_INVALID_RX.sub("", str(s))
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def core_props(title: str, created: str) -> str:
    """docProps/core.xml: title and created only. No creator or lastModifiedBy (output-style.md, "Converted files").
    created is YYYY-MM-DD or a full W3CDTF time."""
    when = created if "T" in created else f"{created}T00:00:00Z"
    return (XML_DECL + '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
            'xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            f"<dc:title>{xml_text(title)}</dc:title>"
            f'<dcterms:created xsi:type="dcterms:W3CDTF">{xml_text(when)}</dcterms:created>'
            f'<dcterms:modified xsi:type="dcterms:W3CDTF">{xml_text(when)}</dcterms:modified>'
            "</cp:coreProperties>")


def app_props() -> str:
    """docProps/app.xml: the application name only."""
    return (XML_DECL + '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
            'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
            "<Application>ProbeMatrix Learnings Coach</Application></Properties>")


def content_types(defaults: dict, overrides: dict) -> str:
    """[Content_Types].xml: defaults is extension -> type, overrides is part name -> type (a leading / is added)."""
    d = "".join(f'<Default Extension="{xml_text(e)}" ContentType="{xml_text(t)}"/>' for e, t in sorted(defaults.items()))
    o = "".join(f'<Override PartName="/{xml_text(p.lstrip("/"))}" ContentType="{xml_text(t)}"/>'
                for p, t in sorted(overrides.items()))
    return XML_DECL + f'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">{d}{o}</Types>'


def rels(items: list) -> str:
    """A .rels part from (id, type, target) tuples. type is a full relationship URI or a REL_TYPES short name; a
    target starting with http(s):// is marked External."""
    out = []
    for rid, typ, target in items:
        ext = ' TargetMode="External"' if str(target).startswith(("http://", "https://")) else ""
        out.append(f'<Relationship Id="{xml_text(rid)}" Type="{xml_text(REL_TYPES.get(typ, typ))}" '
                   f'Target="{xml_text(target)}"{ext}/>')
    return XML_DECL + f'<Relationships xmlns="{PKG_REL_NS}">{"".join(out)}</Relationships>'
