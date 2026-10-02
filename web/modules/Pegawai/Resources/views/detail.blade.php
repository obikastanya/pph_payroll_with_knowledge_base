@extends('main.index')
@use('App\Helpers\Format')
@use('Modules\Payroll\Services\Label')

@section('page-title', $pegawai->nama)

@section('content')
    <div class="row g-2">
        <div class="col-12">
            <div class="card">
                <div class="card-body p-3">
                    <div class="d-flex flex-wrap justify-content-between align-items-start gap-3 mb-3">
                        <div class="d-flex align-items-center gap-3">
                            <span class="avatar avatar-md rounded-3 mdka-bg-blue-100 mdka-text-blue-600"><i class="ti ti-user fs-2"></i></span>
                            <div>
                                <div class="text-muted small">{{ $pegawai->nomor_induk }}</div>
                                <h3 class="mb-0">{{ $pegawai->nama }}</h3>
                            </div>
                        </div>
                        <div class="d-flex gap-2">
                            <x-global.btn-detail label="Ubah" color="orange" size="sm" outline="true" onclick="bukaModalPegawai('edit', {{ $pegawai->id }})">
                                <x-slot:icon><i class="ti ti-edit"></i></x-slot:icon>
                            </x-global.btn-detail>
                            <x-global.btn-detail label="" color="red" size="sm" outline="true" onclick="hapusPegawai()" data-bs-toggle="tooltip" data-bs-title="Hapus pegawai">
                                <x-slot:icon><i class="ti ti-trash"></i></x-slot:icon>
                            </x-global.btn-detail>
                        </div>
                    </div>
                    <div class="datagrid">
                        <div class="datagrid-item">
                            <div class="datagrid-title">Jenis kelamin</div>
                            <div class="datagrid-content">{{ Label::JENIS_KELAMIN[$pegawai->jenis_kelamin] ?? $pegawai->jenis_kelamin }}</div>
                        </div>
                        <div class="datagrid-item">
                            <div class="datagrid-title">NPWP / NIK valid</div>
                            <div class="datagrid-content">
                                @if ($pegawai->punya_npwp)
                                    <span class="status status-green">ya</span>
                                @else
                                    <span class="status status-red">tidak</span>
                                @endif
                            </div>
                        </div>
                        <div class="datagrid-item">
                            <div class="datagrid-title">Masuk kerja</div>
                            <div class="datagrid-content">{{ Format::tanggal($pegawai->tanggal_masuk) }}</div>
                        </div>
                        <div class="datagrid-item">
                            <div class="datagrid-title">Berhenti</div>
                            <div class="datagrid-content">{{ $pegawai->tanggal_berhenti ? Format::tanggal($pegawai->tanggal_berhenti) : 'masih bekerja' }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-12">
            <div class="card">
                <div class="card-body p-2">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h4 class="mb-0 ms-1">Data HR per tahun pajak</h4>
                        <x-global.btn-detail label="Tambah tahun" color="blue" size="sm" href="{{ route('payroll.create', $pegawai) }}">
                            <x-slot:icon><i class="ti ti-plus"></i></x-slot:icon>
                        </x-global.btn-detail>
                    </div>
                    <div class="card overflow-hidden mdka-border-gray-200">
                        <div class="card-body table-responsive p-0">
                            <table class="table table-vcenter mb-0 text-nowrap">
                                <thead>
                                    <tr class="mdka-bg-gray-50">
                                        <th class="py-3">Tahun</th>
                                        <th class="py-3">PTKP</th>
                                        <th class="py-3">Metode</th>
                                        <th class="py-3 text-end">Gaji pokok</th>
                                        <th class="py-3 text-end">PPh 21 setahun</th>
                                        <th class="py-3">Cek silang</th>
                                        <th class="py-3">Dihitung</th>
                                        <th class="py-3 text-center">Aksi</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    @forelse ($pegawai->payrollTahun as $pt)
                                        @php($p = $pt->perhitunganTerakhir)
                                        <tr>
                                            <td><a href="{{ route('payroll.show', $pt) }}" class="fw-bold">{{ $pt->tahun }}</a></td>
                                            <td>{{ $pt->status_ptkp }}</td>
                                            <td class="text-muted">{{ Label::METODE[$pt->metode] ?? $pt->metode }}</td>
                                            <td class="angka">{{ Format::rp($pt->gaji_pokok, false) }}</td>
                                            <td class="angka fw-bold">
                                                @if ($p?->berhasil)
                                                    {{ Format::rp($p->pph21_setahun, false) }}
                                                @elseif ($p)
                                                    <span class="status status-red">galat</span>
                                                @endif
                                            </td>
                                            <td><x-global.cek-silang :status="$p?->cek_silang" /></td>
                                            <td class="text-muted">{{ $p ? $p->created_at->format('d/m/Y H:i') : 'belum' }}</td>
                                            <td class="text-center">
                                                <x-global.btn-detail label="" color="blue" size="sm" href="{{ route('payroll.show', $pt) }}" data-bs-toggle="tooltip" data-bs-title="Lihat hasil">
                                                    <x-slot:icon><i class="ti ti-eye"></i></x-slot:icon>
                                                </x-global.btn-detail>
                                                <x-global.btn-detail label="" color="orange" size="sm" href="{{ route('payroll.edit', $pt) }}" data-bs-toggle="tooltip" data-bs-title="Ubah data HR">
                                                    <x-slot:icon><i class="ti ti-edit"></i></x-slot:icon>
                                                </x-global.btn-detail>
                                            </td>
                                        </tr>
                                    @empty
                                        <tr>
                                            <td colspan="8" class="text-center text-muted py-4">Belum ada data HR. Tambahkan tahun pajak pertama.</td>
                                        </tr>
                                    @endforelse
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    @include('Pegawai::modal')
@endsection

@push('javascript')
    <script>
        window.setelahSimpanPegawai = () => setTimeout(() => location.reload(), 900);

        function hapusPegawai() {
            Swal.fire({
                title: @json("Hapus {$pegawai->nama}?"),
                text: 'Seluruh data payroll dan riwayat perhitungannya ikut terhapus.',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Hapus',
                cancelButtonText: 'Batal',
                reverseButtons: true,
            }).then(result => {
                if (!result.isConfirmed) return;
                $.ajax({
                    url: @json(route('pegawai.destroy', $pegawai)),
                    type: 'DELETE',
                    success: () => location.href = @json(route('pegawai.index')),
                    error: showError
                });
            });
        }
    </script>
@endpush
