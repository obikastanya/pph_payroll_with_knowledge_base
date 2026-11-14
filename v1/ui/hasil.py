"""Panel kanan kalkulator: slip gaji, perhitungan setahun (gaya 1721-A1), dasar hukum / dasar kode per angka.

Semua angka dibaca dari keluaran mesin (ui/mesin.py); di sini hanya pemformatan dan penyusunan tampilan.
"""
import csv
import io

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ui import data as D
from ui import mesin as M

BIRU = "#2a78d6"
ORANYE = "#eb6834"
TEKS = "#0b0b0b"
TEKS2 = "#52514e"
GRID = "#e8e7e3"
SUMBU = "#c9c8c3"


def tinggi(n):
    """Tinggi st.dataframe agar n baris tampil tanpa scroll."""
    return 36 * (n + 1) + 8


def galat(pesan):
    st.error(pesan, icon=":material/error:")


def _urut(per_masa):
    return sorted(per_masa, key=lambda b: (b is None, b or 0))


def _layout(fig, h=320):
    fig.update_layout(height=h, margin=dict(l=8, r=8, t=40, b=8), plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
                      font=dict(size=15, color=TEKS), separators=",.", barcornerradius=4, bargap=0.3,
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=TEKS2)),
                      hoverlabel=dict(font_size=15, bgcolor="#ffffff", bordercolor=SUMBU, font_color=TEKS))
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=SUMBU, tickformat=",d", tickprefix="Rp", tickfont=dict(color=TEKS2, size=13))
    fig.update_xaxes(showgrid=False, linecolor=SUMBU, tickfont=dict(color=TEKS2, size=14))
    return fig


# ---------------------------------------------------------------------------- banner verifikasi

def banner_cek_silang(mesin, kasus):
    lain = M.NAMA[M.TANPA_KB if mesin == M.KB else M.KB].lower()
    r = M.cek_silang(kasus)
    if r["status"] == "identik":
        st.success(f"**Cek silang:** kalkulator {lain} memberi hasil **identik sampai rupiah** untuk isian ini.",
                   icon=":material/done_all:")
    elif r["status"] == "sah_titik_tetap_ganda":
        st.info(f"**Cek silang:** kalkulator {lain} berbeda di {len(r['selisih'])} angka, tetapi **keduanya sah**: gross-up di sini "
                "punya lebih dari satu tunjangan pajak yang memenuhi persamaan T = PPh(bruto + T) (adjudikasi A-02). "
                "Kalkulator dengan KB memilih yang terkecil.", icon=":material/call_split:")
    elif r["status"] == "berbeda":
        rinci = "; ".join(f"{D.label(f)} {D.NAMA_BULAN.get(b, 'setahun') if b else 'setahun'}: {D.rp(a)} vs {D.rp(c)}"
                          for b, f, a, c in r["selisih"][:4])
        st.warning(f"**Cek silang:** hasil berbeda dari kalkulator {lain} ({rinci}).", icon=":material/warning:")


STATUS_V1 = {"cocok": "cocok", "cocok_terkoreksi": "cocok dengan nilai koreksi (dokumen salah cetak)",
             "cocok_tafsir": "cocok dengan tafsir yang tercatat", "SELISIH": "SELISIH", "TIDAK_DIHASILKAN": "tidak dihasilkan"}


def banner_resmi(mesin, data_id, utuh):
    k = D.muat_kanonik(data_id)
    reg = (k.get("sumber") or {}).get("regulasi", "")
    if not utuh:
        st.caption(f":material/edit_note: Data sudah diubah dari contoh {reg}; pencocokan dengan dokumen tidak berlaku.")
        return
    rows = M.cek_resmi(data_id, mesin)
    ok = sum(1 for r in rows if r["status"].startswith("cocok"))
    if ok == len(rows):
        st.success(f"**{ok} dari {len(rows)} angka** di contoh resmi {reg} cocok sampai rupiah.", icon=":material/verified:")
    else:
        st.error(f"{len(rows) - ok} dari {len(rows)} angka tidak cocok dengan contoh resmi {reg}.", icon=":material/error:")
    with st.expander("Lihat pencocokan dengan dokumen"):
        hrp = {(x["fakta"], x["bulan"]): x for x in k["harapan"]}
        st.dataframe(pd.DataFrame([{
            "Angka": D.label(r["fakta"]), "Masa": "setahun" if r["bulan"] is None else D.NAMA_BULAN.get(r["bulan"]),
            "Di dokumen": D.rp(r["harapan"], False) if isinstance(r["harapan"], int) else D.persen(r["harapan"]) if "/" in str(r["harapan"]) else str(r["harapan"]),
            "Kalkulator": _fmt(r.get("aktual_varian", r["aktual"])), "Status": STATUS_V1.get(r["status"], r["status"]),
            "Catatan": hrp.get((r["fakta"], r["bulan"]), {}).get("erratum", "")} for r in rows]),
            hide_index=True, width="stretch", height=min(tinggi(len(rows)), 420))


def _fmt(v):
    if isinstance(v, bool):
        return "ya" if v else "tidak"
    if isinstance(v, int):
        return D.rp(v, False)
    if isinstance(v, str) and "/" in v:
        return D.persen(v)
    return "-" if v is None else str(v)


# ---------------------------------------------------------------------------- ringkasan

def ringkasan(h, kasus, mode_hr):
    t, pm = h["tahunan"], h["per_masa"]
    kartu = []
    total_pph = sum(m.get("pph21") or 0 for m in pm.values())
    dtp = sum(m.get("pph21_dtp") or 0 for m in pm.values())
    if "pph21_setahun" in t:
        kartu.append(("PPh 21 setahun", D.rp(t["pph21_setahun"]), "PPh 21 terutang satu tahun pajak"))
    else:
        kartu.append(("PPh 21", D.rp(total_pph), "PPh 21 terutang masa ini"))
    if mode_hr:
        kartu.append(("Take home pay setahun", D.rp(sum(m.get("px_thp") or 0 for m in pm.values())),
                      "Total uang diterima pegawai: penghasilan tunai - iuran pegawai - PPh 21 dipotong"))
    bruto = t.get("bruto_setahun")
    if bruto is None:
        bruto = sum(m.get("bruto") or m.get("bruto_total_masa") or 0 for m in pm.values())
    kartu.append(("Penghasilan bruto", D.rp(bruto), "Dasar pengenaan pajak (termasuk premi BPJS yang dibayar perusahaan)"))
    kartu.append(("Tarif efektif", D.rasio_persen(t.get("pph21_setahun", total_pph), bruto), "PPh 21 / penghasilan bruto"))
    if dtp:
        kartu.append(("Ditanggung pemerintah (DTP)", D.rp(dtp), "PPh 21 DTP dibayarkan tunai ke pegawai"))
    for i in range(0, len(kartu), 3):
        kol = st.columns(3)
        for c, (lbl, v, bantu) in zip(kol, kartu[i:i + 3]):
            c.metric(lbl, v, help=bantu, border=True)


# ---------------------------------------------------------------------------- slip gaji

def _baris(uraian, nilai, mesin, h, fakta, bulan, tahun, tanda=""):
    d = M.dasar(mesin, h, fakta, bulan, tahun) if fakta else None
    return {"Uraian": uraian, "Jumlah": (tanda + D.rp(nilai, False)) if isinstance(nilai, int) else (nilai if nilai is not None else "-"),
            "Dasar": d["pendek"] if d else "input admin", "Rincian dasar": d["panjang"] if d else "diisi di panel kiri"}


def _ket_pph(m, b, kasus, h):
    terakhir = (kasus["pegawai"].get("bulan_terakhir_bekerja") or 12) if kasus.get("cakupan") == "setahun" else None
    if m.get("tarif_ter"):
        return f"PPh 21 (TER kategori {m.get('kategori_ter')} {D.persen(m['tarif_ter'])} × bruto)"
    if b == terakhir and "pph21_setahun" in h["tahunan"]:
        return "PPh 21 masa terakhir (PPh setahun - yang sudah dipotong)"
    return "PPh 21"


def slip(mesin, h, kasus, mode_hr):
    pm = h["per_masa"]
    bulan = _urut(pm)
    tahun = kasus["tahun_pajak"]
    c1, c2 = st.columns([1, 3])
    i = c1.selectbox("Slip bulan", list(range(len(bulan))), len(bulan) - 1, key=f"{mesin}:slip:{kasus.get('id')}:{bulan}",
                     format_func=lambda j: D.NAMA_BULAN.get(bulan[j], "Masa"))
    b = bulan[i]
    m = pm[b]
    rows = []
    if mode_hr:
        per = kasus["data_hr"]["per_masa"].get(str(b), {})
        hadir = f" ({per.get('hk_aktual')}/{per.get('hk_penuh')} hari kerja)" if per.get("hk_aktual") != per.get("hk_penuh") else ""
        rows.append({"Uraian": "PENGHASILAN", "Jumlah": "", "Dasar": "", "Rincian dasar": ""})
        rows.append(_baris(f"Gaji{hadir}", m.get("px_gaji"), mesin, h, "px_gaji", b, tahun))
        for f, lbl in (("px_tunjangan", "Tunjangan"), ("px_thr", "THR"), ("px_kompensasi", "Kompensasi"), ("px_ota", "Insentif OTA"),
                       ("px_lembur", "Lembur"), ("px_komisi", "Komisi"), ("tunjangan_pajak", "Tunjangan pajak (gross-up)")):
            if m.get(f):
                rows.append(_baris(lbl, m[f], mesin, h, f, b, tahun))
        rows.append({"Uraian": "DITANGGUNG PERUSAHAAN (menambah bruto, tidak dibayar tunai)", "Jumlah": "", "Dasar": "", "Rincian dasar": ""})
        for f, lbl in (("px_premi_jkk", "Premi JKK"), ("px_premi_jkm", "Premi JKM"), ("px_premi_kes", "Premi BPJS Kesehatan")):
            rows.append(_baris(lbl, m.get(f), mesin, h, f, b, tahun))
    else:
        rows.append({"Uraian": "KOMPONEN GAJI", "Jumlah": "", "Dasar": "", "Rincian dasar": ""})
        for mm in kasus["masa"]:
            if mm["bulan"] == b:
                for c in mm["komponen"]:
                    nilai = c.get("nominal")
                    if nilai is None and "valas" in c:
                        nilai = f"{c['valas']['jumlah']} {c['valas']['mata_uang']}"
                    rows.append({"Uraian": D.label_komponen(c["kode"]),
                                 "Jumlah": D.rp(nilai, False) if isinstance(nilai, int) else nilai, "Dasar": "input admin",
                                 "Rincian dasar": f"dikenai pajak sebagai {D.LABEL_KATEGORI_PAJAK.get(c['kategori'], c['kategori'])}"})
    bruto_f = "bruto_total_masa" if "bruto_total_masa" in m else "bruto"
    rows.append(_baris("Penghasilan bruto (dasar pajak)", m.get(bruto_f), mesin, h, bruto_f, b, tahun))
    rows.append({"Uraian": "POTONGAN", "Jumlah": "", "Dasar": "", "Rincian dasar": ""})
    if mode_hr:
        for f, lbl in (("px_iuran_jht_pg", "Iuran JHT pegawai"), ("px_iuran_jp_pg", "Iuran JP pegawai"),
                       ("px_iuran_kes_pg", "Iuran BPJS Kesehatan pegawai")):
            rows.append(_baris(lbl, m.get(f), mesin, h, f, b, tahun, "-"))
    rows.append(_baris(_ket_pph(m, b, kasus, h), m.get("pph21"), mesin, h, "pph21", b, tahun, "-" if (m.get("pph21") or 0) >= 0 else ""))
    if m.get("pph21_dtp"):
        rows.append(_baris("PPh 21 ditanggung pemerintah (dibayar tunai)", m["pph21_dtp"], mesin, h, "pph21_dtp", b, tahun, "+"))
    if mode_hr:
        rows.append(_baris("TAKE HOME PAY", m.get("px_thp"), mesin, h, "px_thp", b, tahun))
    df = pd.DataFrame(rows)
    tebal = {"PENGHASILAN", "POTONGAN", "KOMPONEN GAJI", "TAKE HOME PAY", "DITANGGUNG PERUSAHAAN (menambah bruto, tidak dibayar tunai)",
             "Penghasilan bruto (dasar pajak)"}
    gaya = df.style.apply(lambda r: ["font-weight: 700; background-color: #f4f4f2" if r["Uraian"] in tebal else "" for _ in r], axis=1)
    c2.caption("Kolom **Dasar** menunjukkan dari mana angka berasal: "
               + ("aturan di knowledge base (lapisan + ID aturan); arahkan kursor ke *Rincian dasar* untuk pasal."
                  if mesin == M.KB else "fungsi di kode Python yang menghitungnya (aturan ditanam di kode)."))
    st.dataframe(gaya, hide_index=True, width="stretch", height=tinggi(len(rows)),
                 column_config={"Uraian": st.column_config.TextColumn(width="large"), "Jumlah": st.column_config.TextColumn(width="medium"),
                                "Dasar": st.column_config.TextColumn(width="medium"),
                                "Rincian dasar": st.column_config.TextColumn(width="large")})


# ---------------------------------------------------------------------------- perhitungan setahun

def setahun(mesin, h, kasus):
    t = h["tahunan"]
    tahun = kasus["tahun_pajak"]
    if "pph21_setahun" not in t:
        st.caption("Perhitungan satu masa pajak; tidak ada perhitungan setahun.")
        _rincian_masa(mesin, h, kasus)
        return
    rows = []
    tambah = lambda lbl, f, tanda="": rows.append(_baris(lbl, t.get(f), mesin, h, f, None, tahun, tanda)) if f in t else None
    tambah("Penghasilan bruto setahun", "bruto_setahun")
    tambah("Biaya jabatan (5%, maks. Rp500.000 sebulan)", "biaya_jabatan", "-")
    tambah("Iuran pensiun/JHT/JP pegawai", "iuran_pengurang", "-")
    if t.get("zakat"):
        tambah("Zakat / sumbangan keagamaan wajib", "zakat", "-")
    tambah("Penghasilan neto", "neto_setahun")
    if t.get("neto_disetahunkan") not in (None, t.get("neto_setahun")):
        tambah("Penghasilan neto disetahunkan", "neto_disetahunkan")
    tambah(f"PTKP ({t.get('status_ptkp_efektif', kasus['pegawai']['status_ptkp'])})", "ptkp", "-")
    tambah("Penghasilan kena pajak (dibulatkan ke bawah ribuan)", "pkp")
    rinci = h.get("rincian_p17")
    if rinci:
        for l in rinci["lapisan"]:
            atas = "∞" if l["atas"] is None else D.rp(l["atas"], False)
            rows.append({"Uraian": f"   Pasal 17: {D.persen(l['tarif'])} × {D.rp(l['dasar'], False)}  (lapisan {D.rp(l['bawah'], False)} - {atas})",
                         "Jumlah": D.rp(l["pajak"], False) if isinstance(l["pajak"], int) else str(l["pajak"]),
                         "Dasar": (M.dasar(mesin, h, "pph21_disetahunkan" if "pph21_disetahunkan" in t else "pph21_setahun", None, tahun) or {}).get("pendek", ""),
                         "Rincian dasar": "UU PPh Ps. 17(1)a (tarif progresif per lapisan)"})
    if "pph21_disetahunkan" in t:
        tambah("PPh 21 atas penghasilan disetahunkan", "pph21_disetahunkan")
    tambah("PPh 21 terutang setahun", "pph21_setahun")
    tambah("Sudah dipotong masa sebelumnya", "pph21_dipotong_sebelumnya", "-")
    tambah("PPh 21 masa pajak terakhir (negatif = lebih bayar)", "pph21_masa_terakhir")
    if t.get("lebih_bayar_dikembalikan"):
        tambah("Lebih bayar dikembalikan ke pegawai", "lebih_bayar_dikembalikan")
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=tinggi(len(rows)),
                 column_config={"Uraian": st.column_config.TextColumn(width="large"), "Jumlah": st.column_config.TextColumn(width="medium"),
                                "Dasar": st.column_config.TextColumn(width="medium"),
                                "Rincian dasar": st.column_config.TextColumn(width="large")})


def _rincian_masa(mesin, h, kasus):
    rows = []
    for b in _urut(h["per_masa"]):
        for f, v in h["per_masa"][b].items():
            if isinstance(v, (int, str)) and not isinstance(v, bool):
                rows.append({**_baris(D.label(f), v if isinstance(v, int) else _fmt(v), mesin, h, f, b, kasus["tahun_pajak"]),
                             "Masa": D.NAMA_BULAN.get(b, "Masa")})
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=min(tinggi(len(rows)), 480))


# ---------------------------------------------------------------------------- tabel & grafik 12 bulan

def tabel_bulanan(h, mode_hr):
    pm = h["per_masa"]
    rows = []
    for b in _urut(pm):
        m = pm[b]
        r = {"Bulan": D.NAMA_BULAN.get(b, "Masa"), "Bruto": D.rp(m.get("bruto_total_masa", m.get("bruto")), False),
             "TER": f"{m.get('kategori_ter', '')} {D.persen(m.get('tarif_ter'))}".strip() if m.get("tarif_ter") else "-",
             "PPh 21": D.rp(m.get("pph21"), False)}
        if any(x.get("pph21_dtp") for x in pm.values()):
            r["DTP"] = D.rp(m.get("pph21_dtp") or 0, False)
        if any(x.get("tunjangan_pajak") for x in pm.values()):
            r["Tunjangan pajak"] = D.rp(m.get("tunjangan_pajak") or 0, False)
        if mode_hr:
            r["Take home pay"] = D.rp(m.get("px_thp"), False)
        rows.append(r)
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=tinggi(len(rows)))


def grafik(h, mesin):
    pm = h["per_masa"]
    bulan = _urut(pm)
    if len(bulan) < 2:
        return
    x = [D.NAMA_BULAN.get(b) for b in bulan]
    fig = go.Figure()
    fig.add_bar(x=x, y=[pm[b].get("pph21") or 0 for b in bulan], name="PPh 21", marker_color=BIRU,
                hovertemplate="%{x}: Rp%{y:,d}<extra>PPh 21</extra>")
    if any(pm[b].get("pph21_dtp") for b in bulan):
        fig.add_bar(x=x, y=[pm[b].get("pph21_dtp") or 0 for b in bulan], name="Ditanggung pemerintah", marker_color=ORANYE,
                    hovertemplate="%{x}: Rp%{y:,d}<extra>DTP</extra>")
    else:
        fig.update_layout(showlegend=False)
    fig.update_layout(title=dict(text="PPh 21 per bulan", font=dict(size=17, color=TEKS), x=0, y=0.98))
    st.plotly_chart(_layout(fig), config={"displayModeBar": False}, key=f"{mesin}:grafik")


# ---------------------------------------------------------------------------- peringatan & mekanisme

def _kategori(k):
    return (k or "?").replace("_", " ")


def _daftar(x):
    return ", ".join(x) if isinstance(x, (list, tuple)) else str(x or "?")


def teks_peringatan(p):
    """Satu peringatan engine -> (teks markdown, jenis: konflik|grossup|info), atau None bila diringkas terpisah.

    KONFLIK_WAJIB punya dua bentuk: tingkat klasifikasi (kategori_perusahaan/kategori_wajib, dari kategori_efektif)
    dan tingkat aturan (ditolak/pemenang, dari resolusi lex superior); kunci opsional dibaca aman."""
    kode = p.get("kode")
    if kode == "KONFLIK_WAJIB":
        if "kategori_wajib" in p or "kategori_perusahaan" in p:
            teks = (f"**Konflik kebijakan perusahaan dengan aturan wajib:** komponen `{p.get('fakta')}` ({p.get('jenis') or '-'}) "
                    f"dikategorikan perusahaan sebagai *{_kategori(p.get('kategori_perusahaan'))}*, padahal regulasi menetapkan "
                    f"*{_kategori(p.get('kategori_wajib'))}* ({p.get('sumber') or ''}). Kalkulator memakai aturan regulasi.")
        else:
            teks = (f"**Konflik kebijakan perusahaan dengan aturan wajib:** aturan {_daftar(p.get('ditolak'))} untuk "
                    f"{D.label(p.get('fakta') or '?')} tidak dipakai karena aturan wajib {_daftar(p.get('pemenang'))} berlaku.")
        return teks, "konflik"
    if kode == "GROSSUP_GANDA":
        terkecil, terbesar = p.get("terkecil"), p.get("terbesar")
        teks = (f"**Gross-up punya dua jawaban sah** ({D.NAMA_BULAN.get(p.get('bulan'), 'masa terakhir')}): tunjangan pajak "
                f"{D.rp(terkecil) if terkecil is not None else '-'} atau {D.rp(terbesar) if terbesar is not None else '-'}; "
                f"dipakai yang {p.get('dipilih') or 'terkecil'}.")
        return teks, "grossup"
    if kode == "KLASIFIKASI_TIDAK_DIATUR":
        return None
    return f"**{kode}**: {p}", "info"


def peringatan(mesin, h):
    if mesin == M.TANPA_KB:
        st.caption(":material/info: Kalkulator tanpa KB tidak memeriksa konflik kebijakan: aturan langsung ditulis di kode, "
                   "jadi kesalahan kebijakan hanya bisa ditemukan dengan membaca kode.")
        return
    tampil = set()
    for p in h.get("peringatan") or []:
        hasil = teks_peringatan(p)
        if hasil is None:
            continue
        teks, jenis = hasil
        if teks not in tampil:
            tampil.add(teks)
            if jenis == "konflik":
                st.warning(teks, icon=":material/gavel:")
            else:
                st.info(teks, icon=":material/call_split:" if jenis == "grossup" else ":material/info:")
    tidak_diatur = sorted({f"{D.label(p.get('fakta') or '?')} ({_kategori(p.get('kategori_perusahaan'))})"
                           for p in h.get("peringatan") or [] if p.get("kode") == "KLASIFIKASI_TIDAK_DIATUR"})
    if tidak_diatur:
        st.info("**Klasifikasi mengikuti kebijakan perusahaan** karena regulasi tidak mengaturnya secara tegas: " + ", ".join(tidak_diatur),
                icon=":material/info:")


def mekanisme(mesin, h, kasus):
    if mesin == M.KB:
        jejak = h["jejak"] or []
        lap = {"regulasi": 0, "perusahaan": 0}
        for a in {(j["aturan"], j["lapisan"]) for j in jejak}:
            lap[a[1]] = lap.get(a[1], 0) + 1
        st.markdown(f"Mesin inferensi membaca **{lap['regulasi']} aturan regulasi** dan **{lap['perusahaan']} aturan Perusahaan X** "
                    "dari berkas YAML, menyusun urutan hitung dari ketergantungan antar-angka, lalu mengevaluasinya (forward chaining). "
                    "Mengganti aturan = mengubah berkas KB; kode mesin tidak berubah.")
        st.dataframe(pd.DataFrame([{"Angka": D.label(j["fakta"]), "Masa": "setahun" if j["bulan"] is None else D.NAMA_BULAN.get(j["bulan"]),
                                    "Nilai": _fmt(j["nilai"]), "Aturan": j["aturan"],
                                    "Lapisan": "Perusahaan X" if j["lapisan"] == "perusahaan" else "Regulasi",
                                    "Dasar hukum / kebijakan": j["sumber"],
                                    "Aturan yang ditolak": ", ".join(j["ditolak"]) + (f" ({', '.join(j['alasan'])})" if j["ditolak"] else "")}
                                   for j in jejak if not j["fakta"].startswith("_")]),
                     hide_index=True, width="stretch", height=420, column_config={"Dasar hukum / kebijakan": st.column_config.TextColumn(width="large")})
        return
    st.markdown("Aturan pajak dan kebijakan perusahaan **ditanam langsung di kode Python** (konstanta dan rumus di dalam fungsi). "
                "Mengganti aturan, misalnya batas upah JP atau tarif, berarti **mengubah dan menguji ulang kode ini**.")
    fungsi = []
    for f in list(h["per_masa"][_urut(h["per_masa"])[0]]) + list(h["tahunan"]):
        d = M.dasar(mesin, h, f, None, kasus["tahun_pajak"])
        if d and d["fungsi"] not in fungsi:
            fungsi.append(d["fungsi"])
    pilih = st.selectbox("Lihat kode fungsi", fungsi, format_func=lambda x: f"{x[1]}()  ·  {M.kode_sumber(*x)['berkas']}",
                         key=f"{mesin}:kode")
    info = M.kode_sumber(*pilih)
    st.caption(f"{info['berkas']}, baris {info['awal']}-{info['akhir']}")
    st.code(info["kode"], language="python", line_numbers=True)


def csv_hasil(h):
    buf = io.StringIO()
    kol = ["bulan", "bruto", "kategori_ter", "tarif_ter", "pph21", "pph21_dtp", "tunjangan_pajak", "px_thp"]
    w = csv.writer(buf)
    w.writerow(kol)
    for b in _urut(h["per_masa"]):
        m = h["per_masa"][b]
        w.writerow(["" if b is None else b] + [m.get(k, "") for k in kol[1:]])
    return buf.getvalue()


# ---------------------------------------------------------------------------- panel

def panel(mesin, kasus, info, data_id, utuh):
    h, err = M.hitung(kasus, mesin)
    if err:
        galat(err)
        return
    mode_hr = bool(kasus.get("data_hr"))
    banner_cek_silang(mesin, kasus)
    if info["resmi"]:
        banner_resmi(mesin, data_id, utuh)
    ringkasan(h, kasus, mode_hr)
    t1, t2, t3, t4 = st.tabs([":material/receipt_long: Slip gaji", ":material/functions: Perhitungan setahun",
                              ":material/table_chart: 12 bulan", ":material/settings_suggest: Cara mesin menghitung"])
    with t1:
        slip(mesin, h, kasus, mode_hr)
    with t2:
        setahun(mesin, h, kasus)
    with t3:
        grafik(h, mesin)
        tabel_bulanan(h, mode_hr)
    with t4:
        mekanisme(mesin, h, kasus)
    peringatan(mesin, h)
    st.download_button("Unduh hasil per bulan (CSV)", csv_hasil(h), file_name=f"hasil_{kasus.get('id', 'pegawai')}_{mesin}.csv",
                       mime="text/csv", key=f"{mesin}:unduh", icon=":material/download:")
