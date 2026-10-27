"""Build the locked text store dataset/13_teks (akuisisi.md 3.1).

    env\\Scripts\\python system\\tools\\build_texts.py            # build missing documents
    env\\Scripts\\python system\\tools\\build_texts.py --force    # rebuild all

For every document in the registry: text per page (pdfplumber, HTML text, Markdown as is, or stored OCR for scanned
PDFs), segments (opening, articles, closing, annexes), and SHA-256 of source file and text in MANIFEST.sha256.
The registry dataset/13_teks/dokumen.csv is written from the event table, the policy indexes, and the background list
below.
"""
import csv
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "dataset"
OUT = DATA / "13_teks"

# id, files (relative to dataset/), issued, title, role
BACKGROUND = [
    ("UU-36-2008", ["01_regulasi/UU_36_2008_PPh.pdf"], "2008-09-23", "UU 36/2008 perubahan keempat UU PPh", "background"),
    ("UU-7-2021", ["01_regulasi/UU_7_2021_HPP.pdf"], "2021-10-29", "UU 7/2021 Harmonisasi Peraturan Perpajakan", "background"),
    ("PMK-101-PMK010-2016", ["01_regulasi/PMK_101_PMK010_2016.pdf"], "2016-06-27", "PMK 101/PMK.010/2016 PTKP", "background"),
    ("PER-16-PJ-2016", ["01_regulasi/PER_16_PJ_2016.pdf"], "2016-09-29", "PER-16/PJ/2016 pedoman pemotongan PPh 21", "background"),
    ("PP-44-2015", ["01_regulasi/PP_44_2015_JKK_JKM.pdf", "01_regulasi/PP_44_2015_Lampiran_1.pdf"], "2015-06-30", "PP 44/2015 JKK dan JKM", "background"),
    ("PP-45-2015", ["01_regulasi/PP_45_2015_JP.pdf"], "2015-06-30", "PP 45/2015 Jaminan Pensiun", "background"),
    ("PP-46-2015", ["01_regulasi/PP_46_2015_JHT.pdf"], "2015-06-30", "PP 46/2015 Jaminan Hari Tua", "background"),
    ("PP-82-2019", ["01_regulasi/PP_82_2019_JKK_JKM.pdf"], "2019-12-02", "PP 82/2019 perubahan PP 44/2015", "background"),
    ("PERPRES-82-2018", ["01_regulasi/Perpres_82_2018_JKN.pdf"], "2018-09-18", "Perpres 82/2018 Jaminan Kesehatan", "background"),
    ("PERPRES-75-2019", ["01_regulasi/Perpres_75_2019_JKN.pdf"], "2019-10-24", "Perpres 75/2019 perubahan Perpres 82/2018", "background"),
    ("PERPRES-64-2020", ["01_regulasi/Perpres_64_2020_JKN.pdf"], "2020-05-06", "Perpres 64/2020 perubahan kedua Perpres 82/2018", "background"),
    ("PP-55-2022", ["01_regulasi/PP_55_2022.pdf"], "2022-12-20", "PP 55/2022 penyesuaian pengaturan bidang PPh", "background"),
    ("PP-37-2021", ["01_regulasi/PP_37_2021_JKP.pdf"], "2021-02-02", "PP 37/2021 Jaminan Kehilangan Pekerjaan", "background"),
    ("FAQ-PMK-72-2025", ["01_regulasi/FAQ_PMK_72_2025_DJP.pdf"], "2025-11-04", "FAQ DJP PPh 21 DTP sektor pariwisata", "support"),
    ("PP-68-2009", ["01_regulasi/pendukung/PP_68_2009_PPh21_pesangon.pdf"], "2009-11-16", "PP 68/2009 PPh 21 pesangon", "support"),
    ("PERMENAKER-6-2016", ["01_regulasi/pendukung/Permenaker_6_2016_THR.pdf"], "2016-03-08", "Permenaker 6/2016 THR", "support"),
    ("PP-35-2021", ["01_regulasi/pendukung/PP_35_2021_PKWT_PHK.pdf"], "2021-02-02", "PP 35/2021 PKWT, waktu kerja, PHK", "support"),
    ("PP-36-2021", ["01_regulasi/pendukung/PP_36_2021_pengupahan.pdf"], "2021-02-02", "PP 36/2021 Pengupahan", "support"),
    ("UU-13-2003", ["01_regulasi/pendukung/UU_13_2003_ketenagakerjaan.pdf"], "2003-03-25", "UU 13/2003 Ketenagakerjaan", "support"),
]
POLICIES = [
    ("PKB-WIKA-2025", "10_kebijakan_perusahaan/dokumen/PKB_WIKA_2025_2026.pdf", "2025-03-01", "PKB PT Wijaya Karya 2025-2026", "policy"),
    ("PKB-CENTEX-2024", "10_kebijakan_perusahaan/dokumen/PKB_Century_Textile_2024_2026.html", "2024-03-27", "PKB PT Century Textile Industry 2024-2026", "policy"),
    ("PKB-AVCO-2024", "10_kebijakan_perusahaan/dokumen/PKB_AVCO_2024_2026.pdf", "2024-04-01", "PKB PT Airfast Aviation Facilities 2024-2026", "policy"),
    ("PKB-TAEKWANG-2024", "10_kebijakan_perusahaan/dokumen/PKB_Taekwang_2024_2026.html", "2024-01-01", "PKB PT TKG Taekwang Indonesia 2024-2026", "policy"),
    ("PKB-SANSAN-2021", "10_kebijakan_perusahaan/dokumen/PKB_Sansan_2021_2024.html", "2021-01-01", "PKB PT Sansan Saudaratex Jaya 2021-2024", "policy"),
    ("PKB-KOJA-2012", "10_kebijakan_perusahaan/dokumen/PKB_TPK_Koja_2012_2014.html", "2012-12-28", "PKB Terminal Petikemas Koja 2012-2014", "policy_dev"),
]
OCR = {"PER-16-PJ-2016": "01_regulasi/ocr/PER_16_PJ_2016_ocr.txt", "PP-36-2021": "01_regulasi/ocr/PP_36_2021_pengupahan_ocr.txt"}
LETTERS = {"E01": "BPJSTK-JP-2023", "E05": "BPJSTK-JP-2024", "E08": "BPJSTK-JP-2025", "E12": "BPJSTK-JP-2026"}
EXTRA_FILES = {"P02": ["01_regulasi/PER_2_PJ_2024_Lampiran.pdf"]}


def doc_id(name):
    s = name.upper().replace("PERATURAN BPJS KESEHATAN", "PERBPJSKES")
    s = re.sub(r"[/.\s]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")


def registry_rows():
    rows = []
    with open(DATA / "09_korpus_peristiwa" / "peristiwa.csv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if not r["berkas"]:
                continue
            did = LETTERS.get(r["id"], doc_id(r["dokumen"]))
            role = {"uji": "event", "pengecoh": "distractor", "pengembangan": "dev"}[r["bagian"]]
            files = [r["berkas"]] + EXTRA_FILES.get(r["id"], [])
            rows.append({"id": did, "event": r["id"], "role": role, "issued": r["tanggal_terbit"],
                         "title": f"{r['dokumen']}: {r['judul']}", "files": ";".join(files)})
    for did, files, issued, title, role in BACKGROUND:
        rows.append({"id": did, "event": "", "role": role, "issued": issued, "title": title, "files": ";".join(files)})
    for did, path, issued, title, role in POLICIES:
        rows.append({"id": did, "event": "", "role": role, "issued": issued, "title": title, "files": path})
    with open(DATA / "10_kebijakan_perusahaan" / "sintetis" / "INDEX.csv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            rows.append({"id": r["id"], "event": "", "role": "policy_synthetic", "issued": r["berlaku_mulai"],
                         "title": f"{r['perusahaan']}: {r['jenis_dokumen']}",
                         "files": f"10_kebijakan_perusahaan/sintetis/{r['berkas_md']}"})
    fict = DATA / "09_korpus_peristiwa" / "fiktif"
    with open(fict / "INDEX.csv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            names = sorted(p.name for p in fict.glob(f"{r['id']}*.md"))
            for name in names:
                did = name[:-3].upper()
                rows.append({"id": did, "event": r["id"], "role": "fictive",
                             "issued": r["diundangkan"] or r["ditetapkan"], "title": f"{r['nomor']}: {r['judul']}",
                             "files": f"09_korpus_peristiwa/fiktif/{name}"})
    rows.append({"id": "INPUT-CONVENTION", "event": "", "role": "convention", "issued": "2009-01-01",
                 "title": "Konvensi data masukan kasus (bukan dokumen hukum)", "files": ""})
    return rows


class _Text(HTMLParser):
    SKIP = {"script", "style", "nav", "header", "footer", "noscript"}

    def __init__(self):
        super().__init__()
        self.out, self._skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip += 1
        if tag in ("p", "br", "li", "div", "tr", "h1", "h2", "h3", "h4", "td"):
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.out.append(data)


def extract(row):
    files = [f for f in row["files"].split(";") if f]
    if row["id"] in OCR:
        raw = (DATA / OCR[row["id"]]).read_text(encoding="utf-8")
        raw = re.sub(r"^=+\s*PAGE (\d+)\s*=+$", lambda m: f"=== PDF hlm. {m.group(1)} ===", raw, flags=re.M)
        return re.sub(r"^#.*\n", "", raw, count=1)
    parts, page_offset = [], 0
    for rel in files:
        path = DATA / rel
        if path.suffix.lower() == ".pdf":
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                for i, p in enumerate(pdf.pages, start=1):
                    parts.append(f"=== PDF hlm. {page_offset + i} ===\n{p.extract_text() or ''}")
                page_offset += len(pdf.pages)
        elif path.suffix.lower() in (".html", ".htm"):
            parser = _Text()
            parser.feed(path.read_text(encoding="utf-8", errors="replace"))
            text = re.sub(r"\n\s*\n+", "\n", "".join(parser.out))
            parts.append(f"=== PDF hlm. {page_offset + 1} ===\n{text}")
            page_offset += 1
        else:
            parts.append(f"=== PDF hlm. {page_offset + 1} ===\n{path.read_text(encoding='utf-8')}")
            page_offset += 1
    return "\n".join(parts)


ARTICLE = re.compile(r"^\s*Pasal\s+([0-9]+[A-Z]?|[IVX]+)\s*$")
CLOSING = re.compile(r"^\s*Ditetapkan di\b", re.I)
ANNEX = re.compile(r"^\s*LAMPIRAN\b")


def segment(text):
    segs, cur = [], {"id": "pembuka", "kind": "opening", "heading": "pembuka", "page_start": 1, "lines": []}
    page = 1
    for line in text.splitlines():
        m = re.match(r"^=== PDF hlm\. (\d+) ===$", line)
        if m:
            page = int(m.group(1))
            continue
        new = None
        a = ARTICLE.match(line)
        if a:
            new = {"id": f"Pasal {a.group(1)}", "kind": "article", "heading": line.strip()}
        elif CLOSING.match(line) and cur["kind"] != "closing":
            new = {"id": "penutup", "kind": "closing", "heading": "penutup"}
        elif ANNEX.match(line) and cur["kind"] != "annex":
            new = {"id": f"Lampiran {sum(s['kind'] == 'annex' for s in segs) + 1}", "kind": "annex",
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


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(force=False):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = registry_rows()
    with open(OUT / "dokumen.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, ["id", "event", "role", "issued", "title", "files"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    built = 0
    for row in rows:
        d = OUT / row["id"]
        if row["id"] == "INPUT-CONVENTION" or (d / "teks.txt").exists() and not force:
            continue
        d.mkdir(exist_ok=True)
        text = extract(row)
        (d / "teks.txt").write_text(text, encoding="utf-8")
        (d / "segmen.json").write_text(json.dumps(segment(text), ensure_ascii=False, indent=1), encoding="utf-8")
        lines = [f"{sha(DATA / rel)}  sumber:{rel}" for rel in row["files"].split(";") if rel]
        lines.append(f"{sha(d / 'teks.txt')}  teks.txt")
        (d / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
        built += 1
        print(f"{row['id']:24} {row['role']:16} {len(text):>8} chars")
    print(f"{built} documents built, {len(rows)} in registry")


if __name__ == "__main__":
    main("--force" in sys.argv)
