@extends('main.index')
@use('App\Helpers\Format')
@use('Modules\Payroll\Services\Label')
@use('Modules\Payroll\Http\Controllers\PayrollController')

@section('page-title', "Payroll {$payroll->tahun}")

@section('content')
    <div class="row g-2">
        {{-- Identitas & aksi --}}
        <div class="col-12">
            <div class="card">
                <div class="card-body p-3 d-flex flex-wrap justify-content-between align-items-center gap-3">
                    <div class="d-flex align-items-center gap-3">
                        <span class="avatar avatar-md rounded-3 mdka-bg-blue-100 mdka-text-blue-600"><i class="ti ti-user fs-2"></i></span>
                        <div>
                            <div class="text-muted small">{{ $payroll->pegawai->nomor_induk }}</div>
                            <h3 class="mb-1">{{ $payroll->pegawai->nama }}</h3>
                            <div class="d-flex flex-wrap gap-1">
                                <span class="badge mdka-bg-gray-100 mdka-text-gray-700">Tahun {{ $payroll->tahun }}</span>
                                <span class="badge mdka-bg-gray-100 mdka-text-gray-700">PTKP {{ $payroll->status_ptkp }}</span>
                                <span class="badge mdka-bg-gray-100 mdka-text-gray-700">{{ Label::METODE[$payroll->metode] ?? $payroll->metode }}</span>
                                <span class="badge mdka-bg-gray-100 mdka-text-gray-700">Gaji pokok {{ Format::rp($payroll->gaji_pokok) }}</span>
                            </div>
                        </div>
                    </div>
                    <div class="d-flex flex-wrap gap-2">
                        <form method="POST" action="{{ route('payroll.hitung', $payroll) }}" data-proses="Menghitung…">
                            @csrf
                            <x-global.btn-detail :label="$terakhir ? 'Hitung ulang' : 'Hitung'" color="blue" type="submit">
                                <x-slot:icon><i class="ti ti-calculator"></i></x-slot:icon>
                            </x-global.btn-detail>
                        </form>
                        <x-global.btn-detail label="Ubah data HR" color="orange" outline="true" href="{{ route('payroll.edit', $payroll) }}">
                            <x-slot:icon><i class="ti ti-edit"></i></x-slot:icon>
                        </x-global.btn-detail>
                        @if ($tampil)
                            <x-global.btn-detail label="Unduh CSV" color="green" outline="true" href="{{ route('payroll.ekspor', $payroll) }}">
                                <x-slot:icon><i class="ti ti-file-spreadsheet"></i></x-slot:icon>
                            </x-global.btn-detail>
                        @endif
                        <form method="POST" action="{{ route('payroll.destroy', $payroll) }}" data-konfirmasi="Hapus data HR {{ $payroll->tahun }}?"
                            data-konfirmasi-teks="Riwayat perhitungannya ikut terhapus." data-konfirmasi-ikon="warning" data-konfirmasi-tombol="Hapus">
                            @csrf
                            @method('DELETE')
                            <x-global.btn-detail label="" color="red" outline="true" type="submit" data-bs-toggle="tooltip" data-bs-title="Hapus data HR">
                                <x-slot:icon><i class="ti ti-trash"></i></x-slot:icon>
                            </x-global.btn-detail>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        {{-- Status --}}
        @if (! $terakhir)
            <div class="col-12">
                <div class="card">
                    <div class="empty py-5">
                        <div class="empty-icon"><i class="ti ti-calculator fs-1 mdka-text-blue-500"></i></div>
                        <p class="empty-title">Belum dihitung</p>
                        <p class="empty-subtitle text-muted">Tekan <strong>Hitung</strong> untuk mengirim data HR ke engine knowledge base.</p>
                    </div>
                </div>
            </div>
        @else
            @if ($kedaluwarsa === 'data')
                <div class="col-12">
                    <div class="alert alert-warning mb-0" role="status">
                        <div class="d-flex gap-2"><i class="ti ti-refresh-alert fs-2"></i>
                            <div><strong>Data HR berubah sejak perhitungan terakhir.</strong> Angka di bawah masih memakai data lama; tekan <strong>Hitung ulang</strong>.</div>
                        </div>
                    </div>
                </div>
            @elseif ($kedaluwarsa === 'kb')
                <div class="col-12">
                    <div class="alert alert-warning mb-0" role="status">
                        <div class="d-flex gap-2"><i class="ti ti-books fs-2"></i>
                            <div><strong>Aturan knowledge base berubah sejak perhitungan terakhir</strong> (berkas KB tambahan diterapkan atau dinonaktifkan di
                                <a href="{{ route('kb.index') }}">Basis pengetahuan</a>). Periksa isian tambahan di <a href="{{ route('payroll.edit', $payroll) }}">Ubah data HR</a>,
                                lalu tekan <strong>Hitung ulang</strong>.</div>
                        </div>
                    </div>
                </div>
            @endif
            @if (! $terakhir->berhasil)
                <div class="col-12">
                    <div class="alert alert-danger mb-0" role="alert">
                        <div class="d-flex gap-2"><i class="ti ti-alert-triangle fs-2"></i>
                            <div><strong>Perhitungan terakhir gagal</strong> ({{ $terakhir->jenis_galat }}): {{ $terakhir->pesan }}</div>
                        </div>
                    </div>
                </div>
            @endif
        @endif

        @if ($tampil)
            <div class="col-12">
                @include('Payroll::partials.cek_silang', ['p' => $terakhir])
            </div>

            {{-- Ringkasan --}}
            @php($ikon = ['PPh 21 setahun' => ['receipt-tax', 'blue'], 'Take home pay setahun' => ['wallet', 'green'], 'Penghasilan bruto' => ['coins', 'purple'], 'Tarif efektif' => ['percentage', 'orange'], 'Ditanggung pemerintah (DTP)' => ['building-bank', 'yellow']])
            @foreach ($tampil->ringkasan() as [$lbl, $v, $bantu])
                <div class="col-sm-6 {{ count($tampil->ringkasan()) > 4 ? 'col-xl' : 'col-xl-3' }}">
                    <x-global.summary-card :title="$lbl" :value="$v" :color="$ikon[$lbl][1] ?? 'gray'" :keterangan="$bantu">
                        <x-slot:icon><i class="ti ti-{{ $ikon[$lbl][0] ?? 'info-circle' }}"></i></x-slot:icon>
                    </x-global.summary-card>
                </div>
            @endforeach

            @foreach ($tampil->peringatan() as $p)
                <div class="col-12">
                    <div class="alert {{ $p['jenis'] === 'warning' ? 'alert-warning' : 'alert-info' }} mb-0">
                        <div class="d-flex gap-2">
                            <i class="ti {{ $p['jenis'] === 'warning' ? 'ti-gavel' : 'ti-info-circle' }} fs-2"></i>
                            <div><strong>{{ $p['judul'] }}.</strong> {{ $p['teks'] }}</div>
                        </div>
                    </div>
                </div>
            @endforeach

            {{-- Tab hasil --}}
            <div class="col-12">
                <div class="card">
                    <div class="card-body p-2">
                        <ul class="mdka-nav-btn mb-3" aria-label="Bagian hasil">
                            @foreach (PayrollController::TAB as $k => $lbl)
                                <li class="mdka-nav-btn-item">
                                    <a href="{{ route('payroll.show', [$payroll, 'tab' => $k, 'bulan' => $bulanSlip]) }}"
                                        class="mdka-nav-btn-link {{ $tab === $k ? 'active' : '' }}" @if ($tab === $k) aria-current="page" @endif>{{ $lbl }}</a>
                                </li>
                            @endforeach
                        </ul>
                        @include("Payroll::partials.tab_{$tab}")
                    </div>
                </div>
            </div>

            <div class="col-12 d-flex flex-wrap justify-content-between gap-2 text-muted small px-1">
                <span><i class="ti ti-clock me-1"></i>Dihitung {{ $terakhir->created_at->format('d/m/Y H:i') }} oleh {{ $terakhir->user?->name ?? 'sistem' }}</span>
                <span><i class="ti ti-git-commit me-1"></i>Engine {{ $terakhir->versi_engine }} · KB <code title="{{ $terakhir->versi_kb }}">{{ $terakhir->versiKbRingkas() }}</code>
                    ({{ $tampil->h['audit']['tanggal_kebaruan_kb'] ?? '-' }})@if ($terakhir->sidik_kb) + berkas KB tambahan <code>{{ $terakhir->sidik_kb }}</code>@endif</span>
            </div>
        @endif

        {{-- Riwayat --}}
        @if ($riwayat->count() > 1)
            <div class="col-12">
                <div class="card">
                    <div class="card-header p-3">
                        <a class="card-title mb-0 text-reset text-decoration-none d-flex align-items-center gap-2" data-bs-toggle="collapse" href="#riwayatPerhitungan"
                            role="button" aria-expanded="false" aria-controls="riwayatPerhitungan">
                            <i class="ti ti-history"></i> Riwayat perhitungan ({{ $riwayat->count() }}) <i class="ti ti-chevron-down"></i>
                        </a>
                    </div>
                    <div class="collapse" id="riwayatPerhitungan">
                        <div class="card-body table-responsive p-0">
                            <table class="table table-vcenter mb-0 text-nowrap">
                                <thead>
                                    <tr class="mdka-bg-gray-50">
                                        <th class="py-3">Waktu</th><th class="py-3">Oleh</th><th class="py-3">Status</th>
                                        <th class="py-3 text-end">PPh 21 setahun</th><th class="py-3 text-end">Take home pay</th>
                                        <th class="py-3">Cek silang</th><th class="py-3">Versi KB</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    @foreach ($riwayat as $r)
                                        <tr>
                                            <td>{{ $r->created_at->format('d/m/Y H:i:s') }}</td>
                                            <td>{{ $r->user?->name ?? 'sistem' }}</td>
                                            <td>
                                                @if ($r->berhasil)
                                                    <span class="status status-green">berhasil</span>
                                                @else
                                                    <span class="status status-red" title="{{ $r->pesan }}">galat</span>
                                                @endif
                                            </td>
                                            <td class="angka">{{ $r->berhasil ? Format::rp($r->pph21_setahun, false) : '' }}</td>
                                            <td class="angka">{{ $r->berhasil ? Format::rp($r->thp_setahun, false) : '' }}</td>
                                            <td><x-global.cek-silang :status="$r->cek_silang" /></td>
                                            <td><code title="{{ $r->versi_kb }}">{{ $r->versiKbRingkas() }}</code>@if ($r->sidik_kb) <span class="text-muted">+ <code>{{ $r->sidik_kb }}</code></span>@endif</td>
                                        </tr>
                                    @endforeach
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        @endif
    </div>
@endsection
