<?php

namespace Modules\BasisPengetahuan\Jobs;

use App\Models\Kb\UsulanKb;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Process\Exceptions\ProcessTimedOutException;
use Illuminate\Queue\MaxAttemptsExceededException;
use Illuminate\Queue\TimeoutExceededException;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;
use Modules\Payroll\Services\MesinPajak;
use Modules\Payroll\Services\MesinTidakTersedia;
use Throwable;

/**
 * Membaca PDF peraturan dengan LLM lewat jembatan (`perintah: usulkan`), lalu menyimpan rancangan berkas KB dan hasil
 * validasinya. Berjalan di antrean karena satu dokumen bisa memakan beberapa menit. Rancangan TIDAK diterapkan di
 * sini: status akhirnya siap_tinjau dan menunggu admin.
 *
 * Setiap perubahan status bersyarat pada status yang diharapkan: usulan yang dibatalkan (dihapus saat antre), ditandai
 * macet, atau diambil job lain tidak ditimpa oleh job yang terlambat selesai.
 */
class ProsesUsulanKb implements ShouldQueue
{
    use Queueable;

    public const PESAN_PEKERJA_BERHENTI = 'Proses tidak selesai: pekerja antrean berhenti atau job diambil ulang sebelum selesai. Tekan Baca ulang.';

    public int $tries = 1;

    public int $timeout;

    public function __construct(public int $usulanId)
    {
        $this->timeout = config('payroll.llm_timeout') + 60;
    }

    public function handle(MesinPajak $mesin): void
    {
        $u = UsulanKb::find($this->usulanId);
        if ($u === null || $u->status !== 'antre') {
            return;
        }
        // ambil alih secara bersyarat: bila baris baru saja dihapus/dibatalkan, job berhenti tanpa memanggil LLM
        if (UsulanKb::whereKey($u->id)->where('status', 'antre')->update(['status' => 'diproses', 'pesan_galat' => null]) === 0) {
            return;
        }
        $mulai = hrtime(true);
        try {
            $j = $mesin->usulkan(Storage::disk('local')->path($u->path_pdf), $u->lapisan, $u->catatan);
        } catch (MesinTidakTersedia $e) {
            $this->simpanBilaMasihDiproses($u, ['status' => 'gagal', 'pesan_galat' => $e->getMessage()]);
            Log::warning('Usulan KB gagal dibaca', ['usulan' => $u->id, 'durasi_detik' => self::detikSejak($mulai), 'galat' => mb_substr($e->getMessage(), 0, 500)]);

            return;
        }
        $status = $j['yaml'] === '' ? 'tidak_dapat_dikodifikasi' : 'siap_tinjau';
        $tersimpan = $this->simpanBilaMasihDiproses($u, [
            'usulan' => $j['usulan'],
            'info_llm' => $j['info'],
            'yaml' => $j['yaml'] !== '' ? $j['yaml'] : null,
            'validasi' => $j['validasi'],
            'valid' => isset($j['validasi']) ? (bool) $j['validasi']['ok'] : null,
            'status' => $status,
            'pesan_galat' => null,
        ]);
        $info = is_array($j['info'] ?? null) ? $j['info'] : [];
        Log::info($tersimpan ? 'Usulan KB selesai dibaca' : 'Usulan KB selesai dibaca, tetapi hasilnya dibuang (status sudah berubah)', [
            'usulan' => $u->id, 'status' => $status, 'model' => $info['model'] ?? null, 'durasi_detik' => self::detikSejak($mulai),
            'token_masuk' => $info['token_masuk'] ?? null, 'token_keluar' => $info['token_keluar'] ?? null,
            'token_cache_baca' => $info['token_cache_baca'] ?? null,
        ]);
    }

    public function failed(?Throwable $e): void
    {
        $pesan = match (true) {
            $e instanceof ProcessTimedOutException => 'Membaca dokumen melebihi batas waktu ('.config('payroll.llm_timeout').' detik).',
            $e instanceof TimeoutExceededException => "Membaca dokumen melebihi batas waktu ({$this->timeout} detik).",
            $e instanceof MaxAttemptsExceededException => self::PESAN_PEKERJA_BERHENTI,
            default => 'Proses berhenti: '.($e?->getMessage() ?: 'sebab tidak diketahui'),
        };
        UsulanKb::whereKey($this->usulanId)->whereIn('status', ['antre', 'diproses'])->update(['status' => 'gagal', 'pesan_galat' => $pesan]);
        Log::warning('Job usulan KB gagal', ['usulan' => $this->usulanId, 'jenis' => $e ? $e::class : null, 'pesan' => $pesan]);
    }

    /** Update hanya bila usulan masih diproses job ini; atribut lewat model agar cast JSON/boolean berlaku. */
    private function simpanBilaMasihDiproses(UsulanKb $u, array $atribut): bool
    {
        $u->fill($atribut);

        return UsulanKb::whereKey($u->id)->where('status', 'diproses')->update(array_intersect_key($u->getAttributes(), $atribut)) > 0;
    }

    private static function detikSejak(int $mulai): int
    {
        return intdiv(hrtime(true) - $mulai, 1_000_000_000);
    }
}
