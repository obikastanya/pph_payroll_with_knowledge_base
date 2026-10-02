<?php

namespace Modules\BasisPengetahuan\Repositories;

use App\Models\Kb\UsulanKb;
use Illuminate\Contracts\Pagination\LengthAwarePaginator;
use Illuminate\Support\Collection;

class UsulanKbRepository implements UsulanKbInterface
{
    public function daftar(array $opsi): LengthAwarePaginator
    {
        $cari = trim((string) ($opsi['search'] ?? ''));
        $perHalaman = min(max((int) ($opsi['paginated'] ?? 10), 1), 100);

        return UsulanKb::query()
            ->with('user')
            ->when($cari !== '', fn ($q) => $q->where(fn ($w) => $w->where('judul', 'like', "%{$cari}%")->orWhere('nama_pdf', 'like', "%{$cari}%")))
            ->when(array_key_exists($opsi['status'] ?? '', UsulanKb::STATUS), fn ($q) => $q->where('status', $opsi['status']))
            ->when(array_key_exists($opsi['lapisan'] ?? '', UsulanKb::LAPISAN), fn ($q) => $q->where('lapisan', $opsi['lapisan']))
            ->orderByDesc('id')
            ->paginate($perHalaman);
    }

    public function aktif(): Collection
    {
        return UsulanKb::query()->aktif()->with('penerap')->get();
    }

    public function buat(array $data): UsulanKb
    {
        return UsulanKb::create($data);
    }
}
