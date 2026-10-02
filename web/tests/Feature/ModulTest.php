<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\File;
use Illuminate\Support\Facades\Route;
use Tests\TestCase;

/** Struktur modules (pola Base-Apps-Merdeka): provider terdaftar otomatis, generator make:module, dashboard. */
class ModulTest extends TestCase
{
    use RefreshDatabase;

    public function test_route_dan_view_setiap_module_terdaftar(): void
    {
        foreach (['dashboard.index', 'dashboard.list', 'pegawai.index', 'pegawai.list', 'payroll.show', 'payroll.create', 'mesin.index'] as $nama) {
            $this->assertTrue(Route::has($nama), "route {$nama} belum terdaftar");
        }
        foreach (['Dashboard::index', 'Pegawai::index', 'Payroll::show', 'Mesin::index'] as $view) {
            $this->assertTrue(view()->exists($view), "view {$view} tidak ditemukan");
        }
    }

    public function test_make_module_membuat_kerangka(): void
    {
        $dasar = base_path('modules/UjiKerangka');
        try {
            $this->artisan('make:module', ['name' => 'UjiKerangka'])->assertSuccessful();
            foreach (['Http/Controllers/UjiKerangkaController.php', 'Http/Requests/UjiKerangkaRequest.php', 'Repositories/UjiKerangkaInterface.php',
                'Repositories/UjiKerangkaRepository.php', 'Providers/UjiKerangkaServiceProvider.php', 'Routes/web/uji-kerangka.php',
                'Resources/views/index.blade.php'] as $f) {
                $this->assertFileExists("{$dasar}/{$f}");
            }
            foreach (array_merge(glob("{$dasar}/*/*.php"), glob("{$dasar}/*/*/*.php")) as $f) {
                exec('php -l '.escapeshellarg($f), $out, $kode);
                $this->assertSame(0, $kode, "sintaks PHP tidak sah: {$f}");
            }
            $this->artisan('make:module', ['name' => 'UjiKerangka'])->assertFailed();
        } finally {
            File::deleteDirectory($dasar);
        }
    }

    public function test_dashboard_ringkasan_dan_daftar(): void
    {
        $this->masuk();
        $pt = $this->payroll(2024);
        $pt->perhitungan()->create(['berhasil' => true, 'kasus' => 'kasus-lama', 'hasil' => '{}', 'cek_silang' => 'identik',
            'bruto_setahun' => 120_000_000, 'pph21_setahun' => 3_000_000, 'thp_setahun' => 100_000_000]);

        $this->get('/dashboard?tahun=2024')->assertOk()
            ->assertSee('Total PPh 21 setahun')->assertSee('Rp3.000.000')->assertSee('Rp120.000.000')->assertSee('Tahun pajak 2024');
        $this->getJson('/dashboard/list?tahun=2024')->assertOk()
            ->assertJsonPath('meta.total', 1)
            ->assertJsonPath('data.0.pph21_setahun', 3_000_000)
            ->assertJsonPath('data.0.cek_silang', 'identik')
            ->assertJsonPath('data.0.status', 'kedaluwarsa');   // kasus tersimpan berbeda dengan data HR sekarang
        $this->getJson('/dashboard/list?tahun=2024&search=tidak-ada')->assertJsonPath('meta.total', 0);
    }
}
