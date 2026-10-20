"""ProbeMatrix Learnings Coach engine package. pmlc.py is a thin shim over it; see cli.py for the subcommands.
The version, the brand and the other fixed copy live here only."""
from __future__ import annotations


__version__ = "2.0.0a4"
BRAND = (f"Generated with ProbeMatrix Learnings Coach v{__version__} (open source, MIT) from a ProbeMatrix "
         "four-level human-factors investigation. ProbeMatrix by Eyekyam: ashley@eyekyam.com")
# Fixed copy: this module is the only place these strings are written; renderers import them, and the
# dashboard JS reads them from the embedded `brand` payload (brand_payload()).
STATUS_PHRASE = "Learning purposes: not a statutory document"
AI_STATUS = "Learnings drafted by an AI agent from AI-assisted findings"
AI_JUSTIFICATION_LABEL = "AI justification (ProbeMatrix)"
AI_CHIP = "AI-drafted, not human-edited"
EXPORT_BANNER = ("This is the investigation's AI-drafted wording, shown as evidence; "
                 "it is not the coach's learning.")
DRAFT_LABEL = "DRAFT"
VERSION_STAMP = f"ProbeMatrix Learnings Coach v{__version__}"


def brand_payload() -> dict:
    """The fixed strings, for embedding in HTML data blocks as `data.brand`."""
    return {"status_phrase": STATUS_PHRASE, "ai_status": AI_STATUS, "ai_justification_label": AI_JUSTIFICATION_LABEL,
            "ai_chip": AI_CHIP, "export_banner": EXPORT_BANNER, "draft_label": DRAFT_LABEL, "brand": BRAND}


LEVEL_NAMES = {1: "Unsafe Acts", 2: "Preconditions", 3: "Supervision", 4: "Organisational Influences"}
