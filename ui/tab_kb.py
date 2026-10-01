"""Tab Knowledge Base: menunjukkan pengetahuan yang tersedia di KB, disusun per tahap perhitungan agar mudah dipahami.

Penjelasan berbahasa biasa ditulis di sini; NILAI yang berlaku, aturan, dan pasal dibaca langsung dari KB.
"""
from datetime import date

import pandas as pd
import streamlit as st

from engine.audit import metadata_audit
from engine.kalkulator import kb_aktif
from engine.kb import parameter_pada
from ui import data as D
from ui.hasil import tinggi

ALUR = ["Data HR pegawai", "Kebijakan perusahaan", "Komponen gaji", "Aturan pajak pemerintah", "PPh 21 & slip gaji"]

TOPIK_REGULASI = [
    {"judul": "PTKP: penghasilan tidak kena pajak", "awalan": ["REG-PTKP-"], "nilai": "ptkp",
     "teks": "Bagian penghasilan setahun yang tidak dikenai pajak, menurut status kawin dan jumlah tanggungan pada awal tahun pajak. "
             "Status PTKP juga menentukan kategori tarif TER (A, B, atau C)."},
    {"judul": "Penghasilan bruto & jenis komponen", "awalan": ["R24-03", "R16-01", "REG-NAT-"], "nilai": "klasifikasi",
     "teks": "Semua penghasilan dijumlahkan menjadi bruto, termasuk premi JKK, JKM, dan BPJS Kesehatan yang dibayar perusahaan. "
             "Regulasi menetapkan jenis setiap komponen (teratur, tidak teratur, bukan objek); kebijakan perusahaan tidak boleh "
             "menyimpang dari klasifikasi wajib ini."},
    {"judul": "Biaya jabatan", "awalan": ["REG-BJ-", "R16-02a"], "nilai": "bj",
     "teks": "Pengurang otomatis 5% dari bruto, paling banyak Rp500.000 sebulan atau Rp6.000.000 setahun."},
    {"judul": "Iuran pensiun/JHT/JP & zakat", "awalan": ["REG-PENG-", "R24-PENG-", "R16-02b", "R16-02c", "R16-PENG-"],
     "teks": "Iuran pensiun, JHT, dan JP yang dibayar pegawai, serta zakat yang dibayar lewat pemberi kerja, mengurangi penghasilan bruto. "
             "Iuran BPJS Kesehatan pegawai tidak menjadi pengurang."},
    {"judul": "Penghasilan kena pajak (PKP)", "awalan": ["REG-PKP-", "REG-MT-04", "REG-MT-NETO", "REG-MT-BRUTO", "REG-SUB-"],
     "nilai": "pembulatan_pkp",
     "teks": "PKP = neto setahun - PTKP, dibulatkan ke bawah ke ribuan rupiah. Pegawai yang menjadi subjek pajak hanya sebagian tahun "
             "(mis. WNA baru datang) penghasilannya disetahunkan dulu."},
    {"judul": "Tarif Pasal 17 (progresif)", "awalan": ["REG-P17-"], "nilai": "p17",
     "teks": "PPh setahun dihitung per lapisan PKP dengan tarif bertingkat. Versi tarif dipilih menurut tahun pajak (UU HPP berlaku 2022)."},
    {"judul": "Tarif efektif rata-rata (TER) bulanan", "awalan": ["R24-01", "R24-02"], "nilai": "ter",
     "teks": "Sejak 2024, PPh Januari-November = tarif TER x bruto bulan itu. Tarif dicari di tabel menurut kategori (dari status PTKP) "
             "dan besarnya bruto."},
    {"judul": "Masa pajak terakhir", "awalan": ["REG-MT-0", "REG-MT-LB", "R24-MT-", "R16-MT-"],
     "teks": "Di Desember (atau bulan terakhir bekerja) PPh dihitung ulang setahun dengan tarif Pasal 17, lalu dikurangi yang sudah "
             "dipotong. Hasilnya bisa kurang bayar atau lebih bayar yang dikembalikan ke pegawai."},
    {"judul": "Metode lama PER-16 (sampai 2023)", "awalan": ["R16-0", "R16-BJLN", "R16-NPWP", "R16-05N"],
     "teks": "Sebelum TER: penghasilan sebulan disetahunkan, PPh setahun dihitung dengan Pasal 17, lalu dibagi 12. Penghasilan tidak "
             "teratur (bonus, THR) dihitung dengan selisih PPh dengan dan tanpa komponen itu. Tanpa NPWP: lebih tinggi 20%."},
    {"judul": "Gross-up & PPh ditanggung pemberi kerja", "awalan": ["R24-GU", "R24-05"],
     "teks": "Perusahaan memberi tunjangan pajak sebesar PPh-nya. Karena tunjangan menambah bruto, besarnya diselesaikan sebagai titik "
             "tetap T = PPh(bruto + T). Bila ada lebih dari satu jawaban sah, kalkulator memberi peringatan."},
    {"judul": "PPh 21 ditanggung pemerintah (DTP)", "awalan": ["DTP-"], "nilai": "dtp",
     "teks": "Tahun 2025-2026, PPh 21 pegawai di sektor tertentu (menurut KLU pemberi kerja) dengan penghasilan tetap teratur "
             "paling banyak Rp10 juta sebulan ditanggung pemerintah dan dibayarkan tunai ke pegawai."},
    {"judul": "Tarif & batas upah BPJS", "awalan": [], "nilai": "bpjs",
     "teks": "Tarif iuran BPJS Ketenagakerjaan dan Kesehatan serta batas atas upahnya ditetapkan pemerintah. Batas upah JP berubah setiap "
             "1 Maret. Nilai ini dipakai oleh kebijakan perusahaan untuk menghitung premi dan iuran."},
]

TOPIK_PERUSAHAAN = [
    {"judul": "Gaji & prorata kehadiran", "awalan": ["PX-GAJI-", "PX-NAIK-"],
     "teks": "Gaji = gaji pokok x hari hadir / hari kerja bulan itu. Bila gaji naik di tengah bulan, bulan itu dipecah: hari sebelum "
             "kenaikan memakai gaji lama, sesudahnya gaji baru."},
    {"judul": "Tunjangan tetap & prorata", "awalan": ["PX-TUNJ-"],
     "teks": "Tunjangan tetap dibayar penuh; tunjangan prorata mengikuti kehadiran. Nilainya bisa berbeda sebelum dan sesudah kenaikan gaji."},
    {"judul": "BPJS", "awalan": ["PX-BPJS-"],
     "teks": "Premi (dibayar perusahaan) dan iuran (dipotong dari pegawai) dihitung dari gaji pokok sejak bulan terdaftar, memakai tarif "
             "dan batas upah dari lapisan regulasi. Iuran BPJS Kesehatan tidak dibayar di bulan pegawai berhenti."},
    {"judul": "THR", "awalan": ["PX-THR-"],
     "teks": "THR = gaji pokok x hari masa kerja sampai Lebaran / hari setahun (paling banyak 1 bulan gaji). Masuk masa pajak saat terutang: "
             "tanggal dibayar atau Lebaran, mana yang lebih dahulu."},
    {"judul": "Kompensasi, insentif, lembur, komisi", "awalan": ["PX-KOMP-", "PX-OTA-", "PX-LEMBUR-", "PX-KOMISI-"],
     "teks": "Kompensasi = persen x gaji pokok x masa kerja (maks. 12 bulan) / 12. Insentif OTA, lembur, dan komisi diisi nominalnya per bulan."},
    {"judul": "Take home pay", "awalan": ["PX-THP-"],
     "teks": "Uang yang diterima pegawai = penghasilan tunai - iuran pegawai - PPh 21 dipotong (+ PPh 21 DTP, + tunjangan pajak bila gross-up). "
             "Premi BPJS perusahaan tidak dibayar tunai."},
]


def _aturan(kb, awalan, tahun):
    return [a for a in kb.aturan if any(a.id.startswith(x) for x in awalan) and a.berlaku_di_tahun(tahun)]


def _param(kb, nama, tgl):
    try:
        return parameter_pada(kb, nama, tgl)
    except Exception:  # noqa: BLE001 - parameter belum/tidak berlaku pada tanggal itu
        return None


def _nilai(kb, jenis, tahun):
    if jenis == "ptkp":
        versi = {}
        for r in kb.tabel["ptkp"]:
            versi.setdefault(r["status"], r)
        st.dataframe(pd.DataFrame([{"Status": r["status"], "PTKP setahun": D.rp(r["ptkp_setahun"]), "Kategori TER": r["kategori_ter"],
                                    "Rincian": r["derivasi"]} for r in versi.values()]), hide_index=True, width="stretch",
                     height=tinggi(len(versi)))
    elif jenis == "klasifikasi":
        rows = [{"Komponen": x.jenis.replace("_", " "), "Wajib dikategorikan": x.kategori.replace("_", " "), "Dasar": x.sumber}
                for x in kb.klasifikasi if x.mulai <= date(tahun, 12, 31)]
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=min(tinggi(len(rows)), 320),
                     column_config={"Dasar": st.column_config.TextColumn(width="large")})
    elif jenis == "bj":
        t = date(tahun, 12, 1)
        c = st.columns(3)
        c[0].metric("Persentase", f"{D._desimal(_param(kb, 'bj_persen', t))}%")
        c[1].metric("Maks. sebulan", D.rp(_param(kb, "bj_maks_bulan", t)))
        c[2].metric("Maks. setahun", D.rp(_param(kb, "bj_maks_tahun", t)))
    elif jenis == "pembulatan_pkp":
        e = next(e for e in kb.registri if e.id == "BULAT-PKP-01")
        st.caption(f"Pembulatan: {e.mode} ke kelipatan Rp{e.satuan:,} · {e.dasar}".replace(",", "."))
    elif jenis == "p17":
        rows = [r for r in kb.tabel["tarif_pasal17"] if date.fromisoformat(r["berlaku_mulai"]) <= date(tahun, 12, 31)
                and (not r["berlaku_sampai"] or date.fromisoformat(r["berlaku_sampai"]) >= date(tahun, 1, 1))]
        st.dataframe(pd.DataFrame([{"PKP di atas": D.rp(r["pkp_batas_bawah"]),
                                    "sampai": D.rp(r["pkp_batas_atas"]) if r["pkp_batas_atas"] else "seterusnya",
                                    "Tarif": D.persen(r["tarif_persen"])} for r in rows]), hide_index=True, width="stretch",
                     height=tinggi(len(rows)))
        if rows:
            st.caption(f"{rows[0]['rezim']} · {rows[0]['sumber']}")
    elif jenis == "ter":
        versi = sorted({r["berlaku_mulai"] for r in kb.tabel["ter_bulanan"] if date.fromisoformat(r["berlaku_mulai"]) <= date(tahun, 12, 31)})
        if not versi:
            st.caption(f"Belum berlaku pada {tahun}.")
            return
        kat = st.segmented_control("Kategori", ["A", "B", "C"], default="A", key=f"kb:ter:{tahun}") or "A"
        status = sorted({r["status"] for r in kb.tabel["ptkp"] if r["kategori_ter"] == kat})
        st.caption(f"Kategori {kat}: status PTKP {', '.join(status)} · tabel berlaku mulai {versi[-1]}")
        rows = [r for r in kb.tabel["ter_bulanan"] if r["berlaku_mulai"] == versi[-1] and r["kategori"] == kat]
        st.dataframe(pd.DataFrame([{"Bruto sebulan di atas": D.rp(r["batas_bawah"]),
                                    "sampai": D.rp(r["batas_atas"]) if r["batas_atas"] is not None else "seterusnya",
                                    "Tarif": D.persen(r["tarif_desimal"])} for r in rows]), hide_index=True, width="stretch", height=280)
    elif jenis == "dtp":
        t = date(tahun, 6, 1)
        batas = _param(kb, "dtp_batas_penghasilan_tetap", t)
        klu = [r for r in kb.tabel["klu_dtp"] if r["masa_mulai"][:4] <= str(tahun) <= r["masa_akhir"][:4]]
        c = st.columns(2)
        c[0].metric("Batas penghasilan tetap sebulan", D.rp(batas) if batas else "tidak berlaku")
        c[1].metric(f"Kode KLU penerima {tahun}", len(klu))
        if klu:
            sektor = {}
            for r in klu:
                sektor[(r["sektor"], r["regulasi"])] = sektor.get((r["sektor"], r["regulasi"]), 0) + 1
            st.caption(" · ".join(f"{s.replace('_', ' ')} ({reg}): {n} KLU" for (s, reg), n in sektor.items()))
    elif jenis == "bpjs":
        t = date(tahun, 6, 1)
        item = [("JKM perusahaan", "jkm_pk_persen", "%"), ("JHT perusahaan", "jht_pk_persen", "%"), ("JHT pegawai", "jht_pg_persen", "%"),
                ("JP perusahaan", "jp_pk_persen", "%"), ("JP pegawai", "jp_pg_persen", "%"), ("Kesehatan perusahaan", "kes_pk_persen", "%"),
                ("Kesehatan pegawai", "kes_pg_persen", "%"), ("Batas upah BPJS Kesehatan", "kes_batas_upah", "rp")]
        rows = []
        for lbl, n, s in item:
            v = _param(kb, n, t)
            rows.append({"Komponen": lbl, "Nilai": "-" if v is None else (f"{D._desimal(v)}%" if s == "%" else D.rp(v))})
        for mulai, sampai, v, _ in kb.parameter.get("jp_batas_upah", []):
            if mulai <= date(tahun, 12, 31) and (sampai is None or sampai >= date(tahun, 1, 1)):
                rows.append({"Komponen": (f"Batas upah JP ({mulai:%d-%m-%Y} s.d. {sampai:%d-%m-%Y})" if sampai
                                          else f"Batas upah JP (mulai {mulai:%d-%m-%Y})"), "Nilai": D.rp(v)})
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=tinggi(len(rows)))


def _kartu(kb, t, tahun, lapisan):
    aturan = _aturan(kb, t["awalan"], tahun)
    if t["awalan"] and not aturan:
        return False
    with st.container(border=True):
        lbl = ":blue-badge[Pemerintah · wajib]" if lapisan == "regulasi" else ":orange-badge[Perusahaan X · kebijakan]"
        st.markdown(f"**{t['judul']}**  {lbl}")
        st.markdown(t["teks"])
        if t.get("nilai"):
            _nilai(kb, t["nilai"], tahun)
        sumber = []
        for a in aturan:
            if a.sumber not in sumber:
                sumber.append(a.sumber)
        if sumber:
            with st.expander(f"Dasar & aturan di KB ({len(aturan)} aturan)"):
                st.markdown("\n".join(f"- {s}" for s in sumber[:8]) + ("\n- ..." if len(sumber) > 8 else ""))
                st.dataframe(pd.DataFrame([{"ID": a.id, "Menghasilkan": a.menghasilkan, "Jika": a.jika.teks if a.jika else "",
                                            "Maka": a.maka.teks, "Berlaku": f"{a.mulai} s.d. {a.sampai or 'sekarang'}"} for a in aturan]),
                             hide_index=True, width="stretch", height=min(tinggi(len(aturan)), 320))
    return True


@st.cache_data(show_spinner="Mencocokkan kalkulator dengan 45 contoh resmi...")
def _bukti_v1():
    from eksperimen.v1 import jalankan, ringkas
    from engine.kalkulator import fakta, hitung
    hasil = jalankan(hitung, fakta)
    c, stj = ringkas(hasil)
    return dict(c), stj, len(hasil), len({r["kasus"] for r in hasil})


@st.cache_data(show_spinner="Membandingkan kalkulator dengan dan tanpa KB...")
def _bukti_e12():
    from eksperimen.e12_tanpa_kb import cek_silang, kasus_uji
    return [(n, cek_silang(k)["status"]) for n, k in kasus_uji()]


@st.cache_data(show_spinner=False)
def _katalog():
    from eksperimen.ekspresivitas import jalankan
    return jalankan()


def tampilkan():
    st.markdown("<div class='cerita'><b>Apa yang diketahui kalkulator?</b> Semua aturan pajak pemerintah dan kebijakan perusahaan "
                "disimpan sebagai <b>knowledge base</b>: berkas aturan (YAML) dan tabel (CSV), masing-masing mencatat pasal sumbernya "
                "dan masa berlakunya. Mesin hanya membaca dan menjalankannya.</div>", unsafe_allow_html=True)
    st.markdown("<div class='alur'>" + "<span class='panah'>→</span>".join(
        f"<span class='langkah {'perusahaan' if i == 1 else 'regulasi' if i == 3 else ''}'>{x}</span>" for i, x in enumerate(ALUR))
        + "</div>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 3])
    tahun = c1.selectbox("Aturan yang berlaku pada tahun", [2023, 2024, 2025, 2026], 1, key="kb:tahun")
    kb = kb_aktif([D.BERKAS_PX])
    aktif = [a for a in kb.aturan if a.berlaku_di_tahun(tahun)]
    with c2:
        k = st.columns(4)
        k[0].metric("Aturan pemerintah", sum(1 for a in aktif if a.lapisan == "regulasi"), border=True)
        k[1].metric("Aturan Perusahaan X", sum(1 for a in aktif if a.lapisan == "perusahaan"), border=True)
        k[2].metric("Parameter", len(kb.parameter), border=True)
        k[3].metric("Tabel resmi", len(kb.tabel), border=True, help="PTKP, TER, Pasal 17, KLU DTP; dikunci hash SHA-256")

    t_reg, t_px, t_kat, t_bukti, t_tek = st.tabs([":material/account_balance: Aturan pemerintah", ":material/apartment: Kebijakan Perusahaan X",
                                                 ":material/library_books: Katalog kebijakan lain", ":material/verified: Bukti kebenaran",
                                                 ":material/code: Rincian teknis"])
    with t_reg:
        st.caption(f"Lapisan regulasi · tahun pajak {tahun} · {'rezim TER (PMK 168/2023)' if tahun >= 2024 else 'rezim PER-16/PJ/2016'}")
        kol = st.columns(2)
        n = 0
        for t in TOPIK_REGULASI:
            with kol[n % 2]:
                if _kartu(kb, t, tahun, "regulasi"):
                    n += 1
    with t_px:
        st.caption("Lapisan perusahaan · `kb/perusahaan/perusahaan_x.yaml` (direkonstruksi dari spreadsheet kantor, dianonimkan). "
                   "Aturan perusahaan boleh mengatur cara menghitung gaji, tetapi tidak boleh menimpa aturan wajib pemerintah.")
        kol = st.columns(2)
        for i, t in enumerate(TOPIK_PERUSAHAAN):
            with kol[i % 2]:
                _kartu(kb, t, tahun, "perusahaan")
        st.markdown("##### Jenis komponen menurut perusahaan vs regulasi")
        wajib = {x.jenis: x for x in kb.klasifikasi}
        rows = []
        for c in kb.komponen:
            w = wajib.get(c.jenis)
            status = ("sesuai" if w and w.kategori == c.kategori else
                      f"KONFLIK: regulasi menetapkan {w.kategori.replace('_', ' ')} (aturan regulasi yang dipakai)" if w else
                      "tidak diatur regulasi: kategori perusahaan dipakai")
            rows.append({"Komponen": D.label(c.fakta), "Menurut perusahaan": c.kategori.replace("_", " "), "Status": status})
        st.dataframe(pd.DataFrame(rows).style.apply(
            lambda r: ["background-color: #fdecea" if str(r["Status"]).startswith("KONFLIK") else "" for _ in r], axis=1),
            hide_index=True, width="stretch", height=tinggi(len(rows)))
        st.caption("Pembulatan Perusahaan X: setiap komponen hasil prorata/persentase dibulatkan setengah ke atas (seperti ROUND di Excel).")
    with t_kat:
        st.markdown("Contoh kebijakan perusahaan lain yang umum dipakai, disusun sebagai berkas KB terpisah (`kb/perusahaan/katalog/`). "
                    "Kolom *Status* menunjukkan apakah kebijakan bisa dinyatakan di KB tanpa mengubah kode mesin.")
        rows = _katalog()
        ket = {"native": "bisa, cukup berkas KB (dijalankan & dicek angkanya)", "input": "bisa, cukup isian data pegawai",
               "tidak_bisa": "belum bisa tanpa mengubah mesin"}
        st.dataframe(pd.DataFrame([{"Kebijakan": r["kebijakan"], "Isi": r["nama"], "Status": ket.get(r["status"], r["status"]),
                                    "Keterangan": r["bukti"] if isinstance(r["bukti"], str) else
                                    "; ".join(f"{k_}: {v['aktual']}" for k_, v in r["bukti"].items())} for r in rows]),
                     hide_index=True, width="stretch", height=tinggi(len(rows)),
                     column_config={"Keterangan": st.column_config.TextColumn(width="large")})
    with t_bukti:
        st.markdown("Bagaimana kita tahu isi KB benar? Acuan kebenarannya adalah **contoh perhitungan di lampiran regulasi**, "
                    "bukan kalkulator lain.")
        if st.button("Jalankan verifikasi", icon=":material/play_arrow:", key="kb:verif") or st.session_state.get("kb:sudah_verif"):
            st.session_state["kb:sudah_verif"] = True
            c, stj, n, nk = _bukti_v1()
            k = st.columns(4)
            k[0].metric("Contoh resmi diuji", nk, border=True, help="Lampiran PMK 168/2023, PP 58/2023, PER-16/PJ/2016, PMK 10/72/105/2025")
            k[1].metric("Angka dicocokkan", n, border=True)
            k[2].metric("Cocok", c.get("cocok", 0) + c.get("cocok_terkoreksi", 0) + c.get("cocok_tafsir", 0), border=True)
            k[3].metric("Selisih tak terjelaskan", stj, border=True)
            st.caption(f"Termasuk {c.get('cocok_terkoreksi', 0)} angka yang salah cetak di dokumen resmi (kalkulator cocok dengan nilai "
                       f"koreksinya) dan {c.get('cocok_tafsir', 0)} angka yang bergantung tafsir yang dicatat.")
            e12 = _bukti_e12()
            st.markdown("**Kalkulator dengan KB vs tanpa KB** (mekanisme berbeda, hasil harus sama):")
            st.dataframe(pd.DataFrame([{"Data pegawai": n_, "Hasil": "identik sampai rupiah" if s == "identik" else s} for n_, s in e12]),
                         hide_index=True, width="stretch", height=tinggi(len(e12)))
        else:
            st.caption("Tekan tombol untuk mencocokkan kalkulator dengan semua contoh resmi (beberapa detik).")
    with t_tek:
        meta = metadata_audit(asumsi=[])
        st.caption(f"Versi KB (commit) {meta['versi_kb'][:7]} · kebaruan {meta['tanggal_kebaruan_kb']} · {len(aktif)} aturan aktif {tahun}")
        st.dataframe(pd.DataFrame([{"ID": a.id, "Lapisan": a.lapisan, "Sifat": a.sifat, "Menghasilkan": a.menghasilkan, "Lingkup": a.lingkup,
                                    "Jika": a.jika.teks if a.jika else "", "Maka": a.maka.teks,
                                    "Berlaku": f"{a.mulai} s.d. {a.sampai or 'sekarang'}", "Sumber": a.sumber, "Berkas": a.berkas}
                                   for a in aktif]), hide_index=True, width="stretch", height=460,
                     column_config={"Maka": st.column_config.TextColumn(width="large"), "Sumber": st.column_config.TextColumn(width="large")})
        st.markdown("##### Integritas tabel")
        st.dataframe(pd.DataFrame([{"Tabel": n_, "SHA-256": meta["hash_tabel"].get(n_, "")[:16] + "...",
                                    "Verifikasi": meta["status_verifikasi_tabel"].get(n_, "")} for n_ in kb.tabel]),
                     hide_index=True, width="stretch")
