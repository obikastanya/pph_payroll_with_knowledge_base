<?php

namespace Modules\BasisPengetahuan\Services;

use App\Models\Kb\UsulanKb;
use App\Models\User;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;
use Modules\Payroll\Services\KbTambahan;
use Modules\Payroll\Services\MesinPajak;
use Modules\Payroll\Services\MesinTidakTersedia;

/**
 * Siklus hidup berkas KB tambahan: validasi ulang rancangan, terapkan (tulis ke kb/tambahan/), aktif/nonaktif, hapus.
 * Setiap langkah yang mengubah KB yang dimuat engine didahului validasi engine terhadap berkas aktif lainnya, sehingga
 * KB aktif selalu dapat dimuat (tidak ada perhitungan payroll yang rusak karena berkas yang bertentangan).
 */
final class PenerapanKb
{
    public function __construct(private MesinPajak $mesin, private KbTambahan $kb) {}

    /** Validasi $yaml (atau rancangan tersimpan) terhadap berkas aktif selain usulan ini; hasil disimpan ke usulan. */
    public function validasi(UsulanKb $u, ?string $yaml = null): array
    {
        $yaml = KbTambahan::normal($yaml ?? (string) $u->yaml);
        $v = $this->mesin->validasi($yaml, $this->namaBerkas($u), $this->berkasLain($u));
        $u->update(['yaml' => $yaml, 'validasi' => $v, 'valid' => (bool) $v['ok']]);

        return $v;
    }

    /** @return array hasil validasi; berkas hanya ditulis & diaktifkan bila validasi lolos */
    public function terapkan(UsulanKb $u, User $oleh): array
    {
        $v = $this->validasi($u);
        if ($v['ok']) {
            $nama = $this->namaBerkas($u);
            $this->kb->tulis($nama, $u->yaml);
            $u->update(['status' => 'diterapkan', 'aktif' => true, 'nama_berkas' => $nama, 'diterapkan_pada' => now(),
                'diterapkan_oleh' => $oleh->id]);
        }

        return $v;
    }

    /** Aktif kembali = diterapkan ulang di urutan paling akhir (urutan berpengaruh pada amandemen parameter). */
    public function aktifkan(UsulanKb $u, User $oleh): array
    {
        $v = $this->validasi($u);
        if ($v['ok']) {
            $this->kb->tulis($u->nama_berkas, $u->yaml);
            $u->update(['aktif' => true, 'diterapkan_pada' => now(), 'diterapkan_oleh' => $oleh->id]);
        }

        return $v;
    }

    /** @throws MesinTidakTersedia bila KB tanpa berkas ini tidak dapat dimuat (berkas lain bergantung padanya) */
    public function nonaktifkan(UsulanKb $u): void
    {
        $this->mesin->masukan($this->berkasLain($u));
        $u->update(['aktif' => false]);
    }

    public function hapus(UsulanKb $u): void
    {
        if ($u->aktif) {
            throw new \LogicException('berkas KB yang aktif tidak boleh dihapus; nonaktifkan dulu');
        }
        if ($u->nama_berkas) {
            $this->kb->hapus($u->nama_berkas);
        }
        Storage::disk('local')->delete($u->path_pdf);
        $u->delete();
    }

    public function namaBerkas(UsulanKb $u): string
    {
        if ($u->nama_berkas) {
            return $u->nama_berkas;
        }
        $dasar = Str::slug($u->usulan['id_berkas'] ?? '', '_') ?: Str::slug($u->judul, '_') ?: 'rancangan';

        return sprintf('%04d_%s.yaml', $u->id, Str::limit($dasar, 50, ''));
    }

    private function berkasLain(UsulanKb $u): array
    {
        $diri = $u->nama_berkas ? $this->kb->relatif($u->nama_berkas) : null;

        return array_values(array_filter($this->kb->berkasAktif(), fn ($b) => $b !== $diri));
    }
}
