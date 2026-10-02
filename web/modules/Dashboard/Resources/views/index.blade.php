@extends('main.index')
@use('App\Helpers\Format')

@section('page-title', 'Dashboard')

@section('content')
    <div class="row g-2">
        {{-- Ringkasan --}}
        <div class="col-sm-6 col-xl-3">
            <x-global.summary-card title="Pegawai dengan data HR {{ $tahun }}" :value="$jumlah" color="blue"
                keterangan="{{ $belumDihitung }} belum dihitung / perlu dihitung ulang">
                <x-slot:icon><i class="ti ti-users"></i></x-slot:icon>
            </x-global.summary-card>
        </div>
        <div class="col-sm-6 col-xl-3">
            <x-global.summary-card title="Total bruto setahun" :value="Format::rp($total['bruto'])" color="purple">
                <x-slot:icon><i class="ti ti-coins"></i></x-slot:icon>
            </x-global.summary-card>
        </div>
        <div class="col-sm-6 col-xl-3">
            <x-global.summary-card title="Total PPh 21 setahun" :value="Format::rp($total['pph21'])" color="orange">
                <x-slot:icon><i class="ti ti-receipt-tax"></i></x-slot:icon>
            </x-global.summary-card>
        </div>
        <div class="col-sm-6 col-xl-3">
            <x-global.summary-card title="Total take home pay" :value="Format::rp($total['thp'])" color="green">
                <x-slot:icon><i class="ti ti-wallet"></i></x-slot:icon>
            </x-global.summary-card>
        </div>

        {{-- Table --}}
        <div class="col-12">
            <div class="card">
                <div class="card-body p-2">
                    <div class="row g-2">
                        <div class="col-12 d-flex flex-wrap justify-content-between align-items-center gap-2">
                            <div class="d-flex flex-wrap align-items-center gap-2">
                                <form method="GET" action="{{ route('dashboard.index') }}" class="m-0">
                                    <label for="tahun" class="visually-hidden">Tahun pajak</label>
                                    <select id="tahun" name="tahun" class="form-select" style="width: auto" onchange="this.form.submit()">
                                        @foreach ($tahunAda as $t)
                                            <option value="{{ $t }}" @selected($t === $tahun)>Tahun pajak {{ $t }}</option>
                                        @endforeach
                                    </select>
                                </form>
                                <input type="text" id="rekapSearch" class="form-control rounded-3" autocomplete="off"
                                    placeholder="Cari nama / nomor induk…" aria-label="Cari pegawai" style="width: 240px" />
                                <x-global.btn-detail label="" color="red" size="sm" outline="true" id="toggleResetButton"
                                    data-bs-toggle="tooltip" data-bs-title="Reset">
                                    <x-slot:icon><i class="ti ti-restore"></i></x-slot:icon>
                                </x-global.btn-detail>
                            </div>
                            @if ($jumlah)
                                <div class="d-flex align-items-center gap-2">
                                    <x-global.btn-detail label="Unduh CSV" color="green" size="sm" outline="true" href="{{ route('dashboard.ekspor', ['tahun' => $tahun]) }}">
                                        <x-slot:icon><i class="ti ti-file-spreadsheet"></i></x-slot:icon>
                                    </x-global.btn-detail>
                                    <form method="POST" action="{{ route('dashboard.hitung') }}" class="m-0" data-proses="Menghitung {{ $jumlah }} pegawai…">
                                        @csrf
                                        <input type="hidden" name="tahun" value="{{ $tahun }}">
                                        <x-global.btn-detail label="Hitung semua ({{ $jumlah }})" color="blue" size="sm" type="submit">
                                            <x-slot:icon><i class="ti ti-calculator"></i></x-slot:icon>
                                        </x-global.btn-detail>
                                    </form>
                                </div>
                            @endif
                        </div>

                        <div class="col-12">
                            <div class="card overflow-hidden mdka-border-gray-200">
                                <div class="card-body table-responsive p-0">
                                    <table class="table table-vcenter mdka-border-gray-100 text-nowrap mb-0" id="rekapTable">
                                        <thead>
                                            <tr class="mdka-bg-gray-50">
                                                <th scope="col" width="30" class="fs-5 py-3 text-center">No</th>
                                                <th scope="col" class="fs-5 py-3">Pegawai</th>
                                                <th scope="col" class="fs-5 py-3">PTKP</th>
                                                <th scope="col" class="fs-5 py-3">Metode</th>
                                                <th scope="col" class="fs-5 py-3 text-end">Bruto setahun</th>
                                                <th scope="col" class="fs-5 py-3 text-end">PPh 21 setahun</th>
                                                <th scope="col" class="fs-5 py-3 text-end">Take home pay</th>
                                                <th scope="col" class="fs-5 py-3">Cek silang</th>
                                                <th scope="col" class="fs-5 py-3">Status</th>
                                                <th scope="col" class="fs-5 py-3 text-center">Aksi</th>
                                            </tr>
                                        </thead>
                                        <tbody></tbody>
                                    </table>
                                </div>
                            </div>
                            <div class="pagination-container mt-2"></div>
                        </div>
                        <div class="col-12">
                            <p class="text-muted small mb-0 px-1">
                                <i class="ti ti-arrows-exchange me-1"></i>Cek silang membandingkan setiap hasil dengan kalkulator independen tanpa
                                knowledge base (eksperimen E12). <strong>Hitung semua</strong> mengirim seluruh pegawai tahun ini ke engine dalam satu panggilan.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
@endsection

@push('javascript')
    <script>
        const urlRekapList = @json(route('dashboard.list'));
        const tahunPajak = @json($tahun);
        const labelCekSilang = {
            identik: ['green', 'identik'],
            sah_titik_tetap_ganda: ['blue', 'beda, keduanya sah'],
            berbeda: ['red', 'BERBEDA'],
            galat: ['gray', 'tidak dapat dicek'],
            dilewati: ['gray', 'dilewati (KB tambahan)']
        };

        let currentPage = 1;
        let limit = 10;
        let search = '';

        const columns = [
            'index',
            {
                key: 'nama',
                render: item => `<a href="${item.url}" class="fw-medium">${escapeHtml(item.nama)}</a>
                    <div class="text-muted small">${escapeHtml(item.nomor_induk)}</div>`
            },
            'status_ptkp',
            {
                key: 'metode',
                className: 'text-muted',
                render: item => escapeHtml(item.metode.replaceAll('_', ' '))
            },
            {
                key: 'bruto_setahun',
                className: 'angka',
                render: item => item.bruto_setahun === null ? '' : formatRupiah(item.bruto_setahun)
            },
            {
                key: 'pph21_setahun',
                className: 'angka fw-bold',
                render: item => item.pph21_setahun === null ? '' : formatRupiah(item.pph21_setahun)
            },
            {
                key: 'thp_setahun',
                className: 'angka',
                render: item => item.thp_setahun === null ? '' : formatRupiah(item.thp_setahun)
            },
            {
                key: 'cek_silang',
                render: item => {
                    const c = labelCekSilang[item.cek_silang];
                    return c ? `<span class="status status-${c[0]}">${c[1]}</span>` : '';
                }
            },
            {
                key: 'status',
                render: item => ({
                    belum: '<span class="status status-gray">belum dihitung</span>',
                    kedaluwarsa: '<span class="status status-yellow">data / aturan berubah, hitung ulang</span>',
                    galat: `<span class="status status-red">galat</span><div class="mdka-text-red-600 small text-wrap" style="max-width: 260px">${escapeHtml(item.pesan)}</div>`,
                    berhasil: `<span class="text-muted">${escapeHtml(item.dihitung)}</span>`,
                })[item.status]
            },
            {
                key: 'aksi',
                className: 'text-center',
                render: item => `
                    <x-global.btn-detail label="" color="blue" size="sm" href="${item.url}" data-bs-toggle="tooltip" data-bs-title="Lihat hasil">
                        <x-slot:icon><i class="ti ti-eye"></i></x-slot:icon>
                    </x-global.btn-detail>`
            }
        ];

        function rekapTable() {
            renderTableWithFeatures({
                container: '#rekapTable',
                columns,
                currentPage,
                limit,
                loading: true
            });
            $.ajax({
                url: urlRekapList,
                data: {
                    tahun: tahunPajak,
                    page: currentPage,
                    paginated: limit,
                    search
                },
                dataType: 'json',
                success: response => {
                    renderTableWithFeatures({
                        container: '#rekapTable',
                        data: response.data,
                        columns,
                        currentPage,
                        limit,
                        meta: response.meta,
                        emptyText: search ? 'Tidak ada pegawai yang cocok.' : `Belum ada data HR untuk tahun ${tahunPajak}. Isi lewat menu Pegawai.`,
                        onPageChange: page => {
                            currentPage = page;
                            rekapTable();
                        },
                        onLimitChange: newLimit => {
                            limit = newLimit;
                            currentPage = 1;
                            rekapTable();
                        },
                    });
                    $('#rekapTable [data-bs-toggle="tooltip"]').tooltip({
                        trigger: 'hover'
                    });
                },
                error: () => renderTableWithFeatures({
                    container: '#rekapTable',
                    columns,
                    currentPage,
                    limit,
                    emptyText: 'Gagal memuat data. Silakan coba lagi.'
                })
            });
        }

        $(function() {
            rekapTable();
            $('#rekapSearch').on('input', debounce(function() {
                search = $(this).val();
                currentPage = 1;
                rekapTable();
            }));
            $('#toggleResetButton').on('click', () => {
                search = '';
                currentPage = 1;
                limit = 10;
                $('#rekapSearch').val('');
                rekapTable();
            });
        });
    </script>
@endpush
