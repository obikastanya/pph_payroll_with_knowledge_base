<?php

namespace Modules\Mesin\Http\Controllers;

use App\Http\Controllers\Controller;
use Illuminate\View\View;
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

    public function index(MesinPajak $mesin): View
    {
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
                'Tahun pajak yang dibuka' => config('payroll.tahun_min').'–'.config('payroll.tahun_max'),
            ],
        ]);
    }
}
