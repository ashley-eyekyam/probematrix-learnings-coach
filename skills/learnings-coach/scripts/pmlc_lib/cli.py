"""pmlc — ProbeMatrix Learnings Coach engine.

Deterministic data work over a ProbeMatrix findings export (.xlsx), so that the
LLM skills spend their effort on judgement, not counting.

Subcommands
  ingest          xlsx -> JSON workspace in <export-dir>/pmlc-runs/<date>-<site>-<event>/workspace
  profile         Markdown profile of the workspace (counts, levels, roles, data-quality flags)
  classify        map 'Individuals Involved' roles to Learning Clusters (entity x tier x relation)
  select          compact Markdown/JSON bundle of findings for one audience or cluster
  causal          causal graph extracted from the AI's causal explanations (+ Causal Chain sheet)
  timeline        dated precursor candidates found in findings and evidence
  interfaces      entity x entity interface matrix (shared findings + cross-entity causal links)
  dashboard       self-contained HTML organisational learning dashboard
  register-xlsx   write a Learnings Register JSON to a formatted .xlsx
  scan-names      deterministic zero-hit name scan over files (de-identification check)
  check-pack      check a learning pack JSON against the workspace
  sign-off        record a person's review of a pack or register (writes its handling block and content hash)
  check-register  check a Learnings Register JSON against the workspace
  check-language  just-culture and grounding lint (JC1-JC12) of a pack or register JSON
  pack            learning pack JSON -> <run>/outputs/<pack>.html and .md
  causal-item     the top causal links as a ready graph item for a pack (JSON on stdout)
  status          which derived files are current or stale, and the last check of each pack
  run-path        print a workspace's run folder, outputs folder and slug
  check-samples   check samples/<slug>/ folders follow the contribution layout
  run-manifest    set a run's intended use, jurisdiction, retention review date and classification
  purge           delete a run's workspace (and outputs) after retention, keeping run-manifest.json
  setup           ingest, profile, classify, causal, timeline and interfaces in one go
  check-all       check every pack and the register in outputs/
  render-all      render every pack that passed its check, and the register
  index           write outputs/index.html, one row per pack
  dossier-index   write outputs/dossier-index.json listing the dossier-F*.json packs
  templates       blank adoption.csv, distribution.csv or verification.jsonl for the organisation to fill in
  export-actions  recommendations, decisions and indicators as actions.csv / actions.json (owners left blank)
  plan            resolve a workflow preset, audiences or skills into an ordered plan (<ws>/plan.json)

Only dependency outside the standard library: openpyxl.
Run `python3 pmlc.py <subcommand> -h` for options.
"""
from __future__ import annotations

import argparse
import sys

from . import __version__
from .analysis.causal import cmd_causal
from .analysis.interfaces import cmd_interfaces
from .analysis.timeline import cmd_timeline
from .classify import cmd_classify
from .dashboard.data import EMBED_MODES
from .dashboard.render import cmd_dashboard
from .handling import cmd_sign_off, HANDLING_ENUMS, SHARE_MODES
from .ingest.xlsx import cmd_ingest
from .lint import cmd_check_language
from .orchestrate import cmd_check_all, cmd_dossier_index, cmd_index, cmd_render_all, cmd_setup
from .pack.html import cmd_pack
from .pack.items import cmd_causal_item
from .pack.schema import cmd_check_pack
from .plan import cmd_plan
from .privacy import cmd_scan_names
from .profile import cmd_profile
from .register.check import cmd_check_register
from .register.xlsx import cmd_register_xlsx
from .samples import cmd_check_samples
from .templates import cmd_templates, FILES as TEMPLATE_FILES
from .actions import cmd_export_actions, PROFILE_NAMES
from .select import cmd_select, COUNT_BY, SELECT_FIELDS
from .util import HERE
from .retention import cmd_purge, cmd_run_manifest, CLASSIFICATIONS, JURISDICTIONS
from .workspace import cmd_run_path, cmd_status


# ----------------------------------------------------------------------------- main

def _non_negative_int(v):
    n = int(v)
    if n < 0:
        raise argparse.ArgumentTypeError("--budget-chars must be 0 or more")
    return n


def _lint_flags(s):
    s.add_argument("--share", choices=["internal", "external", "public"],
                   help="lint for this audience (default: the handling classification, else internal)")
    s.add_argument("--names", help="names file, one per line (default: $PMLC_NAMES)")
    s.add_argument("--orgs", help="organisation names file, one per line (default: $PMLC_ORGS)")


def add_share_args(s):
    s.add_argument("--share", choices=SHARE_MODES, default=None,
                   help="internal (default), or a copy for outside the organisation: external or public. A shared "
                        "copy needs an approved sign-off with that classification, legal_review cleared and --embed "
                        "summary; names, organisations, tags, singleton roles, times and full dates are masked, and "
                        "the file is written as <name>.<mode>.<ext>")
    s.add_argument("--names", help="names file, one per line (default: $PMLC_NAMES); masked when shared, and in any "
                                   "mode the output is refused if one appears in it")
    s.add_argument("--orgs", help="organisation names file, one per line (default: $PMLC_ORGS)")


def add_embed_arg(s):
    s.add_argument("--embed", choices=EMBED_MODES, default=None,
                   help="records the page embeds: cited (default; uncovered findings as label and rating), "
                        "summary (cited, without evidence descriptions, quotes, interviews, key questions or vote "
                        "reasons) or full (every relevant record)")


def build_parser():
    p = argparse.ArgumentParser(prog="pmlc", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
                                allow_abbrev=False)
    p.add_argument("--version", action="version", version=f"pmlc {__version__}")
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("ingest", help="xlsx export -> JSON workspace in <export-dir>/pmlc-runs/<slug>/workspace", allow_abbrev=False)
    s.add_argument("xlsx")
    where = s.add_mutually_exclusive_group()
    where.add_argument("--slug", help="<site>-<event>: lowercase words joined by hyphens, e.g. hazira-gas-release-fire")
    s.add_argument("--date", help="incident date YYYY-MM-DD (default: the summary sheet's Date)")
    s.add_argument("--root", help="folder that holds pmlc-runs/ (default: the export's folder)")
    where.add_argument("--out", help="explicit workspace path; must be <dir>/pmlc-runs/<YYYY-MM-DD>-<site>-<event>/workspace")
    where.add_argument("--legacy-out", help="write the workspace to any folder (pre-0.2 layout; not for new runs)")
    s.add_argument("--force", action="store_true", help="overwrite an existing workspace in the run folder")
    s.add_argument("--strict", action="store_true", help="exit 1 when a required column is missing")
    s.add_argument("--redact", metavar="MAP.json",
                   help='JSON object {"name": "role"}; each name (and its variants) is replaced in the workspace')
    s.set_defaults(fn=cmd_ingest)

    s = sp.add_parser("profile", help="Markdown profile", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--top", type=int, default=15)
    s.add_argument("--out")
    s.set_defaults(fn=cmd_profile)

    s = sp.add_parser("classify", help="roles -> Learning Clusters", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--taxonomy", help="alternative taxonomy.json")
    s.add_argument("--overlay", action="append", metavar="NAME_OR_PATH",
                   help="extra site role words OR-ed onto the taxonomy (repeatable); a bare name means "
                        "references/overlays/<name>.json, e.g. india-process-site")
    s.add_argument("--no-overlay", action="store_true",
                   help="use no overlay. Without --taxonomy/--overlay/--no-overlay, classify reuses the taxonomy "
                        "and overlays the previous classify used")
    s.add_argument("--overrides", help="JSON {role: {F:[..], T:.., R:..}} from the LLM resolution pass "
                                          "(default: <ws>/role_overrides.json when it exists)")
    s.add_argument("--no-overrides", action="store_true", help="ignore any overrides file")
    s.set_defaults(fn=cmd_classify)

    s = sp.add_parser("select", help="filtered findings bundle", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--entity", nargs="*", help="e.g. F02 F09b")
    s.add_argument("--tag", nargs="+", help="entity tags, e.g. emergency or supply contractor; unioned with --entity")
    s.add_argument("--tier", nargs="*", help="e.g. T2 T3")
    s.add_argument("--relation", nargs="*", help="actor approver owner absent norm_setter learner challenger")
    s.add_argument("--level", nargs="*", type=int, help="1 2 3 4")
    s.add_argument("--min-rating", type=int)
    s.add_argument("--top-rated", action="store_true", help="only findings at the workspace's top rating (run-path prints it)")
    s.add_argument("--entity-mode", choices=["any", "all"], default="any",
                   help="any: a finding matches if it has any requested entity (default). all: it must have every "
                        "--entity and, for each --tag, at least one of that tag's entities (the shared findings)")
    s.add_argument("--exclude-downgraded", action="store_true",
                   help="drop findings a reviewer voted to downgrade, reject or remove, and say which")
    s.add_argument("--subcategory", nargs="+", help="HFACS subcategory, case-insensitive exact match")
    s.add_argument("--prefix", nargs="+", help="Nanocode prefix before the space, e.g. SV OR")
    s.add_argument("--code", nargs="*")
    s.add_argument("--text", help="regex over short/justification/causal/label")
    s.add_argument("--max", type=int)
    s.add_argument("--brief", action="store_true", help="omit justification, causal text and evidence quotes")
    s.add_argument("--budget-chars", type=_non_negative_int, help="keep findings in rating order while the output stays within "
                                                    "N characters, and say how many were dropped; the header and "
                                                    "footer lines are always printed")
    s.add_argument("--fields", help="comma-separated: " + ", ".join(SELECT_FIELDS) + " (id is always kept)")
    s.add_argument("--group-by", choices=["level", "subcategory", "code", "entity"],
                   help="group the findings under one heading (md) or key (json) per value")
    s.add_argument("--count-by", choices=COUNT_BY, help="print only a count table (md) or dict (json)")
    s.add_argument("--format", choices=["md", "json"], default="md")
    s.add_argument("--out")
    s.add_argument("--preset", metavar="SKILL[:NAME]",
                   help="run a skill's recorded gather calls (references/select-presets.json); takes only output "
                        "flags. Each call keeps its own --format unless you pass --format, which overrides all. "
                        "With several calls the output is one bundle per call under '# Preset <skill>: <name>' "
                        "headings, so json output is concatenated bundles, not one JSON value. --budget-chars "
                        "caps the whole bundle, headings included: each call gets what the earlier calls left, and a "
                        "call with nothing left prints only its minimum output (with the below-minimum warning)")
    s.set_defaults(fn=cmd_select)

    s = sp.add_parser("causal", help="extract causal graph", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--top", type=int, default=60)
    s.add_argument("--include-justification", action="store_true")
    s.set_defaults(fn=cmd_causal)

    s = sp.add_parser("timeline", help="dated precursor candidates", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--before", help="ISO date, or the word incident for the workspace's incident date; keep only events up to it")
    s.add_argument("--per-date", type=int, default=4)
    s.add_argument("--show", type=int, default=60)
    s.add_argument("--on", metavar="DAY|incident",
                   help="also write timeline_event_day.json: every clock time for that day (YYYY-MM-DD, or incident). "
                        "Times in undated sentences count only for the incident date; for any other day a time "
                        "counts only when its sentence gives that day's date")
    s.add_argument("--entity", nargs="+", metavar="F", help="keep only findings in these entities, and their linked evidence")
    s.add_argument("--min-precision", choices=["day", "month", "year"], default="year",
                   help="coarsest date precision to keep (year keeps everything)")
    s.set_defaults(fn=cmd_timeline)

    s = sp.add_parser("interfaces", help="entity x entity interfaces", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--top", type=int, default=25)
    s.set_defaults(fn=cmd_interfaces)

    s = sp.add_parser("dashboard", help="HTML organisational learning map", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--out", help="default: <run>/outputs/organisation-learning-map.html")
    s.add_argument("--register", help="Learnings Register JSON: adds learnings, tier plan and control-strength sections")
    s.add_argument("--title", help="override the incident title shown in the header")
    s.add_argument("--date", help="override the incident date (use when the summary sheet is wrong)")
    s.add_argument("--location", help="override the location shown in the header")
    add_embed_arg(s)
    add_share_args(s)
    s.set_defaults(fn=cmd_dashboard)

    s = sp.add_parser("check-register", help="validate a Learnings Register JSON against the workspace", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("register")
    _lint_flags(s)
    s.set_defaults(fn=cmd_check_register)

    s = sp.add_parser("check-language", help="just-culture and grounding lint (JC1-JC12) of a pack or register JSON", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("json", help="a learning pack or Learnings Register JSON")
    _lint_flags(s)
    s.set_defaults(fn=cmd_check_language)

    s = sp.add_parser("register-xlsx", help="Learnings Register JSON -> xlsx", allow_abbrev=False)
    s.add_argument("register")
    s.add_argument("--out", help="default: learnings-register.xlsx next to the register JSON")
    s.add_argument("--ws", help="workspace for the review status (default: the run's workspace in the standard layout)")
    add_share_args(s)
    s.set_defaults(fn=cmd_register_xlsx)

    s = sp.add_parser("status", help="show which workspace files are current or stale, and pack check history", allow_abbrev=False)
    s.add_argument("ws")
    s.set_defaults(fn=cmd_status)

    s = sp.add_parser("run-path", help="print the run folder, workspace, outputs folder and slug of a workspace", allow_abbrev=False)
    s.add_argument("ws")
    s.set_defaults(fn=cmd_run_path)

    s = sp.add_parser("run-manifest", help="update <run>/run-manifest.json (intended use, jurisdiction, retention review, classification)", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--intended-use", dest="intended_use", help="what the learnings are for (free text)")
    s.add_argument("--jurisdiction", help="comma-separated: " + ",".join(JURISDICTIONS))
    s.add_argument("--retention-review", dest="retention_review", help="YYYY-MM-DD")
    s.add_argument("--classification", choices=list(CLASSIFICATIONS))
    s.set_defaults(fn=cmd_run_manifest)

    s = sp.add_parser("purge", help="delete a run's workspace and outputs, keeping run-manifest.json (needs --yes)", allow_abbrev=False)
    s.add_argument("run", help="the run folder <dir>/pmlc-runs/<YYYY-MM-DD>-<site>-<event>")
    s.add_argument("--keep", choices=["outputs"], help="keep the outputs folder")
    s.add_argument("--yes", action="store_true", help="really delete (without it, list what would go and exit 1)")
    s.set_defaults(fn=cmd_purge)

    s = sp.add_parser("check-samples", help="check samples/<slug>/ folders follow the contribution layout", allow_abbrev=False)
    s.add_argument("dir", nargs="?", default=str(HERE.parents[2] / "samples"))
    s.set_defaults(fn=cmd_check_samples)

    s = sp.add_parser("check-pack", help="check a learning pack JSON against the workspace", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("pack")
    _lint_flags(s)
    s.set_defaults(fn=cmd_check_pack)

    s = sp.add_parser("pack", help="learning pack JSON -> <run>/outputs/<pack>.html (and .md)", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("pack")
    s.add_argument("--out", help="output folder (default: <run>/outputs)")
    s.add_argument("--no-md", action="store_true", help="write only the HTML")
    add_embed_arg(s)
    add_share_args(s)
    s.set_defaults(fn=cmd_pack)

    s = sp.add_parser("causal-item", help="top causal links as a pack graph item (JSON on stdout)", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--top", type=int, default=40, help="links to keep (default 40)")
    s.set_defaults(fn=cmd_causal_item)

    s = sp.add_parser("sign-off", help="record a person's review of a pack or register (writes its handling block)", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("file")
    s.add_argument("--role", required=True, help="the reviewer's role (never a name)")
    s.add_argument("--status", choices=["reviewed", "approved"], default="reviewed")
    s.add_argument("--classification", choices=list(HANDLING_ENUMS["classification"]))
    s.add_argument("--legal-review", dest="legal_review", choices=list(HANDLING_ENUMS["legal_review"]))
    s.add_argument("--distribution", nargs="+", metavar="AUDIENCE")
    s.add_argument("--retention-review", dest="retention_review", metavar="YYYY-MM-DD")
    s.add_argument("--version")
    s.add_argument("--date", metavar="YYYY-MM-DD", help="review date (default: today)")
    s.add_argument("--names", help="names file: --role and --distribution must not name a listed person "
                                   "(default: $PMLC_NAMES)")
    s.set_defaults(fn=cmd_sign_off)

    s = sp.add_parser("scan-names", help="zero-hit name scan (exit 1 on hits, 2 if a file could not be read)", allow_abbrev=False)
    s.add_argument("names", help="text file, one name per line")
    s.add_argument("paths", nargs="+")
    s.add_argument("--show", type=int, default=50)
    s.add_argument("--variants", action="store_true",
                   help="also match surname, initial + surname and honorific + surname for each name")
    s.add_argument("--patterns", action="store_true",
                   help="also flag email, phone and staff-number patterns (an aid, not proof of de-identification)")
    s.set_defaults(fn=cmd_scan_names)

    s = sp.add_parser("setup", help="ingest, profile, classify, causal, timeline and interfaces in one go", allow_abbrev=False)
    s.add_argument("xlsx")
    s.add_argument("--slug", required=True, help="<site>-<event>, e.g. hazira-gas-release-fire")
    s.add_argument("--date", help="incident date YYYY-MM-DD (default: the summary sheet's Date)")
    s.add_argument("--root", help="folder that holds pmlc-runs/ (default: the export's folder)")
    s.add_argument("--force", action="store_true", help="overwrite an existing workspace in the run folder")
    s.add_argument("--strict", action="store_true", help="exit 1 when a required column is missing")
    s.add_argument("--redact", metavar="MAP.json", help="JSON {name: role}; passed to ingest")
    s.add_argument("--overlay", metavar="NAME_OR_PATH", help="role overlay for classify, e.g. india-process-site")
    s.set_defaults(fn=cmd_setup)

    s = sp.add_parser("check-all", help="check every pack and the register in outputs/", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--strict", action="store_true", help="pass --strict to check-pack where it is available")
    s.add_argument("--json", action="store_true", help="print one JSON object on stdout; messages go to stderr")
    s.set_defaults(fn=cmd_check_all)

    s = sp.add_parser("render-all", help="render every pack that passed its last check, and the register", allow_abbrev=False)
    s.add_argument("ws")
    add_embed_arg(s)
    add_share_args(s)
    s.set_defaults(fn=cmd_render_all)

    s = sp.add_parser("index", help="write outputs/index.html: one row per pack", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--out", help="default: <run>/outputs/index.html")
    s.set_defaults(fn=cmd_index)

    s = sp.add_parser("dossier-index", help="write outputs/dossier-index.json listing the dossier-F*.json packs", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--out", help="default: <run>/outputs/dossier-index.json")
    s.set_defaults(fn=cmd_dossier_index)
    s = sp.add_parser("templates", help="write adoption.csv, distribution.csv or verification.jsonl for the organisation to fill in", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("mode", choices=list(TEMPLATE_FILES))
    s.add_argument("--register", help="Learnings Register JSON (default: <run>/outputs/learnings-register.json)")
    s.add_argument("--out", help="file to write (default: <run>/outputs/<file>); never overwrites an existing file")
    s.set_defaults(fn=cmd_templates)

    s = sp.add_parser("export-actions", help="write actions.csv and actions.json from the packs and register", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--packs", nargs="+", metavar="PACK", help="pack names or JSON paths (default: every pack in <run>/outputs)")
    s.add_argument("--register", help="Learnings Register JSON (default: <run>/outputs/learnings-register.json when present)")
    s.add_argument("--profile", choices=PROFILE_NAMES, default="generic", help="column names for a target system (default generic)")
    s.add_argument("--names", help="names file: nothing is written if one appears in the actions (default: $PMLC_NAMES)")
    s.add_argument("--out-dir", dest="out_dir", help="folder to write into (default: <run>/outputs)")
    s.set_defaults(fn=cmd_export_actions)
    s = sp.add_parser("plan", help="resolve a workflow preset, audiences or skills into an ordered plan",
                      allow_abbrev=False)
    s.add_argument("ws")
    what = s.add_mutually_exclusive_group(required=True)
    what.add_argument("--workflow", metavar="NAME", help="a preset from references/workflows.json")
    what.add_argument("--audiences", metavar="A,B", help="audience ids from references/audiences.json")
    what.add_argument("--skills", metavar="S,T", help="skill names")
    what.add_argument("--next", action="store_true",
                      help="refresh the saved plan and print only its next step (exit 2 when the plan is complete)")
    s.add_argument("--json", action="store_true", help="print the plan as one JSON object")
    s.set_defaults(fn=cmd_plan)

    return p


def main(argv=None):
    a = build_parser().parse_args(argv)
    a._argv = list(sys.argv[1:] if argv is None else argv)
    a.fn(a)
    return 0
