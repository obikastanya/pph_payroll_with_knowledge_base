<?php

namespace Database\Seeders;

use App\Models\User;
use App\Payroll\ImporContoh;
use App\Payroll\MesinTidakTersedia;
use Illuminate\Database\Seeder;

/** Data demo lokal: satu admin + pegawai contoh dari dataset induk. Jangan dipakai di server produksi. */
class DatabaseSeeder extends Seeder
{
    public function run(ImporContoh $impor): void
    {
        User::firstOrCreate(['email' => 'admin@example.com'], ['name' => 'Admin Finance', 'password' => 'password']);
        $this->command?->info('Pengguna demo: admin@example.com / password (ganti dengan php artisan payroll:pengguna).');

        try {
            $dibuat = $impor->jalankan();
            $this->command?->info(count($dibuat).' pegawai contoh dimuat dari dataset.');
        } catch (MesinTidakTersedia $e) {
            $this->command?->warn('Pegawai contoh tidak dimuat, engine tidak dapat dipanggil: '.$e->getMessage());
        }
    }
}
