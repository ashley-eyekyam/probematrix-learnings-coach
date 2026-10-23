"""The v1 module names (pmlc, pmlc_pack, pmlc_lint, pmlc_privacy) stay importable for the whole of v2.0: each is a
shim that copies every module-level name of its pmlc_lib modules into its own namespace (Ruling P3-1)."""
from __future__ import annotations

import importlib
import types

# The modules whose names `pmlc` exports, in order: a later module's name wins over an earlier one's. Only modules
# carved out of the v1 pmlc.py (plus the privacy core, which now holds scan-names) belong here; a later task adds
# its new modules to this list.
MODULES = [
    "pmlc_lib",
    "pmlc_lib.util",
    "pmlc_lib.privacy",
    "pmlc_lib.workspace",
    "pmlc_lib.handling",
    "pmlc_lib.ingest.schema",
    "pmlc_lib.ingest.xlsx",
    "pmlc_lib.profile",
    "pmlc_lib.classify",
    "pmlc_lib.select",
    "pmlc_lib.analysis.causal",
    "pmlc_lib.analysis.timeline",
    "pmlc_lib.analysis.interfaces",
    "pmlc_lib.dashboard.data",
    "pmlc_lib.dashboard.render",
    "pmlc_lib.register.check",
    "pmlc_lib.register.xlsx",
    "pmlc_lib.retention",
    "pmlc_lib.register.markdown",
    "pmlc_lib.samples",
    "pmlc_lib.orchestrate",
    "pmlc_lib.templates",
    "pmlc_lib.actions",
    "pmlc_lib.contracts",
    "pmlc_lib.plan",
    "pmlc_lib.compare",
    "pmlc_lib.facts",
    "pmlc_lib.render",
    "pmlc_lib.render.labels",
    "pmlc_lib.render.fields",
    "pmlc_lib.render.ooxml",
    "pmlc_lib.render.normalise",
    "pmlc_lib.render.graphs",
    "pmlc_lib.render.bowtie",
    "pmlc_lib.render.ics",
    "pmlc_lib.render.quiz",
    "pmlc_lib.render.email",
    "pmlc_lib.render.exports",
    "pmlc_lib.render.docx",
    "pmlc_lib.render.script",
    "pmlc_lib.register.render",
    "pmlc_lib.render.layouts",
    "pmlc_lib.render.pptx",
    "pmlc_lib.render.scorm",
    "pmlc_lib.pack.command",
    "pmlc_lib.strings",
    "pmlc_lib.open_questions",
    "pmlc_lib.cli",
]
PACK_MODULES = ["pmlc_lib.pack.profiles", "pmlc_lib.pack.schema", "pmlc_lib.pack.graph_layout", "pmlc_lib.pack.items",
                "pmlc_lib.pack.markdown", "pmlc_lib.pack.html", "pmlc_lib.pack.xlsx", "pmlc_lib.pack.command"]
LINT_MODULES = ["pmlc_lib.lint"]
PRIVACY_MODULES = ["pmlc_lib.privacy"]


def export(ns: dict, modules: list) -> None:
    """Copy every module-level name of each module (private names included, dunders other than __version__ left
    out) into the namespace ns. A subpackage's own submodule attributes are skipped (pmlc_lib.util is not `util`)."""
    for name in modules:
        mod = importlib.import_module(name)
        for k, v in vars(mod).items():
            if k.startswith("__") and k != "__version__":
                continue
            if isinstance(v, types.ModuleType) and v.__name__ == f"{name}.{k}":
                continue
            ns[k] = v
