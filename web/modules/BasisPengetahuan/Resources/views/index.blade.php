@extends('main.index')
@use('App\Models\Kb\UsulanKb')

@section('page-title', 'Basis pengetahuan')

@section('content')
    <div class="row g-2">
        <div class="col-12">
            <div class="alert alert-info mb-0">
                <div class="d-flex gap-2"><i class="ti ti-books fs-2"></i>
                    <div>
                        <strong>Aturan baru masuk sebagai berkas knowledge base, bukan perubahan rumus di kode.</strong>
                        Unggah PDF peraturan, LLM menyusun <em>rancangan</em> berkas KB, engine memvalidasi dan menyimulasikannya pada pegawai contoh,
                        lalu Anda meninjau dan menerapkannya. Bila aturan baru membutuhkan isian baru, isian itu muncul otomatis di form data HR.
                        LLM tidak pernah menghitung pajak dan rancangannya tidak berlaku sebelum Anda setujui.
                    </div>
                </div>
            </div>
        </div>

        @unless ($llmSiap)
            <div class="col-12">
                <div class="alert alert-warning mb-0" role="status">
                    <div class="d-flex gap-2"><i class="ti ti-key-off fs-2"></i>
                        <div><strong>Kunci API LLM belum diatur.</strong> Isi <code>ANTHROPIC_API_KEY</code> di <code>web/.env</code> agar dokumen dapat dibaca.
                            Berkas KB yang sudah diterapkan tetap berlaku.</div>
                    </div>
                </div>
            </div>
        @endunless

        {{-- Unggah --}}
        <div class="col-lg-5">
            <div class="card h-100">
                <div class="card-header p-3">
                    <h4 class="card-title mb-0"><i class="ti ti-file-upload me-2 mdka-text-blue-500"></i>Unggah peraturan</h4>
                </div>
                <div class="card-body p-3">
                    @if ($errors->any())
                        <div class="alert alert-danger" role="alert">
                            <ul class="mb-0 ps-3">
                                @foreach ($errors->all() as $e)
                                    <li>{{ $e }}</li>
                                @endforeach
                            </ul>
                        </div>
                    @endif
                    <form method="POST" action="{{ route('kb.store') }}" enctype="multipart/form-data" class="row g-3" data-proses="Mengunggah…">
                        @csrf
                        <div class="col-12">
                            <label for="judul" class="form-label required">Judul dokumen</label>
                            <input id="judul" name="judul" value="{{ old('judul') }}" required maxlength="150" autocomplete="off"
                                placeholder="mis. Peraturan Perusahaan 2026 tentang uang transport…" class="form-control @error('judul') is-invalid @enderror">
                        </div>
                        <div class="col-md-6">
                            <label for="lapisan" class="form-label required">Jenis peraturan</label>
                            <select id="lapisan" name="lapisan" class="form-select @error('lapisan') is-invalid @enderror">
                                @foreach (UsulanKb::LAPISAN as $k => $v)
                                    <option value="{{ $k }}" @selected(old('lapisan', 'perusahaan') === $k)>{{ $v }}</option>
                                @endforeach
                            </select>
                            <small class="form-hint">Aturan pemerintah yang wajib mengalahkan kebijakan perusahaan.</small>
                        </div>
                        <div class="col-md-6">
                            <label for="pdf" class="form-label required">Berkas PDF</label>
                            <input id="pdf" name="pdf" type="file" accept="application/pdf,.pdf" required class="form-control @error('pdf') is-invalid @enderror">
                            <small class="form-hint">Paling besar 30 MB.</small>
                        </div>
                        <div class="col-12">
                            <label for="catatan" class="form-label">Catatan untuk LLM</label>
                            <textarea id="catatan" name="catatan" rows="3" maxlength="2000" class="form-control @error('catatan') is-invalid @enderror"
                                placeholder="Opsional: pasal yang relevan, tanggal berlaku, atau hal yang perlu diperhatikan…">{{ old('catatan') }}</textarea>
                        </div>
                        <div class="col-12 d-flex justify-content-end">
                            <x-global.btn-detail label="Unggah & baca dengan LLM" color="blue" type="submit">
                                <x-slot:icon><i class="ti ti-sparkles"></i></x-slot:icon>
                            </x-global.btn-detail>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        {{-- KB aktif --}}
        <div class="col-lg-7">
            <div class="card h-100">
                <div class="card-header p-3 d-flex justify-content-between align-items-center">
                    <h4 class="card-title mb-0"><i class="ti ti-database me-2 mdka-text-green-600"></i>Berkas KB tambahan yang aktif</h4>
                    @if ($sidik !== '')
                        <span class="text-muted small">sidik <code>{{ $sidik }}</code></span>
                    @endif
                </div>
                @if ($aktif->isEmpty())
                    <div class="empty py-4">
                        <div class="empty-icon"><i class="ti ti-database-off fs-1 text-muted"></i></div>
                        <p class="empty-title">Belum ada berkas tambahan</p>
                        <p class="empty-subtitle text-muted mb-0">Engine memakai KB bawaan: regulasi PPh 21 dan kebijakan {{ config('payroll.nama_perusahaan') }}.</p>
                    </div>
                @else
                    <div class="card-body table-responsive p-0">
                        <table class="table table-vcenter mb-0">
                            <thead>
                                <tr class="mdka-bg-gray-50">
                                    <th class="py-3">Dokumen</th>
                                    <th class="py-3">Isi</th>
                                    <th class="py-3">Diterapkan</th>
                                </tr>
                            </thead>
                            <tbody>
                                @foreach ($aktif as $a)
                                    <tr>
                                        <td>
                                            <a href="{{ route('kb.show', $a) }}" class="fw-medium">{{ $a->judul }}</a>
                                            <div class="text-muted small font-monospace">kb/tambahan/{{ $a->nama_berkas }}</div>
                                        </td>
                                        <td class="text-nowrap">
                                            <span class="badge mdka-bg-gray-100 mdka-text-gray-700">{{ $a->validasi['ringkasan']['aturan'] ?? 0 }} aturan</span>
                                            @if (count($a->validasi['masukan'] ?? []))
                                                <span class="badge mdka-bg-purple-100 mdka-text-purple-600">{{ count($a->validasi['masukan']) }} isian baru</span>
                                            @endif
                                            @if ($a->validasi['ringkasan']['parameter'] ?? 0)
                                                <span class="badge mdka-bg-orange-100 mdka-text-orange-600">{{ $a->validasi['ringkasan']['parameter'] }} parameter</span>
                                            @endif
                                        </td>
                                        <td class="text-nowrap text-muted small">{{ $a->diterapkan_pada?->format('d/m/Y H:i') }}<br>{{ $a->penerap?->name ?? '-' }}</td>
                                    </tr>
                                @endforeach
                            </tbody>
                        </table>
                    </div>
                @endif
            </div>
        </div>

        {{-- Daftar usulan --}}
        <div class="col-12">
            <div class="card">
                <div class="card-body p-2">
                    <div class="row g-2">
                        <div class="col-12 d-flex flex-wrap gap-2">
                            <input type="text" id="kbSearch" class="form-control rounded-3" autocomplete="off" placeholder="Cari judul / nama PDF…"
                                aria-label="Cari usulan" style="max-width: 280px">
                            <select id="kbStatus" class="form-select" aria-label="Status" style="max-width: 220px">
                                <option value="">Semua status</option>
                                @foreach (UsulanKb::STATUS as $k => [$label])
                                    <option value="{{ $k }}">{{ ucfirst($label) }}</option>
                                @endforeach
                            </select>
                        </div>
                        <div class="col-12">
                            <div class="card overflow-hidden mdka-border-gray-200">
                                <div class="card-body table-responsive p-0">
                                    <table class="table table-vcenter mdka-border-gray-100 text-nowrap mb-0" id="kbTable">
                                        <thead>
                                            <tr class="mdka-bg-gray-50">
                                                <th scope="col" width="30" class="fs-5 py-3 text-center">No</th>
                                                <th scope="col" class="fs-5 py-3">Dokumen</th>
                                                <th scope="col" class="fs-5 py-3">Jenis</th>
                                                <th scope="col" class="fs-5 py-3">Status</th>
                                                <th scope="col" class="fs-5 py-3">Rancangan</th>
                                                <th scope="col" class="fs-5 py-3">Diunggah</th>
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
@endsection

@push('javascript')
    <script>
        const urlKbList = @json(route('kb.list'));
        let currentPage = 1;
        let limit = 10;
        let search = '';
        let status = '';
        let timerSegarkan = null;

        const columns = [
            'index',
            {
                key: 'judul',
                render: item => `<a href="${item.url}" class="fw-medium">${escapeHtml(item.judul)}</a>
                    <div class="text-muted small">${escapeHtml(item.nama_pdf)}</div>`
            },
            'lapisan',
            {
                key: 'status',
                render: item => `<span class="status status-${item.warna}">${escapeHtml(item.status)}</span>`
            },
            {
                key: 'rancangan',
                render: item => item.aturan === null ? '<span class="text-muted">-</span>' :
                    `${item.aturan} aturan${item.masukan ? ` · ${item.masukan} isian baru` : ''} ` +
                    (item.valid ? '<span class="status status-green">lolos validasi</span>' : '<span class="status status-red">belum lolos</span>')
            },
            {
                key: 'dibuat',
                render: item => `${escapeHtml(item.dibuat)}<div class="text-muted small">${escapeHtml(item.oleh)}</div>`
            },
            {
                key: 'actions',
                className: 'text-center',
                render: item => `
                    <x-global.btn-detail label="" color="blue" size="sm" href="${item.url}" data-bs-toggle="tooltip" data-bs-title="Tinjau">
                        <x-slot:icon><i class="ti ti-eye"></i></x-slot:icon>
                    </x-global.btn-detail>`
            }
        ];

        function kbTable(diam = false) {
            if (!diam) {
                renderTableWithFeatures({
                    container: '#kbTable',
                    columns,
                    currentPage,
                    limit,
                    loading: true
                });
            }
            $.ajax({
                url: urlKbList,
                type: 'GET',
                data: {
                    page: currentPage,
                    paginated: limit,
                    search,
                    status
                },
                dataType: 'json',
                success: response => {
                    renderTableWithFeatures({
                        container: '#kbTable',
                        data: response.data,
                        columns,
                        currentPage,
                        limit,
                        meta: response.meta,
                        emptyText: search || status ? 'Tidak ada usulan yang cocok.' : 'Belum ada dokumen yang diunggah.',
                        onPageChange: page => {
                            currentPage = page;
                            kbTable();
                        },
                        onLimitChange: newLimit => {
                            limit = newLimit;
                            currentPage = 1;
                            kbTable();
                        }
                    });
                    $('#kbTable [data-bs-toggle="tooltip"]').tooltip({
                        trigger: 'hover'
                    });
                    // selama ada dokumen yang masih dibaca LLM, segarkan tabel diam-diam
                    clearTimeout(timerSegarkan);
                    if (response.data.some(item => item.diproses)) {
                        timerSegarkan = setTimeout(() => kbTable(true), 6000);
                    }
                },
                error: () => renderTableWithFeatures({
                    container: '#kbTable',
                    columns,
                    currentPage,
                    limit,
                    emptyText: 'Gagal memuat data. Silakan coba lagi.'
                })
            });
        }

        $(function() {
            kbTable();
            $('#kbSearch').on('input', debounce(function() {
                search = $(this).val();
                currentPage = 1;
                kbTable();
            }));
            $('#kbStatus').on('change', function() {
                status = $(this).val();
                currentPage = 1;
                kbTable();
            });
        });
    </script>
@endpush
