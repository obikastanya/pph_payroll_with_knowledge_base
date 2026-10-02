<?php

namespace Modules\Mesin\Http\Controllers;

use App\Http\Controllers\Controller;
use Illuminate\View\View;
use Modules\Payroll\Services\KbTambahan;
use Modules\Payroll\Services\MesinPajak;
use Modules\Payroll\Services\MesinTidakTersedia;

/** Status engine KB (Python): konfigurasi jembatan, versi engine & commit KB, status verifikasi tabel parameter. */
class MesinController extends Controller
{
    protected $pageTitle;

    protected $menuItems;

    public function __construct()
    {
        $this->pageTitle = 'Mesin perhitungan';
        $this->menuItems = [
            ['url' => '/dashboard', 'label' => 'Dashboard', 'active' => false],
            ['url' => '/mesin', 'label' => 'Mesin perhitungan', 'active' => true],
        ];
    }

    public function index(MesinPajak $mesin, KbTambahan $kb): View
    {
        $tambahan = $kb->berkasAktif();
        try {
            $info = $mesin->info();
            $galat = null;
        } catch (MesinTidakTersedia $e) {
            $info = null;
            $galat = $e->getMessage();
        }

        return view('Mesin::index', [
            'pageTitle' => $this->pageTitle,
            'menuItems' => $this->menuItems,
            'info' => $info,
            'galat' => $galat,
            'konfigurasi' => [
                'Folder engine (PAYROLL_ROOT)' => config('payroll.root'),
                'Python (PAYROLL_PYTHON)' => config('payroll.python'),
                'Batas waktu (detik)' => config('payroll.timeout'),
                'KLU pemberi kerja (PAYROLL_KLU)' => config('payroll.klu') ?? '— tidak diketahui (fasilitas DTP tidak diterapkan)',
                'Lapisan kebijakan perusahaan' => config('payroll.nama_perusahaan').' (kb/perusahaan/perusahaan_x.yaml)',
                'Berkas KB tambahan aktif (menu Basis pengetahuan)' => $tambahan === [] ? '— tidak ada'
                    : implode(', ', $tambahan).' · sidik '.$kb->sidik($tambahan),
                'Asisten KB / LLM (PAYROLL_LLM_MODEL, '.config('payroll.llm_kunci_env').')' => config('payroll.llm_model')
                    .(config('payroll.llm_kunci') ? ' · kunci API terpasang' : ' · kunci API belum diatur'),
                'Tahun pajak yang dibuka' => config('payroll.tahun_min').'–'.config('payroll.tahun_max'),
            ],
        ]);
    }
}
