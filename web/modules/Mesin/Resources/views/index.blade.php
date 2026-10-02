@extends('main.index')

@section('page-title', 'Mesin perhitungan')

@section('content')
    <div class="row g-2">
        <div class="col-12">
            @if ($galat)
                <div class="alert alert-danger mb-0" role="alert">
                    <div class="d-flex gap-2"><i class="ti ti-plug-connected-x fs-2"></i>
                        <div><strong>Engine tidak dapat dipanggil.</strong>
                            <div class="text-wrap" style="white-space: pre-line">{{ $galat }}</div>
                        </div>
                    </div>
                </div>
            @else
                <div class="alert alert-success mb-0">
                    <div class="d-flex gap-2"><i class="ti ti-plug-connected fs-2"></i>
                        <div><strong>Engine siap.</strong> Aplikasi ini tidak menghitung pajak sendiri: setiap angka dihitung oleh engine knowledge base
                            (Python) di repositori induk lewat jembatan JSON. Aturan pajak dan kebijakan perusahaan berada di berkas KB, bukan di kode aplikasi.</div>
                    </div>
                </div>
            @endif
        </div>

        <div class="col-lg-5">
            <div class="card h-100">
                <div class="card-header p-3">
                    <h4 class="card-title mb-0"><i class="ti ti-settings me-2 mdka-text-gray-600"></i>Konfigurasi</h4>
                </div>
                <div class="card-body p-3">
                    <div class="datagrid" style="--tblr-datagrid-item-width: 100%">
                        @foreach ($konfigurasi as $k => $v)
                            <div class="datagrid-item">
                                <div class="datagrid-title">{{ $k }}</div>
                                <div class="datagrid-content font-monospace text-break" style="font-size: .7rem">{{ $v }}</div>
                            </div>
                        @endforeach
                    </div>
                    <p class="text-muted small mt-3 mb-0">Diatur di <code>web/.env</code>.</p>
                </div>
            </div>
        </div>

        @if ($info)
            <div class="col-lg-7">
                <div class="card h-100">
                    <div class="card-header p-3">
                        <h4 class="card-title mb-0"><i class="ti ti-database me-2 mdka-text-blue-500"></i>Versi knowledge base</h4>
                    </div>
                    <div class="card-body p-3">
                        <div class="datagrid mb-3">
                            <div class="datagrid-item">
                                <div class="datagrid-title">Engine</div>
                                <div class="datagrid-content">{{ $info['versi_engine'] }}</div>
                            </div>
                            <div class="datagrid-item">
                                <div class="datagrid-title">Kebaruan KB</div>
                                <div class="datagrid-content">{{ $info['tanggal_kebaruan_kb'] }}</div>
                            </div>
                            <div class="datagrid-item">
                                <div class="datagrid-title">Commit KB</div>
                                <div class="datagrid-content font-monospace" style="font-size: .7rem">{{ $info['versi_kb'] }}</div>
                            </div>
                        </div>
                        <div class="card overflow-hidden mdka-border-gray-200">
                            <div class="card-body table-responsive p-0">
                                <table class="table table-vcenter mb-0">
                                    <thead>
                                        <tr class="mdka-bg-gray-50">
                                            <th class="py-3">Tabel parameter</th>
                                            <th class="py-3">Verifikasi</th>
                                            <th class="py-3">SHA-256</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        @foreach ($info['hash_tabel'] as $tabel => $hash)
                                            @php($status = $info['status_verifikasi_tabel'][$tabel] ?? '-')
                                            <tr>
                                                <td class="fw-medium">{{ $tabel }}</td>
                                                <td><span class="status {{ $status === 'double_entry' ? 'status-green' : 'status-yellow' }}">{{ str_replace('_', ' ', $status) }}</span></td>
                                                <td class="font-monospace text-muted">{{ substr($hash, 0, 16) }}…</td>
                                            </tr>
                                        @endforeach
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <p class="text-muted small mt-2 mb-0">"double entry" = tabel diekstraksi dua kali dari PDF regulasi dan dicocokkan sel per sel.</p>
                    </div>
                </div>
            </div>
        @endif
    </div>
@endsection
