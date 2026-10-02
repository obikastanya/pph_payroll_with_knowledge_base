<?php

namespace App\Models\Payroll;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

/** Satu nilai isian tambahan dari KB (bulan 0 = tahunan). `nilai` = JSON agar tipe tidak berubah. */
#[Table('payroll_masukan')]
#[Fillable(['kunci', 'bulan', 'nilai'])]
class PayrollMasukan extends Model
{
    protected function casts(): array
    {
        return [
            'bulan' => 'integer',
            'nilai' => 'json',
        ];
    }

    public function payrollTahun(): BelongsTo
    {
        return $this->belongsTo(PayrollTahun::class);
    }
}
