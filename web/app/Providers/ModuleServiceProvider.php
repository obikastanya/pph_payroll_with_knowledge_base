<?php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;

/**
 * Mendaftarkan service provider setiap module secara otomatis (modules/{Nama}/Providers/*.php),
 * sama seperti Base-Apps-Merdeka. Module baru cukup dibuat dengan `php artisan make:module {Nama}`.
 */
class ModuleServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        foreach (glob(base_path('modules/*/Providers/*.php')) as $file) {
            $moduleName = basename(dirname(dirname($file)));
            $providerClass = "Modules\\$moduleName\\Providers\\".basename($file, '.php');

            if (class_exists($providerClass)) {
                $this->app->register($providerClass);
            }
        }
    }
}
