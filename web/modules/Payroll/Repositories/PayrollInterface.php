<?php

namespace Modules\Payroll\Repositories;

use App\Models\Payroll\PayrollTahun;
use App\Models\Payroll\Pegawai;
use Illuminate\Support\Collection;

interface PayrollInterface
{
    /** Data HR satu tahun pajak (dengan pegawai, bulan, perhitungan terakhir), urut nomor induk. */
    public function daftarTahun(int $tahun, ?string $cari = null): Collection;

    /** Tahun pajak yang sudah punya data HR, terbaru dulu. */
    public function tahunAda(): array;

    /** Tahun yang belum punya data HR dan termasuk masa kerja pegawai, terbaru dulu. */
    public function tahunBelumDiisi(Pegawai $pegawai): array;

    /**
     * Isian awal form tambah: [PayrollTahun belum disimpan, baris 12 bulan, isian tambahan KB (bentuk isianMasukan)].
     * Isian tambahan tahunan untuk $kunciTahunan dilanjutkan dari tahun terbaru pegawai yang memilikinya.
     */
    public function isianBaru(Pegawai $pegawai, int $tahun, array $kunciTahunan = []): array;

    /** Isian form ubah: baris 12 bulan dari database. */
    public function isianBulan(PayrollTahun $payroll): array;

    /** Isian tambahan dari KB yang tersimpan: ['tahun' => [kunci => nilai], 'bulan' => [bulan => [kunci => nilai]]]. */
    public function isianMasukan(?PayrollTahun $payroll): array;

    /**
     * Simpan data tahunan + bulan (bulan yang seluruhnya kosong dihapus) + isian tambahan KB ([{kunci, bulan, nilai}];
     * nilai null = hapus). Isian tambahan untuk kunci yang tidak tampil di form tidak disentuh.
     */
    public function simpan(Pegawai $pegawai, array $dataTahun, array $dataBulan, ?PayrollTahun $payroll = null, array $dataMasukan = []): PayrollTahun;
}
