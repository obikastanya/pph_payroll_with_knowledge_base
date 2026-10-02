<?php

namespace Modules\Pegawai\Providers;

use Illuminate\Support\ServiceProvider;

class PegawaiServiceProvider extends ServiceProvider
{
    public function boot()
    {
        $this->loadRoutesFrom(base_path('modules/Pegawai/Routes/web/pegawai.php'));
        $this->loadViewsFrom(base_path('modules/Pegawai/Resources/views'), 'Pegawai');
    }

    public function register()
    {
        // Ikat otomatis setiap pasangan {Nama}Interface -> {Nama}Repository
        $repositoryPath = base_path('modules/Pegawai/Repositories');

        if (is_dir($repositoryPath)) {
            foreach (scandir($repositoryPath) as $file) {
                if (preg_match('/^(.+)Interface\.php$/', $file, $matches)) {
                    $interface = "Modules\\Pegawai\\Repositories\\{$matches[1]}Interface";
                    $repository = "Modules\\Pegawai\\Repositories\\{$matches[1]}Repository";

                    if (interface_exists($interface) && class_exists($repository)) {
                        $this->app->bind($interface, $repository);
                    }
                }
            }
        }
    }
}
