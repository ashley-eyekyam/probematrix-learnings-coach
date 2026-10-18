#!/usr/bin/env python3
"""Smoke test: ingest the Hazira sample into a temp root and check the baseline.

Uses only the standard library. Exits non-zero naming the failing assertion.
Later tasks add assertions here.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(ROOT, "skills", "learnings-coach", "scripts", "pmlc.py")
SAMPLE = os.path.join(ROOT, "samples", "2020-09-24-hazira-gas-release-fire")
EXPORT = os.path.join(SAMPLE, "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx")
REGISTER = os.path.join(SAMPLE, "outputs", "learnings-register.json")
RUN_NAME = "2020-09-24-hazira-gas-release-fire"

EXPECT_FINDINGS = 436
EXPECT_EVIDENCE = 46


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
        pmlc("ingest", EXPORT, "--slug", "hazira-gas-release-fire", "--root", tmp)
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

        out = pmlc("check-register", ws, REGISTER)
        if not re.search(r"; 0 problem\(s\)\.", out):
            fail("check-register did not report 0 problem(s):\n" + out)

    print("smoke OK: %d findings, %d evidence, register 0 problems" % (EXPECT_FINDINGS, EXPECT_EVIDENCE))


if __name__ == "__main__":
    main()
