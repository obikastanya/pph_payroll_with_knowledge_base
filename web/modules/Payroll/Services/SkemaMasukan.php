<?php

namespace Modules\Payroll\Services;

use Illuminate\Support\Facades\Cache;

/**
 * Isian tambahan yang diminta KB aktif (deklarasi `masukan` di berkas KB tambahan) dan metadata komponen gajinya.
 * Diambil dari engine (`perintah: masukan`) lalu di-cache per sidik KB, sehingga form data HR menyesuaikan diri
 * tanpa perubahan kode setiap kali aturan baru menambah isian.
 *
 * Satu masukan: {kunci, label, tipe, lingkup: tahun|bulan, wajib, bawaan, pilihan[], keterangan, sumber, mulai, sampai}.
 */
final class SkemaMasukan
{
    public const TIPE = ['rupiah', 'bilangan', 'persen', 'desimal', 'tanggal', 'pilihan', 'ya_tidak'];

    /** Berkas dasar yang ikut menentukan skema (relatif terhadap payroll.root); pola glob diurutkan agar sidik stabil. */
    public const BERKAS_DASAR = ['kb/regulasi/*.yaml', 'kb/perusahaan/*.yaml', 'jembatan/kontrak.py', 'asisten_kb/rancangan.py'];

    private ?array $memo = null;

    private ?string $dasar = null;

    public function __construct(private MesinPajak $mesin, private KbTambahan $kb) {}

    /**
     * @return array{masukan: list<array>, komponen: list<array>}
     *
     * @throws MesinTidakTersedia bila KB aktif tidak dapat dimuat engine
     */
    public function semua(): array
    {
        $berkas = $this->kb->berkasAktif();
        if ($berkas === []) {
            return ['masukan' => [], 'komponen' => []];
        }
        // KB dasar & kode asisten ikut kunci cache: perubahan di sana juga mengubah skema, tanpa perlu cache:clear
        $kunci = "kb_skema:{$this->sidikDasar()}:{$this->kb->sidik($berkas)}";
        if (($this->memo['kunci'] ?? null) !== $kunci) {
            $isi = Cache::rememberForever($kunci, fn () => $this->mesin->masukan($berkas));
            $this->memo = ['kunci' => $kunci, 'isi' => $isi];
        }

        return $this->memo['isi'];
    }

    /** sha256 isi berkas dasar (16 hex), sekali per instance. Berkas yang tidak ada tidak menyumbang apa pun. */
    public function sidikDasar(): string
    {
        if ($this->dasar === null) {
            $root = rtrim(config('payroll.root'), '/\\');
            $h = hash_init('sha256');
            foreach (self::BERKAS_DASAR as $pola) {
                $daftar = glob($root.'/'.$pola) ?: [];
                sort($daftar);
                foreach ($daftar as $path) {
                    if (is_file($path)) {
                        hash_update($h, substr($path, strlen($root) + 1)."\0".file_get_contents($path)."\0");
                    }
                }
            }
            $this->dasar = substr(hash_final($h), 0, 16);
        }

        return $this->dasar;
    }

    /** @return list<array> masukan yang dipakai aturan yang berlaku di salah satu masa tahun pajak ini */
    public function untukTahun(int $tahun): array
    {
        return array_values(array_filter($this->semua()['masukan'], fn (array $m) => self::berlakuTahun($m, $tahun)));
    }

    /**
     * Engine mengevaluasi aturan pada tanggal 1 setiap masa: aturan yang mulai tanggal 15 Juli baru dipakai di masa
     * Agustus, jadi isiannya tidak diminta untuk Juli.
     */
    public static function berlakuBulan(array $m, int $tahun, int $bulan): bool
    {
        $tgl = sprintf('%04d-%02d-01', $tahun, $bulan);

        return self::berlaku($m, $tgl, $tgl);
    }

    /** Berlaku di sedikitnya satu masa tahun ini: mulai paling lambat 1 Desember, sampai paling awal 1 Januari. */
    public static function berlakuTahun(array $m, int $tahun): bool
    {
        return self::berlaku($m, "{$tahun}-01-01", "{$tahun}-12-01");
    }

    /** Rentang [mulai, sampai] masukan beririsan dengan tanggal evaluasi [$awal, $akhir] (tanggal ISO). */
    private static function berlaku(array $m, string $awal, string $akhir): bool
    {
        return (($m['mulai'] ?? null) === null || $m['mulai'] <= $akhir) && (($m['sampai'] ?? null) === null || $m['sampai'] >= $awal);
    }
}
