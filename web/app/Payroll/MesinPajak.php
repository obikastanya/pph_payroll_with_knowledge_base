<?php

namespace App\Payroll;

use Illuminate\Support\Facades\Process;
use JsonException;

/**
 * Klien jembatan ke engine KB: menjalankan `python -m jembatan` di repositori induk, satu permintaan JSON di stdin,
 * satu jawaban JSON di stdout (lihat jembatan/__main__.py). Satu panggilan dapat memuat banyak kasus, sehingga KB
 * cukup dimuat sekali untuk satu batch payroll.
 */
class MesinPajak
{
    /**
     * @param  list<array>  $daftarKasus
     * @return list<array> satu jawaban per kasus, urutan sama: {ok, hasil, cek_silang} atau {ok: false, jenis, pesan}
     */
    public function hitung(array $daftarKasus, bool $cekSilang = true): array
    {
        if ($daftarKasus === []) {
            return [];
        }
        $jawab = $this->panggil(['perintah' => 'hitung', 'kasus' => array_values($daftarKasus), 'cek_silang' => $cekSilang]);
        if (! is_array($jawab['hasil'] ?? null) || count($jawab['hasil']) !== count($daftarKasus)) {
            throw new MesinTidakTersedia('jawaban engine tidak lengkap: jumlah hasil tidak sama dengan jumlah kasus');
        }

        return $jawab['hasil'];
    }

    /** Pegawai contoh dari dataset induk: [{id, label, kasus}]. */
    public function contoh(): array
    {
        return $this->panggil(['perintah' => 'contoh'])['contoh'];
    }

    /** Metadata audit: versi engine, versi KB (commit), hash & status verifikasi tabel. */
    public function info(): array
    {
        return $this->panggil(['perintah' => 'info'])['audit'];
    }

    private function panggil(array $permintaan): array
    {
        $python = config('payroll.python');
        $root = config('payroll.root');
        $hasil = Process::path($root)
            ->timeout(config('payroll.timeout'))
            ->env(['PYTHONIOENCODING' => 'utf-8', 'PYTHONDONTWRITEBYTECODE' => '1'])
            ->input(json_encode($permintaan, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR))
            ->run([$python, '-m', 'jembatan']);

        try {
            $jawab = json_decode($hasil->output(), true, 512, JSON_THROW_ON_ERROR);
        } catch (JsonException) {
            $petunjuk = is_file($python) ? '' : " Python tidak ditemukan di '{$python}' (atur PAYROLL_PYTHON di .env).";
            $stderr = trim(mb_substr($hasil->errorOutput(), -1500));
            throw new MesinTidakTersedia("engine tidak memberi jawaban yang valid (kode keluar {$hasil->exitCode()}).{$petunjuk}"
                .($stderr !== '' ? "\n{$stderr}" : ''));
        }
        if (! ($jawab['ok'] ?? false)) {
            throw new MesinTidakTersedia(($jawab['jenis'] ?? 'galat').': '.($jawab['pesan'] ?? 'tanpa pesan'));
        }

        return $jawab;
    }
}
