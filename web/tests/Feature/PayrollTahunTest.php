<?php

namespace Tests\Feature;

use App\Models\PayrollTahun;
use App\Models\Pegawai;
use App\Payroll\DataTidakLengkap;
use App\Payroll\PenyusunKasus;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class PayrollTahunTest extends TestCase
{
    use RefreshDatabase;

    private function pegawai(array $atr = []): Pegawai
    {
        return Pegawai::create($atr + ['nomor_induk' => 'P-1', 'nama' => 'Budi', 'jenis_kelamin' => 'L', 'punya_npwp' => true,
            'tanggal_masuk' => '2020-01-01']);
    }

    public function test_simpan_data_hr_dan_kasus_kanonik(): void
    {
        $this->masuk();
        $p = $this->pegawai();
        $isian = $this->isianPayroll(2025, ['bulan' => [3 => ['kompensasi_persen' => '12,5', 'lembur' => 750000, 'komisi' => 0]]]);
        $this->post("/pegawai/{$p->id}/payroll", $isian)->assertRedirect();

        $pt = PayrollTahun::firstOrFail();
        $this->assertSame('0.24', $pt->kelas_jkk_persen);
        $kasus = (new PenyusunKasus)->susun($pt);
        $this->assertSame(2025, $kasus['tahun_pajak']);
        $this->assertSame('K/1', $kasus['pegawai']['status_ptkp']);
        $this->assertNull($kasus['pegawai']['bulan_masuk']);
        $this->assertNull($kasus['pegawai']['bulan_terakhir_bekerja']);
        $this->assertCount(12, $kasus['masa']);
        $this->assertSame(['hk_penuh' => 22, 'hk_aktual' => 22, 'kompensasi_persen' => '0.125', 'lembur' => 750000, 'komisi' => 0],
            $kasus['data_hr']['per_masa'][3]);
        $this->assertSame(['hk_penuh' => 22, 'hk_aktual' => 22], $kasus['data_hr']['per_masa'][4]);
        $this->assertSame('2020-01-01', $kasus['data_hr']['tanggal_masuk_awal_bulan']);
        // kontrak presisi: tidak ada float di kasus yang dikirim ke engine
        $this->assertStringNotContainsString('e+', PenyusunKasus::json($kasus));
        array_walk_recursive($kasus, fn ($v) => $this->assertIsNotFloat($v));
    }

    public function test_masuk_dan_berhenti_di_tengah_tahun(): void
    {
        $this->masuk();
        $p = $this->pegawai(['tanggal_masuk' => '2026-03-16', 'tanggal_berhenti' => '2026-12-05']);
        $isian = $this->isianPayroll(2026);
        unset($isian['bulan'][1], $isian['bulan'][2]);
        $this->post("/pegawai/{$p->id}/payroll", $isian)->assertSessionHasNoErrors();

        $kasus = (new PenyusunKasus)->susun(PayrollTahun::firstOrFail());
        $this->assertSame(3, $kasus['pegawai']['bulan_masuk']);
        // berhenti Desember tetap resign sungguhan (BPJS Kes tidak dibayar di bulan resign), bukan sekadar akhir tahun
        $this->assertSame(12, $kasus['pegawai']['bulan_terakhir_bekerja']);
        $this->assertSame(range(3, 12), array_column($kasus['masa'], 'bulan'));
        $this->assertSame('2026-03-01', $kasus['data_hr']['tanggal_masuk_awal_bulan']);
    }

    public function test_bulan_dalam_masa_kerja_wajib_lengkap(): void
    {
        $this->masuk();
        $p = $this->pegawai();
        $isian = $this->isianPayroll(2024, ['bulan' => [5 => ['hk_aktual' => 23]]]);
        $isian['bulan'][7] = ['hk_penuh' => null, 'hk_aktual' => null];
        $this->post("/pegawai/{$p->id}/payroll", $isian)->assertSessionHasErrors(['bulan.5.hk_aktual', 'bulan.7.hk_penuh']);
        $this->assertSame(0, PayrollTahun::count());
    }

    public function test_float_dan_persen_tidak_valid_ditolak(): void
    {
        $this->masuk();
        $p = $this->pegawai();
        $isian = $this->isianPayroll(2024, ['gaji_pokok' => '1000000.5', 'kelas_jkk_persen' => 'nol', 'bulan' => [2 => ['kompensasi_persen' => '10%']]]);
        $this->post("/pegawai/{$p->id}/payroll", $isian)->assertSessionHasErrors(['gaji_pokok', 'kelas_jkk_persen', 'bulan.2.kompensasi_persen']);
    }

    public function test_kenaikan_tengah_bulan_wajib_dipecah(): void
    {
        $this->masuk();
        $p = $this->pegawai();
        $isian = $this->isianPayroll(2024, ['kenaikan_nominal' => 1_000_000, 'kenaikan_tanggal' => '2024-03-18',
            'bulan' => [3 => ['hk_penuh' => 21, 'hk_aktual' => 20]]]);
        $this->post("/pegawai/{$p->id}/payroll", $isian)->assertSessionHasErrors(['kenaikan_hk_sebelum', 'kenaikan_hari_sebelum']);

        $isian += ['kenaikan_hk_sebelum' => 11, 'kenaikan_hk_sesudah' => 9, 'kenaikan_hari_sebelum' => 11, 'kenaikan_hari_sesudah' => 10];
        $this->post("/pegawai/{$p->id}/payroll", $isian)->assertSessionHasNoErrors();
    }

    public function test_tahun_ganda_dan_di_luar_rentang_ditolak(): void
    {
        $this->masuk();
        $pt = $this->payroll(2024);
        $this->post("/pegawai/{$pt->pegawai_id}/payroll", $this->isianPayroll(2024))->assertSessionHasErrors('tahun');
        $this->post("/pegawai/{$pt->pegawai_id}/payroll", $this->isianPayroll(2027))->assertSessionHasErrors('tahun');
    }

    public function test_ubah_menghapus_bulan_yang_dikosongkan(): void
    {
        $this->masuk();
        $pt = $this->payroll(2024);
        $pt->pegawai->update(['tanggal_berhenti' => '2024-06-30']);
        $isian = $this->isianPayroll(2024);
        foreach (range(7, 12) as $b) {
            $isian['bulan'][$b] = ['hk_penuh' => null, 'hk_aktual' => null];
        }
        $this->put("/payroll/{$pt->id}", $isian)->assertSessionHasNoErrors();
        $this->assertSame(range(1, 6), $pt->bulan()->pluck('bulan')->all());
        $this->assertSame('K/1', $pt->fresh()->status_ptkp);
    }

    public function test_data_tidak_lengkap_terdeteksi_saat_menyusun(): void
    {
        $pt = $this->payroll(2024);
        $pt->bulan()->where('bulan', 8)->delete();
        $this->expectException(DataTidakLengkap::class);
        (new PenyusunKasus)->susun($pt->fresh(['pegawai', 'bulan']));
    }

    public function test_form_tambah_melanjutkan_tahun_sebelumnya(): void
    {
        $this->masuk();
        $pt = $this->payroll(2024, ['kenaikan_nominal' => 500_000, 'kenaikan_tanggal' => '2024-07-01', 'tunjangan_tetap_baru' => 300_000]);
        $this->get("/pegawai/{$pt->pegawai_id}/payroll/create")
            ->assertOk()
            ->assertSee('value="10500000"', false)   // gaji pokok + kenaikan tahun lalu
            ->assertSee('value="300000"', false)     // tunjangan sesudah kenaikan
            ->assertSee('<option value="2026"', false)
            ->assertDontSee('<option value="2024"', false);
    }
}
