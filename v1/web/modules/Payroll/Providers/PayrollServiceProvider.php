<?php

namespace Modules\Payroll\Providers;

use Illuminate\Support\ServiceProvider;

class PayrollServiceProvider extends ServiceProvider
{
    public function boot()
    {
        $this->loadRoutesFrom(base_path('modules/Payroll/Routes/web/payroll.php'));
        $this->loadViewsFrom(base_path('modules/Payroll/Resources/views'), 'Payroll');
    }

    public function register()
    {
        // Ikat otomatis setiap pasangan {Nama}Interface -> {Nama}Repository
        $repositoryPath = base_path('modules/Payroll/Repositories');

        if (is_dir($repositoryPath)) {
            foreach (scandir($repositoryPath) as $file) {
                if (preg_match('/^(.+)Interface\.php$/', $file, $matches)) {
                    $interface = "Modules\\Payroll\\Repositories\\{$matches[1]}Interface";
                    $repository = "Modules\\Payroll\\Repositories\\{$matches[1]}Repository";

                    if (interface_exists($interface) && class_exists($repository)) {
                        $this->app->bind($interface, $repository);
                    }
                }
            }
        }
    }
}
