<?php

namespace Modules\Payroll\Repositories;

use App\Models\Payroll\PayrollMasukan;
use App\Models\Payroll\PayrollTahun;
use App\Models\Payroll\Pegawai;
use Carbon\CarbonImmutable;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\LazyCollection;

class PayrollRepository implements PayrollInterface
{
    private const KOLOM_BULAN = ['hk_penuh', 'hk_aktual', 'kompensasi_persen', 'ota', 'lembur', 'komisi'];

    /** Kolom perhitungan terakhir untuk daftar tahunan: `kasus` tetap dimuat (status usang membandingkannya). */
    private const KOLOM_PERHITUNGAN_RINGKAS = ['id', 'payroll_tahun_id', 'user_id', 'berhasil', 'jenis_galat', 'pesan', 'kasus',
        'cek_silang', 'versi_engine', 'versi_kb', 'sidik_kb', 'bruto_setahun', 'pph21_setahun', 'thp_setahun', 'created_at', 'updated_at'];

    public function daftarTahun(int $tahun, ?string $cari = null): Collection
    {
        return PayrollTahun::query()
            ->where('tahun', $tahun)
            ->when($cari, fn ($q) => $q->whereHas('pegawai', fn ($p) => $p->where(
                fn ($w) => $w->whereLike('nama', "%{$cari}%")->orWhereLike('nomor_induk', "%{$cari}%")
            )))
            // tanpa hasil lengkap engine (±150 KB per pegawai) dan rincian cek silang: daftar/rekap tidak membacanya
            ->with(['pegawai', 'bulan', 'perhitunganTerakhir' => fn ($q) => $q->select(
                array_map(fn (string $k) => "perhitungan.{$k}", self::KOLOM_PERHITUNGAN_RINGKAS)
            )])
            ->get()
            ->sortBy(fn ($pt) => $pt->pegawai->nomor_induk)
            ->values();
    }

    public function daftarHitung(int $tahun, int $ukuran): LazyCollection
    {
        return PayrollTahun::query()->where('tahun', $tahun)->with(['pegawai', 'bulan', 'masukan'])->lazyById($ukuran);
    }

    public function jumlahTahun(int $tahun): int
    {
        return PayrollTahun::query()->where('tahun', $tahun)->count();
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

    public function isianBaru(Pegawai $pegawai, int $tahun, array $kunciTahunan = []): array
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

        return [$payroll, $bulan, ['tahun' => $this->masukanTahunanTerakhir($pegawai, $kunciTahunan), 'bulan' => []]];
    }

    /**
     * Isian tambahan tahunan (bulan 0) dari tahun data HR terbaru pegawai yang memilikinya, per kunci, hanya untuk
     * kunci yang masih diminta skema sekarang. Isian bulanan tidak dilanjutkan (berbeda tiap masa).
     */
    private function masukanTahunanTerakhir(Pegawai $pegawai, array $kunci): array
    {
        if ($kunci === []) {
            return [];
        }
        $baris = PayrollMasukan::query()
            ->join('payroll_tahun', 'payroll_tahun.id', '=', 'payroll_masukan.payroll_tahun_id')
            ->where('payroll_tahun.pegawai_id', $pegawai->id)
            ->where('payroll_masukan.bulan', 0)
            ->whereIn('payroll_masukan.kunci', $kunci)
            ->orderByDesc('payroll_tahun.tahun')
            ->get(['payroll_masukan.kunci', 'payroll_masukan.nilai']);
        $isian = [];
        foreach ($baris as $m) {
            if (! array_key_exists($m->kunci, $isian) && $m->nilai !== null) {
                $isian[$m->kunci] = $m->nilai;
            }
        }

        return $isian;
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

    public function isianMasukan(?PayrollTahun $payroll): array
    {
        $isian = ['tahun' => [], 'bulan' => []];
        foreach ($payroll?->masukan ?? [] as $m) {
            if ($m->bulan === 0) {
                $isian['tahun'][$m->kunci] = $m->nilai;
            } else {
                $isian['bulan'][$m->bulan][$m->kunci] = $m->nilai;
            }
        }

        return $isian;
    }

    public function simpan(Pegawai $pegawai, array $dataTahun, array $dataBulan, ?PayrollTahun $payroll = null, array $dataMasukan = []): PayrollTahun
    {
        return DB::transaction(function () use ($pegawai, $dataTahun, $dataBulan, $payroll, $dataMasukan) {
            if ($payroll) {
                $payroll->update($dataTahun);
            } else {
                $payroll = $pegawai->payrollTahun()->create($dataTahun);
            }
            $payroll->bulan()->whereNotIn('bulan', array_keys($dataBulan))->delete();
            foreach ($dataBulan as $b => $isi) {
                $payroll->bulan()->updateOrCreate(['bulan' => $b], $isi);
            }
            foreach ($dataMasukan as $m) {
                $kunci = ['kunci' => $m['kunci'], 'bulan' => $m['bulan']];
                if ($m['nilai'] === null) {
                    $payroll->masukan()->where($kunci)->delete();
                } else {
                    $payroll->masukan()->updateOrCreate($kunci, ['nilai' => $m['nilai']]);
                }
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
