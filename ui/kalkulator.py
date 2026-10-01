"""Tab Kalkulator: panel kiri isian admin finance (default dari dataset), panel kanan hasil mesin.

Dipakai dua kali: sub-tab "Dengan KB" (mesin=kb) dan "Tanpa KB" (mesin=tanpa_kb). Isian setiap sub-tab berdiri sendiri.
Tidak ada konfigurasi sistem di sini (tafsir, versi KB, berkas kebijakan, kategori pajak): hanya data pegawai.
Edit hanya tersimpan di sesi browser; berkas dataset tidak pernah ditulis.
"""
import copy
from datetime import date

import pandas as pd
import streamlit as st

from ui import data as D
from ui import hasil as H

TANGGAL_HR = ("kenaikan_tanggal", "tanggal_lebaran", "tanggal_thr_bayar")


def _S(mesin):
    return st.session_state.setdefault(f"K:{mesin}", {})


def muat_ke_state(mesin, data_id):
    S = _S(mesin)
    kasus = D.muat_data(data_id)
    S.update(data_id=data_id, dasar=kasus, gen=S.get("gen", 0) + 1, ver=0)
    if not kasus.get("data_hr"):
        baris, bulan, khusus = D.kasus_ke_tabel(kasus)
        S.update(baris=baris, cur=copy.deepcopy(baris), bulan=bulan, khusus=khusus)


def _cb_data(mesin, key):
    muat_ke_state(mesin, st.session_state[key])


def _cb_reset(mesin):
    muat_ke_state(mesin, _S(mesin)["data_id"])


# ============================================================================ mode Data HR (Perusahaan X)

def _cb_tahun_hr(mesin, g):
    """Tahun pajak berubah -> tanggal kebijakan bertahun lama ikut digeser (tanggal masuk tidak)."""
    baru = st.session_state[f"{mesin}:{g}:tahun"]
    for f in TANGGAL_HR:
        k = f"{mesin}:{g}:{f}"
        v = st.session_state.get(k)
        if isinstance(v, date):
            hari = v.day
            while True:
                try:
                    st.session_state[k] = v.replace(year=baru, day=hari)
                    break
                except ValueError:
                    hari -= 1


def form_hr(mesin, S):
    g, dasar = S["gen"], S["dasar"]
    hr, p = dasar["data_hr"], dasar["pegawai"]
    k = lambda nama: f"{mesin}:{g}:{nama}"
    for f in TANGGAL_HR:
        st.session_state.setdefault(k(f), date.fromisoformat(hr[f]))
    tahun_opsi = [2023, 2024, 2025, 2026]
    with st.container(border=True):
        st.markdown("##### :material/badge: Pegawai")
        c1, c2, c3 = st.columns(3)
        tahun = c1.selectbox("Tahun pajak", tahun_opsi, tahun_opsi.index(dasar["tahun_pajak"]), key=k("tahun"),
                             on_change=_cb_tahun_hr, args=(mesin, g))
        status = c2.selectbox("Status PTKP", D.STATUS_PTKP, D.STATUS_PTKP.index(p["status_ptkp"]), key=k("ptkp"),
                              help="Status per 1 Januari tahun pajak")
        npwp = c3.toggle("Punya NPWP/NIK valid", p.get("punya_npwp", True), key=k("npwp"))
        c1, c2, c3 = st.columns(3)
        masuk = c1.date_input("Tanggal masuk kerja", date.fromisoformat(hr["tanggal_masuk"]), key=k("masuk"), format="DD/MM/YYYY")
        opsi_keluar = [None] + list(range(1, 13))
        keluar = c2.selectbox("Berhenti bekerja (bulan)", opsi_keluar, opsi_keluar.index(p.get("bulan_terakhir_bekerja")),
                              key=k("keluar"), format_func=lambda b: "masih bekerja" if b is None else D.NAMA_BULAN[b])
        metode = c3.selectbox("Metode pajak", list(D.METODE), list(D.METODE).index(dasar["metode"]), key=k("metode"),
                              format_func=D.METODE.get)
    with st.container(border=True):
        st.markdown("##### :material/payments: Gaji & tunjangan")
        c1, c2 = st.columns(2)
        gaji = c1.number_input(f"Gaji pokok sebulan · **{D.rp(st.session_state.get(k('gaji'), hr['gaji_pokok']))}**", 0, None,
                               hr["gaji_pokok"], step=100000, key=k("gaji"))
        naik = c2.number_input(f"Kenaikan gaji · **{D.rp(st.session_state.get(k('naik'), hr['kenaikan_nominal']))}**", 0, None,
                               hr["kenaikan_nominal"], step=100000, key=k("naik"))
        c1, c2, c3 = st.columns(3)
        naik_tgl = c1.date_input("Berlaku mulai", key=k("kenaikan_tanggal"), format="DD/MM/YYYY")
        hk_sbl = c2.number_input("Hari kerja sebelum naik", 0, 31, hr["kenaikan_hk_sebelum"], key=k("hksbl"),
                                 help="Hari kerja aktual di bulan kenaikan, sebelum tanggal berlaku (bila kenaikan di tengah bulan)")
        hk_ssd = c3.number_input("Hari kerja sesudah naik", 0, 31, hr["kenaikan_hk_sesudah"], key=k("hkssd"))
        st.caption("Tunjangan sebelum / sesudah kenaikan gaji. *Tetap* dibayar penuh; *prorata* mengikuti kehadiran.")
        c1, c2, c3, c4 = st.columns(4)
        ttl = c1.number_input("Tetap (lama)", 0, None, hr["tunjangan_tetap_lama"], step=50000, key=k("ttl"))
        tpl = c2.number_input("Prorata (lama)", 0, None, hr["tunjangan_prorata_lama"], step=50000, key=k("tpl"))
        ttb = c3.number_input("Tetap (baru)", 0, None, hr["tunjangan_tetap_baru"], step=50000, key=k("ttb"))
        tpb = c4.number_input("Prorata (baru)", 0, None, hr["tunjangan_prorata_baru"], step=50000, key=k("tpb"))
    with st.container(border=True):
        st.markdown("##### :material/redeem: THR & BPJS")
        c1, c2 = st.columns(2)
        lebaran = c1.date_input("Hari Raya (Idul Fitri)", key=k("tanggal_lebaran"), format="DD/MM/YYYY")
        bayar = c2.date_input("THR dibayarkan", key=k("tanggal_thr_bayar"), format="DD/MM/YYYY")
        c1, c2, c3 = st.columns(3)
        tk = c1.number_input("BPJS TK terdaftar sejak bulan", 1, 12, hr["bpjs_tk_mulai_bulan"], key=k("tk"))
        kes = c2.number_input("BPJS Kes terdaftar sejak bulan", 1, 12, hr["bpjs_kes_mulai_bulan"], key=k("kes"))
        jkk = c3.text_input("Tarif JKK perusahaan (%)", hr["kelas_jkk_persen"], key=k("jkk"),
                            help="Sesuai kelas risiko yang terdaftar di BPJS Ketenagakerjaan, mis. 0,24")
    with st.container(border=True):
        st.markdown("##### :material/calendar_month: Kehadiran & penghasilan variabel per bulan")
        baris = []
        for b in range(1, 13):
            m = hr["per_masa"].get(str(b), {})
            baris.append({"Bulan": D.NAMA_BULAN[b], "Hari kerja": m.get("hk_penuh"), "Hadir": m.get("hk_aktual"),
                          "Kompensasi (% gaji)": D.desimal_ke_persen(m.get("kompensasi_persen")),
                          "Insentif OTA": m.get("ota", 0) if m else None, "Lembur": m.get("lembur", 0) if m else None,
                          "Komisi": m.get("komisi", 0) if m else None})
        df = pd.DataFrame(baris)
        for c in ("Hari kerja", "Hadir", "Insentif OTA", "Lembur", "Komisi"):
            df[c] = pd.array([None if pd.isna(v) else int(v) for v in df[c]], dtype="Int64")
        rp = {"min_value": 0, "step": 1, "format": "localized"}
        ed = st.data_editor(df, key=k("ed"), hide_index=True, width="stretch", height=H.tinggi(13), disabled=["Bulan"],
                            column_config={"Hari kerja": st.column_config.NumberColumn(min_value=1, max_value=31, step=1,
                                                                                        help="Hari kerja penuh bulan itu"),
                                           "Hadir": st.column_config.NumberColumn(min_value=0, max_value=31, step=1,
                                                                                  help="Hari kerja yang dibayar"),
                                           "Kompensasi (% gaji)": st.column_config.TextColumn(help="Persentase dari gaji pokok, mis. 10"),
                                           "Insentif OTA": st.column_config.NumberColumn(**rp),
                                           "Lembur": st.column_config.NumberColumn(**rp), "Komisi": st.column_config.NumberColumn(**rp)})
        st.caption("Bulan di luar masa kerja (sebelum masuk / sesudah berhenti) diabaikan.")

    kasus = copy.deepcopy(dasar)
    kasus["tahun_pajak"] = int(tahun)
    kasus["metode"] = metode
    try:
        if masuk.year > tahun:
            raise D.IsianTidakValid("tanggal masuk kerja sesudah tahun pajak")
        mulai = masuk.month if masuk.year == tahun else 1
        akhir = keluar or 12
        if akhir < mulai:
            raise D.IsianTidakValid("bulan berhenti sebelum bulan masuk")
        bulan = list(range(mulai, akhir + 1))
        kasus["pegawai"].update(status_ptkp=status, punya_npwp=bool(npwp), bulan_masuk=mulai if mulai > 1 else None,
                                bulan_terakhir_bekerja=keluar)
        kasus["masa"] = [{"bulan": b, "komponen": []} for b in bulan]
        jkk_s = (jkk or "").strip().replace(",", ".")
        if D.persen_ke_desimal(jkk_s, "Tarif JKK") is None:
            raise D.IsianTidakValid("tarif JKK wajib diisi")
        h2 = kasus["data_hr"]
        h2.update(gaji_pokok=int(gaji), kenaikan_nominal=int(naik), kenaikan_tanggal=naik_tgl.isoformat(),
                  kenaikan_hk_sebelum=int(hk_sbl), kenaikan_hk_sesudah=int(hk_ssd), tunjangan_tetap_lama=int(ttl),
                  tunjangan_prorata_lama=int(tpl), tunjangan_tetap_baru=int(ttb), tunjangan_prorata_baru=int(tpb),
                  tanggal_masuk=masuk.isoformat(), tanggal_masuk_awal_bulan=masuk.isoformat()[:8] + "01",
                  tanggal_lebaran=lebaran.isoformat(), tanggal_thr_bayar=bayar.isoformat(), bpjs_tk_mulai_bulan=int(tk),
                  bpjs_kes_mulai_bulan=int(kes), kelas_jkk_persen=jkk_s)
        per = {}
        for b, r in zip(range(1, 13), ed.to_dict("records")):
            if b not in bulan:
                continue
            t = f"bulan {D.NAMA_BULAN[b]}"
            m = {"hk_penuh": D.rupiah_dari_sel(r["Hari kerja"], t + " hari kerja"), "hk_aktual": D.rupiah_dari_sel(r["Hadir"], t + " hadir")}
            if not m["hk_penuh"]:
                raise D.IsianTidakValid(f"{t}: hari kerja wajib diisi (> 0)")
            if m["hk_aktual"] is None:
                raise D.IsianTidakValid(f"{t}: jumlah hadir wajib diisi")
            kp = D.persen_ke_desimal(r["Kompensasi (% gaji)"], t + " kompensasi")
            if kp is not None:
                m["kompensasi_persen"] = kp
            asli = hr["per_masa"].get(str(b), {})
            for kol, f in (("Insentif OTA", "ota"), ("Lembur", "lembur"), ("Komisi", "komisi")):
                v = D.rupiah_dari_sel(r[kol], f"{t} {kol}")
                if v is not None and not (v == 0 and f not in asli):
                    m[f] = v
            per[str(b)] = m
        h2["per_masa"] = per
    except D.IsianTidakValid as e:
        return kasus, f"Isian tidak valid: {e}"
    return kasus, None


# ============================================================================ mode komponen sudah jadi (contoh resmi)

def _cb_tetap(mesin, idx, key):
    S = _S(mesin)
    v = st.session_state.get(key)
    if v is None:
        return
    rows = copy.deepcopy(S["cur"])
    for b in S["bulan"]:
        rows[idx][D.kolom_bulan(b)] = int(v)
    S["baris"], S["cur"] = rows, copy.deepcopy(rows)
    S["ver"] += 1


def _cb_bulan(mesin, key):
    S = _S(mesin)
    baru = sorted(st.session_state[key])
    if baru:
        rows = D.ubah_bulan(S["cur"], S["bulan"], baru)
        S.update(baris=rows, cur=copy.deepcopy(rows), bulan=baru)
        S["ver"] += 1


def _cb_tambah(mesin, key):
    S = _S(mesin)
    kode, kategori = D.KOMPONEN_STANDAR[st.session_state[key]]
    rows = copy.deepcopy(S["cur"])
    if any(r["kode"] == kode and r["kategori"] == kategori for r in rows):
        return
    rows.append({"kode": kode, "kategori": kategori, "satuan": "bulan", **{D.kolom_bulan(b): None for b in S["bulan"]}})
    S["baris"], S["cur"] = rows, copy.deepcopy(rows)
    S["ver"] += 1


def form_komponen(mesin, S):
    g, dasar = S["gen"], S["dasar"]
    p = dasar["pegawai"]
    k = lambda nama: f"{mesin}:{g}:{nama}"
    with st.container(border=True):
        st.markdown("##### :material/badge: Pegawai & pemberi kerja")
        c1, c2, c3 = st.columns(3)
        tahun = c1.number_input("Tahun pajak", 2016, 2026, dasar["tahun_pajak"], key=k("tahun"))
        status = c2.selectbox("Status PTKP", D.STATUS_PTKP, D.STATUS_PTKP.index(p["status_ptkp"]), key=k("ptkp"))
        npwp = c3.toggle("Punya NPWP/NIK valid", p.get("punya_npwp", True), key=k("npwp"))
        c1, c2, c3 = st.columns(3)
        opsi_jk = ["L", "P"] + ([p["jenis_kelamin"]] if p.get("jenis_kelamin") not in (None, "L", "P") else [])
        jk = c1.selectbox("Jenis kelamin", opsi_jk, opsi_jk.index(p.get("jenis_kelamin") or "L"), key=k("jk"),
                          format_func=lambda x: {"L": "Laki-laki", "P": "Perempuan"}.get(x, x.replace("_", " ")))
        metode = c2.selectbox("Metode pajak", list(D.METODE), list(D.METODE).index(dasar["metode"]), key=k("metode"),
                              format_func=D.METODE.get)
        klu = c3.text_input("KLU usaha pemberi kerja", dasar["pemberi_kerja"].get("klu") or "", key=k("klu"),
                            help="Kode lapangan usaha pemberi kerja (menentukan fasilitas PPh 21 DTP 2025-2026)").strip() or None
        with st.expander("Data pegawai lainnya"):
            c1, c2 = st.columns(2)
            lanjut = {}
            for kol, (f, lbl) in zip([c1, c2, c1, c2], [("bulan_masuk", "Bulan mulai bekerja"), ("bulan_terakhir_bekerja", "Bulan terakhir bekerja"),
                                                        ("subjektif_mulai_bulan", "Mulai subjek pajak dalam negeri"),
                                                        ("subjektif_akhir_bulan", "Akhir subjek pajak dalam negeri")]):
                lanjut[f] = kol.number_input(lbl, 1, 12, p.get(f), key=k(f), placeholder="-")
            per = c1.selectbox("Periode gaji", ["bulanan", "mingguan", "harian"],
                               ["bulanan", "mingguan", "harian"].index(p.get("periode_gaji") or "bulanan"), key=k("periode"))
            hk = c2.number_input("Hari kerja sebulan", 1, 31, p.get("hari_kerja_sebulan"), key=k("hk"), placeholder="-")
    with st.container(border=True):
        st.markdown("##### :material/payments: Komponen gaji per bulan")
        if dasar.get("cakupan") == "setahun":
            kb_ = f"{mesin}:{g}:{S['ver']}:bulan"
            st.multiselect("Bulan dibayar", list(range(1, 13)), S["bulan"], key=kb_, format_func=D.NAMA_BULAN.get,
                           on_change=_cb_bulan, args=(mesin, kb_))
        else:
            st.caption(f"Perhitungan satu masa pajak: **{D.NAMA_BULAN.get(S['bulan'][0])}**")
        wadah = st.container()
        with st.expander("Rincian per bulan (tabel)", expanded=len(S["bulan"]) <= 1):
            kol = ["kode", "kategori", "satuan"] + [D.kolom_bulan(b) for b in S["bulan"]]
            df = pd.DataFrame(S["baris"], columns=kol)
            df.insert(0, "Komponen", [D.label_komponen(x) for x in df["kode"]])
            df.insert(1, "Dikenai pajak sebagai", [D.LABEL_KATEGORI_PAJAK.get(x, x) for x in df["kategori"]])
            for b in S["bulan"]:
                c = D.kolom_bulan(b)
                df[c] = pd.array([None if pd.isna(v) else int(v) for v in df[c]], dtype="Int64")
            kc = {"Komponen": st.column_config.TextColumn(width="medium"), "Dikenai pajak sebagai": st.column_config.TextColumn(width="medium")}
            for b in S["bulan"]:
                kc[D.kolom_bulan(b)] = st.column_config.NumberColumn(D.kolom_bulan(b), min_value=0, step=1, format="localized")
            ed = st.data_editor(df, key=f"{mesin}:{g}:{S['ver']}:ed", hide_index=True, width="stretch", column_config=kc,
                                column_order=["Komponen", "Dikenai pajak sebagai"] + [D.kolom_bulan(b) for b in S["bulan"]],
                                disabled=["Komponen", "Dikenai pajak sebagai"], num_rows="fixed")
            S["cur"] = [{c: r[c] for c in kol} for r in ed.to_dict("records")]
            c1, c2 = st.columns([3, 1])
            kt = f"{mesin}:{g}:tambah"
            c1.selectbox("Tambah komponen", list(D.KOMPONEN_STANDAR), key=kt, label_visibility="collapsed")
            c2.button("Tambah", key=f"{mesin}:{g}:btn_tambah", on_click=_cb_tambah, args=(mesin, kt), icon=":material/add:",
                      width="stretch")
            st.caption("Sel kosong = komponen tidak dibayar di bulan itu.")
            if S["khusus"]:
                st.caption("Komponen dalam valuta asing dari data asli: "
                           + ", ".join(f"{D.label_komponen(c['kode'])} ({c['valas']['jumlah']} {c['valas']['mata_uang']})"
                                       for _, c in S["khusus"]))
        with wadah:
            tetap = D.baris_tetap(S["cur"], S["bulan"])
            if tetap:
                kolom = st.columns(2)
                for n, i in enumerate(tetap):
                    r = S["cur"][i]
                    v = r[D.kolom_bulan(S["bulan"][0])]
                    key = f"{mesin}:{g}:{S['ver']}:q:{i}:{v}"
                    kolom[n % 2].number_input(f"{D.label_komponen(r['kode'])} per bulan · **{D.rp(int(v))}**", 0, None, int(v),
                                              step=100000, key=key, on_change=_cb_tetap, args=(mesin, i, key))

    kasus = copy.deepcopy(dasar)
    kasus.update(tahun_pajak=int(tahun), metode=metode)
    kasus["pemberi_kerja"]["klu"] = klu
    pg = kasus["pegawai"]
    pg.update(status_ptkp=status, punya_npwp=bool(npwp), jenis_kelamin=jk)
    for f, v in list(lanjut.items()) + [("periode_gaji", per), ("hari_kerja_sebulan", hk)]:
        if f in pg or v is not None:
            pg[f] = None if v is None else (v if isinstance(v, str) else int(v))
    try:
        kasus["masa"] = D.tabel_ke_masa(S["cur"], S["bulan"], S["khusus"])
    except D.IsianTidakValid as e:
        return kasus, f"Isian tidak valid: {e}"
    return kasus, None


# ============================================================================ tab

def tampilkan(mesin):
    S = _S(mesin)
    daftar = D.daftar_data()
    if "data_id" not in S:
        muat_ke_state(mesin, "KAR-A")
    kiri, kanan = st.columns([5, 7], gap="large")
    with kiri:
        grup_kini = daftar[S["data_id"]]["grup"]
        kg = f"{mesin}:grup"
        grup = st.segmented_control("Sumber data pegawai", [D.GRUP_HR, D.GRUP_RESMI], default=grup_kini, key=kg) or grup_kini
        opsi = [i for i, d in daftar.items() if d["grup"] == grup]
        if S["data_id"] not in opsi:
            muat_ke_state(mesin, opsi[0])
        kd = f"{mesin}:data:{grup}"
        if st.session_state.get(kd) != S["data_id"]:
            st.session_state[kd] = S["data_id"]
        st.selectbox("Data pegawai", opsi, key=kd, format_func=lambda i: daftar[i]["label"], on_change=_cb_data, args=(mesin, kd))
        info = daftar[S["data_id"]]
        c1, c2 = st.columns([4, 1])
        c1.caption(f":material/database: Sumber: {info['sumber']}  \nPerubahan hanya di layar ini; dataset tidak diubah.")
        c2.button("Reset", key=f"{mesin}:reset", on_click=_cb_reset, args=(mesin,), icon=":material/restart_alt:", width="stretch")
        if info["jenis"] == "hr":
            kasus, galat = form_hr(mesin, S)
        else:
            kasus, galat = form_komponen(mesin, S)
    with kanan:
        if galat:
            H.galat(galat)
            return
        utuh = D.normal(kasus) == D.normal(D.muat_data(S["data_id"]))
        H.panel(mesin, kasus, info, S["data_id"], utuh)
