"""--json on every analysis and check command (P3-24) and the documented exit codes (P3-2)."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from test_pmlc import PMLC, make_export

ROOT = Path(__file__).resolve().parents[1]
FIX = Path(__file__).resolve().parent / "fixtures" / "packs"


def go(*args):
    return subprocess.run([sys.executable, str(PMLC), *map(str, args)], capture_output=True, text=True)


@pytest.fixture(scope="module")
def env(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("json")
    x = make_export(tmp)
    r = go("setup", x, "--slug", "pump-fire", "--root", tmp)
    assert r.returncode == 0, r.stderr
    ws = tmp / "pmlc-runs" / "2024-03-20-pump-fire" / "workspace"
    outd = ws.parent / "outputs"
    outd.mkdir(exist_ok=True)
    shutil.copy(FIX / "board-brief.json", outd / "board-brief.json")
    shutil.copy(FIX / "bad-l3-01.json", outd / "bad-l3-01.json")
    names = tmp / "names.txt"
    names.write_text("Fictional Person\n")
    (tmp / "scan").mkdir()
    (tmp / "scan" / "a.txt").write_text("nothing here\n")
    return {"ws": ws, "outd": outd, "tmp": tmp, "names": names}


def cases(e):
    ws, o = e["ws"], e["outd"]
    return [
        ("profile", [ws]), ("classify", [ws]), ("causal", [ws]), ("timeline", [ws]), ("interfaces", [ws]),
        ("status", [ws]), ("facts", [ws]), ("plan", [ws, "--workflow", "full-cascade"]),
        ("check-pack", [ws, o / "board-brief.json"]), ("check-pack", [ws, o / "bad-l3-01.json"]),
        ("check-language", [ws, o / "board-brief.json"]), ("check-language", [ws, o / "bad-l3-01.json"]),
        ("check-all", [ws]), ("check-samples", [e["tmp"] / "nosamples"]),
        ("check-samples", [e["tmp"] / "scan"]), ("scan-names", [e["names"], e["tmp"] / "scan"]),
        ("scan-names", [e["names"], o / "board-brief.json"]),
    ]


def test_json_flag_everywhere(env):
    (env["tmp"] / "nosamples").mkdir(exist_ok=True)
    seen = set()
    for cmd, args in cases(env):
        plain = go(cmd, *args)
        js = go(cmd, *args, "--json")
        assert js.returncode == plain.returncode, (cmd, args, js.stderr)
        try:
            obj = json.loads(js.stdout)
        except ValueError:
            pytest.fail(f"{cmd} {args}: rc={js.returncode} stderr={js.stderr[:300]}")
        assert isinstance(obj, dict), cmd
        seen.add(cmd)
    assert {"profile", "classify", "causal", "timeline", "interfaces", "status", "facts", "plan", "check-pack",
            "check-language", "check-all", "check-samples", "scan-names"} <= seen


def test_json_object_shape_and_failures(env):
    o = env["outd"]
    r = go("check-pack", env["ws"], o / "bad-l3-01.json", "--json")
    d = json.loads(r.stdout)
    assert r.returncode == 1 and d["ok"] is False and d["exit_code"] == 1 and d["command"] == "check-pack"
    assert d["problems"]
    d = json.loads(go("check-pack", env["ws"], o / "board-brief.json", "--json").stdout)
    assert d["ok"] is True and d["problems"] == [] and d["stats"]["sections"] >= 1
    d = json.loads(go("check-language", env["ws"], o / "board-brief.json", "--json").stdout)
    assert isinstance(d["hits"], list)
    r = go("profile", env["ws"], "--json")
    assert "# Investigation profile" in "\n".join(json.loads(r.stdout)["output"]) and "# Investigation" not in r.stdout.split('"output"')[0]


def test_json_usage_error_stays_exit_2(env):
    r = go("profile", env["ws"], "--json", "--nope")
    assert r.returncode == 2 and r.stdout == ""


def test_select_json_alias(env):
    a = go("select", env["ws"], "--format", "json")
    b = go("select", env["ws"], "--json")
    assert a.returncode == b.returncode == 0 and a.stdout == b.stdout
    json.loads(b.stdout)


def test_exit_codes_documented():
    page = (ROOT / "docs" / "manual" / "Commands.md").read_text(encoding="utf-8")
    sec = page.split("## Exit codes", 1)[1].split("\n## ", 1)[0]
    assert "| 0 | OK" in sec and "| 1 | Problems found, or the plan cannot be resolved" in sec
    assert "| 2 | Usage error" in sec and "the plan is complete (`plan --next`)" in sec
    assert "`check-*` commands never use 2 for problems" in sec


def jrun(*args):
    r = go(*args, "--json")
    return r, json.loads(r.stdout)


def test_profile_structured(env):
    r, d = jrun("profile", env["ws"])
    f = json.loads((env["ws"] / "findings.json").read_text())
    findings = f["findings"] if isinstance(f, dict) else f
    assert d["findings"] == len(findings) and sum(d["levels"].values()) == len(findings)
    assert isinstance(d["flags"], list) and isinstance(d["empty_columns"], list)


def test_classify_structured(env):
    r, d = jrun("classify", env["ws"])
    c = json.loads((env["ws"] / "clusters.json").read_text())
    for t, v in d["tiers"].items():
        assert v["findings"] == sum(1 for x in c["findings"].values() if t in x["T"])
    assert set(d["entities"]) == set(c["entities"])
    assert d["unresolved_count"] == len(c["unresolved_roles"])
    assert d["taxonomy_fingerprint"] == c["taxonomy_fingerprint"]


def test_causal_structured(env):
    r, d = jrun("causal", env["ws"], "--hubs")
    g = json.loads((env["ws"] / "causal_graph.json").read_text())
    assert d["edges"] == g["edges"] and isinstance(d["hubs"], list)


def test_timeline_structured(env):
    r, d = jrun("timeline", env["ws"])
    assert d["candidates"] == json.loads((env["ws"] / "timeline_candidates.json").read_text())


def test_interfaces_structured(env):
    r, d = jrun("interfaces", env["ws"])
    assert d["pairs"] == json.loads((env["ws"] / "interfaces.json").read_text())["pairs"]


def test_status_structured(env):
    r, d = jrun("status", env["ws"])
    assert {"file": "findings.json", "state": "current", "reason": ""} in d["files"]
    assert isinstance(d["packs"], list) and isinstance(d["sign_offs"], list)


@pytest.mark.parametrize("args", [["profile", "NOPE"], ["classify", "NOPE"], ["check-pack", "NOPE", "x.json"],
                                  ["check-samples", "NOPE"]])
def test_json_failure_carries_reason(args, env):
    r, d = jrun(*args)
    assert r.returncode == 1 and d["ok"] is False and d["exit_code"] == 1 and d["error"]
    assert d["error"] in r.stderr


def test_scan_names_hit_count(env):
    r, d = jrun("scan-names", env["names"], env["tmp"] / "scan")
    assert d["hit_count"] == 0 and "hits" not in d
