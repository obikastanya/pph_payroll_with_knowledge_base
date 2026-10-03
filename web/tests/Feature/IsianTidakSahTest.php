<?php

namespace Tests\Feature;

use App\Http\Middleware\BersihkanTeks;
use App\Models\Payroll\Pegawai;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\Request;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Process;
use Tests\Concerns\KbUji;
use Tests\TestCase;

/**
 * Isian yang lolos di SQLite tetapi membuat PostgreSQL galat 500: id di URL yang bukan bigint, ?tahun liar, byte NUL
 * dan UTF-8 tidak sah. Hasilnya harus 404, tahun bawaan, atau teks yang sudah dibersihkan.
 */
class IsianTidakSahTest extends TestCase
{
    use KbUji, RefreshDatabase;

    public function test_id_di_url_yang_bukan_bigint_menjadi_404(): void
    {
        $this->masuk();
        $pt = $this->payroll(2024);
        $u = $this->usulan();

        foreach (['abc', '0', '007', '1e3', '99999999999999999999'] as $id) {
            $this->get("/payroll/{$id}")->assertNotFound();
            $this->post("/payroll/{$id}/hitung")->assertNotFound();
            $this->get("/pegawai/{$id}")->assertNotFound();
            $this->get("/pegawai/{$id}/detail")->assertNotFound();
            $this->putJson("/pegawai/{$id}", [])->assertNotFound();
            $this->get("/pegawai/{$id}/payroll/create")->assertNotFound();
            $this->get("/kb/{$id}")->assertNotFound();
            $this->delete("/kb/{$id}")->assertNotFound();
        }
        // nol di depan id yang ada: SQLite tetap menemukannya, jadi yang menolak di sini adalah pola route
        $this->get("/payroll/0{$pt->id}")->assertNotFound();
        $this->get("/pegawai/0{$pt->pegawai_id}/detail")->assertNotFound();
        $this->get("/kb/0{$u->id}")->assertNotFound();
        $this->get("/payroll/{$pt->id}/slip/99999999999999999999")->assertNotFound();   // dulu TypeError pada int $bulan
        $this->get('/payroll/999999999999999999')->assertNotFound();                    // 18 digit: lolos pola, barisnya tidak ada

        $this->get("/payroll/{$pt->id}")->assertOk();
        $this->get("/pegawai/{$pt->pegawai_id}/detail")->assertOk();
        $this->getJson('/pegawai/list')->assertOk();
        $this->get("/kb/{$u->id}")->assertOk();
    }

    public function test_tahun_liar_di_query_jatuh_ke_tahun_bawaan(): void
    {
        $this->masuk();
        $pt = $this->payroll(2024);
        Process::fake();

        foreach (['abc', '99999999999', '-1', '2024.5', '2030'] as $t) {
            $this->get("/dashboard?tahun={$t}")->assertOk()->assertSee('Pegawai dengan data HR 2024');
            $this->getJson("/dashboard/list?tahun={$t}")->assertOk()->assertJsonPath('meta.total', 1);
            $this->get("/dashboard/ekspor?tahun={$t}")->assertOk()->assertDownload('rekap_payroll_2024.csv');
        }
        $this->get('/dashboard?tahun[]=2025')->assertOk()->assertSee('Pegawai dengan data HR 2024');

        // form tambah: tahun yang bukan pilihan (liar, di luar rentang, atau sudah diisi) -> pilihan pertama
        foreach (['abc', '99999999999', '2024'] as $t) {
            $this->get("/pegawai/{$pt->pegawai_id}/payroll/create?tahun={$t}")->assertOk()
                ->assertSee('<input type="hidden" name="tahun" value="2026">', false);
        }
        $this->get("/pegawai/{$pt->pegawai_id}/payroll/create?tahun=2023")->assertOk()
            ->assertSee('<input type="hidden" name="tahun" value="2023">', false);

        // hitung semua: tahun tidak sah -> pesan, engine tidak dipanggil
        foreach (['abc', '99999999999', '2030'] as $t) {
            $this->post('/dashboard/hitung', ['tahun' => $t])->assertRedirect()
                ->assertSessionHas('error', 'Tahun pajak tidak valid (pilih 2023–2026).');
        }
        Process::assertNothingRan();
    }

    public function test_byte_nul_dan_utf8_tidak_sah_dibersihkan(): void
    {
        $this->masuk();
        $this->post('/pegawai', ['nomor_induk' => "P-\0".'77', 'nama' => "Siti\xC3 A", 'jenis_kelamin' => 'P', 'punya_npwp' => 1,
            'tanggal_masuk' => '2022-03-01'])->assertOk();
        $p = Pegawai::sole();
        $this->assertSame(['P-77', 'Siti? A'], [$p->nomor_induk, $p->nama]);

        $this->getJson('/pegawai/list?search='.rawurlencode("Siti\0\xC3"))->assertOk();
        $this->getJson('/dashboard/list?search='.rawurlencode("\0\xFF"))->assertOk();
        $this->getJson('/kb/list?search='.rawurlencode("pp\0\xFE"))->assertOk();

        // larik bersarang ikut dibersihkan; kata sandi, nilai bukan teks, dan berkas unggahan tidak disentuh
        $r = Request::create('/x', 'POST', ['a' => ['b' => ["x\0y", "\xFF"]], 'password' => "rahasia\0", 'jumlah' => 5], [],
            ['berkas' => UploadedFile::fake()->create('pp.pdf', 1)]);
        (new BersihkanTeks)->handle($r, fn () => null);
        $this->assertSame([['b' => ['xy', '?']], "rahasia\0", 5], [$r->input('a'), $r->input('password'), $r->input('jumlah')]);
        $this->assertInstanceOf(UploadedFile::class, $r->file('berkas'));
    }
}
