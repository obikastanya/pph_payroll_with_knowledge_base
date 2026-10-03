<?php

namespace Modules\Payroll\Services;

use App\Models\Payroll\PayrollTahun;
use App\Models\Payroll\Perhitungan;
use App\Models\User;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\LazyCollection;
use JsonException;

/**
 * Menghitung pegawai-tahun per batch (payroll.ukuran_batch pegawai per panggilan engine), lalu mencatat setiap hasil
 * sebagai baris `perhitungan` baru (riwayat tidak pernah ditimpa). Setiap batch dicatat dalam transaksinya sendiri:
 * bila engine gagal di tengah jalan, batch sebelumnya tetap tersimpan. Angka yang disimpan adalah keluaran engine
 * apa adanya.
 */
class Penghitung
{
    public function __construct(private MesinPajak $mesin, private PenyusunKasus $penyusun, private KbTambahan $kb) {}

    /**
     * Hitung dan kembalikan baris riwayat yang dicatat (halaman payroll: satu pegawai-tahun).
     *
     * @param  iterable<PayrollTahun>  $daftar
     * @return list<Perhitungan>
     *
     * @throws HitungTerhenti bila engine gagal (baris batch sebelumnya tetap tercatat)
     */
    public function hitung(iterable $daftar, ?User $user = null): array
    {
        $tercatat = [];
        $this->proses($daftar, $user, null, function (Perhitungan $p) use (&$tercatat) {
            $tercatat[] = $p;
        });

        return $tercatat;
    }

    /**
     * Hitung semua (Dashboard): hanya jumlahnya yang dikembalikan. Hasil setiap batch dilepas setelah dicatat, jadi
     * memori tidak tumbuh dengan jumlah pegawai bila $daftar dimuat bertahap (LazyCollection). $sebelumBatch dipanggil
     * sebelum setiap batch dengan jumlah baris yang sudah tercatat (perpanjang kunci, laporan kemajuan).
     *
     * @param  iterable<PayrollTahun>  $daftar
     * @param  null|callable(int): void  $sebelumBatch
     * @return array{dihitung: int, gagal: int}
     *
     * @throws HitungTerhenti bila engine gagal di tengah jalan ($e->dicatat pegawai sudah tercatat)
     */
    public function hitungSemua(iterable $daftar, ?User $user = null, ?callable $sebelumBatch = null): array
    {
        $gagal = 0;
        $dihitung = $this->proses($daftar, $user, $sebelumBatch, function (Perhitungan $p) use (&$gagal) {
            $gagal += $p->berhasil ? 0 : 1;
        });

        return ['dihitung' => $dihitung, 'gagal' => $gagal];
    }

    /** Pegawai per panggilan engine (PAYROLL_UKURAN_BATCH, minimal 1). */
    public function ukuranBatch(): int
    {
        return max(1, (int) config('payroll.ukuran_batch'));
    }

    /**
     * Per batch: panggil $sebelumBatch (bila ada), susun kasus, satu panggilan engine, catat dalam satu transaksi, serahkan
     * setiap baris ke $tiapBaris, lalu lepaskan sebelum batch berikutnya. Mengembalikan jumlah baris yang tercatat.
     */
    private function proses(iterable $daftar, ?User $user, ?callable $sebelumBatch, callable $tiapBaris): int
    {
        $berkas = $this->kb->berkasAktif();
        $sidik = $this->kb->sidik($berkas);
        $dicatat = 0;
        foreach (LazyCollection::make($daftar)->chunk($this->ukuranBatch()) as $batch) {
            if ($sebelumBatch !== null) {
                $sebelumBatch($dicatat);
            }
            self::perpanjangBatasWaktu();
            try {
                $catatan = $this->hitungBatch($batch, $berkas, $sidik);
            } catch (MesinTidakTersedia $e) {   // termasuk batas waktu engine (MesinPajak::panggil)
                throw new HitungTerhenti($e->getMessage(), $dicatat, $e);
            }
            $baris = DB::transaction(fn () => array_map(fn (array $c) => $this->catat($c[0], $c[1], $c[2], $user, $c[3]), $catatan));
            unset($catatan);
            foreach ($baris as $p) {
                $tiapBaris($p);
            }
            $dicatat += count($baris);
            unset($baris);
        }

        return $dicatat;
    }

    /**
     * Susun kasus satu batch dan hitung dalam satu panggilan engine.
     *
     * @return list<array{0: PayrollTahun, 1: ?array, 2: array, 3: string}> [data HR, kasus, jawaban engine, sidik KB]
     */
    private function hitungBatch(iterable $batch, array $berkas, string $sidik): array
    {
        $siap = [];
        $catatan = [];
        foreach ($batch as $pt) {
            $pt->loadMissing('pegawai', 'bulan', 'masukan');
            try {
                $siap[] = [$pt, $this->penyusun->susun($pt)];
            } catch (DataTidakLengkap $e) {
                $catatan[] = [$pt, null, ['ok' => false, 'jenis' => 'data_tidak_lengkap', 'pesan' => 'Data belum lengkap: '.$e->getMessage()], $sidik];
            }
        }
        $jawab = $this->mesin->hitungDenganSidik(array_column($siap, 1), true, $berkas);
        foreach ($siap as $i => [$pt, $kasus]) {
            // sidik berkas yang benar-benar dimuat engine untuk batch ini; sidik hitungan PHP bila jawaban tidak memuatnya
            $catatan[] = [$pt, $kasus, $jawab['hasil'][$i], $jawab['sidik_kb'] ?? $sidik];
        }

        return $catatan;
    }

    /**
     * Batas waktu PHP (max_execution_time) berlaku untuk seluruh request dan di Windows ikut menghitung waktu menunggu
     * engine: setiap batch mendapat jatah baru. Tanpa batas (CLI, tes) tidak diubah.
     */
    private static function perpanjangBatasWaktu(): void
    {
        if ((int) ini_get('max_execution_time') > 0 && function_exists('set_time_limit')) {
            set_time_limit((int) config('payroll.timeout') + 60);
        }
    }

    private function catat(PayrollTahun $pt, ?array $kasus, array $jawab, ?User $user, string $sidik): Perhitungan
    {
        return $pt->perhitungan()->create([
            'user_id' => $user?->id,
            'kasus' => $kasus === null ? 'null' : PenyusunKasus::json($kasus),
            'sidik_kb' => $sidik,
        ] + self::kolomHasil($jawab));
    }

    /**
     * Kolom hasil dari satu jawaban engine. Jawaban yang tidak dapat disimpan menjadi baris gagal untuk pegawai itu saja:
     * di PostgreSQL satu nilai yang ditolak membatalkan seluruh transaksi batch.
     */
    private static function kolomHasil(array $jawab): array
    {
        if (! $jawab['ok']) {
            return ['berhasil' => false, 'jenis_galat' => $jawab['jenis'] ?? 'galat', 'pesan' => $jawab['pesan'] ?? null];
        }
        $h = $jawab['hasil'];
        $thp = 0;
        foreach ($h['per_masa'] as $m) {
            $px = $m['px_thp'] ?? 0;
            if (! is_int($px)) {
                return self::diLuarBatas('thp_setahun');
            }
            $thp += $px;
        }
        $angka = ['bruto_setahun' => $h['tahunan']['bruto_setahun'] ?? null, 'pph21_setahun' => $h['tahunan']['pph21_setahun'] ?? null,
            'thp_setahun' => $thp];
        foreach ($angka as $kolom => $nilai) {
            // bigint: bilangan di luar batas PHP menjadi float (json_decode, atau penjumlahan thp yang meluap)
            if ($nilai !== null && ! is_int($nilai)) {
                return self::diLuarBatas($kolom);
            }
        }
        $cek = $jawab['cek_silang'] ?? null;
        try {
            return $angka + [
                'berhasil' => true,
                'hasil' => json_encode($h, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR),
                'cek_silang' => $cek['status'] ?? null,
                'cek_silang_rinci' => $cek ? json_encode($cek['selisih'] ?? [], JSON_THROW_ON_ERROR) : null,
                'versi_engine' => $h['audit']['versi_engine'] ?? null,
                'versi_kb' => $h['audit']['versi_kb'] ?? null,
            ];
        } catch (JsonException $e) {
            return ['berhasil' => false, 'jenis_galat' => 'hasil_tidak_valid',
                'pesan' => 'Hasil engine tidak dapat disimpan sebagai JSON: '.$e->getMessage().'.'];
        }
    }

    private static function diLuarBatas(string $kolom): array
    {
        return ['berhasil' => false, 'jenis_galat' => 'nilai_di_luar_batas',
            'pesan' => "Hasil engine tidak dapat disimpan: {$kolom} bukan bilangan bulat dalam batas kolom database (bigint)."];
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
