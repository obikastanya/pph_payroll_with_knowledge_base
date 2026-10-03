<?php

namespace Modules\Payroll\Services;

use Illuminate\Process\Exceptions\ProcessTimedOutException;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Process;
use JsonException;

/**
 * Klien jembatan ke engine KB: menjalankan `python -m jembatan` di repositori induk, satu permintaan JSON di stdin,
 * satu jawaban JSON di stdout (lihat jembatan/__main__.py). Satu panggilan dapat memuat banyak kasus, sehingga KB
 * cukup dimuat sekali untuk satu batch payroll. Berkas KB tambahan yang aktif ikut dikirim pada setiap panggilan.
 */
class MesinPajak
{
    /**
     * Rahasia di lingkungan PHP yang tidak boleh diwarisi proses jembatan (false = dihapus dari lingkungan proses anak,
     * lihat Symfony Process::start). Hanya `usulkan` yang menerima satu kunci: kunci penyedia LLM yang dikonfigurasi.
     */
    public const RAHASIA = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'DB_PASSWORD', 'DB_URL', 'APP_KEY', 'MAIL_PASSWORD', 'REDIS_PASSWORD',
        'AWS_SECRET_ACCESS_KEY'];

    public function __construct(private KbTambahan $kb) {}

    /**
     * @param  list<array>  $daftarKasus
     * @param  list<string>|null  $berkasTambahan  null = berkas KB tambahan yang aktif sekarang
     * @return list<array> satu jawaban per kasus, urutan sama: {ok, hasil, cek_silang} atau {ok: false, jenis, pesan}
     */
    public function hitung(array $daftarKasus, bool $cekSilang = true, ?array $berkasTambahan = null): array
    {
        return $this->hitungDenganSidik($daftarKasus, $cekSilang, $berkasTambahan)['hasil'];
    }

    /**
     * Seperti hitung(), ditambah sidik berkas KB tambahan yang benar-benar dimuat engine pada panggilan ini.
     *
     * @return array{hasil: list<array>, sidik_kb: ?string} sidik_kb null bila jawaban tidak memuat sidik yang sah
     */
    public function hitungDenganSidik(array $daftarKasus, bool $cekSilang = true, ?array $berkasTambahan = null): array
    {
        if ($daftarKasus === []) {
            return ['hasil' => [], 'sidik_kb' => null];
        }
        $jawab = $this->panggil(['perintah' => 'hitung', 'kasus' => array_values($daftarKasus), 'cek_silang' => $cekSilang,
            'berkas_tambahan' => $berkasTambahan ?? $this->kb->berkasAktif()]);
        if (! is_array($jawab['hasil'] ?? null) || count($jawab['hasil']) !== count($daftarKasus)) {
            throw new MesinTidakTersedia('jawaban engine tidak lengkap: jumlah hasil tidak sama dengan jumlah kasus');
        }
        // sama dengan KbTambahan::sidik: 16 hex, atau '' tanpa berkas tambahan (kolom sidik_kb varchar(16))
        $sidik = $jawab['sidik_kb'] ?? null;

        return ['hasil' => $jawab['hasil'], 'sidik_kb' => is_string($sidik) && preg_match('/^(?:[0-9a-f]{16})?$/', $sidik) ? $sidik : null];
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

    /** Isian tambahan yang diminta KB + metadata komponen gaji: {masukan: [...], komponen: [...]}. */
    public function masukan(?array $berkasTambahan = null): array
    {
        $jawab = $this->panggil(['perintah' => 'masukan', 'berkas_tambahan' => $berkasTambahan ?? $this->kb->berkasAktif()]);

        return ['masukan' => $jawab['masukan'], 'komponen' => $jawab['komponen']];
    }

    /**
     * Apakah KB bawaan + $berkasTambahan dapat dimuat dan dihitung engine: {ok, galat: [teks], tahun: [int]}.
     * Dipakai sebelum menonaktifkan berkas (berkas lain mungkin bergantung padanya) dan di halaman status engine.
     */
    public function periksa(?array $berkasTambahan = null): array
    {
        return $this->panggil(['perintah' => 'periksa', 'berkas_tambahan' => $berkasTambahan ?? $this->kb->berkasAktif()])['periksa'];
    }

    /**
     * PDF peraturan -> rancangan berkas KB lewat LLM, lalu divalidasi engine terhadap KB aktif.
     *
     * @return array{usulan: array, info: array, yaml: string, validasi: ?array}
     */
    public function usulkan(string $pathPdf, string $lapisan, ?string $catatan): array
    {
        $kunci = config('payroll.llm_kunci');
        $jawab = $this->panggil([
            'perintah' => 'usulkan', 'pdf' => $pathPdf, 'lapisan' => $lapisan, 'catatan' => (string) $catatan,
            'model' => config('payroll.llm_model'), 'berkas_tambahan' => $this->kb->berkasAktif(),
        ], config('payroll.llm_timeout'), $kunci ? [config('payroll.llm_kunci_env') => (string) $kunci] : []);

        return ['usulan' => $jawab['usulan'], 'info' => $jawab['info'], 'yaml' => $jawab['yaml'], 'validasi' => $jawab['validasi']];
    }

    /**
     * Validasi rancangan berkas KB (skema, verifikasi statis, simulasi dampak) terhadap berkas tambahan lain.
     * $lapisan = lapisan yang dipilih saat unggah; engine membandingkannya dengan lapisan yang tertulis di berkas.
     */
    public function validasi(string $yaml, string $nama, ?array $berkasTambahan = null, ?string $lapisan = null): array
    {
        $permintaan = ['perintah' => 'validasi', 'yaml' => $yaml, 'nama' => $nama,
            'berkas_tambahan' => $berkasTambahan ?? $this->kb->berkasAktif()];
        if ($lapisan !== null) {
            $permintaan['lapisan'] = $lapisan;
        }

        return $this->panggil($permintaan)['validasi'];
    }

    /** @param  array<string, string>  $env  variabel tambahan untuk proses ini (hanya `usulkan`: kunci API LLM) */
    private function panggil(array $permintaan, ?int $timeout = null, array $env = []): array
    {
        $python = config('payroll.python');
        $root = config('payroll.root');
        $perintah = (string) ($permintaan['perintah'] ?? '?');
        $mulai = hrtime(true);
        try {
            $hasil = Process::path($root)
                ->timeout($timeout ?? config('payroll.timeout'))
                ->env($env + ['PYTHONIOENCODING' => 'utf-8', 'PYTHONDONTWRITEBYTECODE' => '1'] + array_fill_keys(self::RAHASIA, false))
                ->input(json_encode($permintaan, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR))
                ->run([$python, '-m', 'jembatan']);
        } catch (ProcessTimedOutException $e) {
            self::catatGagal($perintah, null, $mulai, $e->result->errorOutput(), 'batas waktu habis');
            if ($perintah === 'usulkan') {
                throw $e;   // job ProsesUsulanKb memetakan batas waktu LLM ke pesannya sendiri
            }
            // perintah lain diperlakukan seperti engine yang tidak menjawab: setiap pemanggil yang menangani
            // MesinTidakTersedia menampilkan pesan, bukan galat 500
            throw new MesinTidakTersedia('engine melebihi batas waktu ('.($timeout ?? config('payroll.timeout')).' detik). Naikkan '
                .'PAYROLL_TIMEOUT'.($perintah === 'hitung' ? ', atau perkecil PAYROLL_UKURAN_BATCH untuk Hitung semua.' : '.'), 0, $e);
        }

        try {
            $jawab = json_decode($hasil->output(), true, 512, JSON_THROW_ON_ERROR);
        } catch (JsonException) {
            self::catatGagal($perintah, $hasil->exitCode(), $mulai, $hasil->errorOutput(), 'jawaban bukan JSON');
            $petunjuk = is_file($python) ? '' : " Python tidak ditemukan di '{$python}' (atur PAYROLL_PYTHON di .env).";
            // pesan untuk pengguna cukup satu baris; jejak (traceback) lengkap hanya di log
            $akhir = self::barisTerakhir($hasil->errorOutput());
            throw new MesinTidakTersedia("engine tidak memberi jawaban yang valid (kode keluar {$hasil->exitCode()}).{$petunjuk}"
                .($akhir !== '' ? " {$akhir}" : ''));
        }
        if (! ($jawab['ok'] ?? false)) {
            self::catatGagal($perintah, $hasil->exitCode(), $mulai, $hasil->errorOutput(), (string) ($jawab['jenis'] ?? 'galat'));
            throw new MesinTidakTersedia(($jawab['jenis'] ?? 'galat').': '.($jawab['pesan'] ?? 'tanpa pesan'));
        }

        return $jawab;
    }

    /** Jejak kegagalan untuk admin server. Isi permintaan (dokumen, data pegawai) dan lingkungan tidak pernah dicatat. */
    private static function catatGagal(string $perintah, ?int $kodeKeluar, int $mulai, string $stderr, string $sebab): void
    {
        Log::warning("Panggilan engine gagal: {$perintah}", [
            'perintah' => $perintah, 'sebab' => $sebab, 'kode_keluar' => $kodeKeluar,
            'durasi_ms' => intdiv(hrtime(true) - $mulai, 1_000_000), 'stderr' => mb_substr($stderr, -8000),
        ]);
    }

    /** Baris stderr terakhir yang berisi (biasanya galat Python, mis. "ModuleNotFoundError: ..."), paling banyak 200 karakter. */
    private static function barisTerakhir(string $stderr): string
    {
        $baris = preg_split('/\R/u', trim(mb_scrub($stderr, 'UTF-8'))) ?: [''];

        return mb_substr(trim(end($baris)), 0, 200);
    }
}
