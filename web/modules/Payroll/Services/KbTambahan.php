<?php

namespace Modules\Payroll\Services;

use App\Models\Kb\UsulanKb;
use ErrorException;
use Illuminate\Support\Facades\Log;
use RuntimeException;

/**
 * Berkas KB tambahan yang disetujui di menu Basis pengetahuan: ditulis ke {root}/kb/tambahan/ dan dikirim ke
 * engine (`berkas_tambahan`) pada setiap panggilan selama aktif. Isi berkas tidak pernah dibaca/ditafsirkan di
 * PHP; validasinya selalu oleh engine.
 */
final class KbTambahan
{
    /**
     * Database adalah sumber kebenaran: berkas aktif yang hilang (klon baru, restore database tanpa folder kb/tambahan
     * yang di-gitignore) atau isinya berbeda dengan kolom yaml ditulis ulang dari database. Tanpa ini setiap panggilan
     * engine gagal karena berkas tidak ditemukan, dan berkasnya pun tidak dapat dinonaktifkan.
     *
     * @return list<string> path relatif terhadap root, urut waktu diterapkan, mis. kb/tambahan/0003_transport.yaml
     */
    public function berkasAktif(): array
    {
        return UsulanKb::query()->aktif()->get(['id', 'nama_berkas', 'yaml'])->map(function (UsulanKb $u) {
            $this->pulihkan($u);

            return $this->relatif($u->nama_berkas);
        })->all();
    }

    private function pulihkan(UsulanKb $u): void
    {
        if ($u->yaml === null) {
            return;
        }
        $path = $this->absolut($u->nama_berkas);
        $ada = is_file($path);
        if ($ada && file_get_contents($path) === self::normal($u->yaml)) {
            return;
        }
        try {
            $this->tulis($u->nama_berkas, $u->yaml);
            Log::warning($ada ? 'Berkas KB tambahan berbeda dengan database; ditulis ulang dari database'
                : 'Berkas KB tambahan hilang; ditulis ulang dari database', ['usulan' => $u->id, 'berkas' => $this->relatif($u->nama_berkas)]);
        } catch (RuntimeException|ErrorException $e) {
            // engine nanti melaporkan berkas yang tidak dapat dibaca; halaman tetap terbuka agar admin dapat bertindak
            Log::error('Berkas KB tambahan tidak dapat dipulihkan', ['usulan' => $u->id, 'galat' => $e->getMessage()]);
        }
    }

    public function relatif(string $nama): string
    {
        return trim(config('payroll.kb_tambahan_dir'), '/\\').'/'.$nama;
    }

    public function absolut(string $nama): string
    {
        return rtrim(config('payroll.root'), '/\\').DIRECTORY_SEPARATOR.str_replace('/', DIRECTORY_SEPARATOR, $this->relatif($nama));
    }

    /**
     * Sidik isi berkas aktif (sama dengan jembatan/__main__.py::sidik_kb). Perhitungan yang sidiknya berbeda dengan
     * sidik sekarang dihitung dengan aturan lama. '' = tanpa berkas tambahan.
     */
    public function sidik(?array $berkas = null): string
    {
        $berkas ??= $this->berkasAktif();
        if ($berkas === []) {
            return '';
        }
        $h = hash_init('sha256');
        foreach ($berkas as $rel) {
            $path = rtrim(config('payroll.root'), '/\\').DIRECTORY_SEPARATOR.str_replace('/', DIRECTORY_SEPARATOR, $rel);
            hash_update($h, basename($rel)."\0".(is_file($path) ? file_get_contents($path) : '')."\0");
        }

        return substr(hash_final($h), 0, 16);
    }

    public function tulis(string $nama, string $isi): void
    {
        $path = $this->absolut($nama);
        if (! is_dir(dirname($path)) && ! mkdir(dirname($path), 0775, true) && ! is_dir(dirname($path))) {
            throw new RuntimeException('folder KB tambahan tidak dapat dibuat: '.dirname($path));
        }
        if (file_put_contents($path, self::normal($isi)) === false) {
            throw new RuntimeException("berkas KB tidak dapat ditulis: {$path}");
        }
    }

    public function hapus(string $nama): void
    {
        $path = $this->absolut($nama);
        if (is_file($path)) {
            unlink($path);
        }
    }

    /** Akhir baris LF dan satu baris kosong di akhir (textarea browser mengirim CRLF). */
    public static function normal(string $isi): string
    {
        return rtrim(str_replace("\r\n", "\n", $isi))."\n";
    }
}
