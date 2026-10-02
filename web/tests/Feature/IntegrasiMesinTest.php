<?php

namespace Tests\Feature;

use App\Models\Payroll\Pegawai;
use App\Models\Payroll\Perhitungan;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Modules\Payroll\Services\ImporContoh;
use Modules\Payroll\Services\MesinPajak;
use Modules\Payroll\Services\PenyusunKasus;
use PHPUnit\Framework\Attributes\Group;
use Tests\TestCase;

/**
 * Integrasi nyata dengan engine Python di repositori induk (dilewati bila venv belum dibuat).
 *
 * Inti jaminannya: database -> kasus kanonik harus IDENTIK dengan kasus di dataset untuk semua pegawai contoh.
 * Engine dan KB tidak diubah, jadi angka yang ditampilkan aplikasi web mewarisi bukti verifikasi engine (V1-V3, E12).
 */
#[Group('mesin')]
class IntegrasiMesinTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        if (! is_file(config('payroll.python'))) {
            $this->markTestSkipped('Python venv induk tidak ditemukan: '.config('payroll.python'));
        }
    }

    private static function kanonik(mixed $x): mixed
    {
        if (! is_array($x)) {
            return $x;
        }
        if (! array_is_list($x)) {
            ksort($x);
        }

        return array_map(self::kanonik(...), $x);
    }

    public function test_kasus_dari_database_identik_dengan_dataset(): void
    {
        $contoh = collect(app(MesinPajak::class)->contoh())->keyBy('id');
        $this->assertCount(9, $contoh);
        app(ImporContoh::class)->jalankan();
        $this->assertSame([], app(ImporContoh::class)->jalankan(), 'impor kedua harus tidak membuat apa pun');

        foreach (Pegawai::with('payrollTahun.bulan')->get() as $p) {
            $pt = $p->payrollTahun->sole();
            $dariDb = json_decode(PenyusunKasus::json((new PenyusunKasus)->susun($pt)), true);
            $dataset = json_decode(json_encode($contoh[$p->nomor_induk]['kasus']), true);
            unset($dariDb['id'], $dataset['id'], $dataset['harapan']);
            $this->assertSame(self::kanonik($dataset), self::kanonik($dariDb), "kasus {$p->nomor_induk} berbeda dari dataset");
        }
    }

    public function test_hitung_lewat_web_sama_dengan_engine_langsung(): void
    {
        $this->masuk();
        app(ImporContoh::class)->jalankan();

        $this->post('/dashboard/hitung', ['tahun' => 2023])->assertSessionHas('success');
        $karA = Pegawai::firstWhere('nomor_induk', 'KAR-A')->payrollTahun->sole()->perhitunganTerakhir;
        // README induk: E8/E12 Karyawan A 2023; cek silang dengan kalkulator tanpa KB harus identik
        $this->assertSame(7_341_750, $karA->pph21_setahun);
        $this->assertSame('identik', $karA->cek_silang);

        $contoh = collect(app(MesinPajak::class)->contoh())->firstWhere('id', 'KAR-A');
        [$langsung] = app(MesinPajak::class)->hitung([$contoh['kasus']], false);
        $dariWeb = $karA->hasilEngine();
        $this->assertSame(json_encode($langsung['hasil']['per_masa']), json_encode($dariWeb['per_masa']));
        $this->assertSame(json_encode($langsung['hasil']['tahunan']), json_encode($dariWeb['tahunan']));

        $this->post('/dashboard/hitung', ['tahun' => 2026])->assertSessionHas('success');
        $this->assertSame(0, Perhitungan::where('berhasil', false)->count());
        $this->assertSame(['identik'], Perhitungan::distinct()->pluck('cek_silang')->all());
        $this->get('/mesin')->assertOk()->assertSee('Engine siap');
    }
}
