<?php

use App\Models\User;
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\Validator;
use Modules\Payroll\Services\ImporContoh;
use Modules\Payroll\Services\MesinTidakTersedia;

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
