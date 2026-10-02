<?php

namespace Tests\Feature;

use App\Models\Payroll\PayrollMasukan;
use App\Models\Payroll\Perhitungan;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Process\PendingProcess;
use Illuminate\Support\Facades\Process;
use Modules\Payroll\Services\KbTambahan;
use Modules\Payroll\Services\PenyusunKasus;
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
        $csv = $this->get("/payroll/{$pt->id}/ekspor")->streamedContent();
        $this->assertStringContainsString('px_komisi,px_transport,tunjangan_pajak', $csv);

        // berkas KB dinonaktifkan -> hasil lama dihitung dengan aturan yang tidak lagi berlaku
        $u->update(['aktif' => false]);
        $this->get("/payroll/{$pt->id}")->assertOk()->assertSee('Aturan knowledge base berubah');
        $this->getJson('/dashboard/list?tahun=2026')->assertJsonPath('data.0.status', 'kedaluwarsa');
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
