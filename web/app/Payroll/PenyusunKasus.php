<?php

namespace App\Payroll;

use App\Models\PayrollTahun;
use App\Support\Desimal;
use App\Support\Format;

/**
 * Database -> kasus kanonik (format README induk §3) dengan `data_hr` untuk lapisan Perusahaan X.
 *
 * Padanan ui/kalkulator.py::form_hr di induk: hanya menyalin dan menata data, tanpa aturan pajak. Hasilnya untuk
 * pegawai contoh harus identik dengan kasus di dataset (diuji di tests/Feature/IntegrasiMesinTest.php).
 */
final class PenyusunKasus
{
    public function susun(PayrollTahun $pt): array
    {
        $pegawai = $pt->pegawai;
        $tahun = $pt->tahun;
        $rentang = $pegawai->rentangBulan($tahun);
        if ($rentang === null) {
            throw new DataTidakLengkap("pegawai tidak bekerja di tahun pajak {$tahun} (cek tanggal masuk/berhenti)");
        }
        [$mulai, $akhir] = $rentang;
        $bulanKerja = range($mulai, $akhir);

        return [
            'id' => "PAYROLL-{$pt->id}",
            'tahun_pajak' => $tahun,
            'cakupan' => 'setahun',
            'metode' => $pt->metode,
            'kurs' => new \stdClass,
            'dtp' => new \stdClass,
            'pegawai' => [
                'status_ptkp' => $pt->status_ptkp,
                'jenis_kelamin' => $pegawai->jenis_kelamin,
                'punya_npwp' => (bool) $pegawai->punya_npwp,
                'subjektif_mulai_bulan' => null,
                'subjektif_akhir_bulan' => null,
                'bulan_masuk' => $mulai > 1 ? $mulai : null,
                // berhenti di tahun ini (termasuk Desember) = resign sungguhan; bukan sekadar akhir tahun
                'bulan_terakhir_bekerja' => $pegawai->tanggal_berhenti?->year === $tahun ? $akhir : null,
                'periode_gaji' => 'bulanan',
                'hari_kerja_sebulan' => null,
            ],
            'pemberi_kerja' => ['klu' => config('payroll.klu'), 'jenis' => 'biasa'],
            'masa' => array_map(fn (int $b) => ['bulan' => $b, 'komponen' => []], $bulanKerja),
            'data_hr' => $this->dataHr($pt, $bulanKerja),
        ];
    }

    /** Teks JSON kanonik kasus: dipakai untuk dikirim ke engine dan untuk mendeteksi data berubah sejak dihitung. */
    public static function json(array $kasus): string
    {
        return json_encode($kasus, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR);
    }

    private function dataHr(PayrollTahun $pt, array $bulanKerja): array
    {
        $masuk = $pt->pegawai->tanggal_masuk;
        $perBulan = $pt->bulan->keyBy('bulan');
        $perMasa = [];
        foreach ($bulanKerja as $b) {
            $m = $perBulan->get($b);
            $nama = Format::bulan($b, true);
            if ($m === null || ! $m->hk_penuh) {
                throw new DataTidakLengkap("hari kerja bulan {$nama} belum diisi");
            }
            if ($m->hk_aktual === null) {
                throw new DataTidakLengkap("jumlah hadir bulan {$nama} belum diisi");
            }
            $isi = ['hk_penuh' => $m->hk_penuh, 'hk_aktual' => $m->hk_aktual];
            if ($m->kompensasi_persen !== null) {
                $isi['kompensasi_persen'] = Desimal::persenKePecahan($m->kompensasi_persen);
            }
            foreach (['ota', 'lembur', 'komisi'] as $f) {
                if ($m->{$f} !== null) {
                    $isi[$f] = $m->{$f};
                }
            }
            $perMasa[(string) $b] = $isi;
        }

        return [
            'gaji_pokok' => $pt->gaji_pokok,
            'kenaikan_tanggal' => $pt->kenaikan_tanggal->toDateString(),
            'kenaikan_nominal' => $pt->kenaikan_nominal,
            'kenaikan_hk_sebelum' => $pt->kenaikan_hk_sebelum,
            'kenaikan_hk_sesudah' => $pt->kenaikan_hk_sesudah,
            'kenaikan_hari_sebelum' => $pt->kenaikan_hari_sebelum,
            'kenaikan_hari_sesudah' => $pt->kenaikan_hari_sesudah,
            'tunjangan_tetap_lama' => $pt->tunjangan_tetap_lama,
            'tunjangan_prorata_lama' => $pt->tunjangan_prorata_lama,
            'tunjangan_tetap_baru' => $pt->tunjangan_tetap_baru,
            'tunjangan_prorata_baru' => $pt->tunjangan_prorata_baru,
            'tanggal_masuk' => $masuk->toDateString(),
            'tanggal_masuk_awal_bulan' => $masuk->copy()->startOfMonth()->toDateString(),
            'tanggal_lebaran' => $pt->tanggal_lebaran->toDateString(),
            'tanggal_thr_bayar' => $pt->tanggal_thr_bayar->toDateString(),
            'bpjs_tk_mulai_bulan' => $pt->bpjs_tk_mulai_bulan,
            'bpjs_kes_mulai_bulan' => $pt->bpjs_kes_mulai_bulan,
            'kelas_jkk_persen' => $pt->kelas_jkk_persen,
            'per_masa' => $perMasa === [] ? new \stdClass : $perMasa,
        ];
    }
}
