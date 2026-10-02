<?php

namespace Modules\BasisPengetahuan\Providers;

use Illuminate\Support\ServiceProvider;

class BasisPengetahuanServiceProvider extends ServiceProvider
{
    public function boot()
    {
        $this->loadRoutesFrom(base_path('modules/BasisPengetahuan/Routes/web/kb.php'));
        $this->loadViewsFrom(base_path('modules/BasisPengetahuan/Resources/views'), 'BasisPengetahuan');
    }

    public function register()
    {
        // Ikat otomatis setiap pasangan {Nama}Interface -> {Nama}Repository
        $repositoryPath = base_path('modules/BasisPengetahuan/Repositories');

        if (is_dir($repositoryPath)) {
            foreach (scandir($repositoryPath) as $file) {
                if (preg_match('/^(.+)Interface\.php$/', $file, $matches)) {
                    $interface = "Modules\\BasisPengetahuan\\Repositories\\{$matches[1]}Interface";
                    $repository = "Modules\\BasisPengetahuan\\Repositories\\{$matches[1]}Repository";

                    if (interface_exists($interface) && class_exists($repository)) {
                        $this->app->bind($interface, $repository);
                    }
                }
            }
        }
    }
}
