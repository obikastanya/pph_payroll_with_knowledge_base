<?php

namespace Tests\Feature;

use App\Models\Payroll\Perhitungan;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Process\PendingProcess;
use Illuminate\Support\Facades\Process;
use Modules\Payroll\Http\Controllers\PayrollController;
use Modules\Payroll\Services\TampilanHasil;
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
                'kategori_wajib' => 'teratur', 'sumber' => 'PER-16/PJ/2016 Ps. 1 angka 15'],
                // bentuk tingkat aturan (resolusi lex superior): tanpa kategori_*, satu per masa
                ['kode' => 'KONFLIK_WAJIB', 'fakta' => 'px_lembur', 'bulan' => 1, 'ditolak' => ['PX-LEMBUR-01'], 'pemenang' => ['R-LEMBUR-01']],
                ['kode' => 'KONFLIK_WAJIB', 'fakta' => 'px_lembur', 'bulan' => 2, 'ditolak' => ['PX-LEMBUR-01'], 'pemenang' => ['R-LEMBUR-01']],
                ['kode' => 'GROSSUP_GANDA', 'bulan' => 12]],
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

    public function test_peringatan_konflik_tingkat_aturan_tidak_membuat_galat_500(): void
    {
        $this->masuk();
        $pt = $this->payroll(2024);
        $this->palsukanEngine([['ok' => true, 'hasil' => self::hasilPalsu()]]);
        $this->post("/payroll/{$pt->id}/hitung");

        $html = $this->get("/payroll/{$pt->id}?tab=slip&bulan=1")->assertOk()
            ->assertSee('Komponen Lembur dikategorikan perusahaan sebagai penghasilan tidak teratur, padahal regulasi menetapkan teratur')
            ->assertSee('Gross-up punya dua jawaban sah')
            ->getContent();
        // peringatan per masa yang sama tampil sekali, tanpa nama bulan
        $teks = 'Aturan PX-LEMBUR-01 untuk Lembur tidak dipakai karena aturan wajib R-LEMBUR-01 berlaku.';
        $this->assertSame(1, substr_count($html, $teks));
        $this->get("/payroll/{$pt->id}/slip/1")->assertOk();
    }

    public function test_nama_berkas_ekspor_disaring(): void
    {
        $this->masuk();
        $pt = $this->payroll(2024, [], ['nomor_induk' => '001/HR/2023 a"b']);
        $this->palsukanEngine([['ok' => true, 'hasil' => self::hasilPalsu()]]);
        $this->post("/payroll/{$pt->id}/hitung");

        $this->get("/payroll/{$pt->id}/ekspor")->assertOk()->assertDownload('payroll_001-HR-2023-a-b_2024.csv');
        $this->assertSame('a.b_c-d-e--f', PayrollController::namaBerkas('a.b_c-d/e\\ f'));
    }

    /** Hasil palsu dengan komponen dari berkas KB tambahan di setiap kategori yang dikelompokkan slip. */
    private static function hasilKomponenTambahan(): array
    {
        $h = self::hasilPalsu();
        foreach ($h['per_masa'] as $b => $m) {
            $h['per_masa'][$b] = $m + ['px_iuran_kes_pg' => 50_000, 'px_premi_jht_pk' => 370_000, 'koperasi' => 200_000,
                'jht_tambahan_pk' => 120_000, 'makan' => 300_000, 'beasiswa' => 400_000];
        }
        $h['komponen'] = [
            ['fakta' => 'px_gaji', 'jenis' => 'gaji', 'kategori' => 'teratur', 'label' => null, 'berkas' => 'perusahaan_x.yaml'],
            ['fakta' => 'px_premi_jht_pk', 'jenis' => 'iuran_jht_pemberi_kerja', 'kategori' => 'bukan_objek', 'label' => null, 'berkas' => 'perusahaan_x.yaml'],
            ['fakta' => 'px_iuran_kes_pg', 'jenis' => 'iuran_jkn_pegawai', 'kategori' => 'tidak_diperhitungkan', 'label' => null, 'berkas' => 'perusahaan_x.yaml'],
            ['fakta' => 'koperasi', 'jenis' => 'cicilan_koperasi', 'kategori' => 'tidak_diperhitungkan', 'label' => 'Cicilan koperasi', 'berkas' => '0002_koperasi.yaml'],
            ['fakta' => 'jht_tambahan_pk', 'jenis' => 'iuran_dplk_pemberi_kerja', 'kategori' => 'bukan_objek', 'label' => 'DPLK perusahaan', 'berkas' => '0003_dplk.yaml'],
            ['fakta' => 'makan', 'jenis' => 'tunjangan_makan', 'kategori' => 'teratur', 'label' => 'Uang makan', 'berkas' => '0004_makan.yaml'],
            // dideklarasikan teratur, tetapi regulasi mewajibkan natura: engine menghitungnya sebagai natura
            ['fakta' => 'beasiswa', 'jenis' => 'beasiswa_anak', 'kategori' => 'teratur', 'label' => 'Beasiswa anak', 'berkas' => '0004_makan.yaml'],
        ];
        $h['peringatan'][] = ['kode' => 'KONFLIK_WAJIB', 'fakta' => 'beasiswa', 'jenis' => 'beasiswa_anak', 'kategori_perusahaan' => 'teratur',
            'kategori_wajib' => 'natura', 'sumber' => 'PMK 66/2023', 'berkas' => '0004_makan.yaml'];

        return $h;
    }

    public function test_slip_mengelompokkan_komponen_tambahan_menurut_kategori_efektif(): void
    {
        $t = new TampilanHasil(self::hasilKomponenTambahan(), ['data_hr' => ['per_masa' => []], 'pegawai' => []]);
        $bagian = null;
        $kelompok = [];
        foreach ($t->slip(3) as $r) {
            if ($r['judul']) {
                $bagian = $r['uraian'];
            } else {
                $kelompok[$r['uraian']] = [$bagian, $r['tanda']];
            }
        }

        $this->assertSame(['Penghasilan', ''], $kelompok['Uang makan']);
        $this->assertSame(['Ditanggung perusahaan (menambah bruto, tidak dibayar tunai)', ''], $kelompok['Beasiswa anak']);
        $this->assertSame(['Potongan', '-'], $kelompok['Cicilan koperasi']);
        $this->assertSame(['Lainnya (bukan objek pajak, tidak dibayar tunai)', ''], $kelompok['DPLK perusahaan']);
        // baris dasar Perusahaan X tidak berubah: JHT perusahaan (bukan objek) tidak muncul, iuran BPJS Kes tetap di Potongan
        $this->assertArrayNotHasKey('JHT perusahaan (bukan objek)', $kelompok);
        $this->assertSame(['Potongan', '-'], $kelompok['Iuran BPJS Kesehatan pegawai']);
        $urutan = array_keys($kelompok);
        $this->assertSame('DPLK perusahaan', end($urutan));   // setelah take home pay: tidak termasuk THP
        $this->assertLessThan(array_search('Take home pay', $urutan), array_search('Cicilan koperasi', $urutan));

        // tanpa komponen bukan objek bernilai di bulan itu, bagian Lainnya tidak tampil
        $h = self::hasilKomponenTambahan();
        unset($h['per_masa'][3]['jht_tambahan_pk']);
        $judul = array_column(array_filter((new TampilanHasil($h, ['data_hr' => []]))->slip(3), fn ($r) => $r['judul']), 'uraian');
        $this->assertNotContains('Lainnya (bukan objek pajak, tidak dibayar tunai)', $judul);
    }

    public function test_slip_layar_dan_cetak_memakai_baris_yang_sama(): void
    {
        $this->masuk();
        $pt = $this->payroll(2024);
        $this->palsukanEngine([['ok' => true, 'hasil' => self::hasilKomponenTambahan()]]);
        $this->post("/payroll/{$pt->id}/hitung");

        $urutan = ['Penghasilan', 'Uang makan', 'Beasiswa anak', 'Potongan', 'Iuran BPJS Kesehatan pegawai', 'Cicilan koperasi',
            'Take home pay', 'Lainnya (bukan objek pajak, tidak dibayar tunai)', 'DPLK perusahaan'];
        $this->get("/payroll/{$pt->id}?tab=slip&bulan=3")->assertOk()->assertSeeInOrder($urutan)->assertSee('-200.000');
        $this->get("/payroll/{$pt->id}/slip/3")->assertOk()->assertSeeInOrder($urutan)->assertSee('-200.000')
            ->assertDontSee('Hasil usang');
    }

    public function test_data_berubah_sejak_dihitung(): void
    {
        $this->masuk();
        $pt = $this->payroll(2024);
        $this->palsukanEngine([['ok' => true, 'hasil' => self::hasilPalsu()]]);
        $this->post("/payroll/{$pt->id}/hitung");

        $this->get('/dashboard?tahun=2024')->assertSee('0 belum dihitung / perlu dihitung ulang"', false);
        $pt->update(['gaji_pokok' => 11_000_000]);
        $this->get("/payroll/{$pt->id}")->assertSee('Data HR berubah sejak');
        $this->getJson('/dashboard/list?tahun=2024')->assertJsonPath('data.0.status', 'kedaluwarsa')->assertJsonPath('data.0.alasan', 'data');
        // hasil usang dihitung sebagai perlu dihitung ulang, dan ditandai di rekap CSV maupun slip cetak
        $this->get('/dashboard?tahun=2024')->assertSee('1 belum dihitung / perlu dihitung ulang (termasuk 1 hasil usang)');
        $csv = array_map('str_getcsv', explode("\n", trim($this->get('/dashboard/ekspor?tahun=2024')->streamedContent())));
        $this->assertSame(['dihitung_pada', 'status', 'sidik_kb', 'pesan'], array_slice($csv[0], 10));
        $this->assertSame(['usang (data)', ''], array_slice($csv[1], 11, 2));
        $this->get("/payroll/{$pt->id}/slip/3")->assertOk()->assertSee('Hasil usang: data HR berubah');
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
        $rekap = $this->get('/dashboard/ekspor?tahun=2025')->streamedContent();
        $status = array_map(fn ($b) => str_getcsv($b)[11], array_slice(explode("\n", trim($rekap)), 1));
        $this->assertEqualsCanonicalizing(['berhasil', 'berhasil', 'galat'], $status);
        $this->assertStringContainsString('hari kerja bulan April belum diisi', $rekap);   // pesan galat di kolom pesan

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
