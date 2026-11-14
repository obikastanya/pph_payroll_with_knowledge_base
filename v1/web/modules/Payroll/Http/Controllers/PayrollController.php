<?php

namespace Modules\Payroll\Http\Controllers;

use App\Helpers\Format;
use App\Http\Controllers\Controller;
use App\Models\Payroll\PayrollTahun;
use App\Models\Payroll\Pegawai;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\View\View;
use Modules\Payroll\Http\Requests\PayrollTahunRequest;
use Modules\Payroll\Repositories\PayrollInterface;
use Modules\Payroll\Services\Label;
use Modules\Payroll\Services\MesinTidakTersedia;
use Modules\Payroll\Services\Penghitung;
use Modules\Payroll\Services\SkemaMasukan;
use Modules\Payroll\Services\TampilanHasil;
use Symfony\Component\HttpFoundation\StreamedResponse;

/**
 * Data HR per tahun pajak dan hasil perhitungannya. Angka pajak tidak dihitung di sini: Penghitung memanggil
 * engine KB (Python) lewat jembatan JSON dan menyimpan keluarannya apa adanya.
 */
class PayrollController extends Controller
{
    public const TAB = ['slip' => 'Slip gaji', 'setahun' => 'Perhitungan setahun', 'bulanan' => '12 bulan', 'jejak' => 'Cara mesin menghitung'];

    public const KOLOM_CSV = ['px_gaji', 'px_tunjangan', 'px_thr', 'px_kompensasi', 'px_ota', 'px_lembur', 'px_komisi', 'tunjangan_pajak',
        'px_premi_jkk', 'px_premi_jkm', 'px_premi_kes', 'bruto', 'kategori_ter', 'tarif_ter', 'pph21', 'pph21_dtp',
        'px_iuran_jht_pg', 'px_iuran_jp_pg', 'px_iuran_kes_pg', 'px_thp'];

    protected $pageTitle;

    public function __construct(private PayrollInterface $payroll)
    {
        $this->pageTitle = 'Payroll';
    }

    private function menuItems(Pegawai $pegawai, ?string $halaman = null, ?PayrollTahun $pt = null): array
    {
        return array_values(array_filter([
            ['url' => '/dashboard', 'label' => 'Dashboard', 'active' => false],
            ['url' => '/pegawai', 'label' => 'Pegawai', 'active' => false],
            ['url' => "/pegawai/{$pegawai->id}/detail", 'label' => $pegawai->nama, 'active' => false],
            $pt ? ['url' => "/payroll/{$pt->id}", 'label' => "Payroll {$pt->tahun}", 'active' => $halaman === null] : null,
            $halaman ? ['url' => '#', 'label' => $halaman, 'active' => true] : null,
        ]));
    }

    /** Isian tambahan yang diminta KB untuk tahun ini: [daftar masukan, pesan galat bila KB tidak dapat dimuat]. */
    private function skemaMasukan(int $tahun): array
    {
        try {
            return [app(SkemaMasukan::class)->untukTahun($tahun), null];
        } catch (MesinTidakTersedia $e) {
            return [[], $e->getMessage()];
        }
    }

    public function create(Request $request, Pegawai $pegawai): View
    {
        $tahunOpsi = $this->payroll->tahunBelumDiisi($pegawai);
        // ?tahun yang bukan pilihan (bukan angka, di luar rentang/masa kerja, atau sudah diisi) -> pilihan pertama
        $tahun = filter_var($request->query('tahun'), FILTER_VALIDATE_INT);
        if (! in_array($tahun, $tahunOpsi, true)) {
            $tahun = $tahunOpsi[0] ?? config('payroll.tahun_max');
        }
        [$masukan, $galatMasukan] = $this->skemaMasukan($tahun);
        $kunciTahunan = array_column(array_filter($masukan, fn (array $m) => $m['lingkup'] === 'tahun'), 'kunci');
        [$payroll, $bulan, $isianMasukan] = $this->payroll->isianBaru($pegawai, $tahun, $kunciTahunan);

        return view('Payroll::form', [
            'pageTitle' => $this->pageTitle,
            'menuItems' => $this->menuItems($pegawai, 'Tambah data HR'),
            'pegawai' => $pegawai,
            'payroll' => $payroll,
            'bulan' => $bulan,
            'rentang' => $pegawai->rentangBulan($tahun),
            'tahunOpsi' => $tahunOpsi,
            'masukan' => $masukan,
            'galatMasukan' => $galatMasukan,
            'isianMasukan' => $isianMasukan,
        ]);
    }

    public function store(PayrollTahunRequest $request, Pegawai $pegawai): RedirectResponse
    {
        $payroll = $this->payroll->simpan($pegawai, ['tahun' => $request->tahun()] + $request->dataTahun(), $request->dataBulan(), null,
            $request->dataMasukan());

        return redirect()->route('payroll.show', $payroll)
            ->with('success', "Data HR {$payroll->tahun} disimpan. Tekan Hitung untuk menghitung payroll.");
    }

    public function show(Request $request, PayrollTahun $payroll, Penghitung $penghitung): View
    {
        $payroll->load('pegawai');
        $terakhir = $payroll->perhitunganTerakhir;
        $tampil = $terakhir?->berhasil ? new TampilanHasil($terakhir->hasilEngine(), json_decode($terakhir->kasus, true)) : null;
        $tab = array_key_exists($request->query('tab'), self::TAB) ? $request->query('tab') : 'slip';
        $daftarBulan = $tampil?->bulan() ?? [];
        $bulanSlip = (int) $request->query('bulan', end($daftarBulan) ?: 12);
        if ($tampil && ! in_array($bulanSlip, $daftarBulan, true)) {
            $bulanSlip = end($daftarBulan);
        }

        return view('Payroll::show', [
            'pageTitle' => $this->pageTitle,
            'menuItems' => $this->menuItems($payroll->pegawai, null, $payroll),
            'payroll' => $payroll,
            'terakhir' => $terakhir,
            'tampil' => $tampil,
            'kedaluwarsa' => $penghitung->alasanKedaluwarsa($payroll, $terakhir),
            'tab' => $tab,
            'bulanSlip' => $bulanSlip,
            'riwayat' => $payroll->perhitungan()->with('user')->limit(20)->get(),
        ]);
    }

    public function edit(PayrollTahun $payroll): View
    {
        $pegawai = $payroll->pegawai;
        [$masukan, $galatMasukan] = $this->skemaMasukan($payroll->tahun);

        return view('Payroll::form', [
            'pageTitle' => $this->pageTitle,
            'menuItems' => $this->menuItems($pegawai, 'Ubah data HR', $payroll),
            'pegawai' => $pegawai,
            'payroll' => $payroll,
            'bulan' => $this->payroll->isianBulan($payroll),
            'rentang' => $pegawai->rentangBulan($payroll->tahun),
            'tahunOpsi' => [],
            'masukan' => $masukan,
            'galatMasukan' => $galatMasukan,
            'isianMasukan' => $this->payroll->isianMasukan($payroll),
        ]);
    }

    public function update(PayrollTahunRequest $request, PayrollTahun $payroll): RedirectResponse
    {
        $this->payroll->simpan($payroll->pegawai, $request->dataTahun(), $request->dataBulan(), $payroll, $request->dataMasukan());

        return redirect()->route('payroll.show', $payroll)->with('success', 'Data HR disimpan. Hitung ulang agar hasil mengikuti data terbaru.');
    }

    public function destroy(PayrollTahun $payroll): RedirectResponse
    {
        $pegawai = $payroll->pegawai;
        $payroll->delete();

        return redirect()->route('pegawai.detail', $pegawai)->with('success', "Data HR tahun {$payroll->tahun} dihapus.");
    }

    public function hitung(Request $request, PayrollTahun $payroll, Penghitung $penghitung): RedirectResponse
    {
        try {
            [$p] = $penghitung->hitung([$payroll], $request->user());
        } catch (MesinTidakTersedia $e) {   // termasuk HitungTerhenti dan batas waktu engine
            return back()->with('error', 'Engine tidak dapat dipanggil: '.$e->getMessage());
        }

        return $p->berhasil
            ? back()->with('success', 'Selesai dihitung. PPh 21 setahun '.Format::rp($p->pph21_setahun).'.')
            : back()->with('error', $p->pesan);
    }

    public function slip(PayrollTahun $payroll, int $bulan, Penghitung $penghitung): View
    {
        $p = $payroll->perhitunganTerakhir;
        abort_unless($p?->berhasil, 404, 'Belum ada perhitungan yang berhasil.');
        $tampil = new TampilanHasil($p->hasilEngine(), json_decode($p->kasus, true));
        abort_unless(in_array($bulan, $tampil->bulan(), true), 404, 'Bulan di luar masa kerja.');

        return view('Payroll::cetak', ['payroll' => $payroll->load('pegawai'), 'perhitungan' => $p, 'tampil' => $tampil, 'bulan' => $bulan,
            'kedaluwarsa' => $penghitung->alasanKedaluwarsa($payroll, $p)]);
    }

    public function ekspor(PayrollTahun $payroll): StreamedResponse
    {
        $p = $payroll->perhitunganTerakhir;
        abort_unless($p?->berhasil, 404, 'Belum ada perhitungan yang berhasil.');
        $h = $p->hasilEngine();
        $kolom = self::kolomCsv($h);

        return response()->streamDownload(function () use ($h, $kolom) {
            $out = fopen('php://output', 'w');
            fputcsv($out, ['bulan', ...$kolom]);
            $bulan = array_keys($h['per_masa']);
            sort($bulan);
            foreach ($bulan as $b) {
                fputcsv($out, [$b, ...array_map(fn ($k) => $h['per_masa'][$b][$k] ?? '', $kolom)]);
            }
            fclose($out);
        }, self::namaBerkas("payroll_{$payroll->pegawai->nomor_induk}_{$payroll->tahun}.csv"), ['Content-Type' => 'text/csv; charset=UTF-8']);
    }

    /**
     * Kolom CSV: KOLOM_CSV tetap di posisinya agar impor spreadsheet lama tidak bergeser; komponen dari berkas KB
     * tambahan (bukan perusahaan_x.yaml) menyusul di AKHIR sesuai urutan deklarasi.
     */
    public static function kolomCsv(array $h): array
    {
        $tambahan = [];
        foreach ($h['komponen'] ?? [] as $k) {
            $fakta = $k['fakta'] ?? null;
            // Label::FAKTA menjaga hasil tanpa `berkas`; berkas tambahan tidak boleh mendeklarasikan ulang komponen dasar
            $dasar = ($k['berkas'] ?? '') === 'perusahaan_x.yaml' || array_key_exists($fakta ?? '', Label::FAKTA);
            if ($fakta !== null && ! $dasar && ! in_array($fakta, self::KOLOM_CSV, true)) {
                $tambahan[$fakta] = true;
            }
        }

        return [...self::KOLOM_CSV, ...array_keys($tambahan)];
    }

    /** Nama berkas unduhan aman: nomor induk seperti 001/HR/2023 membuat header Content-Disposition ditolak. */
    public static function namaBerkas(string $nama): string
    {
        return preg_replace('/[^A-Za-z0-9._-]/', '-', $nama);
    }
}
