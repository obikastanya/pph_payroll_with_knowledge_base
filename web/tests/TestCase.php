<?php

namespace Tests;

use App\Models\Payroll\PayrollTahun;
use App\Models\Payroll\Pegawai;
use App\Models\User;
use Illuminate\Foundation\Testing\TestCase as BaseTestCase;

abstract class TestCase extends BaseTestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        $this->withoutVite();
    }

    /**
     * Dijalankan sebelum trait (RefreshDatabase) sempat mengosongkan database. Dengan konfigurasi ter-cache
     * (php artisan config:cache) nilai env dari phpunit.xml diabaikan, sehingga uji akan menghapus database aplikasi.
     */
    protected function setUpTraits()
    {
        $this->pastikanDatabaseUji();

        return parent::setUpTraits();
    }

    protected function pastikanDatabaseUji(): void
    {
        $nama = config('database.default');
        $koneksi = config("database.connections.{$nama}", []);
        $driver = $koneksi['driver'] ?? '?';
        $database = (string) ($koneksi['database'] ?? '');
        $sqliteMemori = $driver === 'sqlite' && $database === ':memory:';
        $pgsqlUji = (string) env('PAYROLL_UJI_PGSQL') === '1' && str_ends_with($database, '_uji');
        if (! $sqliteMemori && ! $pgsqlUji) {
            $this->fail("Uji dihentikan: koneksi database uji adalah {$driver} '{$database}', bukan SQLite :memory:. Menjalankan uji "
                .'di sini akan mengosongkan database aplikasi. Hapus konfigurasi ter-cache (php artisan config:clear) lalu ulangi; '
                .'untuk uji PostgreSQL pakai phpunit.pgsql.xml (database berakhiran _uji).');
        }
    }

    protected function masuk(): User
    {
        $user = User::factory()->create();
        $this->actingAs($user);

        return $user;
    }

    /** Pegawai bekerja penuh di $tahun dengan data HR lengkap 12 bulan (22 hari kerja, hadir penuh). */
    protected function payroll(int $tahun = 2024, array $tahunan = [], array $pegawai = []): PayrollTahun
    {
        $p = Pegawai::create($pegawai + [
            'nomor_induk' => 'P-'.fake()->unique()->numerify('####'), 'nama' => 'Pegawai Uji', 'jenis_kelamin' => 'L',
            'punya_npwp' => true, 'tanggal_masuk' => '2020-01-01',
        ]);
        $pt = $p->payrollTahun()->create($tahunan + [
            'tahun' => $tahun, 'status_ptkp' => 'TK/0', 'metode' => 'gross', 'gaji_pokok' => 10_000_000,
            'kenaikan_tanggal' => "{$tahun}-01-01", 'tanggal_lebaran' => "{$tahun}-04-10", 'tanggal_thr_bayar' => "{$tahun}-04-03",
            'bpjs_tk_mulai_bulan' => 1, 'bpjs_kes_mulai_bulan' => 1, 'kelas_jkk_persen' => '0.24',
        ]);
        foreach (range(1, 12) as $b) {
            $pt->bulan()->create(['bulan' => $b, 'hk_penuh' => 22, 'hk_aktual' => 22]);
        }

        return $pt->fresh(['pegawai', 'bulan']);
    }

    /** Isian form data HR yang sah untuk $tahun (12 bulan, hadir penuh). */
    protected function isianPayroll(int $tahun = 2024, array $timpa = []): array
    {
        $bulan = [];
        foreach (range(1, 12) as $b) {
            $bulan[$b] = ['hk_penuh' => 22, 'hk_aktual' => 22];
        }

        return array_replace_recursive([
            'tahun' => $tahun, 'status_ptkp' => 'K/1', 'metode' => 'gross', 'gaji_pokok' => 12_000_000, 'kenaikan_nominal' => 0,
            'kenaikan_tanggal' => "{$tahun}-01-01", 'tanggal_lebaran' => "{$tahun}-04-10", 'tanggal_thr_bayar' => "{$tahun}-04-03",
            'bpjs_tk_mulai_bulan' => 1, 'bpjs_kes_mulai_bulan' => 1, 'kelas_jkk_persen' => '0,24', 'bulan' => $bulan,
        ], $timpa);
    }
}
