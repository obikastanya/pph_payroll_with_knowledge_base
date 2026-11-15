"""Render a prospective unit like a real document and read it back like one: teks.md -> DOCX (running header,
page numbers, annex tables) -> PDF (Word) -> text per page (pdfplumber, the extractor of the locked real texts).

teks.md: one paragraph per line, blank lines between paragraphs; a line "Pasal N" (or "BAB ...", "LAMPIRAN") is a
heading; a block of lines starting with "|" is a table. spec.json "header" is the running header (for example
"PRESIDEN REPUBLIK INDONESIA" or "MENTERI KEUANGAN REPUBLIK INDONESIA" or the company's name).

    env\\Scripts\\python -m v2.harness.render [unit ids ...]
"""
import json
import os
import subprocess
import sys
import time

import docx
import pdfplumber
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

from .prospective import UNITS

HEADING_START = ("Pasal ", "BAB ", "LAMPIRAN", "MEMUTUSKAN", "Menetapkan", "PENJELASAN")


def _page_number(paragraph):
    run = paragraph.add_run("- ")
    for kind, text in (("begin", None), (None, "PAGE"), ("end", None)):
        if kind:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), kind)
        else:
            el = OxmlElement("w:instrText")
            el.text = text
        run._r.append(el)
    paragraph.add_run(" -")


def to_docx(md_text, header, path):
    d = docx.Document()
    style = d.styles["Normal"]
    style.font.name, style.font.size = "Bookman Old Style", Pt(11)
    section = d.sections[0]
    hp = section.header.paragraphs[0]
    hp.text, hp.alignment = header, WD_ALIGN_PARAGRAPH.CENTER
    fp = section.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _page_number(fp)
    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith("|"):
            block = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(set(c) <= set("-: ") for c in cells):
                    block.append(cells)
                i += 1
            t = d.add_table(rows=len(block), cols=max(len(r) for r in block))
            t.style = "Table Grid"
            for r, row in enumerate(block):
                for c, text in enumerate(row):
                    t.cell(r, c).text = text
            continue
        if line.strip():
            p = d.add_paragraph(line.strip())
            if line.startswith(HEADING_START):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        i += 1
    d.save(path)


LOCK = UNITS.parent / ".word.lock"


def to_pdf(docx_path, pdf_path):
    """Word export, one at a time across processes (a lock file), since parallel Word automation collides."""
    script = (f"$w=New-Object -ComObject Word.Application; $d=$w.Documents.Open('{docx_path}',$false,$true); "
              f"$d.ExportAsFixedFormat('{pdf_path}',17); $d.Close($false); $w.Quit()")
    for _ in range(600):
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            if time.time() - LOCK.stat().st_mtime > 300:     # a lock left by a crashed process
                LOCK.unlink(missing_ok=True)
            time.sleep(1)
    else:
        raise TimeoutError("Word is busy")
    try:
        subprocess.run(["powershell.exe", "-NoProfile", "-Command", script], check=True, capture_output=True)
    finally:
        os.close(fd)
        LOCK.unlink(missing_ok=True)


def to_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(f"=== PDF hlm. {i} ===\n{p.extract_text() or ''}" for i, p in enumerate(pdf.pages, 1))


def render(unit_id):
    folder = UNITS / unit_id
    spec = json.loads((folder / "spec.json").read_text(encoding="utf-8"))
    to_docx((folder / "teks.md").read_text(encoding="utf-8"), spec.get("header", ""), folder / "dokumen.docx")
    to_pdf(str((folder / "dokumen.docx").resolve()), str((folder / "dokumen.pdf").resolve()))
    text = to_text(folder / "dokumen.pdf")
    (folder / "teks.txt").write_text(text, encoding="utf-8")
    (folder / "dokumen.docx").unlink()
    return len(text)


if __name__ == "__main__":
    ids = sys.argv[1:] or [d.name for d in sorted(UNITS.iterdir()) if (d / "teks.md").exists()]
    for uid in ids:
        print(uid, render(uid), "characters")
