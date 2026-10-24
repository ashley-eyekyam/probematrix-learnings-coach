"""Translation round trip for a learning pack (L4-14, L1-08; Rulings P4-13 and P4-14): `strings extract` writes the
pack's translatable text as XLIFF 1.2 or CSV for a translator, and `strings apply` reads the translated file back
into a variant pack <pack>-<lang>.json. Locked fields (ids, cites, enums, dates, the status line) are never offered;
inline citations travel as placeholders that must come back exactly; safety-critical items carry their English
source text and a back-translation. Neither file is ever overwritten (they hold a translator's or reviewer's work)."""
from __future__ import annotations

import copy
import csv
import functools
import io
import json
import re
import sys
import xml.etree.ElementTree as ET
import xml.parsers.expat
from pathlib import Path
from xml.sax.saxutils import escape as _st_xml_escape

from . import BRAND
from .handling import status_line
from .util import REFS

XLIFF_NS = "urn:oasis:names:tc:xliff:document:1.2"
STRINGS_FORMATS = ("xliff", "csv")
CSV_COLUMNS = ["id", "source", "target", "note"]
BACK_TRANSLATION = "#back_translation"
DOCTYPE_REFUSAL = "strings file must not contain a DOCTYPE or entity declarations"
NOT_UTF8 = ("strings file must be UTF-8 text (in Excel, save as \"CSV UTF-8\"; in a translation tool, export UTF-8 "
            "XLIFF)")
# Never offered for translation, wherever they sit (P4-13), plus what apply itself writes and the sign-off block.
LOCKED_FIELDS = frozenset({
    "schema", "pack", "skill", "status", "scope", "kind", "id", "cites", "supporting_cites", "row_cites",
    "row_supporting_cites", "evidence_strength", "hoc_tier", "group", "learning", "clauses", "comparator_refs", "state",
    "type", "hold_point", "seconds", "offset", "correct", "date", "time", "barrier_id", "channel", "lint_ok",
    "handling", "lang", "dir", "translation_of", "source_text", "back_translation", "lens"})
SAFETY_RX = re.compile(r"\b(stop|halt|do not (start|proceed|restart|enter))\b", re.I)
_ST_ID = r"(?:FND-[0-9A-Za-z]{4,}|EVD-\d{3,})"
_ST_CITE_RX = re.compile(rf"\[[^\[\]]*\b{_ST_ID}\b[^\[\]]*\]|\b{_ST_ID}\b")   # a [FND-…; EVD-…] bracket, or a bare ID
_ST_PH_RX = re.compile(r"\{(c\d+)\}")
_ST_FORMULA_LEAD = ("=", "+", "-", "@", "\t", "\r")


class StringsError(Exception):
    """A strings file that cannot be applied: the message says why (the command exits 1 and writes nothing)."""


# ----------------------------------------------------------------------------- units

def _st_path(toks) -> str:
    out = ""
    for t in toks:
        out += f"[{t}]" if isinstance(t, int) else (f".{t}" if out else str(t))
    return out


def _st_has_words(s: str) -> bool:
    return any(ch.isalpha() for ch in _ST_CITE_RX.sub("", s))


def _st_walk(v, toks=(), parent=None):
    """The token paths of every translatable string under v."""
    if isinstance(v, str):
        if _st_has_words(v):
            yield toks
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from _st_walk(x, toks + (i,), parent)
    elif isinstance(v, dict):
        for k, x in v.items():
            if k in LOCKED_FIELDS or (parent == "edges" and k in ("from", "to")):
                continue
            yield from _st_walk(x, toks + (k,), k)


def _st_get(d, toks):
    for t in toks:
        d = d[t]
    return d


def _st_set(d, toks, value) -> None:
    _st_get(d, toks[:-1])[toks[-1]] = value


def _st_placeholders(text: str) -> tuple:
    """(text with each citation as {c1}, {c2}…, {"c1": original})."""
    found = {}

    def sub(m):
        key = f"c{len(found) + 1}"
        found[key] = m.group(0)
        return "{" + key + "}"
    return _ST_CITE_RX.sub(sub, text), found


def _st_item_strings(it) -> list:
    return [(toks, _st_get(it, toks)) for toks in _st_walk(it)]


def safety_critical(item) -> bool:
    """P4-14: a check with hold_point true, or any item whose English text says stop, halt or do not start, proceed,
    restart or enter. A translated item is judged on its source_text as well."""
    if not isinstance(item, dict):
        return False
    if item.get("kind") == "check" and item.get("hold_point") is True:
        return True
    texts = [s for _, s in _st_item_strings(item)]
    if isinstance(item.get("source_text"), dict):
        texts += [s for s in item["source_text"].values() if isinstance(s, str)]
    return any(SAFETY_RX.search(s) for s in texts)


def _st_units(pack) -> list:
    """[(path, english, tokens or None, item tokens or None)]: every translatable string in walk order, with a
    <item>#back_translation unit after the last unit of each safety-critical item (its English is the item's text)."""
    out = []
    for toks in _st_walk(pack):
        out.append((_st_path(toks), _st_get(pack, toks), toks,
                    toks[:4] if len(toks) > 4 and toks[0] == "sections" and toks[2] == "items" else None))
    res, i = [], 0
    while i < len(out):
        item = out[i][3]
        j = i
        while j < len(out) and item is not None and out[j][3] == item:
            j += 1
        if item is None:
            res.append(out[i])
            i += 1
            continue
        res += out[i:j]
        if safety_critical(_st_get(pack, item)):
            res.append((_st_path(item) + BACK_TRANSLATION, "\n".join(u[1] for u in out[i:j]), None, item))
        i = j
    return res


def units(pack) -> list:
    """[(path, source)]: the translation units of a pack, with citations as {c1}… placeholders."""
    return [(p, _st_placeholders(eng)[0]) for p, eng, _, _ in _st_units(pack)]


# ----------------------------------------------------------------------------- glossary notes

@functools.lru_cache(maxsize=1)
def _st_glossary() -> tuple:
    data = json.loads((REFS / "glossary.json").read_text(encoding="utf-8"))
    return tuple((t["term"], bool(t.get("do_not_translate")), dict(t.get("translations") or {}),
                  re.compile(rf"(?<!\w){re.escape(t['term'])}(?:s|es)?(?!\w)", re.I)) for t in data["terms"])


def _st_note(path: str, english: str, lang: str) -> str:
    """The glossary terms found in a unit's English, as `term = translation` or `term (keep as written)`."""
    parts = []
    for term, keep, tr, rx in _st_glossary():
        if rx.search(english):
            if keep:
                parts.append(f"{term} (keep as written)")
            elif tr.get(lang):
                parts.append(f"{term} = {tr[lang]}")
            else:
                parts.append(term)
    note = ("back-translation: write your translation of this safety-critical item back into English, for a reviewer "
            "to compare with the source; " if path.endswith(BACK_TRANSLATION) else "")
    return note + ("glossary: " + "; ".join(parts) if parts else "")


# ----------------------------------------------------------------------------- extract

def _st_xml_inline(text: str) -> str:
    """Escaped text with each {cN} as an XLIFF <x/> placeholder."""
    out, last = [], 0
    for m in _ST_PH_RX.finditer(text):
        out += [_st_xml_escape(text[last:m.start()]), f'<x id="{m.group(1)}" ctype="x-pmlc-cite"/>']
        last = m.end()
    return "".join(out) + _st_xml_escape(text[last:])


def _st_cell(s: str) -> str:
    return "'" + s if s.startswith(_ST_FORMULA_LEAD) else s


def _st_uncell(s: str) -> str:
    return s[1:] if s.startswith("'") and s[1:].startswith(_ST_FORMULA_LEAD) else s


def extract(pack, lang, fmt) -> str:
    """The pack's translation units as an XLIFF 1.2 document (fmt "xliff") or a CSV (fmt "csv", with a byte-order mark
    so that Excel opens it as UTF-8)."""
    us = [(p, src, eng) for (p, eng, _, _), (_, src) in zip(_st_units(pack), units(pack))]
    if fmt == "csv":
        buf = io.StringIO(newline="")
        w = csv.writer(buf, lineterminator="\r\n")
        w.writerow(CSV_COLUMNS)
        for p, src, eng in us:
            note = "; ".join(x for x in (f"target-language: {lang}", _st_note(p, eng, lang)) if x)
            w.writerow([p, _st_cell(src), "", _st_cell(note)])
        return "\ufeff" + buf.getvalue()
    a = lambda s: _st_xml_escape(s, {'"': "&quot;"})   # noqa: E731
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', f'<xliff version="1.2" xmlns="{XLIFF_NS}">',
             f' <file original="{a(str(pack.get("pack", "")))}.json" source-language="en" target-language="{a(lang)}" '
             f'datatype="plaintext">', "  <header>",                 # the status and the brand: a file-level
             f'   <note from="pmlc">{_st_xml_escape(status_line(pack.get("status") or ""))}</note>',   # note (P4-20)
             f'   <note from="pmlc">{_st_xml_escape(BRAND)}</note>', "  </header>", "  <body>"]
    for p, src, eng in us:
        note = _st_note(p, eng, lang)
        lines += [f'   <trans-unit id="{a(p)}">', f"    <source>{_st_xml_inline(src)}</source>",
                  '    <target state="needs-translation"/>']
        if note:
            lines.append(f"    <note>{_st_xml_escape(note)}</note>")
        lines.append("   </trans-unit>")
    lines += ["  </body>", " </file>", "</xliff>", ""]
    return "\n".join(lines)


# ----------------------------------------------------------------------------- apply

def _st_xml_text(el) -> str:
    """An element's text with <x id="cN"/> placeholders back as {cN}."""
    parts = [el.text or ""]
    for child in el:
        if child.tag.rsplit("}", 1)[-1] in ("x", "ph", "bx", "ex") and child.get("id"):
            parts.append("{" + child.get("id") + "}")
        else:
            parts.append(_st_xml_text(child))
        parts.append(child.tail or "")
    return "".join(parts)


def _st_decode(data: bytes) -> str:
    """A strings file's bytes as text: strict UTF-8 with an optional byte-order mark, never UTF-16 or a legacy code
    page (a UTF-16 file without a BOM is ASCII plus NULs, so NULs are refused too)."""
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        raise StringsError(NOT_UTF8) from e
    return _st_text(text)


def _st_text(text: str) -> str:
    text = text.lstrip("\ufeff")
    if "\x00" in text or "\ufffd" in text:
        raise StringsError(NOT_UTF8)
    return text


def _st_no_doctype(text: str) -> str:
    """text, refused when it declares a DOCTYPE or an entity: first by a plain search, then by expat itself (which
    stops at the first declaration, before any entity is expanded). The XML declaration is dropped, because the text
    is already decoded and a stale encoding="UTF-16" must not steer the parser."""
    if re.search(r"<!\s*(DOCTYPE|ENTITY)", text, re.I):
        raise StringsError(DOCTYPE_REFUSAL)
    text = re.sub(r"\A\s*<\?xml[^>]*\?>", "", text)

    def refuse(*_):
        raise StringsError(DOCTYPE_REFUSAL)
    scan = xml.parsers.expat.ParserCreate("UTF-8")
    scan.StartDoctypeDeclHandler = refuse
    scan.EntityDeclHandler = refuse
    scan.UnparsedEntityDeclHandler = refuse
    try:
        scan.Parse(text.encode("utf-8"), True)
    except xml.parsers.expat.ExpatError as e:
        raise StringsError(f"strings file is not a valid XLIFF document ({e})") from e
    return text


def _st_read_xliff(text: str, lang: str) -> dict:
    text = _st_no_doctype(_st_text(text))
    try:
        root = ET.fromstring(text)                  # the same checked str, never the file's raw bytes
    except ET.ParseError as e:
        raise StringsError(f"strings file is not a valid XLIFF document ({e})") from e
    for f in root.iter():
        if f.tag.rsplit("}", 1)[-1] == "file" and f.get("target-language") and f.get("target-language") != lang:
            raise StringsError(f"the strings file is for {f.get('target-language')}, not {lang}")
    got = {}
    for tu in root.iter():
        if tu.tag.rsplit("}", 1)[-1] != "trans-unit":
            continue
        src = tgt = None
        for child in tu:
            name = child.tag.rsplit("}", 1)[-1]
            if name == "source":
                src = _st_xml_text(child)
            elif name == "target":
                tgt = _st_xml_text(child)
        got[tu.get("id", "")] = (src, tgt)
    return got


def _st_read_csv(text: str, lang: str) -> dict:
    rows = csv.reader(io.StringIO(_st_text(text), newline=""))
    head = [h.strip().lower() for h in next(rows, [])]
    if "id" not in head or "target" not in head:
        raise StringsError("a strings CSV needs the columns id and target (and source, note)")
    ix = {h: head.index(h) for h in ("id", "source", "target", "note") if h in head}
    got = {}
    for r in rows:
        cell = {h: (_st_uncell(r[i]) if i < len(r) else "") for h, i in ix.items()}
        if not cell["id"].strip():
            continue                                            # Excel's blank rows
        m = re.match(r"target-language: ([^;\s]+)", cell.get("note") or "")
        if m and m.group(1) != lang:
            raise StringsError(f"the strings file is for {m.group(1)}, not {lang}")
        got[cell["id"].strip()] = (cell.get("source"), cell["target"])
    return got


def _st_same(a: str, b: str) -> bool:
    return " ".join(a.split()) == " ".join(b.split())


def apply(pack, text, lang, fmt, allow_partial=False) -> dict:
    """The translated variant of pack from a filled strings file (StringsError when it cannot be applied)."""
    if isinstance(text, bytes):
        text = _st_decode(text)
    got = _st_read_xliff(text, lang) if fmt == "xliff" else _st_read_csv(text, lang)
    us = _st_units(pack)
    known = {u[0] for u in us}
    extra = [k for k in got if k not in known]
    if extra:
        raise StringsError(f"{extra[0]}: not a unit of this pack ({len(extra)} in all); extract the strings again")
    out = copy.deepcopy(pack)
    out.pop("handling", None)                     # a sign-off of the English is not a sign-off of the translation
    untranslated, sources, backs = [], {}, {}
    for path, eng, toks, item in us:
        src, mapping = _st_placeholders(eng)
        file_src, tgt = got.get(path, (None, None))
        if file_src is not None and not _st_same(file_src, src):
            raise StringsError(f"{path}: the English has changed since extract; extract the strings again")
        if item is not None and toks is not None and safety_critical(_st_get(pack, item)):
            sources.setdefault(item, {})[_st_path(toks[4:])] = eng
        tgt = (tgt or "").replace("\r\n", "\n").strip()
        if not tgt:
            untranslated.append(path)
            continue
        want, have = sorted(mapping), sorted(_ST_PH_RX.findall(tgt))
        if want != have:
            miss = [x for x in want if x not in have] or [x for x in have if x not in want]
            raise StringsError(f"{path}: placeholders differ from the source ({', '.join('{' + x + '}' for x in miss)} "
                               f"missing or added); keep every {{cN}} exactly once")
        if _ST_CITE_RX.search(tgt):
            raise StringsError(f"{path}: the translation adds a Finding or Evidence ID; citations travel only as the "
                               f"{{cN}} placeholders")
        value = _ST_PH_RX.sub(lambda m: mapping[m.group(1)], tgt)
        if toks is None:
            backs[item] = value
        else:
            _st_set(out, toks, value)
    if untranslated and not allow_partial:
        raise StringsError(f"{len(untranslated)} units are untranslated (first: {untranslated[0]}); translate them, or "
                           f"pass --allow-partial to keep their English")
    for item, st in sources.items():
        it = _st_get(out, item)
        it["source_text"] = st
        if item in backs:
            it["back_translation"] = backs[item]
    head = {"pack": f"{pack['pack']}-{lang.lower()}", "schema": pack.get("schema"),
            "skill": pack.get("skill") or _st_skill_of(pack.get("pack")), "translation_of": pack["pack"], "lang": lang}
    return {**{k: v for k, v in head.items() if v is not None}, **{k: v for k, v in out.items() if k not in head}}


def _st_skill_of(name):
    """A pack with no `skill` field is named after its skill (P4-22); None when no such skill exists."""
    from .pack.schema import pack_fits_skill
    return name if isinstance(name, str) and pack_fits_skill(name, name) else None


# ----------------------------------------------------------------------------- the command

def _st_refuse_existing(target: Path, what: str) -> None:
    if target.exists():
        sys.exit(f"{target} already exists and may hold {what}; move it or pass a new --out")


def _st_write_new(target: Path, data: bytes, what: str) -> None:
    """Write data to a file that must not exist yet (exclusive create, so a file that appears meanwhile is kept)."""
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(target, "xb") as fh:
            fh.write(data)
    except FileExistsError:
        _st_refuse_existing(target, what)


def _st_load_pack(path) -> dict:
    p = Path(path)
    if not p.is_file():
        sys.exit(f"No pack file {path}")
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError):
        d = None
    if not (isinstance(d, dict) and isinstance(d.get("pack"), str) and isinstance(d.get("sections"), list)):
        sys.exit(f"{p} is not a learning pack (it needs 'pack' and 'sections')")
    return d


def cmd_strings(a):
    from .render.labels import LOCALE_RX
    from .workspace import outputs_dir
    if a.lang is not None and not LOCALE_RX.fullmatch(a.lang):
        sys.exit("--lang must be a language tag such as hi or pt-BR")
    out_dir = outputs_dir(a.ws)
    if a.action == "extract":
        if a.file:
            sys.exit("strings extract takes no strings file; did you mean strings apply?")
        pack = _st_load_pack(a.pack)
        fmt, lang = a.to or "xliff", a.lang or "hi"
        target = Path(a.out) if a.out else out_dir / f"{pack['pack']}.strings.{'xlf' if fmt == 'xliff' else 'csv'}"
        _st_refuse_existing(target, "your translator's work")
        text = extract(pack, lang, fmt)
        _st_write_new(target, text.encode("utf-8"), "your translator's work")
        n = len(units(pack))
        print(f"strings written to {target} ({n} units, {fmt}, en -> {lang}); translate the targets, then run "
              f"strings apply")
        return
    if not a.file:
        sys.exit("strings apply needs the strings file: strings apply <ws> <pack.json> <strings-file> --lang <lang>")
    if not a.lang:
        sys.exit("strings apply needs --lang, the language of the translation (for example --lang hi)")
    pack = _st_load_pack(a.pack)
    sf = Path(a.file)
    if not sf.is_file():
        sys.exit(f"strings file {sf} not found")
    target = Path(a.out) if a.out else out_dir / f"{pack['pack']}-{a.lang.lower()}.json"
    _st_refuse_existing(target, "a reviewed translation")
    try:
        raw = _st_decode(sf.read_bytes())           # read once; everything below sees only this checked text
        fmt = a.to or ("csv" if sf.suffix.lower() == ".csv" or not raw.lstrip().startswith("<") else "xliff")
        result = apply(pack, raw, a.lang, fmt, allow_partial=a.allow_partial)
    except StringsError as e:
        print(str(e), file=sys.stderr)
        sys.exit(f"strings file {sf} not applied; nothing written")
    _st_write_new(target, (json.dumps(result, indent=1, ensure_ascii=False) + "\n").encode("utf-8"),
                  "a reviewed translation")
    print(f"translation written to {target}; check it with check-pack, and have a fluent speaker review it before use")
