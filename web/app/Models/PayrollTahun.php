<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\HasOne;

#[Table('payroll_tahun')]
#[Fillable([
    'tahun', 'status_ptkp', 'metode', 'gaji_pokok', 'kenaikan_nominal', 'kenaikan_tanggal',
    'kenaikan_hk_sebelum', 'kenaikan_hk_sesudah', 'kenaikan_hari_sebelum', 'kenaikan_hari_sesudah',
    'tunjangan_tetap_lama', 'tunjangan_prorata_lama', 'tunjangan_tetap_baru', 'tunjangan_prorata_baru',
    'tanggal_lebaran', 'tanggal_thr_bayar', 'bpjs_tk_mulai_bulan', 'bpjs_kes_mulai_bulan', 'kelas_jkk_persen',
])]
class PayrollTahun extends Model
{
    protected function casts(): array
    {
        return [
            'tahun' => 'integer',
            'gaji_pokok' => 'integer',
            'kenaikan_nominal' => 'integer',
            'kenaikan_tanggal' => 'date',
            'kenaikan_hk_sebelum' => 'integer',
            'kenaikan_hk_sesudah' => 'integer',
            'kenaikan_hari_sebelum' => 'integer',
            'kenaikan_hari_sesudah' => 'integer',
            'tunjangan_tetap_lama' => 'integer',
            'tunjangan_prorata_lama' => 'integer',
            'tunjangan_tetap_baru' => 'integer',
            'tunjangan_prorata_baru' => 'integer',
            'tanggal_lebaran' => 'date',
            'tanggal_thr_bayar' => 'date',
            'bpjs_tk_mulai_bulan' => 'integer',
            'bpjs_kes_mulai_bulan' => 'integer',
        ];
    }

    public function pegawai(): BelongsTo
    {
        return $this->belongsTo(Pegawai::class);
    }

    public function bulan(): HasMany
    {
        return $this->hasMany(PayrollBulan::class)->orderBy('bulan');
    }

    public function perhitungan(): HasMany
    {
        return $this->hasMany(Perhitungan::class)->orderByDesc('id');
    }

    public function perhitunganTerakhir(): HasOne
    {
        return $this->hasOne(Perhitungan::class)->latestOfMany();
    }
}
