"""Unduh dokumen korpus tambahan dan catat manifesnya (RENCANA_DATASET.md, D03, D04, D08).

    env\\Scripts\\python dataset\\unduh_dataset.py

- Regulasi resmi (JDIH BPK, JDIH Kemenkeu, pajak.go.id, BPJS) masuk ke 01_regulasi/pengecoh/, pengembangan/, dan
  pendukung/ dan di-commit: peraturan perundang-undangan tidak dilindungi hak cipta (UU 28/2014 Ps. 42).
- Dokumen kebijakan perusahaan masuk ke 10_kebijakan_perusahaan/dokumen/ dan TIDAK di-commit (salinan pihak ketiga
  bertanda hak cipta). Yang di-commit hanya manifes: URL, tanggal akses, ukuran, dan SHA-256.
Berkas yang sudah ada tidak diunduh ulang. Setiap PDF diperiksa: diawali %PDF dan jumlah halaman > 0.
"""
import csv
import hashlib
import sys
import time
from datetime import date
from pathlib import Path

import httpx
import pdfplumber

HERE = Path(__file__).resolve().parent
JK = "https://jdih.kemenkeu.go.id/api/download/"
BPK = "https://peraturan.bpk.go.id/Download/"

REGULASI = {
    "pengecoh": {
        "PMK_1_2026.pdf": JK + "b5f99bff-f689-4e4f-ae3a-7c6a9a4cfe8a/2026pmkeuangan001.pdf",
        "PMK_54_2025.pdf": JK + "454dde57-6a75-40ef-9afe-ff66077074db/2025pmkeuangan054.pdf",
        "PER_12_PJ_2026_materi_DJP.pdf": "https://pajak.go.id/sites/default/files/2026-09/Pelaporan%20SPT%20Dalam%20Rangka%20Pelaksanaan%20Sistem%20Inti%20Administrasi%20Perpajakan%20(PER-12_PJ_%202026%20tentang%20Perubahan%20PER-11_PJ_2025%20%20tentang%20Ketentuan%20Pelaporan%20PPh,%20PPN,%20PPnBM,%20dan%20Bea%20Materai).pdf",
        "PER_3_PJ_2026.pdf": JK + "d1f55ada-c07a-4a58-bb82-4b43e1a9c94d/PER-3_PJ_2026.pdf",
        "PMK_92_2023.pdf": JK + "a3449575-8378-4e4f-8a93-37fd6c92ca73/2023pmkeuangan092.pdf",
        "PP_9_2026.pdf": BPK + "409079/2026pp009.pdf",
        "PP_50_2025.pdf": BPK + "402226/PP%20Nomor%2050%20Tahun%202025.pdf",
        "PerBPJSKes_2_2024.pdf": BPK + "371869/peraturan-bpjs-kesehatan-no-2-tahun-2024.pdf",
        "Permenaker_5_2023.pdf": BPK + "301552/Permenaker%205%20Tahun%202023.pdf",
        "PMK_8_2026.pdf": JK + "d52eebae-f58d-4efb-ab8d-f215f33cb563/2026pmkeuangan008.pdf",
        "PMK_114_2025.pdf": JK + "956c4a77-a4bb-4c97-a4a9-989bc6a98c79/2025pmkeuangan114.pdf",
        "PER_4_PJ_2026.pdf": JK + "81b88742-77a0-4189-843a-649524d15466/PER-4_PJ_2026.pdf",
    },
    "pengembangan": {
        "PMK_162_PMK011_2012.pdf": BPK + "118015/2012%20PMK%20162.pdf",
        "Perpres_111_2013_JKN.pdf": BPK + "68737/Perpres%20111%202013.pdf",
        "PMK_122_PMK010_2015.pdf": BPK + "106550/122~PMK.010~2015Per.pdf",
        "Perpres_19_2016_JKN.pdf": BPK + "29425/Perpres%20Nomor%2019%20Tahun%202016.pdf",
        "PMK_23_PMK03_2020.pdf": BPK + "127801/23_PMK.03_2020.pdf",
        "PMK_44_PMK03_2020.pdf": BPK + "127913/44_PMK.03_2020.pdf",
        "PMK_86_PMK03_2020.pdf": BPK + "132789/86_PMK.03_2020.pdf",
        "PMK_110_PMK03_2020.pdf": BPK + "254838/110_PMK.03_2020.pdf",
        "PMK_9_PMK03_2021.pdf": BPK + "152649/9_PMK.03_2021.pdf",
        "PMK_82_PMK03_2021.pdf": BPK + "165035/82_PMK.03_2021.pdf",
        "PP_49_2020_relaksasi_BPJSTK.pdf": "https://www.bpjsketenagakerjaan.go.id/assets/uploads/peraturan/Salinan_PP_Nomor_49_Tahun_2020.pdf",
        "PMK_149_PMK03_2021.pdf": BPK + "178670/149_PMK.03_2021-compressed.pdf",
        "PMK_3_PMK03_2022.pdf": BPK + "206815/3_PMK.03_2022.pdf",
    },
    # Dirujuk lapisan kebijakan perusahaan (klausul PKB, GT5): pajak pesangon dan hak minimum ketenagakerjaan.
    "pendukung": {
        "PP_68_2009_PPh21_pesangon.pdf": BPK + "36688/PP_No_68_2009.pdf",
        "Permenaker_6_2016_THR.pdf": BPK + "252116/Kemnaker%20No.%206%20Tahun%202016.pdf",
        "PP_35_2021_PKWT_PHK.pdf": BPK + "154582/PP%20Nomor%2035%20Tahun%202021.pdf",
        "PP_36_2021_pengupahan.pdf": BPK + "154587/PP%20Nomor%2036%20Tahun%202021.pdf",
        "PP_51_2023_perubahan_pengupahan.pdf": BPK + "328142/PP%20Nomor%2051%20Tahun%202023.pdf",
        "PP_49_2025_perubahan_kedua_pengupahan.pdf": BPK + "402111/PP%20Nomor%2049%20Tahun%202025.pdf",
        "UU_13_2003_ketenagakerjaan.pdf": BPK + "31128/UU%20Nomor%2013%20Tahun%202003.pdf",
    },
}

W = "https://wageindicator.org/id-id/"
KEBIJAKAN = {
    "PKB_WIKA_2025_2026.pdf": "https://sustainability.wika.co.id/images/komunikasi-publikasi/laporan/laporan-sosial/Perjanjian%20Kerja%20Bersama%20PT.%20Wijaya%20Karya%20(Persero)%20Tbk%202025-2026.pdf",
    "PKB_AVCO_2024_2026.pdf": "https://www.fpe-sbsi.or.id/wp-content/uploads/2024/10/PKB-dan-PHI-AVCO-2024-2026-FINAL.pdf",
    "PKB_Century_Textile_2024_2026.html": W + "bekerja-di-indonesia/perjanjian-kerja-bersama/perjanjian-kerja-bersama-antara-pt-century-textile-industry-dengan-pimpinan-serikat-pekerja-serikat-pekerja-nasional-periode-2024-2026/",
    "PKB_Taekwang_2024_2026.html": W + "bekerja-di-indonesia/perjanjian-kerja-bersama/perjanjian-kerja-bersama-pt-tkg-taekwang-indonesia-dengan-serikat-pekerja-tingkat-perusahaan-sptp-harmoni-serikat-buruh-independent-taekwang-sbit-dan-serikat-pekerja-nasional-spn-pt-tkg-taekwang-indonesia-periode-2024-2026/",
    "PKB_Sansan_2021_2024.html": W + "bekerja-di-indonesia/perjanjian-kerja-bersama/perjanjian-kerja-bersama-antara-pt-sansan-saudaratex-jaya-dengan-serikat-pekerja-buruh-pt-sansan-saudaratex-jaya-periode-2021-2024/",
    "PKB_TPK_Koja_2012_2014.html": W + "ai/bekerja-di-indonesia/perjanjian-kerja-bersama/perjanjian-kerja-bersama-antara-terminal-petikemas-koja-dengan-sp-tpk-koja/",
}
HEADERS = {"User-Agent": "Mozilla/5.0 (research corpus download; pph21 KBS study)"}


def fetch(url, target):
    if target.exists() and target.stat().st_size > 0:
        return "ada"
    r = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=120)
    r.raise_for_status()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(r.content)
    time.sleep(1)
    return "diunduh"


def check(target):
    data = target.read_bytes()
    if target.suffix == ".pdf":
        if not data.startswith(b"%PDF"):
            return "BUKAN PDF", 0
        with pdfplumber.open(target) as pdf:
            pages = len(pdf.pages)
            text = sum(len(p.extract_text() or "") for p in pdf.pages[:3])
        return ("ok" if text else "ok, tanpa lapisan teks (pindaian)"), pages
    return ("ok" if b"<html" in data[:2000].lower() else "BUKAN HTML"), 0


def run(items, manifest):
    rows, failed = [], 0
    for target, url in items:
        try:
            status = fetch(url, target)
            verdict, pages = check(target)
        except (httpx.HTTPError, OSError) as e:
            status, verdict, pages = "gagal", f"{type(e).__name__}: {e}"[:120], 0
            failed += 1
        data = target.read_bytes() if target.exists() else b""
        rows.append({"berkas": target.relative_to(HERE).as_posix(), "url": url, "diakses": date.today().isoformat(),
                     "status": status, "pemeriksaan": verdict, "halaman": pages, "byte": len(data),
                     "sha256": hashlib.sha256(data).hexdigest() if data else ""})
        print(f"{rows[-1]['status']:8} {verdict:34} {target.name}")
    with open(manifest, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, list(rows[0])); w.writeheader(); w.writerows(rows)
    return failed


def main():
    regulasi = [(HERE / "01_regulasi" / group / name, url) for group, files in REGULASI.items() for name, url in files.items()]
    kebijakan = [(HERE / "10_kebijakan_perusahaan" / "dokumen" / name, url) for name, url in KEBIJAKAN.items()]
    failed = run(regulasi, HERE / "01_regulasi" / "manifest_tambahan.csv")
    failed += run(kebijakan, HERE / "10_kebijakan_perusahaan" / "manifest_dokumen.csv")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
