<?php

namespace Tests\Feature;

use App\Models\Payroll\PayrollTahun;
use App\Models\Payroll\Pegawai;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class PegawaiTest extends TestCase
{
    use RefreshDatabase;

    private const DATA = ['nomor_induk' => 'P-001', 'nama' => 'Siti', 'jenis_kelamin' => 'P', 'punya_npwp' => 0, 'tanggal_masuk' => '2022-03-01'];

    public function test_tamu_diarahkan_ke_login(): void
    {
        foreach (['/', '/dashboard', '/pegawai', '/pegawai/list', '/mesin'] as $url) {
            $this->get($url)->assertRedirect('/login');
        }
        $this->get('/login')->assertOk()->assertSee('Masuk dengan akun admin finance')
            ->assertSee('assets/img/bg-auth/auth-1.jpg', false)->assertSee('accessLoginGuide', false);
    }

    public function test_login_dan_kredensial_salah(): void
    {
        $user = User::factory()->create(['password' => 'rahasia123']);
        $this->post('/login', ['email' => $user->email, 'password' => 'salah'])->assertSessionHasErrors('email');
        $this->post('/login', ['email' => $user->email, 'password' => 'rahasia123'])->assertRedirect('/dashboard');
        $this->assertAuthenticatedAs($user);
        $this->get('/')->assertRedirect('/dashboard');
        $this->post('/logout')->assertRedirect('/login')->assertSessionHas('success', 'Anda telah keluar.');
        $this->assertGuest();
    }

    public function test_halaman_memakai_layout_dan_menu_sidebar(): void
    {
        $this->masuk();
        $this->get('/pegawai')->assertOk()
            ->assertSee('navbar-vertical', false)
            ->assertSee('Pegawai &amp; data HR', false)
            ->assertSee('active-mdka-nav', false)
            ->assertSee(route('mesin.index'), false);
    }

    public function test_tambah_ubah_hapus_pegawai_lewat_json(): void
    {
        $this->masuk();
        $id = $this->postJson('/pegawai', self::DATA)->assertOk()->assertJsonPath('message', 'Pegawai ditambahkan.')->json('data.id');
        $p = Pegawai::findOrFail($id);
        $this->assertFalse($p->punya_npwp);

        $this->getJson("/pegawai/{$id}")->assertOk()->assertJsonPath('data.nama', 'Siti')->assertJsonPath('data.tanggal_berhenti', null);
        $this->get("/pegawai/{$id}/detail")->assertOk()->assertSee('Siti')->assertSee('Belum ada data HR');

        $this->putJson("/pegawai/{$id}", ['nama' => 'Siti A', 'punya_npwp' => 1, 'tanggal_berhenti' => '2026-09-15'] + self::DATA)->assertOk();
        $this->assertTrue($p->fresh()->punya_npwp);
        $this->assertSame([1, 9], $p->fresh()->rentangBulan(2026));

        $this->deleteJson("/pegawai/{$id}")->assertOk();
        $this->assertDatabaseMissing('pegawai', ['id' => $id]);
    }

    public function test_daftar_json_cari_filter_urut_dan_paginasi(): void
    {
        $this->masuk();
        $this->payroll(pegawai: ['nomor_induk' => 'A-1', 'nama' => 'Budi']);
        $this->payroll(pegawai: ['nomor_induk' => 'A-2', 'nama' => 'Ani', 'tanggal_berhenti' => '2024-06-30']);
        $this->payroll(pegawai: ['nomor_induk' => 'A-3', 'nama' => 'Citra', 'jenis_kelamin' => 'P']);

        $this->getJson('/pegawai/list')->assertOk()->assertJsonPath('meta.total', 3)->assertJsonPath('data.0.nomor_induk', 'A-1')
            ->assertJsonPath('data.0.data_hr_terakhir.tahun', 2024);
        $this->getJson('/pegawai/list?search=cit')->assertJsonPath('meta.total', 1)->assertJsonPath('data.0.nama', 'Citra');
        $this->getJson('/pegawai/list?status=berhenti')->assertJsonPath('meta.total', 1)->assertJsonPath('data.0.berhenti', true);
        $this->getJson('/pegawai/list?status=aktif&jenis_kelamin=P')->assertJsonPath('meta.total', 1);
        $this->getJson('/pegawai/list?orderBy=nama&orderDir=desc')->assertJsonPath('data.0.nama', 'Citra');
        // kolom urut di luar daftar putih diabaikan (tidak pernah masuk SQL)
        $this->getJson('/pegawai/list?orderBy=id;drop%20table%20pegawai&orderDir=desc')->assertOk()->assertJsonPath('data.0.nomor_induk', 'A-3');
        $this->getJson('/pegawai/list?paginated=2&page=2')->assertJsonPath('meta.last_page', 2)->assertJsonCount(1, 'data');
    }

    public function test_validasi_pegawai_json(): void
    {
        $this->masuk();
        $this->payroll(pegawai: ['nomor_induk' => 'DUP']);
        $this->postJson('/pegawai', ['nomor_induk' => 'DUP', 'nama' => '', 'jenis_kelamin' => 'X', 'tanggal_masuk' => '2024-05-01',
            'tanggal_berhenti' => '2024-01-01'])
            ->assertStatus(422)
            ->assertJsonValidationErrors(['nomor_induk', 'nama', 'jenis_kelamin', 'tanggal_berhenti']);
    }

    public function test_hapus_pegawai_menghapus_payroll_dan_riwayat(): void
    {
        $this->masuk();
        $pt = $this->payroll();
        $pt->perhitungan()->create(['berhasil' => false, 'kasus' => 'null', 'jenis_galat' => 'x']);
        $this->deleteJson("/pegawai/{$pt->pegawai_id}")->assertOk();
        $this->assertSame(0, PayrollTahun::count());
        $this->assertDatabaseCount('payroll_bulan', 0);
        $this->assertDatabaseCount('perhitungan', 0);
    }
}
