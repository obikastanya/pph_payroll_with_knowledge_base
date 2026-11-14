<?php

namespace App\Providers;

use Illuminate\Support\Facades\Route;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /** Id di URL = kunci primer bigint: 1-18 digit tanpa nol di depan (selalu di bawah batas bigint). */
    public const POLA_ID = '[1-9][0-9]{0,17}';

    /**
     * Register any application services.
     */
    public function register(): void
    {
        //
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        // Didaftarkan sebelum route module dimuat (provider module boot sesudah provider ini). Id lain langsung 404:
        // PostgreSQL menolak "abc" atau 99999999999999999999 sebagai bigint (galat 500), SQLite sekadar tidak menemukannya.
        Route::patterns(array_fill_keys(['pegawai', 'payroll', 'usulan'], self::POLA_ID));
    }
}
