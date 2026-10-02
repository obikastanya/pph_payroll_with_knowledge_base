<?php

namespace Tests\Feature;

use App\Models\Kb\UsulanKb;
use App\Models\Payroll\Pegawai;
use App\Models\Payroll\Perhitungan;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\File;
use Modules\Payroll\Services\ImporContoh;
use Modules\Payroll\Services\KbTambahan;
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
            $dariDb = json_decode(PenyusunKasus::json(app(PenyusunKasus::class)->susun($pt)), true);
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

    /**
     * Aturan baru tanpa mengubah kode: berkas KB tambahan (uang transport per hari hadir, dengan isian baru) divalidasi
     * dan dimuat engine sungguhan, isiannya muncul di form, hasilnya ikut bruto/PPh/THP, dan menonaktifkannya
     * mengembalikan angka semula. LLM tidak dipanggil: rancangan ditulis langsung seperti hasil tinjauan admin.
     */
    public function test_berkas_kb_tambahan_dengan_isian_baru_dari_ujung_ke_ujung(): void
    {
        $dir = 'kb/tambahan/_uji_phpunit';
        config(['payroll.kb_tambahan_dir' => $dir]);
        $this->beforeApplicationDestroyed(fn () => File::deleteDirectory(config('payroll.root').'/'.$dir));
        $this->masuk();
        app(ImporContoh::class)->jalankan();
        $pt = Pegawai::firstWhere('nomor_induk', 'KAR-A')->payrollTahun->sole();
        $u = UsulanKb::create(['judul' => 'Peraturan Perusahaan (uji)', 'lapisan' => 'perusahaan', 'nama_pdf' => 'pp.pdf', 'path_pdf' => 'kb_usulan/pp.pdf',
            'ukuran_pdf' => 1, 'status' => 'siap_tinjau', 'usulan' => ['id_berkas' => 'transport_uji'], 'yaml' => <<<'YAML'
            lapisan: perusahaan
            id: transport_uji
            komponen:
              - {fakta: px_transport, jenis: tunjangan_transport, kategori: teratur, label: "Uang transport"}
            masukan:
              - {kunci: uang_transport_per_hari, label: "Uang transport per hari hadir", tipe: rupiah, lingkup: tahun, wajib: false, bawaan: 0, sumber: "PP Ps. 12"}
            aturan:
              - id: PPT-TRANSPORT-01
                sifat: opsional
                berlaku: {mulai: 2023-01-01}
                lingkup: masa
                menghasilkan: px_transport
                maka: "hr('uang_transport_per_hari') * hr_masa('hk_aktual')"
                tipe_hasil: rupiah
                sumber: "Peraturan Perusahaan (uji) Ps. 12"
            YAML]);

        // rancangan yang salah ditolak engine dan tidak pernah menjadi berkas KB
        $this->put("/kb/{$u->id}/yaml", ['yaml' => str_replace("hr('uang_transport_per_hari')", "hr('uang_makan')", $u->yaml)])->assertSessionHas('warning');
        $this->assertStringContainsString('belum dideklarasikan', implode(' ', $u->refresh()->validasi['galat']));
        $this->post("/kb/{$u->id}/terapkan")->assertSessionHas('error');
        $this->assertSame([], app(KbTambahan::class)->berkasAktif());

        $this->put("/kb/{$u->id}/yaml", ['yaml' => str_replace("hr('uang_makan')", "hr('uang_transport_per_hari')", $u->yaml)])->assertSessionHas('success');
        $this->post("/kb/{$u->id}/terapkan")->assertSessionHas('success');
        $this->assertFileExists(app(KbTambahan::class)->absolut($u->refresh()->nama_berkas));
        $this->assertSame(2023, $u->validasi['dampak'][0]['tahun']);

        // isian baru muncul di form data HR tanpa perubahan kode
        $this->get("/payroll/{$pt->id}/edit")->assertOk()->assertSee('Uang transport per hari hadir (Rp)');
        $pt->masukan()->create(['kunci' => 'uang_transport_per_hari', 'bulan' => 0, 'nilai' => 50_000]);
        $this->get("/payroll/{$pt->id}")->assertOk();
        $this->post("/payroll/{$pt->id}/hitung")->assertSessionHas('success');
        $p = $pt->perhitunganTerakhir()->first();
        $h = $p->hasilEngine();
        $hadirJan = $pt->bulan->firstWhere('bulan', 1)->hk_aktual;
        $this->assertSame(50_000 * $hadirJan, $h['per_masa'][1]['px_transport']);
        $this->assertGreaterThan(7_341_750, $p->pph21_setahun);
        $this->assertSame(['dilewati', app(KbTambahan::class)->sidik()], [$p->cek_silang, $p->sidik_kb]);
        $this->get("/payroll/{$pt->id}?tab=slip&bulan=1")->assertOk()->assertSee('Uang transport')->assertDontSee('Aturan knowledge base berubah');

        // dinonaktifkan: hasil lama ditandai usang, hitung ulang kembali ke angka semula dan cek silang identik
        $this->post("/kb/{$u->id}/aktif")->assertSessionHas('success');
        $this->get("/payroll/{$pt->id}")->assertOk()->assertSee('Aturan knowledge base berubah');
        $this->post("/payroll/{$pt->id}/hitung")->assertSessionHas('success');
        $p = $pt->perhitunganTerakhir()->first();
        $this->assertSame([7_341_750, 'identik', ''], [$p->pph21_setahun, $p->cek_silang, $p->sidik_kb]);
    }
}
