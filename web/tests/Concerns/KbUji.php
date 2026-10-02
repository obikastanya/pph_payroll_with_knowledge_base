<?php

namespace Tests\Concerns;

use App\Models\Kb\UsulanKb;
use Illuminate\Process\PendingProcess;
use Illuminate\Support\Facades\File;
use Illuminate\Support\Facades\Process;
use Modules\Payroll\Services\KbTambahan;

/** Alat uji fitur Basis pengetahuan: folder KB sementara, jawaban jembatan tiruan, dan usulan contoh (uang transport). */
trait KbUji
{
    protected const YAML = "lapisan: perusahaan\nid: transport_2026\naturan:\n- id: PPT-TRANSPORT-01\n  maka: hr('uang_transport_per_hari') * hr_masa('hk_aktual')\n";

    private ?string $rootUji = null;

    /** Alihkan folder repositori induk ke folder sementara agar berkas KB uji tidak tertulis ke repo. */
    protected function rootSementara(): string
    {
        $this->rootUji = sys_get_temp_dir().DIRECTORY_SEPARATOR.'payroll_uji_'.uniqid();
        File::ensureDirectoryExists($this->rootUji);
        config(['payroll.root' => $this->rootUji]);

        return $this->rootUji;
    }

    protected function tearDown(): void
    {
        if ($this->rootUji !== null) {
            File::deleteDirectory($this->rootUji);
        }
        parent::tearDown();
    }

    /** Jembatan tiruan: satu jawaban per `perintah`; perintah lain dijawab galat agar panggilan tak terduga terlihat. */
    protected function palsukanJembatan(array $jawabPerPerintah): void
    {
        Process::fake(['*' => function (PendingProcess $p) use ($jawabPerPerintah) {
            $perintah = json_decode($p->input, true)['perintah'];
            $jawab = $jawabPerPerintah[$perintah] ?? ['ok' => false, 'jenis' => 'tak_terduga', 'pesan' => "perintah {$perintah} tidak dipalsukan"];

            return Process::result(output: json_encode($jawab), exitCode: ($jawab['ok'] ?? false) ? 0 : 2);
        }]);
    }

    protected static function masukanTransport(array $timpa = []): array
    {
        return $timpa + [
            'kunci' => 'uang_transport_per_hari', 'label' => 'Uang transport per hari hadir', 'tipe' => 'rupiah', 'lingkup' => 'tahun',
            'wajib' => false, 'bawaan' => 0, 'pilihan' => [], 'keterangan' => 'Nominal per hari kerja yang dihadiri', 'sumber' => 'PP 2026 Ps. 12',
            'dideklarasikan' => true, 'berkas' => ['0001_transport_2026.yaml'], 'aturan' => ['PPT-TRANSPORT-01'], 'mulai' => '2026-07-01', 'sampai' => null,
        ];
    }

    protected static function validasiLolos(array $timpa = []): array
    {
        return $timpa + [
            'ok' => true, 'galat' => [], 'peringatan' => [],
            'ringkasan' => ['lapisan' => 'perusahaan', 'aturan' => 1, 'komponen' => 1, 'masukan' => 1, 'parameter' => 0, 'pembulatan' => 0],
            'isi' => [
                'lapisan' => 'perusahaan', 'id' => 'transport_2026',
                'komponen' => [['fakta' => 'px_transport', 'jenis' => 'tunjangan_transport', 'kategori' => 'teratur', 'label' => 'Uang transport']],
                'aturan' => [['id' => 'PPT-TRANSPORT-01', 'sifat' => 'opsional', 'berlaku' => ['mulai' => '2026-07-01'], 'lingkup' => 'masa',
                    'menghasilkan' => 'px_transport', 'maka' => "hr('uang_transport_per_hari') * hr_masa('hk_aktual')", 'tipe_hasil' => 'rupiah',
                    'sumber' => 'Peraturan Perusahaan 2026 Ps. 12 ayat (1)']],
            ],
            'masukan' => [self::masukanTransport()],
            'dampak' => [['pegawai' => 'Karyawan A (contoh)', 'tahun' => 2026, 'nilai_contoh' => ['uang_transport_per_hari' => 100_000],
                'sebelum' => ['bruto_setahun' => 151_968_866, 'pph21_setahun' => 7_341_750, 'thp_setahun' => 136_021_637],
                'sesudah' => ['bruto_setahun' => 164_568_866, 'pph21_setahun' => 9_231_750, 'thp_setahun' => 146_731_637],
                'fakta_baru' => ['px_transport' => 12_600_000]]],
        ];
    }

    protected static function jawabUsulkan(array $timpa = []): array
    {
        return $timpa + [
            'ok' => true,
            'usulan' => [
                'ringkasan' => 'Perusahaan memberi uang transport per hari hadir mulai 1 Juli 2026.', 'dapat_dikodifikasi' => true, 'alasan' => '',
                'lapisan' => 'perusahaan', 'id_berkas' => 'transport_2026', 'keterangan' => 'PP 2026: uang transport',
                'rujukan' => [['bagian' => 'PPT-TRANSPORT-01', 'halaman' => 3, 'kutipan' => 'uang transport dibayarkan untuk setiap hari hadir']],
                'catatan_peninjau' => ['Nominal per hari tidak disebut di dokumen; dijadikan isian.'],
            ],
            'info' => ['model' => 'gpt-5.6-sol', 'token_masuk' => 21_000, 'token_keluar' => 1_800, 'token_cache_baca' => 20_000, 'token_cache_tulis' => 0],
            'yaml' => self::YAML,
            'validasi' => self::validasiLolos(),
        ];
    }

    protected function usulan(array $timpa = []): UsulanKb
    {
        return UsulanKb::create($timpa + [
            'judul' => 'Peraturan Perusahaan 2026', 'lapisan' => 'perusahaan', 'nama_pdf' => 'pp_2026.pdf', 'path_pdf' => 'kb_usulan/pp.pdf',
            'ukuran_pdf' => 120_000, 'status' => 'siap_tinjau', 'usulan' => self::jawabUsulkan()['usulan'], 'yaml' => self::YAML,
            'validasi' => self::validasiLolos(), 'valid' => true, 'info_llm' => self::jawabUsulkan()['info'],
        ]);
    }

    /** Usulan yang sudah diterapkan & aktif, dengan berkasnya di folder KB sementara. */
    protected function kbAktif(array $timpa = []): UsulanKb
    {
        if ($this->rootUji === null) {
            $this->rootSementara();
        }
        $u = $this->usulan($timpa + ['status' => 'diterapkan', 'aktif' => true, 'nama_berkas' => '0001_transport_2026.yaml', 'diterapkan_pada' => now()]);
        app(KbTambahan::class)->tulis($u->nama_berkas, $u->yaml);

        return $u;
    }
}
