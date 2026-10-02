<?php

namespace Modules\Payroll\Services;

use Carbon\CarbonImmutable;
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

    private ?array $memo = null;

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
        $sidik = $this->kb->sidik($berkas);
        if (($this->memo['sidik'] ?? null) !== $sidik) {
            $isi = Cache::rememberForever("kb_skema:{$sidik}", fn () => $this->mesin->masukan($berkas));
            $this->memo = ['sidik' => $sidik, 'isi' => $isi];
        }

        return $this->memo['isi'];
    }

    /** @return list<array> masukan yang dipakai aturan yang berlaku (sebagian) di tahun pajak ini */
    public function untukTahun(int $tahun): array
    {
        return array_values(array_filter($this->semua()['masukan'], fn (array $m) => self::berlaku($m, "{$tahun}-01-01", "{$tahun}-12-31")));
    }

    public static function berlakuBulan(array $m, int $tahun, int $bulan): bool
    {
        $awal = CarbonImmutable::create($tahun, $bulan, 1);

        return self::berlaku($m, $awal->toDateString(), $awal->endOfMonth()->toDateString());
    }

    private static function berlaku(array $m, string $awal, string $akhir): bool
    {
        return (($m['mulai'] ?? null) === null || $m['mulai'] <= $akhir) && (($m['sampai'] ?? null) === null || $m['sampai'] >= $awal);
    }
}
