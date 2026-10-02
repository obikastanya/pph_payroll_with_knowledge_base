<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Support\Facades\File;
use Illuminate\Support\Str;

/**
 * Kerangka module baru dengan struktur Base-Apps-Merdeka:
 * Http/Controllers, Http/Requests, Repositories (Interface + Repository), Providers, Resources/views, Routes/web.
 * Provider module terdaftar otomatis lewat App\Providers\ModuleServiceProvider.
 */
class MakeModule extends Command
{
    protected $signature = 'make:module {name? : Nama module, PascalCase (mis. Laporan)}';

    protected $description = 'Buat kerangka module baru di modules/';

    public function handle(): int
    {
        $nama = Str::studly((string) ($this->argument('name') ?: $this->ask('Nama module?')));
        if ($nama === '') {
            $this->error('Nama module tidak boleh kosong.');

            return self::FAILURE;
        }
        $dasar = base_path("modules/{$nama}");
        if (File::exists($dasar)) {
            $this->error("Module {$nama} sudah ada.");

            return self::FAILURE;
        }
        $rute = Str::kebab($nama);

        $berkas = [
            "Http/Controllers/{$nama}Controller.php" => $this->controller($nama, $rute),
            "Http/Requests/{$nama}Request.php" => $this->request($nama),
            "Repositories/{$nama}Interface.php" => $this->interface($nama),
            "Repositories/{$nama}Repository.php" => $this->repository($nama),
            "Providers/{$nama}ServiceProvider.php" => $this->provider($nama, $rute),
            "Routes/web/{$rute}.php" => $this->routes($nama, $rute),
            'Resources/views/index.blade.php' => $this->view($nama),
        ];
        foreach ($berkas as $path => $isi) {
            File::ensureDirectoryExists(dirname("{$dasar}/{$path}"));
            File::put("{$dasar}/{$path}", $isi);
            $this->line("  <info>dibuat</info> modules/{$nama}/{$path}");
        }
        $this->info("Module {$nama} siap: route '{$rute}.index' di /{$rute}. Tambahkan ke config/menu.php bila perlu tampil di sidebar.");

        return self::SUCCESS;
    }

    private function controller(string $nama, string $rute): string
    {
        return <<<PHP
        <?php

        namespace Modules\\{$nama}\\Http\\Controllers;

        use App\\Http\\Controllers\\Controller;
        use Exception;
        use Illuminate\\View\\View;
        use Modules\\{$nama}\\Repositories\\{$nama}Interface;

        class {$nama}Controller extends Controller
        {
            protected \$pageTitle;

            protected \$menuItems;

            public function __construct(private {$nama}Interface \$repository)
            {
                \$this->pageTitle = '{$nama}';
                \$this->menuItems = [
                    ['url' => '/dashboard', 'label' => 'Dashboard', 'active' => false],
                    ['url' => '/{$rute}', 'label' => '{$nama}', 'active' => true],
                ];
            }

            public function index(): View
            {
                try {
                    return view('{$nama}::index', [
                        'pageTitle' => \$this->pageTitle,
                        'menuItems' => \$this->menuItems,
                    ]);
                } catch (Exception \$e) {
                    throw \$e;
                }
            }
        }

        PHP;
    }

    private function request(string $nama): string
    {
        return <<<PHP
        <?php

        namespace Modules\\{$nama}\\Http\\Requests;

        use Illuminate\\Foundation\\Http\\FormRequest;

        class {$nama}Request extends FormRequest
        {
            public function rules(): array
            {
                return [];
            }
        }

        PHP;
    }

    private function interface(string $nama): string
    {
        return <<<PHP
        <?php

        namespace Modules\\{$nama}\\Repositories;

        interface {$nama}Interface
        {
            public function getAll();
        }

        PHP;
    }

    private function repository(string $nama): string
    {
        return <<<PHP
        <?php

        namespace Modules\\{$nama}\\Repositories;

        class {$nama}Repository implements {$nama}Interface
        {
            public function getAll()
            {
                return [];
            }
        }

        PHP;
    }

    private function provider(string $nama, string $rute): string
    {
        return <<<PHP
        <?php

        namespace Modules\\{$nama}\\Providers;

        use Illuminate\\Support\\ServiceProvider;

        class {$nama}ServiceProvider extends ServiceProvider
        {
            public function boot()
            {
                \$this->loadRoutesFrom(base_path('modules/{$nama}/Routes/web/{$rute}.php'));
                \$this->loadViewsFrom(base_path('modules/{$nama}/Resources/views'), '{$nama}');
            }

            public function register()
            {
                // Ikat otomatis setiap pasangan {Nama}Interface -> {Nama}Repository
                \$repositoryPath = base_path('modules/{$nama}/Repositories');

                if (is_dir(\$repositoryPath)) {
                    foreach (scandir(\$repositoryPath) as \$file) {
                        if (preg_match('/^(.+)Interface\\.php\$/', \$file, \$matches)) {
                            \$interface = "Modules\\\\{$nama}\\\\Repositories\\\\{\$matches[1]}Interface";
                            \$repository = "Modules\\\\{$nama}\\\\Repositories\\\\{\$matches[1]}Repository";

                            if (interface_exists(\$interface) && class_exists(\$repository)) {
                                \$this->app->bind(\$interface, \$repository);
                            }
                        }
                    }
                }
            }
        }

        PHP;
    }

    private function routes(string $nama, string $rute): string
    {
        return <<<PHP
        <?php

        use Illuminate\\Support\\Facades\\Route;
        use Modules\\{$nama}\\Http\\Controllers\\{$nama}Controller;

        Route::middleware(['web', 'auth'])->prefix('{$rute}')->name('{$rute}.')->group(function () {
            Route::get('/', [{$nama}Controller::class, 'index'])->name('index');
        });

        PHP;
    }

    private function view(string $nama): string
    {
        return <<<BLADE
        @extends('main.index')

        @section('page-title', '{$nama}')

        @section('content')
            <div class="row g-2">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body p-3">
                            Module {$nama}
                        </div>
                    </div>
                </div>
            </div>
        @endsection

        BLADE;
    }
}
