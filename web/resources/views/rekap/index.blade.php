@extends('layouts.app', ['judul' => "Rekap {$tahun}"])
@use('App\Support\Format')
@use('App\Payroll\Label')

@section('isi')
    <div class="mb-5 flex flex-wrap items-end justify-between gap-4">
        <div>
            <h1 class="text-2xl font-semibold">Rekap payroll {{ $tahun }}</h1>
            <p class="mt-1 text-sm text-slate-500">Hasil perhitungan terakhir setiap pegawai. Semua angka berasal dari engine knowledge base.</p>
        </div>
        <div class="flex flex-wrap items-center gap-2">
            <form method="GET" action="{{ route('rekap') }}">
                <label for="tahun" class="sr-only">Tahun pajak</label>
                <select id="tahun" name="tahun" class="input w-auto" onchange="this.form.submit()">
                    @foreach (collect($tahunAda)->push($tahun)->unique()->sortDesc() as $t)
                        <option value="{{ $t }}" @selected($t === $tahun)>{{ $t }}</option>
                    @endforeach
                </select>
            </form>
            @if ($baris->isNotEmpty())
                <a href="{{ route('rekap.ekspor', ['tahun' => $tahun]) }}" class="btn btn-secondary">Unduh CSV</a>
                <form method="POST" action="{{ route('rekap.hitung') }}">
                    @csrf
                    <input type="hidden" name="tahun" value="{{ $tahun }}">
                    <button class="btn btn-primary">Hitung semua ({{ $baris->count() }})</button>
                </form>
            @endif
        </div>
    </div>

    @if ($baris->isEmpty())
        <div class="card p-8 text-center text-sm text-slate-600">
            Belum ada data HR untuk tahun {{ $tahun }}.
            <a href="{{ route('pegawai.index') }}" class="font-medium text-blue-700 hover:underline">Buka daftar pegawai</a> untuk mengisinya.
        </div>
    @else
        <div class="mb-5 grid gap-3 sm:grid-cols-3">
            @foreach ([['Total bruto setahun', $total['bruto']], ['Total PPh 21 setahun', $total['pph21']], ['Total take home pay', $total['thp']]] as [$lbl, $v])
                <div class="card p-4">
                    <div class="text-sm text-slate-500">{{ $lbl }}</div>
                    <div class="mt-1 text-xl font-semibold tabular-nums">{{ Format::rp($v) }}</div>
                </div>
            @endforeach
        </div>

        <div class="card overflow-x-auto">
            <table class="tbl">
                <thead>
                <tr>
                    <th>Pegawai</th><th>PTKP</th><th>Metode</th>
                    <th class="text-right">Bruto setahun</th><th class="text-right">PPh 21 setahun</th><th class="text-right">Take home pay</th>
                    <th>Cek silang</th><th>Status</th>
                </tr>
                </thead>
                <tbody>
                @foreach ($baris as $r)
                    @php($p = $r['hasil'])
                    <tr class="hover:bg-slate-50">
                        <td>
                            <a href="{{ route('payroll.show', $r['payroll']) }}" class="font-medium text-blue-700 hover:underline">{{ $r['payroll']->pegawai->nama }}</a>
                            <div class="text-xs text-slate-500">{{ $r['payroll']->pegawai->nomor_induk }}</div>
                        </td>
                        <td>{{ $r['payroll']->status_ptkp }}</td>
                        <td class="text-slate-600">{{ str_replace('_', ' ', $r['payroll']->metode) }}</td>
                        <td class="angka">{{ $p?->berhasil ? Format::rp($p->bruto_setahun, false) : '' }}</td>
                        <td class="angka font-medium">{{ $p?->berhasil ? Format::rp($p->pph21_setahun, false) : '' }}</td>
                        <td class="angka">{{ $p?->berhasil ? Format::rp($p->thp_setahun, false) : '' }}</td>
                        <td>@include('payroll._cek_silang_lencana', ['status' => $p?->cek_silang])</td>
                        <td class="text-xs">
                            @if ($p === null)
                                <span class="lencana bg-slate-100 text-slate-600">belum dihitung</span>
                            @elseif (! $p->berhasil)
                                <span class="lencana bg-red-100 text-red-800" title="{{ $p->pesan }}">galat</span>
                                <div class="mt-1 max-w-xs text-red-700">{{ \Illuminate\Support\Str::limit($p->pesan, 90) }}</div>
                            @elseif ($r['kedaluwarsa'])
                                <span class="lencana bg-amber-100 text-amber-800">data berubah, hitung ulang</span>
                            @else
                                <span class="text-slate-500">{{ $p->created_at->format('d/m/Y H:i') }}</span>
                            @endif
                        </td>
                    </tr>
                @endforeach
                </tbody>
            </table>
        </div>
        <p class="mt-3 text-xs text-slate-500">
            Cek silang membandingkan setiap hasil dengan kalkulator independen tanpa knowledge base (eksperimen E12).
            "Hitung semua" mengirim seluruh pegawai tahun ini ke engine dalam satu panggilan.
        </p>
    @endif
@endsection
