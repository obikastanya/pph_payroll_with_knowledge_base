"""PDF extraction with Docling: the text layer where the page has one, OCR where it does not (scanned pages), and table
structure (TableFormer, accurate mode).

The result keeps the locked-text format of the corpus: one block per PDF page under "=== PDF hlm. N ===", in reading
order. A table is written into its page as Markdown (so a quote from a table row can be found by gate G2) and returned
as a DataFrame, saved as tabel/<name>.csv beside the text (the same place as the extracted tables of the corpus, which
rows_ref of a table element can point to).

The locked texts of the research corpus (dataset/13_teks) were extracted earlier with pdfplumber and OCR files, and
every gold quote and result was checked against them; they are not extracted again. Docling is used for new documents.
"""
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path


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
        return "\n".join(f"=== PDF hlm. {p} ===\n{t}" for p, t in self.pages)


def _tesseract():
    """Tesseract with the Indonesian model, when installed: it reads Indonesian legal text better than the default
    engine of Docling (RapidOCR, trained on Chinese and English)."""
    import shutil
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
    return "Tesseract (ind+eng)" if _tesseract() else "RapidOCR (bawaan Docling)"


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
    """Extraction of a PDF file. force_ocr=True runs OCR on every page even when a text layer exists (a broken
    text layer). page_range=(first, last) limits the pages."""
    from docling_core.types.doc import TableItem
    kwargs = {"page_range": page_range} if page_range else {}
    doc = _converter(force_ocr).convert(str(path), **kwargs).document
    pages = {p: [] for p in sorted(doc.pages)}
    tables = []
    first = min(pages) if pages else 1
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
            md = re.sub(r"-{3,}", "---", re.sub(r" {2,}", " ", md))       # column padding costs LLM tokens
            pages.setdefault(page, []).append(f"[Tabel {name}]\n{md}")
        elif getattr(item, "text", None):
            pages.setdefault(page, []).append(item.text)
    return Extraction([(p, "\n".join(pages[p])) for p in sorted(pages)], tables)


def write(extraction, folder):
    """teks.txt and tabel/<name>.csv (+ README.txt listing the tables) in folder."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "teks.txt").write_text(extraction.text(), encoding="utf-8")
    if extraction.tables:
        tdir = folder / "tabel"
        tdir.mkdir(exist_ok=True)
        lines = ["Tabel hasil ekstraksi Docling (TableFormer, mode akurat): nama, halaman PDF, baris x kolom"]
        for t in extraction.tables:
            t.frame.to_csv(tdir / f"{t.name}.csv", index=False, encoding="utf-8")
            lines.append(f"{t.name}\thlm. {t.page}\t{t.frame.shape[0]} x {t.frame.shape[1]}")
        (tdir / "README.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return folder / "teks.txt"
