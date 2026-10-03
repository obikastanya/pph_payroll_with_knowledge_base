<?php

namespace Tests\Feature;

use App\Models\Kb\UsulanKb;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\UploadedFile;
use Illuminate\Process\Exceptions\ProcessTimedOutException;
use Illuminate\Process\FakeProcessResult;
use Illuminate\Process\PendingProcess;
use Illuminate\Queue\MaxAttemptsExceededException;
use Illuminate\Queue\TimeoutExceededException;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Process;
use Illuminate\Support\Facades\Queue;
use Illuminate\Support\Facades\Storage;
use Modules\BasisPengetahuan\Http\Controllers\BasisPengetahuanController;
use Modules\BasisPengetahuan\Http\Requests\UnggahPeraturanRequest;
use Modules\BasisPengetahuan\Jobs\ProsesUsulanKb;
use Modules\BasisPengetahuan\Services\PenerapanKb;
use Modules\Payroll\Services\KbTambahan;
use Modules\Payroll\Services\MesinPajak;
use Modules\Payroll\Services\MesinTidakTersedia;
use PHPUnit\Framework\AssertionFailedError;
use Symfony\Component\Process\Exception\ProcessTimedOutException as SymfonyTimeout;
use Symfony\Component\Process\Process as SymfonyProcess;
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

        config(['payroll.llm_model' => 'gpt-5.6-sol', 'payroll.llm_kunci_env' => 'OPENAI_API_KEY', 'payroll.llm_kunci' => null]);
        $this->get('/kb')->assertOk()->assertSee('Unggah peraturan')->assertSee('Belum ada berkas tambahan')
            ->assertSee('Kunci API LLM belum diatur')->assertSee('OPENAI_API_KEY')->assertSee('gpt-5.6-sol');
        config(['payroll.llm_kunci' => 'sk-uji']);
        $this->get('/kb')->assertOk()->assertDontSee('Kunci API LLM belum diatur');
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
        $u->update(['status' => 'diproses']);
        $this->delete("/kb/{$u->id}")->assertStatus(409);   // sedang dibaca LLM; usulan antre boleh dibatalkan (uji tersendiri)
    }

    public function test_job_menyimpan_rancangan_untuk_ditinjau(): void
    {
        Storage::fake('local');
        Storage::disk('local')->put('kb_usulan/pp.pdf', '%PDF-1.4');
        config(['payroll.llm_model' => 'gpt-5.6-sol', 'payroll.llm_kunci_env' => 'OPENAI_API_KEY', 'payroll.llm_kunci' => 'sk-uji',
            'payroll.llm_timeout' => 600]);
        $u = $this->usulan(['status' => 'antre', 'usulan' => null, 'yaml' => null, 'validasi' => null, 'valid' => null, 'info_llm' => null,
            'catatan' => 'berlaku Juli']);
        $this->palsukanJembatan(['usulkan' => self::jawabUsulkan()]);

        (new ProsesUsulanKb($u->id))->handle(app(MesinPajak::class));

        $u->refresh();
        $this->assertSame('siap_tinjau', $u->status);
        $this->assertTrue($u->valid);
        $this->assertSame(self::YAML, $u->yaml);
        $this->assertSame('gpt-5.6-sol', $u->info_llm['model']);
        $this->assertFalse($u->aktif, 'rancangan LLM tidak pernah langsung berlaku');
        Process::assertRan(function (PendingProcess $p) use ($u) {
            $permintaan = json_decode($p->input, true);

            return $permintaan['perintah'] === 'usulkan' && $permintaan['lapisan'] === 'perusahaan' && $permintaan['catatan'] === 'berlaku Juli'
                && $permintaan['pdf'] === Storage::disk('local')->path($u->path_pdf) && $permintaan['model'] === 'gpt-5.6-sol'
                && $p->environment['OPENAI_API_KEY'] === 'sk-uji' && $p->environment['ANTHROPIC_API_KEY'] === false
                && $p->environment['DB_PASSWORD'] === false && $p->environment['APP_KEY'] === false && $p->timeout === 600;
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
            'nama' => self::nama($u), 'berkas_tambahan' => [], 'lapisan' => 'perusahaan']);
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
        $this->palsukanJembatan(['periksa' => ['ok' => false, 'jenis' => 'kesalahan_kb', 'pesan' => 'fakta px_transport tidak dihasilkan']]);
        $this->post("/kb/{$u->id}/aktif")->assertSessionHas('error');
        $this->assertTrue($u->refresh()->aktif);

        $this->palsukanJembatan(['periksa' => self::jawabPeriksa(), 'validasi' => ['ok' => true, 'validasi' => self::validasiLolos()]]);
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

    public function test_nonaktifkan_ditolak_bila_kb_sisanya_gagal_diperiksa(): void
    {
        $this->masuk();
        $u = $this->kbAktif();
        $this->palsukanJembatan(['periksa' => self::jawabPeriksa(false, ['0002_lembur.yaml: fakta px_transport tidak dihasilkan aturan mana pun'])]);

        $this->post("/kb/{$u->id}/aktif")
            ->assertSessionHas('error', fn (string $m) => str_contains($m, 'berkas lain mungkin bergantung padanya')
                && str_contains($m, 'px_transport tidak dihasilkan aturan mana pun'));
        $this->assertTrue($u->refresh()->aktif);
        Process::assertRan(fn (PendingProcess $p) => json_decode($p->input, true) == ['perintah' => 'periksa', 'berkas_tambahan' => []]);

        $this->palsukanJembatan(['periksa' => self::jawabPeriksa()]);
        $this->post("/kb/{$u->id}/aktif")->assertSessionHas('success');
        $this->assertFalse($u->refresh()->aktif);
    }

    public function test_halaman_mesin_memakai_periksa_bila_ada_berkas_tambahan(): void
    {
        $this->masuk();
        $info = ['ok' => true, 'audit' => ['versi_engine' => '1.0', 'tanggal_kebaruan_kb' => '2026-01-01', 'versi_kb' => 'abc',
            'hash_tabel' => ['ter_a' => str_repeat('a', 64)], 'status_verifikasi_tabel' => ['ter_a' => 'double_entry']]];

        $this->palsukanJembatan(['info' => $info]);
        $this->get('/mesin')->assertOk()->assertSee('Engine siap');
        Process::assertNotRan(fn (PendingProcess $p) => json_decode($p->input, true)['perintah'] === 'periksa');

        $this->kbAktif();
        $this->palsukanJembatan(['info' => $info, 'periksa' => self::jawabPeriksa(false, ['0001_transport_2026.yaml: parameter tidak dikenal: x'])]);
        $this->get('/mesin')->assertOk()->assertDontSee('Engine siap')
            ->assertSee('tidak dapat dimuat atau dihitung')->assertSee('parameter tidak dikenal: x');

        $this->palsukanJembatan(['info' => $info, 'periksa' => self::jawabPeriksa()]);
        $this->get('/mesin')->assertOk()->assertSee('Engine siap')->assertSee('2023, 2024, 2025, 2026');
    }

    public function test_proses_yang_macet_ditandai_gagal(): void
    {
        $this->masuk();
        config(['payroll.llm_timeout' => 600]);
        $kosong = ['status' => 'diproses', 'usulan' => null, 'yaml' => null, 'validasi' => null, 'valid' => null, 'info_llm' => null];
        $mundur = fn (UsulanKb $u, int $detik) => UsulanKb::query()->toBase()->where('id', $u->id)->update(['updated_at' => now()->subSeconds($detik)]);

        $berjalan = $this->usulan($kosong);
        $mundur($berjalan, 200);       // masih dalam batas waktu LLM: tetap diproses, petunjuk pekerja tampil
        $this->getJson("/kb/{$berjalan->id}/status")->assertJson(['status' => 'diproses', 'selesai' => false])
            ->assertJsonPath('berjalan_detik', fn (int $d) => $d >= 200);
        $this->get("/kb/{$berjalan->id}")->assertOk()->assertSee('mb-0 " id="petunjukLama"', false);

        $mundur($berjalan, 600 + 121);
        $this->getJson("/kb/{$berjalan->id}/status")->assertJson(['status' => 'gagal', 'selesai' => true]);
        $this->assertSame(UsulanKb::PESAN_MACET, $berjalan->refresh()->pesan_galat);

        $lain = $this->usulan($kosong);
        $this->get("/kb/{$lain->id}")->assertOk()->assertSee('mb-0 d-none" id="petunjukLama"', false);
        $mundur($lain, 600 + 121);
        $this->get("/kb/{$lain->id}")->assertOk()->assertSee('Dokumen gagal dibaca')->assertSee('pekerja antrean berhenti di tengah jalan')
            ->assertSee('Baca ulang');
        $this->assertSame('gagal', $lain->refresh()->status);
    }

    public function test_unggahan_antre_dapat_dibatalkan(): void
    {
        $this->masuk();
        Storage::fake('local');
        Storage::disk('local')->put('kb_usulan/pp.pdf', '%PDF-1.4');
        $kosong = ['status' => 'antre', 'usulan' => null, 'yaml' => null, 'validasi' => null, 'valid' => null, 'info_llm' => null];
        $u = $this->usulan($kosong);

        $this->get("/kb/{$u->id}")->assertOk()->assertSee('Batalkan unggahan ini?');
        $this->delete("/kb/{$u->id}")->assertRedirect('/kb')->assertSessionHas('success', fn (string $m) => str_contains($m, 'dibatalkan'));
        $this->assertSame(0, UsulanKb::count());
        Storage::disk('local')->assertMissing('kb_usulan/pp.pdf');

        // job yang menyusul untuk usulan yang sudah dibatalkan berhenti tanpa memanggil LLM
        $this->palsukanJembatan([]);
        (new ProsesUsulanKb($u->id))->handle(app(MesinPajak::class));
        Process::assertNothingRan();

        // usulan yang diambil job tepat sebelum dihapus tidak kehilangan PDF-nya
        Storage::disk('local')->put('kb_usulan/pp.pdf', '%PDF-1.4');
        $diambil = $this->usulan($kosong);
        UsulanKb::whereKey($diambil->id)->update(['status' => 'diproses']);
        $this->assertFalse(app(PenerapanKb::class)->hapus($diambil));
        $this->assertSame(1, UsulanKb::count());
        Storage::disk('local')->assertExists('kb_usulan/pp.pdf');
    }

    public function test_job_hanya_menyimpan_hasil_bila_usulan_masih_diproses(): void
    {
        Storage::fake('local');
        Log::spy();
        $kosong = ['status' => 'antre', 'usulan' => null, 'yaml' => null, 'validasi' => null, 'valid' => null, 'info_llm' => null];
        $jawabSambil = function (callable $sambil) {
            Process::fake(['*' => function () use ($sambil) {
                $sambil();

                return Process::result(output: json_encode(self::jawabUsulkan()));
            }]);
        };

        // ditandai macet/gagal oleh permintaan lain selagi LLM membaca: hasil yang terlambat dibuang
        $u = $this->usulan($kosong);
        $jawabSambil(fn () => UsulanKb::whereKey($u->id)->update(['status' => 'gagal', 'pesan_galat' => 'macet']));
        (new ProsesUsulanKb($u->id))->handle(app(MesinPajak::class));
        $this->assertSame(['gagal', 'macet', null], [$u->refresh()->status, $u->pesan_galat, $u->yaml]);
        Log::shouldHaveReceived('info')->withArgs(fn (string $m, array $c) => str_contains($m, 'dibuang') && $c['usulan'] === $u->id);

        // berhasil: pesan galat yang tersisa dihapus, log tanpa isi dokumen
        $v = $this->usulan($kosong);
        $jawabSambil(fn () => UsulanKb::whereKey($v->id)->update(['pesan_galat' => 'sisa percobaan lama']));
        (new ProsesUsulanKb($v->id))->handle(app(MesinPajak::class));
        $this->assertSame(['siap_tinjau', null, self::YAML], [$v->refresh()->status, $v->pesan_galat, $v->yaml]);
        $this->assertSame('PPT-TRANSPORT-01', $v->validasi['isi']['aturan'][0]['id']);
        Log::shouldHaveReceived('info')->withArgs(fn (string $m, array $c) => $m === 'Usulan KB selesai dibaca' && $c['usulan'] === $v->id
            && $c['model'] === 'gpt-5.6-sol' && $c['token_masuk'] === 21_000 && is_int($c['durasi_detik']) && ! isset($c['yaml']));

        // bukan antre (mis. sudah selesai): tidak diproses ulang
        (new ProsesUsulanKb($v->id))->handle(app(MesinPajak::class));
        Process::assertRanTimes(fn (PendingProcess $p) => json_decode($p->input, true)['perintah'] === 'usulkan', 2);
    }

    public function test_kegagalan_job_diterjemahkan(): void
    {
        config(['payroll.llm_timeout' => 600]);
        Log::spy();
        $kasus = [
            [new MaxAttemptsExceededException('ProsesUsulanKb has been attempted too many times.'), ProsesUsulanKb::PESAN_PEKERJA_BERHENTI],
            [new ProcessTimedOutException(new SymfonyTimeout(new SymfonyProcess(['python']), SymfonyTimeout::TYPE_GENERAL), new FakeProcessResult),
                'Membaca dokumen melebihi batas waktu (600 detik).'],
            [new TimeoutExceededException('ProsesUsulanKb has timed out.'), 'Membaca dokumen melebihi batas waktu (660 detik).'],
            [new \RuntimeException('disk penuh'), 'Proses berhenti: disk penuh'],
        ];
        foreach ($kasus as [$e, $pesan]) {
            $u = $this->usulan(['status' => 'diproses']);
            (new ProsesUsulanKb($u->id))->failed($e);
            $this->assertSame(['gagal', $pesan], [$u->refresh()->status, $u->pesan_galat]);
        }
        Log::shouldHaveReceived('warning')->times(4);
    }

    public function test_halaman_tinjau_tahan_terhadap_isi_validasi_rusak(): void
    {
        $this->masuk();
        $this->rootSementara();
        $u = $this->usulan();

        // alur nyata: admin menyimpan YAML rusak, engine menolak dan isi berbentuk tak terduga
        $this->palsukanJembatan(['validasi' => ['ok' => true, 'validasi' => ['ok' => false, 'galat' => ['YAML tidak dapat dibaca: baris 2'],
            'peringatan' => [], 'ringkasan' => [], 'isi' => ['aturan' => 'rusak', 'komponen' => [1, 2]], 'masukan' => [], 'dampak' => []]]]);
        $this->put("/kb/{$u->id}/yaml", ['yaml' => "aturan: rusak\nkomponen: [1, 2]"])->assertSessionHas('warning');
        $this->get("/kb/{$u->id}")->assertOk()->assertSee('Belum lolos')->assertSee('YAML tidak dapat dibaca: baris 2')
            ->assertDontSee('Aturan yang diusulkan');

        // bentuk apa pun (dari LLM atau engine) tidak boleh membuat HTTP 500
        $rusak = [
            ['ok' => false, 'galat' => ['x', ['bukan teks']], 'peringatan' => 'bukan daftar', 'ringkasan' => 'x', 'isi' => ['aturan' => [['id' => ['x']]]],
                'masukan' => [['kunci' => ['x'], 'bawaan' => ['y'], 'pilihan' => 'z', 'aturan' => 'a'], 'x'], 'perubahan' => 'x', 'belum_teruji' => [1, ['aturan' => ['y']]],
                'dampak' => [['tahun' => [2026], 'sebelum' => 'x', 'sesudah' => ['bruto_setahun' => '1'], 'nilai_contoh' => 'x', 'fakta_baru' => ['a' => ['b']]]]],
            self::validasiLolos(['ringkasan' => ['lapisan' => ['x'], 'aturan' => '1'], 'isi' => [
                'aturan' => [['id' => ['x'], 'berlaku' => '2026', 'maka' => ['y'], 'jika' => 5, 'pembulatan' => ['z']], 'bukan rekaman'],
                'komponen' => [['fakta' => ['a'], 'kategori' => 1]], 'parameter' => [['nama' => 'p', 'nilai' => ['x'], 'berlaku' => ['mulai' => ['x']]]],
                'klasifikasi_wajib' => 'x', 'pembulatan' => [['satuan' => 'x', 'mode' => ['m']]]]]),
            self::validasiLolos(['isi' => 'bukan objek', 'dampak' => 'x', 'masukan' => [['tipe' => ['x']]]]),
            'bukan objek',
        ];
        foreach ($rusak as $validasi) {
            $u->update(['validasi' => $validasi, 'usulan' => ['ringkasan' => ['x'], 'catatan_peninjau' => 'x', 'rujukan' => ['x', ['bagian' => ['y']]],
                'id_berkas' => ['x'], 'dapat_dikodifikasi' => 'tidak'], 'info_llm' => ['model' => ['x'], 'token_masuk' => ['y']]]);
            $this->get("/kb/{$u->id}")->assertOk();
        }
    }

    public function test_halaman_tinjau_menampilkan_lapisan_perubahan_dan_aturan_belum_teruji(): void
    {
        $this->masuk();
        $biasa = $this->usulan();
        $this->get("/kb/{$biasa->id}")->assertOk()->assertSee('Lolos.')->assertDontSee('berbeda dari pilihan unggah')
            ->assertDontSee('Yang diubah rancangan ini')->assertSee('lapisan perusahaan');

        $u = $this->usulan(['validasi' => self::validasiLolos([
            'ringkasan' => ['lapisan' => 'regulasi', 'aturan' => 2, 'komponen' => 0, 'masukan' => 1, 'parameter' => 1, 'pembulatan' => 0],
            'perubahan' => [['jenis' => 'parameter', 'teks' => 'ptkp_tk0: 54000000 menjadi 60000000 mulai 2026-07-01'],
                ['jenis' => 'aturan', 'teks' => 'PX-THP-01 diganti oleh aturan berkas ini']],
            'belum_teruji' => [['aturan' => 'PPT-TRANSPORT-02', 'alasan' => 'syarat jika tidak terpenuhi pada pegawai contoh']],
        ])]);
        $this->get("/kb/{$u->id}")->assertOk()
            ->assertSee('Lapisan di berkas: regulasi (berbeda dari pilihan unggah)')
            ->assertSee('Yang diubah rancangan ini')->assertSee('ptkp_tk0: 54000000 menjadi 60000000 mulai 2026-07-01')
            ->assertSee('PX-THP-01 diganti oleh aturan berkas ini')
            ->assertSee('Aturan belum teruji')->assertSee('PPT-TRANSPORT-02')->assertSee('syarat jika tidak terpenuhi pada pegawai contoh')
            ->assertSee('Lolos pemeriksaan bentuk, tetapi ada')->assertSee('1 hal yang perlu diperiksa sebelum menerapkan.')
            ->assertDontSee('Lolos.</strong>', false)
            ->assertSee('Rancangan ini mengubah 2 hal yang sudah ada di KB (1 parameter, 1 aturan).');
    }

    public function test_rahasia_tidak_diwariskan_ke_proses_jembatan(): void
    {
        // mekanisme: nilai false pada env Process menghapus variabel yang diwarisi dari PHP (proses nyata, bukan tiruan).
        // Symfony Process mewariskan seluruh $_ENV, tempat Dotenv menaruh isi .env (termasuk DB_PASSWORD dan kunci API).
        $_ENV['PAYROLL_UJI_RAHASIA'] = 'bocor';
        try {
            $skrip = ['-r', 'echo getenv("PAYROLL_UJI_RAHASIA") === false ? "hilang" : "ada";'];
            $this->assertSame('ada', Process::run([PHP_BINARY, ...$skrip])->output());
            $this->assertSame('hilang', Process::env(['PAYROLL_UJI_RAHASIA' => false])->run([PHP_BINARY, ...$skrip])->output());
        } finally {
            unset($_ENV['PAYROLL_UJI_RAHASIA']);
        }

        $semuaDihapus = fn (PendingProcess $p, array $kecuali = []) => collect(MesinPajak::RAHASIA)
            ->diff($kecuali)->every(fn ($k) => ($p->environment[$k] ?? null) === false);
        $this->palsukanJembatan(['masukan' => ['ok' => true, 'masukan' => [], 'komponen' => []],
            'usulkan' => self::jawabUsulkan(), 'periksa' => self::jawabPeriksa()]);
        app(MesinPajak::class)->masukan([]);
        app(MesinPajak::class)->periksa([]);
        Process::assertRan(fn (PendingProcess $p) => json_decode($p->input, true)['perintah'] === 'masukan' && $semuaDihapus($p)
            && $p->environment['PYTHONIOENCODING'] === 'utf-8');
        Process::assertRan(fn (PendingProcess $p) => json_decode($p->input, true)['perintah'] === 'periksa' && $semuaDihapus($p));

        config(['payroll.llm_kunci_env' => 'ANTHROPIC_API_KEY', 'payroll.llm_kunci' => 'sk-ant-uji']);
        app(MesinPajak::class)->usulkan('/tmp/pp.pdf', 'perusahaan', null);
        Process::assertRan(fn (PendingProcess $p) => json_decode($p->input, true)['perintah'] === 'usulkan'
            && $p->environment['ANTHROPIC_API_KEY'] === 'sk-ant-uji' && $semuaDihapus($p, ['ANTHROPIC_API_KEY']));
    }

    public function test_kegagalan_jembatan_dicatat_tanpa_isi_permintaan(): void
    {
        Log::spy();
        Process::fake(['*' => Process::result(output: json_encode(['ok' => false, 'jenis' => 'kesalahan_kb', 'pesan' => 'aturan duplikat']),
            errorOutput: str_repeat('x', 2000).'jejak akhir', exitCode: 2)]);
        try {
            app(MesinPajak::class)->validasi("lapisan: perusahaan\n# isi-rahasia-dokumen\n", 'x.yaml', []);
            $this->fail('validasi yang ditolak engine harus melempar MesinTidakTersedia');
        } catch (MesinTidakTersedia $e) {
            $this->assertSame('kesalahan_kb: aturan duplikat', $e->getMessage());
        }
        Log::shouldHaveReceived('warning')->once();
        Log::shouldHaveReceived('warning')->withArgs(fn (string $m, array $c) => $c['perintah'] === 'validasi' && $c['kode_keluar'] === 2
            && $c['sebab'] === 'kesalahan_kb' && is_int($c['durasi_ms']) && mb_strlen($c['stderr']) === 1500
            && str_contains($c['stderr'], 'jejak akhir') && ! str_contains(json_encode($c), 'isi-rahasia-dokumen'));
    }

    public function test_berkas_aktif_dipulihkan_dari_database(): void
    {
        $u = $this->kbAktif();
        $kb = app(KbTambahan::class);
        $path = $kb->absolut($u->nama_berkas);
        Log::spy();

        unlink($path);      // klon baru / restore database tanpa folder kb/tambahan
        $this->assertSame(['kb/tambahan/0001_transport_2026.yaml'], $kb->berkasAktif());
        $this->assertSame(self::YAML, file_get_contents($path));
        Log::shouldHaveReceived('warning')->withArgs(fn (string $m, array $c) => str_contains($m, 'hilang') && $c['usulan'] === $u->id);

        file_put_contents($path, "lapisan: perusahaan\nid: diubah_di_disk\n");
        $kb->berkasAktif();
        $this->assertSame(self::YAML, file_get_contents($path));
        Log::shouldHaveReceived('warning')->withArgs(fn (string $m) => str_contains($m, 'berbeda'));

        // berkas yang sama dengan database tidak ditulis ulang
        $kb->berkasAktif();
        Log::shouldHaveReceived('warning')->twice();
    }

    public function test_batas_unggahan(): void
    {
        $this->masuk();
        Queue::fake();
        Storage::fake('local');
        $this->assertSame([8 * 1024 ** 2, 1024 ** 3, 512 * 1024, 100, 0, 0], array_map([UnggahPeraturanRequest::class, 'bita'], ['8M', '1g', '512K', '100', '0', '']));
        $batas = UnggahPeraturanRequest::batasEfektif();
        $this->assertLessThanOrEqual(20 * 1024 ** 2, $batas);
        $this->get('/kb')->assertOk()->assertSee('Paling besar '.BasisPengetahuanController::ukuran($batas));

        $isian = ['judul' => 'PP 2026', 'lapisan' => 'perusahaan'];
        $this->post('/kb', $isian + ['pdf' => UploadedFile::fake()->create('pp.pdf', 20481, 'application/pdf')])
            ->assertSessionHasErrors(['pdf' => 'PDF paling besar 20 MB; pecah dokumen bila lebih besar.']);

        // ditolak PHP (upload_max_filesize): pesan menjelaskan batas php.ini
        $sementara = tempnam(sys_get_temp_dir(), 'pdf');
        file_put_contents($sementara, '%PDF-1.4');
        $this->post('/kb', $isian + ['pdf' => new UploadedFile($sementara, 'pp.pdf', 'application/pdf', UPLOAD_ERR_INI_SIZE, true)])
            ->assertSessionHasErrors('pdf');
        $this->assertStringContainsString('upload_max_filesize', session('errors')->first('pdf'));
        @unlink($sementara);

        // melebihi post_max_size: kembali ke form dengan pesan, bukan halaman 413/419
        $maks = UnggahPeraturanRequest::bita((string) ini_get('post_max_size'));
        if ($maks > 0) {
            $this->from('/kb')->call('POST', '/kb', [], [], [], ['CONTENT_LENGTH' => (string) ($maks + 1)])
                ->assertRedirect('/kb')->assertSessionHas('error', fn (string $m) => str_contains($m, 'post_max_size'));
        }
        $this->assertSame(0, UsulanKb::count());
        Queue::assertNothingPushed();
    }

    public function test_pengaman_database_uji(): void
    {
        $gagal = function (): ?string {
            try {
                $this->pastikanDatabaseUji();
            } catch (AssertionFailedError $e) {
                return $e->getMessage();
            }

            return null;
        };
        $this->assertNull($gagal(), 'SQLite :memory: (phpunit.xml) diizinkan');

        config(['database.connections.sqlite.database' => database_path('database.sqlite')]);
        $this->assertStringContainsString('Uji dihentikan', (string) $gagal());

        config(['database.default' => 'pgsql', 'database.connections.pgsql.database' => 'its_pph21']);
        $this->assertNotNull($gagal(), 'database aplikasi tidak boleh dipakai uji');
        putenv('PAYROLL_UJI_PGSQL=1');
        $_ENV['PAYROLL_UJI_PGSQL'] = $_SERVER['PAYROLL_UJI_PGSQL'] = '1';
        try {
            $this->assertNotNull($gagal(), 'tanpa akhiran _uji tetap ditolak');
            config(['database.connections.pgsql.database' => 'its_pph21_uji']);
            $this->assertNull($gagal());
        } finally {
            putenv('PAYROLL_UJI_PGSQL');
            unset($_ENV['PAYROLL_UJI_PGSQL'], $_SERVER['PAYROLL_UJI_PGSQL']);
            config(['database.default' => 'sqlite', 'database.connections.sqlite.database' => ':memory:']);
        }
    }
}
