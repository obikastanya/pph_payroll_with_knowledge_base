<?php

namespace Tests\Feature;

use App\Models\Payroll\Perhitungan;
use Illuminate\Contracts\Process\ProcessResult;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Process\PendingProcess;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Process;
use Modules\Payroll\Services\KunciHitungSemua;
use Tests\TestCase;

/**
 * Kunci Hitung semua per tahun pajak (KunciHitungSemua): permintaan kedua ditolak tanpa memanggil engine, kunci
 * diperpanjang sebelum setiap batch dan dilepas setelah selesai atau gagal; perintah `payroll:hitung` memakai kunci yang sama.
 */
class KunciHitungSemuaTest extends TestCase
{
    use RefreshDatabase;

    /**
     * Jembatan tiruan: semua kasus berhasil. $saatDipanggil(n) dijalankan di dalam panggilan engine ke-n; bila
     * mengembalikan jawaban proses, jawaban itu yang dipakai.
     */
    private function palsukan(?callable $saatDipanggil = null): void
    {
        $n = 0;
        Process::fake(['*' => function (PendingProcess $p) use ($saatDipanggil, &$n) {
            $ganti = $saatDipanggil ? $saatDipanggil(++$n) : null;
            if ($ganti !== null) {
                return $ganti;
            }
            $satu = ['ok' => true, 'hasil' => ['per_masa' => [1 => ['px_thp' => 9_500_000]],
                'tahunan' => ['bruto_setahun' => 126_000_000, 'pph21_setahun' => 1_000_000],
                'jejak' => [], 'peringatan' => [], 'rincian_pasal17' => [], 'audit' => ['versi_engine' => '0.1.0', 'versi_kb' => 'abc']]];

            return Process::result(output: json_encode(['ok' => true,
                'hasil' => array_map(fn () => $satu, json_decode($p->input, true)['kasus'])]));
        }]);
    }

    private static function gagal(): ProcessResult
    {
        return Process::result(output: '', errorOutput: "MemoryError\n", exitCode: 1);
    }

    public function test_permintaan_kedua_saat_kunci_dipegang_ditolak_tanpa_memanggil_engine(): void
    {
        $this->masuk();
        config(['payroll.timeout' => 300]);
        $this->payroll(2025);
        $this->payroll(2024);
        $this->palsukan();
        $this->assertNotNull(KunciHitungSemua::ambil(2025));   // proses lain sedang menghitung 2025

        $this->post('/dashboard/hitung', ['tahun' => 2025])->assertRedirect()->assertSessionHas('warning',
            'Hitung semua tahun 2025 masih berjalan di proses lain; tunggu sampai selesai. Kunci yang tertinggal '
            .'(proses terhenti) lepas sendiri paling lama 420 detik.');
        Process::assertNothingRan();
        $this->assertSame(0, Perhitungan::count());
        $this->assertTrue(Cache::has('hitung-semua:2025'));   // kunci proses lain tidak ikut dilepas

        // kunci berlaku per tahun pajak
        $this->post('/dashboard/hitung', ['tahun' => 2024])->assertSessionHas('success', '1 pegawai dihitung. Semua berhasil.');

        // kunci yang tertinggal lepas sendiri setelah masa berlakunya (payroll.timeout + 120 detik)
        $this->travel(421)->seconds();
        $this->post('/dashboard/hitung', ['tahun' => 2025])->assertSessionHas('success', '1 pegawai dihitung. Semua berhasil.');
    }

    public function test_kunci_dilepas_setelah_berhasil_dan_setelah_engine_terhenti(): void
    {
        $this->masuk();
        $this->payroll(2025);
        $dipegang = [];
        $this->palsukan(function () use (&$dipegang) {
            $dipegang[] = Cache::has('hitung-semua:2025');
        });

        $this->post('/dashboard/hitung', ['tahun' => 2025])->assertSessionHas('success');
        $this->assertSame([true], $dipegang);   // selama engine bekerja kunci dipegang
        $this->assertFalse(Cache::has('hitung-semua:2025'));

        $this->palsukan(fn () => self::gagal());
        $this->post('/dashboard/hitung', ['tahun' => 2025])
            ->assertSessionHas('error', fn (string $m) => str_starts_with($m, 'Engine tidak dapat dipanggil: '));
        $this->assertFalse(Cache::has('hitung-semua:2025'));

        // satu pegawai (halaman payroll) tidak memakai kunci
        $this->palsukan();
        $this->assertNotNull(KunciHitungSemua::ambil(2025));
        $this->post('/payroll/'.$this->payroll(2025)->id.'/hitung')->assertSessionMissing('warning')->assertSessionMissing('error');
        $this->assertSame(2, Perhitungan::count());
    }

    public function test_kunci_diperpanjang_sebelum_setiap_batch(): void
    {
        $this->masuk();
        config(['payroll.ukuran_batch' => 1, 'payroll.timeout' => 300]);
        foreach (range(1, 3) as $_) {
            $this->payroll(2025);
        }
        $dipegang = [];
        // setiap batch memakan 400 dari 420 detik masa berlaku: tanpa perpanjangan kunci sudah habis di batch ketiga
        $this->palsukan(function () use (&$dipegang) {
            $dipegang[] = Cache::has('hitung-semua:2025');
            $this->travel(400)->seconds();
        });

        $this->post('/dashboard/hitung', ['tahun' => 2025])->assertSessionHas('success', '3 pegawai dihitung. Semua berhasil.');
        $this->assertSame([true, true, true], $dipegang);
        $this->assertFalse(Cache::has('hitung-semua:2025'));
    }

    public function test_kunci_bertoken_asing_tidak_dilepas(): void
    {
        $this->masuk();
        $this->payroll(2025);
        // kunci kita kedaluwarsa di tengah jalan lalu diambil proses lain
        $this->palsukan(function () {
            Cache::put('hitung-semua:2025', 'token-proses-lain', 600);
        });

        $this->post('/dashboard/hitung', ['tahun' => 2025])->assertSessionHas('success');
        $this->assertSame('token-proses-lain', Cache::get('hitung-semua:2025'));
    }

    public function test_perintah_artisan_menghitung_per_batch_dan_melepas_kunci(): void
    {
        config(['payroll.ukuran_batch' => 2]);
        foreach (range(1, 3) as $_) {
            $this->payroll(2025);
        }
        $this->palsukan();

        $this->artisan('payroll:hitung', ['tahun' => '2025'])
            ->expectsOutput('0 dari 3 pegawai tercatat ...')
            ->expectsOutput('2 dari 3 pegawai tercatat ...')
            ->expectsOutput('Tahun 2025: 3 pegawai dihitung, 0 gagal.')
            ->assertExitCode(0);

        $this->assertSame(3, Perhitungan::whereNull('user_id')->where('berhasil', true)->count());
        $this->assertFalse(Cache::has('hitung-semua:2025'));
    }

    public function test_perintah_artisan_gagal_bila_kunci_dipegang_tahun_tidak_sah_atau_tanpa_data(): void
    {
        config(['payroll.timeout' => 300]);
        $this->payroll(2025);
        $this->palsukan();
        $this->assertNotNull(KunciHitungSemua::ambil(2025));

        $this->artisan('payroll:hitung', ['tahun' => '2025'])
            ->expectsOutputToContain('Hitung semua tahun 2025 masih berjalan di proses lain')->assertExitCode(1);
        foreach (['2022', '2027', 'abc'] as $tahun) {
            $this->artisan('payroll:hitung', ['tahun' => $tahun])->expectsOutput('Tahun pajak tidak valid (pilih 2023–2026).')->assertExitCode(1);
        }
        $this->artisan('payroll:hitung', ['tahun' => '2024'])->expectsOutput('Belum ada data HR untuk tahun 2024.')->assertExitCode(1);

        Process::assertNothingRan();
        $this->assertSame(0, Perhitungan::count());
        $this->assertTrue(Cache::has('hitung-semua:2025'));
    }

    public function test_perintah_artisan_gagal_bila_engine_terhenti_di_tengah_jalan(): void
    {
        config(['payroll.ukuran_batch' => 2]);
        foreach (range(1, 3) as $_) {
            $this->payroll(2025);
        }
        $this->palsukan(fn (int $n) => $n === 1 ? null : self::gagal());

        $this->artisan('payroll:hitung', ['tahun' => '2025'])
            ->expectsOutputToContain('Engine gagal setelah 2 dari 3 pegawai tercatat: ')->assertExitCode(1);

        $this->assertSame(2, Perhitungan::count());
        $this->assertFalse(Cache::has('hitung-semua:2025'));
    }
}
