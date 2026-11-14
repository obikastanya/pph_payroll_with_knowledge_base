<?php

namespace App\Models\Payroll;

use App\Models\User;
use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

/**
 * Satu kali panggilan engine untuk satu pegawai-tahun. `kasus` disimpan sebagai teks JSON persis seperti yang
 * dikirim, sehingga "data berubah sejak dihitung" cukup dideteksi dengan membandingkan teks.
 */
#[Table('perhitungan')]
#[Fillable([
    'user_id', 'berhasil', 'jenis_galat', 'pesan', 'kasus', 'hasil', 'cek_silang', 'cek_silang_rinci', 'versi_engine', 'versi_kb',
    'sidik_kb', 'bruto_setahun', 'pph21_setahun', 'thp_setahun',
])]
class Perhitungan extends Model
{
    protected function casts(): array
    {
        return [
            'berhasil' => 'boolean',
            'bruto_setahun' => 'integer',
            'pph21_setahun' => 'integer',
            'thp_setahun' => 'integer',
        ];
    }

    public function payrollTahun(): BelongsTo
    {
        return $this->belongsTo(PayrollTahun::class);
    }

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    /** Keluaran engine (per_masa, tahunan, jejak, peringatan, rincian_pasal17, audit), atau null bila galat. */
    public function hasilEngine(): ?array
    {
        return $this->hasil === null ? null : json_decode($this->hasil, true, 512, JSON_THROW_ON_ERROR);
    }

    /**
     * versi_kb ringkas untuk tampilan: 12 karakter pertama hash commit beserta penandanya bila ada ("+belum-dikomit" =
     * KB/engine berubah tanpa di-commit); nilai lain (mis. "tidak-diketahui") utuh.
     */
    public function versiKbRingkas(): ?string
    {
        return preg_match('/^([0-9a-f]{40,64})(\+.+)?$/', (string) $this->versi_kb, $m)
            ? substr($m[1], 0, 12).($m[2] ?? '')
            : $this->versi_kb;
    }

    /** Selisih terhadap kalkulator tanpa KB (E12): [{bulan, fakta, kb, tanpa_kb}]. */
    public function selisihCekSilang(): array
    {
        return $this->cek_silang_rinci === null ? [] : json_decode($this->cek_silang_rinci, true, 512, JSON_THROW_ON_ERROR);
    }
}
