<?php

namespace Tests\Feature;

use App\Models\Kb\UsulanKb;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\UploadedFile;
use Illuminate\Process\PendingProcess;
use Illuminate\Support\Facades\Process;
use Illuminate\Support\Facades\Queue;
use Illuminate\Support\Facades\Storage;
use Modules\BasisPengetahuan\Jobs\ProsesUsulanKb;
use Modules\Payroll\Services\KbTambahan;
use Modules\Payroll\Services\MesinPajak;
use Tests\Concerns\KbUji;
use Tests\TestCase;

/**
 * Menu Basis pengetahuan: unggah PDF -> antrean LLM -> tinjau -> terapkan / tolak / nonaktifkan. Jembatan Python (dan
 * LLM di baliknya) dipalsukan; yang diuji adalah alur, status, dan bahwa berkas KB hanya ditulis setelah lolos validasi.
 */
class BasisPengetahuanTest extends TestCase
{
    use KbUji, RefreshDatabase;

    private static function nama(UsulanKb $u): string
    {
        return sprintf('%04d_transport_2026.yaml', $u->id);
    }

    public function test_unggah_pdf_masuk_antrean(): void
    {
        $user = $this->masuk();
        Queue::fake();
        Storage::fake('local');

        $this->get('/kb')->assertOk()->assertSee('Unggah peraturan')->assertSee('Belum ada berkas tambahan');
        $this->post('/kb', ['judul' => 'PP 2026', 'lapisan' => 'perusahaan', 'pdf' => UploadedFile::fake()->create('pp.txt', 10, 'text/plain')])
            ->assertSessionHasErrors('pdf');
        $this->post('/kb', ['judul' => 'PP 2026', 'lapisan' => 'undang-undang', 'pdf' => UploadedFile::fake()->create('pp.pdf', 10, 'application/pdf')])
            ->assertSessionHasErrors('lapisan');

        $this->post('/kb', ['judul' => 'PP 2026', 'lapisan' => 'perusahaan', 'catatan' => 'berlaku Juli',
            'pdf' => UploadedFile::fake()->create('pp 2026.pdf', 200, 'application/pdf')])->assertRedirect();

        $u = UsulanKb::sole();
        $this->assertSame(['antre', 'perusahaan', 'pp 2026.pdf', $user->id], [$u->status, $u->lapisan, $u->nama_pdf, $u->user_id]);
        Storage::disk('local')->assertExists($u->path_pdf);
        Queue::assertPushed(ProsesUsulanKb::class, fn ($job) => $job->usulanId === $u->id);

        $this->get("/kb/{$u->id}")->assertOk()->assertSee('LLM sedang membaca dokumen');
        $this->getJson("/kb/{$u->id}/status")->assertJson(['status' => 'antre', 'selesai' => false]);
        $this->getJson('/kb/list')->assertJsonPath('data.0.judul', 'PP 2026')->assertJsonPath('data.0.diproses', true);
        $this->get("/kb/{$u->id}/pdf")->assertOk()->assertDownload('pp 2026.pdf');
        $this->delete("/kb/{$u->id}")->assertStatus(409);   // sedang diproses
    }

    public function test_job_menyimpan_rancangan_untuk_ditinjau(): void
    {
        Storage::fake('local');
        Storage::disk('local')->put('kb_usulan/pp.pdf', '%PDF-1.4');
        config(['payroll.anthropic_key' => 'sk-ant-uji', 'payroll.llm_timeout' => 600]);
        $u = $this->usulan(['status' => 'antre', 'usulan' => null, 'yaml' => null, 'validasi' => null, 'valid' => null, 'info_llm' => null,
            'catatan' => 'berlaku Juli']);
        $this->palsukanJembatan(['usulkan' => self::jawabUsulkan()]);

        (new ProsesUsulanKb($u->id))->handle(app(MesinPajak::class));

        $u->refresh();
        $this->assertSame('siap_tinjau', $u->status);
        $this->assertTrue($u->valid);
        $this->assertSame(self::YAML, $u->yaml);
        $this->assertSame('claude-opus-5-5', $u->info_llm['model']);
        $this->assertFalse($u->aktif, 'rancangan LLM tidak pernah langsung berlaku');
        Process::assertRan(function (PendingProcess $p) use ($u) {
            $permintaan = json_decode($p->input, true);

            return $permintaan['perintah'] === 'usulkan' && $permintaan['lapisan'] === 'perusahaan' && $permintaan['catatan'] === 'berlaku Juli'
                && $permintaan['pdf'] === Storage::disk('local')->path($u->path_pdf) && $permintaan['model'] === 'claude-opus-5-5'
                && $p->environment['ANTHROPIC_API_KEY'] === 'sk-ant-uji' && $p->timeout === 600;
        });
        $this->assertSame(660, (new ProsesUsulanKb($u->id))->timeout);
    }

    public function test_job_mencatat_kegagalan_dan_dokumen_tanpa_aturan(): void
    {
        Storage::fake('local');
        $kosong = ['status' => 'antre', 'usulan' => null, 'yaml' => null, 'validasi' => null, 'valid' => null, 'info_llm' => null];
        $gagal = $this->usulan($kosong);
        $this->palsukanJembatan(['usulkan' => ['ok' => false, 'jenis' => 'gagal_llm', 'pesan' => 'model menolak memproses dokumen ini']]);
        (new ProsesUsulanKb($gagal->id))->handle(app(MesinPajak::class));
        $this->assertSame(['gagal', 'gagal_llm: model menolak memproses dokumen ini'], [$gagal->refresh()->status, $gagal->pesan_galat]);

        $tanpa = $this->usulan($kosong);
        $jawab = self::jawabUsulkan(['yaml' => '', 'validasi' => null]);
        $jawab['usulan'] = ['dapat_dikodifikasi' => false, 'alasan' => 'Dokumen hanya mengubah tabel TER.'] + $jawab['usulan'];
        $this->palsukanJembatan(['usulkan' => $jawab]);
        (new ProsesUsulanKb($tanpa->id))->handle(app(MesinPajak::class));
        $this->assertSame(['tidak_dapat_dikodifikasi', null, null], [$tanpa->refresh()->status, $tanpa->yaml, $tanpa->valid]);

        (new ProsesUsulanKb($tanpa->id))->failed(new \RuntimeException('waktu habis'));
        $this->assertSame('tidak_dapat_dikodifikasi', $tanpa->refresh()->status, 'failed() hanya menandai usulan yang masih diproses');

        $this->masuk();
        $this->get("/kb/{$gagal->id}")->assertOk()->assertSee('Dokumen gagal dibaca')->assertSee('model menolak');
        $this->get("/kb/{$tanpa->id}")->assertOk()->assertSee('Tidak dapat dijadikan aturan KB')->assertSee('hanya mengubah tabel TER');
        Queue::fake();
        $this->post("/kb/{$gagal->id}/ulang")->assertSessionHas('success');
        $this->assertSame(['antre', null], [$gagal->refresh()->status, $gagal->pesan_galat]);
        Queue::assertPushed(ProsesUsulanKb::class, fn ($job) => $job->usulanId === $gagal->id);
    }

    public function test_halaman_tinjau_menampilkan_rancangan(): void
    {
        $this->masuk();
        $u = $this->usulan();

        $this->get("/kb/{$u->id}")->assertOk()
            ->assertSee('Uang transport per hari hadir')->assertSee('uang_transport_per_hari')       // isian baru
            ->assertSee('PPT-TRANSPORT-01')->assertSee('uang transport dibayarkan untuk setiap hari hadir')->assertSee('hlm. 3')
            ->assertSee('Nominal per hari tidak disebut di dokumen')                                    // catatan peninjau dari LLM
            ->assertSee('12.600.000')->assertSee('+1.890.000')                                         // simulasi dampak
            ->assertSee('Lolos.')->assertSee('Terapkan ke KB')->assertSee('kb/tambahan/'.self::nama($u));
        $this->getJson("/kb/{$u->id}/status")->assertJson(['status' => 'siap_tinjau', 'selesai' => true]);
        $this->get("/kb/{$u->id}/unduh")->assertOk()->assertDownload(self::nama($u));
    }

    public function test_terapkan_hanya_bila_lolos_validasi_engine(): void
    {
        $this->masuk();
        $root = $this->rootSementara();
        $u = $this->usulan();
        $berkas = $root.'/kb/tambahan/'.self::nama($u);

        $this->palsukanJembatan(['validasi' => ['ok' => true, 'validasi' => self::validasiLolos(['ok' => false, 'galat' => ['id aturan duplikat: PPT-TRANSPORT-01']])]]);
        $this->post("/kb/{$u->id}/terapkan")->assertSessionHas('error');
        $this->assertFileDoesNotExist($berkas);
        $this->assertSame(['siap_tinjau', false, false], [$u->refresh()->status, $u->valid, $u->aktif]);
        $this->get("/kb/{$u->id}")->assertSee('Belum lolos')->assertSee('id aturan duplikat');

        $this->palsukanJembatan(['validasi' => ['ok' => true, 'validasi' => self::validasiLolos()]]);
        $this->post("/kb/{$u->id}/terapkan")->assertSessionHas('success');
        $this->assertSame(self::YAML, file_get_contents($berkas));
        $this->assertSame(['diterapkan', true, self::nama($u)], [$u->refresh()->status, $u->aktif, $u->nama_berkas]);
        $this->assertSame(['kb/tambahan/'.self::nama($u)], app(KbTambahan::class)->berkasAktif());
        $this->assertSame(16, strlen(app(KbTambahan::class)->sidik()));

        $this->get('/kb')->assertOk()->assertSee('kb/tambahan/'.self::nama($u))->assertSee('1 isian baru');
        $this->post("/kb/{$u->id}/terapkan")->assertStatus(409);                       // sudah diterapkan
        $this->put("/kb/{$u->id}/yaml", ['yaml' => 'lapisan: perusahaan'])->assertStatus(409);  // aktif: tidak boleh diubah
        $this->delete("/kb/{$u->id}")->assertStatus(409);
    }

    public function test_ubah_rancangan_divalidasi_ulang(): void
    {
        $this->masuk();
        $this->rootSementara();
        $u = $this->usulan();
        $this->palsukanJembatan(['validasi' => ['ok' => true, 'validasi' => self::validasiLolos(['ok' => false, 'galat' => ['YAML tidak dapat dibaca: x']])]]);

        $this->put("/kb/{$u->id}/yaml", ['yaml' => "lapisan: [\r\n"])->assertSessionHas('warning');
        $this->assertSame(["lapisan: [\n", false], [$u->refresh()->yaml, $u->valid]);
        Process::assertRan(fn (PendingProcess $p) => json_decode($p->input, true) == ['perintah' => 'validasi', 'yaml' => "lapisan: [\n",
            'nama' => self::nama($u), 'berkas_tambahan' => []]);
        $this->put("/kb/{$u->id}/yaml", ['yaml' => ''])->assertSessionHasErrors('yaml');

        Process::fake(['*' => Process::result(output: '', errorOutput: 'python: not found', exitCode: 127)]);
        $this->put("/kb/{$u->id}/yaml", ['yaml' => 'lapisan: perusahaan'])->assertSessionHas('error');
    }

    public function test_nonaktifkan_aktifkan_tolak_dan_hapus(): void
    {
        $this->masuk();
        Storage::fake('local');
        $u = $this->kbAktif();
        $berkas = app(KbTambahan::class)->absolut($u->nama_berkas);

        // menonaktifkan: KB sisanya harus tetap dapat dimuat engine
        $this->palsukanJembatan(['masukan' => ['ok' => false, 'jenis' => 'kesalahan_kb', 'pesan' => 'fakta px_transport tidak dihasilkan']]);
        $this->post("/kb/{$u->id}/aktif")->assertSessionHas('error');
        $this->assertTrue($u->refresh()->aktif);

        $this->palsukanJembatan(['masukan' => ['ok' => true, 'masukan' => [], 'komponen' => []], 'validasi' => ['ok' => true, 'validasi' => self::validasiLolos()]]);
        $this->post("/kb/{$u->id}/aktif")->assertSessionHas('success');
        $this->assertFalse($u->refresh()->aktif);
        $this->assertSame([], app(KbTambahan::class)->berkasAktif());
        $this->assertSame('', app(KbTambahan::class)->sidik());
        $this->get("/kb/{$u->id}")->assertOk()->assertSee('diterapkan, nonaktif')->assertSee('Aktifkan kembali')->assertSee('Simpan & validasi ulang');

        $this->post("/kb/{$u->id}/aktif")->assertSessionHas('success');
        $this->assertTrue($u->refresh()->aktif);
        $this->post("/kb/{$u->id}/aktif");
        $this->delete("/kb/{$u->id}")->assertRedirect('/kb');
        $this->assertFileDoesNotExist($berkas);
        $this->assertSame(0, UsulanKb::count());

        $lain = $this->usulan();
        $this->post("/kb/{$lain->id}/tolak")->assertSessionHas('success');
        $this->assertSame('ditolak', $lain->refresh()->status);
        $this->post("/kb/{$lain->id}/terapkan")->assertStatus(409);
    }

    public function test_tamu_tidak_dapat_membuka(): void
    {
        $u = $this->usulan();
        $this->get('/kb')->assertRedirect('/login');
        $this->post("/kb/{$u->id}/terapkan")->assertRedirect('/login');
    }
}
