<?php

namespace Tests\Feature;

use App\Models\PayrollTahun;
use App\Models\Pegawai;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class PegawaiTest extends TestCase
{
    use RefreshDatabase;

    public function test_tamu_diarahkan_ke_login(): void
    {
        foreach (['/', '/pegawai', '/mesin'] as $url) {
            $this->get($url)->assertRedirect('/login');
        }
    }

    public function test_login_dan_kredensial_salah(): void
    {
        $user = User::factory()->create(['password' => 'rahasia123']);
        $this->post('/login', ['email' => $user->email, 'password' => 'salah'])->assertSessionHasErrors('email');
        $this->post('/login', ['email' => $user->email, 'password' => 'rahasia123'])->assertRedirect('/');
        $this->assertAuthenticatedAs($user);
    }

    public function test_tambah_ubah_hapus_pegawai(): void
    {
        $this->masuk();
        $this->post('/pegawai', ['nomor_induk' => 'P-001', 'nama' => 'Siti', 'jenis_kelamin' => 'P', 'punya_npwp' => '0',
            'tanggal_masuk' => '2022-03-01'])->assertRedirect();
        $p = Pegawai::firstWhere('nomor_induk', 'P-001');
        $this->assertFalse($p->punya_npwp);
        $this->get("/pegawai/{$p->id}")->assertOk()->assertSee('Siti');

        $this->put("/pegawai/{$p->id}", ['nomor_induk' => 'P-001', 'nama' => 'Siti A', 'jenis_kelamin' => 'P', 'punya_npwp' => '1',
            'tanggal_masuk' => '2022-03-01', 'tanggal_berhenti' => '2026-09-15'])->assertRedirect();
        $this->assertTrue($p->fresh()->punya_npwp);
        $this->assertSame([1, 9], $p->fresh()->rentangBulan(2026));

        $this->delete("/pegawai/{$p->id}")->assertRedirect('/pegawai');
        $this->assertDatabaseMissing('pegawai', ['id' => $p->id]);
    }

    public function test_validasi_pegawai(): void
    {
        $this->masuk();
        $this->payroll(pegawai: ['nomor_induk' => 'DUP']);
        $this->post('/pegawai', ['nomor_induk' => 'DUP', 'nama' => '', 'jenis_kelamin' => 'X', 'tanggal_masuk' => '2024-05-01',
            'tanggal_berhenti' => '2024-01-01'])
            ->assertSessionHasErrors(['nomor_induk', 'nama', 'jenis_kelamin', 'tanggal_berhenti']);
    }

    public function test_hapus_pegawai_menghapus_payroll_dan_riwayat(): void
    {
        $this->masuk();
        $pt = $this->payroll();
        $pt->perhitungan()->create(['berhasil' => false, 'kasus' => 'null', 'jenis_galat' => 'x']);
        $this->delete("/pegawai/{$pt->pegawai_id}");
        $this->assertSame(0, PayrollTahun::count());
        $this->assertDatabaseCount('payroll_bulan', 0);
        $this->assertDatabaseCount('perhitungan', 0);
    }
}
