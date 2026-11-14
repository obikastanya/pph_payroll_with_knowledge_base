<?php

namespace App\Models\Payroll;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\HasOne;

#[Table('pegawai')]
#[Fillable(['nomor_induk', 'nama', 'jenis_kelamin', 'punya_npwp', 'tanggal_masuk', 'tanggal_berhenti'])]
class Pegawai extends Model
{
    protected function casts(): array
    {
        return [
            'punya_npwp' => 'boolean',
            'tanggal_masuk' => 'date',
            'tanggal_berhenti' => 'date',
        ];
    }

    public function payrollTahun(): HasMany
    {
        return $this->hasMany(PayrollTahun::class)->orderByDesc('tahun');
    }

    public function payrollTerakhir(): HasOne
    {
        return $this->hasOne(PayrollTahun::class)->latestOfMany('tahun');
    }

    /** Bulan pertama & terakhir bekerja di tahun pajak, atau null bila tidak bekerja sama sekali di tahun itu. */
    public function rentangBulan(int $tahun): ?array
    {
        if ($this->tanggal_masuk->year > $tahun) {
            return null;
        }
        if ($this->tanggal_berhenti && $this->tanggal_berhenti->year < $tahun) {
            return null;
        }
        $mulai = $this->tanggal_masuk->year === $tahun ? $this->tanggal_masuk->month : 1;
        $akhir = $this->tanggal_berhenti && $this->tanggal_berhenti->year === $tahun ? $this->tanggal_berhenti->month : 12;

        return $akhir < $mulai ? null : [$mulai, $akhir];
    }
}
