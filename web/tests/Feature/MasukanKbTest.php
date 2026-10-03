<?php

namespace Tests\Feature;

use App\Models\Payroll\PayrollMasukan;
use App\Models\Payroll\Perhitungan;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Process\PendingProcess;
use Illuminate\Support\Facades\File;
use Illuminate\Support\Facades\Process;
use Modules\Payroll\Http\Controllers\PayrollController;
use Modules\Payroll\Services\KbTambahan;
use Modules\Payroll\Services\PenyusunKasus;
use Modules\Payroll\Services\SkemaMasukan;
use Tests\Concerns\KbUji;
use Tests\TestCase;

/**
 * Isian tambahan yang diminta berkas KB: form data HR menampilkannya dari deklarasi `masukan` (tanpa kode khusus per
 * aturan), nilainya divalidasi menurut tipe, disimpan, dan dikirim ke engine di `data_hr`.
 */
class MasukanKbTest extends TestCase
{
    use KbUji, RefreshDatabase;

    private static function skema(array ...$masukan): array
    {
        return ['ok' => true, 'sidik_kb' => 'x', 'masukan' => $masukan,
            'komponen' => [['fakta' => 'px_gaji', 'jenis' => 'gaji', 'kategori' => 'teratur', 'label' => null, 'berkas' => 'perusahaan_x.yaml'],
                ['fakta' => 'px_transport', 'jenis' => 'tunjangan_transport', 'kategori' => 'teratur', 'label' => 'Uang transport', 'berkas' => '0001_transport_2026.yaml']]];
    }

    public function test_tanpa_berkas_tambahan_form_dan_kasus_tidak_berubah(): void
    {
        $this->masuk();
        Process::fake();
        $pt = $this->payroll(2026);

        $this->get("/payroll/{$pt->id}/edit")->assertOk()->assertDontSee('Isian tambahan dari knowledge base');
        $this->assertArrayNotHasKey('uang_transport_per_hari', app(PenyusunKasus::class)->susun($pt)['data_hr']);
        Process::assertNothingRan();   // skema kosong tidak perlu memanggil engine
    }

    public function test_isian_tahunan_tampil_disimpan_dan_dikirim_ke_engine(): void
    {
        $this->masuk();
        $this->kbAktif();
        $this->palsukanJembatan(['masukan' => self::skema(self::masukanTransport())]);
        $pt = $this->payroll(2026);
        $lama = $this->payroll(2024);

        $this->get("/payroll/{$pt->id}/edit")->assertOk()->assertSee('Isian tambahan dari knowledge base')
            ->assertSee('Uang transport per hari hadir (Rp)')->assertSee('name="masukan[uang_transport_per_hari]"', false)->assertSee('PP 2026 Ps. 12');
        // aturan baru berlaku 1 Juli 2026: data HR 2024 tidak diminta isian ini
        $this->get("/payroll/{$lama->id}/edit")->assertOk()->assertDontSee('Uang transport per hari hadir');

        $this->put("/payroll/{$pt->id}", $this->isianPayroll(2026, ['masukan' => ['uang_transport_per_hari' => 'banyak']]))
            ->assertSessionHasErrors('masukan.uang_transport_per_hari');
        $this->put("/payroll/{$pt->id}", $this->isianPayroll(2026, ['masukan' => ['uang_transport_per_hari' => '25000']]))->assertSessionHasNoErrors();

        $this->assertSame(25_000, PayrollMasukan::sole()->nilai);
        $kasus = app(PenyusunKasus::class)->susun($pt->fresh());
        $this->assertSame(25_000, $kasus['data_hr']['uang_transport_per_hari']);
        $this->assertSame(12_000_000, $kasus['data_hr']['gaji_pokok']);
        $this->get("/payroll/{$pt->id}/edit")->assertSee('value="25000"', false);

        // dikosongkan -> baris dihapus, engine memakai nilai bawaan deklarasi
        $this->put("/payroll/{$pt->id}", $this->isianPayroll(2026, ['masukan' => ['uang_transport_per_hari' => '']]))->assertSessionHasNoErrors();
        $this->assertSame(0, PayrollMasukan::count());
        $this->assertArrayNotHasKey('uang_transport_per_hari', app(PenyusunKasus::class)->susun($pt->fresh())['data_hr']);
        Process::assertRanTimes(fn (PendingProcess $p) => json_decode($p->input, true)['perintah'] === 'masukan', 1);   // skema di-cache per sidik
    }

    public function test_isian_wajib_dan_tipe_lain(): void
    {
        $this->masuk();
        $this->kbAktif();
        $this->palsukanJembatan(['masukan' => self::skema(
            self::masukanTransport(['wajib' => true, 'bawaan' => null, 'mulai' => '2024-01-01']),
            self::masukanTransport(['kunci' => 'persen_bonus', 'label' => 'Bonus tahunan', 'tipe' => 'persen', 'mulai' => '2024-01-01', 'bawaan' => null]),
            self::masukanTransport(['kunci' => 'ikut_dplk', 'label' => 'Ikut DPLK', 'tipe' => 'ya_tidak', 'mulai' => '2024-01-01', 'bawaan' => false]),
            self::masukanTransport(['kunci' => 'golongan', 'label' => 'Golongan', 'tipe' => 'pilihan', 'pilihan' => ['A', 'B'], 'mulai' => '2024-01-01', 'bawaan' => null]),
            self::masukanTransport(['kunci' => 'tanggal_kontrak', 'label' => 'Tanggal kontrak', 'tipe' => 'tanggal', 'mulai' => '2024-01-01', 'bawaan' => null]),
        )]);
        $pegawai = $this->payroll(2025)->pegawai;

        $this->get("/pegawai/{$pegawai->id}/payroll/create?tahun=2024")->assertOk()->assertSee('Bonus tahunan (%)')->assertSee('Ikut DPLK')->assertSee('Golongan');
        $this->post("/pegawai/{$pegawai->id}/payroll", $this->isianPayroll(2024))->assertSessionHasErrors('masukan.uang_transport_per_hari');
        $this->post("/pegawai/{$pegawai->id}/payroll", $this->isianPayroll(2024, ['masukan' => ['uang_transport_per_hari' => 30000, 'persen_bonus' => '12,50',
            'ikut_dplk' => '1', 'golongan' => 'C', 'tanggal_kontrak' => '31-12-2024']]))
            ->assertSessionHasErrors(['masukan.golongan', 'masukan.tanggal_kontrak'])->assertSessionDoesntHaveErrors(['masukan.persen_bonus', 'masukan.ikut_dplk']);

        $this->post("/pegawai/{$pegawai->id}/payroll", $this->isianPayroll(2024, ['masukan' => ['uang_transport_per_hari' => 30000, 'persen_bonus' => '12,50',
            'ikut_dplk' => '1', 'golongan' => 'B', 'tanggal_kontrak' => '2024-12-31']]))->assertSessionHasNoErrors();
        $pt = $pegawai->payrollTahun()->where('tahun', 2024)->sole();
        $hr = app(PenyusunKasus::class)->susun($pt)['data_hr'];
        $this->assertSame([30_000, '12.5', true, 'B', '2024-12-31'],
            [$hr['uang_transport_per_hari'], $hr['persen_bonus'], $hr['ikut_dplk'], $hr['golongan'], $hr['tanggal_kontrak']]);
    }

    public function test_isian_bulanan_hanya_untuk_bulan_aturan_berlaku(): void
    {
        $this->masuk();
        $this->kbAktif();
        $this->palsukanJembatan(['masukan' => self::skema(
            self::masukanTransport(['kunci' => 'hari_dinas', 'label' => 'Hari dinas luar', 'tipe' => 'bilangan', 'lingkup' => 'bulan', 'wajib' => true, 'bawaan' => null]),
        )]);
        $pt = $this->payroll(2026);

        $this->get("/payroll/{$pt->id}/edit")->assertOk()->assertSee('Hari dinas luar')
            ->assertSee('name="masukan_bulan[7][hari_dinas]"', false)->assertDontSee('name="masukan_bulan[6][hari_dinas]"', false);
        $this->put("/payroll/{$pt->id}", $this->isianPayroll(2026))->assertSessionHasErrors(['masukan_bulan.7.hari_dinas', 'masukan_bulan.12.hari_dinas'])
            ->assertSessionDoesntHaveErrors(['masukan_bulan.6.hari_dinas']);

        $isi = [];
        foreach (range(1, 12) as $b) {
            $isi[$b] = ['hari_dinas' => $b];   // Jan-Jun dikirim tetapi aturan belum berlaku -> diabaikan
        }
        $this->put("/payroll/{$pt->id}", $this->isianPayroll(2026, ['masukan_bulan' => $isi]))->assertSessionHasNoErrors();
        $this->assertSame(range(7, 12), PayrollMasukan::orderBy('bulan')->pluck('bulan')->all());
        $perMasa = app(PenyusunKasus::class)->susun($pt->fresh())['data_hr']['per_masa'];
        $this->assertSame(9, $perMasa['9']['hari_dinas']);
        $this->assertArrayNotHasKey('hari_dinas', $perMasa['6']);
        $this->assertSame(22, $perMasa['9']['hk_aktual']);
    }

    public function test_hitung_mengirim_berkas_tambahan_dan_menandai_hasil_usang_saat_kb_berubah(): void
    {
        $this->masuk();
        $u = $this->kbAktif();
        $pt = $this->payroll(2026);
        $pt->masukan()->create(['kunci' => 'uang_transport_per_hari', 'bulan' => 0, 'nilai' => 25_000]);
        $perMasa = [];
        foreach (range(1, 12) as $b) {
            $perMasa[$b] = ['px_gaji' => 10_000_000, 'bruto' => 10_500_000, 'pph21' => 157_500, 'px_thp' => 9_500_000] + ($b >= 7 ? ['px_transport' => 550_000] : []);
        }
        $skema = self::skema(self::masukanTransport());
        $this->palsukanJembatan(['masukan' => $skema, 'hitung' => ['ok' => true, 'sidik_kb' => 'x', 'hasil' => [['ok' => true,
            'cek_silang' => ['status' => 'dilewati', 'selisih' => [], 'pesan' => 'ada berkas KB tambahan'],
            'hasil' => ['per_masa' => $perMasa, 'tahunan' => ['bruto_setahun' => 129_300_000, 'pph21_setahun' => 2_000_000], 'jejak' => [], 'peringatan' => [],
                'rincian_pasal17' => [], 'komponen' => $skema['komponen'], 'audit' => ['versi_engine' => '0.1.0', 'versi_kb' => 'abc']]]]]]);

        $this->post("/payroll/{$pt->id}/hitung")->assertSessionHas('success');
        $p = Perhitungan::sole();
        $this->assertSame(app(KbTambahan::class)->sidik(), $p->sidik_kb);
        $this->assertSame('dilewati', $p->cek_silang);
        Process::assertRan(function (PendingProcess $proses) {
            $permintaan = json_decode($proses->input, true);

            return $permintaan['perintah'] === 'hitung' && $permintaan['berkas_tambahan'] === ['kb/tambahan/0001_transport_2026.yaml']
                && $permintaan['kasus'][0]['data_hr']['uang_transport_per_hari'] === 25_000;
        });

        // komponen baru tampil di slip dengan label dari deklarasi KB, tanpa perubahan kode tampilan
        $this->get("/payroll/{$pt->id}?tab=slip&bulan=7")->assertOk()->assertSee('Uang transport')->assertSee('550.000')
            ->assertDontSee('Aturan knowledge base berubah');
        $this->get("/payroll/{$pt->id}?tab=slip&bulan=6")->assertOk()->assertDontSee('Uang transport');
        // kolom tetap tidak bergeser; komponen dari berkas tambahan menyusul di akhir (komponen dasar tidak ditambahkan)
        $csv = $this->get("/payroll/{$pt->id}/ekspor")->streamedContent();
        $this->assertStringStartsWith('bulan,'.implode(',', PayrollController::KOLOM_CSV).",px_transport\n", $csv);
        $this->get("/payroll/{$pt->id}/slip/7")->assertOk()->assertSee('+ berkas KB tambahan '.$p->sidik_kb)->assertDontSee('Hasil usang');

        // berkas KB dinonaktifkan -> hasil lama dihitung dengan aturan yang tidak lagi berlaku
        $u->update(['aktif' => false]);
        $this->get("/payroll/{$pt->id}")->assertOk()->assertSee('Aturan knowledge base berubah');
        $this->getJson('/dashboard/list?tahun=2026')->assertJsonPath('data.0.status', 'kedaluwarsa')->assertJsonPath('data.0.alasan', 'kb');
        $this->get("/payroll/{$pt->id}/slip/7")->assertOk()->assertSee('Hasil usang: aturan knowledge base berubah');
        $rekap = array_map('str_getcsv', explode("\n", trim($this->get('/dashboard/ekspor?tahun=2026')->streamedContent())));
        $this->assertSame(['usang (aturan KB)', $p->sidik_kb], array_slice($rekap[1], 11, 2));
    }

    public function test_kolom_csv_komponen_tambahan_di_akhir_urut_deklarasi(): void
    {
        $kolom = PayrollController::kolomCsv(['komponen' => [
            ['fakta' => 'px_gaji', 'kategori' => 'teratur', 'berkas' => 'perusahaan_x.yaml'],
            ['fakta' => 'px_premi_jht_pk', 'kategori' => 'bukan_objek', 'berkas' => 'perusahaan_x.yaml'],
            ['fakta' => 'px_premi_jp_pk', 'kategori' => 'bukan_objek'],   // hasil tanpa `berkas`: tetap dikenali sebagai dasar
            ['fakta' => 'zz_transport', 'kategori' => 'teratur', 'berkas' => '0001_a.yaml'],
            ['fakta' => 'aa_koperasi', 'kategori' => 'tidak_diperhitungkan', 'berkas' => '0002_b.yaml'],
        ]]);

        $this->assertSame([...PayrollController::KOLOM_CSV, 'zz_transport', 'aa_koperasi'], $kolom);
    }

    public function test_aturan_mulai_tengah_bulan_mengikuti_tanggal_evaluasi_engine(): void
    {
        $m = ['mulai' => '2026-07-15', 'sampai' => null];
        $this->assertFalse(SkemaMasukan::berlakuBulan($m, 2026, 7));   // engine menilai 1 Juli: aturan belum berlaku
        $this->assertTrue(SkemaMasukan::berlakuBulan($m, 2026, 8));
        $s = ['mulai' => '2026-01-01', 'sampai' => '2026-03-20'];
        $this->assertTrue(SkemaMasukan::berlakuBulan($s, 2026, 3));
        $this->assertFalse(SkemaMasukan::berlakuBulan($s, 2026, 4));
        $this->assertTrue(SkemaMasukan::berlakuBulan(['mulai' => null, 'sampai' => null], 2026, 1));

        $this->assertFalse(SkemaMasukan::berlakuTahun(['mulai' => '2026-12-15', 'sampai' => null], 2026));   // tidak ada masa yang memakainya
        $this->assertTrue(SkemaMasukan::berlakuTahun(['mulai' => '2026-12-01', 'sampai' => null], 2026));
        $this->assertTrue(SkemaMasukan::berlakuTahun(['mulai' => '2026-12-15', 'sampai' => null], 2027));
        $this->assertTrue(SkemaMasukan::berlakuTahun(['mulai' => '2020-01-01', 'sampai' => '2026-01-01'], 2026));
        $this->assertFalse(SkemaMasukan::berlakuTahun(['mulai' => '2020-01-01', 'sampai' => '2025-12-31'], 2026));

        $this->masuk();
        $this->kbAktif();
        $this->palsukanJembatan(['masukan' => self::skema(
            self::masukanTransport(['kunci' => 'hari_dinas', 'label' => 'Hari dinas luar', 'tipe' => 'bilangan', 'lingkup' => 'bulan', 'wajib' => true,
                'bawaan' => null, 'mulai' => '2026-07-15']),
            self::masukanTransport(['kunci' => 'bonus_desember', 'label' => 'Bonus akhir tahun', 'mulai' => '2026-12-15']),
        )]);
        $pt = $this->payroll(2026);

        $this->get("/payroll/{$pt->id}/edit")->assertOk()->assertDontSee('name="masukan_bulan[7][hari_dinas]"', false)
            ->assertSee('name="masukan_bulan[8][hari_dinas]"', false)->assertDontSee('Bonus akhir tahun');
        $this->put("/payroll/{$pt->id}", $this->isianPayroll(2026))->assertSessionHasErrors('masukan_bulan.8.hari_dinas')
            ->assertSessionDoesntHaveErrors('masukan_bulan.7.hari_dinas');
    }

    public function test_rupiah_tidak_boleh_negatif_dan_pilihan_wajib_required(): void
    {
        $this->masuk();
        $this->kbAktif();
        $this->palsukanJembatan(['masukan' => self::skema(
            self::masukanTransport(['mulai' => '2026-01-01']),
            self::masukanTransport(['kunci' => 'selisih_hari', 'label' => 'Selisih hari', 'tipe' => 'bilangan', 'mulai' => '2026-01-01']),
            self::masukanTransport(['kunci' => 'golongan', 'label' => 'Golongan', 'tipe' => 'pilihan', 'pilihan' => ['A', 'B'], 'wajib' => true,
                'bawaan' => null, 'mulai' => '2026-01-01']),
            self::masukanTransport(['kunci' => 'ikut_dplk', 'label' => 'Ikut DPLK', 'tipe' => 'ya_tidak', 'wajib' => true, 'bawaan' => null, 'mulai' => '2026-01-01']),
        )]);
        $pt = $this->payroll(2026);

        $html = $this->get("/payroll/{$pt->id}/edit")->assertOk()->getContent();
        $this->assertMatchesRegularExpression('/<input[^>]*name="masukan\[uang_transport_per_hari\]"[^>]*min="0"/s', $html);
        $this->assertDoesNotMatchRegularExpression('/<input[^>]*name="masukan\[selisih_hari\]"[^>]*min="0"/s', $html);
        $this->assertMatchesRegularExpression('/<select[^>]*name="masukan\[golongan\]"[^>]*required/s', $html);
        $this->assertMatchesRegularExpression('/<select[^>]*name="masukan\[ikut_dplk\]"[^>]*required/s', $html);

        $this->put("/payroll/{$pt->id}", $this->isianPayroll(2026, ['masukan' => ['uang_transport_per_hari' => '-5', 'selisih_hari' => '-5',
            'golongan' => 'A', 'ikut_dplk' => '0']]))
            ->assertSessionHasErrors('masukan.uang_transport_per_hari')->assertSessionDoesntHaveErrors('masukan.selisih_hari');
        $this->put("/payroll/{$pt->id}", $this->isianPayroll(2026, ['masukan' => ['uang_transport_per_hari' => '0', 'selisih_hari' => '-5',
            'golongan' => 'A', 'ikut_dplk' => '0']]))->assertSessionHasNoErrors();
        $this->assertSame(-5, $pt->masukan()->where('kunci', 'selisih_hari')->sole()->nilai);
    }

    public function test_cache_skema_ikut_berubah_saat_kb_dasar_berubah(): void
    {
        $root = $this->rootSementara();
        File::ensureDirectoryExists("{$root}/kb/regulasi");
        File::put("{$root}/kb/regulasi/parameter.yaml", "versi: 1\n");
        $this->kbAktif();
        $this->palsukanJembatan(['masukan' => self::skema(self::masukanTransport())]);
        $panggilan = fn (int $n) => Process::assertRanTimes(fn (PendingProcess $p) => json_decode($p->input, true)['perintah'] === 'masukan', $n);

        $skema = app(SkemaMasukan::class);
        $dasar = $skema->sidikDasar();
        $this->assertMatchesRegularExpression('/^[0-9a-f]{16}$/', $dasar);
        $skema->semua();
        app(SkemaMasukan::class)->semua();
        $panggilan(1);   // instance baru, KB sama: dari cache

        File::put("{$root}/kb/regulasi/parameter.yaml", "versi: 2\n");
        $this->assertSame($dasar, $skema->sidikDasar());   // dimemo per instance (satu permintaan)
        $baru = app(SkemaMasukan::class);
        $this->assertNotSame($dasar, $baru->sidikDasar());
        $baru->semua();
        $panggilan(2);

        foreach (['kb/perusahaan/perusahaan_x.yaml', 'jembatan/kontrak.py', 'asisten_kb/rancangan.py'] as $i => $rel) {
            File::ensureDirectoryExists(dirname("{$root}/{$rel}"));
            File::put("{$root}/{$rel}", "# ubah\n");
            app(SkemaMasukan::class)->semua();
            $panggilan(3 + $i);
        }
        File::put("{$root}/kb/regulasi/catatan.txt", 'bukan yaml');   // di luar pola: tidak memengaruhi sidik
        app(SkemaMasukan::class)->semua();
        $panggilan(5);
    }

    public function test_form_tahun_baru_melanjutkan_isian_tahunan_terakhir(): void
    {
        $this->masuk();
        $this->kbAktif();
        $this->palsukanJembatan(['masukan' => self::skema(
            self::masukanTransport(['mulai' => '2023-01-01']),
            self::masukanTransport(['kunci' => 'hari_dinas', 'label' => 'Hari dinas luar', 'tipe' => 'bilangan', 'lingkup' => 'bulan', 'mulai' => '2023-01-01']),
        )]);
        $pt2024 = $this->payroll(2024);
        $pt2023 = $pt2024->replicate(['pegawai']);
        $pt2023->tahun = 2023;
        $pt2023->save();
        $pt2023->masukan()->create(['kunci' => 'uang_transport_per_hari', 'bulan' => 0, 'nilai' => 10_000]);
        $pt2024->masukan()->create(['kunci' => 'uang_transport_per_hari', 'bulan' => 0, 'nilai' => 25_000]);
        $pt2024->masukan()->create(['kunci' => 'hari_dinas', 'bulan' => 3, 'nilai' => 4]);
        $pt2024->masukan()->create(['kunci' => 'kunci_lama', 'bulan' => 0, 'nilai' => 777]);   // tidak lagi diminta KB

        $this->get("/pegawai/{$pt2024->pegawai_id}/payroll/create?tahun=2025")->assertOk()
            ->assertSee('name="masukan[uang_transport_per_hari]" value="25000"', false)
            ->assertSee('name="masukan_bulan[3][hari_dinas]" value=""', false)
            ->assertDontSee('value="777"', false);
    }

    public function test_kb_aktif_tidak_dapat_dimuat_memberi_pesan_bukan_galat_500(): void
    {
        $this->masuk();
        $this->kbAktif();
        $this->palsukanJembatan(['masukan' => ['ok' => false, 'jenis' => 'kesalahan_kb', 'pesan' => 'berkas KB tambahan tidak ditemukan']]);
        $pt = $this->payroll(2026);

        $this->get("/payroll/{$pt->id}/edit")->assertOk()->assertSee('Isian tambahan dari knowledge base tidak dapat dimuat');
        $this->put("/payroll/{$pt->id}", $this->isianPayroll(2026))->assertSessionHasErrors('masukan');
        $this->post("/payroll/{$pt->id}/hitung")->assertSessionHas('error');
        $this->assertSame(0, Perhitungan::count());
    }
}
