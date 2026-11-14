@extends('main.index')

@section('page-title', 'Pegawai & data HR')

@section('content')
    <div class="row g-2">
        {{-- Filter --}}
        <div class="col-12">
            @include('Pegawai::filter')
        </div>
        {{-- Table --}}
        <div class="col-12">
            <div class="card">
                <div class="card-body p-2">
                    <div class="row g-2">
                        <div class="col-12 d-flex flex-wrap justify-content-between gap-2">
                            <div class="d-flex gap-2">
                                <input type="text" name="search" id="pegawaiSearch" value="" class="form-control rounded-3"
                                    autocomplete="off" placeholder="Cari nama / nomor induk…" aria-label="Cari pegawai" style="min-width: 240px" />
                                <x-global.btn-detail label="" color="blue" size="sm" outline="true" id="toggleSearchButton"
                                    data-bs-toggle="tooltip" data-bs-title="Cari">
                                    <x-slot:icon><i class="ti ti-search"></i></x-slot:icon>
                                </x-global.btn-detail>
                                <x-global.btn-detail label="" color="purple" size="sm" outline="true" id="toggleFilterButton"
                                    data-bs-toggle="tooltip" data-bs-title="Filter">
                                    <x-slot:icon><i class="ti ti-filter"></i></x-slot:icon>
                                </x-global.btn-detail>
                                <x-global.btn-detail label="" color="red" size="sm" outline="true" id="toggleResetButton"
                                    data-bs-toggle="tooltip" data-bs-title="Reset">
                                    <x-slot:icon><i class="ti ti-restore"></i></x-slot:icon>
                                </x-global.btn-detail>
                            </div>
                            <div class="d-flex gap-2">
                                <x-global.btn-detail label="Tambah pegawai" color="blue" size="sm" onclick="bukaModalPegawai('add', null)">
                                    <x-slot:icon><i class="ti ti-plus"></i></x-slot:icon>
                                </x-global.btn-detail>
                            </div>
                        </div>

                        <div class="col-12">
                            <div class="card overflow-hidden mdka-border-gray-200">
                                <div class="card-body table-responsive p-0">
                                    <table class="table table-vcenter mdka-border-gray-100 text-nowrap mb-0" id="pegawaiTable">
                                        <thead>
                                            <tr class="mdka-bg-gray-50">
                                                <th scope="col" width="30" class="fs-5 py-3 text-center">No</th>
                                                <th scope="col" data-key="nomor_induk" class="fs-5 py-3">Nomor induk</th>
                                                <th scope="col" data-key="nama" class="fs-5 py-3">Nama</th>
                                                <th scope="col" data-key="tanggal_masuk" class="fs-5 py-3">Masuk</th>
                                                <th scope="col" class="fs-5 py-3">Status kerja</th>
                                                <th scope="col" class="fs-5 py-3">Data HR terakhir</th>
                                                <th scope="col" class="fs-5 py-3 text-center">Aksi</th>
                                            </tr>
                                        </thead>
                                        <tbody></tbody>
                                    </table>
                                </div>
                            </div>
                            <div class="pagination-container mt-2"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    @include('Pegawai::modal')
@endsection

@push('javascript')
    {{-- URL list --}}
    <script>
        const urlPegawaiList = @json(route('pegawai.list'));
        const urlPegawaiDasar = @json(url('pegawai'));
    </script>

    {{-- render Table --}}
    <script>
        let currentPage = 1;
        let limit = 10;
        let search = '';
        let orderBy = 'nomor_induk';
        let orderDir = 'asc';

        const columns = [
            'index',
            {
                key: 'nomor_induk',
                sortable: true,
                className: 'text-muted'
            },
            {
                key: 'nama',
                sortable: true,
                render: item => `<a href="${item.url_detail}" class="fw-medium">${escapeHtml(item.nama)}</a>`
            },
            {
                key: 'tanggal_masuk',
                sortable: true
            },
            {
                key: 'status',
                render: item => item.berhenti ?
                    `<span class="status status-gray">berhenti ${escapeHtml(item.tanggal_berhenti)}</span>` :
                    (item.tanggal_berhenti ? `<span class="status status-yellow">berhenti ${escapeHtml(item.tanggal_berhenti)}</span>` :
                        `<span class="status status-green">aktif</span>`)
            },
            {
                key: 'data_hr_terakhir',
                render: item => item.data_hr_terakhir ?
                    `<a href="${item.data_hr_terakhir.url}">${item.data_hr_terakhir.tahun}</a> <span class="text-muted">· ${escapeHtml(item.data_hr_terakhir.status_ptkp)}</span>` :
                    '<span class="text-muted">belum ada</span>'
            },
            {
                key: 'actions',
                className: 'text-center',
                render: item => `
                    <x-global.btn-detail label="" color="blue" size="sm" href="${item.url_detail}" data-bs-toggle="tooltip" data-bs-title="Detail & data HR">
                        <x-slot:icon><i class="ti ti-eye"></i></x-slot:icon>
                    </x-global.btn-detail>
                    <x-global.btn-detail label="" color="orange" size="sm" onclick="bukaModalPegawai('edit', ${item.id})" data-bs-toggle="tooltip" data-bs-title="Ubah">
                        <x-slot:icon><i class="ti ti-edit"></i></x-slot:icon>
                    </x-global.btn-detail>
                    <x-global.btn-detail label="" color="red" size="sm" onclick="hapusPegawai(${item.id})" data-bs-toggle="tooltip" data-bs-title="Hapus">
                        <x-slot:icon><i class="ti ti-trash"></i></x-slot:icon>
                    </x-global.btn-detail>`
            }
        ];

        function pegawaiTable() {
            renderTableWithFeatures({
                container: '#pegawaiTable',
                columns,
                currentPage,
                limit,
                loading: true
            });

            $.ajax({
                url: urlPegawaiList,
                type: 'GET',
                data: {
                    page: currentPage,
                    paginated: limit,
                    search,
                    orderBy,
                    orderDir,
                    ...filterList
                },
                dataType: 'json',
                success: response => {
                    renderTableWithFeatures({
                        container: '#pegawaiTable',
                        data: response.data,
                        columns,
                        currentPage,
                        limit,
                        meta: response.meta,
                        emptyText: search || filterList.status || filterList.jenis_kelamin ? 'Tidak ada pegawai yang cocok.' :
                            'Belum ada pegawai. Tambahkan pegawai, atau jalankan php artisan payroll:impor-contoh.',
                        onPageChange: page => {
                            currentPage = page;
                            pegawaiTable();
                        },
                        onLimitChange: newLimit => {
                            limit = newLimit;
                            currentPage = 1;
                            pegawaiTable();
                        },
                        onSortChange: (key, dir) => {
                            orderBy = key;
                            orderDir = dir;
                            pegawaiTable();
                        },
                        currentSortKey: orderBy,
                        currentSortDir: orderDir
                    });
                    $('#pegawaiTable [data-bs-toggle="tooltip"]').tooltip({
                        trigger: 'hover'
                    });
                },
                error: () => renderTableWithFeatures({
                    container: '#pegawaiTable',
                    columns,
                    currentPage,
                    limit,
                    emptyText: 'Gagal memuat data. Silakan coba lagi.'
                })
            });
        }

        // setelah modal menyimpan: muat ulang tabel
        window.setelahSimpanPegawai = () => pegawaiTable();

        function hapusPegawai(id) {
            Swal.fire({
                title: 'Hapus pegawai ini?',
                text: 'Seluruh data payroll dan riwayat perhitungannya ikut terhapus.',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Hapus',
                cancelButtonText: 'Batal',
                reverseButtons: true,
            }).then(result => {
                if (!result.isConfirmed) return;
                $.ajax({
                    url: `${urlPegawaiDasar}/${id}`,
                    type: 'DELETE',
                    success: res => {
                        Swal.fire({
                            icon: 'success',
                            title: 'Berhasil',
                            text: res.message,
                            timer: 2500,
                            showConfirmButton: false
                        });
                        pegawaiTable();
                    },
                    error: showError
                });
            });
        }

        $(function() {
            pegawaiTable();

            $('#toggleFilterButton').on('click', () => $('#pegawaiFilterCard').slideToggle(300));
            $('#toggleSearchButton').on('click', () => {
                search = $('#pegawaiSearch').val();
                currentPage = 1;
                pegawaiTable();
            });
            $('#pegawaiSearch').on('input', debounce(function() {
                search = $(this).val();
                currentPage = 1;
                pegawaiTable();
            })).on('keydown', e => e.key === 'Enter' && e.preventDefault());
            $('#toggleResetButton').on('click', () => {
                currentPage = 1;
                limit = 10;
                search = '';
                orderBy = 'nomor_induk';
                orderDir = 'asc';
                $('#pegawaiSearch').val('');
                resetFilter();
                $('#pegawaiFilterCard').slideUp(300);
            });
        });
    </script>
@endpush
