<?php

namespace Modules\Pegawai\Repositories;

use App\Models\Payroll\Pegawai;
use Illuminate\Contracts\Pagination\LengthAwarePaginator;

interface PegawaiInterface
{
    /** Daftar pegawai terpaginasi. Opsi: search, status (aktif|berhenti), jenis_kelamin, orderBy, orderDir, paginated. */
    public function daftar(array $opsi): LengthAwarePaginator;

    public function simpan(array $data, ?Pegawai $pegawai = null): Pegawai;

    public function hapus(Pegawai $pegawai): void;
}
