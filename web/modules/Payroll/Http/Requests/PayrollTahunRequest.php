<?php

namespace Modules\Payroll\Http\Requests;

use App\Helpers\Desimal;
use App\Helpers\Format;
use App\Models\Payroll\PayrollTahun;
use App\Models\Payroll\Pegawai;
use Carbon\CarbonImmutable;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;
use Illuminate\Validation\Validator;
use Modules\Payroll\Services\Label;
use Modules\Payroll\Services\MesinTidakTersedia;
use Modules\Payroll\Services\SkemaMasukan;

/**
 * Isian data HR satu tahun pajak. Selain aturan per kolom, ada pemeriksaan konsistensi yang mencegah angka nol
 * diam-diam: bulan dalam masa kerja wajib berisi hari kerja & hadir, dan kenaikan gaji di tengah bulan wajib
 * dipecah ke hari sebelum/sesudah yang jumlahnya sama dengan hari bulan itu.
 *
 * Isian tambahan dari KB (`masukan[kunci]`, `masukan_bulan[bulan][kunci]`) divalidasi menurut tipe yang
 * dideklarasikan berkas KB (SkemaMasukan), jadi aturan baru yang meminta input baru tidak perlu mengubah kode ini.
 */
class PayrollTahunRequest extends FormRequest
{
    private ?array $skema = null;

    private ?string $galatSkema = null;

    public const RUPIAH = ['gaji_pokok', 'kenaikan_nominal', 'tunjangan_tetap_lama', 'tunjangan_prorata_lama',
        'tunjangan_tetap_baru', 'tunjangan_prorata_baru'];

    public const HARI = ['kenaikan_hk_sebelum', 'kenaikan_hk_sesudah', 'kenaikan_hari_sebelum', 'kenaikan_hari_sesudah'];

    private const DESIMAL = '/^\d+([.,]\d+)?$/';

    public function rules(): array
    {
        $payroll = $this->route('payroll');
        $aturan = [
            'status_ptkp' => ['required', Rule::in(Label::STATUS_PTKP)],
            'metode' => ['required', Rule::in(array_keys(Label::METODE))],
            'kenaikan_tanggal' => ['required', 'date'],
            'tanggal_lebaran' => ['required', 'date'],
            'tanggal_thr_bayar' => ['required', 'date'],
            'bpjs_tk_mulai_bulan' => ['required', 'integer', 'between:1,12'],
            'bpjs_kes_mulai_bulan' => ['required', 'integer', 'between:1,12'],
            'kelas_jkk_persen' => ['required', 'regex:'.self::DESIMAL],
            'bulan' => ['array'],
            'bulan.*.hk_penuh' => ['nullable', 'integer', 'between:1,31'],
            'bulan.*.hk_aktual' => ['nullable', 'integer', 'between:0,31'],
            'bulan.*.kompensasi_persen' => ['nullable', 'regex:'.self::DESIMAL],
            'bulan.*.ota' => ['nullable', 'integer', 'min:0'],
            'bulan.*.lembur' => ['nullable', 'integer', 'min:0'],
            'bulan.*.komisi' => ['nullable', 'integer', 'min:0'],
        ];
        foreach (self::RUPIAH as $f) {
            $aturan[$f] = [$f === 'gaji_pokok' ? 'required' : 'nullable', 'integer', 'min:0'];
        }
        foreach (self::HARI as $f) {
            $aturan[$f] = ['nullable', 'integer', 'between:0,31'];
        }
        if (! $payroll instanceof PayrollTahun) {
            $aturan['tahun'] = ['required', 'integer', 'between:'.config('payroll.tahun_min').','.config('payroll.tahun_max'),
                Rule::unique('payroll_tahun')->where('pegawai_id', $this->pegawai()->id)];
        }
        foreach ($this->skemaMasukan() as $m) {
            if ($m['lingkup'] === 'tahun') {
                $aturan["masukan.{$m['kunci']}"] = [$m['wajib'] ? 'required' : 'nullable', ...self::aturanTipe($m)];
            } else {
                $aturan["masukan_bulan.*.{$m['kunci']}"] = ['nullable', ...self::aturanTipe($m)];
            }
        }

        return $aturan;
    }

    /** Isian tambahan dari KB yang dipakai aturan berlaku di tahun pajak ini (kosong bila tidak ada berkas KB tambahan). */
    public function skemaMasukan(): array
    {
        if ($this->skema === null) {
            try {
                $this->skema = app(SkemaMasukan::class)->untukTahun($this->tahun());
            } catch (MesinTidakTersedia $e) {
                $this->skema = [];
                $this->galatSkema = $e->getMessage();
            }
        }

        return $this->skema;
    }

    private static function aturanTipe(array $m): array
    {
        return match ($m['tipe']) {
            'rupiah', 'bilangan' => ['integer'],
            'persen', 'desimal' => ['regex:'.self::DESIMAL],
            'tanggal' => ['date_format:Y-m-d'],
            'pilihan' => [Rule::in($m['pilihan'])],
            'ya_tidak' => ['in:0,1'],
            default => ['string'],
        };
    }

    public function after(): array
    {
        return [function (Validator $v) {
            if ($this->galatSkema !== null) {
                $v->errors()->add('masukan', 'Isian tambahan dari knowledge base tidak dapat dimuat engine: '.$this->galatSkema);
            }
            if ($v->errors()->isNotEmpty()) {
                return;
            }
            $tahun = $this->tahun();
            $rentang = $this->pegawai()->rentangBulan($tahun);
            if ($rentang === null) {
                $v->errors()->add('tahun', "Pegawai tidak bekerja di tahun {$tahun} (cek tanggal masuk/berhenti di data pegawai).");

                return;
            }
            $bulan = $this->input('bulan', []);
            foreach (range($rentang[0], $rentang[1]) as $b) {
                $penuh = $bulan[$b]['hk_penuh'] ?? null;
                $hadir = $bulan[$b]['hk_aktual'] ?? null;
                $nama = Format::bulan($b, true);
                if ($penuh === null) {
                    $v->errors()->add("bulan.{$b}.hk_penuh", "Hari kerja bulan {$nama} wajib diisi.");
                } elseif ($hadir === null) {
                    $v->errors()->add("bulan.{$b}.hk_aktual", "Jumlah hadir bulan {$nama} wajib diisi.");
                } elseif ((int) $hadir > (int) $penuh) {
                    $v->errors()->add("bulan.{$b}.hk_aktual", "Hadir bulan {$nama} melebihi hari kerjanya.");
                }
                if (Desimal::digitDesimal(Desimal::normal($bulan[$b]['kompensasi_persen'] ?? null) ?? '0') > 6) {
                    $v->errors()->add("bulan.{$b}.kompensasi_persen", "Kompensasi bulan {$nama}: paling banyak 6 digit desimal.");
                }
                foreach ($this->skemaMasukan() as $m) {
                    if ($m['lingkup'] === 'bulan' && $m['wajib'] && SkemaMasukan::berlakuBulan($m, $tahun, $b)
                        && in_array($this->input("masukan_bulan.{$b}.{$m['kunci']}"), [null, ''], true)) {
                        $v->errors()->add("masukan_bulan.{$b}.{$m['kunci']}", "{$m['label']} bulan {$nama} wajib diisi (diminta aturan KB).");
                    }
                }
            }
            $naik = CarbonImmutable::parse($this->input('kenaikan_tanggal'));
            if ($naik->year === $tahun && $naik->day > 1 && $v->errors()->isEmpty()) {
                $b = $naik->month;
                $nama = Format::bulan($b, true);
                $hk = (int) $this->input('kenaikan_hk_sebelum') + (int) $this->input('kenaikan_hk_sesudah');
                $hari = (int) $this->input('kenaikan_hari_sebelum') + (int) $this->input('kenaikan_hari_sesudah');
                if ($hk !== (int) ($bulan[$b]['hk_aktual'] ?? -1)) {
                    $v->errors()->add('kenaikan_hk_sebelum', "Kenaikan berlaku di tengah bulan {$nama}: hari hadir sebelum + sesudah "
                        ."harus sama dengan hadir bulan {$nama} ({$hk} ≠ ".($bulan[$b]['hk_aktual'] ?? '-').').');
                }
                if ($hari !== (int) ($bulan[$b]['hk_penuh'] ?? -1)) {
                    $v->errors()->add('kenaikan_hari_sebelum', "Kenaikan berlaku di tengah bulan {$nama}: hari kerja total sebelum + "
                        ."sesudah harus sama dengan hari kerja bulan {$nama} ({$hari} ≠ ".($bulan[$b]['hk_penuh'] ?? '-').').');
                }
            }
        }];
    }

    public function attributes(): array
    {
        $tambahan = [];
        foreach ($this->skemaMasukan() as $m) {
            $tambahan[$m['lingkup'] === 'tahun' ? "masukan.{$m['kunci']}" : "masukan_bulan.*.{$m['kunci']}"] = $m['label'];
        }

        return $tambahan + [
            'status_ptkp' => 'status PTKP', 'gaji_pokok' => 'gaji pokok', 'kenaikan_nominal' => 'kenaikan gaji',
            'kenaikan_tanggal' => 'tanggal berlaku kenaikan', 'tanggal_lebaran' => 'tanggal Hari Raya',
            'tanggal_thr_bayar' => 'tanggal bayar THR', 'kelas_jkk_persen' => 'tarif JKK',
            'bpjs_tk_mulai_bulan' => 'bulan mulai BPJS TK', 'bpjs_kes_mulai_bulan' => 'bulan mulai BPJS Kesehatan',
            'bulan.*.hk_penuh' => 'hari kerja', 'bulan.*.hk_aktual' => 'hadir', 'bulan.*.kompensasi_persen' => 'kompensasi',
            'bulan.*.ota' => 'insentif OTA', 'bulan.*.lembur' => 'lembur', 'bulan.*.komisi' => 'komisi',
        ];
    }

    public function messages(): array
    {
        return ['kelas_jkk_persen.regex' => 'Tarif JKK harus angka persen, mis. 0,24.',
            'bulan.*.kompensasi_persen.regex' => 'Kompensasi harus angka persen, mis. 10.'];
    }

    public function pegawai(): Pegawai
    {
        $payroll = $this->route('payroll');

        return $payroll instanceof PayrollTahun ? $payroll->pegawai : $this->route('pegawai');
    }

    public function tahun(): int
    {
        $payroll = $this->route('payroll');

        return $payroll instanceof PayrollTahun ? $payroll->tahun : (int) $this->input('tahun');
    }

    /** Kolom tabel payroll_tahun (angka kosong -> 0, persen dinormalkan). */
    public function dataTahun(): array
    {
        $d = $this->safe()->except(['bulan', 'tahun', 'masukan', 'masukan_bulan']);
        foreach ([...self::RUPIAH, ...self::HARI] as $f) {
            $d[$f] = (int) ($d[$f] ?? 0);
        }
        $d['kelas_jkk_persen'] = Desimal::normal($d['kelas_jkk_persen']);

        return $d;
    }

    /** Baris payroll_bulan yang terisi: [bulan => kolom]. Bulan yang seluruhnya kosong tidak disimpan. */
    public function dataBulan(): array
    {
        $hasil = [];
        foreach ($this->validated('bulan', []) as $b => $m) {
            $isi = [
                'hk_penuh' => self::int($m['hk_penuh'] ?? null),
                'hk_aktual' => self::int($m['hk_aktual'] ?? null),
                'kompensasi_persen' => Desimal::normal($m['kompensasi_persen'] ?? null),
                'ota' => self::int($m['ota'] ?? null),
                'lembur' => self::int($m['lembur'] ?? null),
                'komisi' => self::int($m['komisi'] ?? null),
            ];
            if (array_filter($isi, fn ($x) => $x !== null) && $b >= 1 && $b <= 12) {
                $hasil[(int) $b] = $isi;
            }
        }

        return $hasil;
    }

    /**
     * Isian tambahan dari KB: [{kunci, bulan (0 = tahunan), nilai}] untuk setiap isian yang tampil di form; nilai null =
     * dikosongkan (baris dihapus, engine memakai nilai bawaan deklarasi). Nilai sudah bertipe sesuai deklarasi.
     */
    public function dataMasukan(): array
    {
        $tahun = $this->tahun();
        $rentang = $this->pegawai()->rentangBulan($tahun);
        $baris = [];
        foreach ($this->skemaMasukan() as $m) {
            if ($m['lingkup'] === 'tahun') {
                $baris[] = ['kunci' => $m['kunci'], 'bulan' => 0, 'nilai' => self::nilaiMasukan($m, $this->input("masukan.{$m['kunci']}"))];

                continue;
            }
            foreach ($rentang ? range($rentang[0], $rentang[1]) : [] as $b) {
                if (SkemaMasukan::berlakuBulan($m, $tahun, $b)) {
                    $baris[] = ['kunci' => $m['kunci'], 'bulan' => $b,
                        'nilai' => self::nilaiMasukan($m, $this->input("masukan_bulan.{$b}.{$m['kunci']}"))];
                }
            }
        }

        return $baris;
    }

    /** Teks isian form -> nilai bertipe untuk data_hr (rupiah/bilangan int, persen/desimal teks titik, ya/tidak bool). */
    public static function nilaiMasukan(array $m, mixed $v): mixed
    {
        if ($v === null || $v === '') {
            return null;
        }

        return match ($m['tipe']) {
            'rupiah', 'bilangan' => (int) $v,
            'persen', 'desimal' => Desimal::normal((string) $v),
            'ya_tidak' => (bool) (int) $v,
            default => (string) $v,
        };
    }

    private static function int(mixed $v): ?int
    {
        return $v === null || $v === '' ? null : (int) $v;
    }
}
