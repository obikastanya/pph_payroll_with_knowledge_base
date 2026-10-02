<?php

namespace Modules\Pegawai\Repositories;

use App\Models\Payroll\Pegawai;
use Illuminate\Contracts\Pagination\LengthAwarePaginator;

class PegawaiRepository implements PegawaiInterface
{
    /** Kolom yang boleh dipakai untuk urutan (nilai orderBy dari klien tidak pernah masuk SQL apa adanya). */
    public const URUTAN = ['nomor_induk', 'nama', 'tanggal_masuk'];

    public function daftar(array $opsi): LengthAwarePaginator
    {
        $cari = trim((string) ($opsi['search'] ?? ''));
        $orderBy = in_array($opsi['orderBy'] ?? null, self::URUTAN, true) ? $opsi['orderBy'] : 'nomor_induk';
        $orderDir = ($opsi['orderDir'] ?? 'asc') === 'desc' ? 'desc' : 'asc';
        $perHalaman = min(max((int) ($opsi['paginated'] ?? 10), 1), 100);

        return Pegawai::query()
            ->with('payrollTerakhir')
            // Pencarian: nama atau nomor induk
            ->when($cari !== '', fn ($q) => $q->where(fn ($w) => $w->where('nama', 'like', "%{$cari}%")->orWhere('nomor_induk', 'like', "%{$cari}%")))
            // Filter: status kerja hari ini
            ->when(($opsi['status'] ?? null) === 'aktif', fn ($q) => $q->where(fn ($w) => $w->whereNull('tanggal_berhenti')->orWhere('tanggal_berhenti', '>=', today())))
            ->when(($opsi['status'] ?? null) === 'berhenti', fn ($q) => $q->where('tanggal_berhenti', '<', today()))
            // Filter: jenis kelamin
            ->when(in_array($opsi['jenis_kelamin'] ?? null, ['L', 'P'], true), fn ($q) => $q->where('jenis_kelamin', $opsi['jenis_kelamin']))
            ->orderBy($orderBy, $orderDir)
            ->orderBy('id')
            ->paginate($perHalaman);
    }

    public function simpan(array $data, ?Pegawai $pegawai = null): Pegawai
    {
        if ($pegawai) {
            $pegawai->update($data);

            return $pegawai;
        }

        return Pegawai::create($data);
    }

    public function hapus(Pegawai $pegawai): void
    {
        $pegawai->delete();   // payroll_tahun, payroll_bulan, perhitungan ikut terhapus (cascade)
    }
}
