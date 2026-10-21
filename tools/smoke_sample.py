#!/usr/bin/env python3
"""Smoke test: ingest the Hazira sample into a temp root and check the baseline.

Exits non-zero naming the failing assertion. Needs requirements-dev.txt (openpyxl, and pytest for the synthetic
export that tests/test_pmlc.py builds, used by the fixture --strict check).
Checks: ingest cross-check, finding and evidence counts, check-register (also --strict) and check-language on
the sample register, facts --json, plan --workflow for every preset, every fixture pack under --strict, and the
Phase 4 exit-gate format loop: every Hazira golden pack with a pack profile passes check-pack --strict and renders in
html,md,docx,pptx,email,csv (each docx and pptx a sound package).
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(ROOT, "skills", "learnings-coach", "scripts", "pmlc.py")
SAMPLE = os.path.join(ROOT, "samples", "2020-09-24-hazira-gas-release-fire")
EXPORT = os.path.join(SAMPLE, "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx")
REGISTER = os.path.join(SAMPLE, "outputs", "learnings-register.json")
WORKFLOWS = os.path.join(ROOT, "skills", "learnings-coach", "references", "workflows.json")
RUN_NAME = "2020-09-24-hazira-gas-release-fire"
PROFILES = os.path.join(ROOT, "skills", "learnings-coach", "references", "pack-profiles.json")
GATE_FORMATS = "html,md,docx,pptx,email,csv"
GATE_FILES = ("html", "md", "docx", "pptx", "email.html", "email.txt")

EXPECT_FINDINGS = 436
EXPECT_EVIDENCE = 46
EXPECT_PRESETS = 9


def fail(msg):
    print("smoke FAILED: " + msg, file=sys.stderr)
    sys.exit(1)


def pmlc(*args):
    r = subprocess.run([sys.executable, ENGINE, *args], capture_output=True, text=True)
    if r.returncode != 0:
        fail("pmlc %s exited %d\n%s%s" % (args[0], r.returncode, r.stdout, r.stderr))
    return r.stdout


def main():
    with tempfile.TemporaryDirectory() as tmp:
        out = pmlc("ingest", EXPORT, "--slug", "hazira-gas-release-fire", "--root", tmp)
        if "Analysis Statistics agrees (436)" not in out:
            fail("ingest did not cross-check Analysis Statistics:\n" + out)
        if "missing: none; unknown: none" not in out:
            fail("ingest reported schema drift on the sample:\n" + out)
        ws = os.path.join(tmp, "pmlc-runs", RUN_NAME, "workspace")
        if not os.path.isdir(ws):
            fail("workspace not created at " + ws)
        pmlc("classify", ws, "--overlay", "india-process-site")

        with open(os.path.join(ws, "findings.json"), encoding="utf-8") as fh:
            findings = json.load(fh)
        if len(findings) != EXPECT_FINDINGS:
            fail("expected %d findings, got %d" % (EXPECT_FINDINGS, len(findings)))
        with open(os.path.join(ws, "evidence.json"), encoding="utf-8") as fh:
            evidence = json.load(fh)
        if len(evidence) != EXPECT_EVIDENCE:
            fail("expected %d evidence items, got %d" % (EXPECT_EVIDENCE, len(evidence)))

        for strict in ((), ("--strict",)):                 # Ruling X34: the sample also passes --strict
            out = pmlc("check-register", ws, REGISTER, *strict)
            if not re.search(r"; 0 problem\(s\)\.", out):
                fail("check-register %s did not report 0 problem(s):\n" % " ".join(strict) + out)

        facts = json.loads(pmlc("facts", ws, "--json"))
        if facts.get("findings") != EXPECT_FINDINGS:
            fail("facts --json gave findings %r, expected %d" % (facts.get("findings"), EXPECT_FINDINGS))

        with open(WORKFLOWS, encoding="utf-8") as fh:
            presets = list(json.load(fh))
        if len(presets) != EXPECT_PRESETS:
            fail("expected %d workflow presets, got %d: %s" % (EXPECT_PRESETS, len(presets), ", ".join(presets)))
        for preset in presets:                                # pmlc() fails on a non-zero exit
            pmlc("plan", ws, "--workflow", preset)
        print("smoke: plan --workflow exits 0 for all %d presets" % len(presets))

        out = pmlc("check-language", ws, REGISTER)
        if not re.search(r"^check-language: 0 errors, \d+ warnings$", out, re.M):
            fail("check-language did not report 0 errors on the sample register:\n" + out)

        print("smoke: %d fixture packs pass check-pack --strict" % strict_fixtures(tmp))
        print("smoke: %d Hazira golden packs pass check-pack --strict and render in %s"
              % (format_loop(tmp), GATE_FORMATS))

    print("smoke OK: %d findings, %d evidence, register 0 problems, language 0 errors"
          % (EXPECT_FINDINGS, EXPECT_EVIDENCE))


def strict_fixtures(tmp):
    """Ruling P3-5: every committed fixture pack (and so every golden) passes check-pack --strict on the synthetic
    workspace the tests build (tests/test_pmlc.py make_export)."""
    sys.path.insert(0, os.path.join(ROOT, "tests"))
    from test_pmlc import make_export  # noqa: E402  (synthetic, fictional export)
    d = os.path.join(tmp, "synthetic")
    os.makedirs(d)
    pmlc("ingest", str(make_export(pathlib.Path(d))), "--legacy-out", os.path.join(d, "ws"))
    pmlc("classify", os.path.join(d, "ws"))
    fix = os.path.join(ROOT, "tests", "fixtures", "packs")
    names = sorted(f for f in os.listdir(fix) if f.endswith(".json") and f not in ("all-kinds.json", "bad-l3-01.json", "html-golden.json"))
    for f in names:
        pmlc("check-pack", os.path.join(d, "ws"), os.path.join(fix, f), "--strict")
    return len(names)


def format_loop(tmp):
    """The Phase 4 exit gate (Task 23): every Hazira golden pack that has a pack profile (so not the register and not
    dossier-index) passes check-pack --strict against a freshly set-up Hazira workspace, then renders in every exit-gate
    format. The samples stay drafts: nothing here signs them off."""
    sys.path.insert(0, os.path.join(ROOT, "tests"))
    from ooxml_check import check_package  # noqa: E402  (stdlib-only structural check, Ruling P4-28)
    root = os.path.join(tmp, "hazira-gate")
    pmlc("setup", EXPORT, "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", root,
         "--overlay", "india-process-site")
    run_dir = os.path.join(root, "pmlc-runs", RUN_NAME)
    ws = os.path.join(run_dir, "workspace")
    shutil.copy(REGISTER, os.path.join(run_dir, "outputs", "learnings-register.json"))
    with open(PROFILES, encoding="utf-8") as fh:
        profiled = set(json.load(fh))
    outputs = os.path.join(SAMPLE, "outputs")
    names = sorted(f[:-5] for f in os.listdir(outputs) if f.endswith(".json") and f[:-5] in profiled)
    if not names:
        fail("no Hazira golden pack with a pack profile in " + outputs)
    out = os.path.join(tmp, "hazira-gate-out")
    for name in names:
        path = os.path.join(outputs, name + ".json")
        pmlc("check-pack", ws, path, "--strict", "--register", REGISTER)
        pmlc("pack", ws, path, "--format", GATE_FORMATS, "--out", out)
        for ext in GATE_FILES:
            f = os.path.join(out, "%s.%s" % (name, ext))
            if not os.path.isfile(f):
                fail("pack --format %s wrote no %s" % (GATE_FORMATS, f))
            if ext in ("docx", "pptx"):
                problems = check_package(f)
                if problems:
                    fail("%s is not a sound package: %s" % (f, "; ".join(problems)))
    return len(names)


if __name__ == "__main__":
    main()
