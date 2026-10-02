<?php

namespace Modules\BasisPengetahuan\Jobs;

use App\Models\Kb\UsulanKb;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Support\Facades\Storage;
use Modules\Payroll\Services\MesinPajak;
use Modules\Payroll\Services\MesinTidakTersedia;
use Throwable;

/**
 * Membaca PDF peraturan dengan LLM lewat jembatan (`perintah: usulkan`), lalu menyimpan rancangan berkas KB dan hasil
 * validasinya. Berjalan di antrean karena satu dokumen bisa memakan beberapa menit. Rancangan TIDAK diterapkan di
 * sini: status akhirnya siap_tinjau dan menunggu admin.
 */
class ProsesUsulanKb implements ShouldQueue
{
    use Queueable;

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
        $u->update(['status' => 'diproses', 'pesan_galat' => null]);
        try {
            $j = $mesin->usulkan(Storage::disk('local')->path($u->path_pdf), $u->lapisan, $u->catatan);
        } catch (MesinTidakTersedia $e) {
            $u->update(['status' => 'gagal', 'pesan_galat' => $e->getMessage()]);

            return;
        }
        $u->update([
            'usulan' => $j['usulan'],
            'info_llm' => $j['info'],
            'yaml' => $j['yaml'] !== '' ? $j['yaml'] : null,
            'validasi' => $j['validasi'],
            'valid' => isset($j['validasi']) ? (bool) $j['validasi']['ok'] : null,
            'status' => $j['yaml'] === '' ? 'tidak_dapat_dikodifikasi' : 'siap_tinjau',
        ]);
    }

    public function failed(?Throwable $e): void
    {
        UsulanKb::whereKey($this->usulanId)->whereIn('status', ['antre', 'diproses'])
            ->update(['status' => 'gagal', 'pesan_galat' => 'Proses berhenti: '.($e?->getMessage() ?: 'sebab tidak diketahui')]);
    }
}
