<?php

namespace App\Http\Controllers;

use App\Models\PayrollTahun;
use App\Payroll\MesinTidakTersedia;
use App\Payroll\Penghitung;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\View\View;
use Symfony\Component\HttpFoundation\StreamedResponse;

class RekapController extends Controller
{
    public function index(Request $request, Penghitung $penghitung): View
    {
        $tahunAda = PayrollTahun::query()->distinct()->orderByDesc('tahun')->pluck('tahun')->all();
        $tahun = (int) $request->query('tahun', $tahunAda[0] ?? config('payroll.tahun_max'));
        $baris = $this->daftar($tahun)->map(fn (PayrollTahun $pt) => [
            'payroll' => $pt,
            'hasil' => $pt->perhitunganTerakhir,
            'kedaluwarsa' => $penghitung->kedaluwarsa($pt, $pt->perhitunganTerakhir),
        ]);
        $berhasil = $baris->filter(fn ($r) => $r['hasil']?->berhasil);
        $total = [
            'bruto' => $berhasil->sum(fn ($r) => $r['hasil']->bruto_setahun),
            'pph21' => $berhasil->sum(fn ($r) => $r['hasil']->pph21_setahun),
            'thp' => $berhasil->sum(fn ($r) => $r['hasil']->thp_setahun),
        ];

        return view('rekap.index', compact('tahun', 'tahunAda', 'baris', 'total'));
    }

    public function hitung(Request $request, Penghitung $penghitung): RedirectResponse
    {
        $tahun = (int) $request->input('tahun');
        $daftar = $this->daftar($tahun);
        if ($daftar->isEmpty()) {
            return back()->with('galat', "Belum ada data HR untuk tahun {$tahun}.");
        }
        try {
            $hasil = $penghitung->hitung($daftar, $request->user());
        } catch (MesinTidakTersedia $e) {
            return back()->with('galat', 'Engine tidak dapat dipanggil: '.$e->getMessage());
        }
        $gagal = array_filter($hasil, fn ($p) => ! $p->berhasil);
        $pesan = count($hasil).' pegawai dihitung dalam satu panggilan engine.';

        return $gagal
            ? back()->with('galat', $pesan.' '.count($gagal).' gagal; lihat kolom status.')
            : back()->with('sukses', $pesan.' Semua berhasil.');
    }

    public function ekspor(Request $request): StreamedResponse
    {
        $tahun = (int) $request->query('tahun');
        $daftar = $this->daftar($tahun);

        return response()->streamDownload(function () use ($daftar) {
            $out = fopen('php://output', 'w');
            fputcsv($out, ['nomor_induk', 'nama', 'tahun', 'status_ptkp', 'metode', 'bruto_setahun', 'pph21_setahun', 'thp_setahun',
                'cek_silang', 'versi_kb', 'dihitung_pada', 'status']);
            foreach ($daftar as $pt) {
                $p = $pt->perhitunganTerakhir;
                fputcsv($out, [self::teks($pt->pegawai->nomor_induk), self::teks($pt->pegawai->nama), $pt->tahun, $pt->status_ptkp,
                    $pt->metode, $p?->bruto_setahun, $p?->pph21_setahun, $p?->thp_setahun, $p?->cek_silang, $p?->versi_kb,
                    $p?->created_at?->toDateTimeString(),
                    $p === null ? 'belum dihitung' : ($p->berhasil ? 'berhasil' : self::teks('galat: '.$p->pesan))]);
            }
            fclose($out);
        }, "rekap_payroll_{$tahun}.csv", ['Content-Type' => 'text/csv; charset=UTF-8']);
    }

    /** Teks bebas isian pengguna: cegah dibaca sebagai rumus oleh spreadsheet (CSV injection). */
    private static function teks(string $s): string
    {
        return preg_match('/^[=+\-@\t\r]/', $s) ? "'".$s : $s;
    }

    private function daftar(int $tahun)
    {
        return PayrollTahun::query()
            ->where('tahun', $tahun)
            ->with(['pegawai', 'bulan', 'perhitunganTerakhir'])
            ->get()
            ->sortBy(fn ($pt) => $pt->pegawai->nomor_induk)
            ->values();
    }
}
