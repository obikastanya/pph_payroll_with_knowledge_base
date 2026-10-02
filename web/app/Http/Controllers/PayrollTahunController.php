<?php

namespace App\Http\Controllers;

use App\Http\Requests\PayrollTahunRequest;
use App\Models\PayrollTahun;
use App\Models\Pegawai;
use App\Payroll\MesinTidakTersedia;
use App\Payroll\Penghitung;
use App\Payroll\TampilanHasil;
use App\Support\Format;
use Carbon\CarbonImmutable;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\View\View;
use Symfony\Component\HttpFoundation\StreamedResponse;

class PayrollTahunController extends Controller
{
    public const TAB = ['slip' => 'Slip gaji', 'setahun' => 'Perhitungan setahun', 'bulanan' => '12 bulan', 'jejak' => 'Cara mesin menghitung'];

    public const KOLOM_CSV = ['px_gaji', 'px_tunjangan', 'px_thr', 'px_kompensasi', 'px_ota', 'px_lembur', 'px_komisi', 'tunjangan_pajak',
        'px_premi_jkk', 'px_premi_jkm', 'px_premi_kes', 'bruto', 'kategori_ter', 'tarif_ter', 'pph21', 'pph21_dtp',
        'px_iuran_jht_pg', 'px_iuran_jp_pg', 'px_iuran_kes_pg', 'px_thp'];

    public function create(Request $request, Pegawai $pegawai): View
    {
        $acuan = $pegawai->payrollTerakhir;
        $tahunOpsi = $this->tahunTersedia($pegawai);
        $tahun = (int) $request->query('tahun', $tahunOpsi[0] ?? config('payroll.tahun_max'));
        $payroll = new PayrollTahun($this->bawaan($pegawai, $acuan, $tahun));
        $payroll->tahun = $tahun;
        $rentang = $pegawai->rentangBulan($tahun);
        $bulan = [];
        foreach (range(1, 12) as $b) {
            $dalam = $rentang && $b >= $rentang[0] && $b <= $rentang[1];
            $hk = $dalam ? self::hariKerja($tahun, $b) : null;
            $bulan[$b] = ['hk_penuh' => $hk, 'hk_aktual' => $hk, 'kompensasi_persen' => null, 'ota' => null, 'lembur' => null, 'komisi' => null];
        }

        return view('payroll.form', compact('pegawai', 'payroll', 'bulan', 'rentang', 'tahunOpsi'));
    }

    public function store(PayrollTahunRequest $request, Pegawai $pegawai): RedirectResponse
    {
        $payroll = DB::transaction(function () use ($request, $pegawai) {
            $payroll = $pegawai->payrollTahun()->create(['tahun' => $request->tahun()] + $request->dataTahun());
            $this->simpanBulan($payroll, $request->dataBulan());

            return $payroll;
        });

        return redirect()->route('payroll.show', $payroll)->with('sukses', "Data HR {$payroll->tahun} disimpan. Tekan Hitung untuk menghitung payroll.");
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

        return view('payroll.show', [
            'payroll' => $payroll,
            'terakhir' => $terakhir,
            'tampil' => $tampil,
            'kedaluwarsa' => $penghitung->kedaluwarsa($payroll, $terakhir),
            'tab' => $tab,
            'bulanSlip' => $bulanSlip,
            'riwayat' => $payroll->perhitungan()->with('user')->limit(20)->get(),
        ]);
    }

    public function edit(PayrollTahun $payroll): View
    {
        $pegawai = $payroll->pegawai;
        $tersimpan = $payroll->bulan->keyBy('bulan');
        $bulan = [];
        foreach (range(1, 12) as $b) {
            $m = $tersimpan->get($b);
            $bulan[$b] = $m ? $m->only(['hk_penuh', 'hk_aktual', 'kompensasi_persen', 'ota', 'lembur', 'komisi'])
                : array_fill_keys(['hk_penuh', 'hk_aktual', 'kompensasi_persen', 'ota', 'lembur', 'komisi'], null);
        }
        $rentang = $pegawai->rentangBulan($payroll->tahun);

        return view('payroll.form', ['pegawai' => $pegawai, 'payroll' => $payroll, 'bulan' => $bulan, 'rentang' => $rentang,
            'tahunOpsi' => []]);
    }

    public function update(PayrollTahunRequest $request, PayrollTahun $payroll): RedirectResponse
    {
        DB::transaction(function () use ($request, $payroll) {
            $payroll->update($request->dataTahun());
            $this->simpanBulan($payroll, $request->dataBulan());
        });

        return redirect()->route('payroll.show', $payroll)->with('sukses', 'Data HR disimpan. Hitung ulang agar hasil mengikuti data terbaru.');
    }

    public function destroy(PayrollTahun $payroll): RedirectResponse
    {
        $pegawai = $payroll->pegawai;
        $payroll->delete();

        return redirect()->route('pegawai.show', $pegawai)->with('sukses', "Data HR tahun {$payroll->tahun} dihapus.");
    }

    public function hitung(Request $request, PayrollTahun $payroll, Penghitung $penghitung): RedirectResponse
    {
        try {
            [$p] = $penghitung->hitung([$payroll], $request->user());
        } catch (MesinTidakTersedia $e) {
            return back()->with('galat', 'Engine tidak dapat dipanggil: '.$e->getMessage());
        }

        return $p->berhasil
            ? back()->with('sukses', 'Selesai dihitung. PPh 21 setahun '.Format::rp($p->pph21_setahun).'.')
            : back()->with('galat', $p->pesan);
    }

    public function slip(PayrollTahun $payroll, int $bulan): View
    {
        $p = $payroll->perhitunganTerakhir;
        abort_unless($p?->berhasil, 404, 'Belum ada perhitungan yang berhasil.');
        $tampil = new TampilanHasil($p->hasilEngine(), json_decode($p->kasus, true));
        abort_unless(in_array($bulan, $tampil->bulan(), true), 404, 'Bulan di luar masa kerja.');

        return view('payroll.cetak', ['payroll' => $payroll->load('pegawai'), 'perhitungan' => $p, 'tampil' => $tampil, 'bulan' => $bulan]);
    }

    public function ekspor(PayrollTahun $payroll): StreamedResponse
    {
        $p = $payroll->perhitunganTerakhir;
        abort_unless($p?->berhasil, 404, 'Belum ada perhitungan yang berhasil.');
        $h = $p->hasilEngine();
        $nama = "payroll_{$payroll->pegawai->nomor_induk}_{$payroll->tahun}.csv";

        return response()->streamDownload(function () use ($h) {
            $out = fopen('php://output', 'w');
            fputcsv($out, ['bulan', ...self::KOLOM_CSV]);
            $bulan = array_keys($h['per_masa']);
            sort($bulan);
            foreach ($bulan as $b) {
                fputcsv($out, [$b, ...array_map(fn ($k) => $h['per_masa'][$b][$k] ?? '', self::KOLOM_CSV)]);
            }
            fclose($out);
        }, $nama, ['Content-Type' => 'text/csv; charset=UTF-8']);
    }

    private function simpanBulan(PayrollTahun $payroll, array $data): void
    {
        $payroll->bulan()->whereNotIn('bulan', array_keys($data))->delete();
        foreach ($data as $b => $isi) {
            $payroll->bulan()->updateOrCreate(['bulan' => $b], $isi);
        }
    }

    /** Tahun yang belum punya data HR dan termasuk masa kerja pegawai, terbaru dulu. */
    private function tahunTersedia(Pegawai $pegawai): array
    {
        $ada = $pegawai->payrollTahun()->pluck('tahun')->all();

        return array_values(array_filter(
            range(config('payroll.tahun_max'), config('payroll.tahun_min')),
            fn ($t) => ! in_array($t, $ada, true) && $pegawai->rentangBulan($t) !== null,
        ));
    }

    /** Isian awal: lanjutan dari tahun terakhir pegawai (gaji & tunjangan sesudah kenaikan), selebihnya data umum. */
    private function bawaan(Pegawai $pegawai, ?PayrollTahun $acuan, int $tahun): array
    {
        $masuk = $pegawai->tanggal_masuk;
        $mulaiBpjs = $masuk->year < $tahun ? 1 : $masuk->month;
        $lain = PayrollTahun::where('tahun', $tahun)->latest('id')->first();
        $d = [
            'status_ptkp' => 'TK/0', 'metode' => 'gross', 'gaji_pokok' => null, 'kenaikan_nominal' => 0,
            'kenaikan_tanggal' => CarbonImmutable::create($tahun, 1, 1), 'tunjangan_tetap_lama' => 0, 'tunjangan_prorata_lama' => 0,
            'tunjangan_tetap_baru' => 0, 'tunjangan_prorata_baru' => 0,
            'tanggal_lebaran' => $lain?->tanggal_lebaran, 'tanggal_thr_bayar' => $lain?->tanggal_thr_bayar,
            'bpjs_tk_mulai_bulan' => $mulaiBpjs, 'bpjs_kes_mulai_bulan' => $mulaiBpjs,
            'kelas_jkk_persen' => PayrollTahun::latest('id')->value('kelas_jkk_persen'),
        ];
        if ($acuan) {
            $naik = $acuan->kenaikan_tanggal->year === $acuan->tahun;
            $d = array_merge($d, [
                'status_ptkp' => $acuan->status_ptkp, 'metode' => $acuan->metode, 'kelas_jkk_persen' => $acuan->kelas_jkk_persen,
                'gaji_pokok' => $acuan->gaji_pokok + ($naik ? $acuan->kenaikan_nominal : 0),
                'tunjangan_tetap_lama' => $naik ? $acuan->tunjangan_tetap_baru : $acuan->tunjangan_tetap_lama,
                'tunjangan_prorata_lama' => $naik ? $acuan->tunjangan_prorata_baru : $acuan->tunjangan_prorata_lama,
            ]);
            $d['tunjangan_tetap_baru'] = $d['tunjangan_tetap_lama'];
            $d['tunjangan_prorata_baru'] = $d['tunjangan_prorata_lama'];
        }

        return $d;
    }

    /** Hari Senin-Jumat dalam sebulan: hanya isian awal, admin tetap menyesuaikan dengan kalender libur. */
    private static function hariKerja(int $tahun, int $bulan): int
    {
        $t = CarbonImmutable::create($tahun, $bulan, 1);
        $n = 0;
        for ($d = $t; $d->month === $bulan; $d = $d->addDay()) {
            $n += $d->isWeekday() ? 1 : 0;
        }

        return $n;
    }
}
