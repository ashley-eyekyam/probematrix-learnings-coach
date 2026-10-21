"""Phase 4, Task 15: standalone SVG, PNG (through a browser) and GraphML graphs, the bow-tie CSV and the ics
follow-ups (L4-22 to L4-24, Rulings P4-18 and P4-20, owner decision OD4-2). Synthetic fixtures only."""
import csv
import datetime as dt
import io
import json
import struct
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from test_pmlc import ws  # noqa: F401  (ws is a module-scoped fixture)
from test_pack import fixture, item, pack_with, render_fixture
from test_privacy import SPACK, _cli, share_ws, sign, write_doc
import pmlc  # noqa: E402

from pmlc_lib import BRAND, STATUS_PHRASE  # noqa: E402
from pmlc_lib import render as R  # noqa: E402
from pmlc_lib.render import bowtie as RB  # noqa: E402
from pmlc_lib.pack.graph_layout import layout_graph  # noqa: E402

SVG_NS = "{http://www.w3.org/2000/svg}"
LONG = "L4 OR 2.2 Spares Programme Failure in the purchasing system"
GRAPH = {"kind": "graph", "id": "g1", "nodes": [{"id": "A", "label": LONG}, {"id": "B", "label": "Short"},
                                               {"id": "C", "label": "Fire"}],
         "edges": [{"from": "A", "to": "B", "label": "2 mentions"}, {"from": "B", "to": "C"}], "cites": ["FND-0001"]}


@pytest.fixture(scope="module")
def w(ws):  # noqa: F811
    return pmlc.load_ws(ws)


def graph_pack(**top):
    return pack_with(GRAPH, **top)


def no_browser(monkeypatch, tmp_path):
    monkeypatch.setenv("PMLC_BROWSER", "/nonexistent")
    monkeypatch.setenv("PATH", str(tmp_path))


def test_svg_standalone_unclipped(w):
    outs = render_fixture("x", "svg", w=w, pack=graph_pack())
    assert [o.name for o in outs] == ["test-pack.g1.svg"]
    text = outs[0].data
    root = ET.fromstring(text.encode("utf-8"))                     # parses as XML
    assert root.tag == SVG_NS + "svg"
    assert LONG in " ".join(" ".join(root.itertext()).split())
    assert "…" not in text
    desc = root.find(SVG_NS + "desc").text
    assert STATUS_PHRASE in desc and BRAND in desc
    assert root.find(SVG_NS + "title") is not None
    assert "<style>" in text and ".node rect{" in text                 # drawn without the page's css
    two = render_fixture("x", "svg", w=w, pack=pack_with(GRAPH, dict(GRAPH, id="g2")))
    assert [o.name for o in two] == ["test-pack.g1.svg", "test-pack.g2.svg"]
    assert render_fixture("x", "svg", w=w, pack=pack_with(item("para"))) == []


def test_layout_label_max_default_is_unchanged():
    nodes = [{"id": "A", "label": LONG}, {"id": "B", "label": "x"}]
    edges = [{"from": "A", "to": "B"}]
    assert "…" in layout_graph(nodes, edges, uid="u")["svg"]
    assert "…" not in layout_graph(nodes, edges, uid="u", label_max=None)["svg"]
    assert layout_graph(nodes, edges, uid="u") == layout_graph(nodes, edges, uid="u", label_max=28)


def test_graphml_yed_shape(w):
    outs = render_fixture("x", "graphml", w=w, pack=graph_pack())
    assert [o.name for o in outs] == ["test-pack.g1.graphml"]
    two = render_fixture("x", "graphml", w=w, pack=pack_with(GRAPH, dict(GRAPH, id="g2")))
    assert [o.name for o in two] == ["test-pack.g1.graphml", "test-pack.g2.graphml"]
    root = ET.fromstring(outs[0].data.encode("utf-8"))
    ns = "{http://graphml.graphdrawing.org/xmlns}"
    assert root.tag == ns + "graphml"
    keys = {k.get("attr.name"): k for k in root.findall(ns + "key")}
    assert "label" in keys
    g = root.find(ns + "graph")
    assert g.get("edgedefault") == "directed"
    assert len(g.findall(ns + "node")) == 3 and len(g.findall(ns + "edge")) == 2
    labels = [d.text for n in g.findall(ns + "node") for d in n.findall(ns + "data")]
    assert LONG in labels
    desc = root.find(ns + "desc").text
    assert STATUS_PHRASE in desc and BRAND in desc


def test_png_without_browser(w, monkeypatch, tmp_path, capsys):
    no_browser(monkeypatch, tmp_path)
    ctx_notes = []
    from pmlc_lib.handling import effective_handling
    pack = pmlc.with_item_ids(graph_pack())
    ctx = R.RenderContext(w=w, pack=pack, run="r", generated="2020-09-24", embed="cited",
                          eh=effective_handling(pack, w), notes=ctx_notes)
    assert R.render("png", ctx) == []
    assert R.PNG_NO_BROWSER in ctx_notes
    assert "PMLC_BROWSER" in capsys.readouterr().err                  # the unusable setting is named, once
    assert len(R.render("svg", ctx)) == 1 and len(R.render("graphml", ctx)) == 1


def test_png_no_browser_through_the_command(tmp_path):
    ws_, orgs = share_ws(tmp_path)
    doc = json.loads(json.dumps(SPACK))
    doc["sections"][0]["items"].append(dict(GRAPH))
    p = write_doc(tmp_path, doc)
    r = _cli("pack", str(ws_), str(p), "--format", "png,svg,graphml", "--out", str(tmp_path / "o"),
             env={"PMLC_BROWSER": "/nonexistent", "PATH": str(Path(sys.executable).parent)})
    assert r.returncode == 0, r.stderr
    assert R.PNG_NO_BROWSER in r.stderr
    names = sorted(x.name for x in (tmp_path / "o").iterdir())
    assert "test-pack.g1.svg" in names and "test-pack.g1.graphml" in names and not any(n.endswith(".png") for n in names)


@pytest.mark.skipif(R.find_browser() is None, reason="no Chromium-family browser")
def test_png_with_browser(w):
    outs = render_fixture("x", "png", w=w, pack=graph_pack())
    assert [o.name for o in outs] == ["test-pack.g1.png"]
    png = outs[0].data
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = struct.unpack(">II", png[16:24])
    svg = ET.fromstring(render_fixture("x", "svg", w=w, pack=graph_pack())[0].data.encode("utf-8"))
    assert width == int(svg.get("width")) and height == int(svg.get("height"))


def test_png_failure_is_a_note_not_an_error(w, monkeypatch, tmp_path):
    fake = tmp_path / "fakebrowser"
    fake.write_text("#!/bin/sh\nexit 3\n")
    fake.chmod(0o755)
    monkeypatch.setenv("PMLC_BROWSER", str(fake))
    notes = []
    from pmlc_lib.handling import effective_handling
    pack = pmlc.with_item_ids(graph_pack())
    ctx = R.RenderContext(w=w, pack=pack, run="r", generated="2020-09-24", embed="cited",
                          eh=effective_handling(pack, w), notes=notes)
    assert R.render("png", ctx) == []
    assert len(notes) == 1 and notes[0].startswith("png: the browser did not produce an image (")


def test_bowtie_csv(w):
    outs = render_fixture("barrier-learnings", "bowtie-csv", w=w)
    assert [o.name for o in outs] == ["barrier-learnings.bowtie.csv"]
    rows = list(csv.reader(io.StringIO(outs[0].data)))
    assert ",".join(rows[0]) == "side,barrier,barrier_id,state,type,hoc_tier,failure_mode,fix,owner_role,indicator,cites"
    pack = fixture("barrier-learnings")
    barriers = [i for s in pack["sections"] for i in s["items"] if i["kind"] == "barrier"]
    assert len(rows) == len(barriers) + 1
    by = {r[1]: r for r in rows[1:]}
    prev = by["materials and spares: specification of critical spares"]
    assert prev[0] == "threat" and prev[2] == "BR-12" and prev[8] == "Materials Management (F06)"
    assert prev[10] == "FND-0003;EVD-0003"
    mit = by["detection and alarm: gas detection with shutdown"]
    assert mit[0] == "consequence" and mit[8] == ""
    assert render_fixture("x", "bowtie-csv", w=w, pack=pack_with(item("para"))) == []


@pytest.mark.parametrize("group,side", [("Prevention", "threat"), ("prevent loss", "threat"), ("Mitigation", "consequence"),
                                        ("Recovery", "consequence"), ("Other", ""), (None, "")])
def test_bowtie_side(group, side):
    assert RB._bt_side(group) == side


def test_bowtie_csv_cells_are_safe_for_a_spreadsheet(w):
    b = item("barrier", barrier="=SUM(A1)", failure_mode="@x", group="Prevention")
    rows = list(csv.reader(io.StringIO(render_fixture("x", "bowtie-csv", w=w, pack=pack_with(b))[0].data)))
    assert rows[1][1] == "'=SUM(A1)" and rows[1][6] == "'@x"


@pytest.fixture(autouse=True)
def _epoch(monkeypatch):
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1600905600")


def ics_ctx(w, pack, start=None):
    from pmlc_lib.handling import effective_handling
    pack = pmlc.with_item_ids(pack)
    return R.RenderContext(w=w, pack=pack, run="2020-09-24-site-event", generated="2020-09-24", embed="cited",
                           eh=effective_handling(pack, w), start=start, notes=[])


def test_ics_needs_start(w, tmp_path):
    ctx = ics_ctx(w, fixture("safety-committee-guide"))
    assert R.render("ics", ctx) == [] and ctx.notes == [R.ICS_NEEDS_START]
    ws_, orgs = share_ws(tmp_path)
    doc = json.loads(json.dumps(SPACK))
    doc["sections"][0]["items"].append({"kind": "check", "text": "Ask for the record.", "when": "30 days"})
    p = write_doc(tmp_path, doc)
    r = _cli("pack", str(ws_), str(p), "--format", "ics", "--out", str(tmp_path / "o"))
    assert r.returncode == 0 and R.ICS_NEEDS_START in r.stderr and not list((tmp_path / "o").glob("*.ics"))
    r = _cli("pack", str(ws_), str(p), "--format", "ics", "--start", "2026-11-02", "--out", str(tmp_path / "o"))
    assert r.returncode == 0, r.stderr
    t = (tmp_path / "o" / "test-pack.ics").read_bytes().decode("utf-8")
    assert "DTSTART;VALUE=DATE:20261202" in t
    assert _cli("pack", str(ws_), str(p), "--format", "ics", "--start", "soon").returncode == 2


def test_ics_events(w):
    ctx = ics_ctx(w, fixture("safety-committee-guide"), start=dt.date(2026, 11, 2))
    outs = R.render("ics", ctx)
    assert [o.name for o in outs] == ["safety-committee-guide.ics"]
    raw = outs[0].data
    assert isinstance(raw, bytes) and b"\r\n" in raw and b"\n" not in raw.replace(b"\r\n", b"")
    t = raw.decode("utf-8")
    unfolded = t.replace("\r\n ", "")
    assert unfolded.count("BEGIN:VEVENT") == 2
    assert "DTSTART;VALUE=DATE:20261202" in unfolded and "DTSTART;VALUE=DATE:20270131" in unfolded
    assert "ATTENDEE" not in t and "ORGANIZER" not in t
    assert "X-PMLC-STATUS:" in t and "DTSTAMP:20200924T000000Z" in t
    assert STATUS_PHRASE in unfolded and "UID:2020-09-24-site-event-safety-committee-guide-" in unfolded
    assert all(len(line.encode("utf-8")) <= 75 for line in t.split("\r\n"))
    assert "FND-0002" in unfolded


@pytest.mark.parametrize("when,days", [("30 days", 30), ("1 day", 1), ("Day 14", 14), ("day 14", 14), ("2 weeks", 14),
                                       ("12 weeks", 84), ("1 week", 7)])
def test_ics_offsets(when, days):
    from pmlc_lib.render import ics as RI
    assert RI._ic_offset(when) == days


@pytest.mark.parametrize("when", ["next quarter", "1000 days", "100 weeks", "", None, "30 days later", "Q3"])
def test_ics_offsets_reject(when):
    from pmlc_lib.render import ics as RI
    assert RI._ic_offset(when) is None


def test_ics_sources_and_escaping(w):
    p = pack_with(item("check", text="A, B; C\nand a very long summary " + "x" * 90, when="Day 7"),
                  item("decision", decision="Decide", by_when="2 weeks"),
                  item("recommendation", by_when="1 week"),
                  item("check", text="No date", when="soon"))
    outs = R.render("ics", ics_ctx(w, p, start=dt.date(2026, 1, 1)))
    t = outs[0].data.decode("utf-8").replace("\r\n ", "")
    assert t.count("BEGIN:VEVENT") == 3
    assert "DTSTART;VALUE=DATE:20260108" in t and "DTSTART;VALUE=DATE:20260115" in t
    summ = next(x for x in t.split("\r\n") if x.startswith("SUMMARY:"))
    assert summ.startswith("SUMMARY:A\\, B\\; C and a very long") and len(summ) - len("SUMMARY:") <= 70 + 6


def test_graph_formats_shared_copy(tmp_path):
    ws_, orgs = share_ws(tmp_path)
    doc = json.loads(json.dumps(SPACK))
    doc["sections"][0]["items"] += [dict(GRAPH, nodes=[{"id": "A", "label": "Seal fitted at 09:15"},
                                                       {"id": "B", "label": "Leak"}, {"id": "C", "label": "Fire"}]),
                                    {"kind": "barrier", "group": "Prevention", "barrier": "seal check",
                                     "failure_mode": "skipped", "hoc_tier": "engineering",
                                     "owner": "Plant Manager", "cites": ["FND-0001"]},
                                    {"kind": "check", "text": "Ask for the record.", "when": "30 days"}]
    p = sign(ws_, write_doc(tmp_path, doc), "--classification", "external", "--legal-review", "cleared")
    r = _cli("pack", str(ws_), str(p), "--share", "external", "--orgs", str(orgs), "--embed", "summary",
             "--format", "svg,graphml,bowtie-csv,ics", "--start", "2026-11-02", "--out", str(tmp_path / "o"))
    assert r.returncode == 0, r.stderr
    names = sorted(x.name for x in (tmp_path / "o").iterdir())
    assert names == ["test-pack.bowtie.external.csv", "test-pack.external.ics", "test-pack.g1.external.graphml",
                     "test-pack.g1.external.svg"]
    for n in names:
        t = (tmp_path / "o" / n).read_text(encoding="utf-8")
        assert "09:15" not in t, n
        if n.endswith(".ics"):
            assert "UID:test-pack-" in t                                 # no run slug in a shared copy
    svg = next(n for n in names if n.endswith(".svg"))
    bow = (tmp_path / "o" / "test-pack.bowtie.external.csv").read_text(encoding="utf-8")
    assert "Plant Manager" not in bow and "Site leadership" in bow           # the owner role is generalised
    assert "Seal fitted" in (tmp_path / "o" / svg).read_text(encoding="utf-8")
