<?php

namespace Modules\Payroll\Services;

use Throwable;

/**
 * Engine gagal (tidak dapat dipanggil, jawaban rusak, atau batas waktu habis) di tengah hitung. Batch sebelumnya sudah
 * tercatat ($dicatat pegawai); batch yang gagal dan sesudahnya tidak.
 */
class HitungTerhenti extends MesinTidakTersedia
{
    public function __construct(string $pesan, public readonly int $dicatat, ?Throwable $sebab = null)
    {
        parent::__construct($pesan, 0, $sebab);
    }
}
