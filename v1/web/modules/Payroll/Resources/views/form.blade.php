@extends('main.index')
@use('App\Helpers\Format')
@use('Modules\Payroll\Services\Label')

@php
    $nilai = fn (string $f) => old($f, $payroll->{$f} instanceof \Carbon\CarbonInterface ? $payroll->{$f}->toDateString() : $payroll->{$f});
@endphp

@section('page-title', $payroll->exists ? "Ubah data HR {$payroll->tahun}" : 'Tambah data HR')

@section('content')
    <div class="row g-2">
        <div class="col-12">
            <div class="card">
                <div class="card-body p-3 d-flex flex-wrap justify-content-between align-items-center gap-2">
                    <div>
                        <div class="text-muted small">{{ $pegawai->nomor_induk }}</div>
                        <h3 class="mb-0">{{ $pegawai->nama }}</h3>
                    </div>
                    @if (! $payroll->exists && $tahunOpsi !== [])
                        <form method="GET" action="{{ route('payroll.create', $pegawai) }}" class="d-flex align-items-center gap-2">
                            <label for="pilih_tahun" class="form-label mb-0 text-nowrap">Tahun pajak</label>
                            <select id="pilih_tahun" name="tahun" class="form-select" onchange="this.form.submit()">
                                @foreach ($tahunOpsi as $t)
                                    <option value="{{ $t }}" @selected($t === $payroll->tahun)>{{ $t }}</option>
                                @endforeach
                            </select>
                        </form>
                    @endif
                </div>
            </div>
        </div>

        @if (! $payroll->exists && $tahunOpsi === [])
            <div class="col-12">
                <div class="alert alert-info mb-0">
                    Semua tahun pajak {{ config('payroll.tahun_min') }}–{{ config('payroll.tahun_max') }} dalam masa kerja pegawai ini sudah punya data HR.
                </div>
            </div>
        @else
            @if ($errors->any())
                <div class="col-12">
                    <div class="alert alert-danger mb-0" role="alert">
                        <div class="d-flex gap-2">
                            <i class="ti ti-alert-circle fs-2"></i>
                            <div>
                                <h4 class="alert-title">Periksa kembali isian</h4>
                                <ul class="mb-0 ps-3">
                                    @foreach ($errors->all() as $e)
                                        <li>{{ $e }}</li>
                                    @endforeach
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            @endif

            <div class="col-12">
                <form method="POST" action="{{ $payroll->exists ? route('payroll.update', $payroll) : route('payroll.store', $pegawai) }}" class="row g-2">
                    @csrf
                    @if ($payroll->exists)
                        @method('PUT')
                    @else
                        <input type="hidden" name="tahun" value="{{ $payroll->tahun }}">
                    @endif

                    <div class="col-12">
                        <div class="card">
                            <div class="card-header p-3">
                                <h4 class="card-title mb-0"><i class="ti ti-id-badge-2 me-2 mdka-text-blue-500"></i>Pegawai · tahun {{ $payroll->tahun }}</h4>
                            </div>
                            <div class="card-body p-3 row g-3">
                                <div class="col-md-3">
                                    <label for="status_ptkp" class="form-label required">Status PTKP</label>
                                    <select id="status_ptkp" name="status_ptkp" class="form-select">
                                        @foreach (Label::STATUS_PTKP as $s)
                                            <option value="{{ $s }}" @selected($nilai('status_ptkp') === $s)>{{ $s }}</option>
                                        @endforeach
                                    </select>
                                    <small class="form-hint">Status per 1 Januari tahun pajak.</small>
                                </div>
                                <div class="col-md-5">
                                    <label for="metode" class="form-label required">Metode pajak</label>
                                    <select id="metode" name="metode" class="form-select">
                                        @foreach (Label::METODE as $k => $v)
                                            <option value="{{ $k }}" @selected($nilai('metode') === $k)>{{ $v }}</option>
                                        @endforeach
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-12">
                        <div class="card">
                            <div class="card-header p-3">
                                <h4 class="card-title mb-0"><i class="ti ti-cash me-2 mdka-text-green-600"></i>Gaji &amp; tunjangan</h4>
                            </div>
                            <div class="card-body p-3 row g-3">
                                @include('Payroll::partials.angka', ['f' => 'gaji_pokok', 'lbl' => 'Gaji pokok sebulan (Rp)', 'wajib' => true])
                                @include('Payroll::partials.angka', ['f' => 'kenaikan_nominal', 'lbl' => 'Kenaikan gaji (Rp)'])
                                <div class="col-md-3">
                                    <label for="kenaikan_tanggal" class="form-label required">Kenaikan berlaku mulai</label>
                                    <input id="kenaikan_tanggal" name="kenaikan_tanggal" type="date" value="{{ $nilai('kenaikan_tanggal') }}" required
                                        class="form-control @error('kenaikan_tanggal') is-invalid @enderror">
                                    <small class="form-hint">1 Januari = tanpa kenaikan di tengah tahun.</small>
                                </div>
                                <div class="col-12">
                                    <div class="hr-text hr-text-left my-1">Bila kenaikan berlaku di tengah bulan (tanggal &gt; 1), pecah hari bulan itu</div>
                                </div>
                                @include('Payroll::partials.angka', ['f' => 'kenaikan_hk_sebelum', 'lbl' => 'Hadir sebelum naik', 'bantu' => 'Untuk gaji & tunjangan prorata'])
                                @include('Payroll::partials.angka', ['f' => 'kenaikan_hk_sesudah', 'lbl' => 'Hadir sesudah naik'])
                                @include('Payroll::partials.angka', ['f' => 'kenaikan_hari_sebelum', 'lbl' => 'Hari kerja sebelum naik', 'bantu' => 'Untuk tunjangan tetap'])
                                @include('Payroll::partials.angka', ['f' => 'kenaikan_hari_sesudah', 'lbl' => 'Hari kerja sesudah naik'])
                                <div class="col-12">
                                    <div class="hr-text hr-text-left my-1">Tunjangan sebelum / sesudah kenaikan — tetap dibayar penuh, prorata mengikuti kehadiran</div>
                                </div>
                                @include('Payroll::partials.angka', ['f' => 'tunjangan_tetap_lama', 'lbl' => 'Tetap (lama)'])
                                @include('Payroll::partials.angka', ['f' => 'tunjangan_prorata_lama', 'lbl' => 'Prorata (lama)'])
                                @include('Payroll::partials.angka', ['f' => 'tunjangan_tetap_baru', 'lbl' => 'Tetap (baru)'])
                                @include('Payroll::partials.angka', ['f' => 'tunjangan_prorata_baru', 'lbl' => 'Prorata (baru)'])
                            </div>
                        </div>
                    </div>

                    <div class="col-12">
                        <div class="card">
                            <div class="card-header p-3">
                                <h4 class="card-title mb-0"><i class="ti ti-gift me-2 mdka-text-orange-600"></i>THR &amp; BPJS</h4>
                            </div>
                            <div class="card-body p-3 row g-3">
                                <div class="col-md-3">
                                    <label for="tanggal_lebaran" class="form-label required">Hari Raya (Idul Fitri)</label>
                                    <input id="tanggal_lebaran" name="tanggal_lebaran" type="date" value="{{ $nilai('tanggal_lebaran') }}" required
                                        class="form-control @error('tanggal_lebaran') is-invalid @enderror">
                                </div>
                                <div class="col-md-3">
                                    <label for="tanggal_thr_bayar" class="form-label required">THR dibayarkan</label>
                                    <input id="tanggal_thr_bayar" name="tanggal_thr_bayar" type="date" value="{{ $nilai('tanggal_thr_bayar') }}" required
                                        class="form-control @error('tanggal_thr_bayar') is-invalid @enderror">
                                </div>
                                @include('Payroll::partials.angka', ['f' => 'bpjs_tk_mulai_bulan', 'lbl' => 'BPJS TK sejak bulan', 'min' => 1, 'max' => 12, 'kolom' => 'col-md-2'])
                                @include('Payroll::partials.angka', ['f' => 'bpjs_kes_mulai_bulan', 'lbl' => 'BPJS Kes sejak bulan', 'min' => 1, 'max' => 12, 'kolom' => 'col-md-2'])
                                <div class="col-md-2">
                                    <label for="kelas_jkk_persen" class="form-label required">Tarif JKK (%)</label>
                                    <input id="kelas_jkk_persen" name="kelas_jkk_persen" value="{{ $nilai('kelas_jkk_persen') }}" required inputmode="decimal"
                                        placeholder="0,24" class="form-control @error('kelas_jkk_persen') is-invalid @enderror">
                                    <small class="form-hint">Kelas risiko BPJS TK.</small>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-12">
                        <div class="card">
                            <div class="card-header p-3 d-block">
                                <h4 class="card-title mb-1"><i class="ti ti-calendar me-2 mdka-text-purple-600"></i>Kehadiran &amp; penghasilan variabel per bulan</h4>
                                <div class="text-muted small">
                                    @if ($rentang)
                                        Masa kerja tahun ini: <strong>{{ Format::bulan($rentang[0], true) }}–{{ Format::bulan($rentang[1], true) }}</strong>; bulan di luar masa kerja diabaikan.
                                    @else
                                        Pegawai tidak bekerja di tahun ini.
                                    @endif
                                    Hari kerja awal = Senin–Jumat, sesuaikan dengan kalender libur. Kolom variabel kosong = tidak ada.
                                </div>
                            </div>
                            <div class="card-body table-responsive p-0">
                                <table class="table table-vcenter table-sm mb-0 text-nowrap">
                                    <thead>
                                        <tr class="mdka-bg-gray-50">
                                            <th class="py-2 ps-3">Bulan</th>
                                            <th class="py-2">Hari kerja</th>
                                            <th class="py-2">Hadir</th>
                                            <th class="py-2">Kompensasi (% gaji)</th>
                                            <th class="py-2">Insentif OTA (Rp)</th>
                                            <th class="py-2">Lembur (Rp)</th>
                                            <th class="py-2 pe-3">Komisi (Rp)</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        @foreach ($bulan as $b => $m)
                                            @php($dalam = $rentang && $b >= $rentang[0] && $b <= $rentang[1])
                                            <tr class="{{ $dalam ? '' : 'mdka-bg-gray-50 text-muted' }}">
                                                <td class="ps-3 fw-medium">{{ Format::bulan($b, true) }}</td>
                                                @foreach (['hk_penuh' => [1, 31, '90px'], 'hk_aktual' => [0, 31, '90px'], 'kompensasi_persen' => [null, null, '120px'],
                                                    'ota' => [0, null, '150px'], 'lembur' => [0, null, '150px'], 'komisi' => [0, null, '150px']] as $f => [$min, $max, $lebar])
                                                    @php($nama = "bulan.{$b}.{$f}")
                                                    <td class="{{ $f === 'komisi' ? 'pe-3' : '' }}">
                                                        <input name="bulan[{{ $b }}][{{ $f }}]" value="{{ old($nama, $m[$f]) }}" aria-label="{{ $f }} {{ Format::bulan($b, true) }}"
                                                            style="width: {{ $lebar }}"
                                                            @if ($f === 'kompensasi_persen') inputmode="decimal" @else type="number" step="1" min="{{ $min }}" @if ($max) max="{{ $max }}" @endif @endif
                                                            class="form-control form-control-sm tabular-nums @error($nama) is-invalid @enderror">
                                                    </td>
                                                @endforeach
                                            </tr>
                                        @endforeach
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>

                    @include('Payroll::partials.masukan_kb')

                    <div class="col-12 d-flex justify-content-end gap-2">
                        <x-global.btn-detail label="Batal" color="secondary" outline="true"
                            href="{{ $payroll->exists ? route('payroll.show', $payroll) : route('pegawai.detail', $pegawai) }}">
                            <x-slot:icon><i class="ti ti-x"></i></x-slot:icon>
                        </x-global.btn-detail>
                        <x-global.btn-detail label="Simpan" color="blue" type="submit">
                            <x-slot:icon><i class="ti ti-device-floppy"></i></x-slot:icon>
                        </x-global.btn-detail>
                    </div>
                </form>
            </div>
        @endif
    </div>
@endsection
