<?php

namespace App\Payroll;

use App\Models\PayrollTahun;
use App\Models\Perhitungan;
use App\Models\User;
use Illuminate\Support\Facades\DB;

/**
 * Menghitung satu atau banyak pegawai-tahun dalam satu panggilan engine, lalu mencatat setiap hasil sebagai baris
 * `perhitungan` baru (riwayat tidak pernah ditimpa). Angka yang disimpan adalah keluaran engine apa adanya.
 */
class Penghitung
{
    public function __construct(private MesinPajak $mesin, private PenyusunKasus $penyusun) {}

    /**
     * @param  iterable<PayrollTahun>  $daftar
     * @return list<Perhitungan>
     *
     * @throws MesinTidakTersedia bila engine tidak dapat dipanggil (tidak ada baris yang dicatat)
     */
    public function hitung(iterable $daftar, ?User $user = null): array
    {
        $siap = [];
        $catatan = [];
        foreach ($daftar as $pt) {
            $pt->loadMissing('pegawai', 'bulan');
            try {
                $kasus = $this->penyusun->susun($pt);
                $siap[] = [$pt, $kasus];
            } catch (DataTidakLengkap $e) {
                $catatan[] = [$pt, null, ['ok' => false, 'jenis' => 'data_tidak_lengkap', 'pesan' => 'Data belum lengkap: '.$e->getMessage()]];
            }
        }
        $jawaban = $this->mesin->hitung(array_column($siap, 1));
        foreach ($siap as $i => [$pt, $kasus]) {
            $catatan[] = [$pt, $kasus, $jawaban[$i]];
        }

        return DB::transaction(fn () => array_map(
            fn ($c) => $this->catat($c[0], $c[1], $c[2], $user),
            $catatan,
        ));
    }

    private function catat(PayrollTahun $pt, ?array $kasus, array $jawab, ?User $user): Perhitungan
    {
        $data = [
            'user_id' => $user?->id,
            'berhasil' => (bool) $jawab['ok'],
            'kasus' => $kasus === null ? 'null' : PenyusunKasus::json($kasus),
        ];
        if (! $jawab['ok']) {
            return $pt->perhitungan()->create($data + ['jenis_galat' => $jawab['jenis'] ?? 'galat', 'pesan' => $jawab['pesan'] ?? null]);
        }
        $h = $jawab['hasil'];
        $cek = $jawab['cek_silang'] ?? null;
        $thp = 0;
        foreach ($h['per_masa'] as $m) {
            $thp += $m['px_thp'] ?? 0;
        }

        return $pt->perhitungan()->create($data + [
            'hasil' => json_encode($h, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR),
            'cek_silang' => $cek['status'] ?? null,
            'cek_silang_rinci' => $cek ? json_encode($cek['selisih'] ?? [], JSON_THROW_ON_ERROR) : null,
            'versi_engine' => $h['audit']['versi_engine'] ?? null,
            'versi_kb' => $h['audit']['versi_kb'] ?? null,
            'bruto_setahun' => $h['tahunan']['bruto_setahun'] ?? null,
            'pph21_setahun' => $h['tahunan']['pph21_setahun'] ?? null,
            'thp_setahun' => $thp,
        ]);
    }

    /** True bila data HR sudah berubah sejak perhitungan terakhir (kasus yang akan dikirim tidak sama lagi). */
    public function kedaluwarsa(PayrollTahun $pt, ?Perhitungan $p): bool
    {
        if ($p === null) {
            return false;
        }
        try {
            return PenyusunKasus::json($this->penyusun->susun($pt)) !== $p->kasus;
        } catch (DataTidakLengkap) {
            return $p->kasus !== 'null';
        }
    }
}
