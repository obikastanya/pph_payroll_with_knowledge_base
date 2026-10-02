<?php

namespace Modules\Payroll\Services;

use App\Models\Payroll\PayrollTahun;
use App\Models\Payroll\Perhitungan;
use App\Models\User;
use Illuminate\Support\Facades\DB;

/**
 * Menghitung satu atau banyak pegawai-tahun dalam satu panggilan engine, lalu mencatat setiap hasil sebagai baris
 * `perhitungan` baru (riwayat tidak pernah ditimpa). Angka yang disimpan adalah keluaran engine apa adanya.
 */
class Penghitung
{
    public function __construct(private MesinPajak $mesin, private PenyusunKasus $penyusun, private KbTambahan $kb) {}

    /**
     * @param  iterable<PayrollTahun>  $daftar
     * @return list<Perhitungan>
     *
     * @throws MesinTidakTersedia bila engine tidak dapat dipanggil (tidak ada baris yang dicatat)
     */
    public function hitung(iterable $daftar, ?User $user = null): array
    {
        $berkas = $this->kb->berkasAktif();
        $sidik = $this->kb->sidik($berkas);
        $siap = [];
        $catatan = [];
        foreach ($daftar as $pt) {
            $pt->loadMissing('pegawai', 'bulan', 'masukan');
            try {
                $kasus = $this->penyusun->susun($pt);
                $siap[] = [$pt, $kasus];
            } catch (DataTidakLengkap $e) {
                $catatan[] = [$pt, null, ['ok' => false, 'jenis' => 'data_tidak_lengkap', 'pesan' => 'Data belum lengkap: '.$e->getMessage()]];
            }
        }
        $jawaban = $this->mesin->hitung(array_column($siap, 1), true, $berkas);
        foreach ($siap as $i => [$pt, $kasus]) {
            $catatan[] = [$pt, $kasus, $jawaban[$i]];
        }

        return DB::transaction(fn () => array_map(
            fn ($c) => $this->catat($c[0], $c[1], $c[2], $user, $sidik),
            $catatan,
        ));
    }

    private function catat(PayrollTahun $pt, ?array $kasus, array $jawab, ?User $user, string $sidik): Perhitungan
    {
        $data = [
            'user_id' => $user?->id,
            'berhasil' => (bool) $jawab['ok'],
            'kasus' => $kasus === null ? 'null' : PenyusunKasus::json($kasus),
            'sidik_kb' => $sidik,
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

    /** True bila hasil terakhir tidak lagi mengikuti data HR atau aturan KB yang berlaku sekarang. */
    public function kedaluwarsa(PayrollTahun $pt, ?Perhitungan $p): bool
    {
        return $this->alasanKedaluwarsa($pt, $p) !== null;
    }

    /** 'kb' = berkas KB tambahan berubah sejak dihitung; 'data' = data HR berubah; null = masih berlaku. */
    public function alasanKedaluwarsa(PayrollTahun $pt, ?Perhitungan $p): ?string
    {
        if ($p === null) {
            return null;
        }
        if (($p->sidik_kb ?? '') !== $this->kb->sidik()) {
            return 'kb';
        }
        try {
            $berubah = PenyusunKasus::json($this->penyusun->susun($pt)) !== $p->kasus;
        } catch (DataTidakLengkap) {
            $berubah = $p->kasus !== 'null';
        } catch (MesinTidakTersedia) {
            return null;   // isian tambahan tidak dapat dibaca: jangan menuduh data berubah
        }

        return $berubah ? 'data' : null;
    }
}
