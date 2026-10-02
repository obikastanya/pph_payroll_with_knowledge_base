<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Table('payroll_bulan')]
#[Fillable(['bulan', 'hk_penuh', 'hk_aktual', 'kompensasi_persen', 'ota', 'lembur', 'komisi'])]
class PayrollBulan extends Model
{
    protected function casts(): array
    {
        return [
            'bulan' => 'integer',
            'hk_penuh' => 'integer',
            'hk_aktual' => 'integer',
            'ota' => 'integer',
            'lembur' => 'integer',
            'komisi' => 'integer',
        ];
    }

    public function payrollTahun(): BelongsTo
    {
        return $this->belongsTo(PayrollTahun::class);
    }
}
