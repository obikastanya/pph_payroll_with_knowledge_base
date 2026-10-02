<?php

namespace Modules\Payroll\Services;

/** Daftar pilihan dan label tampilan (padanan ui/data.py di induk). */
final class Label
{
    public const STATUS_PTKP = ['TK/0', 'TK/1', 'TK/2', 'TK/3', 'K/0', 'K/1', 'K/2', 'K/3', 'K/I/0', 'K/I/1', 'K/I/2', 'K/I/3'];

    public const METODE = [
        'gross' => 'Gross (dipotong dari gaji)',
        'gross_up' => 'Gross-up (perusahaan beri tunjangan pajak)',
        'ditanggung_pemberi_kerja' => 'Ditanggung pemberi kerja (nett)',
    ];

    public const JENIS_KELAMIN = ['L' => 'Laki-laki', 'P' => 'Perempuan'];

    public const FAKTA = [
        'bruto' => 'Penghasilan bruto', 'kategori_ter' => 'Kategori TER', 'tarif_ter' => 'Tarif TER', 'pph21' => 'PPh 21',
        'pph21_dtp' => 'PPh 21 ditanggung pemerintah', 'tunjangan_pajak' => 'Tunjangan pajak', 'pph21_berjalan' => 'PPh 21 masa berjalan',
        'bruto_setahun' => 'Bruto setahun', 'biaya_jabatan' => 'Biaya jabatan', 'iuran_pengurang' => 'Iuran pensiun/JHT/JP pegawai',
        'zakat' => 'Zakat / sumbangan wajib', 'neto_setahun' => 'Neto setahun', 'neto_disetahunkan' => 'Neto disetahunkan',
        'ptkp' => 'PTKP', 'pkp' => 'PKP (dibulatkan ke bawah ribuan)', 'pph21_disetahunkan' => 'PPh 21 atas neto disetahunkan',
        'pph21_setahun' => 'PPh 21 terutang setahun', 'pph21_dipotong_sebelumnya' => 'Sudah dipotong masa sebelumnya',
        'pph21_masa_terakhir' => 'PPh 21 masa terakhir', 'lebih_bayar_dikembalikan' => 'Lebih bayar dikembalikan',
        'berhak_dtp' => 'Berhak DTP', 'status_ptkp_efektif' => 'Status PTKP efektif', 'n_subjektif' => 'Jumlah bulan subjektif',
        'gross_up' => 'Metode gross-up', 'bruto_total_masa' => 'Bruto masa (termasuk tidak teratur)', 'iuran_masa' => 'Iuran pegawai masa',
        'zakat_masa' => 'Zakat masa', 'natura_objek' => 'Natura objek pajak', 'px_gaji' => 'Gaji (prorata)', 'px_tunjangan' => 'Tunjangan',
        'px_thr' => 'THR', 'px_kompensasi' => 'Kompensasi', 'px_ota' => 'Insentif OTA', 'px_lembur' => 'Lembur', 'px_komisi' => 'Komisi',
        'px_premi_jkk' => 'Premi JKK (perusahaan)', 'px_premi_jkm' => 'Premi JKM (perusahaan)', 'px_premi_kes' => 'Premi BPJS Kes (perusahaan)',
        'px_premi_jht_pk' => 'JHT perusahaan (bukan objek)', 'px_premi_jp_pk' => 'JP perusahaan (bukan objek)',
        'px_iuran_jht_pg' => 'Iuran JHT pegawai', 'px_iuran_jp_pg' => 'Iuran JP pegawai', 'px_iuran_kes_pg' => 'Iuran BPJS Kes pegawai',
        'px_penghasilan_tunai' => 'Penghasilan tunai', 'px_thp' => 'Take home pay',
    ];

    public const CEK_SILANG = [
        'identik' => 'identik',
        'sah_titik_tetap_ganda' => 'beda, keduanya sah',
        'berbeda' => 'BERBEDA',
        'galat' => 'tidak dapat dicek',
        'dilewati' => 'dilewati (KB tambahan)',
    ];

    public static function fakta(string $fakta): string
    {
        return self::FAKTA[$fakta] ?? $fakta;
    }
}
