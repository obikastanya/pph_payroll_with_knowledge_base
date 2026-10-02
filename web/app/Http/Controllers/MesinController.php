<?php

namespace App\Http\Controllers;

use App\Payroll\MesinPajak;
use App\Payroll\MesinTidakTersedia;
use Illuminate\View\View;

class MesinController extends Controller
{
    public function index(MesinPajak $mesin): View
    {
        try {
            $info = $mesin->info();
            $galat = null;
        } catch (MesinTidakTersedia $e) {
            $info = null;
            $galat = $e->getMessage();
        }

        return view('mesin.index', [
            'info' => $info,
            'galat' => $galat,
            'konfigurasi' => [
                'Folder engine (PAYROLL_ROOT)' => config('payroll.root'),
                'Python (PAYROLL_PYTHON)' => config('payroll.python'),
                'Batas waktu (detik)' => config('payroll.timeout'),
                'KLU pemberi kerja (PAYROLL_KLU)' => config('payroll.klu') ?? '— tidak diketahui (fasilitas DTP tidak diterapkan)',
                'Tahun pajak yang dibuka' => config('payroll.tahun_min').'–'.config('payroll.tahun_max'),
            ],
        ]);
    }
}
