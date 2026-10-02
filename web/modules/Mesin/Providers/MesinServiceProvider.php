<?php

namespace Modules\Mesin\Providers;

use Illuminate\Support\ServiceProvider;

class MesinServiceProvider extends ServiceProvider
{
    public function boot()
    {
        $this->loadRoutesFrom(base_path('modules/Mesin/Routes/web/mesin.php'));
        $this->loadViewsFrom(base_path('modules/Mesin/Resources/views'), 'Mesin');
    }

    public function register()
    {
        //
    }
}
