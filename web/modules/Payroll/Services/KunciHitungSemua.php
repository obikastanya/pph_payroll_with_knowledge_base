<?php

namespace Modules\Payroll\Services;

use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Str;

/**
 * Kunci Hitung semua per tahun pajak: dua proses (dua admin, atau Dashboard dan `payroll:hitung`) tidak boleh menghitung
 * tahun yang sama bersamaan, karena setiap hitungan menambah baris riwayat. Kunci disimpan di cache dengan masa berlaku
 * payroll.timeout + 120 detik dan diperpanjang sebelum setiap batch; bila PHP berhenti tanpa sempat melepasnya (galat
 * fatal, batas waktu), kunci lepas sendiri setelah masa berlakunya habis.
 */
class KunciHitungSemua
{
    private function __construct(private string $kunci, private string $token) {}

    /** Ambil kunci tahun ini; null bila sedang dipegang proses lain. */
    public static function ambil(int $tahun): ?self
    {
        $kunci = new self(self::nama($tahun), (string) Str::uuid());

        return Cache::add($kunci->kunci, $kunci->token, self::masaBerlaku()) ? $kunci : null;
    }

    public static function nama(int $tahun): string
    {
        return "hitung-semua:{$tahun}";
    }

    /** Detik: satu panggilan engine paling lama payroll.timeout, ditambah jeda untuk menyusun kasus dan mencatat hasil. */
    public static function masaBerlaku(): int
    {
        return (int) config('payroll.timeout') + 120;
    }

    public static function pesanTerkunci(int $tahun): string
    {
        return "Hitung semua tahun {$tahun} masih berjalan di proses lain; tunggu sampai selesai. Kunci yang tertinggal "
            .'(proses terhenti) lepas sendiri paling lama '.self::masaBerlaku().' detik.';
    }

    /** Dipanggil sebelum setiap batch: masa berlaku dihitung ulang dari sekarang. */
    public function perpanjang(): void
    {
        Cache::put($this->kunci, $this->token, self::masaBerlaku());
    }

    /** Lepas hanya bila kunci masih milik proses ini (kunci yang kedaluwarsa bisa sudah diambil proses lain). */
    public function lepas(): void
    {
        if (Cache::get($this->kunci) === $this->token) {
            Cache::forget($this->kunci);
        }
    }
}
