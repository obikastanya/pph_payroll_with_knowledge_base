@extends('layouts.app', ['judul' => $pegawai->nama])
@use('App\Support\Format')
@use('App\Payroll\Label')

@section('isi')
    <div class="mb-5 flex flex-wrap items-start justify-between gap-4">
        <div>
            <p class="text-sm text-slate-500"><a href="{{ route('pegawai.index') }}" class="hover:underline">Pegawai</a> / {{ $pegawai->nomor_induk }}</p>
            <h1 class="text-2xl font-semibold">{{ $pegawai->nama }}</h1>
        </div>
        <div class="flex gap-2">
            <a href="{{ route('pegawai.edit', $pegawai) }}" class="btn btn-secondary">Ubah</a>
            <form method="POST" action="{{ route('pegawai.destroy', $pegawai) }}"
                  onsubmit="return confirm('Hapus pegawai ini beserta seluruh data payroll dan riwayat perhitungannya?')">
                @csrf @method('DELETE')
                <button class="btn btn-danger">Hapus</button>
            </form>
        </div>
    </div>

    <dl class="card mb-6 grid gap-4 p-5 text-sm sm:grid-cols-4">
        <div><dt class="text-slate-500">Jenis kelamin</dt><dd class="font-medium">{{ Label::JENIS_KELAMIN[$pegawai->jenis_kelamin] ?? $pegawai->jenis_kelamin }}</dd></div>
        <div><dt class="text-slate-500">NPWP / NIK valid</dt><dd class="font-medium">{{ $pegawai->punya_npwp ? 'ya' : 'tidak' }}</dd></div>
        <div><dt class="text-slate-500">Masuk kerja</dt><dd class="font-medium">{{ Format::tanggal($pegawai->tanggal_masuk) }}</dd></div>
        <div><dt class="text-slate-500">Berhenti</dt><dd class="font-medium">{{ $pegawai->tanggal_berhenti ? Format::tanggal($pegawai->tanggal_berhenti) : 'masih bekerja' }}</dd></div>
    </dl>

    <div class="mb-3 flex items-center justify-between">
        <h2 class="text-lg font-semibold">Data HR per tahun pajak</h2>
        <a href="{{ route('payroll.create', $pegawai) }}" class="btn btn-primary">Tambah tahun</a>
    </div>
    <div class="card overflow-x-auto">
        <table class="tbl">
            <thead>
            <tr><th>Tahun</th><th>PTKP</th><th>Metode</th><th class="text-right">Gaji pokok</th><th class="text-right">PPh 21 setahun</th><th>Cek silang</th><th>Dihitung</th></tr>
            </thead>
            <tbody>
            @forelse ($pegawai->payrollTahun as $pt)
                @php($p = $pt->perhitunganTerakhir)
                <tr class="hover:bg-slate-50">
                    <td><a href="{{ route('payroll.show', $pt) }}" class="font-medium text-blue-700 hover:underline">{{ $pt->tahun }}</a></td>
                    <td>{{ $pt->status_ptkp }}</td>
                    <td class="text-slate-600">{{ str_replace('_', ' ', $pt->metode) }}</td>
                    <td class="angka">{{ Format::rp($pt->gaji_pokok, false) }}</td>
                    <td class="angka font-medium">{{ $p?->berhasil ? Format::rp($p->pph21_setahun, false) : ($p ? 'galat' : '') }}</td>
                    <td>@include('payroll._cek_silang_lencana', ['status' => $p?->cek_silang])</td>
                    <td class="text-slate-500">{{ $p ? $p->created_at->format('d/m/Y H:i') : 'belum' }}</td>
                </tr>
            @empty
                <tr><td colspan="7" class="py-8 text-center text-slate-500">Belum ada data HR. Tambahkan tahun pajak pertama.</td></tr>
            @endforelse
            </tbody>
        </table>
    </div>
@endsection
