<?php

namespace Modules\BasisPengetahuan\Repositories;

use App\Models\Kb\UsulanKb;
use Illuminate\Contracts\Pagination\LengthAwarePaginator;
use Illuminate\Support\Collection;

interface UsulanKbInterface
{
    /** Daftar usulan untuk tabel: search (judul / nama PDF), status, lapisan, paginated. Terbaru dulu. */
    public function daftar(array $opsi): LengthAwarePaginator;

    /** Berkas KB tambahan yang sedang dimuat engine, urut waktu diterapkan. */
    public function aktif(): Collection;

    public function buat(array $data): UsulanKb;
}
