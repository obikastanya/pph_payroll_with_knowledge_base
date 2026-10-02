<?php

namespace Tests\Feature;

use App\Models\Payroll\Perhitungan;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Process\PendingProcess;
use Illuminate\Support\Facades\Process;
use Tests\TestCase;

/** Alur hitung dengan engine palsu (Process::fake): pencatatan, galat, dan deteksi data berubah. */
class HitungTest extends TestCase
{
    use RefreshDatabase;

    private static function hasilPalsu(int $pph = 1_234_000): array
    {
        $perMasa = [];
        foreach (range(1, 12) as $b) {
            $perMasa[$b] = ['px_gaji' => 10_000_000, 'bruto' => 10_500_000, 'kategori_ter' => 'A', 'tarif_ter' => '3/200',
                'pph21' => 157_500, 'px_thp' => 9_500_000];
        }

        return ['per_masa' => $perMasa,
            'tahunan' => ['bruto_setahun' => 126_000_000, 'pph21_setahun' => $pph, 'ptkp' => 54_000_000, 'pkp' => 66_000_000],
            'jejak' => [['fakta' => 'px_gaji', 'bulan' => 1, 'nilai' => 10_000_000, 'aturan' => 'PX-GAJI-02', 'lapisan' => 'perusahaan',
                'sifat' => 'opsional', 'sumber' => 'xlsx v8 baris 5', 'ditolak' => [], 'alasan' => []]],
            'peringatan' => [['kode' => 'KONFLIK_WAJIB', 'fakta' => 'px_lembur', 'jenis' => 'lembur', 'kategori_perusahaan' => 'tidak_teratur',
                'kategori_wajib' => 'teratur', 'sumber' => 'PER-16/PJ/2016 Ps. 1 angka 15']],
            'rincian_pasal17' => [], 'audit' => ['versi_engine' => '0.1.0', 'versi_kb' => 'abc123', 'tanggal_kebaruan_kb' => '2026-10-01']];
    }

    private function palsukanEngine(array $jawabanPerKasus): void
    {
        Process::fake(['*' => Process::result(output: json_encode(['ok' => true, 'hasil' => $jawabanPerKasus]))]);
    }

    public function test_hitung_satu_pegawai_mencatat_riwayat(): void
    {
        $user = $this->masuk();
        $pt = $this->payroll(2024);
        $this->palsukanEngine([['ok' => true, 'hasil' => self::hasilPalsu(), 'cek_silang' => ['status' => 'identik', 'selisih' => []]]]);

        $this->post("/payroll/{$pt->id}/hitung")->assertSessionHas('success');

        $p = Perhitungan::sole();
        $this->assertTrue($p->berhasil);
        $this->assertSame(1_234_000, $p->pph21_setahun);
        $this->assertSame(12 * 9_500_000, $p->thp_setahun);
        $this->assertSame('identik', $p->cek_silang);
        $this->assertSame('abc123', $p->versi_kb);
        $this->assertSame($user->id, $p->user_id);
        Process::assertRan(function (PendingProcess $proses) use ($pt) {
            $permintaan = json_decode($proses->input, true);

            return $proses->command[1] === '-m' && $proses->command[2] === 'jembatan'
                && $proses->path === config('payroll.root')
                && $permintaan['perintah'] === 'hitung' && $permintaan['kasus'][0]['id'] === "PAYROLL-{$pt->id}";
        });

        foreach (['slip', 'setahun', 'bulanan', 'jejak'] as $tab) {
            $this->get("/payroll/{$pt->id}?tab={$tab}")->assertOk();
        }
        $this->get("/payroll/{$pt->id}?tab=slip&bulan=1")->assertSee('Rp1.234.000')->assertSee('PX-GAJI-02')->assertSee('identik sampai rupiah', false)
            ->assertSee('Konflik kebijakan perusahaan')->assertDontSee('Data HR berubah sejak');
        $this->get("/payroll/{$pt->id}/slip/3")->assertOk()->assertSee('Slip gaji');
        $this->get("/payroll/{$pt->id}/ekspor")->assertOk()->assertDownload("payroll_{$pt->pegawai->nomor_induk}_2024.csv");
    }

    public function test_data_berubah_sejak_dihitung(): void
    {
        $this->masuk();
        $pt = $this->payroll(2024);
        $this->palsukanEngine([['ok' => true, 'hasil' => self::hasilPalsu()]]);
        $this->post("/payroll/{$pt->id}/hitung");

        $pt->update(['gaji_pokok' => 11_000_000]);
        $this->get("/payroll/{$pt->id}")->assertSee('Data HR berubah sejak');
        $this->getJson('/dashboard/list?tahun=2024')->assertJsonPath('data.0.status', 'kedaluwarsa');
    }

    public function test_galat_per_pegawai_dicatat(): void
    {
        $this->masuk();
        $pt = $this->payroll(2023, ['metode' => 'gross_up']);
        $this->palsukanEngine([['ok' => false, 'jenis' => 'di_luar_cakupan', 'pesan' => 'Kasus di luar cakupan kalkulator: gross-up PER-16']]);

        $this->post("/payroll/{$pt->id}/hitung")->assertSessionHas('error', 'Kasus di luar cakupan kalkulator: gross-up PER-16');
        $p = Perhitungan::sole();
        $this->assertFalse($p->berhasil);
        $this->assertSame('di_luar_cakupan', $p->jenis_galat);
        $this->get("/payroll/{$pt->id}")->assertOk()->assertSee('Perhitungan terakhir gagal');
    }

    public function test_engine_tidak_tersedia_tidak_mencatat_apa_pun(): void
    {
        $this->masuk();
        $pt = $this->payroll(2024);
        Process::fake(['*' => Process::result(output: '', errorOutput: 'ModuleNotFoundError: No module named jembatan', exitCode: 1)]);

        $this->post("/payroll/{$pt->id}/hitung")->assertSessionHas('error');
        $this->assertSame(0, Perhitungan::count());
        $this->assertStringContainsString('ModuleNotFoundError', session('error'));
    }

    public function test_hitung_semua_satu_panggilan_dan_data_tidak_lengkap(): void
    {
        $this->masuk();
        $a = $this->payroll(2025);
        $b = $this->payroll(2025);
        $c = $this->payroll(2025);
        $c->bulan()->where('bulan', 4)->delete();
        $this->palsukanEngine([['ok' => true, 'hasil' => self::hasilPalsu(100)], ['ok' => true, 'hasil' => self::hasilPalsu(200)]]);

        $this->post('/dashboard/hitung', ['tahun' => 2025])->assertSessionHas('warning');
        Process::assertRanTimes(fn () => true, 1);
        $this->assertSame(3, Perhitungan::count());
        $this->assertEqualsCanonicalizing([100, 200], Perhitungan::where('berhasil', true)->pluck('pph21_setahun')->all());
        $gagal = Perhitungan::where('berhasil', false)->sole();
        $this->assertSame($c->id, $gagal->payroll_tahun_id);
        $this->assertSame('data_tidak_lengkap', $gagal->jenis_galat);

        $this->get('/dashboard?tahun=2025')->assertOk()->assertSee('Rp300')->assertSee('Pegawai dengan data HR 2025');
        $this->getJson('/dashboard/list?tahun=2025')->assertOk()->assertJsonPath('meta.total', 3)->assertSee('hari kerja bulan April belum diisi');
        $this->get('/dashboard/ekspor?tahun=2025')->assertOk()->assertDownload('rekap_payroll_2025.csv');

        $a->pegawai->update(['nama' => '=HYPERLINK("http://contoh")']);
        $csv = $this->get('/dashboard/ekspor?tahun=2025')->streamedContent();
        $this->assertStringContainsString("'=HYPERLINK", $csv);
    }

    public function test_halaman_mesin_menampilkan_galat_engine(): void
    {
        $this->masuk();
        Process::fake(['*' => Process::result(output: 'bukan json', exitCode: 1)]);
        $this->get('/mesin')->assertOk()->assertSee('Engine tidak dapat dipanggil');
    }
}
