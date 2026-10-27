"""pmlc — ProbeMatrix Learnings Coach engine.

Deterministic data work over a ProbeMatrix findings export (.xlsx), so that the
LLM skills spend their effort on judgement, not counting.

Subcommands
  ingest          xlsx -> JSON workspace in <export-dir>/pmlc-runs/<date>-<site>-<event>/workspace
  profile         Markdown profile of the workspace (counts, levels, roles, data-quality flags)
  classify        map 'Individuals Involved' roles to Learning Clusters (entity x tier x relation)
  rec-review      strength bands, level match, loops and SMART gaps of a register's recommendations
  compare         comparator inventory, both-direction coverage tables and checks (ready pack items)
  select          compact Markdown/JSON bundle of findings for one audience or cluster
  causal          causal graph extracted from the AI's causal explanations (+ Causal Chain sheet)
  timeline        dated precursor candidates found in findings and evidence
  interfaces      entity x entity interface matrix (shared findings + cross-entity causal links)
  dashboard       self-contained HTML organisational learning dashboard
  register-xlsx   write a Learnings Register JSON to a formatted .xlsx
  register-md     write a Learnings Register JSON to learnings-register.md
  register-render write a Learnings Register JSON to a Word document and an email digest
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
  setup           ingest, classify, profile, causal, timeline and interfaces in one go
  check-all       check every pack and the register in outputs/
  render-all      render every pack that passed its check, and the register
  index           write outputs/index.html, one row per pack
  dossier-index   write outputs/dossier-index.json listing the dossier-F*.json packs
  templates       blank adoption.csv, distribution.csv, verification.jsonl or learning-team-notes.csv for the organisation to fill in
  table-item      a ready table item for a pack (JSON on stdout)
  register-items  a tier's learnings (or chosen or transferable ones) from the register as learning items
  timeline-item   timeline candidates as a pack timeline item
  facts           the headline numbers of a workspace
  crosswalk       which standard clauses the register evidences, and what the organisation must show
  evidence-audit  evidence strength per finding, single-source and document-only counts, concentration (engine-computed)
  hfacs-profile   level x subcategory heat map, code recurrence and causal feed counts (hfacs_profile.json)
  pack-xlsx       a pack's test points or questions as an Excel sheet
  export-actions  recommendations, decisions and indicators as actions.csv / actions.json (owners left blank)
  plan            resolve a workflow preset, audiences or skills into an ordered plan (<ws>/plan.json)
  open-questions  what the export leaves open: empty columns, blank fields, absence and hedged findings
  strings         extract a pack's text for translation (XLIFF or CSV), or apply a translation as <pack>-<lang>.json
  nine-m-seed     score every finding against the nine Ms (9M) and print the M profile (<ws>/nine_m_seed.json)
  missed-opportunities  earlier recommendations, Failure-to-Correct findings and dated precursors before the incident
  nine-m-suggest  the suggestions for one 9M question, recorded in <ws>/nine_m_session.json with --record
  nine-m-answer   record the answer to a 9M question (a suggestion's number, or free text)
  nine-m-replay   a scripted 9M session that takes the recommended suggestion at every question (--accept-recommended)
  nine-m-actions-template  a blank actions sheet from a nine-m-analysis pack (Owner, Due date and Status left blank)
  wai-wad         work as imagined against work as done: codes with document and work-as-done evidence, counterfactual wording (wai_wad.json)
  alert-grade     a safety alert's default learnings and grade (register urgency, or a suggestion from priority)

Only dependency outside the standard library: openpyxl.
Run `python3 pmlc.py <subcommand> -h` for options.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .analysis.causal import cmd_causal
from .analysis.interfaces import cmd_interfaces
from .analysis.timeline import cmd_timeline
from .classify import cmd_classify
from .compare import cmd_compare
from .dashboard.data import EMBED_MODES
from .dashboard.render import cmd_dashboard
from .handling import cmd_sign_off, HANDLING_ENUMS, SHARE_MODES
from .ingest.xlsx import cmd_ingest
from .lint import cmd_check_language
from .orchestrate import cmd_check_all, cmd_dossier_index, cmd_index, cmd_render_all, cmd_setup
from .pack.command import cmd_pack
from .pack.items import cmd_causal_item, cmd_register_items, cmd_table_item, cmd_timeline_item, TABLE_KINDS
from .pack.xlsx import cmd_pack_xlsx, XLSX_KINDS
from .crosswalk import cmd_crosswalk
from .waiwad import cmd_wai_wad, WAIWAD_TABLE_KINDS
from .evidence_audit import cmd_evidence_audit, EVAUDIT_TABLE_KINDS as EVIDENCE_AUDIT_TABLES
from .facts import cmd_facts
from .hfacs_profile import HP_TABLE_KINDS, cmd_hfacs_profile
from .open_questions import cmd_open_questions
from .pack.schema import cmd_check_pack
from .plan import cmd_plan
from .privacy import cmd_scan_names
from .profile import cmd_profile
from .render import DEFAULT_FORMATS, FORMATS, parse_formats
from .render.layouts import base_url_arg, LAYOUTS, PAPERS
from .rec_review import cmd_rec_review
from .register.check import cmd_check_register
from .register.markdown import cmd_register_md
from .register.render import cmd_register_render
from .register.xlsx import cmd_register_xlsx
from .samples import cmd_check_samples
from .templates import cmd_templates, FILES as TEMPLATE_FILES
from .actions import cmd_export_actions, PROFILE_NAMES
from .select import cmd_select, COUNT_BY, SELECT_FIELDS
from .util import HERE, industry_arg
from .retention import cmd_purge, cmd_run_manifest, CLASSIFICATIONS, JURISDICTIONS
from .workspace import cmd_run_path, cmd_status
from .strings import cmd_strings, STRINGS_FORMATS
from .ninem import cmd_nine_m_seed, NINE_M_CODES
from .ninem_session import (cmd_nine_m_actions_template, cmd_nine_m_answer, cmd_nine_m_replay, cmd_nine_m_suggest,
                            NINE_M_GLOBAL_STEPS, NINE_M_STEPS)
from .missed import cmd_missed_opportunities
from .alert import cmd_alert_grade


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


def _cli_iso_date(text):
    """argparse type for --start: an ISO date (YYYY-MM-DD)."""
    import datetime as dt
    try:
        return dt.date.fromisoformat(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{text!r} is not a date; use YYYY-MM-DD") from None


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
    s.add_argument("--industry", type=industry_arg, metavar="NAME",
                   help="load the industry reference pack references/industry/<NAME>/overlay.json (e.g. process) like "
                        "an overlay, applied before any --overlay. Method reference, not evidence. Remembered like --overlay")
    s.add_argument("--no-overlay", action="store_true",
                   help="use no overlay. Without --taxonomy/--overlay/--no-overlay, classify reuses the taxonomy "
                        "and overlays the previous classify used")
    s.add_argument("--overrides", help="JSON {role: {F:[..], T:.., R:..}} from the LLM resolution pass "
                                          "(default: <ws>/role_overrides.json when it exists)")
    s.add_argument("--no-overrides", action="store_true", help="ignore any overrides file")
    s.add_argument("--org-chart", metavar="FILE.csv",
                   help="CSV with columns department, entity (optional F-id to extend), match (keywords separated by "
                        "';' or a regex) and tier (optional T1-T5); rows without an entity become F20, F21, ... "
                        "Remembered like --overlay")
    s.add_argument("--no-org-chart", action="store_true", help="forget the remembered org chart")
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
    s.add_argument("--in-evidence", action="store_true", dest="in_evidence",
                   help="also search --text in the findings' linked evidence: Specific Reference and description")
    s.add_argument("--max", type=int)
    s.add_argument("--m", nargs="+", choices=NINE_M_CODES, help="9M lens: findings whose primary M (nine_m_seed.json) is "
                                                                "one of these, e.g. M3 (run nine-m-seed first)")
    s.add_argument("--m-secondary", dest="m_secondary", action="store_true",
                   help="with --m: also findings that carry the M as a secondary M")
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
    s.add_argument("--hubs", action="store_true", help="also print the factors with the most links out")
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
    s.add_argument("--brand", metavar="FILE", help="brand.json: organisation, accent and logo (the footer and status line stay fixed)")
    s.set_defaults(fn=cmd_dashboard)

    s = sp.add_parser("check-register", help="validate a Learnings Register JSON against the workspace", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("register")
    s.add_argument("--strict", action="store_true", help="problems, not warnings, for the priority-1 rule")
    s.add_argument("--json", action="store_true", help="print {ok, problems, warnings, stats} as JSON")
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

    s = sp.add_parser("register-md", help="Learnings Register JSON -> learnings-register.md", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("register")
    s.add_argument("--out", help="default: <run>/outputs/learnings-register.md")
    s.set_defaults(fn=cmd_register_md)

    s = sp.add_parser("register-render", help="Learnings Register JSON -> learnings-register.docx and .email.html/.txt",
                      allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("register")
    s.add_argument("--format", default="docx,email",
                   help="docx, email or docx,email (default). md and xlsx stay with register-md and register-xlsx")
    s.add_argument("--out", help="folder to write to (default: <run>/outputs)")
    add_share_args(s)
    s.set_defaults(fn=cmd_register_render)

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
    s.add_argument("--strict", action="store_true",
                   help="pack-profile violations, padding, scope drift, unknown learning ids and unknown clauses "
                   "are problems, not warnings")
    s.add_argument("--register", help="Learnings Register JSON to check learning ids against "
                   "(default: <run>/outputs/learnings-register.json when it exists)")
    s.set_defaults(fn=cmd_check_pack)

    s = sp.add_parser("pack", help="learning pack JSON -> <run>/outputs/<pack>.html (and .md)", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("pack")
    s.add_argument("--out", help="output folder (default: <run>/outputs)")
    s.add_argument("--no-md", action="store_true", help="write only the HTML")
    add_embed_arg(s)
    add_share_args(s)
    s.add_argument("--format", type=parse_formats, metavar="FORMATS", default=list(DEFAULT_FORMATS),
                   help=f"comma-separated formats to write (default: html,md); one of: {', '.join(FORMATS)}")
    s.add_argument("--view", choices=("full", "learner"), default="full",
                   help="learner: <pack>.learner.<ext> without answers, for the document formats")
    s.add_argument("--start", type=_cli_iso_date, metavar="YYYY-MM-DD",
                   help="the day the ics follow-ups count from (--format ics); the coach never picks a date itself")
    s.add_argument("--brand", metavar="FILE", help="brand.json: organisation, accent and logo (the footer and status line stay fixed)")
    s.add_argument("--layout", choices=LAYOUTS, help="also write the print layout <pack>.<layout>.html")
    s.add_argument("--paper", choices=PAPERS, help="page size of --layout cards (default: A4)")
    s.add_argument("--base-url", type=base_url_arg, metavar="URL",
                   help="where the pack page is published: QR codes in the print layouts link to it")
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

    s = sp.add_parser("setup", help="ingest, classify, profile, causal, timeline and interfaces in one go", allow_abbrev=False)
    s.add_argument("xlsx")
    s.add_argument("--slug", required=True, help="<site>-<event>, e.g. hazira-gas-release-fire")
    s.add_argument("--date", help="incident date YYYY-MM-DD (default: the summary sheet's Date)")
    s.add_argument("--root", help="folder that holds pmlc-runs/ (default: the export's folder)")
    s.add_argument("--force", action="store_true", help="overwrite an existing workspace in the run folder")
    s.add_argument("--strict", action="store_true", help="exit 1 when a required column is missing")
    s.add_argument("--redact", metavar="MAP.json", help="JSON {name: role}; passed to ingest")
    s.add_argument("--overlay", metavar="NAME_OR_PATH", help="role overlay for classify, e.g. india-process-site")
    s.add_argument("--industry", type=industry_arg, metavar="NAME",
                   help="industry reference pack for classify, e.g. process (method reference, not evidence)")
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
    s.add_argument("--format", type=parse_formats, metavar="FORMATS", default=None,
                   help=f"comma-separated formats passed to pack (default: html,md); one of: {', '.join(FORMATS)}")
    s.set_defaults(fn=cmd_render_all)

    s = sp.add_parser("index", help="write outputs/index.html: one row per pack", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--out", help="default: <run>/outputs/index.html")
    s.set_defaults(fn=cmd_index)

    s = sp.add_parser("dossier-index", help="write outputs/dossier-index.json listing the dossier-F*.json packs", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--out", help="default: <run>/outputs/dossier-index.json")
    s.set_defaults(fn=cmd_dossier_index)
    s = sp.add_parser("templates", help="write adoption.csv, distribution.csv, verification.jsonl or learning-team-notes.csv for the organisation to fill in", allow_abbrev=False)
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
    s = sp.add_parser("compare", help="comparator inventory, both-direction coverage and tables (ready pack items)",
                      allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--comparator", help="default: <ws>/comparator.json")
    s.add_argument("--mapping", help="default: <ws>/comparison-map.json")
    s.add_argument("--register", help="Learnings Register JSON: adds the learnings with no match and the owner cross-tab")
    s.add_argument("--client-safe", dest="client_safe", metavar="PACK",
                   help="check this pack's section ids equal the main pack's (needs --main)")
    s.add_argument("--main", metavar="PACK", help="the main pack to compare --client-safe against")
    s.add_argument("--json", action="store_true", help="print the ready pack items as JSON instead of Markdown")
    s.set_defaults(fn=cmd_compare)

    s = sp.add_parser("rec-review", help="strength bands, level match, loops and SMART gaps of a register's recommendations",
                      allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("register", help="Learnings Register JSON")
    s.add_argument("--nine-m", dest="nine_m", action="store_true",
                   help="also read <run>/outputs/nine-m-map.json and count recommendations per M")
    s.add_argument("--json", action="store_true", help="print the review as JSON")
    s.add_argument("--table-item", dest="table_item", choices=["strength", "spread", "smart"],
                   help="print a ready table item for a pack (JSON on stdout)")
    s.set_defaults(fn=cmd_rec_review)

    s = sp.add_parser("table-item", help="a ready table item for a pack (JSON on stdout)", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("kind", choices=TABLE_KINDS)
    s.add_argument("--entity", metavar="F", help="entity for entity-tier, e.g. F02")
    s.add_argument("--level", nargs="+", type=int, metavar="N", help="count only findings of these HFACS levels")
    s.add_argument("--top", type=int, default=15, help="rows to keep (default 15)")
    s.add_argument("--register", help="Learnings Register JSON (hoc, adoption, nine-m)")
    s.add_argument("--pack", help="pack JSON: hoc counts its recommendations and barriers; every kind drops the ids its exclusions list from the cites")
    s.set_defaults(fn=cmd_table_item)

    s = sp.add_parser("register-items", help="a tier's, chosen or transferable learnings from the register as learning items (JSON on stdout)", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--tier", choices=["T1", "T2", "T3", "T4", "T5"],
                   help="one tier's learnings (required unless --lr or --transferable is given)")
    s.add_argument("--register", help="Learnings Register JSON (default: <run>/outputs/learnings-register.json)")
    s.add_argument("--lr", action="append", metavar="LR-ID",
                   help="keep only this learning (repeatable; the items follow the order given)")
    s.add_argument("--transferable", action="store_true",
                   help="keep only the learnings whose transferability is other sites or industry-wide")
    s.set_defaults(fn=cmd_register_items)

    s = sp.add_parser("timeline-item", help="timeline candidates as a pack timeline item (JSON on stdout)", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--before", help="ISO date, or the word incident (required unless --event-day)")
    s.add_argument("--top", type=int, default=12, help="events to keep (default 12)")
    s.add_argument("--event-day", dest="event_day", action="store_true",
                   help="the incident day instead: one event per distinct hh:mm in the incident narrative, in clock "
                        "order, each the whole sentence, cited to the findings that hold the same time")
    s.set_defaults(fn=cmd_timeline_item)

    s = sp.add_parser("open-questions", help="what the export leaves open: empty columns, blank fields, absence and hedged findings",
                      allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--json", dest="as_json", action="store_true", help="print open_questions.json")
    s.add_argument("--items", action="store_true", help="print up to 30 ready question items (JSON)")
    s.set_defaults(fn=cmd_open_questions)

    s = sp.add_parser("facts", help="the headline numbers of a workspace", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--register", help="Learnings Register JSON (default: <run>/outputs/learnings-register.json when present)")
    s.add_argument("--json", action="store_true", help="print one JSON object")
    s.set_defaults(fn=cmd_facts)

    s = sp.add_parser("crosswalk", help="which standard clauses the register gives evidence for, and what the organisation must show",
                      allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--register", help="Learnings Register JSON (default: <run>/outputs/learnings-register.json)")
    s.add_argument("--framework", choices=["iso45001", "psm", "rmp", "seveso", "rbps", "icmm", "india"])
    s.add_argument("--system-csv", metavar="FILE", help="the organisation's own requirements (columns id,title[,topics]); replaces the framework")
    s.add_argument("--json", action="store_true", help="print the crosswalk as JSON")
    s.add_argument("--table-item", action="store_true", help="print a pack table item (JSON)")
    s.set_defaults(fn=cmd_crosswalk)

    s = sp.add_parser("evidence-audit", help="how well the evidence holds up: strength per finding, single-source and "
                                             "document-only counts, concentration (writes evidence_audit.json)",
                      allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--json", action="store_true", help="print the audit as one JSON object")
    s.add_argument("--table-item", choices=EVIDENCE_AUDIT_TABLES, metavar="|".join(EVIDENCE_AUDIT_TABLES),
                   help="print a ready table item for a pack instead of the summary")
    s.set_defaults(fn=cmd_evidence_audit)

    s = sp.add_parser("wai-wad", help="work as imagined against work as done: codes with document and work-as-done "
                                      "evidence, counterfactual wording and its questions (writes wai_wad.json)",
                      allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--json", action="store_true", help="print the comparison as one JSON object")
    s.add_argument("--table-item", choices=WAIWAD_TABLE_KINDS, metavar="|".join(WAIWAD_TABLE_KINDS),
                   help="print a ready table item for a pack instead of the summary")
    s.add_argument("--items", choices=["prompts"], help="print ready question items (what made sense at the time)")
    s.add_argument("--top", type=int, default=None, metavar="N", help="with --items: at most N prompts (default 30)")
    s.set_defaults(fn=cmd_wai_wad)

    s = sp.add_parser("hfacs-profile", help="level x subcategory heat map, code recurrence and causal feed counts",
                      allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--json", action="store_true", help="print the profile as JSON")
    s.add_argument("--table-item", dest="table_item", choices=HP_TABLE_KINDS,
                   help="print a ready table item for a pack (JSON on stdout)")
    s.set_defaults(fn=cmd_hfacs_profile)

    s = sp.add_parser("pack-xlsx", help="a pack's test points or questions as an Excel sheet", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("pack")
    s.add_argument("--kind", required=True, choices=list(XLSX_KINDS))
    s.add_argument("--out", help="default: <run>/outputs/<pack>-test-points.xlsx or -questions.xlsx (.<mode>.xlsx when shared)")
    _lint_flags(s)
    for act in s._actions:
        if "--share" in act.option_strings:
            act.help = ("internal (default), or a masked copy for outside the organisation: external or public. Needs "
                        "an approved sign-off with that classification and legal_review cleared; names, organisations, "
                        "tags, singleton roles, times and full dates are masked; written as <name>.<mode>.xlsx and never "
                        "over the internal copy")
    s.set_defaults(fn=cmd_pack_xlsx)

    s = sp.add_parser("strings", help="extract a pack's text for translation, or apply a translation as <pack>-<lang>.json",
                      allow_abbrev=False)
    s.add_argument("action", choices=["extract", "apply"])
    s.add_argument("ws")
    s.add_argument("pack")
    s.add_argument("file", nargs="?", help="apply: the translated strings file (.xlf or .csv)")
    s.add_argument("--to", choices=list(STRINGS_FORMATS),
                   help="extract: xliff (default) or csv; apply: read the file as this format (default: by its extension)")
    s.add_argument("--lang", help="the translation's language tag (extract default hi; required for apply)")
    s.add_argument("--allow-partial", dest="allow_partial", action="store_true",
                   help="apply: keep the English of untranslated units instead of refusing")
    s.add_argument("--out", help="extract: default <run>/outputs/<pack>.strings.xlf or .csv; apply: default "
                                 "<run>/outputs/<pack>-<lang>.json (never overwritten)")
    s.set_defaults(fn=cmd_strings)

    s = sp.add_parser("nine-m-seed", help="score every finding against the nine Ms (9M) and print the M profile",
                      allow_abbrev=False)
    s.add_argument("ws", help="the workspace folder (a CAPA Planner workbook is refused: pass the findings export's "
                              "workspace)")
    s.add_argument("--map", help="a 9M map in the nine-m-map.json format (default: references/nine-m-map.json)")
    s.add_argument("--out", help="default: <ws>/nine_m_seed.json")
    s.set_defaults(fn=cmd_nine_m_seed)

    s = sp.add_parser("nine-m-suggest", help="the suggestions for one 9M question (recorded with --record)",
                      allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--m", choices=NINE_M_CODES, help="the M the question is about (required for the per-M steps)")
    s.add_argument("--step", required=True, choices=list(NINE_M_STEPS + NINE_M_GLOBAL_STEPS),
                   help="per M: relevance, subcategory, condition, driver, barrier, change; global: scope, cross-m, gaps")
    s.add_argument("--subcategory", help="a subcategory id of the M, e.g. M8.02, to steer the later steps")
    s.add_argument("--top", type=int, default=4, help="how many suggestions before None / unknown (2-4, default 4)")
    s.add_argument("--record", action="store_true", help="append the question to <ws>/nine_m_session.json")
    s.add_argument("--json", action="store_true", help="print the suggestions as JSON")
    s.set_defaults(fn=cmd_nine_m_suggest)

    s = sp.add_parser("nine-m-answer", help="record the answer to a 9M question", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--q", required=True, help="the question id, e.g. Q03")
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--choice", type=int, help="the number of the suggestion chosen (1 is the recommended one)")
    g.add_argument("--text", help="the user's own answer, stored verbatim")
    s.set_defaults(fn=cmd_nine_m_answer)

    s = sp.add_parser("nine-m-replay", help="a scripted 9M session taking the recommended suggestion at every question",
                      allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--accept-recommended", dest="accept_recommended", action="store_true",
                   help="take suggestion 1 at every question (required: the session is marked as a replay)")
    s.add_argument("--ms", help="comma-separated Ms to work through, e.g. M1,M3 (default: the recommended scope)")
    s.set_defaults(fn=cmd_nine_m_replay)

    s = sp.add_parser("nine-m-actions-template", help="a blank actions sheet from a nine-m-analysis pack",
                      allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("pack")
    s.add_argument("--format", choices=["xlsx", "csv"], default="xlsx")
    s.add_argument("--out", help="default: <run>/outputs/<pack>.actions-template.xlsx or .csv (.<mode>. when shared); "
                                 "never overwritten")
    _lint_flags(s)
    for act in s._actions:
        if "--share" in act.option_strings:
            act.help = ("internal (default), or a masked copy for outside the organisation: external or public. Needs "
                        "an approved sign-off with that classification and legal_review cleared; written as "
                        "<name>.<mode>.<ext> and never over the internal copy")
    s.set_defaults(fn=cmd_nine_m_actions_template)

    s = sp.add_parser("missed-opportunities", help="earlier recommendations, Failure-to-Correct findings and dated "
                      "precursors before the incident (writes <ws>/missed_opportunities.json)", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--json", action="store_true", help="print missed_opportunities.json on stdout")
    s.add_argument("--timeline-item", dest="timeline_item", action="store_true",
                   help="print the dated missed opportunities as a ready timeline item (knowable_then: true)")
    s.add_argument("--top", type=int, default=None, metavar="N",
                   help="with --timeline-item: keep the N dated entries that cite the most findings (default: all)")
    s.set_defaults(fn=cmd_missed_opportunities)

    s = sp.add_parser("alert-grade", help="a safety alert's default learnings and its grade, from the register's "
                      "urgency or a suggestion from priority", allow_abbrev=False)
    s.add_argument("ws")
    s.add_argument("--register", help="Learnings Register JSON (default: <run>/outputs/learnings-register.json)")
    s.add_argument("--lr", action="append", metavar="LR-ID",
                   help="the learnings the alert carries (repeatable; default: the top 3 priority-1 learnings)")
    s.add_argument("--json", action="store_true", help="print {grade, grade_source, suggested, learnings, notes}")
    s.set_defaults(fn=cmd_alert_grade)

    for name in JSON_COMMANDS:   # P3-24: --json on every analysis and check command (dest as_json: check-language has a positional "json")
        sp.choices[name].add_argument("--json", dest="as_json", action="store_true",
                                      help="print one JSON object on stdout ({command, ok, exit_code, output, ...}); "
                                           "messages go to stderr; the exit code is unchanged")
    sp.choices["select"].add_argument("--json", dest="as_json", action="store_true", help="alias for --format json")
    return p


# The commands that gain --json in Task 25. check-register, plan, facts, compare and check-all had it already and keep
# their own shapes; select keeps --format json.
JSON_COMMANDS = ("profile", "classify", "causal", "timeline", "interfaces", "status", "check-pack", "check-language",
                 "check-samples", "scan-names")


def _read(ws, name):
    import json
    p = Path(ws) / name
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None


def _workspace_extras(a):
    """The data a command has just written to the workspace, as structured fields (read back, not re-derived)."""
    ws = getattr(a, "ws", None)
    if a.cmd == "classify":
        c = _read(ws, "clusters.json") or {}
        tax = c.get("taxonomy", {})
        tiers = {}
        for v in c.get("findings", {}).values():
            for t in v["T"]:
                tiers[t] = tiers.get(t, 0) + 1
        return {"entities": {e: {"name": d["name"], "findings": d["n"], "by_level": d["by_level"]}
                             for e, d in c.get("entities", {}).items()},
                "tiers": {t: {"name": tax.get("tiers", {}).get(t, ""), "findings": n} for t, n in sorted(tiers.items())},
                "roles_classified": len(c.get("role_map", {})),
                "unresolved_roles": c.get("unresolved_roles", []),
                "unresolved_count": len(c.get("unresolved_roles", [])),
                "taxonomy_version": c.get("taxonomy_version"), "taxonomy_fingerprint": c.get("taxonomy_fingerprint"),
                "statutory_roles": c.get("statutory_roles"), "overrides": c.get("overrides"),
                "written": "clusters.json"}
    if a.cmd == "causal":
        g = _read(ws, "causal_graph.json") or {}
        d = {"nodes": g.get("nodes", []), "edges": g.get("edges", []), "written": "causal_graph.json"}
        if getattr(a, "hubs", False):
            from .analysis.causal import hub_rows
            d["hubs"] = hub_rows(g)
        return d
    if a.cmd == "timeline":
        d = {"candidates": _read(ws, "timeline_candidates.json") or [], "written": "timeline_candidates.json"}
        if getattr(a, "on", None):
            d["event_day"] = _read(ws, "timeline_event_day.json") or []
        return d
    if a.cmd == "interfaces":
        return {"pairs": (_read(ws, "interfaces.json") or {}).get("pairs", []), "written": "interfaces.json"}
    return {}


def run_json(a):
    """Run a command with its stdout captured, then print one JSON object: the exit code is the command's own."""
    import contextlib
    import io
    from .util import JSON_EXTRA, emit_json
    JSON_EXTRA.clear()
    buf = io.StringIO()
    code, error = 0, None
    try:
        with contextlib.redirect_stdout(buf):
            a.fn(a)
    except SystemExit as e:
        if e.code is None:
            code = 0
        elif isinstance(e.code, int):
            code = e.code
        else:
            print(e.code, file=sys.stderr)
            code, error = 1, str(e.code)
    obj = {"command": a.cmd, "ok": code == 0, "exit_code": code}
    if error:
        obj["error"] = error
    obj.update(JSON_EXTRA)
    if code == 0:
        obj.update(_workspace_extras(a))
    obj["output"] = buf.getvalue().splitlines()
    emit_json(obj)
    return code


def main(argv=None):
    a = build_parser().parse_args(argv)
    a._argv = list(sys.argv[1:] if argv is None else argv)
    if a.cmd == "select" and getattr(a, "as_json", False):
        a.format = "json"
    elif a.cmd in JSON_COMMANDS and getattr(a, "as_json", False):
        return run_json(a)
    a.fn(a)
    return 0
