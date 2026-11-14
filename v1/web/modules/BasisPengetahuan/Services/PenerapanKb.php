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

    /**
     * Validasi $yaml (atau rancangan tersimpan) terhadap berkas aktif selain usulan ini; hasil disimpan ke usulan.
     * Lapisan pilihan unggah ikut dikirim agar engine dapat membandingkannya dengan lapisan yang tertulis di berkas.
     */
    public function validasi(UsulanKb $u, ?string $yaml = null): array
    {
        $yaml = KbTambahan::normal($yaml ?? (string) $u->yaml);
        $v = $this->mesin->validasi($yaml, $this->namaBerkas($u), $this->berkasLain($u), $u->lapisan);
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

    /**
     * Aktif kembali = diterapkan ulang di urutan paling akhir. Urutan tidak lagi memengaruhi amandemen parameter (engine
     * mengurutkannya menurut tanggal mulai), tetapi tetap menentukan sidik_kb: sidik meng-hash berkas dalam urutan ini.
     */
    public function aktifkan(UsulanKb $u, User $oleh): array
    {
        $v = $this->validasi($u);
        if ($v['ok']) {
            $this->kb->tulis($u->nama_berkas, $u->yaml);
            $u->update(['aktif' => true, 'diterapkan_pada' => now(), 'diterapkan_oleh' => $oleh->id]);
        }

        return $v;
    }

    /**
     * Engine memuat dan menghitung KB tanpa berkas ini dulu (perintah periksa); berkas lain mungkin bergantung padanya.
     *
     * @throws MesinTidakTersedia bila KB tanpa berkas ini tidak dapat dimuat atau dihitung (pesan = galat engine)
     */
    public function nonaktifkan(UsulanKb $u): void
    {
        $p = $this->mesin->periksa($this->berkasLain($u));
        if (! ($p['ok'] ?? false)) {
            $galat = array_filter(is_array($p['galat'] ?? null) ? $p['galat'] : [], 'is_scalar');
            throw new MesinTidakTersedia($galat === [] ? 'engine menolak KB sisanya tanpa keterangan' : implode("\n", $galat));
        }
        $u->update(['aktif' => false]);
    }

    /**
     * Hapus usulan yang tidak aktif. Baris dihapus lebih dulu secara bersyarat: usulan antre yang baru saja diambil
     * job (status diproses) tidak kehilangan PDF-nya di tengah jalan.
     *
     * @return bool false bila usulan sedang dibaca LLM (tidak dihapus)
     */
    public function hapus(UsulanKb $u): bool
    {
        if ($u->aktif) {
            throw new \LogicException('berkas KB yang aktif tidak boleh dihapus; nonaktifkan dulu');
        }
        if (UsulanKb::whereKey($u->id)->where('status', '!=', 'diproses')->where('aktif', false)->delete() === 0) {
            return false;
        }
        if ($u->nama_berkas) {
            $this->kb->hapus($u->nama_berkas);
        }
        Storage::disk('local')->delete($u->path_pdf);

        return true;
    }

    public function namaBerkas(UsulanKb $u): string
    {
        if ($u->nama_berkas) {
            return $u->nama_berkas;
        }
        $id = is_array($u->usulan) ? ($u->usulan['id_berkas'] ?? '') : '';
        $dasar = Str::slug(is_string($id) ? $id : '', '_') ?: Str::slug($u->judul, '_') ?: 'rancangan';

        return sprintf('%04d_%s.yaml', $u->id, Str::limit($dasar, 50, ''));
    }

    private function berkasLain(UsulanKb $u): array
    {
        $diri = $u->nama_berkas ? $this->kb->relatif($u->nama_berkas) : null;

        return array_values(array_filter($this->kb->berkasAktif(), fn ($b) => $b !== $diri));
    }
}
