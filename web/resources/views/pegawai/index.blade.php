@extends('layouts.app', ['judul' => 'Pegawai'])
@use('App\Support\Format')

@section('isi')
    <div class="mb-5 flex flex-wrap items-end justify-between gap-4">
        <div>
            <h1 class="text-2xl font-semibold">Pegawai</h1>
            <p class="mt-1 text-sm text-slate-500">Pegawai tetap. Data HR (gaji, tunjangan, kehadiran) diisi per tahun pajak.</p>
        </div>
        <div class="flex gap-2">
            <form method="GET" action="{{ route('pegawai.index') }}">
                <label for="cari" class="sr-only">Cari</label>
                <input id="cari" name="cari" value="{{ $cari }}" placeholder="Cari nama / nomor induk" class="input w-64">
            </form>
            <a href="{{ route('pegawai.create') }}" class="btn btn-primary">Tambah pegawai</a>
        </div>
    </div>

    <div class="card overflow-x-auto">
        <table class="tbl">
            <thead>
            <tr><th>Nomor induk</th><th>Nama</th><th>Masuk</th><th>Berhenti</th><th>Data HR terakhir</th></tr>
            </thead>
            <tbody>
            @forelse ($pegawai as $p)
                <tr class="hover:bg-slate-50">
                    <td class="text-slate-600">{{ $p->nomor_induk }}</td>
                    <td><a href="{{ route('pegawai.show', $p) }}" class="font-medium text-blue-700 hover:underline">{{ $p->nama }}</a></td>
                    <td>{{ Format::tanggal($p->tanggal_masuk) }}</td>
                    <td>{{ $p->tanggal_berhenti ? Format::tanggal($p->tanggal_berhenti) : '—' }}</td>
                    <td>
                        @if ($p->payrollTerakhir)
                            <a href="{{ route('payroll.show', $p->payrollTerakhir) }}" class="text-blue-700 hover:underline">{{ $p->payrollTerakhir->tahun }}</a>
                            <span class="text-slate-500">· {{ $p->payrollTerakhir->status_ptkp }}</span>
                        @else
                            <span class="text-slate-400">belum ada</span>
                        @endif
                    </td>
                </tr>
            @empty
                <tr><td colspan="5" class="py-8 text-center text-slate-500">
                    {{ $cari !== '' ? 'Tidak ada pegawai yang cocok.' : 'Belum ada pegawai.' }}
                    @if ($cari === '')
                        Jalankan <code class="rounded bg-slate-100 px-1">php artisan payroll:impor-contoh</code> untuk memuat pegawai contoh dari dataset.
                    @endif
                </td></tr>
            @endforelse
            </tbody>
        </table>
    </div>
    <div class="mt-4">{{ $pegawai->links() }}</div>
@endsection
