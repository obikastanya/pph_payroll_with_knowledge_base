<?php

namespace Modules\Payroll\Repositories;

use App\Models\Payroll\PayrollTahun;
use App\Models\Payroll\Pegawai;
use Carbon\CarbonImmutable;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

class PayrollRepository implements PayrollInterface
{
    private const KOLOM_BULAN = ['hk_penuh', 'hk_aktual', 'kompensasi_persen', 'ota', 'lembur', 'komisi'];

    public function daftarTahun(int $tahun, ?string $cari = null): Collection
    {
        return PayrollTahun::query()
            ->where('tahun', $tahun)
            ->when($cari, fn ($q) => $q->whereHas('pegawai', fn ($p) => $p->where(
                fn ($w) => $w->where('nama', 'like', "%{$cari}%")->orWhere('nomor_induk', 'like', "%{$cari}%")
            )))
            ->with(['pegawai', 'bulan', 'perhitunganTerakhir'])
            ->get()
            ->sortBy(fn ($pt) => $pt->pegawai->nomor_induk)
            ->values();
    }

    public function tahunAda(): array
    {
        return PayrollTahun::query()->distinct()->orderByDesc('tahun')->pluck('tahun')->all();
    }

    public function tahunBelumDiisi(Pegawai $pegawai): array
    {
        $ada = $pegawai->payrollTahun()->pluck('tahun')->all();

        return array_values(array_filter(
            range(config('payroll.tahun_max'), config('payroll.tahun_min')),
            fn ($t) => ! in_array($t, $ada, true) && $pegawai->rentangBulan($t) !== null,
        ));
    }

    public function isianBaru(Pegawai $pegawai, int $tahun): array
    {
        $payroll = new PayrollTahun($this->bawaan($pegawai, $pegawai->payrollTerakhir, $tahun));
        $payroll->tahun = $tahun;
        $rentang = $pegawai->rentangBulan($tahun);
        $bulan = [];
        foreach (range(1, 12) as $b) {
            $dalam = $rentang && $b >= $rentang[0] && $b <= $rentang[1];
            $hk = $dalam ? self::hariKerja($tahun, $b) : null;
            $bulan[$b] = ['hk_penuh' => $hk, 'hk_aktual' => $hk] + array_fill_keys(['kompensasi_persen', 'ota', 'lembur', 'komisi'], null);
        }

        return [$payroll, $bulan];
    }

    public function isianBulan(PayrollTahun $payroll): array
    {
        $tersimpan = $payroll->bulan->keyBy('bulan');
        $bulan = [];
        foreach (range(1, 12) as $b) {
            $m = $tersimpan->get($b);
            $bulan[$b] = $m ? $m->only(self::KOLOM_BULAN) : array_fill_keys(self::KOLOM_BULAN, null);
        }

        return $bulan;
    }

    public function simpan(Pegawai $pegawai, array $dataTahun, array $dataBulan, ?PayrollTahun $payroll = null): PayrollTahun
    {
        return DB::transaction(function () use ($pegawai, $dataTahun, $dataBulan, $payroll) {
            if ($payroll) {
                $payroll->update($dataTahun);
            } else {
                $payroll = $pegawai->payrollTahun()->create($dataTahun);
            }
            $payroll->bulan()->whereNotIn('bulan', array_keys($dataBulan))->delete();
            foreach ($dataBulan as $b => $isi) {
                $payroll->bulan()->updateOrCreate(['bulan' => $b], $isi);
            }

            return $payroll;
        });
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
        $n = 0;
        for ($d = CarbonImmutable::create($tahun, $bulan, 1); $d->month === $bulan; $d = $d->addDay()) {
            $n += $d->isWeekday() ? 1 : 0;
        }

        return $n;
    }
}
