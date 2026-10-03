<?php

use App\Models\User;
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\Validator;
use Modules\Payroll\Repositories\PayrollInterface;
use Modules\Payroll\Services\HitungTerhenti;
use Modules\Payroll\Services\ImporContoh;
use Modules\Payroll\Services\KunciHitungSemua;
use Modules\Payroll\Services\MesinTidakTersedia;
use Modules\Payroll\Services\Penghitung;

Artisan::command('payroll:impor-contoh', function (ImporContoh $impor) {
    try {
        $dibuat = $impor->jalankan();
    } catch (MesinTidakTersedia $e) {
        $this->error('Engine tidak dapat dipanggil: '.$e->getMessage());

        return 1;
    }
    $this->info($dibuat ? count($dibuat).' pegawai contoh dimuat: '.implode(', ', $dibuat) : 'Semua pegawai contoh sudah ada; tidak ada yang dimuat.');

    return 0;
})->purpose('Muat pegawai contoh dari dataset induk (Karyawan A + pegawai sintetis) lewat engine');

Artisan::command('payroll:hitung {tahun}', function (string $tahun, PayrollInterface $payroll, Penghitung $penghitung) {
    [$min, $maks] = [config('payroll.tahun_min'), config('payroll.tahun_max')];
    $tahun = filter_var($tahun, FILTER_VALIDATE_INT, ['options' => ['min_range' => $min, 'max_range' => $maks]]);
    if ($tahun === false) {
        $this->error("Tahun pajak tidak valid (pilih {$min}–{$maks}).");

        return 1;
    }
    $jumlah = $payroll->jumlahTahun($tahun);
    if ($jumlah === 0) {
        $this->error("Belum ada data HR untuk tahun {$tahun}.");

        return 1;
    }
    $kunci = KunciHitungSemua::ambil($tahun);
    if ($kunci === null) {
        $this->error(KunciHitungSemua::pesanTerkunci($tahun));

        return 1;
    }
    try {
        // sama dengan tombol Hitung semua di Dashboard; baris riwayat dicatat tanpa pengguna
        $hasil = $penghitung->hitungSemua($payroll->daftarHitung($tahun, $penghitung->ukuranBatch()), null,
            function (int $dicatat) use ($kunci, $jumlah) {
                $kunci->perpanjang();
                $this->line("{$dicatat} dari {$jumlah} pegawai tercatat ...");
            });
    } catch (HitungTerhenti $e) {
        $this->error("Engine gagal setelah {$e->dicatat} dari {$jumlah} pegawai tercatat: ".$e->getMessage());

        return 1;
    } finally {
        $kunci->lepas();
    }
    $this->info("Tahun {$tahun}: {$hasil['dihitung']} pegawai dihitung, {$hasil['gagal']} gagal.");

    return 0;
})->purpose('Hitung semua pegawai satu tahun pajak per batch, dengan kunci yang sama seperti tombol Hitung semua');

Artisan::command('payroll:pengguna {email} {nama}', function (string $email, string $nama) {
    $sandi = $this->secret('Kata sandi (min. 8 karakter)');
    $v = Validator::make(['email' => $email, 'password' => $sandi], ['email' => 'email', 'password' => 'required|min:8']);
    if ($v->fails()) {
        $this->error(implode(' ', $v->errors()->all()));

        return 1;
    }
    $user = User::updateOrCreate(['email' => $email], ['name' => $nama, 'password' => $sandi]);
    $this->info(($user->wasRecentlyCreated ? 'Pengguna dibuat: ' : 'Kata sandi diperbarui: ').$email);

    return 0;
})->purpose('Buat pengguna admin finance, atau ganti kata sandinya');
