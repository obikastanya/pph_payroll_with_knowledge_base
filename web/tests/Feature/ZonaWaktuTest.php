<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Process;
use Tests\TestCase;

/** Zona waktu aplikasi berasal dari APP_TIMEZONE; uji dipaksa UTC (phpunit.xml) agar tidak mengikuti .env pengembang. */
class ZonaWaktuTest extends TestCase
{
    use RefreshDatabase;

    public function test_zona_waktu_uji_utc_dan_tampil_di_halaman_mesin(): void
    {
        $this->assertSame('UTC', config('app.timezone'));
        $this->assertSame('UTC', date_default_timezone_get());

        $this->masuk();
        Process::fake(['*' => Process::result(output: '', exitCode: 1)]);
        $this->travelTo('2026-10-03 04:05:00');
        $this->get('/mesin')->assertOk()->assertSeeInOrder(['Zona waktu aplikasi (APP_TIMEZONE)', 'UTC · sekarang 03/10/2026 04:05'])
            ->assertDontSee('tidak sah');
    }

    /** Singkatan (WITA), nilai kosong, dan salah ketik ditolak PHP: konfigurasi jatuh ke UTC, nama IANA diterima. */
    public function test_app_timezone_tidak_sah_jatuh_ke_utc(): void
    {
        foreach (['WITA' => 'UTC', '' => 'UTC', 'Asia/Makasar' => 'UTC', 'true' => 'UTC', 'Asia/Makassar' => 'Asia/Makassar', 'UTC' => 'UTC'] as $isi => $harap) {
            $konfigurasi = $this->konfigurasiDengan((string) $isi);
            $this->assertSame($harap, $konfigurasi['timezone'], "APP_TIMEZONE={$isi}");
            // nama yang lolos harus benar-benar diterima PHP
            $this->assertNotFalse(@timezone_open($konfigurasi['timezone']));
        }
        $this->assertSame('WITA', $this->konfigurasiDengan('WITA')['timezone_diminta']);
    }

    public function test_halaman_mesin_menandai_app_timezone_yang_ditolak(): void
    {
        $this->masuk();
        Process::fake(['*' => Process::result(output: '', exitCode: 1)]);
        $this->travelTo('2026-10-03 04:05:00');

        // zona aktif tetap UTC (nilai tidak sah tidak pernah sampai ke PHP); halaman tidak boleh menulis "WITA · sekarang"
        config(['app.timezone_diminta' => 'WITA']);
        $this->get('/mesin')->assertOk()
            ->assertSeeInOrder(['UTC · sekarang 03/10/2026 04:05', 'APP_TIMEZONE=WITA tidak sah', 'dipakai UTC'])
            ->assertDontSee('WITA · sekarang');

        config(['app.timezone_diminta' => '']);
        $this->get('/mesin')->assertOk()->assertSee('APP_TIMEZONE=(kosong) tidak sah');
    }

    /** Memuat ulang config/app.php dengan APP_TIMEZONE tertentu, lalu memulihkan lingkungan uji. */
    private function konfigurasiDengan(string $isi): array
    {
        $lama = [$_ENV['APP_TIMEZONE'] ?? null, $_SERVER['APP_TIMEZONE'] ?? null];
        $_ENV['APP_TIMEZONE'] = $_SERVER['APP_TIMEZONE'] = $isi;
        try {
            return require config_path('app.php');
        } finally {
            foreach (['_ENV', '_SERVER'] as $i => $nama) {
                if ($lama[$i] === null) {
                    unset($GLOBALS[$nama]['APP_TIMEZONE']);
                } else {
                    $GLOBALS[$nama]['APP_TIMEZONE'] = $lama[$i];
                }
            }
        }
    }
}
