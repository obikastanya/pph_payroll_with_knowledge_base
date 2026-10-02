@extends('layouts.app', ['judul' => $payroll->pegawai->nama.' '.$payroll->tahun])
@use('App\Support\Format')
@use('App\Payroll\Label')
@use('App\Http\Controllers\PayrollTahunController')

@section('isi')
    <div class="mb-5 flex flex-wrap items-start justify-between gap-4">
        <div>
            <p class="text-sm text-slate-500">
                <a href="{{ route('pegawai.show', $payroll->pegawai) }}" class="hover:underline">{{ $payroll->pegawai->nama }}</a>
                · {{ $payroll->pegawai->nomor_induk }}
            </p>
            <h1 class="text-2xl font-semibold">Payroll {{ $payroll->tahun }}</h1>
            <p class="mt-1 text-sm text-slate-600">
                PTKP {{ $payroll->status_ptkp }} · {{ Label::METODE[$payroll->metode] ?? $payroll->metode }} · gaji pokok {{ Format::rp($payroll->gaji_pokok) }}
            </p>
        </div>
        <div class="flex flex-wrap gap-2">
            <form method="POST" action="{{ route('payroll.hitung', $payroll) }}">
                @csrf
                <button class="btn btn-primary">{{ $terakhir ? 'Hitung ulang' : 'Hitung' }}</button>
            </form>
            <a href="{{ route('payroll.edit', $payroll) }}" class="btn btn-secondary">Ubah data HR</a>
            @if ($tampil)
                <a href="{{ route('payroll.ekspor', $payroll) }}" class="btn btn-secondary">Unduh CSV</a>
            @endif
            <form method="POST" action="{{ route('payroll.destroy', $payroll) }}"
                  onsubmit="return confirm('Hapus data HR {{ $payroll->tahun }} beserta riwayat perhitungannya?')">
                @csrf @method('DELETE')
                <button class="btn btn-danger">Hapus</button>
            </form>
        </div>
    </div>

    @if (! $terakhir)
        <div class="card p-8 text-center text-sm text-slate-600">Belum dihitung. Tekan <strong>Hitung</strong> untuk mengirim data HR ke engine.</div>
    @else
        @if ($kedaluwarsa)
            <div class="mb-4 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900" role="status">
                <strong>Data HR berubah sejak perhitungan terakhir.</strong> Angka di bawah masih memakai data lama; tekan <strong>Hitung ulang</strong>.
            </div>
        @endif
        @if (! $terakhir->berhasil)
            <div class="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800" role="alert">
                <strong>Perhitungan terakhir gagal</strong> ({{ $terakhir->jenis_galat }}): {{ $terakhir->pesan }}
            </div>
        @endif
    @endif

    @if ($tampil)
        @include('payroll._cek_silang', ['p' => $terakhir])

        <div class="mb-5 grid gap-3 sm:grid-cols-2 {{ count($tampil->ringkasan()) > 4 ? 'lg:grid-cols-5' : 'lg:grid-cols-4' }}">
            @foreach ($tampil->ringkasan() as [$lbl, $v, $bantu])
                <div class="card p-4" title="{{ $bantu }}">
                    <div class="text-sm text-slate-500">{{ $lbl }}</div>
                    <div class="mt-1 text-xl font-semibold tabular-nums">{{ $v }}</div>
                </div>
            @endforeach
        </div>

        @foreach ($tampil->peringatan() as $p)
            <div class="mb-3 rounded-md border px-4 py-3 text-sm {{ $p['jenis'] === 'warning' ? 'border-amber-200 bg-amber-50 text-amber-900' : 'border-blue-200 bg-blue-50 text-blue-900' }}">
                <strong>{{ $p['judul'] }}.</strong> {{ $p['teks'] }}
            </div>
        @endforeach

        <nav class="mt-6 mb-4 flex gap-1 overflow-x-auto border-b border-slate-200 text-sm" aria-label="Bagian hasil">
            @foreach (PayrollTahunController::TAB as $k => $lbl)
                <a href="{{ route('payroll.show', [$payroll, 'tab' => $k, 'bulan' => $bulanSlip]) }}"
                   class="-mb-px border-b-2 px-3 py-2 whitespace-nowrap {{ $tab === $k ? 'border-blue-700 font-medium text-blue-800' : 'border-transparent text-slate-600 hover:text-slate-900' }}"
                   @if ($tab === $k) aria-current="page" @endif>{{ $lbl }}</a>
            @endforeach
        </nav>

        @include("payroll._tab_{$tab}")

        <dl class="mt-6 grid gap-x-6 gap-y-1 text-xs text-slate-500 sm:grid-cols-2">
            <div>Dihitung {{ $terakhir->created_at->format('d/m/Y H:i') }} oleh {{ $terakhir->user?->name ?? 'sistem' }}</div>
            <div>Engine {{ $terakhir->versi_engine }} · KB commit <code>{{ \Illuminate\Support\Str::limit($terakhir->versi_kb, 12, '') }}</code>
                ({{ $tampil->h['audit']['tanggal_kebaruan_kb'] ?? '-' }})</div>
        </dl>
    @endif

    @if ($riwayat->count() > 1)
        <details class="mt-8">
            <summary class="cursor-pointer text-sm font-medium text-slate-700">Riwayat perhitungan ({{ $riwayat->count() }})</summary>
            <div class="card mt-3 overflow-x-auto">
                <table class="tbl">
                    <thead><tr><th>Waktu</th><th>Oleh</th><th>Status</th><th class="text-right">PPh 21 setahun</th><th class="text-right">Take home pay</th><th>Cek silang</th><th>Versi KB</th></tr></thead>
                    <tbody>
                    @foreach ($riwayat as $r)
                        <tr>
                            <td>{{ $r->created_at->format('d/m/Y H:i:s') }}</td>
                            <td>{{ $r->user?->name ?? 'sistem' }}</td>
                            <td>{{ $r->berhasil ? 'berhasil' : 'galat: '.\Illuminate\Support\Str::limit($r->pesan, 60) }}</td>
                            <td class="angka">{{ $r->berhasil ? Format::rp($r->pph21_setahun, false) : '' }}</td>
                            <td class="angka">{{ $r->berhasil ? Format::rp($r->thp_setahun, false) : '' }}</td>
                            <td>@include('payroll._cek_silang_lencana', ['status' => $r->cek_silang])</td>
                            <td><code class="text-xs">{{ \Illuminate\Support\Str::limit($r->versi_kb, 12, '') }}</code></td>
                        </tr>
                    @endforeach
                    </tbody>
                </table>
            </div>
        </details>
    @endif
@endsection
