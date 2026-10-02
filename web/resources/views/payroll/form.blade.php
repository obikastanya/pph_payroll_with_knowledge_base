@extends('layouts.app', ['judul' => ($payroll->exists ? 'Ubah' : 'Tambah').' data HR '.$payroll->tahun])
@use('App\Support\Format')
@use('App\Payroll\Label')

@php
    $nilai = fn (string $f) => old($f, $payroll->{$f} instanceof \Carbon\CarbonInterface ? $payroll->{$f}->toDateString() : $payroll->{$f});
    $err = fn (string $f) => $errors->has($f) ? 'input-error' : '';
@endphp

@section('isi')
    <p class="text-sm text-slate-500">
        <a href="{{ route('pegawai.show', $pegawai) }}" class="hover:underline">{{ $pegawai->nama }}</a> / data HR
    </p>
    <h1 class="mb-5 text-2xl font-semibold">{{ $payroll->exists ? "Ubah data HR {$payroll->tahun}" : 'Tambah data HR tahun pajak' }}</h1>

    @if (! $payroll->exists && $tahunOpsi === [])
        <div class="card p-6 text-sm text-slate-600">
            Semua tahun pajak {{ config('payroll.tahun_min') }}–{{ config('payroll.tahun_max') }} dalam masa kerja pegawai ini sudah punya data HR.
        </div>
    @else
        @if (! $payroll->exists)
            <form method="GET" action="{{ route('payroll.create', $pegawai) }}" class="mb-4 flex items-center gap-2 text-sm">
                <label for="pilih_tahun" class="font-medium text-slate-700">Tahun pajak</label>
                <select id="pilih_tahun" name="tahun" class="input w-auto" onchange="this.form.submit()">
                    @foreach ($tahunOpsi as $t)
                        <option value="{{ $t }}" @selected($t === $payroll->tahun)>{{ $t }}</option>
                    @endforeach
                </select>
                <span class="text-slate-500">Isian awal dilanjutkan dari tahun terakhir pegawai ini; periksa sebelum menyimpan.</span>
            </form>
        @endif

        @if ($errors->any())
            <div class="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800" role="alert">
                <p class="font-medium">Periksa kembali isian:</p>
                <ul class="mt-1 list-disc pl-5">
                    @foreach ($errors->all() as $e)<li>{{ $e }}</li>@endforeach
                </ul>
            </div>
        @endif

        <form method="POST" action="{{ $payroll->exists ? route('payroll.update', $payroll) : route('payroll.store', $pegawai) }}" class="space-y-5">
            @csrf
            @if ($payroll->exists) @method('PUT') @else <input type="hidden" name="tahun" value="{{ $payroll->tahun }}"> @endif

            <section class="card p-5">
                <h2 class="mb-4 font-semibold">Pegawai · tahun {{ $payroll->tahun }}</h2>
                <div class="grid gap-4 sm:grid-cols-3">
                    <div>
                        <label for="status_ptkp" class="label">Status PTKP</label>
                        <select id="status_ptkp" name="status_ptkp" class="input">
                            @foreach (Label::STATUS_PTKP as $s)
                                <option value="{{ $s }}" @selected($nilai('status_ptkp') === $s)>{{ $s }}</option>
                            @endforeach
                        </select>
                        <p class="bantu">Status per 1 Januari tahun pajak.</p>
                    </div>
                    <div class="sm:col-span-2">
                        <label for="metode" class="label">Metode pajak</label>
                        <select id="metode" name="metode" class="input">
                            @foreach (Label::METODE as $k => $v)
                                <option value="{{ $k }}" @selected($nilai('metode') === $k)>{{ $v }}</option>
                            @endforeach
                        </select>
                    </div>
                </div>
            </section>

            <section class="card p-5">
                <h2 class="mb-4 font-semibold">Gaji & tunjangan</h2>
                <div class="grid gap-4 sm:grid-cols-3">
                    @include('payroll._angka', ['f' => 'gaji_pokok', 'lbl' => 'Gaji pokok sebulan (Rp)', 'wajib' => true])
                    @include('payroll._angka', ['f' => 'kenaikan_nominal', 'lbl' => 'Kenaikan gaji (Rp)'])
                    <div>
                        <label for="kenaikan_tanggal" class="label">Kenaikan berlaku mulai</label>
                        <input id="kenaikan_tanggal" name="kenaikan_tanggal" type="date" value="{{ $nilai('kenaikan_tanggal') }}" required
                               class="input {{ $err('kenaikan_tanggal') }}">
                        <p class="bantu">Tanggal 1 Januari = tanpa kenaikan di tengah tahun.</p>
                    </div>
                </div>
                <p class="mt-4 mb-2 text-sm text-slate-600">Bila kenaikan berlaku di tengah bulan (tanggal &gt; 1), pecah hari bulan itu:</p>
                <div class="grid gap-4 sm:grid-cols-4">
                    @include('payroll._angka', ['f' => 'kenaikan_hk_sebelum', 'lbl' => 'Hadir sebelum naik', 'bantu' => 'untuk gaji & tunjangan prorata'])
                    @include('payroll._angka', ['f' => 'kenaikan_hk_sesudah', 'lbl' => 'Hadir sesudah naik'])
                    @include('payroll._angka', ['f' => 'kenaikan_hari_sebelum', 'lbl' => 'Hari kerja sebelum naik', 'bantu' => 'untuk tunjangan tetap'])
                    @include('payroll._angka', ['f' => 'kenaikan_hari_sesudah', 'lbl' => 'Hari kerja sesudah naik'])
                </div>
                <p class="mt-4 mb-2 text-sm text-slate-600">Tunjangan sebelum / sesudah kenaikan. <em>Tetap</em> dibayar penuh; <em>prorata</em> mengikuti kehadiran.</p>
                <div class="grid gap-4 sm:grid-cols-4">
                    @include('payroll._angka', ['f' => 'tunjangan_tetap_lama', 'lbl' => 'Tetap (lama)'])
                    @include('payroll._angka', ['f' => 'tunjangan_prorata_lama', 'lbl' => 'Prorata (lama)'])
                    @include('payroll._angka', ['f' => 'tunjangan_tetap_baru', 'lbl' => 'Tetap (baru)'])
                    @include('payroll._angka', ['f' => 'tunjangan_prorata_baru', 'lbl' => 'Prorata (baru)'])
                </div>
            </section>

            <section class="card p-5">
                <h2 class="mb-4 font-semibold">THR & BPJS</h2>
                <div class="grid gap-4 sm:grid-cols-5">
                    <div>
                        <label for="tanggal_lebaran" class="label">Hari Raya (Idul Fitri)</label>
                        <input id="tanggal_lebaran" name="tanggal_lebaran" type="date" value="{{ $nilai('tanggal_lebaran') }}" required
                               class="input {{ $err('tanggal_lebaran') }}">
                    </div>
                    <div>
                        <label for="tanggal_thr_bayar" class="label">THR dibayarkan</label>
                        <input id="tanggal_thr_bayar" name="tanggal_thr_bayar" type="date" value="{{ $nilai('tanggal_thr_bayar') }}" required
                               class="input {{ $err('tanggal_thr_bayar') }}">
                    </div>
                    @include('payroll._angka', ['f' => 'bpjs_tk_mulai_bulan', 'lbl' => 'BPJS TK sejak bulan', 'min' => 1, 'max' => 12])
                    @include('payroll._angka', ['f' => 'bpjs_kes_mulai_bulan', 'lbl' => 'BPJS Kes sejak bulan', 'min' => 1, 'max' => 12])
                    <div>
                        <label for="kelas_jkk_persen" class="label">Tarif JKK perusahaan (%)</label>
                        <input id="kelas_jkk_persen" name="kelas_jkk_persen" value="{{ $nilai('kelas_jkk_persen') }}" required inputmode="decimal"
                               placeholder="0,24" class="input {{ $err('kelas_jkk_persen') }}">
                        <p class="bantu">Sesuai kelas risiko di BPJS TK.</p>
                    </div>
                </div>
            </section>

            <section class="card p-5">
                <h2 class="mb-1 font-semibold">Kehadiran & penghasilan variabel per bulan</h2>
                <p class="mb-4 text-sm text-slate-500">
                    @if ($rentang)
                        Masa kerja tahun ini: {{ Format::bulan($rentang[0], true) }}–{{ Format::bulan($rentang[1], true) }}. Bulan di luar masa kerja diabaikan.
                    @else
                        Pegawai tidak bekerja di tahun ini.
                    @endif
                    Hari kerja awal = Senin–Jumat; sesuaikan dengan kalender libur. Kolom variabel kosong = tidak ada.
                </p>
                <div class="overflow-x-auto">
                    <table class="tbl">
                        <thead>
                        <tr><th>Bulan</th><th>Hari kerja</th><th>Hadir</th><th>Kompensasi (% gaji)</th><th>Insentif OTA (Rp)</th><th>Lembur (Rp)</th><th>Komisi (Rp)</th></tr>
                        </thead>
                        <tbody>
                        @foreach ($bulan as $b => $m)
                            @php($dalam = $rentang && $b >= $rentang[0] && $b <= $rentang[1])
                            <tr class="{{ $dalam ? '' : 'bg-slate-50 text-slate-400' }}">
                                <td class="align-middle font-medium whitespace-nowrap">{{ Format::bulan($b, true) }}</td>
                                @foreach (['hk_penuh' => [1, 31, 'w-20'], 'hk_aktual' => [0, 31, 'w-20'], 'kompensasi_persen' => [null, null, 'w-28'],
                                           'ota' => [0, null, 'w-36'], 'lembur' => [0, null, 'w-36'], 'komisi' => [0, null, 'w-36']] as $f => [$min, $max, $lebar])
                                    @php($nama = "bulan.{$b}.{$f}")
                                    <td>
                                        <input name="bulan[{{ $b }}][{{ $f }}]" value="{{ old($nama, $m[$f]) }}" aria-label="{{ $f }} {{ Format::bulan($b, true) }}"
                                               @if ($f === 'kompensasi_persen') inputmode="decimal" @else type="number" step="1" min="{{ $min }}" @if ($max) max="{{ $max }}" @endif @endif
                                               class="input {{ $lebar }} {{ $errors->has($nama) ? 'input-error' : '' }}">
                                    </td>
                                @endforeach
                            </tr>
                        @endforeach
                        </tbody>
                    </table>
                </div>
            </section>

            <div class="flex gap-2">
                <button class="btn btn-primary">Simpan</button>
                <a href="{{ $payroll->exists ? route('payroll.show', $payroll) : route('pegawai.show', $pegawai) }}" class="btn btn-secondary">Batal</a>
            </div>
        </form>
    @endif
@endsection
