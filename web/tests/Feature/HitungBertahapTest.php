<?php

namespace Tests\Feature;

use App\Models\Payroll\PayrollTahun;
use App\Models\Payroll\Perhitungan;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Process\Exceptions\ProcessTimedOutException;
use Illuminate\Process\FakeProcessResult;
use Illuminate\Process\PendingProcess;
use Illuminate\Support\Facades\Process;
use Modules\Payroll\Services\KbTambahan;
use Modules\Payroll\Services\MesinPajak;
use Symfony\Component\Process\Exception\ProcessTimedOutException as SymfonyTimeout;
use Symfony\Component\Process\Process as SymfonyProcess;
use Tests\TestCase;

/**
 * Hitung semua per batch (payroll.ukuran_batch): satu panggilan engine dan satu transaksi per batch, sidik KB dari
 * jawaban engine, kegagalan engine di tengah jalan, dan pengaman angka per baris sebelum masuk kolom bigint.
 */
class HitungBertahapTest extends TestCase
{
    use RefreshDatabase;

    private static function berhasil(int $pph = 1_000_000, int $thpPerBulan = 9_500_000): array
    {
        $perMasa = [];
        foreach (range(1, 12) as $b) {
            $perMasa[$b] = ['px_gaji' => 10_000_000, 'bruto' => 10_500_000, 'pph21' => 157_500, 'px_thp' => $thpPerBulan];
        }

        return ['ok' => true, 'hasil' => ['per_masa' => $perMasa, 'tahunan' => ['bruto_setahun' => 126_000_000, 'pph21_setahun' => $pph],
            'jejak' => [], 'peringatan' => [], 'rincian_pasal17' => [], 'audit' => ['versi_engine' => '0.1.0', 'versi_kb' => 'abc']]];
    }

    /** Jembatan tiruan: panggilan ke-n dijawab $jawab(n, kasus) (jawaban JSON atau Throwable); id kasus per panggilan dicatat. */
    private function palsukan(callable $jawab, array &$panggilan): void
    {
        Process::fake(['*' => function (PendingProcess $p) use ($jawab, &$panggilan) {
            $kasus = json_decode($p->input, true)['kasus'];
            $panggilan[] = array_map(fn (array $k) => (int) substr($k['id'], strlen('PAYROLL-')), $kasus);
            $j = $jawab(count($panggilan), $kasus);

            return $j instanceof \Throwable ? $j : Process::result(output: json_encode($j));
        }]);
    }

    private static function semuaBerhasil(array $kasus, array $tambahan = []): array
    {
        return $tambahan + ['ok' => true, 'hasil' => array_map(fn () => self::berhasil(), $kasus)];
    }

    public function test_hitung_semua_per_batch_dicatat_dengan_sidik_kb_batchnya(): void
    {
        $this->masuk();
        config(['payroll.ukuran_batch' => 2]);
        foreach (range(1, 5) as $_) {
            $this->payroll(2025);
        }
        $panggilan = [];
        // sidik berbeda per panggilan: setiap baris harus memakai sidik dari jawaban batchnya sendiri
        $this->palsukan(fn (int $n, array $kasus) => self::semuaBerhasil($kasus, ['sidik_kb' => sprintf('%016x', $n)]), $panggilan);

        $this->post('/dashboard/hitung', ['tahun' => 2025])->assertSessionHas('success', '5 pegawai dihitung. Semua berhasil.');

        $this->assertSame([2, 2, 1], array_map('count', $panggilan));
        $this->assertSame(5, Perhitungan::count());
        foreach ($panggilan as $i => $ids) {
            foreach ($ids as $id) {
                $this->assertSame(sprintf('%016x', $i + 1), Perhitungan::where('payroll_tahun_id', $id)->sole()->sidik_kb);
            }
        }
        $this->get('/dashboard?tahun=2025')->assertOk()->assertSee('(2 pegawai per panggilan)');
    }

    public function test_engine_gagal_di_tengah_jalan_batch_sebelumnya_tetap_tercatat(): void
    {
        $this->masuk();
        config(['payroll.ukuran_batch' => 2]);
        foreach (range(1, 5) as $_) {
            $this->payroll(2025);
        }
        $panggilan = [];
        Process::fake(['*' => function (PendingProcess $p) use (&$panggilan) {
            $kasus = json_decode($p->input, true)['kasus'];
            $panggilan[] = count($kasus);

            return count($panggilan) === 1 ? Process::result(output: json_encode(self::semuaBerhasil($kasus)))
                : Process::result(output: '', errorOutput: "Traceback (most recent call last):\n  File \"jembatan/__main__.py\"\nMemoryError\n", exitCode: 1);
        }]);

        $this->post('/dashboard/hitung', ['tahun' => 2025])->assertRedirect()->assertSessionHas('error', fn (string $m) => str_starts_with($m,
            'Engine gagal setelah 2 dari 5 pegawai dihitung: engine tidak memberi jawaban yang valid (kode keluar 1).')
            && str_ends_with($m, ' MemoryError') && ! str_contains($m, "\n"));

        $this->assertSame([2, 2], $panggilan);   // batch ketiga tidak dicoba
        $this->assertSame(2, Perhitungan::where('berhasil', true)->count());
        $this->assertSame(2, Perhitungan::count());
    }

    public function test_batas_waktu_engine_menjadi_pesan_bukan_galat_500(): void
    {
        $this->masuk();
        config(['payroll.ukuran_batch' => 2, 'payroll.timeout' => 300]);
        $pt = $this->payroll(2025);
        $this->payroll(2025);
        $this->payroll(2025);
        $habis = fn () => new ProcessTimedOutException(new SymfonyTimeout(new SymfonyProcess(['python']), SymfonyTimeout::TYPE_GENERAL),
            new FakeProcessResult);
        $panggilan = [];
        $this->palsukan(fn (int $n, array $kasus) => $n === 1 ? self::semuaBerhasil($kasus) : $habis(), $panggilan);

        $this->post('/dashboard/hitung', ['tahun' => 2025])->assertRedirect()->assertSessionHas('error', fn (string $m) => str_starts_with($m,
            'Engine gagal setelah 2 dari 3 pegawai dihitung: engine melebihi batas waktu (300 detik).'));
        $this->assertSame(2, Perhitungan::count());

        // batch pertama sudah gagal: tidak ada yang tercatat
        Process::fake(['*' => fn () => $habis()]);
        $this->post('/dashboard/hitung', ['tahun' => 2025])
            ->assertSessionHas('error', fn (string $m) => str_starts_with($m, 'Engine tidak dapat dipanggil: engine melebihi batas waktu'));
        // satu pegawai (halaman payroll)
        $this->post("/payroll/{$pt->id}/hitung")->assertRedirect()
            ->assertSessionHas('error', fn (string $m) => str_starts_with($m, 'Engine tidak dapat dipanggil: engine melebihi batas waktu (300 detik).'));
        $this->assertSame(2, Perhitungan::count());
    }

    public function test_batas_waktu_perintah_lain_juga_menjadi_pesan(): void
    {
        $this->masuk();
        config(['payroll.timeout' => 300]);
        Process::fake(['*' => fn () => new ProcessTimedOutException(new SymfonyTimeout(new SymfonyProcess(['python']),
            SymfonyTimeout::TYPE_GENERAL), new FakeProcessResult)]);

        // halaman status engine (`info`) dulu galat 500 bila engine melewati batas waktu
        $this->get('/mesin')->assertOk()->assertSee('engine melebihi batas waktu (300 detik). Naikkan PAYROLL_TIMEOUT.');
    }

    public function test_angka_yang_tidak_muat_di_bigint_menggagalkan_baris_itu_saja(): void
    {
        $this->masuk();
        [$besar, $meluap, $normal] = [$this->payroll(2025), $this->payroll(2025), $this->payroll(2025)];
        $jawab = ['ok' => true, 'hasil' => [self::berhasil(), self::berhasil(thpPerBulan: 5_000_000_000_000_000_000), self::berhasil()]];
        $jawab['hasil'][0]['hasil']['tahunan']['bruto_setahun'] = 'BESAR';
        // integer di luar PHP_INT_MAX dibaca json_decode sebagai float; 12 x 5e18 meluap saat take home pay dijumlah
        Process::fake(['*' => Process::result(output: str_replace('"BESAR"', '99999999999999999999', json_encode($jawab)))]);

        $this->post('/dashboard/hitung', ['tahun' => 2025])->assertSessionHas('warning', '3 pegawai dihitung. 2 gagal; lihat kolom status.');

        $baris = fn (PayrollTahun $pt) => Perhitungan::where('payroll_tahun_id', $pt->id)->sole();
        foreach ([[$besar, 'bruto_setahun'], [$meluap, 'thp_setahun']] as [$pt, $kolom]) {
            $p = $baris($pt);
            $this->assertSame([false, 'nilai_di_luar_batas', null], [$p->berhasil, $p->jenis_galat, $p->hasil]);
            $this->assertStringContainsString($kolom, $p->pesan);
        }
        $this->assertTrue($baris($normal)->berhasil);
        $this->assertSame(12 * 9_500_000, $baris($normal)->thp_setahun);
        $this->getJson('/dashboard/list?tahun=2025')->assertOk()->assertSee('bruto_setahun bukan bilangan bulat');
    }

    public function test_hasil_yang_tidak_dapat_dijadikan_json_menggagalkan_baris_itu_saja(): void
    {
        $this->masuk();
        $a = $this->payroll(2024);
        $b = $this->payroll(2024);
        $rusak = self::berhasil();
        $rusak['hasil']['jejak'] = [NAN];
        app()->instance(MesinPajak::class, new class(app(KbTambahan::class), [$rusak, self::berhasil()]) extends MesinPajak
        {
            public function __construct(KbTambahan $kb, private array $jawab)
            {
                parent::__construct($kb);
            }

            public function hitungDenganSidik(array $daftarKasus, bool $cekSilang = true, ?array $berkasTambahan = null): array
            {
                return ['hasil' => array_slice($this->jawab, 0, count($daftarKasus)), 'sidik_kb' => null];
            }
        });

        $this->post('/dashboard/hitung', ['tahun' => 2024])->assertSessionHas('warning', '2 pegawai dihitung. 1 gagal; lihat kolom status.');
        $gagal = Perhitungan::where('payroll_tahun_id', $a->id)->sole();
        $this->assertSame(['hasil_tidak_valid', false], [$gagal->jenis_galat, $gagal->berhasil]);
        $this->assertStringContainsString('JSON', $gagal->pesan);
        $this->assertTrue(Perhitungan::where('payroll_tahun_id', $b->id)->sole()->berhasil);
        // jawaban tanpa sidik: sidik hitungan PHP ('' = tanpa berkas KB tambahan)
        $this->assertSame([''], Perhitungan::distinct()->pluck('sidik_kb')->all());
    }

    public function test_setiap_batch_memperpanjang_batas_waktu_php(): void
    {
        $this->masuk();
        config(['payroll.ukuran_batch' => 1, 'payroll.timeout' => 300]);
        $this->payroll(2025);
        $panggilan = [];
        $this->palsukan(fn (int $n, array $kasus) => self::semuaBerhasil($kasus), $panggilan);

        ini_set('max_execution_time', '30');   // seperti request web; di CLI bawaannya 0 (tanpa batas) dan tidak diubah
        try {
            $this->post('/dashboard/hitung', ['tahun' => 2025])->assertSessionHas('success');
            $this->assertSame('360', ini_get('max_execution_time'));
        } finally {
            set_time_limit(0);
        }
    }
}
