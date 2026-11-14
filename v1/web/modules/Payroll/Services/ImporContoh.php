<?php

namespace Modules\Payroll\Services;

use App\Helpers\Desimal;
use App\Models\Payroll\Pegawai;
use Carbon\CarbonImmutable;
use Illuminate\Support\Facades\DB;

/**
 * Kasus kanonik dengan `data_hr` -> baris database (kebalikan PenyusunKasus). Dipakai untuk memuat pegawai contoh
 * dari dataset induk: Karyawan A (xlsx kantor, dianonimkan) dan 8 pegawai sintetis berbasis data publik.
 */
class ImporContoh
{
    public function __construct(private MesinPajak $mesin) {}

    /** @return list<string> nomor induk pegawai yang baru dibuat (yang sudah ada dilewati) */
    public function jalankan(): array
    {
        $dibuat = [];
        foreach ($this->mesin->contoh() as $c) {
            if (Pegawai::where('nomor_induk', $c['id'])->exists()) {
                continue;
            }
            $this->impor($c['id'], $c['label'], $c['kasus']);
            $dibuat[] = $c['id'];
        }

        return $dibuat;
    }

    public function impor(string $nomorInduk, string $nama, array $kasus): Pegawai
    {
        $hr = $kasus['data_hr'];
        $p = $kasus['pegawai'];
        $tahun = $kasus['tahun_pajak'];
        $berhenti = $p['bulan_terakhir_bekerja']
            ? CarbonImmutable::create($tahun, $p['bulan_terakhir_bekerja'], 1)->endOfMonth()->toDateString()
            : null;

        return DB::transaction(function () use ($nomorInduk, $nama, $kasus, $hr, $p, $tahun, $berhenti) {
            $pegawai = Pegawai::create([
                'nomor_induk' => $nomorInduk, 'nama' => $nama, 'jenis_kelamin' => $p['jenis_kelamin'],
                'punya_npwp' => $p['punya_npwp'], 'tanggal_masuk' => $hr['tanggal_masuk'], 'tanggal_berhenti' => $berhenti,
            ]);
            $pt = $pegawai->payrollTahun()->create([
                'tahun' => $tahun, 'status_ptkp' => $p['status_ptkp'], 'metode' => $kasus['metode'],
                ...array_intersect_key($hr, array_flip([
                    'gaji_pokok', 'kenaikan_nominal', 'kenaikan_tanggal', 'kenaikan_hk_sebelum', 'kenaikan_hk_sesudah',
                    'kenaikan_hari_sebelum', 'kenaikan_hari_sesudah', 'tunjangan_tetap_lama', 'tunjangan_prorata_lama',
                    'tunjangan_tetap_baru', 'tunjangan_prorata_baru', 'tanggal_lebaran', 'tanggal_thr_bayar',
                    'bpjs_tk_mulai_bulan', 'bpjs_kes_mulai_bulan', 'kelas_jkk_persen',
                ])),
            ]);
            foreach ($hr['per_masa'] as $b => $m) {
                $pt->bulan()->create([
                    'bulan' => (int) $b, 'hk_penuh' => $m['hk_penuh'], 'hk_aktual' => $m['hk_aktual'],
                    'kompensasi_persen' => isset($m['kompensasi_persen']) ? Desimal::pecahanKePersen($m['kompensasi_persen']) : null,
                    'ota' => $m['ota'] ?? null, 'lembur' => $m['lembur'] ?? null, 'komisi' => $m['komisi'] ?? null,
                ]);
            }

            return $pegawai;
        });
    }
}
