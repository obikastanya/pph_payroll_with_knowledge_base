"""Source documents: registry, page texts, quote search, PDF extraction, segmentation, and text selection.

A document lives in workspace/documents/<id>/ as
    text.txt        one block per PDF page under "=== page N ===", in reading order
    segments.json   opening, articles, closing, and annexes, each with its page range
    tables/*.csv    tables extracted from the PDF (an update can refer to them with rows_ref)
    meta.json       id, title, and issue date
The registry lists every document a knowledge-base record may cite: the documents of the starting knowledge base
(data/kb/documents.csv) and the documents added at run time. The same normalisation is used when a quote is written
and when gate G2 checks it, so a quote that passes for one passes for the other.
"""
import csv
import json
import re
import shutil
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from . import config

PAGE_MARK = re.compile(r"^=== page (\d+) ===$", re.M)

_QUOTES = str.maketrans({"“": '"', "”": '"', "„": '"', "‘": "'", "’": "'", "–": "-",
                         "—": "-", "−": "-", "\u00a0": " ", "\u00ad": ""})


# ====================================================================================================================
# Registry, texts, and quotes
# ====================================================================================================================
def normalize(text):
    """Lower case, joined hyphenation, collapsed whitespace, unified quotes and dashes, numbers without inner
    spaces ("9. 559.600" -> "9.559.600"), "Rp 1" -> "rp1"."""
    t = text.translate(_QUOTES)
    t = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", t)
    t = t.lower()
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"(\d)\s*([.,])\s*(?=\d)", r"\1\2", t)
    t = re.sub(r"rp\.?\s+(?=\d)", "rp", t)
    t = re.sub(r"\s*%", "%", t)
    return t.strip()


def folder(doc_id):
    return config.DOCUMENTS / doc_id


@lru_cache(maxsize=None)
def registry():
    """Document id -> {id, title, issued}: the shipped registry plus the documents added at run time."""
    out = {}
    if config.REGISTRY.exists():
        with open(config.REGISTRY, encoding="utf-8", newline="") as f:
            out = {r["id"]: r for r in csv.DictReader(f)}
    for meta in sorted(config.DOCUMENTS.glob("*/meta.json")) if config.DOCUMENTS.exists() else []:
        row = json.loads(meta.read_text(encoding="utf-8"))
        out[row["id"]] = row
    return out


@lru_cache(maxsize=None)
def pages(doc_id):
    """List of (page number, raw text) of a stored document."""
    path = folder(doc_id) / "text.txt"
    if not path.exists():
        raise FileNotFoundError(f"no text for document {doc_id}: {path}")
    parts = PAGE_MARK.split(path.read_text(encoding="utf-8"))
    out = []
    if parts[0].strip():
        out.append((1, parts[0]))
    for i in range(1, len(parts), 2):
        out.append((int(parts[i]), parts[i + 1]))
    return out


@lru_cache(maxsize=None)
def normalized(doc_id):
    """Normalised full text and, for each page, the offset where it starts in that text."""
    chunks, starts, pos = [], [], 0
    for n, t in pages(doc_id):
        nt = normalize(t)
        starts.append((pos, n))
        chunks.append(nt)
        pos += len(nt) + 1
    return " ".join(chunks), starts


def find_quote(doc_id, quote):
    """Page number where the normalised quote occurs in the document, or None."""
    full, starts = normalized(doc_id)
    q = normalize(quote)
    if not q:
        return None
    i = full.find(q)
    if i < 0:
        return None
    page = starts[0][1]
    for s, n in starts:
        if s <= i:
            page = n
        else:
            break
    return page


@lru_cache(maxsize=None)
def segments(doc_id):
    path = folder(doc_id) / "segments.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def tables_of(doc_id):
    d = folder(doc_id) / "tables"
    return sorted(d.glob("*.csv")) if d.exists() else []


def clear_caches():
    for cached in (registry, pages, normalized, segments):
        cached.cache_clear()


# ====================================================================================================================
# Segmentation
# ====================================================================================================================
ARTICLE = re.compile(r"^\s*Pasal\s+([0-9]+[A-Z]?|[IVX]+)\s*$")
# Collective agreements title their articles ("Pasal 1 : Pihak-Pihak", "PASAL 7 - Upah"). Regulations do not; there
# "PASAL 25" names a tax article inside tables, and references in sentences carry "ayat".
ARTICLE_TITLED = re.compile(r"^\s*(?:Pasal|PASAL)\s+([0-9]+[A-Z]?|[IVX]+)\s*"
                            r"(?:$|[:.\-–]\s*(?!.*\bayat\b)[A-Z][^.;]{0,90}$|(?!.*\bayat\b)[A-Z][^a-z.;]{2,90}$)")
CLOSING = re.compile(r"^\s*Ditetapkan di\b", re.I)
ANNEX = re.compile(r"^\s*LAMPIRAN\b")


# ====================================================================================================================
# Cleaning at ingestion
# ====================================================================================================================
PAGE_NUMBER = re.compile(r"^\s*[-–—]?\s*\d{1,4}\s*[-–—]?\s*$")
LEGAL_LINE = re.compile(r"^\s*(pasal|bab|bagian|paragraf|ayat|huruf|lampiran|penjelasan)\b", re.I)
CONTENT_LINE = re.compile(r"[.;:,]\s*$|^\s*(\(?[0-9a-z]{1,3}[.)]|[-•*])\s")   # a sentence or a list item
EDGE = 2                      # running headers and footers sit among the first or last lines of a page
WEB_START = re.compile(r"^\s*(perjanjian kerja bersama|peraturan perusahaan)\b.{6,}", re.I)
WEB_END = re.compile(r"^\s*Tanggal dimulainya perjanjian\s*:")


def _repeat_key(line):
    return re.sub(r"\d+", "#", normalize(line))


def _furniture(line):
    """May be a running header or footer: not a heading of the document's structure, a sentence, or a list item."""
    return not LEGAL_LINE.match(line) and not CONTENT_LINE.search(line)


def _strip_web_page(text):
    """A collective agreement saved from a web page keeps only the agreement: the site menu before its title and the
    site's own summary after the signing record are dropped."""
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if WEB_START.match(l)), None)
    end = next((i for i, l in enumerate(lines) if WEB_END.match(l)), None)
    if start is None:
        return text
    if end is not None and end > start:
        end -= 1 if end - 1 > start and lines[end - 1].strip().startswith("IDN ") else 0
    else:
        end = len(lines)
    head = [l for l in lines[:start] if PAGE_MARK.match(l)][:1]
    return "\n".join(head + lines[start:end])


def clean(raw):
    """Text without page furniture: page numbers and running headers or footers at the top or bottom of a page
    (lines repeated on many pages, digits ignored), and, for a web page, the site menu and summary. Page markers and
    every other line are kept as they are."""
    if "WageIndicator" in raw:
        raw = _strip_web_page(raw)
    parts = PAGE_MARK.split(raw)
    if len(parts) < 3:
        return raw
    blocks = [(int(parts[i]), parts[i + 1].splitlines()) for i in range(1, len(parts), 2)]
    edges = []
    for _, lines in blocks:
        filled = [i for i, l in enumerate(lines) if l.strip()]
        edges.append(set(filled[:EDGE] + filled[-EDGE:]))
    counts = {}
    for (_, lines), edge in zip(blocks, edges):
        for key in {_repeat_key(lines[i]) for i in edge if _furniture(lines[i])}:
            counts[key] = counts.get(key, 0) + 1
    running = {k for k, n in counts.items() if k and n >= max(3, len(blocks) * 0.3)}
    out, seen = ([parts[0]] if parts[0].strip() else []), set()
    for (page, lines), edge in zip(blocks, edges):
        filled = [i for i, l in enumerate(lines) if l.strip()]
        ends = {filled[0], filled[-1]} if filled else set()
        kept = []
        for i, line in enumerate(lines):
            if i in ends and PAGE_NUMBER.match(line):
                continue
            key = _repeat_key(line)
            if i in edge and _furniture(line) and key in running:
                if key in seen:                     # the first occurrence stays (a title, a table's column names)
                    continue
                seen.add(key)
            kept.append(line)
        out.append(f"=== page {page} ===\n" + "\n".join(kept).strip("\n"))
    return "\n".join(out)


def segment(text, titled=False):
    """Split a document into opening, articles (Pasal), closing, and annexes (Lampiran). titled: article headings
    may carry a title, as in collective labour agreements."""
    article = ARTICLE_TITLED if titled else ARTICLE
    segs, cur = [], {"id": "opening", "kind": "opening", "heading": "opening", "page_start": 1, "lines": []}
    page = 1
    for line in text.splitlines():
        m = PAGE_MARK.match(line)
        if m:
            page = int(m.group(1))
            continue
        new = None
        a = article.match(line)
        if a:
            new = {"id": f"Pasal {a.group(1)}", "kind": "article", "heading": line.strip()}
        elif CLOSING.match(line) and cur["kind"] != "closing":
            new = {"id": "closing", "kind": "closing", "heading": "closing"}
        elif ANNEX.match(line) and cur["kind"] != "annex":
            new = {"id": f"Annex {sum(s['kind'] == 'annex' for s in segs) + 1}", "kind": "annex",
                   "heading": line.strip()[:80]}
        if new:
            cur["page_end"] = page
            segs.append(cur)
            new.update(page_start=page, lines=[])
            cur = new
        cur["lines"].append(line)
    cur["page_end"] = page
    segs.append(cur)
    out, seen = [], {}
    for s in segs:
        body = "\n".join(s.pop("lines")).strip()
        if not body:
            continue
        k = s["id"]
        seen[k] = seen.get(k, 0) + 1
        if seen[k] > 1:
            s["id"] = f"{k} ({seen[k]})"
        s["text"] = body
        out.append(s)
    return out


# ====================================================================================================================
# PDF extraction (Docling)
# ====================================================================================================================
@dataclass
class Table:
    name: str
    page: int
    frame: object          # pandas DataFrame


@dataclass
class Extraction:
    pages: list = field(default_factory=list)      # [(page number, text)]
    tables: list = field(default_factory=list)     # [Table]

    def text(self):
        return "\n".join(f"=== page {p} ===\n{t}" for p, t in self.pages)


def _tesseract():
    """Tesseract with the Indonesian model, when installed: it reads Indonesian legal text better than the default
    engine of Docling (RapidOCR, trained on Chinese and English)."""
    import subprocess
    cmd = shutil.which("tesseract") or next((p for p in (r"C:\Program Files\Tesseract-OCR\tesseract.exe",)
                                             if Path(p).exists()), None)
    if not cmd:
        return None
    try:
        langs = subprocess.run([cmd, "--list-langs"], capture_output=True, text=True, timeout=20).stdout.split()
    except (OSError, subprocess.SubprocessError):
        return None
    return cmd if "ind" in langs else None


def ocr_engine():
    return "Tesseract (ind+eng)" if _tesseract() else "RapidOCR (Docling default)"


@lru_cache(maxsize=2)
def _converter(force_ocr=False):
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import (PdfPipelineOptions, TableFormerMode, TableStructureOptions,
                                                    TesseractCliOcrOptions)
    from docling.document_converter import DocumentConverter, PdfFormatOption
    opts = PdfPipelineOptions(do_ocr=True, do_table_structure=True,
                              table_structure_options=TableStructureOptions(mode=TableFormerMode.ACCURATE))
    cmd = _tesseract()
    if cmd:
        opts.ocr_options = TesseractCliOcrOptions(lang=["ind", "eng"], tesseract_cmd=cmd)
    opts.ocr_options.force_full_page_ocr = force_ocr
    return DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)})


def extract(path, force_ocr=False, page_range=None):
    """Text and tables of a PDF file. force_ocr=True runs OCR on every page even when a text layer exists (a broken
    text layer). page_range=(first, last) limits the pages. A table is also written into its page as Markdown, so a
    quote from a table row can be found by gate G2."""
    from docling_core.types.doc import TableItem
    kwargs = {"page_range": page_range} if page_range else {}
    doc = _converter(force_ocr).convert(str(path), **kwargs).document
    by_page = {p: [] for p in sorted(doc.pages)}
    tables = []
    first = min(by_page) if by_page else 1
    for item, _level in doc.iterate_items():
        prov = getattr(item, "prov", None)
        page = prov[0].page_no if prov else first
        if isinstance(item, TableItem):
            k = sum(1 for t in tables if t.page == page) + 1
            name = f"T{page:03d}-{k}"
            try:
                frame = item.export_to_dataframe(doc=doc)
            except TypeError:
                frame = item.export_to_dataframe()
            tables.append(Table(name, page, frame))
            try:
                md = item.export_to_markdown(doc=doc)
            except TypeError:
                md = item.export_to_markdown()
            md = re.sub(r"-{3,}", "---", re.sub(r" {2,}", " ", md))       # column padding costs model tokens
            by_page.setdefault(page, []).append(f"[Table {name}]\n{md}")
        elif getattr(item, "text", None):
            by_page.setdefault(page, []).append(item.text)
    return Extraction([(p, "\n".join(by_page[p])) for p in sorted(by_page)], tables)


def add_document(doc_id, title, issued, *, pdf=None, text=None, company=False, force_ocr=False):
    """Store a new document (a PDF file path or plain text) with its segments and tables, and register it.
    company: the document is a company policy (article headings may carry titles). Returns the document folder."""
    d = folder(doc_id)
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    if pdf is not None:
        shutil.copyfile(pdf, d / "source.pdf")
        ext = extract(d / "source.pdf", force_ocr=force_ocr)
        raw = ext.text()
        if ext.tables:
            (d / "tables").mkdir()
            for t in ext.tables:
                t.frame.to_csv(d / "tables" / f"{t.name}.csv", index=False, encoding="utf-8")
    else:
        raw = text if PAGE_MARK.search(text or "") else f"=== page 1 ===\n{text or ''}"
    raw = clean(raw)
    (d / "text.txt").write_text(raw, encoding="utf-8")
    (d / "segments.json").write_text(json.dumps(segment(raw, titled=company), ensure_ascii=False, indent=1),
                                     encoding="utf-8")
    (d / "meta.json").write_text(json.dumps({"id": doc_id, "title": title, "issued": str(issued)},
                                            ensure_ascii=False, indent=1), encoding="utf-8")
    clear_caches()
    return d


# ====================================================================================================================
# Text selection for the model
# ====================================================================================================================
# Domain terms (in the language of the documents) that make a segment worth showing to the model
FIXED_TERMS = ("pasal 21", "pegawai tetap", "penghasilan bruto", "tarif", "dibulatkan", "iuran", "upah",
               "ditanggung pemerintah", "masa pajak", "penghasilan tidak kena pajak", "biaya jabatan",
               "pemotongan", "tunjangan", "natura", "batas", "berlaku", "dicabut", "tidak berlaku", "pembulatan",
               "klasifikasi lapangan usaha", "insentif")
TOKEN_BUDGET = 14000
ALWAYS_CAP = 3000          # opening and closing segments longer than this are truncated


def tokens(text):
    """Rough token count for Indonesian legal text (about 3.5 characters per token)."""
    return int(len(text) / 3.5) + 1


def cap(text):
    """An opening or closing segment cut at ALWAYS_CAP tokens."""
    return text if tokens(text) <= ALWAYS_CAP else text[: int(ALWAYS_CAP * 3.5)] + "\n[... truncated]"


@dataclass
class Selection:
    document: str
    segments: list          # segments in document order, annex text possibly replaced by a table description
    tables: list            # descriptions of the extracted tables of the document
    dropped: list           # ids of segments left out
    tokens: int


def lexicon(view):
    """Fixed domain terms plus the Indonesian labels of the records of the knowledge base."""
    terms = set(FIXED_TERMS)
    for r in view.records:
        lab = normalize(getattr(r, "label_id", "") or "")
        if len(lab) >= 5:
            terms.add(lab)
    return sorted(terms)


def extracted_tables(doc_id):
    out = []
    for p in tables_of(doc_id):
        with open(p, encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        out.append({"id": f"{doc_id}/{p.stem}", "columns": list(rows[0]) if rows else [], "rows": len(rows),
                    "sample": rows[:6]})
    return out


def table_text(t):
    lines = [f"[Extracted table {t['id']}: {t['rows']} rows; columns {', '.join(t['columns'])}. "
             f"Refer to it with rows_ref; do not copy rows. First rows:]"]
    for r in t["sample"]:
        lines.append("  " + "; ".join(f"{k}={v}" for k, v in r.items()))
    return "\n".join(lines)


def full(doc_id):
    """Every segment word for word; an annex with extracted tables as their description."""
    segs = segments(doc_id)
    if not segs:
        raise ValueError(f"document {doc_id} has no segments ({folder(doc_id) / 'segments.json'})")
    tables = extracted_tables(doc_id)
    chosen = [dict(s, text="\n".join(table_text(t) for t in tables)) if s["kind"] == "annex" and tables else dict(s)
              for s in segs]
    if tables:
        first = next(i for i, s in enumerate(chosen) if s["kind"] == "annex") if any(
            s["kind"] == "annex" for s in chosen) else None
        chosen = [s for i, s in enumerate(chosen) if s["kind"] != "annex" or i == first]
    return Selection(doc_id, chosen, tables, [], sum(tokens(s["text"]) for s in chosen))


def select(doc_id, view, budget=TOKEN_BUDGET):
    """Segments to show the model within the token budget: opening and closing always, annexes with an extracted
    table as a table description, then the segments with the most domain terms per length."""
    segs = segments(doc_id)
    if not segs:
        raise ValueError(f"document {doc_id} has no segments ({folder(doc_id) / 'segments.json'})")
    tables = extracted_tables(doc_id)
    terms = lexicon(view)
    scored = []
    for i, s in enumerate(segs):
        text = s["text"]
        if s["kind"] == "annex" and tables:
            text = "\n".join(table_text(t) for t in tables)
        nt = normalize(text)
        score = sum(len(re.findall(re.escape(t), nt)) for t in terms)
        scored.append((i, dict(s, text=text), score))
    for i, s, score in scored:
        if s["kind"] in ("opening", "closing"):
            s["text"] = cap(s["text"])
    keep = {i for i, s, _ in scored if s["kind"] in ("opening", "closing")}
    keep |= {i for i, s, _ in scored if s["kind"] == "annex" and tables}
    used = sum(tokens(scored[i][1]["text"]) for i in keep)
    # density (matches per square root of length), so that long definition articles do not crowd out short
    # substantive ones; segments without a match come last but are still taken while the budget allows
    order = sorted(scored, key=lambda t: (-(t[2] / tokens(t[1]["text"]) ** 0.5), t[0]))
    for i, s, score in order:
        if i in keep:
            continue
        n = tokens(s["text"])
        if used + n <= budget:
            keep.add(i)
            used += n
    chosen = [s for i, s, _ in scored if i in keep]
    dropped = [s["id"] for i, s, _ in scored if i not in keep]
    return Selection(doc_id, chosen, tables, dropped, used)


def render(selection):
    parts = [f"=== DOCUMENT {selection.document} ==="]
    for s in selection.segments:
        span = f" (PDF pages {s.get('page_start')}-{s.get('page_end')})" if s.get("page_start") else ""
        parts.append(f"--- {s['id']}{span} ---\n{s['text'].strip()}")
    if selection.dropped:
        shown = selection.dropped[:60]
        more = len(selection.dropped) - len(shown)
        parts.append(f"[segments not shown: {', '.join(shown)}" + (f", and {more} more" if more else "") + "]")
    return "\n\n".join(parts)
